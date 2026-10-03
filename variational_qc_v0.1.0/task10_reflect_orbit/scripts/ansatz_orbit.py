#!/usr/bin/env python
"""task10 orbit 拟设：三初态制备 + 反射对称 orbit 参数多层 U_e/U_o + 裸 H 期望.

约定（见 doc/qc/evolution_qc.md 反射对称 orbit 参数节）：
- L=8 OBC，格点 0-indexed，格点 j <-> qubit j（LSB 序，与 task3/4 自洽）。
- 奇轨道 O_OUT={(0,1),(6,7)}、O_IN={(2,3),(4,5)}；
  偶轨道 E_OUT={(1,2),(5,6)}、E_C={(3,4)}（(3,4) 自镜像）。
- 每轨道继承 Sz 守恒的 (θ_1,θ_2) 分工：同 orbit 键 XX/YY 共 θ_1、ZZ 独立 θ_2，
  即每键 RXX(θ_1)RYY(θ_1)RZZ(θ_2)；单层 8 参数
  (o_out1,o_out2,o_in1,o_in2,e_out1,e_out2,e_c1,e_c2)，n 层共 8n 参数。
- GHZ 初态下首作用子层的 2 个 θ_2（每 orbit 各一）只给整体相位（平坦方向）。
- 子层顺序与初态配对（同 task3）：平庸 U_oU_e、拓扑 U_eU_o、GHZ 取 U_oU_e；
  层间逐层交替、首层保持配对顺序（同 task4）。
- 初态制备与裸 H 矩模型与 task3/4 同语义（独立实现，不跨任务 import，
  避免 thetas 误用；数值一致性由 P 扇区与 H 对照脚本保证）。
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

L = 8

# orbit 分组（R: j -> 7-j 镜面对映；键按无序对书写）
O_OUT = [(0, 1), (6, 7)]
O_IN = [(2, 3), (4, 5)]
E_OUT = [(1, 2), (5, 6)]
E_C = [(3, 4)]

O_GROUPS = {"out": list(O_OUT), "in": list(O_IN)}
E_GROUPS = {"out": list(E_OUT), "c": list(E_C)}

INTRA = sorted(O_OUT + O_IN)
INTER = sorted(E_OUT + E_C)

# 初态 -> 先作用子层（'e' 偶键先 / 'o' 奇键先），同 task3 INIT_ORDER
INIT_ORDER = {"triv": "e", "topo": "o", "afm": "e"}

SX = np.array([[0, 1], [1, 0]], dtype=complex)
SY = np.array([[0, -1j], [1j, 0]], dtype=complex)
SZ = np.array([[1, 0], [0, -1]], dtype=complex)
ID2 = np.eye(2, dtype=complex)


def _singlet_prep(circ: QuantumCircuit, a: int, b: int) -> None:
    """在 (a,b) 上制备 |s>=(|01>-|10>)/sqrt(2)：X_b + H_a + CX(a,b) + Z_a."""
    circ.x(b)
    circ.h(a)
    circ.cx(a, b)
    circ.z(a)


def init_triv() -> QuantumCircuit:
    circ = QuantumCircuit(L)
    for a, b in INTRA:
        _singlet_prep(circ, a, b)
    return circ


def init_topo() -> QuantumCircuit:
    circ = QuantumCircuit(L)
    for a, b in INTER:
        _singlet_prep(circ, a, b)
    _singlet_prep(circ, 0, 7)  # 首尾长程对（模拟中直接长程 CNOT）
    return circ


def init_afm() -> QuantumCircuit:
    circ = QuantumCircuit(L)
    circ.h(0)
    for j in range(L - 1):
        circ.cx(j, j + 1)
    for j in (1, 3, 5, 7):
        circ.x(j)
    return circ


INITS = {"triv": init_triv, "topo": init_topo, "afm": init_afm}


def _orbit_sublayer(circ: QuantumCircuit, groups: dict, angles: dict) -> None:
    """单子层：同 orbit 键共用同一 (t1, t2)；每键 RXX(t1)RYY(t1)RZZ(t2)。

    angles: {orbit_key: (t1, t2)}，t1 管 XX/YY、t2 管 ZZ（Sz 守恒分工）。
    """
    for key, bonds in groups.items():
        t1, t2 = (float(v) for v in angles[key])
        for a, b in bonds:
            circ.rxx(t1, a, b)
            circ.ryy(t1, a, b)
            circ.rzz(t2, a, b)


def build_vqe_circuit(init_name: str, theta, n_layers: int = 1) -> QuantumCircuit:
    """orbit 多层拟设电路。theta 按层拼接，每层 8 参数：
    (o_out1, o_out2, o_in1, o_in2, e_out1, e_out2, e_c1, e_c2)。

    层间子层顺序逐层交替、首层保持初态配对顺序（INIT_ORDER）。
    """
    theta = [float(t) for t in theta]
    assert len(theta) == 8 * n_layers, f"need 8*n_layers params, got {len(theta)}"
    circ = INITS[init_name]()
    first = INIT_ORDER[init_name]
    for layer in range(n_layers):
        seg = theta[8 * layer:8 * layer + 8]
        o_out1, o_out2, o_in1, o_in2, e_out1, e_out2, e_c1, e_c2 = seg
        o_angles = {"out": (o_out1, o_out2), "in": (o_in1, o_in2)}
        e_angles = {"out": (e_out1, e_out2), "c": (e_c1, e_c2)}
        order = (first, "o" if first == "e" else "e") if layer % 2 == 0 else (
            ("o" if first == "e" else "e"), first)
        for key in order:
            if key == "o":
                _orbit_sublayer(circ, O_GROUPS, o_angles)
            else:
                _orbit_sublayer(circ, E_GROUPS, e_angles)
    return circ


def _embed1(A: np.ndarray, k: int) -> np.ndarray:
    """单格点算符嵌入（LSB 序：格点 j = bit j）。"""
    ops = [ID2] * L
    ops[k] = A
    M = ops[L - 1]
    for j in range(L - 2, -1, -1):
        M = np.kron(M, ops[j])
    return M


def _embed2(Ak: np.ndarray, Al: np.ndarray, k: int, l: int) -> np.ndarray:
    ops = [ID2] * L
    ops[k] = Ak
    ops[l] = Al
    M = ops[L - 1]
    for j in range(L - 2, -1, -1):
        M = np.kron(M, ops[j])
    return M


def H_matrix(s: float, delta: float) -> np.ndarray:
    """裸 H(s,delta)（LSB 序，与 task3/4 build_H 同模型）。"""
    H = np.zeros((2**L, 2**L), dtype=complex)
    for k, l in INTRA:
        H += (1 - s) * _bond(k, l, delta)
    for k, l in INTER:
        H += s * _bond(k, l, delta)
    return H


def _bond(k: int, l: int, delta: float) -> np.ndarray:
    jxx = np.exp(-delta)
    jz = np.exp(delta)
    return jxx * (_embed2(SX, SX, k, l) + _embed2(SY, SY, k, l)) + jz * _embed2(SZ, SZ, k, l)


def P_matrix() -> np.ndarray:
    """P = Z_tot^2 - prod X（LSB 序）。"""
    Ztot = sum(_embed1(SZ, j) for j in range(L))
    prodX = _embed1(SX, 0)
    for j in range(1, L):
        prodX = prodX @ _embed1(SX, j)
    return Ztot @ Ztot - prodX


def statevector_of(circ: QuantumCircuit) -> np.ndarray:
    return np.asarray(Statevector(circ).data, dtype=complex)


def expectation(psi: np.ndarray, M: np.ndarray) -> float:
    return float(np.real(np.vdot(psi, M @ psi)))


def bit_reverse(vec: np.ndarray) -> np.ndarray:
    """MSB<->LSB 索引转换（与 Julia 存档对照用）。"""
    n = len(vec)
    nb = n.bit_length() - 1
    out = np.empty_like(vec)
    for i in range(n):
        r = int(f"{i:0{nb}b}"[::-1], 2)
        out[r] = vec[i]
    return out
