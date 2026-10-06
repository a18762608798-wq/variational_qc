# Writing Plan: paper-07 收尾（摘要/结论/统稿）

## 1. 写作思路

- 顺序：先拆 `sections/*.tex`（OQ-001 已定拆，一节一文件，`main.tex` 只剩导言 + `\input`），
  再 `SEC-003`（Related Work 入引言，需 CIT-001 先 hunt），
  再 `SEC-001`（摘要重写）+ `SEC-002`（结论），最后 `SEC-004` 全篇统稿。
- 中英双版同步；`main-zh.tex` 同样拆分。

## 2. 章节与 Skill 映射

- 拆分：agent 直接执行（按现有 `\section`/`\label` 切块，不涉及主张，不经过 skill）
- `SEC-003`：`paper-related-work`（对比段落，双方向：真机拓扑 + 变分算法），
  输入用户定位 + `CIT-001` 文献（各方向 1–2 篇代表作，hunt + verify + bind）
- `SEC-001`：`paper-writing-section`（abstract），输入全篇正文
- `SEC-002`：`paper-writing-section`（conclusion），输入各节结果（只复述）
- `SEC-004`：统稿（术语、符号、时态、交叉引用全查）
- 引用：`paper-zotero-hunter`（CIT-001 bind；CIT-002 复用）
- 格式：`paper-latex-formatting`（PRA 投前检查收官）
- 打分 / 改文：`paper-self-review` / `paper-revision`

## 3. LaTeX 工程结构

- `docs/paper/sections/*.tex`（一节一文件，中英同目录、同名 `-zh` 后缀，已定）。
  `main.tex` / `main-zh.tex` 只剩导言 + `\input` + `\bibliography`。
- `figures/`、`references.bib` 不动。

## 4. 编译与评审方案

- `VAL-004`：agent 直接 `latexmk` 双版编译（拆分后首编，交叉引用重点查）。
- `VAL-003`：`CIT-001` 已读确认且 key 齐全。
- `VAL-001/002`：`paper-self-review` 打分覆盖（四节齐、定位有据）。
- 打分不达标 → `paper-revision` 改 → 重编译 → 再打分。

## 5. 写作层未解决问题 / 延后工作

- `GAP-001-INTERP`（CIT-001 hunt）是本 feature 唯一外部依赖，先 hunt 后写 SEC-003。
