"""T009: physical cost + min-over-branches/restarts selection. FAIL-first."""

from ssh_xxz.core.cost import select_branch


def test_select_min_energy_branch():
    res = {"trivial": 1.5, "topological": 0.5, "afm": 2.0}
    assert select_branch(res) == ("topological", 0.5)


def test_select_min_restart():
    assert select_branch({"a": 1.0}, restarts=[1.0, 0.7, 0.9]) == ("a", 0.7)
