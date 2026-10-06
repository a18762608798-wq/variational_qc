# Tasks: paper-01 模型引入和基本性质

**Feature:** paper-01

Writing 任务来自 `plan.md`。

Review 任务落实打分与改文循环，
并覆盖 spec 中对应的 `VAL-*`。

不得在 tasks 阶段引入新的主张或证据绑定。

## Assemble

- [x] T001 [paper-assembly] 核对 D01 / D02a/b/c 数据集与图文件到位，确认零缺件，输出检查结论

## Write

- [x] T002 [SEC-001] `paper-writing-section` 写模型引入（H 定义、`L=8` 默认声明、`~Z_R` 定义引用，`CIT-001` 占位）
- [x] T003 [SEC-002] `paper-writing-section` 写有限尺寸相图正文（三相说明，`CIT-002` 占位）
- [x] T004 [SEC-003] `paper-writing-section` 写附录能隙（交点 `s=0.5`、小拟合截距 `b=0.05`（以 D02c 图为准，原“截距 0”已随 spec CLM-004 修正）、偏差论述，`CIT-003` 按需占位）
- [x] T005 [FIG-001..004] `paper-figure-layout` 组图进文（FIG-001 正文单栏；FIG-002/003/004 附录独立成图）

## Cite

- [x] T006 [CIT-001/002] `paper-zotero-hunter` harvest / verify / bind（SSH 原始文献、拓扑标记方向；CIT-003 按需）

## Format

- [x] T007 `paper-latex-formatting` 建 `docs/paper/` 骨架（PRA 模板 setup + 复制图文件 + 投前检查）

## Review

- [x] T008 [VAL-005] agent 直接 `latexmk` 编译通过，引用/缺图预检干净
- [x] T009 [VAL-001/002/003] `paper-self-review` 打分达标（章节齐套、图caption一致、主张皆有证据）
- [x] T010 [VAL-004] 引用已读确认且 key 齐全
- [x] T011 `paper-revision` 消灭全部审稿意见（如有），重编译再打分直到通过

## Follow-up（按需）

- [ ] paper-02 并入时评估是否拆 `sections/*.tex`
- [ ] 结论节归 paper-07 统稿（self-review R2 意见，本 feature 不背）
- [x] CIT-003（有限尺寸标度方向）已 hunt + verify + bind（`sandvik2010computational`，R3 落位附录方法注）
