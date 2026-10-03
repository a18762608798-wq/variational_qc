"""T044: SC-004/005 integration (counts + tau, tiny subset). FAIL-first."""

import experiments.exp04_ideal as e4


def test_sc004_005_mini(tmp_path):
    ref = tmp_path / "ref"
    var = tmp_path / "var"
    ref.mkdir()
    var.mkdir()
    import experiments.exp03_reference as e3

    e3.run_reference(str(ref), deltas=[1.0], s_grid=[0.5])
    n = e4.run_branches(str(var), str(ref), deltas=[1.0], s_grid=[0.5],
                        depths=[1], branches=["trivial"], de_budget=(5, 3))
    assert n == 1
    rep = e4.verify_selection(str(var), str(ref), tau=1e-6)
    assert rep["n_selected"] == 1
    assert rep["n_violations"] == 0
