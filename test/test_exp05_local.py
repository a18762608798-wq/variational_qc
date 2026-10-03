"""exp05 本地单元测试（T006）：纯逻辑，零真机调用。

qmeas env python -m pytest test/test_exp05_local.py
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from exp05_common import (  # noqa: E402
    canonical_chain,
    canonical_ring,
    dedup_chains,
    match_subchain,
    subchain_windows,
    tie_group,
)


def test_chain_undirected_dedup():
    chains = [[1, 2, 3, 4], [4, 3, 2, 1], [1, 2, 3, 5], [1, 2, 3, 4]]
    out = dedup_chains(chains)
    assert out == [[1, 2, 3, 4], [1, 2, 3, 5]]
    assert canonical_chain([4, 3, 2, 1]) == (1, 2, 3, 4)


def test_ring_rotation_flip_canonical():
    a = [3, 1, 2, 4, 5, 6, 7, 8, 9, 10]
    rot = a[4:] + a[:4]
    flip = list(reversed(a))
    assert canonical_ring(a) == canonical_ring(rot) == canonical_ring(flip)


def test_d09_windows_include_closure():
    ring = list(range(10))
    wins = subchain_windows(ring, 8)
    assert len(wins) == 10
    assert wins[0] == list(range(8))
    # 跨接缝闭合段
    assert wins[9] == [9, 0, 1, 2, 3, 4, 5, 6]
    assert wins[5] == [5, 6, 7, 8, 9, 0, 1, 2]


def test_match_subchain_chip_and_reverse():
    ev = [
        {"chip": "Baihua", "chain": [1, 2, 3, 4, 5, 6, 7, 8]},
        {"chip": "Shenglian", "chain": [1, 2, 3, 4, 5, 6, 7, 8]},
    ]
    # 反转匹配 + 同芯片约束
    hit = match_subchain([8, 7, 6, 5, 4, 3, 2, 1], "Shenglian", ev)
    assert hit is ev[1]
    assert match_subchain([1, 2, 3, 4, 5, 6, 7, 9], "Baihua", ev) is None


def test_tie_boundary():
    ranked = [
        {"score": 0.7700},
        {"score": 0.7501},  # 分差 0.0199 < 0.02 → 并列
        {"score": 0.7499},  # 分差 0.0201 ≥ 0.02 → 不并列
    ]
    tied = tie_group(ranked)
    assert tied == ranked[:2]
    assert tie_group([]) == []


def test_score_chain_handcalc():
    qmeas = pytest.importorskip("qmeas.benchmark.scoring")
    circuits = pytest.importorskip("qmeas.benchmark.circuits")
    cs = circuits.build_circuits(2, ring=False)
    # 理想：稳定子全 +1（全零计数），读出半对半
    counts = {
        "stab_g0": {"00": 100}, "stab_g1": {"00": 100},
        "allzero": {"00": 100}, "allone": {"00": 100},
    }
    m, f, s = qmeas.score_chain(counts, cs.stab_groups, 100)
    assert m == pytest.approx(1.0)
    assert f == pytest.approx(0.5)
    assert s == pytest.approx(0.8 * 1.0 + 0.2 * 0.5)
    # 全对：F_ro = 1 → score = 1
    counts["allone"] = {"11": 100}
    m, f, s = qmeas.score_chain(counts, cs.stab_groups, 100)
    assert (m, f, s) == pytest.approx((1.0, 1.0, 1.0))
