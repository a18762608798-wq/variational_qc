"""T038: SC-003 count integration (98 records). FAIL-first."""

import experiments.exp03_reference as e3


def test_sc003_mini_counts(tmp_path):
    data = tmp_path / "exp03"
    data.mkdir()
    n = e3.run_reference(str(data), deltas=[1.0], s_grid=[0.1, 0.5, 0.9])
    assert n == 3
    recs = list(e3.iter_reference(str(data)))
    assert len(recs) == 3
    assert all({"E0", "Spi", "Ostr"} <= set(r) for r in recs)
