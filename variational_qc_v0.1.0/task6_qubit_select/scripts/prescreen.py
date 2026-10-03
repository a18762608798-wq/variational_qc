"""task6 预筛：force 重拉拓扑 → sample 选链（上限1000有向/机兜底）
→ 无向去重（反转视为同一物理链） → 静态粗筛 → survivors 清单。

去重规则 min(链, 反转)：cluster 制备与稳定子集在反转下不变，读出校验
全对称，故物理等价，只留其一。预筛只做减法：剔除含死比特
（build_chains 已滤）或任一边保真度 < EDGE_MIN 的链，不做加权排名。
零真机提交。

运行（项目根）：
  QPY=../../03_tools_practice/qmeas/.CondaPkg/.pixi/envs/default/bin/python
  $QPY task6_qubit_select/scripts/prescreen.py [--cached]

默认 force 重拉两机拓扑；--cached 则用本地缓存（调试/离线用）。
产物：data/prescreen_<chip>.json（含 survivors、dropped、calibration_time）。
"""

import argparse
import json
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve()
TASK6 = HERE.parent.parent

from qmeas.benchmark import (
    BenchmarkConfig,
    bill,
    build_chains,
    fetch_topology,
    is_dead_qubit,
    usable_edges,
)

EDGE_MIN = 0.9


def canonical(chain) -> tuple:
    """无向 canonical：链与其反转取字典序较小者。"""
    t = tuple(chain)
    r = tuple(reversed(chain))
    return min(t, r)


def prescreen_chain(chain, edges, dead) -> str | None:
    """返回剔除原因，无则为 None（保留）。"""
    if any(q in dead for q in chain):
        return "含死比特"
    worst = min(
        edges[(min(a, b), max(a, b))] for a, b in zip(chain, chain[1:])
    )
    if worst < EDGE_MIN:
        return f"最差边保真度 {worst:.3f} < {EDGE_MIN}"
    return None


def main() -> dict:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cached", action="store_true",
                    help="用本地拓扑缓存，不重拉")
    args = ap.parse_args()

    with open(TASK6 / "config" / "grid.toml", "rb") as f:
        g = tomllib.load(f)
    config = BenchmarkConfig(
        chips=g["chips"],
        chain_length=g["chain_length"],
        max_chains_per_chip=g["max_chains_per_chip"],
        shots=g["shots"],
        w_stab=g["w_stab"],
        w_ro=g["w_ro"],
        expansion=g["expansion"],
        output_dir=TASK6 / "data",
        name=g["name"],
        fetch_throttle_interval=g["fetch_throttle_interval"],
    )
    survivors: dict[str, list] = {}
    for chip in config.chips:
        info = fetch_topology(config, chip, force=not args.cached)
        calib = info.get("calibration_time")
        chains, build_dropped = build_chains(
            info, config.chain_length, config.max_chains_per_chip,
            config.expansion,
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
        seen: set[tuple] = set()
        ndup = 0
        for c in chains:
            k = canonical(c)
            if k in seen:
                ndup += 1
                dropped.append({"chain": c, "reason": "反转去重"})
                continue
            seen.add(k)
            reason = prescreen_chain(c, edges, dead)
            if reason is None:
                surv.append(list(k))
            else:
                dropped.append({"chain": c, "reason": reason})
        survivors[chip] = surv
        out = {
            "chip": chip,
            "calibration_time": calib,
            "sampled": len(chains),
            "survivors": surv,
            "dropped": dropped,
        }
        p = TASK6 / "data" / f"prescreen_{chip}.json"
        tmp = p.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False)
        tmp.replace(p)
        print(f"{chip}: 校准 {calib}，采样 {len(chains)} → "
              f"去重 {ndup} → survivors {len(surv)}，"
              f"剔除 {len(dropped) - ndup}")
    print("survivors 账单:", bill(config, survivors))
    print("仅预筛，未提交。人工确认账单后跑 submit.py。")
    return survivors


if __name__ == "__main__":
    main()
