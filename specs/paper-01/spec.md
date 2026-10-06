# Feature: paper-01 Methods

> 本 spec 是当前活动主线的 Methods feature。
> 旧 paper feature 已归档到 `specs/_archive/legacy-paper-01` 至 `legacy-paper-07`，本文件不依赖旧 spec 作为活动定义。
>
> 本 spec 分为两部分：
>
> - **Part I — Paper Description**：说明主张、证据、上游输入与缺件，面向作者阅读。
> - **Part II — Specification Contract**：定义章节、图位、主张绑定、缺件与引用需求，作为可检查的规范性约束。

## Part I — Paper Description

### 1. Objective

写出论文的 Methods 部分，建立从模型定义、拓扑物理量、变分态制备到真机实施方法的完整链条。参考“先说明方法、后集中报告结果”的论文组织方式：Methods 只说明机制、协议、定义和可复现实验流程，不在这里写具体排名或真机结论。内容包括：

- SSH 哈密顿量、默认 `L=8` 以及归一化拓扑反映量 `~Z_R`；
- 有限尺寸效应的处理口径；具体能隙曲线和拟合结果放入 Appendix；
- `S(q)`、string operator、`Q` 和 `~Z_R` 对三相的刻画及真机可测量量的选择；
- 三相变分电路的起点/终点示意、初态和 orbit 拟设结构；
- 真机优质比特筛选方法；D07 的具体排名结论放入 Results and Discussion；
- 读出误差缓解方法。

目标 venue：PRA regular article。读者读完应理解模型、相的诊断量、态制备方案和真机测量流程，并能据此理解后续 Results and Discussion 中的 D08 比较。D07 图缺失时，只冻结具体排名结论，不阻塞方法文字。

不要在这里写 LaTeX 实现或验收细节。

### 2. Upstream Inputs

- 实验定义：
  - `specs/exp01/spec.md`：S01/D01 相图与 D05 起点终点标记；
  - `specs/exp02/spec.md`：D03 `S(q)` 曲线与 D04a–d 四联热力图；
  - `specs/exp03/spec.md`：D02a–c 有限尺寸能隙分析；
  - `specs/exp04/spec.md`：D06a–c 三相拟设示意图；
  - `specs/exp05/spec.md`：D07a–c 优质比特排名与 S04 目标比特；
  - `specs/exp06/spec.md`：S05 读出标定/缓解流程，供 D08 消费。
- 共享输出：`S01`、`S02`，以及 exp05/exp06 中定义的执行记录。
- 数据产物：D01、D02a/b/c、D03、D04a/b/c/d、D05、D06a/b/c、D07a/b/c。
- 理论文档：`docs/theory/H.md`、`gap.md`、`topological_op.md`、`psi0.md`、`ansatz.md`、`premium_qubits.md`、`readout_mitigation.md`。
- 论文大纲：`docs/paper-outline.md` 中模型、拓扑物理量、变分电路、真机优质比特、读出误差缓解相关条目。

### 3. Claims & Evidence

- `CLM-001`：SSH 哈密顿量和默认 `L=8` 的模型定义明确 ← `docs/theory/H.md`。
- `CLM-002`：`~Z_R` 相图覆盖 `s∈[0,1]`、`δ∈[0,2]`，可区分 trivial / topo / AFM 三相 ← D01。
- `CLM-003`：有限尺寸效应的分析协议定义了相边界和能隙缩放的检查方法；具体交点和拟合结论属于 Appendix 的结果 ← `docs/theory/gap.md`、D02a/b/c。
- `CLM-004`：`S(π)` 可作为 AFM 相标签，string operator 可刻画 SPT，相应算符热图与 D01 相图互相印证 ← D03、D04a–d。
- `CLM-005`：`~Z_R` 不易在真机上直接测量，因此后续重点关注态制备以及 D04a、D04b 对应的可测拓扑信息 ← D04 + `topological_op.md`；这是方法论定位，不是新的数据结论。
- `CLM-006`：变分电路由三相初态和 orbit 拟设组成，镜面对映键共享转角，并对应三相的起点/终点示意 ← D05、D06a–c、`psi0.md`、`ansatz.md`。
- `CLM-007`：优质比特筛选使用基准电路、稳定子均值和读出保真度，以 `score=0.8\,\bar{S}+0.2\,F_{ro}` 排序，并在 8 链与 10 环内部独立比较 ← `premium_qubits.md`、exp05 定义。
- `CLM-008`：优质比特排名按 8 链、10 环和冠军环内 8-子链分别报告；具体排名结论属于 Results and Discussion ← D07a/b/c；图尚未生成，具体排名冻结为 `GAP-001-DATA`。
- `CLM-009`：读出误差可用逐比特 `2×2` 概率分配矩阵标定、求逆、非负截零和重归一流程缓解，标定代价随比特数线性增长 ← `readout_mitigation.md`、exp06 `PRE-006`。

