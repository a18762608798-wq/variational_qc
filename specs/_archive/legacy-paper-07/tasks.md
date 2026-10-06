# Tasks: paper-07 收尾（摘要/结论/统稿）

**Feature:** paper-07

Writing 任务来自 `plan.md`。

Review 任务落实打分与改文循环，
并覆盖 spec 中对应的 `VAL-*`。

不得在 tasks 阶段引入新的主张或证据绑定。

执行顺序注意：T003（hunt）必须在 T004（写 SEC-003）之前完成。

## Assemble

- [x] T001 [paper-assembly] 核对 paper-01~06 收敛状态，确认本 feature 输入齐套，输出检查结论

## Restructure

- [x] T002 拆 `sections/*.tex`（一节一文件，中英双版；`main.tex` 只剩导言 + `\input`），拆后编译验证交叉引用

## Cite

- [x] T003 [CIT-001] `paper-zotero-hunter` hunt（双方向各 1–2 篇）/ verify / bind；CIT-002 复用确认

## Write

- [x] T004 [SEC-003] `paper-related-work` 写 Related Work 并入引言（双方向对比，`CIT-001` 落位）
- [x] T005 [SEC-001] `paper-writing-section` 重写摘要（中英双版，覆盖全篇）
- [x] T006 [SEC-002] `paper-writing-section` 写结论（中英双版，只复述）
- [x] T007 [SEC-004] 全篇统稿（术语、符号、时态、交叉引用）

## Format

- [x] T008 `paper-latex-formatting` PRA 投前检查收官（中英双版）

## Review

- [x] T009 [VAL-004] agent 直接 `latexmk` 双版编译通过，交叉引用干净
- [x] T010 [VAL-001/002/003] `paper-self-review` 打分达标
- [x] T011 `paper-revision` 消灭全部审稿意见（如有），重编译再打分直到通过

## Follow-up（按需）

- [ ] D07/D08 图到后由 paper-04/06 各自填图（不在此 feature）
- [x] R6 节重组后 SEC-004 复查（8 节标题/编号/交叉引用 + 双版编译干净，GAP-001 关闭确认）
