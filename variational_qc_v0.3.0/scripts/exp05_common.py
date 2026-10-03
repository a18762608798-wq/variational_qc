"""exp05 真机优质比特：纯本地共享函数（零真机调用）。

供 exp05_preview / prescreen / submit / assemble / verify 与 pytest 共用。
打分本身复用 qmeas.benchmark.scoring.score_chain，此处只放编排侧纯逻辑。
"""

from __future__ import annotations

import json
from pathlib import Path

# 与项目其他实验保持一致的种子根（见 exp04 manifest MASTER_SEED）。
MASTER_SEED = 20261004

# spec §3：冠军并列阈值（clarify Q5 用户确认）。
TIE_TOL = 0.02

# spec §3 / plan §3：静态边保真度卫生过滤阈值。
EDGE_FID_CUTOFF = 0.9

# plan §3：采样排序聚合函数（边保真度和；定长链下与均值排序等价）。
RNG_SEED = MASTER_SEED

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "exp05"


def canonical_chain(chain: list[int]) -> tuple[int, ...]:
    """无向去重范式：链与其反转视为同一候选（spec §3）。"""
    t = tuple(chain)
    return min(t, t[::-1])


def dedup_chains(chains: list[list[int]]) -> list[list[int]]:
    """保持首见顺序的无向去重。"""
    seen: set[tuple[int, ...]] = set()
    out: list[list[int]] = []
    for c in chains:
        k = canonical_chain(c)
        if k not in seen:
            seen.add(k)
            out.append(list(c))
    return out


def canonical_ring(ring: list[int]) -> tuple[int, ...]:
    """旋转/翻转等价范式（与 qmeas.find_rings 归一一致：首元最小，正反取字典序小者）。"""
    n = len(ring)
    rots = [tuple(ring[i:] + ring[:i]) for i in range(n)]
    best = min(rots)
    rev = list(reversed(ring))
    rots_rev = [tuple(rev[i:] + rev[:i]) for i in range(n)]
    return min(best, min(rots_rev))


def subchain_windows(ring: list[int], length: int = 8) -> list[list[int]]:
    """冠军环内连续子链滑窗（含跨接缝闭合段），共 len(ring) 条（spec D09）。"""
    n = len(ring)
    return [ring[i:i + length] if i + length <= n
            else ring[i:] + ring[:i + length - n]
            for i in range(n)]


def match_subchain(sub: list[int], chip: str, evidence: list[dict]) -> dict | None:
    """在链 evidence 中匹配子链（同芯片 + 序列相等或反转相等）。

    evidence 条目须含 'chip' 与 'chain' 键。返回命中条目，否则 None。
    """
    key = canonical_chain(sub)
    for e in evidence:
        if e["chip"] == chip and canonical_chain(e["chain"]) == key:
            return e
    return None


def tie_group(ranked: list[dict], tol: float = TIE_TOL) -> list[dict]:
    """首名并列组：score 与第 1 名分差 < tol 者全部记入（spec §3 S04）。"""
    if not ranked:
        return []
    top = ranked[0]["score"]
    return [r for r in ranked if top - r["score"] < tol]


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)
