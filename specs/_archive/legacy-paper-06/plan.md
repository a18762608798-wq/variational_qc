# Writing Plan: paper-06 实验结果展示

## 1. 写作思路

- 先 `SEC-001`（比较方法与归一化口径，可全写；误差棒一句话带过）。
- `SEC-002` 只写框架：四个图空位 + 结果论述冻结（`CLM-002/003` 待 D08 图）。
- 中英双版同步；在现有 `main.tex`（paper-05 内容之后、`\appendix` 之前）续写。

## 2. 章节与 Skill 映射

- `SEC-001`：`paper-writing-section`（methods/results），输入大纲比较协议 + exp06 定义
  （`CLM-001`，R3 硬件谱系背景 5 篇已落位，无新主张）
- `SEC-002`：`paper-writing-section`（results），框架先行，四空位 + 冻结论述
- 图位：`paper-figure-layout`（`FIG-001` D08a–d 合一 2×2 `figure*` 空位预排，图到后填图）
- 引用：R3 硬件谱系背景（`colless2018robust`、`hempel2018quantum`、`kandala2017hardware`、
  `google2020hartree`、`yu2023simulating`，均已 hunt + verify + bind，无新主张）
- 格式：`paper-latex-formatting`（沿用 PRA 模板，无新宏包需求）
- 打分 / 改文：`paper-self-review` / `paper-revision`

## 3. LaTeX 工程结构

- 沿用 `docs/paper/`（`main.tex` + `main-zh.tex` + `references.bib`）。
- 图到后从 `figs/exp06/` 复制进 `figures/`（原名保留），空位届时填图。
- 沿用 `docs/paper/`（`main.tex` + `main-zh.tex` + `references.bib`；`sections/` 已拆分，见 paper-07 T002）。

## 4. 编译与评审方案

- `VAL-004`：agent 直接 `latexmk` 双版编译（空位用 `\fbox{TODO}` 占位框，保证可编译）。
- `VAL-001/002/003`：`paper-self-review` 打分覆盖（口径节齐、空位存在、冻结主张无陈述句、无新增未验证引用）。
- 打分不达标 → `paper-revision` 改 → 重编译 → 再打分。

## 5. 写作层未解决问题 / 延后工作

- `GAP-001-DATA`（D08 图）转 exp06 跟踪，不在本 feature 解决。