### 4. Sections

- `SEC-001` 模型与有限尺寸方法：H 定义、`L=8`、D01 的使用口径和有限尺寸分析协议。
- `SEC-002` 拓扑物理量：D03、D04a–d 及真机可测量量的选择。
- `SEC-003` 变分态制备：D05、D06a–c、初态和 orbit 拟设。
- `SEC-004` 真机实施方法：优质比特筛选协议；具体 D07a–c 排名结论移至 Results and Discussion。
- `SEC-005` 读出误差缓解：矩阵模型、校准流程和代价说明。

### 5. Gaps（缺件表）

- `GAP-001-DATA [non-blocking]`：D07a/b/c 图文件尚未出现在 `figs/exp05/`；由 Results feature 冻结具体排名和图中文字，保留三个空位，不阻塞 Methods 或其他无关 feature。
- D01、D03、D04a–d、D05、D06a–c 目前已有对应数据或图，未发现新的方法缺件。
- `SEC-005` 是纯方法节，无独立 D 图缺件；D08 的具体结果属于 Results and Discussion，不在本 feature 内新增。

### 6. Citation Needs

- `CIT-001`：SSH 模型和拓扑模型背景。
- `CIT-002`：string 序参量、SPT 和拓扑标记方向。
- `CIT-003`：有限尺寸标度/能隙分析方向。
- `CIT-004`：VQE、对称性保持拟设和 orbit 结构方向。
- `CIT-005`：cluster 态、基准测试和优质比特筛选方向。
- `CIT-006`：读出误差缓解方法；可复用已验证的 `bravyi2021mitigating`。
- 所有新增引用必须经过 `paper-zotero-hunter` 的 verify，未验证引用不得合稿。

### 7. Open Questions

- `OQ-001 [non-blocking]`：D07 图到位后确定三图的最终版式和具体排名文字，并把结果结论写入 Results and Discussion。
- `OQ-002 [needs-user]`：D02a/b/c 的具体拟合结果和 D07a/b/c 的具体排名，若数据到位但其解释超出图面，先询问用户要采用的解释，再将其标为用户确认的推测；不得自行补写。
- 已确定的版式和坐标约束直接作为本 feature 的实现约束；不把历史 spec 作为活动定义来源。

---

## Part II — Specification Contract

本部分只记录具有规范性、可检查意义的约束。每条独立约束使用稳定 ID。

### A. Boundary

#### In Scope

- `BND-001` 模型和有限尺寸分析方法正文；D02a/b/c 的曲线、拟合和具体结论属于 Appendix，不作为 Methods 的结果结论。
- `BND-002` D03/D04 拓扑物理量解释和四联图呈现。
- `BND-003` D05/D06 变分态制备示意与方法文字。
- `BND-004` 优质比特筛选方法；D07a–c 图位和具体排名结论属于 Results and Discussion。
- `BND-005` 读出误差缓解方法文字。

#### Out of Scope

- `BND-006` 所有 Dxx/figs 的生成；实验和作图仍由上游 exp/shared feature 负责。
- `BND-007` D08 真机/模拟机结果及趋势结论，归 Results and Discussion。
- `BND-008` 摘要、结论、Related Work 统稿，归 Closing。

#### Dependencies

- `DEP-001` 至 `DEP-006`：`specs/exp01` 至 `specs/exp06` 中对应实验定义和执行记录。
- `DEP-007`：`docs/paper-outline.md` 中方法相关条目。
- `DEP-008`：`docs/theory/` 中模型、算符、初态、拟设、比特筛选和读出缓解文档。

### B. Sections

