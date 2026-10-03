# Proposal

## Why

终极目标是在 quafu 平台上用一般变分电路制备目标态并测量其拓扑性质，一次到位风险过高。先建立一个可复现的数值基线：在 8 比特下对解析模型求基态并计算拓扑不变量，为后续变分/硬件实验提供对照标准与可扩展的代码骨架。

## What Changes

- 在 `L=8`、OBC 下构造 `doc/model/H.md` 定义的 AHC 哈密顿量 `H(s,δ)`，用 Julia QuantumToolbox.jl 求解每个 `(s,δ)` 点的基态。
- 按 `doc/model/operator.md` 的 ZR 特殊值设置（`I={2,3,4,5}`，`I1={2,3}`，`I2={4,5}`，反射中心在 `3-4` 键）计算归一化 `tilde Z_R`。
- 以文件（CSV/NPZ）为 Julia→Python 交接界面，用 Python 在 `s∈[0,1]×δ∈[-3,3]` 密网格上绘制 `tilde Z_R` 热力图并落盘。
- 按功能/领域边界搭建可扩展的仓库骨架，区分后续可复用的 shared 能力与本次子问题专用代码；Python 环境创建遵循 `env-python` skill。

## Capabilities

### New Capabilities

- `numerics/zr-ground-state`: OBC 下 8 比特 `H(s,δ)` 构造、基态求解、约化密度矩阵与 `tilde Z_R` 计算、中间数据文件输出。
- `viz/zr-heatmap`: 从中间数据文件读取 `(s,δ,tilde_Z_R)` 并绘制/输出热力图。

### Modified Capabilities

- 无（新项目首个增量，无既有 spec 可改）。

## Impact

- 新增 Julia 求解代码、Python 绘图代码、中间数据与图片产物约定、仓库目录骨架（features/domains/shared 风格，适配 Julia+Python 双语言）。
- 新增依赖：Julia QuantumToolbox.jl、Python 科学计算/绘图栈（matplotlib/numpy/pandas 之一）；不影响 quafu 硬件链路（本次不接入）。
- 后续增量（变分电路、quafu 制备与测量、string/AFM 量）将复用本增量的目录约定与数据接口。
