"""Observables. Authoritative: doc/plan/theory/topological_op.md.

S(q) = (1/L) Σ_ij e^{iq(i-j)} <ZiZj>; S(π) at q=π;
O_str(d=L/2-1) per doc; Q = 4/3 + 2 Ostr − S(π)/6 (derived only);
Z̃R with middle-2n block (n=L/4) and mirror R_I.
Site m (0-indexed) <-> bit m.
"""

import numpy as np


def _bits_matrix(L):
    n = 2**L
    idx = np.arange(n)[:, None]
    return ((idx >> np.arange(L)) & 1) * 2 - 1  # +1 for |1>, -1 for |0>


def _parity_sign(i, j):
    return np.where(((i - j) % 2) == 0, 1.0, -1.0)


def zz_corr(psi, L):
    probs = (np.abs(psi) ** 2).real
    z = _bits_matrix(L)
    return (z.T * probs) @ z


def structure_factor(psi, L, q_array):
    C = zz_corr(psi, L)
    i = np.arange(L)[:, None]
    j = np.arange(L)[None, :]
    out = []
    for q in np.atleast_1d(q_array):
        out.append((np.exp(1j * q * (i - j)) * C).sum().real / L)
    return np.array(out)


def s_pi(psi, L):
    C = zz_corr(psi, L)
    i = np.arange(L)[:, None]
    j = np.arange(L)[None, :]
    return float((_parity_sign(i, j) * C).sum().real / L)


def string_order(psi, L):
    # 1-indexed doc formula, converted: (Z0+Z1)[Π(-Z Z)](Z_{L-2}+Z_{L-1}).
    d = L // 2 - 1
    z = _bits_matrix(L)
    n = z.shape[0]
    val = z[:, 0] + z[:, 1]
    for l in range(1, d):
        val = val * (-z[:, 2 * l] * z[:, 2 * l + 1])
    val = val * (z[:, 2 * d] + z[:, 2 * d + 1])
    return float(np.sum((np.abs(psi) ** 2).real * val))


def q_diagnostic(s_pi_val, ostr_val):
    return 4.0 / 3.0 + 2.0 * ostr_val - s_pi_val / 6.0


def z_tilde_R(psi, L):
    """Normalized ZR with middle 2n block, n = L/4 (vectorized partial trace)."""
    psi = np.asarray(psi, dtype=complex)
    n = L // 4
    start = L // 2 - n
    block = list(range(start, start + 2 * n))
    rest = [m for m in range(L) if m not in block]
    N = 2**L
    bits = ((np.arange(N)[:, None] >> np.arange(L)) & 1)
    BI = bits[:, block]
    pw = 1 << np.arange(len(block))
    RI = BI @ pw
    same_rest = np.ones((N, N), dtype=bool)
    for m in rest:
        same_rest &= bits[:, m][:, None] == bits[:, m][None, :]
    P = psi[:, None] * psi[None, :].conj()
    dim = 2 ** len(block)
    rho = np.zeros((dim, dim), dtype=complex)
    I = np.repeat(RI, N)
    J = np.tile(RI, N)
    M = same_rest.reshape(-1)
    np.add.at(rho, (I[M], J[M]), P.reshape(-1)[M])
    # mirror within block: p[b] = bit-reversal of the 2n-bit block index b.
    # Decoupled from full-basis numbering (prior bug summed a rest-
    # contaminated subset and returned non-negative garbage).
    nb = len(block)
    rev = np.array([int(f"{b:0{nb}b}"[::-1], 2) for b in range(dim)])
    z_r = rho[rev, np.arange(dim)].sum()
    # purities of the two halves
    h = len(block) // 2
    # reshape (b,a,b',a'): low h bits = first half (a), high = second (b)
    r4 = rho.reshape((2**h, 2**h, 2**h, 2**h))
    rho1 = r4.trace(axis1=0, axis2=2)  # trace second half -> (a,a')
    rho2 = r4.trace(axis1=1, axis2=3)  # trace first half -> (b,b')
    p1 = np.trace(rho1 @ rho1).real
    p2 = np.trace(rho2 @ rho2).real
    return float((z_r / np.sqrt((p1 + p2) / 2.0)).real)
