# Proposal

## Why

单层 VQE 的结论已经清楚：相深处贴住 `E0`，过渡区差 0.156，且序参量证明它跟的是 diabatic 分支。下一个问题是 depth scaling：加到 2~5 层，过渡区的能量缺口能不能闭合、Q/ZR 的阶梯跳变会不会磨平？这是"单层不够"之后自然的第二步，也是给"浅层 + 好初态是 NISQ 甜点"这一判断提供反面证据（如果 5 层仍啃不动边界，浅层结论更硬；如果啃动了，得到 depth scaling 曲线）。

## What Changes

- 新顶层任务目录（如 `task4_vqe_depth/`），深度集合 `{2,3,4,5}`；拟态为多层（每层 4 参数，层间子层顺序逐层交替、首层保持初态配对），初态/代价函数/statevector 约定与 task3 完全一致。
- 优化路线为 warm-start：depth `k` 的起点由 depth `k−1` 最优 theta 垫底 + 微扰构成（depth2 由 task3 单层 thetas 递推），每点 3 组微扰取最优；不做全量全局重搜。
- 每个深度、每条 `δ` 线输出 3 张图：min-energy 三线（`E0`/`E1`/`min`）、Q 双线、ZR 双线；不画分初态能量线。产物按深度分目录存放。
- pilot 升级：至少在 depth2 和 depth5 上跑（3~5 个 `s` 点 × 三初态），中间深度插值预算；pilot 跑崩则砍深度集合。

## Capabilities

### New Capabilities

- `numerics/vqe-depth-scaling`: 多层拟态 warm-start 扫描与逐深度目标值/thetas 存档（含升级 pilot）。

### Modified Capabilities

- `viz/vqe-comparison`: 新增逐深度画布组（每深度每 `δ` 三张：min-energy、Q、ZR），按深度分目录。

## Impact

- 新目录 `task4_*`，复用 task3 脚本（`ansatz` 加 `n_layers` 参数、画图三 mode、Q/ZR 派生链）与 task1 解析 CSV；不动 task1/task2/task3 任何产物与结论。
- 无新增依赖（qiskit/scipy 已就位）；Python 解释器沿用项目 pixi env。
- 计算量：4 个深度 × 约 300 格点 × 3 微扰，单点耗时随深度增长（pilot 实测为准，预计总量十几小时，8 workers 并行 + 增量 checkpoint）。
