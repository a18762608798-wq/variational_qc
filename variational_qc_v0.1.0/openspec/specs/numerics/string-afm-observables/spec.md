# numerics/string-afm-observables Specification

## Purpose

从基态存档派生互补序参量，为相图提供拓扑/磁性双重证据：string operator 标记 SPT 区，AFM 结构因子标定反铁磁区；两者只读存档、不重复对角化。

## Requirements

### Requirement: string operator 计算

系统 SHALL 按 `doc/model/operator.md` 从存档基态计算 `O_str`（OBC，`d=L/2-1`，`1/4` 归一从略与既有约定一致）：`O_str(d)=(Z_0+Z_1)[∏_{l=1}^{d-1}(-Z_{2l}Z_{2l+1})](Z_{2d}+Z_{2d+1})`，起点固定格点 `0,1`；输出 SHALL 为实数。

#### Scenario: 公式可审计

- **WHEN** 检查任一输出点的计算链
- **THEN** 能追溯到存档中的基态行、算符构造（起点与键列表）与期望值，且同一存档跑两次结果逐位一致

#### Scenario: 两端显著不同

- **WHEN** 比较深拓扑端（如 `s=1, δ=0`）与深平庸端（如 `s=0, δ=0`）的 `O_str`
- **THEN** 两者取值显著不同（拓扑端为有限值；具体数值由实现记录，不在 spec 写死阈值）

#### Scenario: 与直算交叉一致

- **WHEN** 任取一网格点绕过存档直接由哈密顿量对角化重算 `O_str`
- **THEN** 与存档派生值一致（容差 `1e-8`）

### Requirement: AFM 结构因子计算

系统 SHALL 按 `doc/model/operator.md` 从存档基态计算 `S(π)=(1/L)Σ_{i,j}(-1)^{i-j}⟨Z_i Z_j⟩`（`L=8`，`1/4` 归一从略）；输出 SHALL 为非负实数。

#### Scenario: 非负可审计

- **WHEN** 检查任一输出点
- **THEN** 值为非负实数，能追溯到存档基态行与 `Z_i Z_j` 关联矩阵，且同一存档跑两次结果逐位一致

#### Scenario: 与直算交叉一致

- **WHEN** 任取一网格点绕过存档直接由哈密顿量对角化重算 `S(π)`
- **THEN** 与存档派生值一致（容差 `1e-8`）

### Requirement: 观测量归一化

系统 SHALL 在原始值之外输出归一值：`O_str_norm = -O_str`（取反，不取绝对值；拓扑端 `+1`、平庸端 `0`），`S_pi_norm = S(π)/8`（Néel 饱和为 `1`）；归一 SHALL 为原始值的精确线性函数，不得做绝对值/截断等非线性折叠。

#### Scenario: 拓扑端归一为一

- **WHEN** 取深拓扑端（如 `s=1, δ=0` 附近）的派生行
- **THEN** `O_str_norm` 接近 `+1`（容差 `0.05`，有限尺寸偏差内），深平庸端接近 `0`

#### Scenario: Néel 端归一为一

- **WHEN** 取深反铁磁区（如大 `δ` 处峰值行）的派生行
- **THEN** `S_pi_norm` 接近 `+1`（容差 `0.05`），且全场非负

#### Scenario: 线性无折叠

- **WHEN** 对比同行的原始列与归一列
- **THEN** `O_str_norm == -O_str`、`S_pi_norm == S_pi/8` 逐行精确成立（浮点舍入内）；若某行原始 `O_str` 为正，归一值必须为负（不得折叠隐藏符号）

### Requirement: 派生 CSV 契约

系统 SHALL 输出两个 UTF-8 CSV（`O_str` 与 `S_pi` 各一，表头含 `s,delta`、原始值列、归一值列（`O_str_norm`/`S_pi_norm`）与 `is_degenerate`，列名按文档声明），行数等于网格点数，行序与存档一致（`delta` 外层、`s` 内层）；原始值列保留以保审计链；缺列或行数不符时下游必须报可读错误。

#### Scenario: 行数与同序

- **WHEN** 以默认配置运行派生
- **THEN** 每个 CSV 行数为 `10000`，第 `k` 行 `(s,delta)` 与存档第 `k` 行一致

#### Scenario: 双列齐全

