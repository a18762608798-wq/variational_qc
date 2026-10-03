"""Resume regression: second run over the same dir computes nothing new.

Guards the point_exists/save_point hash-consistency bug (resume silently
recomputing everything, then false 'incompatible' conflicts from ARPACK
last-ulp nondeterminism).
"""

import experiments.exp01_phase as e1


def test_rerun_computes_nothing(tmp_path):
    data = tmp_path / "exp01"
    data.mkdir()
    n1 = e1.run_grid(str(data), s_grid=[0.5], d_grid=[1.02])
    n2 = e1.run_grid(str(data), s_grid=[0.5], d_grid=[1.02])
    assert n1 == 1
    assert n2 == 0
