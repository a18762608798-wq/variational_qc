# Spec Delta

## ADDED Requirements

### Requirement: Q 组合量计算

系统 SHALL 从两个派生 CSV 的归一列按 `doc/model/operator.md` 计算 `Q = (1-2O_str_norm) - (4/3)(S_pi_norm-1/4)`，输出 UTF-8 CSV `Q_L8_OBC.csv`（表头 `s,delta,Q[,is_degenerate]`），行数等于网格点数且第 `k` 行 `(s,delta)` 与输入一致；计算 SHALL 为纯文件后处理，不得重跑求解或改写输入 CSV。

#### Scenario: 三锚点正确

- **WHEN** 取平庸端（如 `s=0`）、拓扑端（如 `s=1`）、AFM 峰区（如大 `δ` 处）的输出行
- **THEN** `Q` 分别接近 `+1`、`-1`、`0`（容差 `0.05`，有限尺寸与基线近似偏差内）

#### Scenario: 可复算

- **WHEN** 用归一列按公式独立重算任一行的 `Q`
- **THEN** 与 CSV 该行值一致（浮点舍入内）；同一输入跑两次逐位一致
