<!-- Sync Impact Report (temporary review scratch, remove before commit)
- Version change: 0.2.0 → 0.3.0 (minor: new principle XII, second Julia cycle)
- Source: user-supplied second-cycle stack/schema directive
- Modified principles: none (I–XI untouched)
- Added sections: Core Principles XII (Julia stack lock, Python core archived read-only, H.md physics pin, schema v2 with III.4 exception, qmeas-reuse pause with baseline cross-check)
- Removed sections: none
- Follow-up TODOs:
  - Cross-check tolerance (Julia vs archived baseline) deferred to /speckit.clarify per XII.4.
  - v1 data deletion requires a converge archive record first (XII.2 gate).
-->

# SSH-XXZ Numerical Project Constitution

本 Constitution 约束 SSH-XXZ 数值计算项目的代码组织、数值正确性、可复现性、数据管理、实验分层与作图流程。

它是**数值项目的工程与科学计算契约，不是论文提纲，也不是具体实验设计**。

具体的系统尺度、扫描网格、代表点、优化器超参数、硬件比特与单个实验输出，由对应 theory/spec/experiment 文件规定；除非属于全项目不变量，否则不得重复冻结在 Constitution 中。

## Core Principles

### I. Physics Specification Is the Source of Truth

1. `theory/` 中的 Hamiltonian、边界条件、初态、ansatz、cost function、observable、对称性约定及辅助算符，是数值实现的物理定义来源。

2. 数值代码 MUST 按 specification 实现物理对象，不得为了实现方便而静默修改公式、边界条件、归一化、参数约定或 sector 定义。

3. 物理 Hamiltonian \(H\) 与任何用于筛选态、sector 或数值辅助的 operator/Hamiltonian MUST 保持为不同对象。除非某个实验 spec 明确另有规定，能量和 variational cost MUST 使用物理 \(H\)。

4. 每个非平凡数值对象 MUST 能追溯到唯一的 authoritative definition。Hamiltonian、observable、ansatz 等数学定义不得在多个模块中各自复制实现。

5. implementation 过程中若发现 specification 存在歧义、冲突或缺失，MUST 停止受影响部分的实现并返回 specification 层澄清；禁止由代码自行"猜测正确物理"。

### II. Numerical Architecture Must Be Modular and One-Way

1. `numerical-code-architecture` skill 一旦提供，其规则即成为本 Constitution 的强制组成部分。

2. reusable physics/numerics、experiment orchestration、data persistence、plotting 与 hardware execution MUST 分层。

3. core numerical functions MUST NOT 依赖 plotting、paper figure 或具体 experiment script。

4. experiment scripts 只负责：读取配置；调用 reusable numerical components；管理扫描/优化流程；保存结果；触发独立 plotting pipeline。experiment scripts MUST NOT 重新实现 Hamiltonian、initial state、ansatz、observable、ED 或 estimator。

5. 已有且与 specification 一致的 `qmeas` 实现 SHOULD 优先复用，可通过 thin adapter 统一接口。若必须重新实现相同功能，MUST 做数值等价性测试。

6. ideal simulation、finite-shot simulation 与 hardware execution MUST 是不同 execution layer。

7. hardware coupling map、initial layout、transpilation 与 device-specific routing MUST NOT 泄漏到 ideal statevector optimization，除非某个专门实验明确研究这些因素。

8. plotting MUST 读取已经保存的 numerical results。绘图函数不得以隐藏副作用重新运行 ED、VQE 或其他昂贵物理计算。

9. production run 禁止依赖 notebook 隐式状态、global mutable state 或未记录的交互式变量。所有决定结果的输入 MUST 显式且可序列化。

### III. Reproducibility and Provenance Are Mandatory

1. 每个 numerical run MUST 能由 saved configuration、code version、environment/dependency information 与 recorded random seeds 重新构造。

2. 所有 stochastic procedure MUST 使用显式 seed，并保存 seed。

3. 每个 result dataset MUST 至少能够识别：experiment/stage、system size、physical parameters、ansatz depth（若适用）、initial-state branch（若适用）、optimizer/backend、random seed、code/software version。

