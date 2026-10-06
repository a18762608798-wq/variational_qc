# Tasks: paper-03 Closing

**Feature:** paper-03

Writing 任务来自 `plan.md`。

Review 任务落实打分与改文循环，并覆盖 spec 中对应的 `VAL-*`。

不得在 tasks 阶段引入新的主张或证据绑定。

## Assemble

- [x] T001 [paper-assembly] 核对 paper-01/02 当前正文、`docs/paper-outline.md`、既有图标签和冻结边界；确认本 feature 无新增 Dxx 图位、无新增数据缺件，并输出输入清单。
- [x] T002 [paper-assembly] 核对 paper-02 D07/D08 Follow-up 状态，明确摘要和结论只消费结果框架，不消费具体排名、趋势、数值或真机-模拟机一致程度。

## Write

- [x] T003 [SEC-001] [paper-writing-section] 重写英文摘要，覆盖研究问题、模型、物理量、变分电路、真机方法、比较协议和结果框架；完成条件是与 `CLM-001` 一致且不预支 D07/D08 冻结结论。
- [x] T004 [SEC-001] [paper-writing-section] 重写中文摘要，使其与英文摘要在研究对象、方法范围、结果边界和术语上对应；完成条件是中英双版均不引入新主张。
- [x] T005 [SEC-002] [paper-writing-section] 撰写英文结论，复述已建立的方法、协议、可复现性和结果框架；完成条件是符合 `CLM-002`，不写冻结的具体排名、趋势或数值。
- [x] T006 [SEC-002] [paper-writing-section] 撰写中文结论并与英文版逐项对齐；完成条件是只复述已有证据，不扩大结论。
- [x] T007 [SEC-003] [paper-writing-section] 将 Related Work 并入英文 Introduction，按 `CIT-001`..`CIT-005` 组织真机拓扑、变分算法、结构因子、string 长程关联、稳定子/读出驱动的优质比特选择、读出误差缓解、有限尺寸能隙与外推背景；完成条件是背景文献只用于定位和方法背景，不替代本文结果证据。
- [x] T008 [SEC-003] [paper-writing-section] 将对应 Related Work 段落并入中文引言，并与英文版的文献轴、定位关系和边界一致；完成条件是无独立 PRA Related Work 章节。
- [x] T009 [SEC-004] [paper-writing-section] 统稿中英全文的术语、符号、时态、章节边界、摘要/结论措辞和中英对应关系；完成条件是 paper-01/02 实验正文边界不被改变。

## Cite

- [x] T010 [CIT-001..006] [paper-zotero-hunter] 从已核验 Zotero 条目 harvest 并绑定 Related Work 和结论所需引用，覆盖真机拓扑/变分算法、结构因子与 string、优质比特选择、读出误差缓解、有限尺寸能隙与外推及已有结果；完成条件是无未经核验的新引用、无手写 `references.bib` 条目。

## Format

- [x] T011 [paper-latex-formatting] 按 PRA 工程检查摘要、Introduction、结论、既有图标签/引用、交叉引用和 bibliography；完成条件是无新增图位、无空章节、无与 paper-01/02 职责重叠的正文。

## Review

- [ ] T012 [VAL-001] 检查 `SEC-001`..`SEC-004` 四节均已成文，Related Work 已并入 Introduction，且中英双版均存在；记录检查结果。
- [ ] T013 [VAL-002] 回查 `CLM-001`..`CLM-003` 的证据绑定和措辞边界；确认摘要、结论与 Related Work 没有新增主张，且没有预支 D07/D08 冻结结果。
- [ ] T014 [VAL-003] 逐项检查 `CIT-001`..`CIT-006` 的引用存在、来源已核验、用途与对应文献方向匹配；记录未绑定或不匹配项并清零。
- [x] T015 [VAL-004] agent 直接编译英文和中文论文，检查未定义引用、未定义交叉引用、缺图、编译错误和 `git diff --check`；完成条件是中英双版编译通过且检查项清零。
- [ ] T016 [paper-self-review] 按 `paper-self-review` 对 paper-03 范围进行多 persona 打分，覆盖摘要、结论、Related Work 定位、边界纪律和 presentation；完成条件是形成评审结果并明确是否需要 revision。
- [x] T017 [paper-revision] 若 T016 发现可修复问题，按评审意见修改正文并重新执行 T012–T016；完成条件是适用意见清零、重新编译通过、引用和边界复核通过；若无问题则记录无需 revision。

## Follow-up

- [ ] T018 [Results] D07/D08 图和具体结果在 paper-02 返工后，按变更内容复核并同步更新摘要与结论；该任务不阻塞当前 paper-03 收敛。
