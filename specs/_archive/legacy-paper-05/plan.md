# Writing Plan: paper-05 真机读出误差缓解介绍

## 1. 写作思路

- 只写 `SEC-001` 一节（分配矩阵 + 求逆矫正 + 非负约束 + 代价），
  在现有 `main.tex`（paper-04 内容之后、`\appendix` 之前）续写，中英双版同步。
- 无图位，无缺件，一次写完。

## 2. 章节与 Skill 映射

- `SEC-001`：`paper-writing-section`（methods），输入 `readout_mitigation.md` + exp06 定义
  （`CLM-001/002/003`，`CIT-001` 落位：`bravyi2021mitigating` 待备 bib）
- 引用：`paper-zotero-hunter`（CIT-001 bind）
- 格式：`paper-latex-formatting`（沿用 PRA 模板，无新宏包需求）
- 打分 / 改文：`paper-self-review` / `paper-revision`

## 3. LaTeX 工程结构

- 沿用 `docs/paper/`（`main.tex` + `main-zh.tex` + `references.bib`）。
- `references.bib` 追加 `bravyi2021mitigating` 条目，禁手写（字段对 Zotero 条目）。

## 4. 编译与评审方案

- `VAL-003`：agent 直接 `latexmk` 双版编译，引用预检。
- `VAL-002`：`CIT-001` 已读确认且 key 齐全。
- `VAL-001`：`paper-self-review` 打分覆盖（方法节齐、主张皆有证据）。
- 打分不达标 → `paper-revision` 改 → 重编译 → 再打分。

## 5. 写作层未解决问题 / 延后工作

- 无。本 feature 无阻塞项，可连续执行。
