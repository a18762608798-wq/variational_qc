# Tasks: exp03 附录能隙

**Feature:** exp03

任务必须来源于 `spec.md` 和 `plan.md`。
不得在 tasks 阶段引入新的实验定义。

## Implementation

- [x] T001 实现 `src/Exp03/SectorBasis.jl`：`sector_basis(L)`（`Z_tot=0` 比特串在
  `{I, X̄, R, X̄R}` 下全 `+` 轨道对称化 + 规范索引）与
  `sector_hamiltonian(L, s, delta)`（键项直接作用比特串组装，键集/权重/基矢约定
  与 `Shared01.Hamiltonian` 同语义）；`src/Exp03.jl` 父模块。
  完成条件：模块可加载，`L=8/12/16` 基矢非空且构造性断言通过（由 T007 锁定）。
- [x] T002 实现 `src/Exp03/GapSolver.jl`：`solve_gap(L, s)`（稀疏组装 → ARPACK 最低两本征对 → 残差断言 →
  `E0, E1, Δ`，残差 `< 1e-10`，`delta=0`）；网格并集定义
  （每 `L` 194 点，4 交叠去重，(iii) 复用 (i) `s=0.5`）。
  完成条件：单点 `(L,s)` 可出 `(E0,E1,Δ)` 且 `Δ` 有限非负（容限内）。
- [x] T003 实现 `src/Exp03/CrossFit.jl`：`crossings(s_grid, A1, A2)`
  （严格变号 bracketing + 相邻两点线性插值，返回全部交点）与
  `linear_fit(xs, ys)`（一次最小二乘）；纯内核。
  完成条件：合成数据（已知交点直线、共线三点）精确恢复（由 T007 锁定）。
- [x] T004 实现 `src/Exp03/Store.jl`：按 `L` 分块 `.npz` + 完成表续算；
  组装 `exp03_D02.npz`（(i) `Δ[3,99]`、(ii) `A[3,99]`、交点表、
  (iii) 三点 + `(a,b)`）+ `exp03_manifest.json`（schema `exp03/v1`）。
  完成条件：中断续算一致（删块重跑组装不变）。
- [x] T005 编写 `scripts/run_exp03.jl`（模块 API → 分块落盘 → 组装）
  并执行全点生产（`3 × 194` 扇区对角化；顺序 `L=8`、`12`、`16`）。
  完成条件：`exp03_D02.npz` + manifest 落盘，形状与网格定义一致。
- [x] T006 出图（`scripts/plot_D02.py`）：三联图 `(a) Δ–s` / `(b) A–s` + 交点 /
  `(c) Δ–1/L` + 拟合直线与 `(a,b)` 标注（mathtext 标签，`figure_style.py`
  风格，矢量 PDF + 300dpi PNG 落 `figs/exp03/`）。
  完成条件：坐标系自检通过，三联顺序正确，交点 marker 与存档交点表一致，
  附 skill 风格检查报告块。

## Validation

- [x] T007 单元测试（`test/runtests.jl` 追加，全绿）：轨道基构造性
  （磁化、`X̄`/`R` 不变性）；`L=8` 全点与全空间暴力一致 `< 1e-10`
  （`L=12` 单点抽查）；`L=16` 单点稀疏与稠密全谱一致 `< 1e-8`；
  插值/拟合合成小例；非法 `L` 拒绝路径。
- [x] T008 生产断言（`scripts/verify_exp03.jl`，对正式输出全量执行）：
  `Δ ≥ −1e-12`；逐点本征对残差 `< 1e-10`；每对交点至少一个 bracketing；
  拟合重算一致 `< 1e-12`；(iii) 与 (i) `s=0.5` 一致；无缺失、无 NaN。

## Follow-up (paper-outline 2026-10-03 更新：(iii) 五点 + 两点拟合)

- [x] T009 代码：`MAX_L 20→26`；`Store` 增 `extra_iii` chunk（存 `L=20/24` 单点、
  进度位续算）+ 组装合并（`fit_x/fit_y` 五点、拟合仅用后两点）+ manifest 字段；
  `run_exp03.jl` 增 extra 步骤；`verify_exp03.jl` 按新口径（五点形状、两点拟合重算、
  仅前三点与 (i) 一致）；`plot_D02.py` 仅重出 `(c)`（五点 + 两点拟合线）；
  单元测试追加两点拟合合成小例。
  完成条件：`runtests.jl` 全绿。
- [x] T010 生产：执行 extra 两点（约 3 分钟）→ 重组装 → `verify_exp03.jl` 全量通过
  → 重出 `(c)` 图并目检。
  完成条件：`VERIFY-EXP03-OK`，`(c)` 五点与拟合线一致。
