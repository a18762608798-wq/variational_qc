# hardware/vqe-forward-d1 Specification

## Purpose

把 Aer 单层 VQE 最优参数搬上真机做前向测量，存档硬件噪声下的 H 期望与 Q 落点，与 E0/E1 解析谱对比，验证真机可执行性；不做真机优化，不测 ZR。

## Requirements

### Requirement: Aer 参数原样前向测量

系统 SHALL 对 δ=±1 全网格（51×2，行序 delta 外层、s 内层）逐点执行：
sym 三初态用 task3 depth-1 获胜 theta，nosym 三初态用 task5 depth-1 获胜
theta，拟态结构（单层 4 参数、子层配对惯例）与 Aer 一致；逐点 SHALL 测
X/Y/Z 三基（1024 shots，读出纠错打开），由三基计数合成 H 期望，
由 Z 基计数合成 Q（O_str/S(pi) 皆 Z-对角），由 Z 基与 X 基合成 P 两项
（只记录不断言）；真机 SHALL NOT 做任何参数优化。

#### Scenario: 零优化可验证

- **WHEN** 检查任一提交电路的参数
- **THEN** 其 theta 与对应 Aer 获胜值逐位一致（容差 1e-12），无优化痕迹

#### Scenario: Q 与 P 免费

- **WHEN** 某点三基计数齐全
- **THEN** Q、Z_tot²、∏X 均可由既有计数合成，无需额外电路

### Requirement: 比特映射与提交

系统 SHALL 全量使用 Baihua：sym-triv/AFM 与 nosym 三初态映射冠军链
`[67..74]`（逻辑 0..7 按序）；sym-topo 映射最优环最佳 8
`[126,127,128,129,142,141,140,139]` + 桥比特 `{125,138}` 走 0-7 连接
（经 `139-138-125-126` 三跳 SWAP）；提交 SHALL 一次性全量
（约 612 点 × 3 电路），提交前 SHALL 打印账单并人工确认；
提交当天 SHALL force 重拉拓扑验映射比特存活，任一死亡 SHALL 中断提交。

#### Scenario: 账单先行

- **WHEN** 真机提交尚未开始
- **THEN** 账单已打印（点数×3电路×1024），无人工确认 SHALL NOT 提交

#### Scenario: 转译优化开满

- **WHEN** 任一测量电路提交前转译
- **THEN** optimization_level SHALL 为 3，basis_gates SHALL 为硬件原生门集，
  coupling_map SHALL 按映射 pin 死（链任务为线性、sym-topo 为 10-环闭合），
  转译后 CZ 数 SHALL NOT 多于逻辑电路（只许合并单比特门）

### Requirement: 存档与对照画布

系统 SHALL 存档目标值 CSV（表头 `s,delta,E_triv,E_topo,E_afm`，行数 102，
行序与 task3 一致）与 Q CSV，并在 min-energy 画布（解析 E0/E1 + 真机
min）与 Q 画布（解析 Q + 真机 Q）上对照；每份电路原始计数 SHALL
checkpoint 落盘，中断重跑只补缺失；任一格点失败 SHALL 以非零退出码失败
且不写该任务 CSV。

#### Scenario: 对标 task3 可并排判读

- **WHEN** 并排查看同 δ 下 task3 Aer 画布与本任务真机画布
- **THEN** 线齐全图例可分；真机相对 Aer 的整体偏移即硬件噪声 penalty，
  如实呈现（均为结论）
