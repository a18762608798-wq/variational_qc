# Proposal

## Why

三张归一化热力图各讲各的语言（string 拓扑 +1、ZR 拓扑 -1、AFM 峰值 1），并排判读时需要在脑子里做换算。`doc/model/operator.md` 新增的 ZR-like 组合量 `Q` 把 string 的符号信息与 AFM 门控合成一张图（平庸 +1、拓扑 -1、AFM 0），与 ZR 图同语言，可直接逐像素对照、互相验证。

## What Changes

- 从两个派生 CSV 的归一列计算 `Q = (1-2Õ_str_norm) - (4/3)(S_pi_norm-1/4)`，输出新 CSV `data/interim/Q_L8_OBC.csv`（`s,delta,Q` 三元组契约，同序同行数；纯 Python 后处理，不碰 Julia、不重跑求解）。
- 用既有绘图脚本出第四张热力图 `Q_heatmap.png/pdf`：RdBu 发散色标（中心 0、范围 [-1,1]、-1/0/+1 刻度），标题无边界条件字样。
- `Q` 定义以 `doc/model/operator.md` 为准（已落文档，本增量只实现）。

## Capabilities

### New Capabilities

- 无。

### Modified Capabilities

- `numerics/string-afm-observables`: 新增 `Q` 组合量计算与 CSV 输出 requirement（既有行为不动）。
- `viz/string-afm-heatmaps`: 新增 `Q` 热力图 requirement（既有两张图不动）。

## Impact

- 新增：一个 Python 后处理脚本（或 Julia derive，二选一，实现时按 design 定）、`Q_L8_OBC.csv`、第四张图；存档、求解、既有三张图均不动。
- 无新增依赖（pandas/numpy 已有）。
