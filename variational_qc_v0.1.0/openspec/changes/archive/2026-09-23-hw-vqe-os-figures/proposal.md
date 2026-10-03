# Proposal

## Why

task8 的 Q 是 `O_str` 与 AFM 结构因子 `S(pi)` 合成的，但分量本身的真机行为
（string 序参塌在哪、结构因子峰剩多少）被合成掩盖了。两分量可由既有 Z 基
计数零机时重算；同时 figures/ 下 16 张图平铺无分类，需要子目录整理。

## What Changes

- `derive_hw.py` 加分量输出：`O_norm / S_norm / <O_str> / <S(pi)>` 四列，
  新写 `vqe_{sym,nosym}_OS_L8_OBC.csv`（不动已有 CSV 表头）。
- O 与 S 对照画布 8 张（O/S × δ=±1 × sym/nosym），对标 Q 画布画法
  （解析线 task1 `Ostr/Spi` + 真机线）。
- figures/ 分类子目录：`min/`、`q/`、`full/`、`os/`；现有 16 张按类搬入，
  文件名语义不变（只换目录）。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `viz/vqe-comparison`: 新增真机 O/S 分量对照画布需求。

## Impact

- 新增 CSV 2 个、PNG/PDF 16 张（8 画布×2 格式）；文件移动 16 张。
- 零真机提交（纯已落盘计数后处理）；`shared/viz/plot_vqe.py` 加 `--mode o/s`
  两个模式（读 OS CSV + task1 `Ostr/Spi` 解析线），其余代码不动。
