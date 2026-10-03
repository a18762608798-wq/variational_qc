# Feature Specification: SSH-XXZ Numerical Experiments 01–04

**Feature Branch**: `001-ssh-xxz-experiments-01-04`

**Created**: 2026-09-30

**Status**: Draft

**Constitution**: v0.2.0

**Input**: User description: "Feature Specification: SSH-XXZ Numerical Experiments 01–04 (experiments 01 phase structure, 02 observable characterization, 03 L=8 exact reference, 04 ideal variational preparation; full text supplied in triggering message)"

## Scope

本 specification 定义当前 SpecKit cycle 中实验 01–04 必须完成的科学计算目标、输入参数、输出数据与验收条件。

当前 cycle 的计算链为

$$
\boxed{
01\ \text{phase structure}
\rightarrow
02\ \text{observable characterization}
\rightarrow
03\ L=8\ \text{exact reference}
\rightarrow
04\ \text{ideal variational preparation}
}
$$

本 specification 规定 **what must be computed and verified**。

代码架构、模块划分、具体 solver、optimizer 实现、并行策略、缓存格式、文件目录与性能优化属于 `/speckit.plan`。

所有 Hamiltonian、initial state、ansatz、cost function、observable 和 symmetry 的数学定义以当前 `theory/` authoritative specification 为准，本文件不重新定义第二份物理公式。

## Clarifications

### Session 2026-09-30

- Q: 实验 01/02 主相图网格的系统尺度用 L=16（spec）还是 L=8（`doc/`）？ → A: L=8；一切矛盾以 `doc/` 为准（用户确认）。
- Q: CL-001–CL-003 是否仍为待澄清问题？ → A: 否；三项已冻结（CL-001=1A、CL-002=2A，CL-003 以 `doc/` 为准），由用户直接给出，未重新提问；已记入 Binding Clarifications。
- Q: q-domain/q-grid 在 `doc/` 无记载时如何处理？ → A: 记录双约束（三条曲线同 q 坐标、q=π 显式），分辨率交 `/speckit.plan` 确定；不引入新科学需求。

## User Scenarios & Testing *(mandatory)*

### Research Story 1 — Establish the Exact Phase Structure (Experiment 01) (Priority: P1)

作为研究者，我需要首先得到 SSH-XXZ 模型的 exact finite-size phase structure，使后续 observable characterization 和 variational experiment 有明确的物理参照。

**Why this priority**: 所有下游实验（observable 选择、exact reference 对照、variational 验证）都依赖 01 建立的相结构参照；它是最上游的阻塞项。

**Independent Test**: 仅用保存的 Experiment 01 数据即可重建 L=8 相图、四条 raw gap 曲线与 s=0.5 scaling 图，无需重新执行 exact diagonalization（SC-001）。

**Required scientific outputs**:

对于 Experiment 01：

* 主系统尺度：$L=8$（以 `doc/` 为准，见 Binding Clarifications 与 Session 2026-09-30）。
* 参数区域：$s\in[0,1],\qquad \delta\in[0,3]$，实际计算取冻结的 $49\times49$ 内点网格：$s_i=i/50\;(i=1,\dots,49)$，$\delta_j=2j/50\;(j=1,\dots,49)$，即 $s\in[0.02,0.98]$、$\delta\in[0.04,1.96]$，不含参数空间边界。（2026-10-01 修订：$\delta$ 网格按现行 `doc/` 由 $3j/50$ 改为 $2j/50$。）
* 在该网格上计算 exact ground-state $\tilde Z_{\mathcal R}(s,\delta)$ 并形成 phase-diagram source data。
* 在 $\delta=1$ 上计算 $L=4,8,12,16$ 的 raw full-Hilbert-space energy gap $\Delta_{\rm raw}(s,L)=E_1(s,L)-E_0(s,L)$。
* raw gap 使用物理 Hamiltonian $H$ 的完整谱定义，不加入 $P$ penalty，不进行 symmetry-sector gap 替换。
* OBC 拓扑侧 edge-state splitting 导致的 $s\to1$ gap collapse 保留为 raw spectrum 的真实结果；不得通过 numerical threshold、cutoff 或人为删点消除。
* finite-size scaling 固定考察 $\Delta_{\rm raw}(s=0.5,L)$ 随 $1/L$ 的变化。
* 不使用 $\arg\min_s\Delta_{\rm raw}(s,L)$ 作为 bulk critical point estimator，也不要求标记各 $L$ 的 global minimum。

