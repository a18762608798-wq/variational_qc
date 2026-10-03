# Proposal

## Why

解析相图（`s-δ` 热力图、`δ=±1` 能谱）已经完整，但全是经典精确对角化的结果。下一步要回答的是量子实验问题：`doc/qc/` 定义的单层变分拟态（4 参数、始终待在 `P=−1` 扇区）能不能在各相区实际达到基态能量？沿 `δ=±1` 切 `s` 轴做 VQE 扫描，并与解析 `E0/E1` 同图对照，可以直接看到每个初态在自己相区贴住 `E0`、在别相区偏离——这是变分实验的第一个可发表证据，也是后续加层数、加噪声模型的基线。

## What Changes

- 用 Qiskit Aer statevector 模拟，对三个初态（`doc/qc/initial_state.md`：平庸单态乘积、拓扑 bulk+首尾单态、AFM Néel GHZ）各配 `doc/qc/evolution_qc.md` 的子层顺序，单层 4 参数拟态，以裸 `H` 为代价函数（`doc/qc/objective.md`），在 `δ ∈ {-1,+1}` × `s ∈ [0,1]` 均匀 51 点上逐点做"全局优化 + 局部 polish"两步优化，输出每任务一份 VQE 目标值 CSV。
- 优化预算不拍脑袋：先跑 3~5 个代表性 `s` 点的 pilot（深平庸端、过渡区、简并区），定出够用的全局预算（seed 稳定性 + polish 前后差值收敛），再全量约 300 点。
- 每条 `δ` 线绘制一个图：解析 `E0`、`E1` 两条线 + 三个初态的 VQE 最优三条线，共 5 线；一共两个图。
- 另每条 `δ` 线绘制一个三线图：`min(VQE)`（同点三初态最优逐点取最小）+ 解析 `E0`、`E1`；一共两个图，共四个画布。
- 另每条 `δ` 线绘制一个双线 Q 图：`Q_vqe`（min(VQE) 态的 Q 期望）+ 解析 `Q`；一共两个图，共六个画布。
- 另每条 `δ` 线绘制一个双线 ZR 图：`ZR_vqe`（min(VQE) 态的归一化 ZR）+ 解析 `tilde_Z_R`；一共两个图，共八个画布。

## Capabilities

### New Capabilities

- `numerics/vqe-fixed-delta-sweep`: 三初态 × 两 `δ` 切线的 VQE 两步优化扫描与目标值 CSV 存档（含 pilot 定预算），另含 VQE-Q 派生与 VQE-ZR 派生（thetas 后处理）。
- `viz/vqe-comparison`: 每 `δ` 一画布五线对照图（解析 `E0/E1` + 三条 VQE 最优线），另每 `δ` 一画布三线图（`min(VQE)` + `E0/E1`），另每 `δ` 一画布双线 Q 图（`Q_vqe` + 解析 `Q`），另每 `δ` 一画布双线 ZR 图（`ZR_vqe` + 解析 `tilde_Z_R`）。

## Impact

- 新增 Python 实验目录（如 `task3_vqe/`，自带 `data/interim`、`data/figures` 与配置），复用既有解析 CSV（`spectra_L8_OBC.csv`）做对照线；不动 task1/task2 任何产物。
- 新增依赖 `qiskit`、`qiskit-aer`（走 CondaPkg，与既有 numpy/matplotlib/pandas 同管理）；Python 解释器沿用项目 pixi env。
- 计算量：约 300 次两步优化（statevector 精确、无采样噪声），各点独立可多进程并行。
