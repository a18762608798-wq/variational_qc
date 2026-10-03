"""T043: nesting clamp (AS-04.5). FAIL-first."""

import numpy as np


def test_clamp_keeps_baseline():
    from experiments.exp04_ideal import apply_nesting_clamp

    base = (np.zeros(8), -3.0)
    worse = (np.ones(8), -2.5)
    x, f, flag = apply_nesting_clamp([worse], base, 1e-6)
    assert f == -3.0 and flag is True


def test_better_result_accepted():
    from experiments.exp04_ideal import apply_nesting_clamp

    base = (np.zeros(8), -3.0)
    better = (np.ones(8), -3.5)
    x, f, flag = apply_nesting_clamp([better], base, 1e-6)
    assert f == -3.5 and flag is False