4. raw numerical results MUST 永久保留。

5. normalization、fit、aggregation、smoothing、interpolation、rescaling 以及 figure-specific transformation MUST 与 raw data 分离，并可由 raw data 重现。

6. expensive computation MUST 支持 checkpoint/resume。已成功完成的 parameter point 不应因单点失败而被迫全部重新计算。

7. 相同 configuration 的重复执行 MUST 是 idempotent：可以读取已经验证的 cache；不得静默覆盖 incompatible result；不得把不同配置产生的数据写成同一结果。

8. 数据格式 MUST machine-readable，并具有稳定 schema。schema 的破坏性变化 MUST 有显式 version 或 migration。

### IV. Correctness Comes Before Scale or Speed

1. large scan、长时间 optimization 或 hardware run 开始前，相关 primitive MUST 先通过 small-system correctness tests。

2. 根据模块适用范围，tests MUST 覆盖：Hamiltonian bond placement；OBC 行为；analytically known limits；initial-state preparation；symmetry preservation；ansatz parameter count；ansatz layer/sub-layer ordering；observable evaluation；exact-reference energies；shot estimators。

3. production sparse/scalable ED 在投入大尺寸计算前，MUST 在小 \(L\) 上与 independent dense calculation 或可信 reference 交叉验证。

4. exact reference 与 variational result 对应同一个 physical problem 时，MUST 检查基本 variational invariant，例如

$$
E_{\rm var}\ge E_0
$$

在数值容差内成立。

5. 当 ansatz 定义保证 \(p-1\) 层解可以通过新增零参数严格嵌入 \(p\) 层时，实现 MUST 对这一性质进行测试；warm start 与 depth comparison MUST 保持这一 nesting property。

6. ansatz 所依赖的 symmetry preservation 不得只通过代码结构假设。MUST 在 representative small systems 上进行 numerical verification。

7. correctness implementation 与 optimized implementation SHOULD 分离。任何性能优化版本 MUST 对 reference implementation 做 regression test。

### V. Experiments Must Introduce Complexity in Controlled Layers

整个项目在概念上按以下层次递进：

$$
\text{global exact physics}
\rightarrow
\text{fixed-size exact reference}
\rightarrow
\text{ideal variational preparation}
\rightarrow
\text{finite-shot sampling}
\rightarrow
\text{hardware validation}.
$$

具体编号、参数和输出由 experiment specs 决定。

1. exact-reference data MUST 独立于 variational results 计算，并作为 downstream ground truth 复用。

2. ideal variational preparation MUST 排除 shot noise、hardware noise 与 hardware routing，除非某个 dedicated experiment 明确研究这些效应。

3. 当实验目的在于隔离 sampling error 或 hardware error 时，finite-shot/hardware stage SHOULD 使用对应 ideal optimization 已得到的 frozen parameters，而不是无意中重新引入 optimizer difference。

4. 每一层 MUST 保存足够 diagnostic data，使异常能够区分为：physics/specification error；ansatz expressibility error；optimizer failure；finite-shot sampling error；hardware/device error。

5. 0–1 normalization 等 presentation transformation 默认属于 post-processing，而不是 physics computation。除非后续 spec 明确改变这一点，raw observable MUST 始终保留。

### VI. Data and Result Contracts Must Be Explicit

1. 每个 experiment 在 implementation 前 MUST 定义 required inputs、canonical outputs 与 completion criteria。

2. parameter scan MUST 保存实际计算的 parameter coordinates。绘图不得在已有明确坐标时仅通过 array index 猜测 \(s,\delta,q\) 等坐标。

3. optimization result MUST 至少保存 final parameters 与 final objective value；并 SHOULD 保存 convergence status、evaluation count、restart identity、initial parameters、selected initial-state branch 与 relevant optimizer diagnostics。

4. exact、ideal variational、finite-shot 与 hardware result MUST 在数据 schema 中具有明确 source/backend identity。

5. 不同来源的数据不得通过文件名或数组位置隐式区分。

