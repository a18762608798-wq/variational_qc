# Tasks: paper-04 真机优质比特选择方法介绍

**Feature:** paper-04

Writing 任务来自 `plan.md`。

Review 任务落实打分与改文循环，
并覆盖 spec 中对应的 `VAL-*`。

不得在 tasks 阶段引入新的主张或证据绑定。

## Assemble

- [x] T001 [paper-assembly] 核对 D07 排名数据存在、图缺失，确认 GAP-001 状态，输出检查结论

## Write

- [x] T002 [SEC-001] `paper-writing-section` 写筛选方法（cluster 态/稳定子/打分公式/各自比较，`CIT-001` 落位）
- [x] T003 [SEC-002] `paper-writing-section` 写排名框架（三图空位占位框，芯片百花可写，比特表冻结）
- [x] T004 [FIG-001/002/003] `paper-figure-layout` 空位标记（`\fbox{TODO}` 占位，不引用缺失文件）

## Cite

- [x] T005 [CIT-001] `paper-zotero-hunter` bind（`raussendorf2001oneway` 落位；CIT-002 按需）

## Format

- [x] T006 `paper-latex-formatting` 检查（沿用 PRA 模板，中英双版）

## Review

- [x] T007 [VAL-005] agent 直接 `latexmk` 双版编译通过，引用预检干净
- [x] T008 [VAL-001/002/003] `paper-self-review` 打分达标（方法节齐、空位存在、冻结主张无陈述句）
- [x] T009 [VAL-004] 引用已读确认且 key 齐全
- [x] T010 `paper-revision` 消灭全部审稿意见（如有），重编译再打分直到通过

## Follow-up（按需）

- [ ] D07 图到后填图并解冻 `CLM-002/003/004`（跟踪 exp05）
