# Proposal

## Why

三张热力图的数值口径不统一，摆在一起不好读：ZR 已是 [-1,1] 量子化标尺，string 却是 [-1,0]（拓扑端 -1），`S(π)` 是 [1.5,8] 的广延量。统一归一到拓扑端/Néel 端取 1 后，三张图都是"序参量强度 ∈[0,1]"的同一种语言，相图结构（SPT/平庸/Néel 各落何处）一目了然。

## What Changes

- `O_str_norm = -O_str`（取反，不取绝对值）：拓扑端 -1→+1，平庸端 0 不变；线性无损，符号链条保持可审计。
- `S_pi_norm = S(π)/8`：Néel 饱和 8→1，其余等比压缩。
- 派生 CSV 保留原始列并新增归一列（审计链不断）；两张热力图改画归一列，色标统一为 [0,1] 顺序色标；ZR 图不动。
- 范围说明：归一后 string 图 ∈[0,1]、AFM 图 ∈[0,1]（实测约 [0.19,1]）；色棒刻度含 0 与 1。

## Capabilities

### New Capabilities

- 无。

### Modified Capabilities

- `numerics/string-afm-observables`: 新增归一化定义与归一列输出要求（原始列保留）。
- `viz/string-afm-heatmaps`: 改画归一列，色标改为 [0,1] 顺序色标。

## Impact

- 改动面：`derive_string.jl`、`derive_afm.jl`（加归一列）、两次绘图调用参数、两张热力图 PNG/PDF 重出；求解与存档不动，无需重跑 50 分钟对角化。
- CSV 表头新增列（加法变更，旧列保留，下游旧脚本仍可读）。
- ZR 链（数值与图）不受影响。
