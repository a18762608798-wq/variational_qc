# Spec Delta

## Purpose

从基态存档派生互补序参量，为相图提供拓扑/磁性双重证据：string operator 标记 SPT 区，AFM 结构因子标定反铁磁区；两者只读存档、不重复对角化。

## ADDED Requirements

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

### Requirement: 派生 CSV 契约

系统 SHALL 输出两个 UTF-8 CSV（`O_str` 与 `S_pi` 各一，表头至少 `s,delta,value[,is_degenerate]` 列名按文档声明），行数等于网格点数，行序与存档一致（`delta` 外层、`s` 内层）；缺列或行数不符时下游必须报可读错误。

#### Scenario: 行数与同序

- **WHEN** 以默认配置运行派生
- **THEN** 每个 CSV 行数为 `10000`，第 `k` 行 `(s,delta)` 与存档第 `k` 行一致
