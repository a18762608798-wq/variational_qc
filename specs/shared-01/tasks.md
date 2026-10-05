# Tasks: shared-01 精确基态公共数据

**Feature:** shared-01

任务必须来源于 `spec.md` 和 `plan.md`。
不得在 tasks 阶段引入新的实验定义。

## Implementation

- [x] T001 建立项目环境：于项目根创建 `Project.toml`（依赖：`NPZ.jl`、`JSON3.jl`，
  `LinearAlgebra` 为 stdlib），`Pkg.instantiate()` 成功且
  `julia --project=. --startup-file=no -e 'using NPZ, JSON3'` 可运行。
  完成条件：`Manifest.toml` 落盘，解释器与依赖选择符合 `scientific-project-environment` skill
  （项目本地环境，无 `.venv`/系统 pip/全局 Julia 环境）。
- [x] T002 实现 `src/Shared01/Hamiltonian.jl`：`build_hamiltonian(L, s, delta)`
  返回稠密 `Matrix{ComplexF64}`，奇键 `(2j-1,2j)`、偶键 `(2j,2j+1)`（OBC），
  基矢约定 `site m ↔ bit (m-1)`、`LSB = site 1` 写进模块文档。
  完成条件：模块可加载，抽样点 `H` 满足 `H == H'`（伴随）。
- [x] T003 实现 `src/Shared01/GroundStates.jl`：网格常量（`s = i/100`、`δ = j/50`，
  `i,j = 1,…,99`）与三代表点坐标；`solve_point(s, delta)` 返回
  `PointSolution`（`E0`、`E1`、`ψ0`、简并旗）；
  `E1 − E0 < 1e-8` 置简并标记；`Threads.@threads` 网格循环且输出按网格顺序确定。
  完成条件：单点调用返回正确形状（`ψ0` 256 分量）与 `E1 ≥ E0`。
- [x] T004 实现 `src/Shared01/Store.jl`：写单个 `.npz`
  （`s_grid[99]`、`delta_grid[99]`、`E0[99,99]`、`E1[99,99]`、`psi[99,99,256]`）
  与同名 `.json` manifest（`L`、网格定义、基矢约定、`H` 定义标识、求解器与精度、
  简并点表、schema 版本），并提供按 `(s,δ)` 检索的读取函数。
  完成条件：小网格子集试写可 round-trip 读回且数值一致。
- [x] T005 编写 `scripts/run_shared01.jl`（薄编排：组装网格 → 调模块 API → 落盘，
  不含数值方法）并执行全 `99×99 = 9801` 点生产。
  完成条件：正式数据文件 + manifest 落盘，数组形状符合 T004 约定。

## Validation

- [x] T006 硬断言测试 [VAL-001..VAL-004, VAL-006]（`test/runtests.jl`，全部通过方为 feature 有效）：
  网格完备性（`99×99` 点、坐标与 spec 一致）；`H` 厄米；每点本征残差
  `‖Hψ0 − E0ψ0‖ / max(1, ‖H‖) < 1e-8`；S02 三点与 S01 同坐标条目一致；
  凡 `E1 − E0 < 1e-8` 的点均在 manifest 简并点表中。
- [x] T007 诊断量记录 [VAL-005]（只记录、不设通过阈值）：最左列与 `s = 0` 奇键单态乘积的重叠；
  与 v0.2.0 同物理定义在抽样点的 `E0` 交叉比对。
  完成条件：两项诊断值写入报告/manifest 备注，物理解释留待 exp01/exp02。
