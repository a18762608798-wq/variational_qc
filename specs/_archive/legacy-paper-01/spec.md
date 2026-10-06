# Feature: paper-01 模型引入和基本性质

> 本 spec 分为两部分：
>
> - **Part I — Paper Description**：说明主张、证据、上游输入与缺件，面向作者阅读。
> - **Part II — Specification Contract**：定义章节、图位、主张绑定、缺件与引用需求，作为可检查的规范性约束。
>
> 两部分必须一致；若存在冲突，应先澄清并修正 spec。

## Part I — Paper Description

### 1. Objective

写出 PRA 论文的模型引入部分与有限尺寸基本性质：
默认 `L=8` 下介绍 SSH 哈密顿量，给出归一化拓扑反映量 `~Z_R` 相图，
并在附录中用对称性能隙说明有限尺寸效应对相图的偏差影响。

目标 venue：PRA（regular article）。读者读完应相信：模型定义清楚，
`L=8` 相图可区分三相，附录能隙分析支撑有限尺寸偏差可控。

不要在这里写 LaTeX 实现或验收细节。

### 2. Upstream Inputs

- 实验定义：`specs/exp01/spec.md`（`S01` 网格基态 → D01 `~Z_R` 网格 + D05 标记；
  本 feature 只用 D01 裸图，D05 标记归 paper-03）、
  `specs/exp03/spec.md`（自含 `L=8,12,16` 对称性能隙 → D02a/b/c）。
- 共享输出：`S01`（`L=8` 参数网格基态，`256` 分量，基矢约定见 S01 manifest）。
- 数据产物：D01（`~Z_R[99,99]` + 无标记相图裸图 `figs/exp01/exp01_D01.pdf/png`）、
  D02a（`δ=0` 能隙曲线 `figs/exp03/exp03_D02a.pdf/png`）、
  D02b（`s` vs `A` 交点 `figs/exp03/exp03_D02b.pdf/png`）、
  D02c（`Δ` vs `1/L` 拟合 `figs/exp03/exp03_D02c.pdf/png`）。
- 理论文档：`docs/theory/H.md`（SSH 模型）、`docs/theory/gap.md`（对称性能隙）、
  `docs/theory/topological_op.md`（`~Z_R` 定义）。
- 论文大纲：`docs/paper-outline.md`“模型的引入和基本性质”节（含附录三项）。

### 3. Claims & Evidence

- `CLM-001`：SSH 模型哈密顿量定义如 `H.md`，默认 `L=8` ← `docs/theory/H.md`
- `CLM-002`：`~Z_R` 相图（`s∈[0,1]`、`δ∈[0,2]`）区分 trivial / topo / AFM 三相 ← D01（`figs/exp01/exp01_D01.pdf`）
- `CLM-003`：`L→∞` 时 `s` vs `A` 交点趋于 `s=0.5` ← D02b（marker 交点）
- `CLM-004`：`s=0.5` 处能隙随 `1/L` 线性拟合（`L=20,24`）截距小（`b=0.05`，以图为准），
  与能隙缩小趋势一致（原“截距为 0”按 D02c 图面修正，不改图）；
  说明能隙缩小效应 ← D02c（拟合系数标于图）
- `CLM-005`：有限尺寸只对相边界有一点影响，不影响相大体结构，论述见附录 ← D02a/b/c（既定结果，非推测）

### 4. Sections

- `SEC-001` 模型引入（正文，H 定义 + `~Z_R` 引入）
- `SEC-002` 有限尺寸相图（正文，D01 图 + 三相说明）
- `SEC-003` 有限尺寸能隙说明（附录，D02a/b/c 三图 + 偏差论述）

### 5. Gaps（缺件表）

- 无缺件：D01、D02a/b/c 图与数据均已落定（`figs/exp01`、`figs/exp03`、`data/`）；
  有限尺寸偏差表述为既定结果，不记 GAP。
- 真正缺数据的 exp05（D07 图未出）、exp06（D08 图未出）归后续
  paper feature（比特选择 / 实验结果），届时再记 `GAP-DATA` + 问用户要解释推测。

