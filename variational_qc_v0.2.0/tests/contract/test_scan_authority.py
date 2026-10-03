"""T037: 03->04 s-authority contract (AS-03.3, scan-03-04 rule 1). FAIL-first."""

import experiments.exp03_reference as e3
import experiments.exp04_ideal as e4


def test_authoritative_s_array():
    assert e4.S_REF is e3.S_REF  # 04 loads 03's array; never regenerates
    assert list(e4.S_REF) == [i / 50 for i in range(1, 50)]
