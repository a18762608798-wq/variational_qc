# Tasks: paper-02 引入反映拓扑性质的物理量

**Feature:** paper-02

Writing 任务来自 `plan.md`。

Review 任务落实打分与改文循环，
并覆盖 spec 中对应的 `VAL-*`。

不得在 tasks 阶段引入新的主张或证据绑定。

## Assemble

- [x] T001 [paper-assembly] 核对 D03 / D04 数据集与图文件到位，确认零缺件，输出检查结论

## Write

- [x] T002 [SEC-001] `paper-writing-section` 写结构因子与 AFM 标签（D03 三线同图论述，`CIT-001` 落位）
- [x] T003 [SEC-002] `paper-writing-section` 写四联热力图（含重点表述原文落位，`CIT-002` 落位）
- [x] T004 [FIG-001/002] `paper-figure-layout` 组图进文（FIG-001 单图；FIG-002 跨栏 `figure*` minipage 拼 `2×2`，手工标签 (a)–(d)）

## Cite

- [x] T005 [CIT-001/002] `paper-zotero-hunter` bind（`dennijs1989preroughening` 新绑；`elben2020manybody` 复用归档确认；CIT-003 按需）

## Format

- [x] T006 `paper-latex-formatting` 检查（reprint 模板 + minipage 编号 + PRA 投前检查，中英双版）

## Review

- [x] T007 [VAL-005] agent 直接 `latexmk` 双版编译通过，引用/缺图预检干净
- [x] T008 [VAL-001/002/003] `paper-self-review` 打分达标（新增两节、2×2 标签一致、主张皆有证据）
- [x] T009 [VAL-004] 引用已读确认且 key 齐全
- [x] T010 `paper-revision` 消灭全部审稿意见（如有），重编译再打分直到通过

## Follow-up（按需）

- [ ] paper-03 并入时再评估 `sections/*.tex` 拆分