- **WHEN** 检查任一派生 CSV 表头与抽查行
- **THEN** 原始列与归一列同时存在且满足线性关系，缺任一列视为契约破坏

### Requirement: Q 组合量计算

系统 SHALL 从两个派生 CSV 的归一列按 `doc/model/operator.md` 计算 `Q = (1-2O_str_norm) - (4/3)(S_pi_norm-1/4)`，输出 UTF-8 CSV `Q_L8_OBC.csv`（表头 `s,delta,Q[,is_degenerate]`），行数等于网格点数且第 `k` 行 `(s,delta)` 与输入一致；计算 SHALL 为纯文件后处理，不得重跑求解或改写输入 CSV。

#### Scenario: 三锚点正确

- **WHEN** 取平庸端（如 `s=0`）、拓扑端（如 `s=1`）、AFM 峰区（如大 `δ` 处）的输出行
- **THEN** `Q` 分别接近 `+1`、`-1`、`0`（容差 `0.05`，有限尺寸与基线近似偏差内）

#### Scenario: 可复算

- **WHEN** 用归一列按公式独立重算任一行的 `Q`
- **THEN** 与 CSV 该行值一致（浮点舍入内）；同一输入跑两次逐位一致

### Requirement: S(q) 曲线计算

系统 SHALL 从基态存档取三行（平庸 `(s,δ)=(0,0)`、SPT `(1,0)`、AFM 取 `S(π)` 实测峰值所在格点），在 `q∈[0,2π]` 密采样（不少于 200 点）下按 `doc/model/operator.md` 的 Fourier 定义计算 `S(q)`（OBC 格点标号约定不变），输出曲线 CSV（三列曲线数据）与取点元数据 `Sq_points.csv`（`curve,s,delta` 三行，图例坐标来源）；计算 SHALL 为纯存档后处理，不得重跑求解。

#### Scenario: 形状符合预期

- **WHEN** 计算三条曲线并取 `q=0, π/2, π` 处的值
- **THEN** 平庸线为 `(0, 1, 2)`（即 `1-cos q`，容差 `1e-8`）、SPT 线近乎重合（峰值 `≈2`，容差 `0.05`）、AFM 线在 π 处为 `≈8` 而其余处接近 `0`（容差 `0.05`）

#### Scenario: 可复算

- **WHEN** 用存档同行独立重算任一 `q` 点
- **THEN** 结果一致（浮点舍入内）；同一存档跑两次逐位一致

### Requirement: task2 派生复用

系统 SHALL 对 task2 基态存档复用既有 derive 定义（`O_str`、`S(π)`、归一化、`Q` 公式与 CSV schema 不变，文件名不变、落盘于 task2 专属目录）：`tilde_ZR` CSV 改为 task2 存档派生，`O_str`/`S_pi`/`Q` CSV 链路同 task1；`Ostr`/`Spi` 的 CSV SHALL 输出（`Q` 依赖其归一列），但不为其画热力图；`S(q)` 曲线 SHALL 跳过。

#### Scenario: 链路同构

- **WHEN** 以默认配置运行 task2 derive 全链
- **THEN** 产出 `tilde_ZR`、`Ostr`、`Spi`、`Q` 四个 CSV（各 `10000` 行，行序与 task2 存档一致），无 `S(q)` 产物

### Requirement: task1/task2 一致性验证

系统 SHALL 逐行对比 task1 与 task2 的四个 CSV（`tilde_ZR`、`O_str_norm`、`S_pi_norm`、`Q` 列）：一致 SHALL 定义为差值绝对值 `≤ 1e-8`；验证 SHALL 输出 pass/fail 结论与差异行清单（`s,delta,列,两值`）；`energies` 差 −1 为预期、不参与 fail 判定；`is_degenerate` 翻转的行 SHALL 单独列出、不判失败（P 劈裂简并子空间为预期内效应）。

#### Scenario: 不变即通过

- **WHEN** 四个对比列全部逐行一致且无能量异常行
- **THEN** 结论为通过，对称性预期成立

#### Scenario: 差异如实记录

- **WHEN** 任一对比列出现超容差行，或能量差偏离 −1
- **THEN** 结论为不通过并列出全部差异行（含坐标与两值），差异本身记为结论（P 选择效应的实证），不得静默截断或放宽容差
