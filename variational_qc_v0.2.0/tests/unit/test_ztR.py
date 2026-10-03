"""Z~R regression: analytic states + brute-force R_I cross-check.

Guards the block-mirror contraction bug (mir indexed by full-basis rows
instead of in-block configurations, yielding non-negative garbage on [-1,1]).
"""

import numpy as np
import pytest

from ssh_xxz.core.hamiltonian import build_hamiltonian
from ssh_xxz.core.initial_states import afm_state, topo_state, trivial_state
from ssh_xxz.core.observables import z_tilde_R
from ssh_xxz.ed.solver import ground_state

L = 8


def test_trivial_plus_one():
    assert z_tilde_R(trivial_state(L), L) == 1.0


def test_topo_minus_one():
    assert z_tilde_R(topo_state(L), L) == -1.0


def test_afm_ghz_zero():
    assert z_tilde_R(afm_state(L), L) == 0.0


def _brute_force(psi):
    """Independent naive implementation: explicit partial trace + R_I matrix."""
    n = L // 4
    start = L // 2 - n
    block = list(range(start, start + 2 * n))
    rest = [m for m in range(L) if m not in block]
    dim = 2 ** len(block)

    def bits(i):
        return [(i >> m) & 1 for m in range(L)]

    rho = np.zeros((dim, dim), dtype=complex)
    for i in range(2**L):
        for j in range(2**L):
            bi, bj = bits(i), bits(j)
            if any(bi[m] != bj[m] for m in rest):
                continue
            ri = sum(bi[m] << k for k, m in enumerate(block))
            cj = sum(bj[m] << k for k, m in enumerate(block))
            rho[ri, cj] += psi[i] * psi[j].conj()

    nb = len(block)
    R = np.zeros((dim, dim))
    for b in range(dim):
        rb = int(f"{b:0{nb}b}"[::-1], 2)
        R[rb, b] = 1.0
    z_r = np.trace(rho @ R).real
    h = nb // 2
    d = 2**h
    rho1 = np.zeros((d, d), dtype=complex)
    rho2 = np.zeros((d, d), dtype=complex)
    for a in range(d):
        for ap in range(d):
            rho1[a, ap] = sum(rho[a + d * b, ap + d * b] for b in range(d))
            rho2[a, ap] = sum(rho[b + d * a, b + d * ap] for b in range(d))
    p1 = np.trace(rho1 @ rho1).real
    p2 = np.trace(rho2 @ rho2).real
    return float((z_r / np.sqrt((p1 + p2) / 2.0)).real)


def test_random_vs_brute_force():
    rng = np.random.default_rng(7)
    for _ in range(3):
        psi = rng.normal(size=2**L) + 1j * rng.normal(size=2**L)
        psi /= np.linalg.norm(psi)
        assert z_tilde_R(psi, L) == pytest.approx(_brute_force(psi), abs=1e-12)


def test_ground_state_in_range():
    H = build_hamiltonian(L, 0.5, 1.0)
    _, psi = ground_state(H)
    assert -1.0 - 1e-9 <= z_tilde_R(psi, L) <= 1.0 + 1e-9
