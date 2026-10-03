"""task7 真机提交：读 survivors 清单 → run_benchmark 并发提交/轮询。

前置：prescreen.py 已产出 data/prescreen_<chip>.json，且账单已人工确认。
两阶段全提交（防插队）+ 每份结果即时 checkpoint；中断重跑只补缺失，
有 tid 只轮询不重提（runner 内建）。

运行（项目根）：
  export QUARK_TOKEN=...
  $QPY task7_ring_select/scripts/submit.py
"""

import asyncio
import json
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve()
TASK7 = HERE.parent.parent

from qmeas.benchmark import (
    BenchmarkConfig,
    build_circuits,
    recommend,
    run_benchmark,
    save_report,
)
from qmeas.random import QuarkOptions


def main() -> None:
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
        # 收割并发（task6 实测 20 偏慢，50 温和提速）
        runner_opts=QuarkOptions(max_poll_concurrency=50),
    )
    chains = {}
    for chip in config.chips:
        with open(TASK7 / "data" / f"prescreen_{chip}.json",
                  encoding="utf-8") as f:
            d = json.load(f)
        chains[chip] = [list(c) for c in d["survivors"]]
        print(f"{chip}: survivors {len(chains[chip])} 个 "
              f"(校准 {d['calibration_time']})")
    results = asyncio.run(run_benchmark(config, chains))
    print(f"收回 {len(results)} 个环结果")
    cset = build_circuits(config.chain_length, ring=True)
    chip, chain, evidence = recommend(
        results, cset, config.w_stab, config.w_ro
    )
    path, _ = save_report(config, chip, chain, evidence)
    print("推荐:", chip, chain)
    print("报告:", path)


if __name__ == "__main__":
    main()
