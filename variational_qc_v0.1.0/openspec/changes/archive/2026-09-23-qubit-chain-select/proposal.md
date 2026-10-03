# Proposal

## Why

VQE 及后续真机实验需要一条 8 比特线性链，真机比特质量差异巨大，随手选链等于把保真度交给运气。在烧机时跑变分电路之前，先用最彻底的采样方式把两台可用机器（Baihua、Shenglian）上最好的 8 比特链找出来，是真机任务的第一步。

## What Changes

- 在 `04_project/variational_param` 下新增 task6（`task6_qubit_select/`）：真机 8 比特选链任务，含环境配置、离线预览、提交脚本与推荐报告。
- 复用 `03_tools_practice/qmeas` 的 benchmark 管线（拓扑拉取、sample 采样、4 电路基准、稳定子+读出打分），不重复造轮子；task6 只做配置、执行与存档。
- 每机 sample 采样（上限 1000 有向链兜底，1024 shots），采样后按无向去重（反转视为同一条物理链，只留其一）；精确枚举证实物理池很小（Baihua 254、Shenglian 558 条无向 8 链），去重后即全覆盖，无采样盲区。打分权重沿用默认（`w_stab=0.8`、`w_ro=0.2`）。
- 采样后加一道零成本静态预筛：用拓扑快照的 T1/T2/门保真度只做减法，砍掉明显烂链，仅 survivors 提交真机；最终排序仍纯按实测分。
- 先离线预览（拓扑→选链→账单，零机时）确认候选规模与账单，再真机提交；全部结果 checkpoint 断点续跑，推荐报告落盘供后续真机任务回填 `target_qubits`。

## Capabilities

### New Capabilities

- `hardware/qubit-chain-select`: 在 Baihua/Shenglian 上采样候选 8 比特链并用真机基准电路打分排序，输出最优链与 evidence 报告。

### Modified Capabilities

（无）

## Impact

- 新增 `task6_qubit_select/` 目录（解释器复用 qmeas 项目 env，不另建环境）。
- 真机提交消耗机时：`survivors × 4 电路 × 1024 shots`（survivors 为预筛+去重后的提交集，预计约 812 条物理链 ≈ 3250 任务），提交前账单需确认。
- 需要 `QUARK_TOKEN` 环境变量；token 永不进代码。
- 无现有代码改动；后续真机 VQE 任务消费推荐报告中的 `(chip, target_qubits)`。
