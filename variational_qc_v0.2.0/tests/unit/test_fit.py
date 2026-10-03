"""T025: free-intercept polyfit post-processing (CL-002, V.5). FAIL-first."""

import numpy as np
import pytest

from plotting.diagnostic.exp01_scaling import fit_scaling


def test_free_intercept_recovers_ab():
    inv_L = np.array([1 / 4, 1 / 8, 1 / 12, 1 / 16])
    gaps = 2.5 * inv_L + 0.03
    a, b = fit_scaling(inv_L, gaps)
    assert a == pytest.approx(2.5)
    assert b == pytest.approx(0.03)
