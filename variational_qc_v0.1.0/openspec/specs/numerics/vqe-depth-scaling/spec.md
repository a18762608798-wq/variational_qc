# numerics/vqe-depth-scaling Specification

## Purpose

沿 `δ=±1` 切线对 2~5 层变分拟态做 warm-start 扫描并存档，为 depth scaling（过渡区缺口是否随深度闭合）提供逐深度、可复算的数值证据；只存档目标值与 theta，不存波函数。

## Requirements

### Requirement: 多层拟态构造

系统 SHALL 按 task3 初态与子层配对构造多层拟态：层数 `n ∈ {2,3,4,5}`，每层 4 参数（`S_z` 守恒约束不变），层间子层顺序 SHALL 逐层交替、首层保持初态配对顺序；拟态 SHALL 始终待在 `P=−1` 扇区；代价函数 SHALL 为裸 `H` 的 statevector 精确期望、不得引入采样噪声。

#### Scenario: 扇区守恒

- **WHEN** 任取深度与随机参数计算拟态的 `P` 期望
- **THEN** 其值在浮点舍入内为 `−1`

#### Scenario: 单层退化一致

- **WHEN** 取 `n=1` 的多层构造与 task3 单层电路同参数对比
- **THEN** 两者 statevector 逐位一致（多层实现向单层回退无回归）

### Requirement: warm-start 优化与升级 pilot

系统 SHALL 对 depth `k` 逐点执行 warm-start 优化：起点由 depth `k−1` 同点最优 theta 垫底 + 微扰构成（depth2 由 task3 单层 thetas 递推），每点 3 组微扰（seed 确定性派生）取最优并做局部 polish；全量前 SHALL 至少在 depth2 和 depth5 上跑 pilot（3~5 个 `s` 点 × 三初态，覆盖深相端、过渡区、简并区），pilot SHALL 报告微扰尺度、polish 增益与多 seed 极差，中间深度预算 SHALL 由 pilot 插值确定并记录；pilot 不通过时 SHALL 砍深度集合而不得强行全量。

#### Scenario: pilot 门控

- **WHEN** 检查任一深度的全量扫描产物
- **THEN** 存在该深度（或其插值依据深度）的 pilot 结论记录，全量配置与之对应一致

#### Scenario: 递推一致性

- **WHEN** 对比 depth `k` 起点（零微扰）与 depth `k−1` 最优的目标值
- **THEN** 两者一致（容差 `1e-12`，垫底无退化）；同一输入同一 seed 跑两次逐位一致

### Requirement: 逐深度目标值与 thetas 存档

系统 SHALL 对每个深度输出目标值 CSV（表头与 task3 同形 `s,delta,E_triv,E_topo,E_afm`，行数 `102`，行序 `delta` 外层、`s` 内层）与 thetas 存档（逐点全部 seed 的 theta 与目标值，供更深层递推与后续复用），落盘于该深度专属目录；任一格点失败 SHALL 以非零退出码失败且不写该深度 CSV；增量 checkpoint SHALL 每完成一格点落盘（abort-safe）。

#### Scenario: 变分上界逐深度成立

- **WHEN** 用任一深度的目标值对比同点解析 `E0`
- **THEN** 每行满足 `E_init ≥ E0 − 1e-6`；违反即视为优化失败而非结论

#### Scenario: 深度单调性可审计

- **WHEN** 对比同点相邻深度的最优目标值
- **THEN** 关系如实记录（深层原则上不差于浅层垫底值；若出现退化则记为优化失败线索并复核，不静默接受）
