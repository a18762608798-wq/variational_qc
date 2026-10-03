"""T005: Hamiltonian bond placement + OBC (IV.2). FAIL-first."""

import numpy as np
import pytest

from ssh_xxz.core.hamiltonian import build_hamiltonian


def test_hermitian():
    H = build_hamiltonian(6, 0.37, 1.7).toarray()
    assert np.allclose(H, H.conj().T)


def test_s0_odd_bonds_only_analytic():
    # s=0, delta=0: L/2 decoupled XX+YY odd bonds, singlet energy -2 each.
    L = 4
    H = build_hamiltonian(L, 0.0, 0.0, sparse=False)
    e0 = np.linalg.eigvalsh(H)[0]
    assert e0 == pytest.approx(-L, abs=1e-10)


def test_s1_obc_even_bonds():
    # s=1, delta=0: L/2-1 even bonds (OBC: no wrap bond), energy -2 each.
    L = 4
    H = build_hamiltonian(L, 1.0, 0.0, sparse=False)
    e0 = np.linalg.eigvalsh(H)[0]
    assert e0 == pytest.approx(-(L - 2), abs=1e-10)


def test_sparse_dense_agree():
    Hs = build_hamiltonian(6, 0.42, 2.1, sparse=True).toarray()
    Hd = build_hamiltonian(6, 0.42, 2.1, sparse=False)
    assert np.allclose(Hs, Hd)
