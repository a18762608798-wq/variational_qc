"""Exact diagonalization. Production = sparse; dense = small-L reference only.

Constitution VIII: dense full-Hilbert-space matrices only for small-system
correctness verification or proven memory/time-safe cases.
"""

import numpy as np
from scipy.sparse.linalg import eigsh

TOL = 1e-10


def ground_state(H, tol=TOL):
    """Lowest eigenpair via sparse eigsh (k=1, SA)."""
    vals, vecs = eigsh(H, k=1, which="SA", tol=tol)
    return float(vals[0].real), np.asarray(vecs[:, 0])


def lowest_two(H, tol=TOL):
    """E0, E1 (, vectors) for raw full-Hilbert-space gaps."""
    vals, vecs = eigsh(H, k=2, which="SA", tol=tol)
    order = np.argsort(vals)
    return (float(vals[order[0]].real), float(vals[order[1]].real),
            np.asarray(vecs[:, order[0]]), np.asarray(vecs[:, order[1]]))


def dense_energies(H, k=2):
    """Independent dense reference (small L only)."""
    w = np.linalg.eigvalsh(H.toarray() if hasattr(H, "toarray") else H)
    return [float(x) for x in np.sort(w)[:k]]
