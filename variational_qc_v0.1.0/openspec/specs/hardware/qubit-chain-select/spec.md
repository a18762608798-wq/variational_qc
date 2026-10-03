# hardware/qubit-chain-select Specification

## Purpose

在 Baihua 与 Shenglian 真机上用统一基准电路对候选 8 比特链打分排序，选出最优链供后续真机变分实验使用，让选链依据从静态校准参数变为实测表现。

## Requirements

### Requirement: 候选链采样与账单确认

系统 SHALL 在 Baihua 与 Shenglian 上采样候选 8 比特线性链（sample 全图随机游走策略，每机上限 1000 有向链兜底），采样 SHALL 过滤死比特与零保真边；采样后 SHALL 按无向去重（反转视为同一条物理链，只保留其一），去重后即为全覆盖（Baihua 约 254、Shenglian 约 558 条）；提交前 SHALL 用静态校准参数做预筛（只砍明显烂链，仅 survivors 提交），再打印账单（每机链数、任务数、总 shots）并经人工确认后方可提交。

#### Scenario: 反转不重复计费

- **WHEN** 两条采样链互为反转
- **THEN** 只提交其中一条（cluster 制备与稳定子集在反转下不变，读出校验全对称），另一条记为去重丢弃，不消耗机时

#### Scenario: 预筛只做减法

- **WHEN** 静态预筛过滤采样链
- **THEN** 只剔除含死比特、边保真度 `< 0.9` 的链，不做加权排名；被剔除数与 survivors 数记入报告，最终排序仍纯按实测分

#### Scenario: 小池全覆盖

- **WHEN** 去重后物理链总数远小于采样上限
- **THEN** 按实际全部物理链提交（Baihua 约 254、Shenglian 约 558 条），最优链必在锅中，无采样盲区；数量如实记入报告

#### Scenario: 账单先行

- **WHEN** 离线预览完成、真机提交尚未开始
- **THEN** 账单已打印（含每机 survivors 链数、每链 4 任务、1024 shots/任务），无人工确认 SHALL NOT 提交

### Requirement: 真机基准与打分排序

系统 SHALL 对每条候选链提交 4 个基准电路（线性 cluster 稳定子奇偶两组 + 全零/全一读出校验，1024 shots），以 `score = 0.8 × 稳定子均值 + 0.2 × 读出保真度` 打分并跨机排序；提交 SHALL 一次性全量（先把全部 survivors 的缺失电路提交完，再统一轮询，避免分波重新排队被插队）；每份电路结果 SHALL 即时 checkpoint 落盘，中断重跑 SHALL 只补缺失结果；全部候选链无有效结果时 SHALL 报错且不返回猜测值。

#### Scenario: 一次性提交占住队列

- **WHEN** survivors 清单确认后开始提交
- **THEN** 全部缺失电路先一次提交完毕（已有 checkpoint 的跳过），再进入统一轮询；中途不得分波重排

#### Scenario: 断点续跑

- **WHEN** 提交中途中断后重跑
- **THEN** 已有 checkpoint 的电路结果被跳过，只补缺失部分，不重复消耗机时

#### Scenario: 打分只看实测

- **WHEN** 全部候选链测完
- **THEN** 排序纯按实测分，排队深度与静态校准参数只记入 evidence、不参与排序

### Requirement: 推荐报告存档

系统 SHALL 将最优 `(chip, target_qubits)` 连同每条链的稳定子均值、读出保真度、任务 id、校准时间、排队深度落盘为推荐报告 JSON，供后续真机任务直接回填；token SHALL 经环境变量提供，永不落盘。

#### Scenario: 报告可回填

- **WHEN** 后续真机任务读取推荐报告
- **THEN** 可直接得到可用的 `(chip, target_qubits)`，无需重新选链
