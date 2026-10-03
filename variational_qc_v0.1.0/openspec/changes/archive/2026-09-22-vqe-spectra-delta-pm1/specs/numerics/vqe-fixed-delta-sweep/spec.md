# Spec Delta

## Purpose

沿 `δ=±1` 切线对三初态变分拟态做两步优化扫描并存档目标值，为 VQE 表达能力提供以点数为单位、可复算的数值证据；只存档优化目标值，不存档波函数与优化轨迹。

## ADDED Requirements

### Requirement: 初态与拟态构造

系统 SHALL 按 `doc/qc/initial_state.md` 制备三个初态（平庸 intra 单态乘积、拓扑 bulk+首尾单态、AFM Néel GHZ，`L=8`）并按 `doc/qc/evolution_qc.md` 配对子层顺序（平庸 `U_oU_e`、拓扑 `U_eU_o`、GHZ 两种等价）；拟态 SHALL 为单层 4 参数（`S_z` 守恒约束下 `XX/YY` 共参数、`ZZ` 独立），始终待在 `P=−1` 扇区；代价函数 SHALL 为裸 `H` 的期望（`doc/qc/objective.md`），模拟 SHALL 用 statevector 精确期望、不得引入采样噪声。

#### Scenario: 初态可制备

- **WHEN** 检查三初态电路
- **THEN** 平庸/拓扑中间对为局域两比特制备，拓扑首尾对经长程 CNOT 或 SWAP 链，GHZ 经链式 CNOT，深度均为 `O(L)`

#### Scenario: 扇区守恒

- **WHEN** 任取一组参数计算拟态的 `P` 期望
- **THEN** 其值在浮点舍入内为 `−1`

### Requirement: 两步优化与 pilot 定预算

系统 SHALL 对每点执行两步优化：全局优化（`θ ∈ [0,2π)^4` 有界）后以其解为起点做局部 polish；全量扫描前 SHALL 先跑 3~5 个代表性 `s` 点的 pilot（覆盖深平庸端、过渡区、简并区），pilot SHALL 报告全局预算（种群/迭代）、多 seed 稳定性与 polish 前后差值，全量预算 SHALL 由 pilot 结论确定并记录；同一输入同一 seed 跑两次结果 SHALL 逐位一致。

#### Scenario: pilot 先行

- **WHEN** 检查全量扫描产物
- **THEN** 存在 pilot 结论记录（含预算取值依据），全量配置与 pilot 结论一致

#### Scenario: polish 有效

- **WHEN** 对比 pilot 点全局解与 polish 后目标值
- **THEN** polish 后不差于全局解（容差 `1e-12`），且多 seed 下最优值稳定（极差记入结论）

### Requirement: VQE 目标值 CSV 契约

系统 SHALL 输出 UTF-8 谱 CSV（表头 `s,delta,E_triv,E_topo,E_afm`，三列为三初态在该点的优化目标值即 min `H`，绝对能量），行数为 `102`（2 `δ` × 51 `s`），行序 SHALL 为 `delta` 外层、`s` 内层，`s` 端点覆盖 `0` 与 `1`；任一格点优化失败（不收敛/异常）时 SHALL 以非零退出码失败并指明坐标，不得静默填数。

#### Scenario: 行数与同序

- **WHEN** 以默认配置运行扫描
- **THEN** CSV 共 `102` 行，第 `k` 行 `(s,delta)` 网格由配置声明（`s` 端点覆盖 `0` 与 `1` 的 51 点均匀网格）

#### Scenario: 可复算

- **WHEN** 用存档目标值对比同点解析 `E0`
- **THEN** 每行满足 `E_init ≥ E0 − 1e-6`（变分上界性，浮点舍入内）；违反即视为优化失败而非结论

### Requirement: VQE-Q 派生

系统 SHALL 从已存档 theta 文件逐点取获胜 `(init, seed)` 的 theta（逐点 argmin，与目标值 CSV 最优值一致），重建拟态电路求 statevector，按 `doc/model/operator.md` 计算 `O_str`、`S(π)`、归一化（`O_str_norm = -O_str`、`S_pi_norm = S(π)/8`）与 `Q`（与 task1 同公式），输出 VQE-Q CSV（表头 `s,delta,Q_vqe`，绝对定义，行数 `102`，行序 `delta` 外层、`s` 内层）；派生 SHALL 为纯 thetas 后处理，不得重跑优化；任一点失败 SHALL 以非零退出码失败且不写文件。

#### Scenario: 算子可验证

- **WHEN** 用 Python 算子在经 bit-reverse 的 Julia 存档态上复算任一网格点
- **THEN** 与 task1 `Ostr`/`Spi` CSV 同行值一致（容差 `1e-8`）

#### Scenario: 可复算

- **WHEN** 用同一 thetas 文件运行派生两次
- **THEN** 两次 CSV 逐位一致

### Requirement: VQE-ZR 派生

系统 SHALL 从已存档 theta 文件逐点取获胜 `(init, seed)` 的 theta（逐点 argmin，与目标值 CSV 最优值一致），重建拟态电路求 statevector，按 `doc/model/operator.md` 的 ZR 定义（`I={2,3,4,5}`、`Z_R=Tr(ρ_I R_I)` 除以两半纯度均值的平方根）计算归一化 `tilde_Z_R`，输出 VQE-ZR CSV（表头 `s,delta,ZR_vqe`，行数 `102`，行序 `delta` 外层、`s` 内层）；派生 SHALL 为纯 thetas 后处理，不得重跑优化；任一点失败 SHALL 以非零退出码失败且不写文件。

#### Scenario: 算子可验证

- **WHEN** 用 Python 算子在经 bit-reverse 的 Julia 存档态上复算任一网格点
- **THEN** 与 task1 `tilde_ZR` CSV 同行值一致（容差 `1e-8`）

#### Scenario: 可复算

- **WHEN** 用同一 thetas 文件运行派生两次
- **THEN** 两次 CSV 逐位一致
