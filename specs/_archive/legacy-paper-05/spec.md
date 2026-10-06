# Feature: paper-05 真机读出误差缓解介绍

> 本 spec 分为两部分：
>
> - **Part I — Paper Description**：说明主张、证据、上游输入与缺件，面向作者阅读。
> - **Part II — Specification Contract**：定义章节、图位、主张绑定、缺件与引用需求，作为可检查的规范性约束。
>
> 两部分必须一致；若存在冲突，应先澄清并修正 spec。

## Part I — Paper Description

### 1. Objective

写出真机读出误差缓解方法节：逐比特标定 `2×2` 概率分配矩阵并求逆矫正
测量分布，加非负约束后再算观测量（各比特独立假设，每比特 2 个标定电路，
代价随比特数线性；分批标定防漂移）。

目标 venue：PRA（regular article）。读者读完应相信：缓解流程透明可复现，
后文 D08 真机数据点均经过此流程处理。

不要在这里写 LaTeX 实现或验收细节。

### 2. Upstream Inputs

- 实验定义：`specs/exp06/spec.md`（S05 自含：`PRE-006` 逐比特标定、
  `POST-004` 随 D08 存档；quark 平台自带矫正关闭）。
- 数据产物：无（纯方法节，无 `D` 图）。
- 理论文档：`docs/theory/readout_mitigation.md`（分配矩阵定义、求逆矫正、非负约束）。
- 论文大纲：`docs/paper-outline.md`“真机读出误差缓解介绍”节。
- 已有正文：`docs/paper/main.tex`（paper-01~04 内容，本节在其后）。

### 3. Claims & Evidence

- `CLM-001`：读出误差模型 `P_meas = M P_ideal`，`M` 列由制备标定 ← `readout_mitigation.md`
- `CLM-002`：矫正流程（求逆 + 非负截零重归一后再算观测量，各比特独立）← 同上 + exp06 `PRE-006`
- `CLM-003`：标定代价每比特 2 电路、随比特数线性，分批标定防漂移 ← 同上 + exp06 执行记录

### 4. Sections

- `SEC-001` 读出误差缓解（正文，矩阵定义 + 矫正流程 + 代价说明）

### 5. Gaps（缺件表）

- 无缺件：纯方法节，定义文档齐全。

### 6. Citation Needs（按需）

- `CIT-001`：读出误差缓解方法原始/常用文献（Bravyi 2021 张量积模型，已 hunt 入库双归档，全文已精读方法节，`bib:bravyi2021mitigating` 待写节时落位；`OQ-001` 关闭）

### 7. Open Questions

（`OQ-001` 已关闭：CIT-001 定 Bravyi 2021 hunt，已入库验证。）

---

## Part II — Specification Contract

本部分只记录具有规范性、可检查意义的约束。每条独立约束使用稳定 ID。

### A. Boundary

#### In Scope

- `BND-001` 读出缓解方法正文（矩阵、求逆、非负约束、代价）

#### Out of Scope

- `BND-002` 具体标定矩阵数值（随 D08 存档，不管）
- `BND-003` D08 结果呈现（归 paper-06）

#### Dependencies

- `DEP-001` 上游 `specs/exp06`（S05 定义与执行记录）
- `DEP-002` `docs/paper-outline.md`“真机读出误差缓解介绍”节
- `DEP-003` `docs/theory/readout_mitigation.md`

### B. Sections

- `SEC-001`（读出误差缓解）：输入理论文档 + exp06 定义 → 输出 `08-readout.tex` 内 subsection 段落（父节为 Hardware implementation）

### C. Figures

- 无（纯方法节，无图位）

### D. Claim Binding

- `CLM-001` ← evidence [`readout_mitigation.md`]
- `CLM-002` ← evidence [`readout_mitigation.md`, exp06 `PRE-006`]
- `CLM-003` ← evidence [`readout_mitigation.md`, exp06 执行记录]

### E. Gaps

- 本 feature 无缺件。

### F. Citation Requirements

- `CIT-001` → 覆盖方法常规性：`bravyi2021mitigating`（已 hunt + verify + bind）
- `CIT-002` → 缓解版图背景（R3 已验证落位，无新主张）：`temme2017error`（PEC 准概率）、
  `gupta2024probabilistic`（动态电路 PEC）、`mari2021extending`（NEPEC 统一）、
  `krebsbach2022optimization`（Richardson 优化）、`koenig2024inverted`（逆电路 ZNE）、
  `li2017efficient`（噪声放大主动抑制）、`schultz2022analyzing`（时间关联 caveat）、
  `nation2021scalable`（M3 无矩阵展开）；`kandala2019error` 仅硬件首证归属句（条目-only）
- 未验证引用不得合稿

### G. Acceptance

- `VAL-001` → verifies [`SEC-001`]：方法节齐套，与理论文档一致
- `VAL-002` → verifies [`CLM-001`..`CLM-003`]：每条主张有证据
- `VAL-003` → verifies [compile]：中英双版编译通过
- `VAL-004` → verifies [`CIT-001`]：Bravyi 2021 已读确认，key 齐全已 bind
