# Proposal

## Why

基态相图（`s-δ` 平面、`L=8` OBC）在对称哈密顿量 `H` 下已建立，但从未验证"加对称性项后观测量不变"这一预期。`P = Z_tot^2 - ∏X` 与 `H` 对易（见 `doc/model/ref/symmetry.md`），`H' = H + P`（λ=1）应只把基态扇区能量整体下移 −1 而不改变基态本身；这个"显然但必须做"的验证是后续从简并初态做演化（用 P 锁定目标对称性分支）的前置工作。同时单任务平铺的 `src/`、`data/` 布局已容不下第二个任务，需要按任务切分子目录。

## What Changes

- 新增 `H' = H + P`（λ=1 固定，不新增扫描轴）：P 构造、`(s,δ)` 全网格（默认 100×100）求解、task2 基态存档。
- 对 task2 存档重复 derive 全链（`tilde_ZR`、归一化 `O_str`/`S(π)`、`Q`），输出 task2 CSV。
- 不变性验证：task2 四个 CSV 与 task1 逐行一致（容差 `1e-8`）；`energies` 差 −1 为预期；`is_degenerate` 翻转点单独列出、不判失败。
- 只画两张图：task2 归一化 `Z_R` 热力图、task2 `Q` 热力图（`Ostr`/`Spi` 热力图与 `S(q)` 曲线跳过）。
- 项目结构重组：`shared/`（H+P 构造器、io、画图 helpers 等复用件）+ `task1_*`（旧任务代码与结果迁入）+ `task2_*`（新任务），各任务自带 `data/{interim,figures}` 与路径配置。**BREAKING（路径层面）**：旧 `data/interim/*`、`data/figures/*`、`src/numerics/*`、`src/viz/*` 搬迁，`src/shared/config/grid.toml` 按任务拆分；文件名与 CSV schema 不变。

## Capabilities

### New Capabilities

- `numerics/h-plus-p-ground-state`: `H+P` 构造（λ=1）、全网格求解与 task2 基态存档。

### Modified Capabilities

- `numerics/string-afm-observables`: 在 task2 存档上复用 derive 定义并做 task1/task2 CSV 一致性验证。
- `viz/zr-heatmap`: 新增 task2 归一化 `Z_R` 热力图。
- `viz/string-afm-heatmaps`: 新增 task2 `Q` 热力图。

## Impact

- `src/numerics/hamiltonian.jl`：H 构造器进 `shared/` 并加 P 项选项；solver 本体不变（接受任意 H）。
- `src/numerics/derive_*.jl`、`compute_sq.py` 除外（S(q) 跳过）：derive 脚本参数化输入/输出路径后复用。
- `src/viz/plot_heatmap.py`：画图函数进 `shared/`，task2 用新配置画两张图。
- `data/`、`src/` 搬迁：旧结果进 `task1_*/`，新结果进 `task2_*/`；`psi_archive.npz` 等文件名不变。
- 不影响已归档 change 的结论；验证通过则确认对称性预期，孤立简并点差异（如有）如实记录为结论而非失败。
