"""task7 预筛：force 重拉拓扑 → 环枚举 → 静态粗筛（含闭合边） → survivors。

只做减法：剔除含死比特（枚举已滤）或任一边（含首尾闭合边）保真度
< EDGE_MIN 的环，不做加权排名。零真机提交。

运行（项目根）：
  QPY=../../03_tools_practice/qmeas/.CondaPkg/.pixi/envs/default/bin/python
  $QPY task7_ring_select/scripts/prescreen.py [--cached]

默认 force 重拉两机拓扑；--cached 则用本地缓存（调试/离线用）。
产物：data/prescreen_<chip>.json（含 survivors、dropped、calibration_time）。
"""

import argparse
import json
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve()
TASK7 = HERE.parent.parent

from qmeas.benchmark import (
    BenchmarkConfig,
    bill,
    build_chains,
    fetch_topology,
    is_dead_qubit,
    usable_edges,
)

EDGE_MIN = 0.9


def ring_pairs(ring):
    return list(zip(ring, ring[1:])) + [(ring[-1], ring[0])]


def prescreen_ring(ring, edges, dead) -> str | None:
    """返回剔除原因，无则为 None（保留）。"""
    if any(q in dead for q in ring):
        return "含死比特"
    worst = min(edges[(min(a, b), max(a, b))] for a, b in ring_pairs(ring))
    if worst < EDGE_MIN:
        return f"最差边保真度 {worst:.3f} < {EDGE_MIN}"
    return None


def main() -> dict:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cached", action="store_true",
                    help="用本地拓扑缓存，不重拉")
    args = ap.parse_args()

    with open(TASK7 / "config" / "grid.toml", "rb") as f:
        g = tomllib.load(f)
    config = BenchmarkConfig(
        chips=g["chips"],
        chain_length=g["chain_length"],
        max_chains_per_chip=g["max_chains_per_chip"],
        shots=g["shots"],
        w_stab=g["w_stab"],
        w_ro=g["w_ro"],
        expansion=g["expansion"],
        shape=g["shape"],
        output_dir=TASK7 / "data",
        name=g["name"],
        fetch_throttle_interval=g["fetch_throttle_interval"],
    )
    survivors: dict[str, list] = {}
    for chip in config.chips:
        info = fetch_topology(config, chip, force=not args.cached)
        calib = info.get("calibration_time")
        rings, build_dropped = build_chains(
            info, config.chain_length, config.max_chains_per_chip,
            config.expansion, shape=config.shape,
        )
        edges = usable_edges(info)
        dead = {
            q.get("index", int(label[1:]))
            for label, q in info.get("qubits_info", {}).items()
            if is_dead_qubit(q)
        }
        surv, dropped = [], [
            {"chain": c, "reason": r} for c, r in build_dropped
        ]
        for c in rings:
            reason = prescreen_ring(c, edges, dead)
            if reason is None:
                surv.append(c)
            else:
                dropped.append({"chain": c, "reason": reason})
        survivors[chip] = surv
        out = {
            "chip": chip,
            "calibration_time": calib,
            "sampled": len(rings),
            "survivors": surv,
            "dropped": dropped,
        }
        p = TASK7 / "data" / f"prescreen_{chip}.json"
        tmp = p.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False)
        tmp.replace(p)
        print(f"{chip}: 校准 {calib}，枚举 {len(rings)} → "
              f"survivors {len(surv)}，剔除 {len(dropped)}")
    print("survivors 账单:", bill(config, survivors))
    print("仅预筛，未提交。人工确认账单后跑 submit.py。")
    return survivors


if __name__ == "__main__":
    main()
