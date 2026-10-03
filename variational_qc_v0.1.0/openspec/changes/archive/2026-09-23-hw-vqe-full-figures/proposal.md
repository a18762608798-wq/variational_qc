# Proposal

## Why

task8 已有 min-energy（3 线）与 Q（2 线）对照画布，但看不到三分量
（triv/topo/afm 各自 cost）在真机噪声下的分化——task3 的 5 线
`vqe_comparison` 画布才有这个信息。补两张 sym 任务的 full 画布
（δ=±1），与 Aer 版并排可判读各相出发点的硬件 penalty 差异。

## What Changes

- 用既有 `shared/viz/plot_vqe.py --mode full` 对 task8 sym 与 nosym 数据
  各渲染两张 5 线画布（E0/E1 + 三初态真机 cost），δ=±1 各一，共 4 张。
- 落盘 `task8_hardware_vqe/data/figures/vqe_hw_{sym,nosym}_full_delta{m1,p1}.png`
  （+ 同名 PDF，绘图器默认行为）。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `viz/vqe-comparison`: 新增真机 sym full 五线画布需求（现有 min/q 之外）。

## Impact

- 新增 PNG/PDF 各 2 张；零真机提交（纯已落盘 CSV 后处理）。
- 无现有代码改动。
