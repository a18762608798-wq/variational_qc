# Proposal

## Why

task3/4 的初态全是"对称性正确但真机难做"：拓扑初态要长程 CNOT/SWAP 链，AFM 初态要 H + 链式 CNOT。`doc/qc/initial_state.md` 新增的真机简化版（topo 去 $(0,7)$ link、AFM 取 Néel 单支）把制备压到局域门/`O(1)` 深度，代价是初态掉出 $P=-1$ 扇区——此时拟态仍保 $P$，VQE 将被锁在错误扇区组合里，min $H$ 与 min $H'$ 的等价性不再成立。这个任务要量化这笔交易：在 depth1 和 depth5 两端，简化初态相对对称初态损失多少能量精度、Q/ZR 相落点偏移多少。这是真机实验前的必答题。

## What Changes

- 新顶层任务目录（如 `task5_vqe_nosym/`），初态换 nosym 版（triv 不变仍对称；topo 为 bulk 三单态 + $|00\rangle_{0,7}$；AFM 为单支 $|01010101\rangle$），拟态层结构、子层配对惯例、代价函数（裸 $H$）、statevector 约定与 task3/4 一致；仍做模拟。
- 只跑深度 {1, 5}：depth1 沿 task3 路线（DE 全局 + COBYLA polish）；depth5 由本任务 depth1 nosym 最优直跳垫底 + 16 参数微扰 + polish，3 restart 取最优。
- 每深度、每条 `δ` 线输出 3 张图：min-energy 三线、Q 双线、ZR 双线（与 task4 同形）；不画分初态能量线。产物按深度分目录。
- pilot 跑 depth1 和 depth5（16 维直跳的微扰尺度必须实测，不得沿用 0.3）。

## Capabilities

### New Capabilities

- `numerics/vqe-nosym-sweep`: nosym 初态 depth1 全局优化 + depth5 直跳 warm-start 扫描与存档（含 pilot）。

### Modified Capabilities

- `viz/vqe-comparison`: 新增 nosym 逐深度画布组（每深度每 `δ` 三张：min-energy、Q、ZR），落本任务深度专属目录。

## Impact

- 新目录 `task5_*`，初态制备函数新增 nosym 分支，其余链路（优化、派生、画图）复用 task3/4；不动 task1~4 任何产物与结论。
- 无新增依赖；Python 解释器沿用项目 pixi env。
- 计算量：约 2 个深度 × 300 格点；depth5 直跳单点耗时以 pilot 为准。
