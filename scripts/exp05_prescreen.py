"""exp05 T002 静态预筛（零机时）：边保真度卫生过滤 → survivors/剔除清单。

读 candidates_{chain,ring}.json（快照锁定），不过滤重跑幂等。
阈值 EDGE_FID_CUTOFF=0.9（plan §3，记入清单 + manifest）。
产物：data/exp05/prescreen_{chain,ring}.json。

--reuse-shenglian-from RUN1：Shenglian 链 survivors 直接沿用上轮
（preview 已保证快照未变）；此处对新鲜快照重做合法性复核，
任一条不通过即中止（顺序即 ckpt 下标，不容漂移）。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from exp05_common import (  # noqa: E402
    DATA_DIR,
    EDGE_FID_CUTOFF,
    write_json,
)

from qmeas.benchmark.config import BenchmarkConfig  # noqa: E402
from qmeas.benchmark.topology import (  # noqa: E402
    chain_is_valid,
    fetch_topology,
    ring_is_valid,
    usable_edges,
)


def edge_fids(cand, edges, ring: bool) -> list[float]:
    pairs = list(zip(cand, cand[1:]))
    if ring:
        pairs.append((cand[-1], cand[0]))
    return [edges[(min(a, b), max(a, b))] for a, b in pairs]


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--reuse-shenglian-from", default=None)
    args = ap.parse_args()
    cfg = BenchmarkConfig(chips=["Baihua", "Shenglian"], output_dir=DATA_DIR,
                          name="exp05_prescreen")
    for kind, n, validator, is_ring in (
        ("chain", 8, chain_is_valid, False),
        ("ring", 10, ring_is_valid, True),
    ):
        cands = json.loads(
            (DATA_DIR / f"candidates_{kind}.json").read_text(
                encoding="utf-8"))["candidates"]
        survivors: dict[str, list] = {}
        dropped: dict[str, list] = {}
        for chip, lst in cands.items():
            info = fetch_topology(cfg, chip)  # 缓存命中，零请求
            if (args.reuse_shenglian_from and kind == "chain"
                    and chip == "Shenglian"):
                edges = usable_edges(info)
                bad = [c for c in lst
                       if not validator(c, info)
                       or min(edge_fids(c, edges, is_ring)) < EDGE_FID_CUTOFF]
                if bad:
                    raise RuntimeError(
                        f"复用 Shenglian 链 {len(bad)} 条对新鲜快照不合法，"
                        f"复用前提已漂移，须全重跑")
                survivors[chip] = list(lst)
                dropped[chip] = []
                print(f"{kind} {chip}：复用上轮 survivors {len(lst)}"
                      f"（新鲜快照复核全过）", flush=True)
                continue
            edges = usable_edges(info)
            surv, drop = [], []
            for c in lst:
                if not validator(c, info):
                    drop.append({"cand": c, "reason": "死比特/重复节点/零保真边"})
                    continue
                fids = edge_fids(c, edges, is_ring)
                if min(fids) < EDGE_FID_CUTOFF:
                    drop.append({"cand": c, "reason": "边保真度<%s" % EDGE_FID_CUTOFF,
                                 "min_edge_fid": min(fids)})
                    continue
                surv.append(c)
            survivors[chip] = surv
            dropped[chip] = drop
            print(f"{kind} {chip}：候选 {len(lst)} → survivors {len(surv)} "
                  f"(剔除 {len(drop)})", flush=True)
        write_json(DATA_DIR / f"prescreen_{kind}.json",
                   {"kind": kind, "length": n,
                    "edge_fid_cutoff": EDGE_FID_CUTOFF,
                    "survivors": survivors, "dropped": dropped})


if __name__ == "__main__":
    main()
