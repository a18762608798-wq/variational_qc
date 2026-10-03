"""T042: tau violation flag (AS-04.4). FAIL-first."""

import numpy as np

TAU = 1e-6


def _check(evar, e0):
    from experiments.exp04_ideal import check_variational_principle

    return check_variational_principle(evar, e0, TAU)


def test_pass_above():
    assert _check(-3.0, -3.0) == "ok"


def test_violation_below_tau():
    assert _check(-3.0 - 2e-6, -3.0) == "failed"


def test_tolerance_band():
    assert _check(-3.0 - 5e-7, -3.0) == "ok"
