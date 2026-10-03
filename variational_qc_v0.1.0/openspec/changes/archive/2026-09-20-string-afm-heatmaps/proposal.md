# Proposal

## Why

ZR 热力图已给出拓扑/平庸的二分证据，但完整的相图判读还需要互补序参量：string operator 区分 SPT 与平庸 dimer，AFM 结构因子 `S(π)` 标定 Néel 反铁磁区。三者共享同一批基态，若各走一遍对角化，每改一次网格就要付三遍约 50 分钟的算力。因此本增量一次求解、持久化全网格基态，三个物理量全部改为存档派生。

## What Changes

- 求解与派生分离：全网格对角化只跑一次，输出基态存档 `psi_archive.npz`（Julia 计算，NPZ 格式以便 Python 将来直接读取；默认 keys：`psi/s_grid/delta_grid/energies/is_degenerate`）。
- ZR 迁移到存档派生（选项 A）：`derive_zr` 从存档重算 `tilde Z_R`，输出必须与现有 `data/interim/tilde_ZR_L8_OBC.csv` 逐行一致（diff 即验收），原直算链退役。
- 新增 string operator 与 AFM 结构因子派生（`doc/model/operator.md` 定义，OBC 特殊值，`1/4` 归一从略与既有实现一致），各输出同契约 CSV 并绘制热力图。
- ZR/string/AFM 同处一个功能区、不拆 sub dir；热力图脚本作为三者的局部共享，不上根 `shared/`（探索结论；未来变分/qiskit 等异构功能再开新 dir）。

## Capabilities

### New Capabilities

- `numerics/string-afm-observables`: 从基态存档计算 string operator 与 `S(π)`，输出同契约 CSV。
- `viz/string-afm-heatmaps`: 从上述 CSV 渲染两张热力图（PNG 必选，PDF 可选同名；标题不强调边界条件）。

### Modified Capabilities

- `numerics/zr-ground-state`: 求解链改为输出基态存档（新增）；`tilde Z_R` 改为存档派生且与旧 CSV 逐行一致；旧直算扫描退役。

## Impact

- 新增 Julia 依赖 NPZ.jl（写 NPZ 存档）；Python 侧无新增依赖（numpy 已可读 NPZ，但本增量 Python 仍只消费 CSV）。
- 新增产物：`data/interim/psi_archive.npz`（约 41MB）、string/AFM 的 CSV 与两张热力图；`scan.jl` 直算链被 `solve.jl + derive_*.jl` 取代。
- 网格配置与 CSV 契约保持不变；后续增量（变分电路、quafu）复用存档或另起 sub dir。
