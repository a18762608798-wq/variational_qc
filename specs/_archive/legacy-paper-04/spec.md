# Feature: paper-04 真机优质比特选择方法介绍

> 本 spec 分为两部分：
>
> - **Part I — Paper Description**：说明主张、证据、上游输入与缺件，面向作者阅读。
> - **Part II — Specification Contract**：定义章节、图位、主张绑定、缺件与引用需求，作为可检查的规范性约束。
>
> 两部分必须一致；若存在冲突，应先澄清并修正 spec。

## Part I — Paper Description

### 1. Objective

写出真机优质比特选择方法节：介绍优质比特筛选（每条候选跑 4 个基准电路
测稳定子均值与读出保真度，按 score 排序；8 链与 10 环基准电路不同，
只各自内部比较），给出三张评分排名图（8 链前十、10 环前十、冠军环内
十条 8-子链），论文中一起呈现。

目标 venue：PRA（regular article）。读者读完应相信：筛选方法合理，
排名可复现，目标比特（S04）选得有据。

不要在这里写 LaTeX 实现或验收细节。

### 2. Upstream Inputs

- 实验定义：`specs/exp05/spec.md`（产出 D07a/b/c 排名 + S04 供 exp06 消费）。
- 数据产物：D07a/b/c 排名数据（`data/exp05/bill.json` + 候选 evidence，
  图文件**未出**）。
- 理论文档：`docs/theory/premium_qubits.md`（cluster 态、稳定子、评分方法）。
- 论文大纲：`docs/paper-outline.md`“真机优质比特选择方法介绍”节
  （打分公式 ${\rm score}=0.8\,\bar{S}+0.2\,F_{\rm ro}$，三图一起呈现）。
- 已有正文：`docs/paper/main.tex`（paper-01~03 内容，本节在其后）。

### 3. Claims & Evidence

- `CLM-001`：筛选方法（4 基准电路 + 稳定子均值/读出保真度 + 加权排序，
  8 链与 10 环各自内部比较）← `premium_qubits.md` + exp05 定义
- `CLM-002`：8 链评分排名前十（芯片为百花，user 2026-10-05 确认；具体比特表待图）← D07a（`GAP-001-DATA`：图未出，比特表冻结）
- `CLM-003`：10 环评分排名前十（芯片为百花，user 2026-10-05 确认；具体比特表待图）← D07b（`GAP-001-DATA`：图未出，比特表冻结）
- `CLM-004`：冠军环内十条 8-子链评分排名（百花冠军环，user 2026-10-05 确认；具体子链表待图）← D07c（`GAP-001-DATA`：图未出，子链表冻结）

### 4. Sections

- `SEC-001` 筛选方法（正文，cluster 态/稳定子/打分公式，可先行）
- `SEC-002` 三张排名图（正文，图位先留空，排名论述冻结）

### 5. Gaps（缺件表）

- `GAP-001-DATA [blocking]`：D07a/b/c 三张排名图未出（`figs/exp05/` 不存在）。
  `SEC-002` 留三个图空位；芯片为百花已由 user 确认可写，具体比特/子链表冻结待图。
  `SEC-001` 方法部分不受影响先行。

### 6. Citation Needs（按需）

- `CIT-001`：cluster 态原始文献（cluster 态引入处，新 hunt）
- `CIT-002`：读出保真度/基准测试方法方向（按需）

### 7. Open Questions（按需）

- 无（方法定义见 `premium_qubits.md` 与 exp05 spec，无歧义）。

---

## Part II — Specification Contract

本部分只记录具有规范性、可检查意义的约束。每条独立约束使用稳定 ID。

### A. Boundary

#### In Scope

- `BND-001` 筛选方法正文（cluster 态、稳定子、打分公式、8 链/10 环各自比较）
- `BND-002` 三张排名图图位 + 空位（图到后填）

#### Out of Scope

- `BND-003` 作图本身（exp05 侧出，不管）
- `BND-004` 真机执行与 S04 消费（归 paper-06）

#### Dependencies

- `DEP-001` 上游 `specs/exp05`（D07a/b/c 定义与排名数据）
- `DEP-002` `docs/paper-outline.md`“真机优质比特选择方法介绍”节
- `DEP-003` `docs/theory/premium_qubits.md`
- `DEP-004` paper-01~03 正文（变分电路定义已落定）

### B. Sections

- `SEC-001`（筛选方法）：输入 `premium_qubits.md` + exp05 定义 → 输出 `07-premium.tex` 内 subsection 段落（先行；父节为 Hardware implementation）
- `SEC-002`（排名图）：输入 D07a/b/c（待图）→ 输出图位空位 + 冻结论述（后填）

### C. Figures

- `FIG-001`：D07a 图（待 `figs/exp05/`）→ `[TODO(GAP-001): 待 D07a 图]`
- `FIG-002`：D07b 图（待）→ `[TODO(GAP-001): 待 D07b 图]`
- `FIG-003`：D07c 图（待）→ `[TODO(GAP-001): 待 D07c 图]`
- 三图论文中一起呈现（版式待图到后定）

### D. Claim Binding

- `CLM-001` ← evidence [`premium_qubits.md`, exp05 spec 定义]
- `CLM-002` ← evidence [D07a 数据，`GAP-001-DATA` 图待出，冻结]
- `CLM-003` ← evidence [D07b 数据，`GAP-001-DATA` 图待出，冻结]
- `CLM-004` ← evidence [D07c 数据，`GAP-001-DATA` 图待出，冻结]

### E. Gaps

- `GAP-001-DATA [blocking]`：D07a/b/c 图未出；`SEC-002` 留空位，`CLM-002/003/004` 冻结；
  `SEC-001` 先行不受影响

### F. Citation Requirements

- `CIT-001` → 覆盖 `CLM-001` 的 cluster 态原始文献：新 hunt + verify
- `CIT-002` → 基准测试方法方向（按需）
- 未验证引用不得合稿

### G. Acceptance

- `VAL-001` → verifies [`SEC-001`]：方法节齐套，与 `premium_qubits.md` 一致
- `VAL-002` → verifies [`FIG-001`..`FIG-003`]：空位标记存在（图到后填图）
- `VAL-003` → verifies [`CLM-001`]：方法主张有证据；`CLM-002/003/004` 保持冻结（无陈述句级无据主张）
- `VAL-004` → verifies [`CIT-001`]：引用已读确认且 key 齐全（`CIT-002` 按需）
- `VAL-005` → verifies [compile]：中英双版编译通过，无未定义引用
