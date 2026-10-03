# numerics/vqe-reflect-orbit-sweep Specification

## Purpose

沿 `δ=±1` 切线对反射对称 orbit 参数拟设做 1–3 层模拟机扫描并存档，为 orbit 参数在浅层的表达增益提供逐深度、可复算的数值证据；只存档目标值与 theta，不存波函数。

## Requirements

### Requirement: orbit 拟设构造

系统 SHALL 按 `doc/qc/evolution_qc.md` 反射对称 orbit 分组构造拟设：奇轨道 `O_out={(0,1),(6,7)}`、`O_in={(2,3),(4,5)}`、偶轨道 `E_out={(1,2),(5,6)}`、`E_c={(3,4)}`，每轨道继承 `S_z` 守恒的 `(θ_1,θ_2)` 分工（同 orbit 键 `XX/YY` 共 `θ_1`、`ZZ` 独立 `θ_2`），单层 8 参数，`n` 层共 `8n` 参数（`n ∈ {1,2,3}`，即 8/16/24）；初态与子层配对 SHALL 沿用 task3 约定（三初态 triv/topo/afm，`L=8 OBC`，平庸 `U_oU_e`、拓扑 `U_eU_o`、GHZ 取 `U_oU_e`）；层间子层顺序 SHALL 逐层交替、首层保持初态配对顺序；拟设 SHALL 始终待在 `P=−1` 扇区；代价函数 SHALL 为裸 `H` 的 statevector 精确期望、不得引入采样噪声。

#### Scenario: 扇区守恒

- **WHEN** 任取深度与随机 orbit 参数计算拟设的 `P` 期望
- **THEN** 其值在浮点舍入内为 `−1`

#### Scenario: orbit 分组可审计

- **WHEN** 检查任一子层电路的键-参数映射
- **THEN** 镜面对映两键共用同一 `(θ_1,θ_2)`（`(0,1)=(6,7)`、`(2,3)=(4,5)`、`(1,2)=(5,6)`），`(3,4)` 自镜像独立，单层恰 8 自由参数

#### Scenario: GHZ 首层平坦方向

- **WHEN** 检查 GHZ 初态任一点的多 seed 优化结果
- **THEN** 首层 2 个 `θ_2`（首作用子层的每 orbit 各一）可取任意值而不改变目标值（整体相位，容差 `1e-12`）；该两方向的 seed 极差 SHALL NOT 计为优化失败

### Requirement: depth1 两步优化与深层 warm-start（含 pilot 门控）

系统 SHALL 对 depth1 逐点执行两步优化：全局优化（`θ ∈ [0,2π)^{8}` 有界）后以其解为起点做局部 polish；对 depth `k ∈ {2,3}` 逐点执行 warm-start 优化：起点由 depth `k−1` 同点最优 theta 垫底 + 微扰构成（depth2 由本任务 depth1 thetas 递推，不得由 task3/4 uniform thetas 递推；垫底维度 SHALL 为 `8(k−1)`，新层垫 8 参数），每点多组微扰（seed 确定性派生，`seed_base=20260929`，与作废的 4 参数版数据命名空间隔离）取最优并做局部 polish；全量前 SHALL 至少在 depth1 上跑 pilot（3~5 个 `s` 点 × 三初态，覆盖深相端、过渡区、简并区；两档预算起点为 light `{de_maxiter=30, popsize=15, cobyla=300}` 与 base `{50, 20, 500}`），pilot SHALL 报告全局预算、多 seed 极差与 polish 增益，深层微扰尺度与 restart 数 SHALL 由 pilot 结论确定并记录；pilot 不通过时 SHALL 砍深度集合而不得强行全量；同一输入同一 seed 跑两次结果 SHALL 逐位一致（含跨进程）。

#### Scenario: pilot 门控

- **WHEN** 检查任一深度的全量扫描产物
- **THEN** 存在本任务的 pilot 结论记录，全量配置与之对应一致

#### Scenario: 递推一致性

- **WHEN** 对比 depth `k` 起点（零微扰）与 depth `k−1` 最优的目标值
- **THEN** 两者一致（容差 `1e-12`，垫底无退化）

### Requirement: 逐深度目标值与 thetas 存档

系统 SHALL 对每个深度输出目标值 CSV（表头与 task3 同形 `s,delta,E_triv,E_topo,E_afm`，行数 `102`，行序 `delta` 外层、`s` 内层，`s` 端点覆盖 `0` 与 `1` 的 51 点均匀网格）与 thetas 存档（逐点全部 seed 的 theta 与目标值，供更深层递推与后续复用），落盘于本任务该深度专属目录；任一格点失败 SHALL 以非零退出码失败且不写该深度 CSV；增量 checkpoint SHALL 每完成一格点落盘（abort-safe）。

#### Scenario: 变分上界逐深度成立

- **WHEN** 用任一深度的目标值对比同点解析 `E0`
- **THEN** 每行满足 `E_init ≥ E0 − 1e-6`；违反即视为优化失败而非结论

#### Scenario: 深度单调性可审计

- **WHEN** 对比同点相邻深度的最优目标值
- **THEN** 关系如实记录（深层原则上不差于浅层垫底值；若出现退化则记为优化失败线索并复核，不静默接受）

### Requirement: VQE-Q 派生（orbit）

系统 SHALL 从本任务已存档 theta 文件逐点取获胜 `(init, seed)` 的 theta（逐点 argmin，与目标值 CSV 最优值一致），重建 orbit 拟设电路求 statevector，按 `doc/model/operator.md` 计算 `O_str`、`S(π)`、归一化与 `Q`（与 task1/task3 同公式），输出 VQE-Q CSV（表头 `s,delta,Q_vqe`，行数 `102`，行序 `delta` 外层、`s` 内层）；派生 SHALL 为纯 thetas 后处理，不得重跑优化；任一点失败 SHALL 以非零退出码失败且不写文件。

#### Scenario: 可复算

- **WHEN** 用同一 thetas 文件运行派生两次
- **THEN** 两次 CSV 逐位一致

### Requirement: VQE-ZR 派生（orbit）

系统 SHALL 从本任务已存档 theta 文件逐点取获胜 `(init, seed)` 的 theta（逐点 argmin，与目标值 CSV 最优值一致），重建 orbit 拟设电路求 statevector，按 `doc/model/operator.md` 的 ZR 定义（`I={2,3,4,5}`、`Z_R=Tr(ρ_I R_I)` 除以两半纯度均值的平方根）计算归一化 `tilde_Z_R`，输出 VQE-ZR CSV（表头 `s,delta,ZR_vqe`，行数 `102`，行序 `delta` 外层、`s` 内层）；派生 SHALL 为纯 thetas 后处理，不得重跑优化；任一点失败 SHALL 以非零退出码失败且不写文件。

#### Scenario: 可复算

- **WHEN** 用同一 thetas 文件运行派生两次
- **THEN** 两次 CSV 逐位一致
