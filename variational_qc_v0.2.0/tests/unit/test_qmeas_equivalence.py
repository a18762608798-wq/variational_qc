"""T012: 5-point 1e-10 qmeas-vs-native equivalence (II.5, grid §5). FAIL-first."""

import numpy as np

from ssh_xxz.adapters.qmeas_adapter import qmeas_hamiltonian
from ssh_xxz.core.hamiltonian import build_hamiltonian

POINTS = [(0.02, 0.06), (0.98, 0.06), (0.50, 2.94), (0.50, 1.02), (0.98, 2.94)]


def test_equivalence_five_points():
    for s, d in POINTS:
        a = qmeas_hamiltonian(8, s, d).toarray()
        b = build_hamiltonian(8, s, d, sparse=False)
        assert np.max(np.abs(a - b)) < 1e-10
