# Writing Plan: paper-04 真机优质比特选择方法介绍

## 1. 写作思路

- 先 `SEC-001`（筛选方法，可全写）：cluster 态/稳定子/打分公式/8 链与 10 环各自比较。
- `SEC-002`（排名图）只写框架：芯片百花可写，具体比特/子链表冻结，
  三个图空位 `[TODO(GAP-001): 待 D07 图]`。
- 中英双版同步；在现有 `main.tex`（paper-03 内容之后、`\appendix` 之前）续写。

## 2. 章节与 Skill 映射

- `SEC-001`：`paper-writing-section`（methods），输入 `premium_qubits.md` + exp05 定义
  （`CLM-001`，`CIT-001` 落位：`raussendorf2001oneway` 已备 bib）
- `SEC-002`：`paper-writing-section`（results），框架先行，排名论述冻结
  （`CLM-002/003/004` 比特表待图）
- 图位：`paper-figure-layout`（`FIG-001/002/003` 空位标记，三图一起呈现待图到后定版式）
- 引用：`paper-zotero-hunter`（CIT-001 bind；CIT-002 按需）
- 格式：`paper-latex-formatting`（沿用 PRA 模板，无新宏包需求）
- 打分 / 改文：`paper-self-review` / `paper-revision`

## 3. LaTeX 工程结构

- 沿用 `docs/paper/`（`main.tex` + `main-zh.tex` + `references.bib` + `figures/`）。
- 图到后从 `figs/exp05/` 复制进 `figures/`（原名保留），空位届时填图。
- `main.tex` / `main-zh.tex` 只剩导言 + `\input` + `\bibliography`（`sections/` 已拆分，见 paper-07 T002）。

## 4. 编译与评审方案

- `VAL-005`：agent 直接 `latexmk` 双版编译（空位用 `\missingfigure` 风格占位框，保证可编译）。
- `VAL-004`：`CIT-001` 已读确认且 key 齐全（`CIT-002` 按需）。
- `VAL-001/002/003`：`paper-self-review` 打分覆盖（方法节齐、空位标记存在、冻结主张无陈述句）。
- 打分不达标 → `paper-revision` 改 → 重编译 → 再打分。

## 5. 写作层未解决问题 / 延后工作

- `GAP-001-DATA`（D07 图）转 paper-05/exp05 跟踪，不在本 feature 解决。
