# Proposal

## Why

Aer 上的 depth-1 VQE（task3 对称初态、task5 简化初态）只证明了变分表达能力，
没证明真机可执行性。现在选链（task6）与选环（task7）已给出 Baihua 最优
比特，是时候把 Aer 最优参数原样搬上真机，做纯前向测量：量出硬件噪声下
的能量与 Q 落点，与 E0/E1 解析线直接对比。

## What Changes

- 在 `04_project/variational_param` 下新增 task8（`task8_hardware_vqe/`）：
  真机单层 VQE 前向测量，两种初态任务（sym / nosym），δ=±1 全网格
  （51×2），无 ZR、无真机优化。
- thetas：sym 用 task3、nosym 用 task5 的 depth-1 获胜值，原样执行。
- 映射（全 Baihua）：sym-triv/AFM 与 nosym 三初态 → 冠军链 `[67..74]`；
  sym-topo → 最优环最佳 8 `[126..139]` + 桥比特 `{125,138}` 走 0-7 连接。
- 逐点 X/Y/Z 三基测量：H 期望全覆盖；Q、`Z_tot²`、`∏X` 免费顺带
  （P 只记录不断言）；读出纠错打开；shots 1024。
- 转译优化开满（optimization_level=3，basis_gates 为硬件原生门集），
  coupling_map 按映射 pin 死（链为线性、环为 10-环闭合），压真机电路深度。
- 一次全交（约 1836 任务），提交当天验比特存活；对标 task3 画布
  （min-energy + Q，去 ZR）。

## Capabilities

### New Capabilities

- `hardware/vqe-forward-d1`: 在真机上以前向测量执行 Aer 最优单层 VQE 参数并存档 H/Q，与解析谱对比。

### Modified Capabilities

（无）

## Impact

- 新增 `task8_hardware_vqe/` 目录（解释器复用 qmeas env）。
- 真机提交：约 612 点 × 3 电路 × 1024 shots ≈ 188 万 shots，一次提交，提交前账单确认。
- 需要 `QUARK_TOKEN`；token 永不进代码。
- 无现有代码改动；产物 CSV/画布对标 task3（行序、纵轴语言一致）。
