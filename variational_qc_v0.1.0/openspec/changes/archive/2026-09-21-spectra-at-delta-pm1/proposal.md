# Proposal

## Why

相图热力图只给出基态派生量的分布，看不到激发隙沿 `s` 的开合——而 task2 的核心结论（P 劈开 SPT 端简并、挑出 `(M=0,+1)` 分支）本质上是能隙 statement。沿 `δ=±1` 切 `s` 轴画基态+第一激发态能量，可以直接看到：task1 在何处隙闭合（简并）、task2 中 P 如何把隙撑开。这是 task1/task2 已有数值结论的互补证据，计算代价几乎为零（既有 solver 本来就做全对角化，`gap` 已顺手算出）。

## What Changes

- 对两个任务的哈密顿量（task1 的 `H`、task2 的 `H'=H+P`）分别在 `δ=-1`、`δ=+1` 上做 `s∈[0,1]` 均匀 201 点扫描，每点记录基态能量 `E0` 与第一激发态能量 `E1`（绝对能量，不减零点），输出谱 CSV。
- 每个任务绘制一个画布、两个子图（左 `δ=-1`、右 `δ=+1`），横轴 `s`、纵轴绝对能量，两条线（`E0`、`E1`），落盘 PNG（必选）+ PDF（可选同名）。
- solver 本体逻辑不变，只需把已算出的第二本征值一并返回（`gap` 已有，`E1 = E0 + gap`）；`λ=1`、网格端点等既有约定不变。

## Capabilities

### New Capabilities

- `numerics/spectra-at-fixed-delta`: 固定 `δ` 切 `s` 轴的全谱（最低两支）扫描与谱 CSV 存档。

### Modified Capabilities

- `viz/string-afm-heatmaps`: 新增两张能谱画布（task1、task2 各一，一画布两子图）。（注：能谱图与 heatmaps 同属"派生 CSV 纯渲染"家族，暂归此 capability；如 reviewer 认为应单立 `viz/spectra` capability，可在 specs 阶段调整。）

## Impact

- `shared/numerics/ground_state.jl`：`solve_ground_state` 返回值增加 `excited`（第一激发态能量），旧调用方不受影响（具名字段追加）。
- 各任务新增谱扫描脚本 + 谱 CSV + 能谱图；不碰既有 `psi_archive`、派生 CSV 与热力图。
- 计算量：每任务 `2×201` 次 256 维稠密对角化，与既有烟测同量级，秒级完成。
