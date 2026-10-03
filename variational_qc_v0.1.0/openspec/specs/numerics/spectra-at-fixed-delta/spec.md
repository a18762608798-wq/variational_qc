# numerics/spectra-at-fixed-delta Specification

## Purpose

沿固定 `δ` 切 `s` 轴记录最低两支本征能量，为 task1/task2 的简并与劈裂结论提供直接的能隙证据；只做全对角化最低两支的扫描存档，不重复基态存档链路。

## Requirements

### Requirement: 固定δ谱扫描与存档

系统 SHALL 对给定哈密顿量构造器（task1 用 `build_H`、task2 用 `build_Hp`，`λ=1` 不变）在 `δ ∈ {-1, +1}`、 `s ∈ [0, 1]` 均匀 201 点（含端点）上逐点求最低两支本征能量，并输出谱 CSV（表头 `s,delta,E0,E1`，`E1 ≥ E0`，绝对能量、不得减零点），行数为 `402`，行序 SHALL 为 `delta` 外层、`s` 内层；同一输入跑两次结果 SHALL 逐位一致。

#### Scenario: 行数与单调性

- **WHEN** 以默认配置运行任一任务的谱扫描
- **THEN** CSV 共 `402` 行，每行 `E1 ≥ E0`（容差 `1e-12`），`s` 端点覆盖 `0` 与 `1`

#### Scenario: 确定性

- **WHEN** 同一任务同一配置运行谱扫描两次
- **THEN** 两次 CSV 逐位一致

### Requirement: task1/task2 谱对照关系

系统 SHALL 用同一扫描定义产出两个任务的谱 CSV（文件名相同、落盘于各自任务专属目录）；在 task2 劈开简并的 `s` 区间内，task2 的隙 `E1-E0` SHALL 显著大于 task1 同点之隙（task1 隙在浮点舍入内为零），其余区间 task2 的 `E0` SHALL 比 task1 同行低 `1`（容差 `1e-8`，基态落在 `P=−1` 扇区已有 task2 验证）；`E1` 不预设平移量（激发态所处 P 扇区不定），SHALL 如实记录。

#### Scenario: 简并区隙被撑开

- **WHEN** 对比两任务同 `(s, δ)` 行且 task1 隙为零处
- **THEN** task2 同行隙为正（`> 1e-6`），`E1-E0` 差值如实记录

#### Scenario: 非简并区基态下移

- **WHEN** 对比两任务同行且 task1 隙非零处
- **THEN** `E0` 比 task1 低 `1`（容差 `1e-8`），`E1` 值如实记录、不做平移断言
