# Spec Delta

## ADDED Requirements

### Requirement: 基态存档输出

系统 SHALL 在全网格求解后输出基态存档 `psi_archive.npz`（NPZ 格式，Julia 写入、Python 可读）：keys 至少为 `psi`（形状 `ns*ndelta × 256` 复数，行序与 CSV 一致：`delta` 外层、`s` 内层）、`s_grid`、`delta_grid`、`energies`、`is_degenerate`；每行态矢模长为 1（容差 `1e-8`），`energies` 为对应基态能量。

#### Scenario: 存档完整可读

- **WHEN** 以默认配置运行求解并用 Python（numpy，无 Julia）打开存档
- **THEN** 五个 keys 齐全，`psi` 形状为 `(10000, 256)`，抽查行模长为 1，`s_grid`/`delta_grid` 端点覆盖 `[0,1]`/`[-3,3]`

#### Scenario: 存档与 CSV 同序

- **WHEN** 对比存档第 `k` 行与 CSV 第 `k` 行
- **THEN** 两者 `(s,delta)` 一致，且由存档该行重算的 `tilde Z_R` 与 CSV 该行值一致（容差 `1e-8`）

## MODIFIED Requirements

### Requirement: 密网格扫描与中间数据文件

系统 SHALL 在全区间 `s∈[0,1]×δ∈[-3,3]` 上做密网格扫描（默认每轴 100 点、等距、端点包含，结果行数等于网格点数）：求解阶段只输出基态存档（见“基态存档输出”）；`tilde_ZR` CSV 改为存档派生（`derive_zr`），行按 `δ` 外层、`s` 内层排列，UTF-8，表头至少 `s,delta,tilde_ZR[,is_degenerate]`；派生 CSV SHALL 与存档前直算链的历史输出逐行一致（容差 `1e-8`）；旧直算扫描退役。NPZ 存档是求解产物，不替代 CSV 契约。

#### Scenario: 网格覆盖与行数完整

- **WHEN** 以默认配置运行全网格
- **THEN** CSV 行数等于 `ns×ndelta`（默认 `100×100=10000`），`s` 最小值 `0`、最大值 `1`，`δ` 最小值 `-3`、最大值 `3` 均出现，无缺行

#### Scenario: 文件即契约

- **WHEN** Python 绘图端仅读取该 CSV（不调用 Julia）
- **THEN** 无需任何额外参数即可画出完整热力图；CSV 缺列或行数不符时绘图端必须报可读错误

#### Scenario: 迁移回归一致

- **WHEN** 用存档派生链重新生成 `tilde_ZR` CSV
- **THEN** 与旧直算链的历史 CSV 逐行一致（容差 `1e-8`），否则迁移不通过
