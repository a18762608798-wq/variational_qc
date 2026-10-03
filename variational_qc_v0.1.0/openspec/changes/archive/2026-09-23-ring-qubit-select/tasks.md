# Tasks

## 1. task7 骨架与离线预览

- [x] 1.1 建 `task7_ring_select/` 目录（config/grid.toml 含 `shape="ring"`、scripts、data、README；解释器复用 qmeas env），照搬 task6 四脚本（preview/prescreen/submit/cancel_stale，链→环），验证 `import` 与离线预览跑通（两机环数、账单打印、零提交）
- [x] 1.2 提交当天 `force` 重拉两机拓扑并重枚举，以当天环数为准产出 survivors 清单，人工确认账单（环数×4任务×1024 shots）后进入提交

## 2. 真机提交与轮询

- [x] 2.1 一次性全提交（两阶段：转译→提交→tids 落盘），验证除已完成外全部缺失电路进入轮询
- [x] 2.2 统一轮询至全部收回；收尾 query Failed 对账（轮询器缺口：Failed 回 `{}` 需单条 cancel+去 tid 重跑），验证每环 4 份结果齐全

## 3. 打分与报告

- [x] 3.1 环内打分排序（不与链混排），首名分差<0.02 则报告标注"并列"，推荐报告 JSON 落盘，并沉淀 `task7_ring_select/ANALYSIS.md` 人话分析
- [x] 3.2 跑 `openspec validate --specs` 全通过，同步 delta 进主 specs，确认可归档