**Acceptance Scenarios**:

1. **AS-01.1** — Given $L=8$ 和完整 Experiment 01 参数网格，when exact calculation 完成，then 每个参数点必须存在对应的 $\tilde Z_{\mathcal R}$ raw record 或显式 failure record。
2. **AS-01.2** — Given $\delta=1$ 和 $L=4,8,12,16$，when finite-size calculation 完成，then 每个 $L$ 必须得到完整的 $\Delta_{\rm raw}(s,L)$ 数据。
3. **AS-01.3** — Given 四个 system sizes，when finite-size scaling 完成，then 必须得到四个 $(1/L,\Delta_{\rm raw}(0.5,L))$ 数据点以及 specification 要求的 linear-fit result。
4. **AS-01.4** — Experiment 01 必须能够仅由保存的数据重新生成：$L=8$ $\tilde Z_{\mathcal R}$ phase diagram；$\delta=1$ 的四条 raw gap curves；$s=0.5$ finite-size scaling figure。

---

### Research Story 2 — Characterize Experimentally Relevant Observables (Experiment 02) (Priority: P2)

作为研究者，我需要在 exact ground states 上比较 $S(q)$、$S(\pi)$、string order、$Q$ 和 $\tilde Z_{\mathcal R}$，从而建立后续为什么重点考察 $S(\pi)$ 与 $O_{\rm str}$ 的数值依据。

**Why this priority**: 02 建立 observable-selection chain，是 04 只需对比 $S(\pi)$ 与 $O_{\rm str}$ 的合法性依据；依赖 01 的相结构，但独立于 03/04 的 variational 工作。

**Independent Test**: 仅用保存的 Experiment 02 数据即可重建三相 $S(q)$ comparison 与四个 observable heatmaps，无需重新执行 exact diagonalization（SC-002）；且 $Q$ 可仅由已保存的 $S(\pi)$ 与 $O_{\rm str}$ 重建（AS-02.3）。

**Required scientific outputs**:

Experiment 02 使用 $L=8$，与 Experiment 01 严格共享同一 $49\times49$ 内点网格（$s_i=i/50$，$\delta_j=2j/50$，$i,j=1,\dots,49$；见 Binding Clarifications CL-001，2026-10-01 按现行 `doc/` 修订）。

Experiment 02 与 Experiment 01 对相同 phase-space coordinates 必须使用一致的 exact-state convention。

必须计算：$S(\pi),\; O_{\rm str},\; Q,\; \tilde Z_{\mathcal R}$。其中 $Q$ 按 theory specification 定义为由 $S(\pi)$ 和 $O_{\rm str}$ 构成的 ZR-like diagnostic。

必须使用冻结的三相代表点 trivial $(s,\delta)=(0.02,0.06)$、topological $(0.98,0.06)$、AFM $(0.5,2.94)$（均为冻结网格点，见 Binding Clarifications CL-003），并计算三条 $S(q)\ {\rm vs}\ q$ 曲线，用于展示 AFM representative 在 $q=\pi$ 的结构因子响应。三条曲线必须使用相同 $q$ coordinates，且 $q=\pi$ 必须为显式 grid point；$q$-grid resolution 由 `/speckit.plan` 在此约束下确定。

Experiment 02 的逻辑目标是建立以下 observable-selection chain：

$$
\text{phase structure}
\rightarrow
\text{representative states}
\rightarrow
S(q)
\rightarrow
S(\pi)
\rightarrow
{S(\pi),O_{\rm str}}
$$

**Acceptance Scenarios**:

