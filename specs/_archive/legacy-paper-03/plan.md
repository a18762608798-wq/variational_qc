# Writing Plan: paper-03 变分电路介绍

## 1. 写作思路

- 在 paper-02 内容之后、`\appendix` 之前续写：`SEC-001`（起点终点示意）→
  `SEC-002`（变分电路结构），中英双版同步。
- 数据流：D05（配对坐标 exp01 `PRE-004`）+ `figs/exp01/exp01_D05.pdf` → SEC-001；
  `psi0.md` + `ansatz.md` + D06a–c → SEC-002。
- 缺件安排：零缺件，连续写完。配对坐标直接引用上游 `PRE-004`，不重复推导。

## 2. 章节与 Skill 映射

- `SEC-001`：`paper-writing-section`（methods），输入 D05 + `FIG-001`
  （`CLM-001`，三对坐标逐对列出）
- `SEC-002`：`paper-writing-section`（methods），输入 `psi0.md` + `ansatz.md` + `FIG-002`
  （`CLM-002/003`，orbit 配对规则简述；`CIT-001` 落位：`peruzzo2014variational` 待备 bib）
- 图位：`paper-figure-layout`（`FIG-001` 单图，标记箭头说明进 caption；
  `FIG-002` D06a–c 三独立单栏 `figure` 散放，共享 FIG.5 编号（后两图前 `\addtocounter{figure}{-1}`），图例 (a) 详写）
- 引用：`paper-zotero-hunter`（CIT-001 bind；CIT-002 按需）
- 格式：`paper-latex-formatting`（沿用 PRA 模板，无新宏包需求）
- 打分 / 改文：`paper-self-review` / `paper-revision`

## 3. LaTeX 工程结构

- 沿用 `docs/paper/`（`main.tex` + `main-zh.tex` + `references.bib` + `figures/`）。
- 上游图复制进 `figures/`：`exp01_D05.pdf`、`exp04_D06{a,b,c}.pdf`（原名保留）。
- `main.tex` / `main-zh.tex` 只剩导言 + `\input` + `\bibliography`（`sections/` 已拆分，见 paper-07 T002）。

## 4. 编译与评审方案

- `VAL-005`：agent 直接 `latexmk` 双版编译，引用/缺图预检。
- `VAL-004`：`CIT-001` 已读确认且 key 齐全（`CIT-002` 按需）。
- `VAL-001/002/003`：`paper-self-review` 打分覆盖。
- 打分不达标 → `paper-revision` 改 → 重编译 → 再打分。

## 5. 写作层未解决问题 / 延后工作

- 无。本 feature 无阻塞项，可连续执行。
