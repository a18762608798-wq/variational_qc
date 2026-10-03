"""T006: initial-state preparation + P=-2 sector (IV.2). FAIL-first."""

import numpy as np
import pytest

from ssh_xxz.core.initial_states import afm_state, topo_state, trivial_state

L = 8


def _z_tot(psi):
    n = len(psi)
    Lloc = int(np.log2(n))
    probs = np.abs(psi) ** 2
    zt = np.zeros(n)
    for m in range(Lloc):
        bits = ((np.arange(n) >> m) & 1) * 2 - 1  # +1 for |1>, -1 for |0>
        zt += bits
    return float(np.sum(probs * zt))


def _reflect(psi):
    n = len(psi)
    Lloc = int(np.log2(n))
    out = np.zeros_like(psi)
    for i in range(n):
        j = sum(((i >> m) & 1) << (Lloc - 1 - m) for m in range(Lloc))
        out[j] = psi[i]
    return out


def test_norms_and_z_tot_zero():
    for fn in (trivial_state, topo_state, afm_state):
        psi = fn(L)
        assert np.vdot(psi, psi).real == pytest.approx(1.0)
        assert _z_tot(psi) == pytest.approx(0.0, abs=1e-12)


def test_reflection_plus_one():
    for fn in (trivial_state, topo_state, afm_state):
        psi = fn(L)
        assert np.allclose(_reflect(psi), psi)


def test_p_minus_two_sector():
    # P = Ztot^2 - prodX - R; here Ztot=0, prodX=+1, R=+1 -> P=-2.
    for fn in (trivial_state, topo_state, afm_state):
        psi = fn(L)
        n = len(psi)
        Lloc = int(np.log2(n))
        prods = np.array([(-1) ** bin(i).count("1") for i in range(n)])
        prodx = float(np.vdot(psi, prods * psi).real)
        assert prodx == pytest.approx(1.0)