1. **AS-02.1** — Given Experiment 02 parameter grid，when exact observable calculation 完成，then 每个有效参数点必须包含 $S(\pi),\; O_{\rm str},\; Q,\; \tilde Z_{\mathcal R}$。
2. **AS-02.2** — Given 三个 phase representative points，when $S(q)$ calculation 完成，then 必须得到三条使用相同 $q$ coordinates 的 $S(q)$ curves。
3. **AS-02.3** — $Q$ 必须能够仅由同一 parameter point 已保存的 $S(\pi)$ 和 $O_{\rm str}$ 重建，不允许存在另一套独立的 $Q$ 物理定义。
4. **AS-02.4** — Experiment 02 保存的数据必须能够重新生成：三相 representative 的 $S(q)$ comparison；$S(\pi)$ heatmap；$O_{\rm str}$ heatmap；$Q$ heatmap；$\tilde Z_{\mathcal R}$ heatmap。若 Experiment 01 已产生完全相同的 $\tilde Z_{\mathcal R}$ source data，Experiment 02 应视其为同一 canonical scientific result，而不是定义第二套不同结果。

---

### Research Story 3 — Establish the L=8 Exact Reference (Experiment 03) (Priority: P3)

作为研究者，我需要为 Experiment 04 建立与其完全相同参数坐标上的 $L=8$ exact ground truth，使 variational result 可以逐点与 exact result 比较。

**Why this priority**: 03 是 04 的唯一 exact ground-truth source（FR-005）；它本身不含 variational 概念，可独立于 04 先行完成并冻结坐标。

**Independent Test**: 两条扫描线各有 49 个 exact records，每条 record 含 $E_0, S_{\rm exact}(\pi), O_{{\rm str},{\rm exact}}$（AS-03.1/AS-03.2）；且其 $s$ 坐标被 04 原样复用为 authoritative scan coordinates（AS-03.3）。

**Required scientific outputs**:

固定 $L=8$。计算两条扫描线 $\delta=1,\; \delta=3$，每条使用 $s_i=i/50\;(i=1,\dots,49)$。因此 exact-reference dataset 共包含 $2\times49=98$ 个 physical parameter points。

每个 parameter point 必须计算并保存：$E_0(s,\delta)$，$S_{\rm exact}(\pi;s,\delta)$，$O_{{\rm str},{\rm exact}}(s,\delta)$。

Experiment 03 只建立 exact reference，不包含 variational depth、optimizer 或 hardware 概念。

**Acceptance Scenarios**:

1. **AS-03.1** — Given $\delta=1,3$，when Experiment 03 完成，then 两条扫描线各必须存在 49 个 exact parameter records。
2. **AS-03.2** — 每个成功的 exact record 必须同时具有 $E_0,\; S_{\rm exact}(\pi),\; O_{{\rm str},{\rm exact}}$。
3. **AS-03.3** — Experiment 03 的 $s$ coordinates 必须作为 Experiment 04 的 authoritative scan coordinates；Experiment 04 不得重新生成一套不同的 $s$ grid。
4. **AS-03.4** — 保存的数据必须能够重新生成 $\delta=1,3$ 下 exact $E_0(s),\; S_{\rm exact}(\pi),\; O_{{\rm str},{\rm exact}}(s)$ reference curves。

---

### Research Story 4 — Validate Ideal Variational State Preparation (Experiment 04) (Priority: P4)

作为研究者，我需要在完全 noiseless、shot-free 的条件下判断 orbit ansatz 随深度增加是否能够逼近 Experiment 03 的 exact ground states，并区分 ansatz/optimization limitation 与未来 sampling/hardware error。

**Why this priority**: 04 是本 cycle 的最终科学判断点（ansatz 表达能力 vs 优化能力），依赖 03 的 exact reference；其 frozen-parameter 方法论同时为未来 finite-shot/hardware 阶段隔离误差做准备。

**Independent Test**: 任一 $(s,\delta,p)$ 下三条 branch 各有独立 result 或显式 failure（AS-04.1），selected 为三者最低 physical energy（AS-04.2），满足 $E_{\rm var}\ge E_0$ 容差检查（AS-04.4），depth 增加不恶化 accepted best energy 否则标记 failure（AS-04.5）。

**Required scientific outputs**:

