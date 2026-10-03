"""T024: SC-001 rebuild-from-saved-data integration. FAIL-first.

Runs a 2x2 mini grid + 2-point gap subset, then rebuilds all three
figures from saved data only and asserts output files exist.
"""

import matplotlib

matplotlib.use("Agg")

import experiments.exp01_phase as e1
import plotting.diagnostic.exp01 as d1
import plotting.pra.exp01 as p1


def test_sc001_mini_rebuild(tmp_path):
    data = tmp_path / "exp01"
    data.mkdir()
    e1.run_grid(str(data), s_grid=[0.5, 0.52], d_grid=[0.96, 1.02])
    e1.run_gaps(str(data), Ls=[4, 8], s_grid=[0.5, 0.52])
    out_d = tmp_path / "diag"
    out_p = tmp_path / "pra"
    made = d1.rebuild_all(str(data), str(out_d)) + p1.rebuild_all(str(data), str(out_p))
    assert len(made) == 6  # 3 diagnostic + 3 PRA figures
