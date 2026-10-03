"""Reference initial states. Authoritative: doc/plan/theory/psi0.md.

All three live in the P=-2 sector for L=4k (Z_tot=0, prodX=+1, R=+1).
Site m (0-indexed) <-> bit m of the basis index.
"""

import numpy as np


def _basis_index(bits):
    return sum(int(b) << m for m, b in enumerate(bits))


def _singlet(L, a, b):
    psi = np.zeros(2**L, dtype=complex)
    ba = [0] * L
    ba[a], ba[b] = 0, 1
    bb = [0] * L
    bb[a], bb[b] = 1, 0
    psi[_basis_index(ba)] = 1.0 / np.sqrt(2.0)
    psi[_basis_index(bb)] = -1.0 / np.sqrt(2.0)
    return psi


def _product_singlets(L, pairs):
    psi = np.zeros(2**L, dtype=complex)
    psi[0] = 1.0
    # multiply singlet factors by explicit tensor assembly over pairs
    for a, b in pairs:
        nxt = np.zeros(2**L, dtype=complex)
        for i in range(2**L):
            amp = psi[i]
            if amp == 0:
                continue
            bits = [(i >> m) & 1 for m in range(L)]
            for va, vb, sgn in ((0, 1, 1.0), (1, 0, -1.0)):
                nb = list(bits)
                nb[a], nb[b] = va, vb
                nxt[_basis_index(nb)] += amp * sgn / np.sqrt(2.0)
        psi = nxt
    return psi


def trivial_state(L):
    """Odd-bond singlet product (s=0 limit)."""
    pairs = [(2 * j, 2 * j + 1) for j in range(L // 2)]
    return _product_singlets(L, pairs)


def topo_state(L):
    """Bulk even singlets + edge (0, L-1) singlet (s=1 limit)."""
    pairs = [(0, L - 1)] + [(2 * j - 1, 2 * j) for j in range(1, L // 2)]
    return _product_singlets(L, pairs)


def afm_state(L):
    """GHZ cat (|0101..> + |1010..>)/sqrt(2)."""
    psi = np.zeros(2**L, dtype=complex)
    a = sum((m % 2) << m for m in range(L))
    b = sum(((m + 1) % 2) << m for m in range(L))
    psi[a] = 1.0 / np.sqrt(2.0)
    psi[b] = 1.0 / np.sqrt(2.0)
    return psi
