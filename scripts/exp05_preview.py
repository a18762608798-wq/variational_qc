"""exp05 T001 离线预览（零机时）：拉拓扑 → 枚举 → 去重截断 → 打印账单。

必须用 qmeas env python 运行（含 qmeas editable + quarkstudio）：
  QPY=../../03_tools_practice/qmeas/.CondaPkg/.pixi/envs/default/bin/python
  $QPY scripts/exp05_preview.py [--force-fetch]

backend() 元数据调用不消耗机时；账单经人工确认后才可进入 submit。
产物：data/exp05/candidates_{chain,ring}.json + data/exp05/bill.json。

--reuse-shenglian-from RUN1：Shenglian 链复用上轮 survivors（省 2/3 账单），
前提是新鲜拓扑 calibration_time 与上轮一致，否则中止（须全重跑）；
Baihua 与环（两芯片）一律新鲜枚举。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from exp05_common import (  # noqa: E402
    DATA_DIR,
    RNG_SEED,
    dedup_chains,
    read_json,
    write_json,
)

from qmeas.benchmark.config import BenchmarkConfig  # noqa: E402
from qmeas.benchmark.runner import bill  # noqa: E402
from qmeas.benchmark.topology import (  # noqa: E402
    build_chains,
    fetch_topology,
    find_rings,
    usable_edges,
)

CHIPS = ["Baihua", "Shenglian"]
CHAIN_LEN = 8
RING_LEN = 10
MAX_CHAINS_PER_CHIP = 3000
SHOTS = 2048


def make_config(shape: str, length: int) -> BenchmarkConfig:
    return BenchmarkConfig(
        chips=list(CHIPS),
        chain_length=length,
        max_chains_per_chip=MAX_CHAINS_PER_CHIP,
        shots=SHOTS,
        w_stab=0.8,
        w_ro=0.2,
        expansion="sample",
        shape=shape,
        output_dir=DATA_DIR,
        name=f"exp05_{shape}",
    )


def edge_sum(chain, edges) -> float:
    pairs = list(zip(chain, chain[1:])) + ([(chain[-1], chain[0])]
                                           if len(chain) == RING_LEN else [])
    return sum(edges[(min(a, b), max(a, b))] for a, b in pairs)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force-fetch", action="store_true",
                    help="强制刷新拓扑快照（默认缓存优先）")
    ap.add_argument("--reuse-shenglian-from", default=None,
                    help="复用上轮 Shenglian 链 survivors 的归档目录 "
                         "(如 data/exp05_run1_20261003)")
    args = ap.parse_args()

    cfg_chain = make_config("chain", CHAIN_LEN)
    snapshots: dict[str, str] = {}
    infos: dict = {}
    for chip in CHIPS:
        info = fetch_topology(cfg_chain, chip, force=True)
        infos[chip] = info
        snapshots[chip] = info.get("calibration_time", "unknown")

    reuse_dir = None
    reuse_snap = None
    if args.reuse_shenglian_from:
        from pathlib import Path as _P
        reuse_dir = _P(args.reuse_shenglian_from)
        old_bill = read_json(reuse_dir / "bill.json")
        reuse_snap = old_bill["snapshots"]["Shenglian"]
        if snapshots["Shenglian"] != reuse_snap:
            raise RuntimeError(
                f"Shenglian 已重校准（{reuse_snap} → {snapshots['Shenglian']}），"
                f"复用前提不成立，须全重跑（去掉 --reuse-shenglian-from）")
        print(f"Shenglian 快照未变（{reuse_snap}），复用上轮链 survivors",
              flush=True)

    # --- 链：sample 枚举 + 无向去重（内核 sample_chains 只做 tuple 级去重，
    # 反转元组视为不同，故此处按 min(链,反转) 二次去重，spec PRE-001）→ 截断 ---
    cand_chain: dict[str, list] = {}
    for chip in CHIPS:
        if reuse_dir is not None and chip == "Shenglian":
            # 复用上轮 prescreen survivors（已去重过滤，顺序即 ckpt 下标）。
            pre = read_json(reuse_dir / "prescreen_chain.json")
            cand_chain[chip] = pre["survivors"][chip]
            print(f"链 {chip}：复用上轮 survivors {len(cand_chain[chip])}",
                  flush=True)
            continue
        raw, _ = build_chains(infos[chip], CHAIN_LEN, MAX_CHAINS_PER_CHIP,
                              "sample", "chain")
        dedup = dedup_chains(raw)
        # sample_chains 已按边保真度"和"降序；定长 8 链（7 条边）和≡均值排序等价。
        cand_chain[chip] = dedup[:MAX_CHAINS_PER_CHIP]
        print(f"链 {chip}：枚举 {len(raw)} → 去重 {len(dedup)} "
              f"→ 截断 {len(cand_chain[chip])}", flush=True)

    # --- 环：全枚举全测（find_rings 自带旋转/翻转去重），按边和降序 ---
    cand_ring: dict[str, list] = {}
    for chip in CHIPS:
        rings = find_rings(infos[chip], RING_LEN)
        edges = usable_edges(infos[chip])
        rings.sort(key=lambda c: edge_sum(c, edges), reverse=True)
        cand_ring[chip] = rings
        print(f"环 {chip}：全枚举 {len(rings)}", flush=True)

    write_json(DATA_DIR / "candidates_chain.json",
               {"chips": CHIPS, "length": CHAIN_LEN, "snapshots": snapshots,
                "rng_seed": RNG_SEED, "candidates": cand_chain})
    write_json(DATA_DIR / "candidates_ring.json",
               {"chips": CHIPS, "length": RING_LEN, "snapshots": snapshots,
                "candidates": cand_ring})

    b_chain = bill(cfg_chain, cand_chain)
    cfg_ring = make_config("ring", RING_LEN)
    b_ring = bill(cfg_ring, cand_ring)
    total_tasks = b_chain["total_tasks"] + b_ring["total_tasks"]
    total_shots = b_chain["total_shots"] + b_ring["total_shots"]
    print("---- 账单 ----")
    print(f"链：{b_chain['total_tasks']} 任务 × {SHOTS} shots")
    print(f"环：{b_ring['total_tasks']} 任务 × {SHOTS} shots")
    print(f"合计：{total_tasks} 任务，{total_shots} shots")
    print(f"快照：{snapshots}")
    write_json(DATA_DIR / "bill.json",
               {"chain": b_chain, "ring": b_ring,
                "total_tasks": total_tasks, "total_shots": total_shots,
                "shots_per_task": SHOTS, "snapshots": snapshots,
                "rng_seed": RNG_SEED, "confirmed": False,
                "reused_shenglian_from": (str(reuse_dir) if reuse_dir else None),
                "reused_shenglian_snapshot": reuse_snap,
                "note": "人工确认后置 confirmed=true 才可 submit"})
    # 打印既有 bill 供复核（若本次命中缓存、非 fresh）
    _ = read_json(DATA_DIR / "bill.json")
    print("账单已落盘 data/exp05/bill.json（confirmed=false），待人工确认。")


if __name__ == "__main__":
    main()
