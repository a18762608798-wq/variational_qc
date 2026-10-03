# Spec Delta

## Purpose

沿 `δ=±1` 切线对 nosym 初态做 depth1 全局优化与 depth5 直跳 warm-start 扫描并存档，量化真机简化初态相对对称初态的能量与相落点代价；只存档目标值与 theta，不存波函数。

## ADDED Requirements

### Requirement: nosym 初态与拟态构造

系统 SHALL 按 `doc/qc/initial_state.md` 真机简化版制备三初态（triv 与对称版一致；topo 为 bulk 三单态 + $|00\rangle_{0,7}$；AFM 为单支 $|01010101\rangle$，比特串按格点 `0→7`），拟态层结构与子层配对惯例 SHALL 与 task3/4 一致（单层 4 参数；多层逐层交替、首层配对），代价函数 SHALL 为裸 `H` 的 statevector 精确期望；拟态 SHALL 保持 `P`（门本身保 `P`），但初态可不在 `P=−1` 扇区——此时 min `H` 与 min `H'` 的等价性 SHALL NOT 被假定，只以解析 `E0` 为变分上界基准。

#### Scenario: 制备深度可审计

- **WHEN** 检查三初态电路
- **THEN** triv/topo-nosym 全为局域两比特门（topo 无长程门），AFM-nosym 仅奇数位 X、无 H、无 CNOT 链

#### Scenario: P 期望只记录不断言

- **WHEN** 任取一组参数计算拟态的 `P` 期望
- **THEN** 其值如实记录（预期偏离 `−1`），偏离本身记为结论而非失败

### Requirement: depth1 优化与 depth5 直跳

系统 SHALL 对 depth1 逐点执行 task3 同形两步优化（有界全局 + COBYLA polish，seed 确定性派生）；对 depth5 逐点执行直跳 warm-start（起点由本任务 depth1 同点最优 theta 垫底 + 16 参数微扰，微扰尺度由 pilot 实测、不得沿用 task4 的 0.3），每点 3 组微扰取最优并 polish；全量前 SHALL 跑 depth1 与 depth5 的 pilot（3~5 个 `s` 点 × 三初态），pilot 不通过 SHALL 砍范围而不得强行全量。

#### Scenario: 标定点保真度更新

- **WHEN** 在 doc 标定点对比 nosym 初态与 `H'` 基态
- **THEN** triv 保真度为 1，topo-nosym 与 AFM 单支保真度按实测记录（预期 < 1，不判失败；AFM 单支 vs GHZ 理论值约为 1/2，可作电路正确性交叉验证）

#### Scenario: 递推与确定性

- **WHEN** 对比 depth5 零微扰起点与 depth1 最优目标值
- **THEN** 两者一致（容差 `1e-12`）；同一输入同一 seed 跑两次逐位一致

### Requirement: 逐深度目标值与 thetas 存档

系统 SHALL 对每个深度（`{1,5}`）输出目标值 CSV（表头 `s,delta,E_triv,E_topo,E_afm`，此处三列指 nosym 初态，行数 `102`，行序 `delta` 外层、`s` 内层）与 thetas 存档（逐点全部 seed 的 theta 与目标值），落盘于本任务该深度专属目录；Q/ZR 派生 SHALL 复用既有定义（获胜 thetas 后处理）；任一格点失败 SHALL 以非零退出码失败且不写该深度 CSV；增量 checkpoint SHALL 每完成一格点落盘。

#### Scenario: 变分上界成立

- **WHEN** 用任一深度的目标值对比同点解析 `E0`
- **THEN** 每行满足 `E_init ≥ E0 − 1e-6`；违反即视为优化失败而非结论
