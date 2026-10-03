# Proposal

## Why

task8 的 O/S 画布只有两条线（解析 + 真机），缺了中间一档——同层拟设在
Aer 下的精确值。没有它，真机偏离解析的原因说不清：是变分表达不够，
还是硬件噪声。三线放一起（解析 + Aer-d1 + 真机-d1），"加一层拟设有用吗、
真机差在哪"直接可读。这是主要目的。

## What Changes

- 由 task3/task5 depth-1 thetas 经 statevector 精确导出 Aer O/S 分量
  （sym/nosym，102 点， winner 口径与 task8 一致：E 最优初态），
  存 `task8_hardware_vqe/data/interim/vqe_{sym,nosym}_OS_aer_L8_OBC.csv`。
- O/S × δ=±1 × sym/nosym 共 8 张三线对照图
  （解析 Ostr/Spi + Aer-d1 + 真机-d1），落盘 task8 figures/os/，
  文件名带 `aer` 标识。只要 OS 图，不要 min/Q/full。
- Aer 导出零机时（本地 statevector）；真机数据复用 task9 OS CSV。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `viz/vqe-comparison`: O/S 对照画布加第三线（Aer-d1）。

## Impact

- 新增 CSV 2 个、PNG/PDF 16 张；零真机提交、零新 Aer sweep
  （thetas 现成，statevector 本地算）。
- `plot_vqe.py` o/s 模式需支持第三线（小幅扩展，落盘逻辑复用）。
