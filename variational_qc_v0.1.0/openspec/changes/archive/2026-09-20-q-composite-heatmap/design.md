# Design

## Context

- 现状：`Ostr_L8_OBC.csv` 与 `Spi_L8_OBC.csv` 均有归一列且与存档同序；`Q` 公式已锁在 `doc/model/operator.md`。见 `proposal.md` 动机。

## Goals / Non-Goals

**Goals:**

- `Q` 输出与输入逐行可审计；第四张图与 ZR 图同配置可直接对照。

**Non-Goals:**

- 不动存档、求解、既有派生与三张图；不引入新依赖。

## Decisions

### 1. Q 从 CSV 归一列算，不从存档算

Python 脚本 join 两个 CSV（按 `(s,delta)` 对齐断言）后逐行套公式。理由：`Q` 定义的输入就是归一列，从 CSV 算使"公式输入"与"落盘审计值"同一份，避免存档→归一重算引入第二份舍入；秒级；Python 生态与绘图侧一致。替代方案（Julia 读存档直算 Q）被否决：多一次大文件读取且舍入链条分叉，收益为零。

### 2. Q 自立新 CSV，不并入既有文件

`Q_L8_OBC.csv`（`s,delta,Q[,is_degenerate]`）独立成文件：`Q` 不是观测量而是组合显示量，与原始/归一观测量语义不同；三元组契约使既有绘图脚本零改动复用（`--value-col Q`）。

### 3. 配色与 ZR 图完全同参

RdBu 发散、中心 0、范围 [-1,1]、-1/0/+1 刻度——同语言才能逐像素对照；标题沿用去边界条件规则。

## Risks / Trade-offs

- [Risk] 两输入 CSV 行数/行序错位 → Mitigation：join 前断言 `(s,delta)` 逐行相等，否则非零退出。
- [Trade-off] Q 超出 [-1,1]（过渡区平面插值可能微超）→ 色标 clip 到范围并在任务验收中记录实测极值；不放宽色标（同语言优先）。

## Migration Plan

- 纯新增，无迁移、无回滚需求（删文件即回滚）。

## Open Questions

- 无。
