"""exp06 本地单元测试（T006）：纯逻辑 + Aer 仿真，零真机调用。

qmeas env python -m pytest test/test_exp06_local.py
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from exp06_circuits import (  # noqa: E402
    A_LABELS,
    L,
    build_ansatz,
    build_estimator_circuit,
    build_init,
    orbit_params,
)

PROJ = Path(__file__).resolve().parent.parent
QISKIT = pytest.importorskip("qiskit")
Aer = pytest.importorskip("qiskit_aer")


def aer_statevector(qc):
    from qiskit.quantum_info import Statevector
    qc2 = qc.copy()
    qc2.remove_final_measurements()
    return np.asarray(Statevector.from_instruction(qc2).data)


def probs_of(psi):
    p = np.abs(np.asarray(psi)) ** 2
    return p / p.sum()


def exp_zdiag(probs, pauli_dict):
    """Z 对角算符期望：pauli_dict {qubit_tuple: coeff}，qubit=格点-1。"""
    ev = 0.0
    for b in range(1 << L):
        bits = [(b >> q) & 1 for q in range(L)]  # 0→Z+1, 1→Z-1
        z = [1 - 2 * x for x in bits]
        for qs, c in pauli_dict.items():
            v = c
            for q in qs:
                v *= z[q]
            ev += v * probs[b]
    return ev


def s_pi_of(probs):
    # (1/L)Σ_{i,j}(-1)^{i-j}⟨ZiZj⟩；对角 i=j 为恒等（本征值恒 1），不得并入单 Z。
    d = {}
    for i in range(L):
        for j in range(L):
            if i == j:
                continue
            key = tuple(sorted((i, j)))
            d[key] = d.get(key, 0) + (-1) ** (i - j) / L
    return exp_zdiag(probs, d) + 1.0


def string_of(probs):
    # Ostr(d=3) = (Z1+Z2)(Z3Z4)(Z5Z6)(Z7+Z8)，0-indexed qubits。
    terms = {}
    for a in (0, 1):
        for b in (6, 7):
            key = tuple(sorted({a, 2, 3, 4, 5, b}))
            terms[key] = terms.get(key, 0) + 1.0
    return exp_zdiag(probs, terms)


def test_init_support_and_sector():
    # triv/topo：16 基矢、振幅 ±1/4、Z_tot=0 扇区（popcount=4）。
    for a in (1, 2):
        psi = aer_statevector(build_init(a))
        p = probs_of(psi)
        nz = np.nonzero(p > 1e-12)[0]
        assert len(nz) == 16
        assert np.allclose(p[nz], 1 / 16)
        assert all(bin(b).count("1") == 4 for b in nz)
    # triv 全 |01⟩ 键：整数 170，振幅 +1/4。
    psi = aer_statevector(build_init(1))
    assert psi[170] == pytest.approx(0.25)
    # afm：两基矢等权正振幅。
    psi = aer_statevector(build_init(3))
    p = probs_of(psi)
    nz = np.nonzero(p > 1e-12)[0]
    assert set(nz.tolist()) == {170, 85}
    assert np.allclose(p[nz], 0.5)
    assert np.all(np.real(psi[nz]) > 0)


def test_single_bond_unitary():
    from qiskit.quantum_info import Operator
    from qiskit import QuantumCircuit
    t1, t2 = 0.7, -0.3
    qc = QuantumCircuit(2)
    qc.rxx(t1, 0, 1)
    qc.ryy(t1, 0, 1)
    qc.rzz(t2, 0, 1)
    U = np.asarray(Operator(qc).data)
    # 手算 RZZ·RYY·RXX（|q1 q0> 基，q0 快）。
    c1, s1 = np.cos(t1 / 2), np.sin(t1 / 2)
    c2, s2 = np.cos(t2 / 2), np.sin(t2 / 2)
    RXX = np.array([[c1, 0, 0, -1j * s1], [0, c1, -1j * s1, 0],
                    [0, -1j * s1, c1, 0], [-1j * s1, 0, 0, c1]])
    RYY = np.array([[c1, 0, 0, 1j * s1], [0, c1, -1j * s1, 0],
                    [0, -1j * s1, c1, 0], [1j * s1, 0, 0, c1]])
    RZZ = np.diag([np.exp(-1j * t2 / 2), np.exp(1j * t2 / 2),
                   np.exp(1j * t2 / 2), np.exp(-1j * t2 / 2)])
    assert np.allclose(U, RZZ @ RYY @ RXX, atol=1e-12)


def test_orbit_param_layout():
    th = np.arange(1, 25, dtype=float)
    lay = orbit_params(th, 2, 3, 0.85)
    assert lay[0]["odd"][0] == (1.0, 2.0)
    assert lay[0]["odd"][1] == (3.0, 4.0)
    assert lay[0]["even"][0] == (5.0, 6.0)
    assert lay[0]["even"][1] == (7.0, 8.0)
    assert lay[1]["odd"][0] == (9.0, 10.0)
    th0 = np.arange(1, 13, dtype=float)
    lay0 = orbit_params(th0, 2, 3, 0.0)
    assert lay0[0]["odd"] == [(1.0, 1.0), (2.0, 2.0)]
    assert lay0[0]["even"] == [(3.0, 3.0), (4.0, 4.0)]
    with pytest.raises(ValueError):
        orbit_params(th0[:3], 2, 1, 0.0)
    with pytest.raises(ValueError):
        build_init(4)


def test_golden_cross_vs_s06():
    """Aer 黄金交叉：抽样组 Qiskit 电路 vs S06 S(π)/string（容限 1e-8）。"""
    s03 = np.load(PROJ / "data/exp04/exp04_S03.npz")
    s06 = np.load(PROJ / "data/exp04/exp04_S06.npz")
    meta, th = s03["meta"], s03["theta"]
    deltas = s03["deltas"]
    n_checked = 0
    for di, delta in enumerate(deltas, start=1):
        tag = "d0" if di == 1 else "d085"
        for si in (1, 49, 97):
            for p in (1, 2, 3):
                r = (di - 1) * 99 * 3 + (si - 1) * 3 + (p - 1)
                assert (meta[r] == [di, si, p, meta[r][3]]).all()
                a = int(meta[r][3])
                npl = L // 2 if abs(float(delta)) < 1e-15 else L
                psi = aer_statevector(build_estimator_circuit(
                    th[r][:npl * p], a, p, float(delta)))
                probs = probs_of(psi)
                assert s_pi_of(probs) == pytest.approx(
                    s06[f"{tag}_spi"][si - 1, p - 1], abs=1e-8)
                assert string_of(probs) == pytest.approx(
                    s06[f"{tag}_ostr"][si - 1, p - 1], abs=1e-8)
                n_checked += 1
    assert n_checked == 18


def test_mitigation_identity_and_recovery():
    from exp06_assemble import mitigate_counts  # noqa: E402
    rng = np.random.default_rng(0)
    ideal = rng.random(256)
    ideal /= ideal.sum()
    # 恒等矩阵 → 不变。
    Ms = [np.eye(2)] * 8
    out = mitigate_counts({format(b, "08b"): int(ideal[b] * 10 ** 9)
                           for b in range(256)}, Ms, 8)
    assert np.allclose(out / out.sum(), ideal, atol=1e-6)
    # 合成误读率数据恢复。
    M1 = np.array([[0.9, 0.2], [0.1, 0.8]])
    Ms = [M1] * 8
    MK = M1
    for _ in range(7):
        MK = np.kron(MK, M1)
    meas = MK @ ideal
    counts = {format(b, "08b"): int(meas[b] * 20000) for b in range(256)}
    rec = mitigate_counts(counts, Ms, 8)
    assert np.allclose(rec / rec.sum(), ideal, atol=2e-2)


def test_minmax_normalize():
    from exp06_assemble import minmax_norm  # noqa: E402
    x = np.array([0.5, 0.7, 0.6])
    assert np.allclose(minmax_norm(x), [0.0, 1.0, 0.5])


def test_manifest_schema():
    from exp06_assemble import (  # noqa: E402
        MANIFEST_KEYS,
        build_manifest,
    )
    m = build_manifest(**{k: None for k in MANIFEST_KEYS - {"schema"}})
    assert m["schema"] == "exp06/v1"
    assert MANIFEST_KEYS <= set(m)
    with pytest.raises(ValueError):
        build_manifest(schema="exp06/v1")
