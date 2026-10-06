# Writing Plan: [FEATURE NAME]

## 1. 写作思路

整体准备怎么把 spec 写成论文。

包括：

- 章节顺序与依赖（先方法结果，后引言结论，还是按 venue 常规顺序）
- 上游产物到章节的数据流（哪个 `D##` 进哪节、哪张图）
- 缺件章节的先行 / 冻结安排（`GAP-DATA` 留空位先行，`GAP-INTERP` 等用户推测）

需要关联 spec 中的约束时引用其 ID，不重复定义 Contract。

## 2. 章节与 Skill 映射

说明每个 `SEC-###` 由哪个 skill 执笔：

Methods 先说明可复现的方法机制，Results and Discussion 再消费结果
数据产品并写具体趋势、排名和比较结论；支持性有限尺寸诊断可放入 Appendix。

例如：

- `SEC-001`（Methods）：`paper-writing-section`（methods），输入 `D##` + 上游 `P##`
- `SEC-002`（Results）：`paper-writing-section`（results），输入 `D##` + `figs/...`
- Related Work 段落：`paper-writing-section`（Related Work 模式；PRA 并入 Introduction，不单列）
- 图位：`paper-figure-layout`（`FIG-###` → 单栏 / `figure*` / 并排）
- 引用：`paper-zotero-hunter`（`CIT-###` → harvest / verify / bind）
- 格式：`paper-latex-formatting`（venue 模板 + `pra-notes.md` / `pra-figures.md`）
- 打分 / 改文：`paper-self-review` / `paper-revision`

## 3. LaTeX 工程结构

- 论文目录：`docs/paper/`（`main.tex` 英文投稿版 + `main-zh.tex` 中文归档版，
  共用 `references.bib` 与 `figures/`；中文版必须 xelatex 编译）
- 上游图文件引用方式：复制 vs 符号链接进 `figures/`（二选一并写理由）
- 主文件结构：单文件 `main.tex` 还是 `sections/*.tex` + `\input`
- 文献库：`references.bib` 由 skill 维护，手写条目禁入

如果某项选择会改变主张、证据指向或 Contract，
则它不属于 plan，应返回 spec 明确定义。

## 4. 编译与评审方案

- 编译：agent 直接 `latexmk`（`paper-latex-compile-qa` 已卸载，不经过 skill），
  引用与缺图预检顺手做掉
- 评审：`paper-self-review` 打分 → `paper-revision` 按意见改 →
  重编译 → 再打分，直到分数达标或用户喊停
- 按 spec 中的 `VAL-*` 引用，不重新定义验收标准

## 5. 写作层未解决问题 / 延后工作（按需）

只记录不改变 spec、且不阻塞当前写作规划的问题。

- ...

如果问题涉及主张、证据、Contract 或引用要求，
不得记录在这里，应返回 spec 处理。
