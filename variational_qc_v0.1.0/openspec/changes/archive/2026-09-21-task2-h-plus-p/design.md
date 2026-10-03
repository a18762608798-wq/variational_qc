# Design: task2-h-plus-p

## Context

当前布局是单任务平铺：`src/{numerics,viz,shared}`、`data/{interim,figures}`，路径硬编码在 `src/shared/config/grid.toml`。求解器 `solve_ground_state(H)` 接受任意 Hermitian 输入，与 H 构造解耦；`P` 的两项（`ΣZ` 单体嵌入、`∏X` 直积）可复用 `hamiltonian.jl` 的 kron 套路（需补一个单体嵌入 helper，`embed2` 只覆盖双体）。derive 脚本与画图脚本目前直连固定路径。动机见 proposal.md。

## Goals / Non-Goals

- Goals：`shared/` 抽出可复用件；`task1_*` 完整迁入旧代码+旧结果；`task2_*` 跑通求解→存档→derive→两图→对比验证全链。
- Non-Goals：不改 solver 数值方法；不做 λ 扫描（λ=1 硬编码）；不做 `S(q)`；不重写 CSV schema（文件名不变，靠目录区分任务）。

## Decisions

1. **顶层按任务切**：`shared/`、`task1_baseline/`、`task2_hplusp/`，各任务自带 `data/{interim,figures}` + 一份 grid 配置。备选（`src/`、`data/` 下分子目录）被否决：任务是最大内聚边界，顶层切分后 task3 只需复制目录。
2. **同名文件、目录区分任务**：`psi_archive.npz`、`tilde_ZR_L8_OBC.csv` 等文件名两任务完全相同，对比脚本按目录配对。备选（文件名加后缀如 `_HpP`）被否决：会污染 CSV schema 与既有约定，目录隔离已足够。
3. **H 构造器进 shared 并加 P 选项**：`build_H(s, δ)` 不变，新增 `build_P(L)` + `build_Hp(s, δ)`（= H+P，λ=1 常量）。`Z_tot` 用新增单体嵌入 helper，`∏X` 用 kron；不断言 P 本征值（由 spec 场景覆盖）。
4. **derive/plot 脚本参数化复用**：`derive_*.jl`、`plot_heatmap.py` 改为接受输入/输出路径参数（默认回落旧路径以便 task1 烟测），逻辑零改动；task2 用新配置调用。`compute_sq.py`、`plot_sq_curves.py` 不动（S(q) 跳过）。
5. **对比脚本放 task2**：`compare_task1_task2.py` 读两边四个 CSV + energies，按 spec 容差输出 pass/fail 与差异清单；图片对比用逐像素（验证通过时的推论，不做独立判定）。
6. **task1 搬迁先行**：先搬文件、拆配置、烟测旧链可跑，再写新代码；搬迁本身不改变任何数值行为。

## Risks / Trade-offs

- [Risk] P 劈裂简并子空间，孤立点观测量与 task1 不一致 → Mitigation：spec 已定为"单独列出、不判失败"，差异即结论；能量差偏离 −1 的行进异常清单。
- [Risk] 搬迁改路径导致旧脚本找不到文件 → Mitigation：路径全部收敛到每任务一份 grid 配置，搬迁后先跑 task1 烟测（11×11）再继续。
- [Risk] task2 全网格 10000 点稠密对角化耗时与 task1 同量级 → Mitigation：流程与 task1 相同，按既有 smoke→full 两步走；无新增性能需求。
- [Trade-off] 同名文件靠目录区分：对比时配错目录会误判 → Mitigation：对比脚本只接受两个任务根目录参数，内部路径写死，不接受散文件。

## Migration Plan

1. 建 `shared/`、`task1_baseline/`、`task2_hplusp/` 骨架，搬迁旧 `src/`、`data/` 内容与结果。
2. 拆分 grid 配置为每任务一份，task1 烟测回归通过。
3. 实现 P 构造 + task2 求解/存档 → derive → 两图 → 对比验证。
4. 回滚：搬迁是纯 `git mv`，任何一步失败 `git checkout` 即回；task2 产物独立目录，删目录即清零。

## Open Questions

无（λ 取值、pass 标准、范围、目录命名均已在 explore 中与用户确认）。
