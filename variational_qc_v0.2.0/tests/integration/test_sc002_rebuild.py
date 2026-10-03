"""T032: SC-002 rebuild integration. FAIL-first.

Mini 2x2 observable grid + 3 S(q) curves, then rebuild comparison +
four heatmaps from saved data only.
"""

import matplotlib

matplotlib.use("Agg")

import experiments.exp02_observables as e2
import plotting.diagnostic.exp02 as d2
import plotting.pra.exp02 as p2


def test_sc002_mini_rebuild(tmp_path):
    data = tmp_path / "exp02"
    data.mkdir()
    e2.run_heatmaps(str(data), s_grid=[0.02, 0.5], d_grid=[0.06, 2.94])
    e2.run_sq_curves(str(data))
    out_d = tmp_path / "diag"
    out_p = tmp_path / "pra"
    made = d2.rebuild_all(str(data), str(out_d)) + p2.rebuild_all(str(data), str(out_p))
    assert len(made) == 10  # 5 diagnostic + 5 PRA figures
