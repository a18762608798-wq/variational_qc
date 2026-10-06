# Feature: paper-03 Closing

> 本 spec 分为两部分：
>
> - **Part I — Paper Description**：说明主张、证据、上游输入与缺件，面向作者阅读。
> - **Part II — Specification Contract**：定义章节、图位、主张绑定、缺件与引用需求，作为可检查的规范性约束。
>
> 两部分必须一致；若存在冲突，应先澄清并修正 spec。

## Part I — Paper Description

### 1. Objective

写出论文的 Closing 部分：重写摘要（覆盖全篇）、新增结论节、把 Related Work 对比并入引言、全篇术语符号统一。结论只复述已建立结果，不引入新主张。Related Work 既覆盖真机拓扑与变分算法，也补充与本文直接对应的方法和理论背景：结构因子 S(q)、string 信号及其长程关联、稳定子与读出驱动的真机优质比特选择、读出误差缓解、有限尺寸能隙与外推。

目标 venue：PRA（regular article）。读者读完摘要结论应对全文工作有完整印象；引言 Related Work 段应讲清本工作相对两方向文献的定位。

不要在这里写 LaTeX 实现或验收细节。

### 2. Upstream Inputs

- paper-01 Methods 正文（模型、诊断量、态制备、硬件方法已落定）。
- paper-02 Results and Discussion 正文（协议先行；D07/D08 结论冻结，Closing 不预支冻结结论）。
- 用户已定 Related Work 定位（真机拓扑 + 变分算法双方向，并补充五类直接对口理论/方法方向）。
- R3 已验证对比文献及本轮补猎文献（全部按 DOI/全文或条目核验并入 Zotero；本 feature 只复用已核验条目，不再扩大方向）。
- 论文大纲：`docs/paper-outline.md` 全文。
- 已有正文：`docs/paper/main.tex` + `main-zh.tex`（含引言、结论占位、摘要草稿）。

### 3. Claims & Evidence

- `CLM-001`：摘要覆盖全篇工作（模型、物理量、变分电路、真机方法、结果框架）← paper-01/02 正文；结果部分只写框架与协议，不写冻结的具体排名/趋势。
- `CLM-002`：结论复述已建立结果，不引入新主张 ← 同上（只复述）。
- `CLM-003`：Related Work 对比定位覆盖两层：真机拓扑与变分算法的总体谱系，以及与本文直接相关的五类方法/理论背景（结构因子、string 长程关联、稳定子/读出优质比特选择、读出误差缓解、有限尺寸能隙与外推）← 用户已定口径 + R3 与本轮已核验文献。

### 4. Sections

- `SEC-001` 摘要重写（中英双版）。
- `SEC-002` 结论节（新增，中英双版；冻结结论未预支，D07/D08numbers 不写）。
- `SEC-003` Related Work 并入引言（含对比文献定位段）。
- `SEC-004` 全篇统稿（术语、符号、时态、交叉引用）。

### 5. Gaps（缺件表）

- 无本 feature 缺件：D07/D08 跟踪中缺件属于 paper-02 Follow-up，Closing 保持框架表述原样，不预支。
- 若 Results 图到后结论变化，摘要结论随 paper-02 返工同步更新，不在本 feature 提前写。

### 6. Citation Needs（按需）

- `CIT-001`：真机拓扑与变分算法对比文献——复用 R3 已验证条目。
- `CIT-002`：结构因子与 string 长程关联文献——复用已核验条目。
- `CIT-003`：稳定子/读出驱动的真机优质比特选择文献——复用已核验条目。
- `CIT-004`：读出误差缓解文献——复用已核验条目。
- `CIT-005`：有限尺寸能隙与外推文献——复用已核验条目。
- `CIT-006`：结论引用的已有结果——复用已验证引用，不新增 hunt。
- 未验证引用不得合稿。

### 7. Open Questions

- 无阻塞问题。Related Work 的七个具体文献方向、引言五步结构、摘要 moves 均已确定；写作时不得把方法背景文献改写成本文已获得的实验结果。

---

## Part II — Specification Contract

本部分只记录具有规范性、可检查意义的约束。每条独立约束使用稳定 ID。

### A. Boundary

#### In Scope

- `BND-001` 摘要重写、结论新增、Related Work 并入引言、全文统稿。

#### Out of Scope

- `BND-002` 新主张、新数据、新图（统稿不产生内容）。
- `BND-003` D07/D08 缺件（归 paper-02 跟踪）；Methods/Results 正文修改（归各自 feature 返工）。

#### Dependencies

- `DEP-001` paper-01/02 主体收敛（当前 paper-01/02 均已收敛）。
- `DEP-002` 用户 Related Work 定位 + R3 与本轮已核验文献。
- `DEP-003` `docs/paper-outline.md` 全文。

### B. Sections

- `SEC-001`（摘要）：输入全篇正文 → 输出中英双版新摘要（结果只写框架）。
- `SEC-002`（结论）：输入各节结果 → 输出中英双版结论（只复述，不预支冻结结论）。
- `SEC-003`（Related Work 入引言）：输入用户定位 + `CIT-001`..`CIT-005` 文献 → 输出按七个具体文献方向组织的引言对比段落；背景文献只支持定位和方法背景，不替代本文结果证据。
- `SEC-004`（统稿）：输入全文 → 术语符号时态统一 + 交叉引用检查。

### C. Figures

- 无新增图位（只检查既有图编号与引用一致）。

### D. Claim Binding

- `CLM-001` ← evidence [paper-01/02 正文]
- `CLM-002` ← evidence [同上（只复述）]
- `CLM-003` ← evidence [用户定位 + R3 与本轮已核验文献]

### E. Gaps

- 本 feature 无缺件；D07/D08 缺件由 paper-02 跟踪，Closing 不预支其结论。

### F. Citation Requirements

- `CIT-001` → 覆盖 `CLM-003` 的真机拓扑与变分算法谱系：复用 R3 已验证条目。
- `CIT-002` → 覆盖结构因子与 string 长程关联背景：复用已核验条目。
- `CIT-003` → 覆盖稳定子/读出驱动的真机优质比特选择背景：复用已核验条目。
- `CIT-004` → 覆盖读出误差缓解背景：复用已核验条目。
- `CIT-005` → 覆盖有限尺寸能隙与外推背景：复用已核验条目。
- `CIT-006` → 复用结论所需的已验证引用：无需新增 hunt。
- 未验证引用不得合稿。

### G. Acceptance

- `VAL-001` → verifies [`SEC-001`..`SEC-004`]：四节齐套。
- `VAL-002` → verifies [`CLM-001`..`CLM-003`]：摘要结论有据，定位有用户口径+文献。
- `VAL-003` → verifies [`CIT-001`..`CIT-006`]：所有 Related Work 与结论引用均来自已核验条目，且引用用途与主张方向匹配。
- `VAL-004` → verifies [compile]：中英双版编译通过，无未定义引用。
