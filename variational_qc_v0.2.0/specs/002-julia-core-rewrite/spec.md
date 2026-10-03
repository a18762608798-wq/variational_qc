# Feature Specification: Julia Core Rewrite (SSH-XXZ 01–04)

**Feature Branch**: `002-julia-core-rewrite`

**Created**: 2026-09-30

**Status**: Draft

**Constitution**: v0.3.0

**Input**: User description: "New round (constitution v0.3.0): modified SSH-XXZ Hamiltonian, migrate compute to Julia rewriting the Python core; experiment scope per doc files; schema v2; v1 data voided except anchors; full 01–04 recompute; no solver/optimizer preference; qmeas equivalent, provenance carryover, cross-check tolerance deferred to clarify."

## Scope

本 specification 定义第二轮（Julia cycle）必须完成的科学计算目标：以修改后的 Hamiltonian（`doc/plan/theory/H.md` 为准，本文件不重复物理公式）为唯一物理口径，用 Julia 重写 Python 核心（`src/ssh_xxz` 封存只读，仅作对照基线），按 `doc/plan/experiment/01–04` 的实验口径全量重算 01–04，结果存为 schema `exp01-04/v2`。

上一轮 v1 数据作废（XII.2–XII.3）：仅保留 5 点等价子集定义与解析态 $+1/-1/0$ 交叉验证锚点；其余 v1 记录在 converge 封存后可删。

本 specification 规定 **what must be computed and verified**。Julia 求解器/优化器选型、qmeas 对等物实现、provenance 落盘细节见 Binding Clarifications（D-001–D-003 已冻结）；其余实现细节属于 `/speckit.plan`。

## Clarifications

### Session 2026-09-30

- Q: Julia 栈的求解器与优化器组合选哪一套？(D-001) → A: Option A — KrylovKit.jl 稀疏本征 + LinearAlgebra 稠密交叉验证 + Yao.jl 理想态矢量 + Optim.jl/NLopt 优化链（对标上一轮 DE+COBYLA 方法）。
- Q: Julia vs 封存基线的交叉验证容差与覆盖范围？(D-002) → A: Option A — 能量 <1e-8、观测量 <1e-6；覆盖 5 点子集全量 + 解析态锚点 + 01–04 每实验 ≥3 点抽样。
- Q: Julia 侧 qmeas 对等物采用什么形式？(D-003) → A: Option A — 最小端口（仅 H 与初态构造器 + 5 点 <1e-10 等价测试）；其余子模块本轮不复用；硬件映射/采样层/通用后端抽象 out-of-scope（XII 锁定，沿 XI 体例）。

## User Scenarios & Testing *(mandatory)*

### Research Story 1 — Recompute the Exact Phase Structure in Julia (Experiment 01) (Priority: P1)

作为研究者，我需要新 Hamiltonian 下 $L=8$ 的 exact 相图与有限尺寸能隙全部由 Julia 栈算出，使后续工作彻底脱离 Python 核心。

**Why this priority**: 最上游阻塞项；新 $H$ 下旧相图数值整体作废，必须先重建。

**Independent Test**: 仅用 v2 保存数据即可重建 $L=8$ $\tilde Z_{\mathcal R}$ 相图、$\delta=0$ 的三条 raw gap 曲线（$L=8,12,16$）与 $s=0.5$ scaling 图，无需重新计算（SC-001 analogues）。

**Required scientific outputs** (per `doc/plan/experiment/01_phase_observables.md`):

$L=8$ 主网格：与上一轮相同的 $49\times49$ 内点网格（$s_i=i/50$，$\delta_j=2j/50$）。$\delta=0$ 线上 $L=8,12,16$ 的 raw full-Hilbert-space gap $\Delta_{\rm raw}(s,L)=E_1-E_0$；scaling 点固定 $s=0.5$，拟合 $\Delta_{\rm raw}=a/L+b$ 自由截距（CL-002 延续有效）。

**Acceptance Scenarios**:

1. **AS-01.1** — 每个网格点存在 v2 $\tilde Z_{\mathcal R}$ raw record 或显式 failure record。
2. **AS-01.2** — $\delta=0$、四个 $L$ 各有完整 $\Delta_{\rm raw}(s,L)$ 数据。
3. **AS-01.3** — 仅用 v2 数据可重建相图、gap 曲线、scaling 图（含 $a,b$ 系数）。

---

### Research Story 2 — Recompute Observable Characterization (Experiment 02) (Priority: P2)

作为研究者，我需要新 $H$ 下 $S(\pi)$、$O_{\rm str}$、$Q$、$\tilde Z_{\mathcal R}$ 与三相 $S(q)$ 全部由 Julia 栈算出。

**Why this priority**: observable 选择链的合法性依据，需与 01 同步刷新。

