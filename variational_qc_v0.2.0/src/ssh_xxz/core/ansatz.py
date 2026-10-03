"""Orbit ansatz. Authoritative: doc/plan/theory/ansatz.md.

Reflection pairs share angles (orbits); delta=1 halves (θ1=θ2);
sublayer order follows the F-rule; layers act F1,S1,F2,S2,... (fixed order).
New layers append at the END, so p-1 params zero-pad into p (nesting).
"""

import numpy as np
from qiskit import QuantumCircuit

_FIRST = {"trivial": "e", "topological": "o", "afm": "e"}


def _orbits(L):
    M = L // 2
    odd = [[(2 * j - 2, 2 * j - 1) for j in (jj, M + 1 - jj)] for jj in range(1, M + 1)]
    odd = [sorted(set(b)) for b in odd]
    odd = [b for i, b in enumerate(odd) if b not in odd[:i]]
    even = [[(2 * j - 1, 2 * j) for j in (jj, M - jj)] for jj in range(1, M)]
    even = [sorted(set(b)) for b in even]
    even = [b for i, b in enumerate(even) if b not in even[:i]]
    return odd, even


def n_orbits(L):
    odd, even = _orbits(L)
    return len(odd) + len(even)


def n_params(L, p, delta):
    per_layer = L if delta != 1 else L // 2
    return per_layer * p


def layer_order(init):
    f = _FIRST[init]
    s = "o" if f == "e" else "e"
    return [f, s]


def _apply_sublayer(circ, bonds, t1, t2):
    for a, b in bonds:
        circ.rxx(t1, a, b)
        circ.ryy(t1, a, b)
        circ.rzz(t2, a, b)


def build_circuit(L, p, delta, init, theta):
    """Build the p-layer orbit circuit; metadata carries sublayer_seq/state_key."""
    theta = np.asarray(theta, dtype=float)
    odd, even = _orbits(L)
    sub = {"o": odd, "e": even}
    f, s = layer_order(init)
    per_layer = L if delta != 1 else L // 2
    if theta.size != per_layer * p:
        raise ValueError(f"expected {per_layer * p} params, got {theta.size}")
    circ = QuantumCircuit(L)
    seq = []
    k = 0
    for _ in range(p):
        for kind in (f, s):
            orbits = sub[kind]
            for orb in orbits:
                if delta != 1:
                    t1, t2 = float(theta[k]), float(theta[k + 1])
                    k += 2
                else:
                    t1 = t2 = float(theta[k])
                    k += 1
                _apply_sublayer(circ, orb, t1, t2)
            seq.append(kind)
    circ.metadata = {
        "sublayer_seq": seq,
        # Effective-state key: trailing all-zero (identity) layers stripped,
        # so an embedded p-1 state keys identically to its p-1 circuit.
        "state_key": (init, _strip_trailing_identity(theta, per_layer)),
    }
    return circ


def _strip_trailing_identity(theta, per_layer):
    key = tuple(np.round(theta, 12))
    while len(key) >= per_layer and all(v == 0 for v in key[-per_layer:]):
        key = key[:-per_layer]
    return key


def embed_params(theta_pm1, L, p, delta, init):
    """Zero-pad a (p-1)-layer vector into p-layer space (nesting)."""
    theta_pm1 = np.asarray(theta_pm1, dtype=float)
    new = np.zeros(n_params(L, 1, delta))
    return np.concatenate([theta_pm1, new])
