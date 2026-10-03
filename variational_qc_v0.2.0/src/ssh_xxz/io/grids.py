"""Canonical frozen coordinate definitions (Binding Clarifications CL-001/1A).

Single source of truth: experiments 01/02 MUST import these arrays,
never regenerate their own (contracts/grid-01-02.md rule 1).
"""

import numpy as np

S_GRID = np.arange(1, 50) / 50.0
D_GRID = 3.0 * np.arange(1, 50) / 50.0

REPS = {
    "trivial": (0.02, 0.06),
    "topological": (0.98, 0.06),
    "afm": (0.50, 2.94),
}


def q_grid(n_points=49):
    """Frozen S(q) sampling: n_points over [0, 2π]; q=π explicit.

    Default 49: q_k = 2πk/48 with π at k=24 (contract q-reconstruction §5).
    S(q) is 2π-periodic; the duplicated endpoint carries no extra physics.
    """
    q = np.linspace(0.0, 2.0 * np.pi, n_points)
    assert np.pi in q  # explicit-pi binding constraint
    return q
