"""task6 真机提交：读 survivors 清单 → run_benchmark 并发提交/轮询。

前置：prescreen.py 已产出 data/prescreen_<chip>.json，且账单已人工确认。
每份结果即时 checkpoint；中断重跑只补缺失（runner 内建）。

运行（项目根）：
  export QUARK_TOKEN=...
  $QPY task6_qubit_select/scripts/submit.py
"""

import asyncio
import json
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve()
TASK6 = HERE.parent.parent

from qmeas.benchmark import (
    BenchmarkConfig,
    build_circuits,
    recommend,
    run_benchmark,
    save_report,
)
from qmeas.random import QuarkOptions


def main() -> None:
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
        # 收割提速：平台结果已就绪，轮询并发 20→50（QPS 约 5/s，温和）
        runner_opts=QuarkOptions(max_poll_concurrency=50),
    )
    chains = {}
    for chip in config.chips:
        with open(TASK6 / "data" / f"prescreen_{chip}.json",
                  encoding="utf-8") as f:
            d = json.load(f)
        chains[chip] = [list(c) for c in d["survivors"]]
        print(f"{chip}: survivors {len(chains[chip])} 条 "
              f"(校准 {d['calibration_time']})")
    results = asyncio.run(run_benchmark(config, chains))
    print(f"收回 {len(results)} 条链结果")
    cset = build_circuits(config.chain_length)
    chip, chain, evidence = recommend(
        results, cset, config.w_stab, config.w_ro
    )
    path, _ = save_report(config, chip, chain, evidence)
    print("推荐:", chip, chain)
    print("报告:", path)


if __name__ == "__main__":
    main()
