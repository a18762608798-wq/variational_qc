# Tasks: paper-06 实验结果展示

**Feature:** paper-06

Writing 任务来自 `plan.md`。

Review 任务落实打分与改文循环，
并覆盖 spec 中对应的 `VAL-*`。

不得在 tasks 阶段引入新的主张或证据绑定。

## Assemble

- [x] T001 [paper-assembly] 核对 D08 缺图现状，确认 GAP-001 状态，输出检查结论

## Write

- [x] T002 [SEC-001] `paper-writing-section` 写比较方法与归一化口径（叠放规则、各自归一化、误差棒一句话）
- [x] T003 [SEC-002] `paper-writing-section` 写四图框架（四空位占位框，结果论述冻结）
- [x] T004 [FIG-001] `paper-figure-layout` 空位标记（D08a–d 合一 2×2 `figure*` 预排 + 联合 caption，不引用缺失文件）

## Cite

- [x] T005 新增引用均为已验证背景引用（R3 落位，无新主张）：`colless2018robust`、`hempel2018quantum`、
  `kandala2017hardware`、`google2020hartree`、`yu2023simulating`（硬件谱系段）；确认无未验证 `\cite`

## Format

- [x] T006 `paper-latex-formatting` 检查（沿用 PRA 模板，中英双版）

## Review

- [x] T007 [VAL-004] agent 直接 `latexmk` 双版编译通过，预检干净
- [x] T008 [VAL-001/002/003] `paper-self-review` 打分达标（口径节齐、空位存在、冻结主张无陈述句）
- [x] T009 `paper-revision` 消灭全部审稿意见（如有），重编译再打分直到通过

## Follow-up（按需）

- [ ] D08 图到后填图并解冻 `CLM-002/003`（跟踪 exp06）
