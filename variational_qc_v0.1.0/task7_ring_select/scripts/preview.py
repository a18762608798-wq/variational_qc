"""task7 离线预览：拓扑（缓存优先）→ 环枚举 → 账单，零真机提交。

运行（项目根）：
  QPY=../../03_tools_practice/qmeas/.CondaPkg/.pixi/envs/default/bin/python
  $QPY task7_ring_select/scripts/preview.py
"""

import tomllib
from pathlib import Path

HERE = Path(__file__).resolve()
TASK7 = HERE.parent.parent

from qmeas.benchmark import BenchmarkConfig, bill, build_chains, fetch_topology


def main() -> dict:
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
    chains = {}
    for chip in config.chips:
        info = fetch_topology(config, chip)
        ch, dropped = build_chains(
            info, config.chain_length, config.max_chains_per_chip,
            config.expansion, shape=config.shape,
        )
        chains[chip] = ch
        print(f"{chip}: 校准 {info.get('calibration_time')}，"
              f"候选环 {len(ch)} 个，丢弃 {len(dropped)} 条")
        for c in ch:
            print("   ", c)
    print("账单:", bill(config, chains))
    print("仅预览，未提交。确认账单后进入 task 1.2/2.1 真机提交。")
    return chains


if __name__ == "__main__":
    main()
