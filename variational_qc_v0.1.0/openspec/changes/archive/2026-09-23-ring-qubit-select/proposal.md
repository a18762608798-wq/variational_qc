# Proposal

## Why

task6 用 8 比特线性链选出 Baihua 67–76 邻域，但 VQE 拟态在周期边界下对应的是**环**：环 cluster 态多一个闭合 CZ，稳定子全为三体（无端点二体项），对门误差更敏感。环质量不能从链分数外推，必须独立实测。qmeas 新增 `shape="ring"` 全套支撑（环枚举、环稳定子、环 coupling），现在是跑环任务的时机。

## What Changes

- 在 `04_project/variational_param` 下新增 task7（`task7_ring_select/`）：真机 10 环选优任务，结构对齐 task6（config+scripts+data+README/ANALYSIS）。
- 复用 qmeas benchmark ring 管线（`find_rings` 全枚举、`build_circuits(n, ring=True)`、`shape="ring"` 提交），task7 只做配置、执行与存档。
- 两机 10-环全测（Baihua 4 + Shenglian 9 = 13 环，枚举已验证池子极小，无需采样），1024 shots，打分权重沿用默认（`w_stab=0.8`、`w_ro=0.2`，与链可比）。
- 环自成一次推荐，只内部比较，不与链混排；先离线预览（拓扑→环枚举→账单，零机时）再真机提交；checkpoint 断点续跑，推荐报告供后续真机任务回填。

## Capabilities

### New Capabilities

- `hardware/ring-qubit-select`: 在 Baihua/Shenglian 上枚举候选 10-环并用环基准电路打分排序，输出最优环与 evidence 报告。

### Modified Capabilities

（无）

## Impact

- 新增 `task7_ring_select/` 目录（解释器复用 qmeas 项目 env，不另建环境）。
- 真机提交消耗机时：`13 环 × 4 电路 × 1024 shots ≈ 5.3 万 shots`，提交前账单需确认。
- 需要 `QUARK_TOKEN` 环境变量；token 永不进代码。
- 无现有代码改动；Baihua 2 号环穿过链任务冠军邻域（67–76），环结果可与链结论互相印证。
