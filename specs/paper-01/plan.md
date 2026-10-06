# Writing Plan: paper-01 Methods

## 1. 写作思路

- 组织顺序参考“方法先行、结果集中报告”的论文结构：先写模型、诊断量、态制备和硬件测量机制；具体 D07/D08 排名、趋势和实验比较放入 Results and Discussion；D02a/b/c 放入 Appendix。
- 写作顺序：`SEC-001` 模型与有限尺寸分析协议 → `SEC-002` 拓扑物理量 → `SEC-003` 变分态制备 → `SEC-004` 优质比特筛选协议 → `SEC-005` 读出误差缓解。
- 数据流：H/topological/gap theory 文档与 D01 的定义支撑 `SEC-001`；D03/D04 支撑 `SEC-002`；D05/D06 和 psi0/ansatz 支撑 `SEC-003`；premium_qubits 与 exp05 定义支撑 `SEC-004`；readout_mitigation 与 exp06 PRE-006 支撑 `SEC-005`。
- D02a/b/c 的具体曲线、交点和拟合结论不在本 feature 写入，由 Appendix feature 消费；D07a/b/c 的具体排名不在本 feature 写入，由 Results feature 消费。
- 缺件策略：D07/D08/D02 结果缺失只冻结对应结果 feature 的图位和结论，不阻塞本 Methods feature。若将来结果到位但解释不能由数据直接推出，询问用户并把回答标为用户确认的推测，不自行补写。

## 2. 章节与 Skill 映射

- `SEC-001`（模型与有限尺寸方法）：`paper-writing-section`（methods），输入 H、topological_op、gap 的方法定义和 D01 参数区域；不写 D02 具体结果。
- `SEC-002`（拓扑物理量）：`paper-writing-section`（methods），输入 D03/D04 和 `topological_op.md`，说明各诊断量的定义和测量选择；不写后续真机趋势结论。
- `SEC-003`（变分态制备）：`paper-writing-section`（methods），输入 D05/D06、`psi0.md`、`ansatz.md`，说明初态、orbit 拟设和起点/终点协议。
- `SEC-004`（优质比特筛选）：`paper-writing-section`（methods），输入 `premium_qubits.md` 和 exp05 定义，说明基准电路、评分和比较口径；D07 排名结果由 Results feature 写。
- `SEC-005`（读出误差缓解）：`paper-writing-section`（methods），输入 `readout_mitigation.md` 和 exp06 `PRE-006`，说明矩阵标定、求逆、非负约束和重归一流程。
- 图位：`paper-figure-layout` 只处理 Methods 中保留的 D01、D03、D04、D05、D06 图；D02 图由 Appendix，D07/D08 图由 Results 负责。
- 引用：`paper-zotero-hunter` 处理 `CIT-001..006` 的 harvest / verify / bind；Related Work 在 Closing 的 Introduction 模式中处理。
- 格式：`paper-latex-formatting` 负责 PRA 版式和引用/图位检查。
- 打分/修改：`paper-self-review` / `paper-revision` 只检查本 feature 的方法边界和一致性，不把缺失的结果结论当作 Methods 缺陷。

## 3. LaTeX 工程结构

- 论文目录继续使用 `docs/paper/`，沿用现有 `main.tex`、`main-zh.tex`、`sections/`、`references.bib` 和 `figures/`。
- 本试点只规划方法内容，不复制、移动或改写正文图文件。
- Methods 相关正文按现有 `sections/` 组织；具体文件拆分由 implement 阶段根据现有正文结构决定。
- 上游图不重新生成；已确定的 D01 单栏、D04 跨栏 `figure*`、D05/D06 版式决策直接写入正式实现任务。
- `references.bib` 继续由 `paper-zotero-hunter` 维护，禁止手写未经验证条目。

## 4. 编译与评审方案

- `VAL-001`：检查五个 Methods 子节是否齐套，方法机制与理论文档一致。
- `VAL-002`：只检查 Methods 负责的图位；D02/D07/D08 结果图由对应 feature 验收。
- `VAL-003`：检查 Methods 主张都有理论文档、实验定义或方法协议证据；不把冻结的结果主张写成事实。
- `VAL-004`：检查 `CIT-001..006` 已 verify 且 key 齐全。
- `VAL-005`：agent 直接执行 LaTeX 编译和未定义引用检查；缺失的结果图保留空位，不阻塞无关 Methods 段落。
- 评审不达标时由 `paper-revision` 修正方法边界、术语和证据引用，再重新编译和检查。

## 5. 写作层未解决问题 / 延后工作

- D02a/b/c 的具体有限尺寸结果及其解释延后到 Appendix feature。
- D07a/b/c 的具体排名、D08 的实验趋势和比较结论延后到 Results and Discussion feature。
- 若结果到位后存在不能由图面直接推出的解释，记录 `GAP-INTERP [needs-user]` 并询问用户；这不阻塞本 Methods 试点。
