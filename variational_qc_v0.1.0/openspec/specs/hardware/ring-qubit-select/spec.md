# hardware/ring-qubit-select Specification

## Purpose

在 Baihua 与 Shenglian 真机上用环基准电路对候选 10-环打分排序，选出最优环供周期边界变分实验使用；环自成一次推荐，不与链混排。

## Requirements

### Requirement: 环枚举与账单确认

系统 SHALL 在 Baihua 与 Shenglian 上全枚举 10-环（`find_rings`，旋转/翻转去重已内建），真机提交前 SHALL 打印账单（每机环数、任务数、总 shots）并经人工确认后方可提交。

#### Scenario: 小池全覆盖

- **WHEN** 两机 10-环总数很少（约 13 个）
- **THEN** 全部提交，无采样盲区；数量如实记入报告

#### Scenario: 账单先行

- **WHEN** 离线预览完成、真机提交尚未开始
- **THEN** 账单已打印（含每机环数、每环 4 任务、1024 shots/任务），无人工确认 SHALL NOT 提交

### Requirement: 环真机基准与打分排序

系统 SHALL 对每个候选环提交 4 个基准电路（环 cluster 制备：H + 10 个 CZ 含闭合边；稳定子奇偶两组，全为 `Z_{i-1} X_i Z_{i+1}` 三体、指标模 10；全零/全一读出校验，1024 shots），以 `score = 0.8 × 稳定子均值 + 0.2 × 读出保真度` 打分并**只在环内部**排序；提交 SHALL 一次性全量（先全部提交再统一轮询）；每份结果 SHALL 即时 checkpoint 落盘，中断重跑 SHALL 只补缺失（有 tid 只轮询不重提）；全部无有效结果时 SHALL 报错且不返回猜测值。

#### Scenario: 环链不混排

- **WHEN** 环测完打分
- **THEN** 排序只含环候选，链任务分数不参与比较（制备 CZ 数与稳定子权重不同，不可比）

#### Scenario: 断点续跑

- **WHEN** 提交中途中断后重跑
- **THEN** 已有 checkpoint 的电路结果被跳过，只补缺失部分，不重复消耗机时

### Requirement: 环推荐报告存档

系统 SHALL 将最优环 `(chip, target_qubits)` 连同每环稳定子均值、读出保真度、任务 id、校准时间、排队深度落盘为推荐报告 JSON，并沉淀人话分析（ANALYSIS.md：结论、两机对照、分数解读）；token SHALL 经环境变量提供，永不落盘。

#### Scenario: 报告可回填

- **WHEN** 后续周期边界真机任务读取推荐报告
- **THEN** 可直接得到可用的 `(chip, target_qubits)`，无需重新选环
