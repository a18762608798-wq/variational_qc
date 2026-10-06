# Feature: paper-03 变分电路介绍

> 本 spec 分为两部分：
>
> - **Part I — Paper Description**：说明主张、证据、上游输入与缺件，面向作者阅读。
> - **Part II — Specification Contract**：定义章节、图位、主张绑定、缺件与引用需求，作为可检查的规范性约束。
>
> 两部分必须一致；若存在冲突，应先澄清并修正 spec。

## Part I — Paper Description

### 1. Objective

写出变分电路介绍节：在 `~Z_R` 相图上标出各相演化起点与一个示范终点
（同相、相深处）并绘制示意图；说明变分电路结构（初态 + 拟设结构），
分三相各绘一个示意图（初态 + 所需拟设电路）。

目标 venue：PRA（regular article）。读者读完应相信：起点终点配对合理
（同相、终点在相深处），三相拟设结构清楚，可直接对应后文真机实验。

不要在这里写 LaTeX 实现或验收细节。

### 2. Upstream Inputs

- 实验定义：`specs/exp01/spec.md`（D05：D01 底图 + 三对标记与配对箭头；
  配对与坐标见 `PRE-004`）、`specs/exp04/spec.md`（D06a–c：三分相拟设示意图）。
- 数据产物：D05（`figs/exp01/exp01_D05.pdf`）、D06a/b/c
 （`figs/exp04/exp04_D06{a,b,c}.pdf`，纯示意、无数据依赖）。
- 理论文档：`docs/theory/psi0.md`（三相初态）、`docs/theory/ansatz.md`
  （orbit 拟设结构）。
- 论文大纲：`docs/paper-outline.md`“变分电路介绍”节。
- 已有正文：`docs/paper/main.tex`（paper-01/02 内容，本节在其后）。

### 3. Claims & Evidence

- `CLM-001`：三对起点/终点（平庸 `(0.01,0.02)→(0.21,0.42)`、
  拓扑 `(0.99,0.02)→(0.90,0.20)`、AFM `(0.50,1.98)→(0.61,1.44)`），
  每对同相、终点在相深处，配对固定 ← D05 + exp01 `PRE-004`
- `CLM-002`：变分电路 = 初态 + orbit 拟设（镜面对映键共享转角）← D06 + `ansatz.md`
- `CLM-003`：三相初态（奇键单态乘积等）均在 `P=-2` 扇区 ← `psi0.md`

### 4. Sections

- `SEC-001` 示意起点终点（`06-ansatz.tex` 内 subsection，D05 图 + 配对说明；终点定位为经典参考目标/示范终点，非真实演化终点）
- `SEC-002` 变分电路结构（正文，D06a–c 三示意图 + orbit 规则说明）

### 5. Gaps（缺件表）

- 无缺件：D05、D06a–c 图均已落定；初态与拟设理论文档齐全。

### 6. Citation Needs（按需）

- `CIT-001`：VQE 原始文献（变分电路引入处，新 hunt）
- `CIT-002`：对称性保持拟设 / orbit 结构相关方向（按需）

### 7. Open Questions

（`OQ-001` 已关闭：横排/合一方案试过废弃，现定三独立单栏散放共享 FIG.5，见 `FIG-002`。）

---

## Part II — Specification Contract

本部分只记录具有规范性、可检查意义的约束。每条独立约束使用稳定 ID。

### A. Boundary

#### In Scope

- `BND-001` D05 示意图正文呈现 + 配对说明
- `BND-002` D06a–c 三示意图正文呈现 + orbit 规则说明

#### Out of Scope

- `BND-003` 作图本身（上游已出，不管）
- `BND-004` 真机执行细节（归 paper-04/06）

#### Dependencies

- `DEP-001` 上游 `specs/exp01`（D05 定义、配对与坐标）
- `DEP-002` 上游 `specs/exp04`（D06a–c 定义）
- `DEP-003` `docs/paper-outline.md`“变分电路介绍”节
- `DEP-004` `docs/theory/psi0.md`、`ansatz.md`
- `DEP-005` paper-01/02 正文（模型与物理量定义已落定）

### B. Sections

- `SEC-001`（示意起点终点）：输入 D05 + `FIG-001` → 输出 `06-ansatz.tex` 内 subsection 段落（配对坐标与同相说明，终点示范定位）
- `SEC-002`（变分电路结构）：输入 D06a–c + `FIG-002` → 输出正文段落（初态 + orbit 规则）

### C. Figures

- `FIG-001`：`figs/exp01/exp01_D05.pdf` → 正文，标记与箭头说明进 caption
- `FIG-002`：`figs/exp04/exp04_D06{a,b,c}.pdf` → 三个独立单栏 `figure` 散放（原图不重画），共享 FIG.5 编号（后两图前 `\addtocounter{figure}{-1}`），图例 (a) 详写 $U^{(k)}$、$\theta^{(k)}_j/\phi^{(k)}_j$、tying 规则，(b)(c) 从简；横排/合一方案已试，废弃

### D. Claim Binding

- `CLM-001` ← evidence [`figs/exp01/exp01_D05.pdf`, exp01 `PRE-004`]
- `CLM-002` ← evidence [`figs/exp04/exp04_D06{a,b,c}.pdf`, `ansatz.md`]
- `CLM-003` ← evidence [`docs/theory/psi0.md`]

### E. Gaps

- 本 feature 无缺件。

### F. Citation Requirements

- `CIT-001` → 覆盖 `CLM-002` 的 VQE 原始文献：新 hunt + verify
- `CIT-002` → orbit/对称拟设方向（按需）：hunt + verify
- 未验证引用不得合稿

### G. Acceptance

- `VAL-001` → verifies [`SEC-001`, `SEC-002`]：两节齐套，与已有模型/物理量定义一致
- `VAL-002` → verifies [`FIG-001`, `FIG-002`]：图文件存在，配对与示意图说明准确
- `VAL-003` → verifies [`CLM-001`..`CLM-003`]：每条主张有证据，无陈述句级无据主张
- `VAL-004` → verifies [`CIT-001`]：引用已读确认且 key 齐全（`CIT-002` 按需）
- `VAL-005` → verifies [compile]：中英双版编译通过，无未定义引用
