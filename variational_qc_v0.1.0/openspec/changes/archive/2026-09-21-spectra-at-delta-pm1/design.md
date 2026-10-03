# Design: spectra-at-delta-pm1

## Context

`solve_ground_state`（`shared/numerics/ground_state.jl`）内部已做 256 维全对角化（`QuantumToolbox.eigenstates`），`gap = vals[2]-vals[1]` 现成可用——取 `E1` 零新增对角化代价。`build_H`/`build_Hp`（`shared/numerics/hamiltonian.jl`，`λ=1` 硬编码）直接复用。画图沿用 `shared/viz/plot_heatmap.py` 的原子写出与确定性约定（新脚本，不是 heatmap 本体）。动机见 proposal.md。

## Goals / Non-Goals

- Goals：两任务各一条谱扫描链（脚本→CSV→一画布两子图），`E1` 以最小改动从既有 solver 透出。
- Non-Goals：不改 solver 数值方法与容差语义；不做 `δ` 扫描（`δ=±1` 写死为常量）；不画高激发态；不动既有存档/派生/热力图。

## Decisions

1. **solver 返回值加 `excited` 字段**：`solve_ground_state` 返回具名元组追加 `excited = real(vals[2])`（即 `energy + gap`）。备选（另写全谱函数）被否决：重复对角化，浪费且引入两处数值源。
2. **新扫描脚本各任务一份**（如 `scan_spectra.jl`，接受 H 构造器选择或 task 参数）：`δ ∈ {-1,+1}` × `s` 201 点，行序 `delta` 外层、`s` 内层，与既有 CSV 契约同序；输出 `spectra_L8_OBC.csv`（表头 `s,delta,E0,E1`），落各自任务 `data/interim/`。
3. **画图用 Python 新脚本**（如 `plot_spectra.py`，`--csv`/`--png` 参数化，原子写出）：一画布两子图共享 y 轴（绝对能量可比），`E0` 实线、`E1` 虚线/异色；标题含任务标识（H vs H+P）与 `δ` 取值。备选（Julia 画图）被否决：既有画图全是 Python/matplotlib，保持一致。
4. **对照结论不另写脚本**：task1/task2 谱对照（隙零点、E0 差 −1）由 spec 场景在验收时用一次性 Python 核对，不沉淀对比脚本——能谱是判读图，不是验证门（与 task2 的 `compare_task1_task2.py` 性质不同）。

## Risks / Trade-offs

- [Risk] `E1` 在 `s` 网格上出现能级交叉导致线条"换支" → Mitigation：只画最低两支包络（排序后取值），交叉即 avoided-crossing 的可视化本身就是结论；不做 diabatic 追踪。
- [Risk] 绝对能量下 task2 两线整体低 −1，两画布 y 轴范围不同影响肉眼对照 → Mitigation：两子图共享 y 轴（画布内可比），画布间允许 y 范围不同并在标题/轴标明绝对能量；对照判读以 CSV 数值为准。
- [Trade-off] `δ=±1` 为硬编码常量：后续想换切线需改脚本 → Mitigation：接受，spec 已限定；真有 task4 需求时再参数化。

## Migration Plan

纯新增：solver 加字段（旧字段不动，旧调用方零改动）、新脚本/CSV/图；删目录即回滚。不涉及迁移。

## Open Questions

无。
