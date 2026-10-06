# Feature: paper-07 收尾（摘要/结论/统稿）

> 本 spec 分为两部分：
>
> - **Part I — Paper Description**：说明主张、证据、上游输入与缺件，面向作者阅读。
> - **Part II — Specification Contract**：定义章节、图位、主张绑定、缺件与引用需求，作为可检查的规范性约束。
>
> 两部分必须一致；若存在冲突，应先澄清并修正 spec。

## Part I — Paper Description

### 1. Objective

收尾统稿：在 paper-01~06 全部收敛后，重写摘要（覆盖全篇）、新增结论节、
把 Related Work 对比并入引言、全篇术语符号统一。结论只复述已建立结果，
不引入新主张；Related Work 定位口径问用户。

目标 venue：PRA（regular article）。读者读完摘要结论应对全文工作有完整印象。

不要在这里写 LaTeX 实现或验收细节。

### 2. Upstream Inputs

- paper-01~06 全部收敛（spec/plan/tasks 一致，正文落定，缺件均为跟踪中外部 GAP）。
- 上游产物：已落定 `D##` 全体（D07/D08 图除外，仍跟踪中）。
- 论文大纲：`docs/paper-outline.md` 全文。
- 已有正文：`docs/paper/main.tex` + `main-zh.tex`（paper-01~06 内容）。

### 3. Claims & Evidence

- `CLM-001`：摘要覆盖全篇工作（模型、物理量、变分电路、真机方法、结果框架）← paper-01~06 正文
- `CLM-002`：结论复述已建立结果，不引入新主张 ← 同上
- `CLM-003`：Related Work 对比定位（真机拓扑工作 + 变分算法工作两方向，user 已定）← 已关闭 `GAP-001-INTERP` + R3 已验证对比文献（见 §5 清单）

### 4. Sections

- `SEC-001` 摘要重写（中英双版）
- `SEC-002` 结论节（新增，中英双版）
- `SEC-003` Related Work 并入引言（含对比文献）
- `SEC-004` 全篇统稿（术语、符号、时态、交叉引用）

### 5. Gaps（缺件表）

- ~~`GAP-001-INTERP [needs-user]`~~ 已关闭（R3 超额完成）：用户定位（真机拓扑 + 变分算法双方向）
  已落位引言相关工作段，对比文献 10+ 篇全部 hunt + verify + bind
 （`satzinger2021realizing`、`sun2023efficient`、`chen2011classification`、
  `schuch2011classifying`、`huang2020predicting`、`elben2022toolbox`、
  `cerezo2021variational`、`tilly2022variational`、`mcclean2018barren`、
  `temme2017error`、`kandala2019error`（条目-only）、`colless2018robust`、`yu2023simulating`）。
- D07/D08 跟踪中缺件不属于本 feature（由 paper-04/06 Follow-up 跟踪），统稿时保持空位原样。

### 6. Citation Needs（按需）

- `CIT-001`：Related Work 对比文献（定位定后 hunt，2–4 篇）
- `CIT-002`：结论引用的已有结果（复用已验证引用，不新增 hunt）

### 7. Open Questions

（`OQ-001` 已关闭：user 2026-10-05 定拆 `sections/*.tex`，一节一文件。）

---

## Part II — Specification Contract

本部分只记录具有规范性、可检查意义的约束。每条独立约束使用稳定 ID。

### A. Boundary

#### In Scope

- `BND-001` 摘要重写、结论新增、Related Work 并入引言、全文统稿

#### Out of Scope

- `BND-002` 新主张、新数据、新图（统稿不产生内容）
- `BND-003` D07/D08 缺件（归原 feature 跟踪）

#### Dependencies

- `DEP-001` paper-01~06 全部收敛
- `DEP-002` `docs/paper-outline.md` 全文

### B. Sections

- `SEC-001`（摘要）：输入全篇正文 → 输出中英双版新摘要
- `SEC-002`（结论）：输入各节结果 → 输出中英双版结论（只复述）
- `SEC-003`（Related Work 入引言）：输入用户定位 + `CIT-001` 文献 → 输出引言对比段落
- `SEC-004`（统稿）：输入全文 → 术语符号时态统一 + 交叉引用检查

### C. Figures

- 无新增图位（只检查既有图编号与引用一致）

### D. Claim Binding

- `CLM-001` ← evidence [paper-01~06 正文]
- `CLM-002` ← evidence [同上（只复述）]
- `CLM-003` ← evidence [`GAP-001-INTERP` 用户定位 + `CIT-001` 文献]

### E. Gaps

- ~~`GAP-001-INTERP [needs-user]`~~ 已关闭：用户定位（真机拓扑工作 + 变分算法工作）2026-10-05 已定；
  R3 hunt 双方向 10+ 篇代表作，全部 verify + bind 落位引言（见 §5 清单）。

### F. Citation Requirements

- `CIT-001` → 覆盖 `CLM-003` 的对比文献（2–4 篇）：hunt + verify
- `CIT-002` → 复用已验证引用：无需 hunt
- 未验证引用不得合稿

### G. Acceptance

- `VAL-001` → verifies [`SEC-001`..`SEC-004`]：四节齐套
- `VAL-002` → verifies [`CLM-001`..`CLM-003`]：摘要结论有据，定位有用户口径+文献
- `VAL-003` → verifies [`CIT-001`]：对比文献已读确认
- `VAL-004` → verifies [compile]：中英双版编译通过，全文交叉引用干净
