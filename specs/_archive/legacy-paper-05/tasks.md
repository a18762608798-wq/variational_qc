# Tasks: paper-05 真机读出误差缓解介绍

**Feature:** paper-05

Writing 任务来自 `plan.md`。

Review 任务落实打分与改文循环，
并覆盖 spec 中对应的 `VAL-*`。

不得在 tasks 阶段引入新的主张或证据绑定。

## Assemble

- [x] T001 [paper-assembly] 核对方法文档与 exp06 定义齐全，确认零缺件，输出检查结论

## Write

- [x] T002 [SEC-001] `paper-writing-section` 写读出误差缓解（矩阵定义 + 求逆矫正 + 非负约束 + 代价，`CIT-001` 落位）

## Cite

- [x] T003 [CIT-001] `paper-zotero-hunter` bind（`bravyi2021mitigating` 备 bib 落位）

## Format

- [x] T004 `paper-latex-formatting` 检查（沿用 PRA 模板，中英双版）

## Review

- [x] T005 [VAL-003] agent 直接 `latexmk` 双版编译通过，引用预检干净
- [x] T006 [VAL-001/002/004] `paper-self-review` 打分达标（方法节齐、主张皆有证据、引用确认）
- [x] T007 `paper-revision` 消灭全部审稿意见（如有），重编译再打分直到通过
