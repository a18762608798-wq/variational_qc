# Writing Plan: paper-01 模型引入和基本性质

## 1. 写作思路

- 顺序：先 `SEC-001`（模型定义，不依赖数据）→ `SEC-002`（D01 相图正文）→
  `SEC-003`（附录能隙，D02a/b/c 均已落定，无等待项）。
- 数据流：`H.md` → SEC-001；D01 数据集 + `figs/exp01/exp01_D01.pdf` → SEC-002；
  D02a/b/c 数据 + `figs/exp03/` 三图 → SEC-003。
- 缺件安排：本 feature 无 `GAP-DATA`、无未转正推测，
  三节可连续写完，不冻结任何主张。

## 2. 章节与 Skill 映射

- `SEC-001`（模型引入）：`paper-writing-section`（introduction/methods），
  输入 `docs/theory/H.md` + `topological_op.md`（`CLM-001`，`CIT-001` 占位）
- `SEC-002`（有限尺寸相图）：`paper-writing-section`（results），
  输入 D01 数据集 + `FIG-001`（`CLM-002`，`CIT-002` 占位）
- `SEC-003`（附录能隙）：`paper-writing-section`（results/appendix），
  输入 D02a/b/c + `FIG-002/003/004`（`CLM-003/004/005`，`CIT-003` 按需占位）
- Related Work：本 feature 不涉及（PRA 并入 Introduction 的工作归 paper-07 统稿）
- 图位：`paper-figure-layout`（`FIG-001` 正文单栏 `figure`；
  `FIG-002/003/004` 附录各独立成图）
- 引用：`paper-zotero-hunter`（`CIT-001/002` 必需，`CIT-003` 按需；
  harvest / verify / bind 全套）
- 格式：`paper-latex-formatting`（PRA 模板 `setup pra` + `pra-notes.md` 合规检查）
- 打分 / 改文：`paper-self-review` / `paper-revision`

## 3. LaTeX 工程结构

- 论文目录：`docs/paper/`（本 feature 先建骨架：`main.tex`、`references.bib`、`figures/`、`output/`）
- 上游图处理：从 `figs/exp01/exp01_D01.pdf`、`figs/exp03/exp03_D02{a,b,c}.pdf`
  复制进 `docs/paper/figures/`（复制不链接：上游图定稿不动，论文侧独立）
- 主文件结构：`main.tex` / `main-zh.tex` 只剩导言 + `\input` + `\bibliography`（`sections/` 已拆分，见 paper-07 T002）。
- 文献库：`docs/paper/references.bib` 由 skill 维护，手写条目禁入

## 4. 编译与评审方案

- `VAL-005`：agent 直接 `latexmk` 编译 `docs/paper/main.tex`，
  引用/缺图预检顺手做掉
- `VAL-004`：`CIT-001/002` 已读确认且 key 齐全（`CIT-003` 按需）
- `VAL-001/002/003`：`paper-self-review` 打分覆盖（章节齐套、图caption一致、主张皆有证据）
- 打分不达标 → `paper-revision` 改 → 重编译 → 再打分

## 5. 写作层未解决问题 / 延后工作

- 无。本 feature 无阻塞项，可连续执行。
