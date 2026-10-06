# Tasks: paper-01 Methods

**Feature:** paper-01

Writing 任务来自 `plan.md`；本文件不新增主张或证据绑定。

## Assemble

- [x] T001 [paper-assembly] 核对 H、topological_op、gap、psi0、ansatz、premium_qubits、readout_mitigation 及 exp01/02/04/05/06 定义是否存在，列出 Methods 可用输入。
- [x] T002 [paper-assembly] 确认 D02a/b/c、D07a/b/c、D08 的结果结论不进入本 Methods feature；分别登记 Appendix/Results 的消费边界和缺件状态。

## Write

- [x] T003 [SEC-001] [paper-writing-section] 写模型与有限尺寸分析协议：SSH H、默认 `L=8`、D01 参数区域和 D02 分析方法；不写 D02 具体曲线/拟合结论。
- [x] T004 [SEC-002] [paper-writing-section] 写 `S(q)`、`S(π)`、string、`Q`、`~Z_R` 的定义、相诊断作用和真机可测量量选择；不写结果趋势结论。
- [x] T005 [SEC-003] [paper-writing-section] 写三相初态、D05 起点/终点协议、orbit 拟设和 D06a/b/c 结构。
- [x] T006 [SEC-004] [paper-writing-section] 写优质比特筛选协议、基准电路、评分公式和 8 链/10 环独立比较口径；不写 D07 具体排名。
- [x] T007 [SEC-005] [paper-writing-section] 写读出误差模型、逐比特标定、求逆、非负约束、重归一和标定代价。
- [x] T008 [FIG-001, FIG-005..008] [paper-figure-layout] 按已确定版式将 Methods 负责的 D01、D03、D04、D05、D06 图位接入；D02/D07/D08 不在本任务处理。

## Cite

- [x] T009 [CIT-001, CIT-002, CIT-003, CIT-004, CIT-005, CIT-006] [paper-zotero-hunter] harvest / verify / bind 方法所需文献；复用已验证条目时核对 `references.bib`，不新增未经 verify 的 key。

## Format

- [x] T010 [paper-latex-formatting] 检查 Methods 章节的 PRA 版式、公式、图 caption、符号和交叉引用；不因缺少结果图改写 Methods 主张。

## Review

- [x] T011 [VAL-001] 检查五个 Methods 子节齐套，方法机制与上游理论/实验定义一致。
- [x] T012 [VAL-002] 检查 Methods 负责的图位存在、版式和 caption 正确；确认 D02/D07/D08 已移交对应 feature。
- [x] T013 [VAL-003] 检查每条 Methods 主张均有证据，冻结的结果主张没有被写成事实语气。
- [x] T014 [VAL-004] 检查引用已经 verify，`references.bib` key 齐全。
- [x] T015 [VAL-005] agent 直接执行编译和未定义引用检查；结果缺件只保留空位，不阻塞无关 Methods 内容。
- [x] T016 [paper-self-review] 对本 Methods feature 做边界、一致性和证据完整性检查；自动 PDF 评分因环境缺少 PyMuPDF/pypdf 未执行，未伪造分数，结果记录在 `review.md`。
- [x] T017 [paper-revision] 本轮人工审阅未发现需要修订的方法边界、术语、符号或引用问题；无需启动 revision，后续自动评分可用时再复核。

## Follow-up

- [ ] T018 [Appendix] 新建 Appendix feature 后消费 D02a/b/c，写具体有限尺寸曲线、交点和拟合结论；缺解释时询问用户并记录 `GAP-INTERP`。
- [ ] T019 [Results] 新建 Results and Discussion feature 后消费 D07a/b/c、D08，写具体排名、趋势、比较和实验结论；缺件默认冻结，不阻塞 Methods。
