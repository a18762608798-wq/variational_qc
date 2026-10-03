# task6 真机 8 比特选链

## 解释器

用 `03_tools_practice/qmeas` 项目 env 的 python（已含 quarkstudio、quarkcircuit、qmeas editable），**不另建环境**：

```bash
QMEAS=../../03_tools_practice/qmeas
QPY=$QMEAS/.CondaPkg/.pixi/envs/default/bin/python
```

## 流程（两步闸门）

1. **离线预览**（零机时）：`$QPY scripts/preview.py` —— 拉拓扑（命中缓存零请求）→ sample 选链 → 打印账单。
2. **人工确认账单后**才真机提交（task 2.1，另起提交脚本）。

## 产物

- `data/topology_cache/`：拓扑快照（key 含 calibration_time）
- `data/checkpoints/`：逐份电路结果（中断续跑只补缺失）
- `data/task6_qubit_select_recommendation.json`：最优 `(chip, target_qubits)` + 全候选 evidence
