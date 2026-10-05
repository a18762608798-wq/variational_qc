"""exp06 T001 Qiskit 电路构造器：Exp04 Julia 内核的 Python 复刻。

对应表（Exp04.jl → 本模块）：
- InitStates.psi_triv/topo/afm (L=8) → build_init(a*)，a*∈{1,2,3}=triv/topo/afm。
  基矢约定两边一致：格点 m ↔ qubit m-1，|0⟩=Z+1（Qiskit 小端，qubit0=LSB）。
- Ansatz.build_meta(8, leg)：奇轨道 [[O1,O4],[O2,O3]]（M=4，O1↔O4、O2↔O3），
  偶轨道 [[E1,E3],[E2]]（E1↔E3，E2 自镜像）；子层顺序 topo 为 odd→even，
  其余 even→odd → SUB_ORDER。
- Ansatz._orbit_base 层内排布：δ≠0 时单层 8 参数（奇轨 oi 基址 2oi-1，
  偶轨偏移 4 后 2oi-1；tx=θ[b]，tz=θ[b+1]）；δ=0 减半单层 4 参数
  （奇轨 oi，偶轨 2+oi；tx=tz=θ[b]）→ orbit_params()。
- Ansatz._bond_unitary = RXX(tx)RYY(tx)RZZ(tz)，作用顺序 RXX 先 →
  Qiskit 按 rxx→ryy→rzz 顺序 append（定义一致：RXX(θ)=exp(-iθXX/2) 等）。
- 层堆叠 U^(1)…U^(p) 依次作用 → 按层顺序 append。

单态 |s⟩=(|01⟩-|10⟩)/√2（前为 a 位）：X(c)→H(a)→CX(a,c)→Z(a)。
GHZ (|0101…⟩+|1010…⟩)/√2：中间发起手写版（逻辑同
qmeas.models.xxz.get_initial_state(8, pidx=0)，但不依赖 qmeas：
三初态构造器保持零外部依赖，单源可审计。H 打中间比特、两路 CNOT
向左右散开、翻奇位；纠缠级联深度 ~n/2。已逐振幅比对
docs/theory/psi0.md 解析式一致。
"""

from __future__ import annotations

from qiskit import QuantumCircuit

L = 8
A_LABELS = {1: "triv", 2: "topo", 3: "afm"}

# 轨道（1-indexed 格点键），顺序与 _orbits 生成一致。
ODD_ORBITS = [[(1, 2), (7, 8)], [(3, 4), (5, 6)]]
EVEN_ORBITS = [[(2, 3), (6, 7)], [(4, 5)]]
SUB_ORDER = {"triv": ("even", "odd"), "afm": ("even", "odd"),
             "topo": ("odd", "even")}


def _singlet(qc: QuantumCircuit, a: int, c: int) -> None:
    """格点 a,c（1-indexed）上制备单态。qubit = 格点-1。"""
    qa, qc_ = a - 1, c - 1
    qc.x(qc_)
    qc.h(qa)
    qc.cx(qa, qc_)
    qc.z(qa)


def build_init(a_star: int) -> QuantumCircuit:
    """三参考初态（docs/theory/psi0.md，L=8）。"""
    if a_star not in A_LABELS:
        raise ValueError(f"a* 须为 1/2/3，当前 {a_star!r}")
    qc = QuantumCircuit(L)
    if a_star == 1:  # 奇键单态乘积
        for j in range(1, 5):
            _singlet(qc, 2 * j - 1, 2 * j)
    elif a_star == 2:  # bulk 偶键单态 + 首尾单态
        for j in range(1, 4):
            _singlet(qc, 2 * j, 2 * j + 1)
        _singlet(qc, 1, L)
    else:  # GHZ 中间发起（手写，逻辑同 qmeas pidx=0；零 qmeas 依赖）
        mid = L // 2
        qc.h(mid)
        for i in range(mid, 0, -1):
            qc.cx(i, i - 1)
        for i in range(mid, L - 1):
            qc.cx(i, i + 1)
        for i in range(1, L, 2):
            qc.x(i)
    return qc


def orbit_params(theta, a_star: int, p: int, delta: float):
    """θ 向量 → 每层每轨道 (tx,tz) 表。

    返回 layers[l][sub][oi] = (tx, tz)，sub ∈ {"odd","even"}。
    δ=0 减半：单层 4 参数；否则单层 8 参数。NaN-pad 尾部忽略。
    """
    leg = A_LABELS[a_star]
    halved = abs(float(delta)) < 1e-15
    npl = L // 2 if halved else L
    if len(theta) < npl * p:
        raise ValueError(f"θ 长度 {len(theta)} < 需要 {npl * p}")
    no = len(ODD_ORBITS)
    layers = []
    for li in range(p):
        blk = list(theta[li * npl:(li + 1) * npl])
        layer = {}
        for oi in range(no):  # 奇轨
            b = oi if halved else 2 * oi
            tx = blk[b]
            layer.setdefault("odd", []).append((tx, tx if halved else blk[b + 1]))
        for oi in range(len(EVEN_ORBITS)):  # 偶轨
            off = no if halved else 2 * no
            b = off + (oi if halved else 2 * oi)
            tx = blk[b]
            layer.setdefault("even", []).append((tx, tx if halved else blk[b + 1]))
        layers.append({s: layer[s] for s in SUB_ORDER[leg]})
    return layers


def build_ansatz(theta, a_star: int, p: int, delta: float) -> QuantumCircuit:
    """orbit 拟设 unitary 部分（不含初态与测量）。"""
    leg = A_LABELS[a_star]
    layers = orbit_params(theta, a_star, p, delta)
    qc = QuantumCircuit(L)
    for layer in layers:
        for sub in SUB_ORDER[leg]:
            orbs = ODD_ORBITS if sub == "odd" else EVEN_ORBITS
            for (oi, orb) in enumerate(orbs):
                tx, tz = layer[sub][oi]
                for (a, c) in orb:
                    qa, qb = a - 1, c - 1
                    qc.rxx(tx, qa, qb)
                    qc.ryy(tx, qa, qb)
                    qc.rzz(tz, qa, qb)
    return qc


def build_estimator_circuit(theta, a_star: int, p: int,
                            delta: float) -> QuantumCircuit:
    """完整 estimator 电路：初态 + 拟设 + 全 Z 测量（S(π)/string 皆 Z 对角）。"""
    qc = build_init(a_star)
    qc.compose(build_ansatz(theta, a_star, p, delta), inplace=True)
    qc.measure_all()
    return qc


def build_calib_circuits() -> dict[str, QuantumCircuit]:
    """S05 标定：全 0 制备 / 全 X 制备（8 比特同时，spec POST-004）。"""
    q0 = QuantumCircuit(L)
    q0.measure_all()
    q1 = QuantumCircuit(L)
    q1.x(range(L))
    q1.measure_all()
    return {"cal_zero": q0, "cal_one": q1}
