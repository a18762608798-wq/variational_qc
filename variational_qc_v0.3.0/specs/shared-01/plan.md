# Implementation Plan: shared-01 精确基态公共数据

## 1. 实现思路

- 主要模块：`Hamiltonian`（`H(s,δ)` 构造，`L=8` OBC）、`GroundStates`
  （网格定义、ED 求解内核、简并标记）、`Store`（落盘与 manifest）、
  薄编排脚本 `scripts/run_shared01.jl`（组装网格 → 求解 → 存储）。
- 数据流：`(s,δ)` 网格 → 逐点构造稠密 `H`（256 维）→ 全对角化取最低两本征对
  `(E0, ψ0, E1)` → 叠成数组一次性写入单个数据文件 + JSON manifest；
  S02 三点不独立计算，从 S01 同坐标条目直接索引引用。
- 核心算法：稠密 Hermitian 全对角化（`LinearAlgebra`），每点天然给出 `E1`，
  用于 spec 的简并记录规则；`9801 × 256` 维规模下单机多线程即可。
- 关键技术选择：数值全部在 Julia（skill 默认分工）；Python 不参与本 feature
  （无出图）；存储用 numpy 可直接读取的单文件格式，下游 exp01/exp02 无需 Julia。

## 2. 代码与模块结构

新增（全部归属本 feature，不建跨 feature 共享框架）：

- `src/Shared01/Hamiltonian.jl`：`build_hamiltonian(L, s, delta)` 稠密 `Matrix{ComplexF64}`；
  奇键 `(2j-1,2j)`、偶键 `(2j,2j+1)`；基矢约定采用 `site m ↔ bit (m-1)`、
  `LSB = site 1`（与 v0.2.0 一致，便于交叉验证；约定同时写入 manifest）。
- `src/Shared01/GroundStates.jl`：网格常量（`s = i/100`，`δ = j/50`，
  `i,j = 1,…,99`）与三代表点坐标；`solve_point(H)` 返回 `(E0, ψ0, E1)`；
  简并标记规则（见第 3 节）；多线程网格循环（顺序确定性输出）。
- `src/Shared01/Store.jl`：写单个 `.npz`（数组：`s_grid[99]`、`delta_grid[99]`、
  `E0[99,99]`、`E1[99,99]`、`psi[99,99,256]` 复数）与同名 `.json` manifest
  （`L`、网格定义、基矢约定、`H` 定义标识、求解器与精度、简并点表、schema 版本）；
  提供按 `(s,δ)` 检索的读取函数。
- `scripts/run_shared01.jl`：薄编排，只做参数组装、调用模块 API、落盘，
  不含数值方法。
- `test/runtests.jl`：见第 4 节。
- 项目环境：`Project.toml`（implement 阶段按 `scientific-project-environment`
  skill 建于项目根，用项目本地环境运行，不用全局环境）。

与 v0.2.0 关系：不跨项目导入其代码（避免代际耦合；skill 规则 5）；
只将其 `Hamiltonian.jl`（`H_DEF` 相同物理定义）与基矢约定作为正确性
交叉参照（抽样点能量比对）。

## 3. 数值与技术决策

- 数值方法：稠密 Hermitian 全对角化取最低两本征对。理由：256 维下全对角化
  每点毫秒级，`E1` 免费给出且恰好满足 spec 简并记录要求；不引入 Krylov/稀疏
  近似（spec 要求无截断、无近似）。
- 精度：`ComplexF64` 全程；本征残差判据与简并标记阈值取 `1e-8`
 （能量量级 O(10)，双精度稠密求解器极限留有余量；纯实现层选择，
  不改变实验语义）。
- 并行：`Threads.@threads` 遍历网格点，输出按网格顺序写入（结果与线程数无关）。
  不用 GPU（规模无必要）。
- 存储：单 `.npz`（波函数约 `9801×256×16B ≈ 40MB`，单文件最简）+ JSON manifest。
  理由：numpy 原生可读，下游 Python 无需 Julia；manifest 人类可读溯源。
  不用多文件分片（徒增检索复杂度）。
- 关键依赖：Julia `LinearAlgebra`（stdlib）、`NPZ.jl`、`JSON3.jl`。
  版本冻结于 `Project.toml`/`Manifest.toml`。

以上均为实现层选择；网格、扇区、输出内容与验证条件沿用 spec，未改动实验语义。

## 4. 验证方案

spec 验证条件的落实（硬断言，失败即 invalid）：

- 网格完备性：输出形状恰为 `99×99 = 9801` 点，坐标与 spec 定义逐点一致。
- `H` 厄米：`H == H'` 精确成立（构造性测试：键算符对称性）。
- 本征残差：每点 `‖Hψ0 − E0ψ0‖ / max(1, ‖H‖) < 1e-8`。
- S02 一致性：三代表点条目与 S01 同坐标条目二进制一致（同一计算、索引引用）。
- 简并记录：凡 `E1 − E0 < 1e-8` 的点必须出现在 manifest 简并点表中，
  且保留求解器返回的最低本征矢（抽查断言）。

诊断量（只记录、不设通过阈值；物理解释归下游）：

- 最左列与 `s = 0` 奇键单态乘积的重叠（spec 的定性一致性检查；阈值由
  exp01/exp02 解释，本 feature 不设）。
- 与 v0.2.0 同物理定义在抽样点的 `E0` 交叉比对（实现正确性参照）。

## 5. 未解决问题 / 延后工作

- 无阻塞实现的未解决问题。`Project.toml` 等环境脚手架留待 implement 阶段建立。