6. failed point MUST 显式记录 failure state 与 diagnostics。禁止静默删除、用零替代、用 NaN 但不保存失败原因、或自动换算法后假装原算法成功。

### VII. Figures Are Reproducible Products of Saved Data

1. `pra-paper-figures` skill 一旦提供，其规则即成为 publication figure 的强制规范，并作为本 Constitution 的组成部分。

2. diagnostic figures 与 publication figures MUST 视为不同产品。

3. diagnostic plots MAY 为 debug 和阶段性检查保留更多信息；publication figures MUST 同时满足 experiment specification 与 `pra-paper-figures`。

4. 每张 figure MUST 能通过 saved numerical data 与 deterministic plotting entry point 完整重现。

5. 禁止手工修改 figure 中承载 numerical meaning 的内容。

6. normalization、clipping、interpolation、smoothing、offset、rescaling 等 transformation MUST 在 plotting/post-processing code 中显式出现。

7. 不得为了获得"更好看"的图而修改 raw numerical data。

8. final paper figure 使用的 source data MUST 保留，并能追溯到对应 numerical run。

9. plotting pipeline MUST 与 expensive computation 解耦；修改字体、layout、legend 或 panel arrangement 不应要求重新运行物理计算。

### VIII. Scalable Numerical Methods Are Required

1. production exact diagonalization MUST 使用与系统规模相适应的 sparse/operator-based representation。

2. dense full-Hilbert-space matrix 只允许用于小系统 correctness verification，或明确证明 memory/time 安全的特殊计算。

3. 不得仅因实现简单而在 production scale 构造不必要的 dense matrix。

4. 被多个 experiment 重复使用的昂贵结果 SHOULD 保存为 canonical data product 并复用。

5. vectorization、sparse methods、symmetry reduction、parallelism 与 caching MAY 用于性能优化，但前提是：correctness 已建立；不改变 specification 中定义的 physical problem；optimized result 与 reference result 已做 regression check。

6. large scan 启动前 SHOULD 用 representative subset 估计 runtime、memory、output size、checkpoint frequency 与 restart strategy。

### IX. Fail Loudly, Log Enough to Debug

1. 以下情况 MUST 显式报错或记录 failure state：invalid physical parameters；incompatible dimensions；malformed parameter vector；missing required data；eigensolver failure；optimizer failure；invalid observable evaluation。

2. 禁止 silent fallback 到不同的 boundary condition、initial state、symmetry sector、optimizer、backend、parameter convention 或 numerical algorithm。

3. long-running experiment MUST 提供 parameter-point level progress information。

4. 单点失败后，日志 MUST 足以定位具体 configuration，而无需重跑完整 scan 才能知道哪里出错。

5. 任何可能改变 scientific interpretation 的 warning MUST 写入 run metadata/log，而不能只打印到 terminal。

### X. SpecKit Workflow and Governance

项目固定按照以下流程推进：

$$
\boxed{
/speckit.constitution
\rightarrow
/speckit.specify
\rightarrow
/speckit.clarify
\rightarrow
/speckit.plan
\rightarrow
/speckit.checklist
\rightarrow
/speckit.tasks
\rightarrow
/speckit.analyze
\rightarrow
/speckit.implement
\rightarrow
/speckit.converge
}
$$

1. 后续 stage MAY 补充实现细节，但 MUST NOT 静默改变由前序 authoritative stage 已经确定的决定。

2. implementation 中若发现必须改变 physics/specification，MUST 回到拥有该决定的 specification 层修改，而不是只修改代码。

3. `/speckit.plan`、`/speckit.checklist`、`/speckit.tasks` 和 implementation 前的 analysis MUST 包含 **Constitution Check**，至少检查：physics fidelity；architecture；numerical correctness；reproducibility；data provenance；testing；figure reproducibility（若相关）。

4. 权责划分：Constitution 负责项目级工程与科学计算规则；theory files 负责物理定义；experiment specs 负责具体实验选择；`numerical-code-architecture` 负责代码架构具体规范；`pra-paper-figures` 负责 publication figure 具体规范。

