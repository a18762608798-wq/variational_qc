# Tasks

## 1. task6 骨架与环境

- [x] 1.1 建 `task6_qubit_select/` 目录（config+scripts+data+README；解释器复用 qmeas 项目 env，见设计备注），验证 `import qmeas.benchmark, quark` 成功
- [x] 1.2 写离线预览脚本（拓扑拉取→sample 选链→打印账单，`DO_SUBMIT=False`），验证两机拓扑快照落缓存、候选链与账单正常打印且零真机提交

## 2. 账单确认与真机提交

- [x] 2.1 写预筛脚本（sample 上限 1000 有向链兜底 → 无向去重 `min(链,反转)` → 静态阈值只做减法：死比特、边保真度 `< 0.9`），产出 survivors 清单与去重/剔除清单；提交当天 `force` 重拉两机拓扑，记录 `calibration_time`，人工确认账单（survivors 数×4任务×1024 shots，预期约 812 链）后提交，验证全部任务进入轮询且 checkpoint 目录开始落盘
- [x] 2.2 一次性全提交改造：改 qmeas runner 为提交/轮询两阶段（电路、打分、checkpoint 语义不变），杀掉旧串行进程，已有 checkpoint 复用零损失；验证除已完成外全部缺失电路进入轮询（tids 落盘）
- [x] 2.3 统一轮询至全部 survivors 收回，验证每条链 4 份结果齐全（缺失则只补缺口），中断重跑不重复消耗机时

## 3. 打分与报告

- [x] 3.1 对全部 ChainResult 打分跨机排序，验证首名分差≥0.02（否则报告标注"并列"），推荐报告 JSON 落盘（含每链 stab_mean、readout_fid、tids、calibration_time、queue_depth），并沉淀 `task6_qubit_select/ANALYSIS.md` 人话分析（两机对照、聚簇、相关性、方法回看）
- [x] 3.2 跑 `openspec validate --specs` 全通过，同步 delta 进主 specs，确认可归档