固定 $L=8$，使用 Experiment 03 的两条扫描线 $\delta=1,\; \delta=3$ 及相同的 49 个 $s$ coordinates。对每个 parameter point 计算 $p=1,2,3,4,5$。因此最终必须存在 $2\times49\times5=490$ 个 parameter-point/depth level 的 selected variational results。

Variational state 使用 authoritative `theory/ansatz.md`。Cost 使用 physical Hamiltonian energy：$\langle\psi(\theta)| H(s,\delta) |\psi(\theta)\rangle$。

每个 $(s,\delta,p)$ 必须分别从三类 reference initial-state branches（$\text{trivial},\; \text{topological},\; \text{AFM}$）执行独立 variational search。selected variational result 定义为三条 branch 中最终 physical energy 最低者。每条 branch 的结果必须保留；不得只保存 selected branch。

对于 selected variational state，至少计算并保存 $E_{\rm var},\; S_{\rm var}(\pi),\; O_{{\rm str},{\rm var}}$，并与 Experiment 03 同一 parameter point 的 $E_0,\; S_{\rm exact}(\pi),\; O_{{\rm str},{\rm exact}}$ 逐点关联。

$\delta=1$ 与 $\delta\neq1$ 的 ansatz parameter constraints、三种 initial state 对应的 sublayer order、GHZ branch 的已确认冗余参数规则以及多层 fixed-order ansatz 均以当前 authoritative theory specification 为准。

Experiment 04 是纯 ideal variational experiment：no shots；no noise model；no physical-qubit mapping；no coupling map；no initial layout；no hardware transpilation/routing；no mitigation；no hardware-specific normalization。

**Acceptance Scenarios**:

1. **AS-04.1** — Given 任意一个 Experiment 03 parameter point 和任意 $p\in\{1,\dots,5\}$，when Experiment 04 完成，then trivial/topological/AFM 三个 branch 均必须存在独立 optimization result 或显式 failure record。
2. **AS-04.2** — Given 三个成功 branch results，selected result 的 energy 必须等于三者中最低的 physical-Hamiltonian energy。
3. **AS-04.3** — Selected result 必须包含 $E_{\rm var},\; S_{\rm var}(\pi),\; O_{{\rm str},{\rm var}}$ 以及能够唯一关联到 Experiment 03 exact record 的 coordinates。
4. **AS-04.4** — 在 numerical tolerance 内必须满足 variational principle $E_{\rm var}\ge E_0$。任何超出 tolerance 的 violation 必须被标记为 correctness failure，而不能作为正常 scientific result 接受。
5. **AS-04.5** — 对于 ansatz specification 保证的 nested depth construction，$p-1$ 的 accepted state 必须能够作为 $p$ 参数空间中的可行状态。因此最终 accepted best energy 不应由于单纯增加 depth 而恶化；若实际 optimization 未达到该 baseline，必须保留 baseline 或显式标记 optimization failure。
6. **AS-04.6** — Experiment 04 保存的数据必须能够生成 exact 与 $p=1,\dots,5$ variational results 的 $E(s),\; S(\pi;s),\; O_{\rm str}(s)$ comparison。

---

### Edge Cases

