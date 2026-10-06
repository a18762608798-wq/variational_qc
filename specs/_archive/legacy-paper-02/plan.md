# Writing Plan: paper-02 引入反映拓扑性质的物理量

## 1. 写作思路

- 在 paper-01 正文之后续写：`SEC-001`（`S(q)`/AFM 标签）→ `SEC-002`（四联热力图），
  均追加进现有 `docs/paper/main.tex`（中英双版同步）。
- 数据流：D03 数据集 + `figs/exp02/exp02_D03.pdf` → SEC-001；
  D04a–d 数据 + `figs/exp02/exp02_D04{a,b,c,d}.pdf` → SEC-002。
- 缺件安排：零缺件，连续写完。`CLM-005` 重点表述按大纲原文落位，不发挥。

## 2. 章节与 Skill 映射

- `SEC-001`：`paper-writing-section`（results），输入 D03 + `FIG-001`
  （`CLM-001`，`CIT-001` 落位：`dennijs1989preroughening` 已备 bib）
- `SEC-002`：`paper-writing-section`（results），输入 D04 + `FIG-002`
  （`CLM-002/003/004/005`，`CIT-002` 落位：复用 `elben2020manybody`）
- 图位：`paper-figure-layout`（`FIG-001` 单图；`FIG-002` 跨栏 `figure*` minipage 拼 `2×2`，
  标签 (a)–(d) 手工编号，与 D04a–d 对应；subfigure 已废弃）
- 引用：`paper-zotero-hunter`（CIT-001 bind；CIT-002 复用已验证条目归档确认；
  CIT-003 按需，缺则跳过）
- 格式：`paper-latex-formatting`（沿用 PRA 模板 reprint；`subcaption` 已卸载，minipage 手工编号）
- 打分 / 改文：`paper-self-review` / `paper-revision`

## 3. LaTeX 工程结构

- 沿用 `docs/paper/`（`main.tex` + `main-zh.tex` + `references.bib` + `figures/`）。
- 上游图复制进 `figures/`：`exp02_D03.pdf`、`exp02_D04{a,b,c,d}.pdf`（4 个独立文件，原名保留）。
- `main.tex` / `main-zh.tex` 只剩导言 + `\input` + `\bibliography`（`sections/` 一节一文件，paper-07 T002 已拆分）
- `references.bib` 追加条目，禁手写（已有 `dennijs1989preroughening` 待用）。

## 4. 编译与评审方案

- `VAL-005`：agent 直接 `latexmk` 双版编译，引用/缺图预检。
- `VAL-004`：`CIT-001/002` 已读确认且 key 齐全（`CIT-003` 按需）。
- `VAL-001/002/003`：`paper-self-review` 打分覆盖（新增两节、2×2 标签一致、主张皆有证据）。
- 打分不达标 → `paper-revision` 改 → 重编译 → 再打分。

## 5. 写作层未解决问题 / 延后工作

- 无。本 feature 无阻塞项，可连续执行。
