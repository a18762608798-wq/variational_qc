"""task6 离线预览：拓扑（缓存优先）→ sample 选链 → 账单，零真机提交。

运行（项目根）：
  QPY=../../03_tools_practice/qmeas/.CondaPkg/.pixi/envs/default/bin/python
  $QPY task6_qubit_select/scripts/preview.py
"""

import tomllib
from pathlib import Path

HERE = Path(__file__).resolve()
TASK6 = HERE.parent.parent

from qmeas.benchmark import BenchmarkConfig, bill, build_chains, fetch_topology


def main() -> dict:
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
        output_dir=TASK6 / g["output_dir"].split("/", 1)[1],
        name=g["name"],
        fetch_throttle_interval=g["fetch_throttle_interval"],
    )
    chains = {}
    for chip in config.chips:
        info = fetch_topology(config, chip)
        ch, dropped = build_chains(
            info, config.chain_length, config.max_chains_per_chip,
            config.expansion,
        )
        chains[chip] = ch
        print(f"{chip}: 校准 {info.get('calibration_time')}，"
              f"候选 {len(ch)} 条，丢弃 {len(dropped)} 条")
        for c in ch[:10]:
            print("   ", c)
        if len(ch) > 10:
            print(f"    ...（共 {len(ch)} 条）")
    print("账单:", bill(config, chains))
    print("仅预览，未提交。确认账单后进入 task 2.1 真机提交。")
    return chains


if __name__ == "__main__":
    main()
