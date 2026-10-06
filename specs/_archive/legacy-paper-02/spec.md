# Feature: paper-02 引入反映拓扑性质的物理量

> 本 spec 分为两部分：
>
> - **Part I — Paper Description**：说明主张、证据、上游输入与缺件，面向作者阅读。
> - **Part II — Specification Contract**：定义章节、图位、主张绑定、缺件与引用需求，作为可检查的规范性约束。
>
> 两部分必须一致；若存在冲突，应先澄清并修正 spec。

## Part I — Paper Description

### 1. Objective

写出拓扑物理量引入节：以三相代表点的 `S(q)` 曲线说明为何用 `S(π)`
标记 AFM 相；以四联热力图（`S(π)` / string / `Q` / `~Z_R`）展示各量
对三相的分辨能力，并明确重点：`~Z_R` 不易在真机上测量，
后续重点关注态制备，以及用 D04a、D04b 刻画态的拓扑信息。

目标 venue：PRA（regular article）。读者读完应相信：`S(π)` 是合格的
AFM 标签，string 算符分辨 SPT，四联图互相印证且与 D01 相图一致。

不要在这里写 LaTeX 实现或验收细节。

### 2. Upstream Inputs

- 实验定义：`specs/exp02/spec.md`（S01/S02 基态轻采样 → D03 三线同图 + D04 四联热力图；
  D04(d) 与 D01 独立重算，见 exp02 `BND-004`）。
- 共享输出：`S01`（`L=8` 网格基态）、`S02`（三相代表点基态）。
- 数据产物：D03（q 网格 + 三代表点 `S(q)` 曲线，`figs/exp02/exp02_D03.pdf`）、
  D04（四联数据各 `99×99` + `figs/exp02/exp02_D04{a,b,c,d}.pdf`）。
- 理论文档：`docs/theory/topological_op.md`（`S(q)`、`O_str`、`Q`、`~Z_R` 定义）。
- 论文大纲：`docs/paper-outline.md`“引入反映拓扑性质的物理量”节。
- 已有正文：`docs/paper/main.tex`（paper-01 的模型与 `~Z_R` 定义，本节在其后）。

### 3. Claims & Evidence

- `CLM-001`：`S(π)` 可作为 AFM 相标签（三代表点 `S(q)` 曲线为证）← D03
- `CLM-002`：string 算符分辨 SPT 相 ← D04b
- `CLM-003`：`Q`（D04a、D04b 线性组合）为 ZR-like 算符 ← D04c + `topological_op.md`
- `CLM-004`：归一化 `~Z_R` 四联图与 D01 相图一致 ← D04d（与 D01 独立重算，可互验）
- `CLM-005`：`~Z_R` 不易真机测量，后续重点是态制备 + D04a/D04b 拓扑刻画 ← 大纲既定表述（方法论定位，非数据结论）

### 4. Sections

- `SEC-001` 结构因子与 AFM 标签（正文，D03 三线同图 + `S(π)` 说明）
- `SEC-002` 四联拓扑热力图（正文，D04a–d + 重点表述）

### 5. Gaps（缺件表）

- 无 `GAP-DATA`：D03、D04 数据与图均已落定（`figs/exp02`、`data/exp02`）。
- 无 `GAP-INTERP`：`CLM-005` 重点表述为大纲既定方法论定位，按原文写，不记推测。

### 6. Citation Needs（按需）

- `CIT-001`：string 序参量原始文献（den Nijs–Rommelse 1989，user 2026-10-05 定方向；
  已 hunt 入库双归档，全文已精读 string 序参量定义处，`bib:dennijs1989preroughening` 待写节时落位）
- `CIT-002`：MBTI/反射不变量方向（`~Z_R` 四联处；Elben 2020 已在库已精读，可复用，需归档到论文目录）
- `CIT-003`：SSH 扩展模型方向（`eSSH` 背景，按需）

### 7. Open Questions（按需）

- `OQ-001 [non-blocking]` 已关闭：reprint 双栏下 D04 进跨栏 `figure*`（minipage 拼装）；D03 单栏（拥挤则转跨栏，暂不需）。

---

## Part II — Specification Contract

本部分只记录具有规范性、可检查意义的约束。每条独立约束使用稳定 ID。

### A. Boundary

#### In Scope

- `BND-001` D03 三线同图正文呈现 + `S(π)` AFM 标签论述
- `BND-002` D04 四联热力图正文呈现（LaTeX 端拼 `2×2`，minipage 手工 (a)–(d) 编号；原 subfigure 方案因 reprint 双栏出队堵塞废弃，见 R5）+ 重点表述

#### Out of Scope

- `BND-003` 作图本身（上游已出四个独立文件，不管）
- `BND-004` 真机测量方案（归 paper-04/06）

#### Dependencies

- `DEP-001` 上游 `specs/exp02`（S01/S02/D03/D04 定义与数据）
- `DEP-002` `docs/paper-outline.md`“引入反映拓扑性质的物理量”节
- `DEP-003` `docs/theory/topological_op.md`
- `DEP-004` paper-01 正文（模型与 `~Z_R` 定义已落定，`docs/paper/main.tex`）

### B. Sections

- `SEC-001`（结构因子与 AFM 标签）：输入 D03 + `FIG-001` → 输出正文段落
- `SEC-002`（四联热力图）：输入 D04a–d + `FIG-002` → 输出正文段落（含重点表述原文落位）

### C. Figures

- `FIG-001`：`figs/exp02/exp02_D03.pdf` → 正文，三线同图
- `FIG-002`：`figs/exp02/exp02_D04{a,b,c,d}.pdf` → 跨栏 `figure*` 拼 `2×2`（minipage 手工编号；subfigure 废弃，见 R5）

### D. Claim Binding

- `CLM-001` ← evidence [`figs/exp02/exp02_D03.pdf`, D03 数据集]
- `CLM-002` ← evidence [`figs/exp02/exp02_D04b.pdf`]
- `CLM-003` ← evidence [`figs/exp02/exp02_D04c.pdf`, `topological_op.md`]
- `CLM-004` ← evidence [`figs/exp02/exp02_D04d.pdf`（与 D01 独立重算互验）]
- `CLM-005` ← evidence [大纲既定表述（方法论定位）]

### E. Gaps

- 本 feature 无缺件。

### F. Citation Requirements

- `CIT-001` → 覆盖 `CLM-002` 的 string 序参量原始文献：新 hunt + verify
- `CIT-002` → 覆盖 `CLM-004` 的 MBTI 方向：复用 Elben 2020（已精读，需确认已归档论文目录）
- `CIT-003` → `eSSH` 背景（按需）：hunt + verify
- 未验证引用不得合稿

### G. Acceptance

- `VAL-001` → verifies [`SEC-001`, `SEC-002`]：两节齐套，与 paper-01 模型定义一致
- `VAL-002` → verifies [`FIG-001`, `FIG-002`]：图文件存在，`2×2` 拼装标签 (a)–(d) 与正文引用一致
- `VAL-003` → verifies [`CLM-001`..`CLM-005`]：每条主张有证据，无陈述句级无据主张
- `VAL-004` → verifies [`CIT-001`, `CIT-002`]：引用已读确认且 key 齐全（`CIT-003` 按需）
- `VAL-005` → verifies [compile]：中英双版编译通过，无未定义引用