- **Degenerate ground states**：当物理基态简并时，observable 按 theory/specification 的 representative/state-selection convention 计算（FR-003）；但 Experiment 01 的 raw gap 仍保持 full-Hilbert-space 定义 $E_1-E_0$，不受影响。
- **OBC edge-state gap collapse**：$s\to1$ 侧的 gap collapse 是 raw spectrum 真实结果，不得用 threshold/cutoff/删点消除；下游不得将其误读为 bulk critical behavior。
- **Failed points/branches**：任何失败点必须显式保存 failure state（FR-008）；plotting 不得静默忽略失败点（SC-001/SC-002/SC-006 的重建必须能区分"失败"与"缺失"）。
- **Variational principle violation**：超出 tolerance 的 $E_{\rm var} < E_0$ 即 correctness failure，不得作为科学结果接受（AS-04.4）。
- **Depth non-monotonicity**：accepted best energy 随 $p$ 恶化时，必须保留 baseline 或标记 optimization failure（AS-04.5）。
- **Grid mismatch**：01/02 网格一致性、03/04 坐标同一性分别由 CL-001 与 AS-03.3 约束；04 不得另起 $s$ grid。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 — Authoritative physics**：所有 01–04 calculation 必须使用当前 `theory/` definitions。不得在 experiment-level code 中创建与 theory 不一致的 Hamiltonian、observable、initial state、ansatz 或 cost convention。
- **FR-002 — Physical Hamiltonian**：所有 physical energies 与 Experiment 04 variational cost 必须来自物理 Hamiltonian $H$。辅助 symmetry operator 或 penalty construction 只能用于 theory specification 明确允许的 state selection，不得把其 eigenvalue 当作 physical energy。
- **FR-003 — Degenerate ground states**：当 physical Hamiltonian ground state 存在 degeneracy 时，ground-state observable 必须使用项目 theory/specification 定义的 representative/state-selection convention。该规则不得改变 Experiment 01 raw gap 的 full-Hilbert-space definition。
- **FR-004 — Observable consistency**：$S(q)$、$S(\pi)$、$O_{\rm str}$、$Q$ 和 $\tilde Z_{\mathcal R}$ 必须在所有实验中保持同一 mathematical convention。
- **FR-005 — Exact-reference reuse**：Experiment 03 是 Experiment 04 的唯一 $L=8$ exact ground-truth source。Experiment 04 不得重新定义 exact reference。
- **FR-006 — Raw data preservation**：所有 scientific outputs 必须保存 raw numerical values。当前 01–04 cycle 不要求 0–1 normalization；任何未来 normalization 不得覆盖 raw result。
- **FR-007 — Intermediate results**：长时间计算必须保留足够的中间结果，使单点失败或任务中断不要求从头重算整个 experiment。
- **FR-008 — Explicit failure**：任何未成功完成的 parameter point 或 optimization branch 必须以 explicit failure state 保存，不得静默删除、用零替代或被 plotting code 忽略。
- **FR-009 — Reproducible coordinates**：每条 numerical record 必须显式保存自己的 physical coordinates，而不能仅通过 array index 推断。
- **FR-010 — Diagnostic and publication outputs**：Experiments 01–04 必须保存足够 source data，以生成：(1) 阶段性 diagnostic figures；(2) 最终符合项目 publication-figure specification 的 PRA figures。具体 visual style、panel layout、字体、尺寸和 export procedure 不在本 specification 定义，由 Constitution 与 `pra-paper-figures` 约束。

### Key Entities *(include if feature involves data)*

- **PhaseGridPoint**：Experiment 01/02 中一个 exact phase-space coordinate；至少包含概念字段 $(L,s,\delta)$ 以及该实验要求的 exact observables。
- **FiniteSizeGapPoint**：一个 raw finite-size spectrum point：$(L,s,\delta=1,E_0,E_1,\Delta_{\rm raw})$。
- **ExactReferencePoint**：Experiment 03 的一个 ground-truth record：$(L=8,s,\delta,E_0,S_{\rm exact}(\pi),O_{{\rm str},{\rm exact}})$。
- **VariationalBranchResult**：Experiment 04 在给定 $(s,\delta,p,\text{initial-state branch})$ 上的一次最终 branch-level scientific result；必须能够追溯到其 optimized parameters 与 final physical energy。
- **SelectedVariationalResult**：同一 $(s,\delta,p)$ 下三条 initial-state branches 中 accepted physical energy 最低的结果，并关联相应 ExactReferencePoint。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**：Experiment 01 能从保存数据完整重建 phase diagram、raw finite-size gap curves 和 $s=0.5$ scaling result，而无需重新执行 exact diagonalization。
- **SC-002**：Experiment 02 能从保存数据完整重建三相 $S(q)$ comparison 和四个 observable heatmaps，而无需重新执行 exact diagonalization。
- **SC-003**：Experiment 03 最终包含完整的 $98=2\times49$ 个 exact reference coordinates，除非存在显式记录的 numerical failure。
- **SC-004**：Experiment 04 最终包含完整的 $490=2\times49\times5$ 个 selected point/depth coordinates；每个 coordinate 同时保留三个 initial-state branch 的 provenance/result 或明确 failure information。
- **SC-005**：所有 Experiment 04 selected energies 满足 variational principle，误差范围由 `/speckit.plan` 中定义并通过 tests 验证。
- **SC-006**：01–04 的所有 final scientific figures 都可以从保存的 source data deterministic regeneration；修改 figure style 不需要重新执行 physics calculation。
- **SC-007**：完成 01–04 后，不需要任何 experiment 05/hardware component 即可独立运行、检查和复现实验 01–04。