**Independent Test**: 仅用 v2 数据重建三相 $S(q)$ comparison（49 点 $q$ 网格，$q=\pi$ 显式）与四个 heatmap；$Q$ 仅由已保存的 $S(\pi)$、$O_{\rm str}$ 重建。

**Required scientific outputs** (per `doc/plan/experiment/02_topological_op.md`):

$L=8$，与 01 同网格（$s_i=i/50$，$\delta_j=2j/50$）；三相代表点 trivial $(0.02,0.06)$、topological $(0.98,0.06)$、AFM $(0.5,1.96)$（2026-10-01 按现行 `doc/` 修订；其中 AFM 点落在冻结网格角上）；$q$ 在 $[0,2\pi)$ 取 49 点。

**Acceptance Scenarios**:

1. **AS-02.1** — 每个有效点含 $S(\pi), O_{\rm str}, Q, \tilde Z_{\mathcal R}$（v2）。
2. **AS-02.2** — 三条同 $q$ 坐标 $S(q)$ 曲线，三线样式可区分。
3. **AS-02.3** — $Q$ 无独立物理定义，纯派生。

---

### Research Story 3 — Rebuild the L=8 Exact Reference (Experiment 03) (Priority: P3)

作为研究者，我需要新 $H$ 下 $\delta=0,0.85$ 两条线、$s_i=i/50$（49 点）的 exact ground truth，共 98 点，全部 v2。

**Why this priority**: 04 的唯一对照源；其 $s$ 坐标仍为 04 的 authoritative scan coordinates。

**Independent Test**: 两条线各 49 条 exact records，每条含 $E_0, S_{\rm exact}(\pi), O_{{\rm str},{\rm exact}}$；04 原样复用其 $s$ 数组。

**Acceptance Scenarios**:

1. **AS-03.1** — $98=2\times49$ exact records（除显式 failure）。
2. **AS-03.2** — Experiment 04 不得另起 $s$ grid。

---

### Research Story 4 — Ideal Variational Preparation on the Julia Stack (Experiment 04) (Priority: P4)

作为研究者，我需要在 Julia 态矢量模拟（Yao.jl，按 `doc/plan/experiment/04_ideal_vqe.md`）下以 orbit ansatz 重做 $p=1,\dots,5$ 三分支理想优化，共 490 selected + 1470 branch（v2）。

**Why this priority**: 本轮最终科学判断点；方法论约束沿用上一轮（frozen parameters 思想、branch 保留、selected 取最低物理能量）。

**Independent Test**: 任一 $(s,\delta,p)$ 三分支各有独立 result 或显式 failure；selected 为最低者；在容差内 $E_{\rm var}\ge E_0$；depth 钳位（baseline 保留或显式 failure）。

**Required scientific outputs** (per `doc/plan/experiment/04_ideal_vqe.md`):

$L=8$，$\delta=0,0.85$ 线，03 的 49 点；$\delta=0$ 参数减半（$\theta_1=\theta_2$），不额外删参数；$\delta=0.85$ 用正常全参数；AFM 初态分支首层首个偶子层的两个独立 $ZZ$ orbit 参数（$L=8$ 时即 $e_{{\rm out},2}$、$e_{c,2}$）固定为 0（与扫描 $\delta$ 无关），第二层起所有 $ZZ$ 参数正常优化；seed 确定性派生；纯 ideal（no shots/noise/mapping）。

**Acceptance Scenarios**:

1. **AS-04.1** — 三分支独立结果或显式 failure。
2. **AS-04.2** — selected 能量 = 三者最低物理能量。
3. **AS-04.3** — selected 含 $E_{\rm var}, S_{\rm var}(\pi), O_{{\rm str},{\rm var}}$ + exact 关联坐标。
4. **AS-04.4** — 容差内 variational principle；超差即 correctness failure。
5. **AS-04.5** — nesting 钳位（baseline 保留或显式标记）。

---

### Edge Cases