- `SEC-001`（模型与有限尺寸方法）：输入 H、`topological_op.md`、`gap.md`、D01 的定义 → 输出模型、相图使用口径和有限尺寸分析方法；D02 具体结果由 Appendix feature 消费。
- `SEC-002`（拓扑物理量）：输入 D03、D04a–d、`topological_op.md` → 输出 `S(π)`、string、`Q`、`~Z_R` 解释和图引用。
- `SEC-003`（变分态制备）：输入 D05、D06a–c、`psi0.md`、`ansatz.md` → 输出三相起点/终点与拟设结构说明。
- `SEC-004`（优质比特筛选）：输入 `premium_qubits.md` 和 exp05 定义 → 输出筛选公式、比较口径和可复现实验协议；D07 排名图及结论由 Results feature 消费。
- `SEC-005`（读出误差缓解）：输入 `readout_mitigation.md`、exp06 `PRE-006` → 输出矩阵、求逆、非负约束、重归一和标定代价说明。

### C. Figures

- `FIG-001`：`figs/exp01/exp01_D01.pdf` → 模型/相图正文，单栏；只用于定义参数区域和相的识别口径。
- D02a/b/c 的图位不属于本 Methods feature；由 Appendix feature 定义和消费。
- `FIG-005`：`figs/exp02/exp02_D03.pdf` → `S(q)` 与 AFM 标签正文。
- `FIG-006`：`figs/exp02/exp02_D04a/b/c/d.pdf` → 四联拓扑热力图，跨栏 `figure*` 拼装。
- `FIG-007`：`figs/exp01/exp01_D05.pdf` → 起点/终点示意。
- `FIG-008`：`figs/exp04/exp04_D06a/b/c.pdf` → 三相拟设示意图。
- D07a/b/c 的图位不属于本 Methods feature；由 Results and Discussion feature 定义和消费。

### D. Claim Binding

- `CLM-001` ← evidence [`docs/theory/H.md`]
- `CLM-002` ← evidence [D01 数据与 `figs/exp01/exp01_D01.pdf`]
- `CLM-003` ← evidence [`docs/theory/gap.md`]；D02a/b/c 的具体结果由 Appendix feature 绑定。
- `CLM-004` ← evidence [D03、D04a/b/c/d 对应图与 `topological_op.md`]
- `CLM-005` ← evidence [D04、`topological_op.md`]
- `CLM-006` ← evidence [D05、D06a/b/c、`psi0.md`、`ansatz.md`]
- `CLM-007` ← evidence [`premium_qubits.md`、exp05 定义]
- `CLM-008` ← evidence [`premium_qubits.md`、exp05 定义]；D07a/b/c 的具体排名由 Results feature 绑定。
- `CLM-009` ← evidence [`readout_mitigation.md`、exp06 `PRE-006`]

### E. Gaps

- 本 Methods feature 不因 D02 或 D07 结果图缺失而阻塞；结果图和具体结论由 Appendix/Results feature 各自冻结。
- 若结果图到位但解释不能由图和实验定义直接推出，新增 `GAP-001-INTERP [needs-user]`，询问用户要采用的解释，再将其标为用户确认的推测；不得自行填充。

### F. Citation Requirements

- `CIT-001` 至 `CIT-005` 分别覆盖模型、拓扑物理量、有限尺寸、VQE/拟设、硬件筛选主张；均须 hunt + verify。
- `CIT-006` 覆盖读出缓解方法，可复用已验证条目。
- 引用 key 必须存在于 `docs/paper/references.bib`，未验证引用不得合稿。

### G. Acceptance

- `VAL-001` → verifies [`SEC-001`..`SEC-005`]：五个方法子节的输入、输出和边界齐套。
- `VAL-002` → verifies [`FIG-001`, `FIG-005`, `FIG-006`, `FIG-007`, `FIG-008`]：Methods 负责的模型、诊断量和态制备图位存在且只承担方法定义口径；D02/D07/D08 结果图由对应 feature 验收。
- `VAL-003` → verifies [`CLM-001`..`CLM-009`]：每条主张有证据；D07 具体排名保持冻结。
- `VAL-004` → verifies [`CIT-001`..`CIT-006`]：引用已 verify，key 齐全。
- `VAL-005` → verifies [compile]：当前正文和附录编译通过，无未定义引用；D07 缺件不阻塞无关方法段落。
