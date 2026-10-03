#!/usr/bin/env python
"""task5 VQE 拟态：nosym 初态制备 + 多层 U_e/U_o + 裸 H 期望（statevector 精确）.

约定（见 doc/qc/*.md，真机简化版）：
- 格点 0-indexed，格点 j <-> qubit j；L=8 OBC。
- intra 键 (0,1),(2,3),(4,5),(6,7) 为奇键子层 U_o；inter 键 (1,2),(3,4),(5,6)
  为偶键子层 U_e；子层配对惯例沿用 task3/4。
- nosym 初态：triv 与对称版一致；topo 去 (0,7) link（0,7 置 |00>）；
  AFM 取单支 |01010101>（偶位 0 奇位 1）。初态可不在 P=-1 扇区。
- Qubit 序为 LSB（qubit j = bit j）；Julia 参考矩阵为 MSB 序，
  fidelity 核对时用 bit_reverse 转换。VQE 内部全部自洽于 LSB。
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

L = 8

INTRA = [(0, 1), (2, 3), (4, 5), (6, 7)]
INTER = [(1, 2), (3, 4), (5, 6)]

# 初态 -> 先作用子层（'e' 偶键先 / 'o' 奇键先）
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


def init_topo_nosym() -> QuantumCircuit:
    """nosym 拓扑：bulk 三单态 + |00>_{0,7}（0,7 无门，无长程 CNOT）。"""
    circ = QuantumCircuit(L)
    for a, b in INTER:
        _singlet_prep(circ, a, b)
    return circ


def init_afm_nosym() -> QuantumCircuit:
    """nosym 反铁磁：单支 |01010101>（奇数位 X，无 H、无 CNOT 链）。"""
    circ = QuantumCircuit(L)
    for j in (1, 3, 5, 7):
        circ.x(j)
    return circ


INITS = {"triv": init_triv, "topo": init_topo_nosym, "afm": init_afm_nosym}


def _sublayer(circ: QuantumCircuit, bonds, t1: float, t2: float) -> None:
    """单子层：每键 RXX(t1) RYY(t1) RZZ(t2)（XX 与 YY 对易，可分开）。"""
    for a, b in bonds:
        circ.rxx(t1, a, b)
        circ.ryy(t1, a, b)
        circ.rzz(t2, a, b)


def build_vqe_circuit(init_name: str, theta, n_layers: int = 1) -> QuantumCircuit:
    """多层拟态电路。theta 按层拼接，每层 (o1, o2, e1, e2) 共 4 参数。

    层间子层顺序逐层交替、首层保持初态配对顺序（INIT_ORDER）；
    n_layers=1 时与 task3 单层逐位一致。
    """
    theta = [float(t) for t in theta]
    assert len(theta) == 4 * n_layers, f"need 4*n_layers params, got {len(theta)}"
    circ = INITS[init_name]()
    first = INIT_ORDER[init_name]
    for layer in range(n_layers):
        tho1, tho2, the1, the2 = theta[4 * layer:4 * layer + 4]
        layers = {"o": (INTRA, tho1, tho2), "e": (INTER, the1, the2)}
        # 偶数层用配对顺序，奇数层交替
        order = (first, "o" if first == "e" else "e") if layer % 2 == 0 else (
            ("o" if first == "e" else "e"), first)
        for key in order:
            bonds, t1, t2 = layers[key]
            _sublayer(circ, bonds, t1, t2)
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
    """裸 H(s,delta)（LSB 序，与 Julia build_H 同模型）。"""
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
