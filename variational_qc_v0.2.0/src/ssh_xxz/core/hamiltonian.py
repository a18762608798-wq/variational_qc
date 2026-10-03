"""Physical SSH-XXZ Hamiltonian, OBC. Authoritative: doc/plan/theory/H.md.

H(s,δ) = H_o + H_e with odd bonds (1-s) and even bonds (s); NO wrap bond (OBC).
Site m (0-indexed) <-> bit m of the basis index (LSB = site 0).
"""

import numpy as np
import scipy.sparse as sp

_SX = sp.csr_matrix(np.array([[0, 1], [1, 0]], dtype=complex))
_SY = sp.csr_matrix(np.array([[0, -1j], [1j, 0]], dtype=complex))
_SZ = sp.csr_matrix(np.array([[1, 0], [0, -1]], dtype=complex))
_ID = sp.identity(2, format="csr", dtype=complex)


def _site_op(L, m, P):
    """Single-site Pauli P on site m (0-indexed), sparse."""
    ops = [_ID] * L
    ops[m] = P
    out = ops[L - 1]
    for op in reversed(ops[:-1]):
        out = sp.kron(out, op, format="csr")
    # kron(f_{L-1},...,f_0): last factor varies fastest -> bit m <-> site m.
    return out


def _bond_term(L, a, b, delta):
    xa, xb = _site_op(L, a, _SX), _site_op(L, b, _SX)
    ya, yb = _site_op(L, a, _SY), _site_op(L, b, _SY)
    za, zb = _site_op(L, a, _SZ), _site_op(L, b, _SZ)
    return xa @ xb + ya @ yb + delta * (za @ zb)


def odd_bonds(L):
    """0-indexed odd-bond pairs (2j-2, 2j-1), j=1..L/2."""
    return [(2 * j - 2, 2 * j - 1) for j in range(1, L // 2 + 1)]


def even_bonds(L):
    """0-indexed even-bond pairs (2j-1, 2j), j=1..L/2-1 (OBC: no wrap)."""
    return [(2 * j - 1, 2 * j) for j in range(1, L // 2)]


def build_hamiltonian(L, s, delta, sparse=True):
    """Return H(s,δ); sparse CSR by default, dense ndarray if sparse=False."""
    if L % 2:
        raise ValueError(f"L must be even, got {L}")
    H = sp.csr_matrix((2**L, 2**L), dtype=complex)
    for a, b in odd_bonds(L):
        H = H + (1.0 - s) * _bond_term(L, a, b, delta)
    for a, b in even_bonds(L):
        H = H + s * _bond_term(L, a, b, delta)
    return H if sparse else H.toarray()
