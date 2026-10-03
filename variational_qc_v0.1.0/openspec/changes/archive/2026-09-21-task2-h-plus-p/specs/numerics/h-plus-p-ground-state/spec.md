# Spec Delta

## Purpose

在 `H' = H + P`（`P = Z_tot^2 - ∏X`，λ=1 固定）下重复全网格基态求解并存档，为对称性不变验证提供 task2 输入；`[H,P]=0` 保证本征态不变，预期基态与 task1 逐点一致、能量整体下移 −1。

## ADDED Requirements

### Requirement: P 对称性项构造

系统 SHALL 按 `doc/model/ref/symmetry.md` 构造 `P = Z_tot^2 - ∏_{i}X_i`（`Z_tot = Σ_i Z_i`，与 `hamiltonian.jl` 同一套格点/嵌入约定，`L=8` 即 256 维 Hermitian 矩阵）；`H' = H + P` 中 P 系数 SHALL 固定为 `1`，不得引入可调参数或新增扫描轴。

#### Scenario: P 本征值可审计

- **WHEN** 在计算基上检查 P 的对角元
- **THEN** `(M=0, ∏X=+1)` 扇区本征值为 `−1`，`|M|=2` 扇区本征值为 `3` 或 `5`，且 `[H, P] = 0`（交换子范数在浮点舍入内）

#### Scenario: 系数无参数

- **WHEN** 检查 H' 构造入口的签名与配置
- **THEN** 不存在除 `(s, δ)` 之外的可调数值参数，λ=1 为硬编码常量并在文档声明

### Requirement: H' 全网格求解与存档

系统 SHALL 在与 task1 相同的 `(s,δ)` 默认网格（每轴 100 点、端点包含）上对 `H'(s,δ)` 逐点求解基态并输出 task2 基态存档（与 task1 存档同 schema：`psi`、`s_grid`、`delta_grid`、`energies`、`is_degenerate`，行序 `delta` 外层、`s` 内层）；求解器 SHALL 复用同一基态求解入口（接受任意 Hermitian 输入）；task2 产物 SHALL 落盘于 task2 专属目录，不得覆盖 task1 文件。

#### Scenario: 存档结构同构

- **WHEN** 以默认配置运行 task2 求解并用 Python（numpy）打开存档
- **THEN** 五个 keys 齐全，`psi` 形状为 `(10000, 256)`，行模长为 1（容差 `1e-8`），网格端点覆盖 `[0,1]`/`[-3,3]`

#### Scenario: 能量整体下移

- **WHEN** 对比 task2 存档与 task1 存档同行 `energies`
- **THEN** task2 比 task1 低 `1`（容差 `1e-8`，基态落在 `P=−1` 扇区内）；若某行差值显著偏离 −1，该行 SHALL 记入异常清单供人工复核