- **Degenerate ground states**：沿用上一轮 representative/state-selection convention（FR-003 精神）；raw gap 保持 full-Hilbert-space 定义。
- **Failed points/branches**：显式 failure state，禁静默删除/零替代/无因 NaN（FR-008 精神）。
- **Cross-check mismatch**：Julia 新栈 vs 封存基线超出 clarify 待定容差时，记 correctness failure，不得作为正常结果接受。
- **v1 residue**：任何 v1 记录（除验证锚点）不得流入 v2 数据集与绘图。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 — Authoritative physics**：一切计算使用 `doc/plan/theory/H.md` 定义；不得在 Julia 代码中另立 Hamiltonian/observable/初态/ansatz/cost convention。封存 Python 核心只读，不得修改。
- **FR-002 — Physical Hamiltonian**：所有物理能量与 variational cost 来自物理 $H$；辅助算符仅用于 theory 允许的 state selection。
- **FR-003 — Schema v2**：所有新记录存 schema `exp01-04/v2`（含 provenance：experiment/stage、$L$、参数、depth、branch、optimizer/backend、seed、code 版本；source/backend 身份明确）。
- **FR-004 — v1 void with anchors**：v1 数据作废；仅保留 5 点等价子集定义与解析态 $+1/-1/0$ 锚点用于交叉验证（XII.3）。
- **FR-005 — Baseline cross-check**：Julia 结果须与封存 Python 基线做数值对照（qmeas 复用暂停期间的替代验证）；对照容差与覆盖范围由 `/speckit.clarify` 确定后冻结为 binding。
- **FR-006 — Raw data preservation**：v2 保存 raw 值；normalization/fit 屬后处理，不得覆盖 raw。
- **FR-007 — Intermediate results + idempotent resume**：长算保留中间结果；同配置重跑幂等，禁静默覆盖 incompatible result。同 $(L,s,\delta)$ 精确基态向量存入 shared canonical store 并复用（01 网格 $L=8$ 与 gaps $L=8,12,16$ 全存；02 直接利用 01 网格基矢；03 $\delta=0$ 线直接利用 01-gap $L=8$ 基矢）；凡 shared 已有同坐标基矢一律复用，不得重复对角化。
- **FR-008 — Diagnostic and publication outputs**：v2 source data 须支撑 diagnostic 与 PRA 双管线（pdf + dpi=600 png 双存延续）；绘图只读已存数据。

### Key Entities *(include if feature involves data)*

- **PhaseGridPoint (v2)**：$(L=8,s_i,\delta_j)$ + exact observables + provenance。
- **FiniteSizeGapPoint (v2)**：$(L\in\{8,12,16\},s,\delta=0,E_0,E_1,\Delta_{\rm raw})$。
- **ExactReferencePoint (v2)**：$(L=8,s,\delta\in\{0,1\},E_0,S_{\rm exact}(\pi),O_{{\rm str},{\rm exact}})$。
- **VariationalBranchResult (v2)**：$(s,\delta,p,{\rm branch})$ + optimized parameters + final energy + provenance。
- **SelectedVariationalResult (v2)**：三分支最低者 + exact 关联。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**：01 能从 v2 数据完整重建相图、gap 曲线、scaling（含 $a,b$），无需重算。
- **SC-002**：02 能从 v2 数据完整重建 $S(q)$ comparison + 四 heatmaps；$Q$ 纯派生可验证。
- **SC-003**：03 含完整 $98=2\times49$ exact coordinates（除显式 failure）。
- **SC-004**：04 含完整 $490=2\times49\times5$ selected + 三分支 provenance/failure。
- **SC-005**：全部 selected 在冻结容差（能量 <1e-8，见 Binding Clarifications D-002）内满足 variational principle。
- **SC-006**：全部 final figures 可从 v2 source data 确定性重建（含哈希门）。
- **SC-007**：01–04 不依赖任何 05/hardware component 独立运行、检查、复现。

## Out of Scope

05/hardware 全套（finite-shot、hardware execution、选比特、coupling map、转译、mitigation、hardware VQE）；Python 核心的任何修改（封存只读）；v1 数据的复活（除验证锚点）。本轮 scope 锁定 01–04 理想计算（exact + ideal variational）；任何硬件映射、采样层、通用后端抽象均 out-of-scope，不得进入 plan 与 tasks（XII 沿 XI 体例锁定）。

## Binding Clarifications (frozen 2026-09-30, clarify session above)

- **D-001 — Julia solver/optimizer stack = A**：KrylovKit.jl `eigsolve` 稀疏 ED + LinearAlgebra 稠密交叉验证（小 $L$）+ Yao.jl 理想态矢量 + Optim.jl/NLopt 优化链（对标上一轮 DE+COBYLA 方法）。
- **D-002 — Cross-check tolerance and coverage = A**：Julia vs 封存基线，能量 <1e-8、观测量 <1e-6；覆盖 5 点等价子集全量 + 解析态 $+1/-1/0$ 锚点 + 01–04 每实验 ≥3 点抽样。超差即 correctness failure。
- **D-003 — qmeas equivalent = A**：最小端口，仅移植本轮实际调用的 H 与初态构造器 + 5 点 <1e-10 等价测试；benchmark/random 等其余子模块本轮不复用。

## Assumptions

1. `doc/plan/theory/H.md` 与 `doc/plan/experiment/01–04` 为本轮权威口径且自洽。
2. 上一轮冻结的网格/代表点/q 网格/拟合约定延续有效（除非 doc 另有规定）。
3. 本轮只研究 OBC SSH-XXZ。
4. 04 目标仍是 ideal state-preparation capability。
5. 实现架构与算法选择留给 `/speckit.plan`。
