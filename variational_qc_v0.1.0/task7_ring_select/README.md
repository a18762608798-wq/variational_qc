# task7 真机 10-环选优

## 解释器

用 `03_tools_practice/qmeas` 项目 env 的 python（已含 quarkstudio、quarkcircuit、qmeas editable），**不另建环境**：

```bash
QMEAS=../../03_tools_practice/qmeas
QPY=$QMEAS/.CondaPkg/.pixi/envs/default/bin/python
```

## 流程（两步闸门）

1. **离线预览**（零机时）：`$QPY scripts/preview.py` —— 拉拓扑（命中缓存零请求）→ 环枚举 → 打印账单。
2. **预筛**：`$QPY scripts/prescreen.py`（默认 force 重拉拓扑）→ survivors 清单。
3. **人工确认账单后**才跑 `$QPY scripts/submit.py` 真机提交。

## 环与链的区别

- 制备多 1 个闭合 CZ（10 个），稳定子全为三体（指标模 10），无端点二体项。
- 环推荐独立，不与链混排比较。
- `find_rings` 自带旋转/翻转去重，无需 task 侧二次去重。

## 产物

- `data/topology_cache/`：拓扑快照（key 含 calibration_time）
- `data/prescreen_<chip>.json`：survivors/剔除清单
- `data/checkpoints/`：逐份电路结果（中断续跑只补缺失）
- `data/task7_ring_select_recommendation.json`：最优环 + 全候选 evidence