### 6. Citation Needs（按需）

- `CIT-001`：SSH 模型原始文献（模型引入处）
- `CIT-002`：拓扑反映量 / 相关拓扑标记方向文献（`~Z_R` 引入处）
- `CIT-003`：有限尺寸标度方向文献（附录拟合处，按需）

### 7. Open Questions

（`OQ-001` 已解决：D01 用单栏，见 `FIG-001`。）

---

## Part II — Specification Contract

本部分只记录具有规范性、可检查意义的约束。每条独立约束使用稳定 ID。

### A. Boundary

#### In Scope

- `BND-001` 模型引入正文（H 定义 + 默认 `L=8` 说明）
- `BND-002` D01 裸图正文呈现 + 三相说明
- `BND-003` 附录 D02a/b/c 三图 + 有限尺寸偏差论述

#### Out of Scope

- `BND-004` D05 起点终点标记与演化箭头（归 paper-03）
- `BND-005` 作图本身（已由上游完成，不管）

#### Dependencies

- `DEP-001` 上游 `specs/exp01`（S01/D01 定义与数据）
- `DEP-002` 上游 `specs/exp03`（D02a/b/c 定义与数据）
- `DEP-003` `docs/paper-outline.md`“模型的引入和基本性质”节
- `DEP-004` `docs/theory/H.md`、`gap.md`、`topological_op.md`

### B. Sections

- `SEC-001`（模型引入）：输入 `H.md` + `topological_op.md` → 输出正文段落（含 H 公式、`L=8` 默认声明、`~Z_R` 定义引用）
- `SEC-002`（有限尺寸相图）：输入 D01 + `FIG-001` → 输出正文段落（三相说明，`s∈[0,1]`、`δ∈[0,2]` 范围声明）
- `SEC-003`（附录能隙）：输入 D02a/b/c + `FIG-002/003/004` → 输出附录段落（交点 `s=0.5`、小拟合截距 `b=0.05`、偏差论述）

### C. Figures

- `FIG-001`：`figs/exp01/exp01_D01.pdf` → 正文单栏 `figure`（user 2026-10-05 定），caption 含坐标范围与三相标识说明
- `FIG-002`：`figs/exp03/exp03_D02a.pdf` → 附录，`δ=0` 三 `L` 能隙曲线
- `FIG-003`：`figs/exp03/exp03_D02b.pdf` → 附录，交点 marker 与 `s=0.5` 说明
- `FIG-004`：`figs/exp03/exp03_D02c.pdf` → 附录，`L=20,24` 拟合线 + 系数标记

### D. Claim Binding

- `CLM-001` ← evidence [`docs/theory/H.md`]
- `CLM-002` ← evidence [`figs/exp01/exp01_D01.pdf`, D01 数据集]
- `CLM-003` ← evidence [`figs/exp03/exp03_D02b.pdf`]
- `CLM-004` ← evidence [`figs/exp03/exp03_D02c.pdf`]
- `CLM-005` ← evidence [D02a/b/c]

### E. Gaps

- 本 feature 无缺件。

### F. Citation Requirements

- `CIT-001` → 覆盖 `CLM-001` 的 SSH 原始文献：经 `paper-zotero-hunter` verify
- `CIT-002` → 覆盖 `CLM-002` 的拓扑标记方向：经 verify
- `CIT-003` → 覆盖 `CLM-004` 的有限尺寸标度方向（按需）：经 verify
- 未验证引用不得合稿

### G. Acceptance

- `VAL-001` → verifies [`SEC-001`, `SEC-002`, `SEC-003`]：三节齐套，公式与符号一致
- `VAL-002` → verifies [`FIG-001`..`FIG-004`]：图文件存在且 caption 与数据一致
- `VAL-003` → verifies [`CLM-001`..`CLM-005`]：每条主张有证据或标记，无陈述句级无据主张
- `VAL-004` → verifies [`CIT-001`, `CIT-002`]：引用已读确认且 key 齐全（`CIT-003` 按需）
- `VAL-005` → verifies [compile]：`docs/paper/` 编译通过，无未定义引用
