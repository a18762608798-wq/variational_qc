# Design

## Context

- 现状：`numerics/zr-ground-state` 是求解+派生一体（`scan.jl` 边对角化边写 `tilde_ZR` CSV）；主 specs 另有 `viz/zr-heatmap`。见 `proposal.md` 动机。
- 约束（探索结论）：单次求解→NPZ 存档（Julia 算、Python 将来可读）；ZR 迁到存档派生（选项 A）；ZR/string/AFM 同处一个功能区不拆 dir；viz 脚本是三者的局部共享；`1/4` 归一从略与既有约定一致。
- 规模：存档 `10000×256` 复数 ≈ 41MB；派生为秒级；求解仍约 50 分钟。

## Goals / Non-Goals

**Goals:**

- 求解与派生分离：改网格只付一遍对角化；string/AFM 与 ZR 共享同一批态。
- ZR 迁移零回归：派生输出与历史 CSV 逐行一致，否则迁移不通过。

**Non-Goals:**

- 不碰 `H(s,δ)` 构造与基态求解算法（复用既有模块）。
- 不实现随机测量版观测量、不接入变分/quafu（后续增量）。
- Python 本增量仍只消费 CSV，不直接读存档（NPZ 只是为将来留门）。

## Decisions

### 1. 存档格式 NPZ，keys 锁定五项

`psi_archive.npz`：`psi`（复数矩阵，行序 `delta` 外层/`s` 内层，与 CSV 同序）、`s_grid`、`delta_grid`、`energies`、`is_degenerate`。Julia 写（新增 NPZ.jl 依赖），numpy 可读。替代方案 JLD2（Julia 最省事）被否决：用户明确要求 Python 将来可直接利用数据。CSV 存波函数被否决：2.56M 复数文本臃肿且精度/解析风险高。

### 2. `scan.jl` 拆成 `solve.jl + derive_*.jl`

- `solve.jl`：网格循环 + 对角化，只写存档（不再写物理量 CSV）。
- `derive_zr.jl` / `derive_string.jl` / `derive_afm.jl`：只读存档，各写各的 CSV。ZR derive 复用既有 `zr.jl` 公式链；string/AFM 新建观测量模块。
- 为何不保留旧 `scan.jl` 并存：两条数据源并存则网格一改要跑两遍 50 分钟，且迟早分叉；旧链退役，历史 CSV 留作回归 oracle。

### 3. 同区共处，viz 局部共享

ZR/string/AFM 三者语义相近（同一批态、同一网格、同一 CSV→PNG 契约），放同一功能区（现有 `src/numerics/` + `src/viz/` 直接加文件，不新建 sub dir）。`plot_heatmap.py` 加 `--value-col/--title` 参数化后服务三张图，不上根 `shared/`（它去掉“热力图”就说不通，不符合 shared 标准）。未来变分/qiskit 等异构功能再开新 dir。

### 4. 存档不进 git

41MB 二进制进 git 拖慢所有 clone/fetch；存档可由 `solve.jl` 确定性再生。`data/interim/psi_archive.npz` 加入 gitignore，CSV/图片照常跟踪。回归依赖的历史 `tilde_ZR` CSV 保留在库内。

## Risks / Trade-offs

- [Risk] NPZ 跨语言复数布局歧义 → Mitigation：写入后立即用 numpy 读回断言形状/模长/抽查值（任务内含）；行序以“存档第 k 行重算值 == CSV 第 k 行”为契约锁死。
- [Risk] 简并点存哪一支 → Mitigation：沿用既有约定（eigenstates 确定性分支 + `is_degenerate` 标志），存档只存该支，不存简并子空间。
- [Risk] 迁移期新旧 CSV 不一致 → Mitigation：diff 验收是硬门槛，不过则迁移不通过，不删旧链。
- [Trade-off] 求解仍 50 分钟单次 → 后续网格变更依然重，可接受；并行化列入实现自由。

## Migration Plan

- 本增量内完成迁移：旧 `scan.jl` 删除，旧 CSV 由派生链重写（diff 通过后覆盖）；`grid.toml` 加存档路径项。
- 回滚：旧 CSV 在 git 内，`git checkout` 即可恢复；存档可重跑。

## Open Questions

- 无前置阻塞问题。色标选型（string 用发散、`S(π)` 用顺序）与 `S(π)` 色棒上限在实现时按数据声明，不改变 specs。
