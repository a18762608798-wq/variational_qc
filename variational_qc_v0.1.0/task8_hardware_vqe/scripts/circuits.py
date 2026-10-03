#!/usr/bin/env python
"""task8 测量电路：Aer 拟态（复用 task3/task5）+ X/Y/Z 测量基旋转。

- sym 初态：task3 ansatz（triv/topo/afm，单层）。
- nosym 初态：task5 ansatz（triv/topo_nosym/afm_nosym，n_layers=1）。
- sym-topo 上环：10 电路比特（逻辑 0..7 + 桥 8/9），制备见
  build_sym_topo_ring；测量只测逻辑 0..7。
- 测量基：X -> h；Y -> sdg + h；Z -> 无门；随后 Qi -> Ci（i 为逻辑序）。
"""

import importlib.util
from pathlib import Path

from qiskit import QuantumCircuit

HERE = Path(__file__).resolve()
ROOT = HERE.parent.parent.parent
T3 = ROOT / "task3_vqe" / "scripts" / "ansatz.py"
T5 = ROOT / "task5_vqe_nosym" / "scripts" / "ansatz.py"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_sym = _load("t3ansatz", T3)
_nosym = _load("t5ansatz", T5)

L = 8
INTRA = _sym.INTRA
INTER = _sym.INTER
INIT_ORDER = _sym.INIT_ORDER

SYM_INITS = _sym.INITS  # triv/topo/afm（含 0-7 长程，仅 Aer/验证用）
NOSYM_INITS = _nosym.INITS  # triv/topo_nosym/afm_nosym

# sym-topo 上环：10 电路比特 -> 物理映射（grid.toml ring10）
# 桥：SWAP(7,8) 把逻辑7送上 c8；SWAP(0,9) 把逻辑0送上 c9；
# _singlet_prep(9,8) 在 (c9,c8)=(逻辑0,逻辑7) 上造 |s>_{0,7}。
# 物理邻接：c8=125 <-> {c0=126, c9=138}；c9=138 <-> {c7=139, c8=125}。


def build_sym_topo_ring(theta) -> QuantumCircuit:
    tho1, tho2, the1, the2 = (float(t) for t in theta)
    circ = QuantumCircuit(10)
    for a, b in INTER:
        _sym._singlet_prep(circ, a, b)
    circ.swap(7, 8)
    circ.swap(0, 9)
    _sym._singlet_prep(circ, 9, 8)
    layers = {"o": (INTRA, tho1, tho2), "e": (INTER, the1, the2)}
    for key in ("o", "e"):  # topo 配对顺序 U_o 先
        bonds, t1, t2 = layers[key]
        _sym._sublayer(circ, bonds, t1, t2)
    return circ


def build_prep(task: str, init: str, theta) -> QuantumCircuit:
    """task in {sym, nosym}；sym-topo 走环（10 比特），其余 8 比特。"""
    if task == "sym" and init == "topo":
        return build_sym_topo_ring(theta)
    if task == "sym":
        return _sym.build_vqe_circuit(init, theta)
    return _nosym.build_vqe_circuit(init, theta, n_layers=1)


def measure_circuit(prep: QuantumCircuit, basis: str,
                    n_logical: int = 8) -> QuantumCircuit:
    """拷贝 prep，加测量基旋转，测逻辑 0..n_logical-1 到经典同序比特。"""
    assert basis in ("X", "Y", "Z")
    circ = prep.copy()
    from qiskit.circuit import ClassicalRegister
    circ.add_register(ClassicalRegister(n_logical, "c"))
    for j in range(n_logical):
        if basis == "X":
            circ.h(j)
        elif basis == "Y":
            circ.sdg(j)
            circ.h(j)
    circ.measure(list(range(n_logical)), list(range(n_logical)))
    return circ


def coupling_for(task: str, init: str):
    if task == "sym" and init == "topo":
        edges = [[i, i + 1] for i in range(7)]
        return edges + [[7, 9], [9, 8], [8, 0]]
    return [[i, i + 1] for i in range(7)]