## Out of Scope

当前 specification 不包含：finite-shot Aer；shot-noise experiment；hardware execution；physical-qubit selection；coupling map；initial layout；hardware transpilation；routing；hardware noise model；measurement mitigation；noise mitigation；hardware VQE；hardware-specific normalization；Experiment 05 或之后实验；为上述未来任务预建 generic backend/execution framework。

这些内容只有在 01–04 完成并通过 `/speckit.converge` 后，才能进入新的 specification cycle。

## Binding Clarifications (frozen 2026-09-30)

CL-001–CL-003 已冻结为 binding specification，不再是 open 问题。来源：用户 2026-09-30 冻结指令与 `doc/plan` authoritative 记录；两者不一致处以 `doc/` 为准（用户已确认，见 Clarifications / Session 2026-09-30）。

### CL-001 — Experiment 01/02 phase-space grid = 1A

- 01 与 02 使用同一 $49\times49$ 内点网格：$s_i=i/50\;(i=1,\dots,49)$，$\delta_j=2j/50\;(j=1,\dots,49)$。
- 即 $s\in[0.02,0.98]$，$\delta\in[0.04,1.96]$；参数空间边界 excluded。
- 01 与 02 必须共享完全相同的 coordinates（与 `doc/plan/experiment/01_phase_observables.md`、`02_topological_op.md` 一致）。
- （2026-10-01 修订：$\delta$ 网格由 $3j/50$ 改为 $2j/50$；1A 的同网格方法与共享规则不变。）

### CL-002 — Finite-size linear fit convention = 2A

- Scaling 点固定为 $s=0.5$；拟合 $\Delta_{\rm raw}(0.5,L)=a/L+b$，截距自由。
- 报告 a 和 b；不约束 $b=0$（`doc/` 中"理论上截距为0"为热力学极限物理注释，非约束拟合指令）。
- 不使用、不搜索 raw OBC gap 的 global minimum 作为 finite-size critical-gap estimator（AS-01.3 的 linear-fit result 即此自由截距拟合）。

### CL-003 — $S(q)$ representatives and $q$-grid (frozen)

- 代表点：trivial $(s,\delta)=(0.02,0.06)$、topological $(0.98,0.06)$、AFM $(0.5,2.94)$（`doc/plan/experiment/02_topological_op.md`；三者均为 CL-001 网格点）。
- $q$ 双约束：三条 $S(q)$ 曲线使用相同 $q$ coordinates（AS-02.2）；$q=\pi$ 必须为显式 grid point。
- $q$-domain/$q$-grid 具体分辨率在 `doc/` 无记载，不另设候选方案；由 `/speckit.plan` 在上述双约束下确定。

### 主尺度裁决（用户 2026-09-30 确认）

- 01/02 主相图网格尺度用 $L=8$（`doc/plan` 01、02 两文件与 REVIEW.md 口径）；本 spec 原 L=16 已按此改写。
- 有限尺寸部分（$L=4,8,12,16$、$\delta=1$、$s=0.5$ scaling）不变，与 `doc/` 一致。

## Assumptions

1. 当前 theory files 已完成本 cycle 所需物理定义。
2. 当前 cycle 只研究 OBC SSH-XXZ problem。
3. Experiment 04 的目标是 ideal variational state-preparation capability，而不是 simulator/hardware execution performance。
4. publication figure 的具体视觉规范不在本 specification 重复定义。
5. numerical implementation 的具体 architecture 和 algorithm selection 留给 `/speckit.plan`。
