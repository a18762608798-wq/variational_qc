# Spec Delta

## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: 派生 CSV 契约

系统 SHALL 输出两个 UTF-8 CSV（`O_str` 与 `S_pi` 各一，表头含 `s,delta`、原始值列、归一值列（`O_str_norm`/`S_pi_norm`）与 `is_degenerate`，列名按文档声明），行数等于网格点数，行序与存档一致（`delta` 外层、`s` 内层）；原始值列保留以保审计链；缺列或行数不符时下游必须报可读错误。

#### Scenario: 行数与同序

- **WHEN** 以默认配置运行派生
- **THEN** 每个 CSV 行数为 `10000`，第 `k` 行 `(s,delta)` 与存档第 `k` 行一致

#### Scenario: 双列齐全

- **WHEN** 检查任一派生 CSV 表头与抽查行
- **THEN** 原始列与归一列同时存在且满足线性关系，缺任一列视为契约破坏
