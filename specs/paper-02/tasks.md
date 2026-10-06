# Tasks: paper-02 Results and Discussion

**Feature:** paper-02

Writing 任务来自 `plan.md`；本文件不新增主张或证据绑定。

## Assemble

- [x] T001 [paper-assembly] 核对 exp04（S06/D08 模拟层）、exp05（D07/S04 定义与落盘状态）、exp06（D08 真机层、`p*` 规则、叠放归一化）存在；确认 D07/D08 图缺件，输出缺件表（`GAP-001/002-DATA`）。
- [x] T002 [paper-assembly] 确认筛选协议、缓解机制不进入本 feature（归 paper-01）；确认 S04 取值跟随最新落盘。

## Write

- [x] T003 [SEC-001] [paper-writing-section] 写比较协议与归一化口径：叠放规则、各自 `0–1` 归一化、误差棒一句话；不展开 multinomial 公式。
- [x] T004 [SEC-002] [paper-writing-section] 写 D07 排名节框架与冻结论述；图位留空，不写具体比特表。
- [x] T005 [SEC-003] [paper-writing-section] 写 D08 比较节框架与冻结论述；图位留空，不写趋势结论。
- [x] T006 [FIG-001/002] [paper-figure-layout] 按版式接入 D07/D08 空位标记（三图一起呈现；四占位 2×2）。

## Cite

- [x] T007 [CIT-001] 复用 R3 硬件谱系与 paper-01 已验证条目并核对 `references.bib`；按需复用，不新增 hunt，不新增未经 verify 的 key。

## Format

- [x] T008 [paper-latex-formatting] 检查 Results 章节 PRA 版式、公式、图 caption、符号和交叉引用；不因缺图改写已冻结主张。

## Review

- [x] T009 [VAL-001] 检查 `SEC-001` 协议节齐套，与大纲/exp06 一致。
- [x] T010 [VAL-002] 检查 `FIG-001/002` 空位标记存在。
- [x] T011 [VAL-003] 检查 `CLM-001` 有据；`CLM-002..006` 冻结，无事实语气。
- [x] T012 [VAL-004] agent 直接执行编译和未定义引用检查。
- [x] T013 [paper-self-review] 按本 feature 边界打分；不把 D07/D08 缺图当 Methods 缺陷。
- [x] T014 [paper-revision] 清理评审指出的问题，重新执行 T009–T013。

## Follow-up

- [ ] T015 [Results] D07/D08 图到后填图并解冻 `CLM-002..006`，按 `POST-002` 复算 `p*`，S04 取最新落盘；届时走返工流程更新本 feature。