5. 若发生冲突：explicit current user decision 与已确认 physical definition 优先；其余情况下，更具体的 binding rule 优先于一般规则；不得自行选择方便实现的一方而不报告冲突。

6. Constitution 修改规则与版本政策见下文 Governance；不允许没有明确 scientific/engineering need 的复杂化。

### XI. Initial Implementation Scope Is Experiments 01–04

当前 SpecKit cycle 的 implementation scope **仅包含实验 01–04**。

当前阶段依次实现：

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

具体物理参数、扫描范围、输出量与优化规则由对应 experiment specification 决定。

1. In scope：公共 SSH-XXZ Hamiltonian 与相关基础物理对象；exact diagonalization 所需数值基础；01 的 phase diagram 与 finite-size calculation；02 的 \(S(q)\)、\(S(\pi)\)、\(O_{\rm str}\)、\(Q\)、\(\tilde Z_{\mathcal R}\)；03 的 \(L=8\) exact reference；initial-state preparation；orbit ansatz；variational cost；04 的 ideal/noiseless variational optimization；01–04 所需的数据保存、checkpoint、tests、diagnostic plots 与 PRA publication figures。

2. 当前阶段 MUST NOT 提前实现：finite-shot Aer experiment；hardware execution；physical-qubit selection；coupling map / initial layout；hardware transpilation / routing；measurement mitigation；hardware noise mitigation；hardware-specific normalization；hardware VQE；实验 05 及之后的 pipeline。

3. 允许为未来阶段保留清晰的扩展边界，但 MUST NOT 为尚未进入 scope 的实验建立 speculative framework、generic backend abstraction 或 hardware execution architecture。

4. 实验 01–04 完成并通过 `/speckit.converge` 后，再开启新的 specification cycle 扩展后续实验。

### XII. Second-Cycle Compute Stack Is Julia

本轮（Julia cycle）主计算栈锁定 Julia；`src/ssh_xxz` 下 Python 核心封存为只读——不得修改，只能作为对照基线读取。

1. 物理口径以 `doc/plan/theory/H.md` 为准（条目 I 在本轮的具体化；冲突时更具体的 binding rule 优先）。

2. 数据 schema 升为 `exp01-04/v2`；旧 v1 数据在 converge 记录封存后可删。此条为对 III.4（raw 永久保留）的本轮例外，除此之外 III 全文仍然有效。

3. v1 删除后，仅保留 5 点等价子集定义与解析态 $+1/-1/0$ 作为交叉验证锚点（grid-01-02 §5 五点；trivial $+1$、topological $-1$、AFM GHZ $0$）。

4. II.5 qmeas 复用本轮暂停；改为 Julia 新栈 vs 封存 Python 基线的数值对照，对照容差交 `/speckit.clarify` 确定。

5. 其余 I–XI 不动；本条仅约束本轮计算栈与数据代际，不改变 XI 的实验 scope 锁。

## Scope Boundaries

本 Constitution 只规定项目级工程与科学计算规则。系统尺度、扫描网格、代表点、优化器超参数、硬件比特与单个实验输出由 theory/spec/experiment 文件规定，不得重复冻结在本 Constitution 中，除非属于全项目不变量。

## Project Objective

本项目的目标是：

$$
\boxed{
\text{correct}
+
\text{inspectable}
+
\text{reproducible}
+
\text{maintainable numerical evidence}
}
$$

而不是最大化 framework complexity。

## Governance

1. 本 Constitution 取代其他一般性工程实践中与之冲突的部分；已确认的 physical definition 与 explicit current user decision 优先。

2. 修正 MUST 有明确理由并更新版本号：breaking governance change → major；新原则或实质性扩展 → minor；wording/clarification → patch。

3. 所有 plan/checklist/tasks 及 implementation 前 analysis MUST 执行 Constitution Check；所有 PR/review MUST 验证合规性；复杂度 MUST 被论证为必要。

4. 冲突解决：explicit current user decision 与已确认 physical definition 优先；其余情况下更具体的 binding rule 优先；禁止不报告冲突而选择易实现的一方。

**Version**: 0.3.0 | **Ratified**: 2026-09-30 | **Last Amended**: 2026-09-30
