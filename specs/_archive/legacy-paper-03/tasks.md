# Tasks: paper-03 变分电路介绍

**Feature:** paper-03

Writing 任务来自 `plan.md`。

Review 任务落实打分与改文循环，
并覆盖 spec 中对应的 `VAL-*`。

不得在 tasks 阶段引入新的主张或证据绑定。

## Assemble

- [x] T001 [paper-assembly] 核对 D05 / D06a–c 数据与图文件到位，确认零缺件，输出检查结论

## Write

- [x] T002 [SEC-001] `paper-writing-section` 写起点终点示意（三对坐标逐对列出，同相说明）
- [x] T003 [SEC-002] `paper-writing-section` 写变分电路结构（初态 + orbit 规则，`CIT-001` 落位）
- [x] T004 [FIG-001/002] `paper-figure-layout` 组图进文（FIG-001 单图；FIG-002 D06a–c 三独立单栏散放，共享 FIG.5，(a) 详写）

## Cite

- [x] T005 [CIT-001] `paper-zotero-hunter` bind（`peruzzo2014variational` 备 bib 落位；CIT-002 按需）

## Format

- [x] T006 `paper-latex-formatting` 检查（沿用 PRA 模板，中英双版）

## Review

- [x] T007 [VAL-005] agent 直接 `latexmk` 双版编译通过，引用/缺图预检干净
- [x] T008 [VAL-001/002/003] `paper-self-review` 打分达标
- [x] T009 [VAL-004] 引用已读确认且 key 齐全
- [x] T010 `paper-revision` 消灭全部审稿意见（如有），重编译再打分直到通过

## Follow-up（按需）

- [ ] paper-04 并入时再评估 `sections/*.tex` 拆分
