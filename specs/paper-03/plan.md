# Writing Plan: paper-03 Closing

## 1. 写作思路

- 顺序：先核对 paper-01/02 的当前正文与冻结边界 → 绑定并检查 Related Work 所需文献 → 完成摘要和结论 → 将 Related Work 并入 Introduction → 做全篇术语、符号、时态和交叉引用统稿。
- 数据流：paper-01 Methods 与 paper-02 Results 的已收敛正文 → `SEC-001` 摘要与 `SEC-002` 结论；R3 及本轮已核验文献 → `SEC-003` Introduction 中的 Related Work 段；全文源文件 → `SEC-004` 统稿检查。
- 结果边界：paper-02 的 D07/D08 图缺件和冻结主张不在本 feature 解冻。摘要与结论只写已建立的模型、测量、协议、比较框架及结果组织方式，不写具体排名、趋势、数值或真机-模拟机一致程度（引用 `CLM-001`、`CLM-002`、`BND-003`）。
- 文献边界：Related Work 使用七个具体文献方向：真机拓扑、变分算法、结构因子、string 长程关联、稳定子/读出驱动的优质比特选择、读出误差缓解、有限尺寸能隙与外推；其中后五项按 `CIT-002`..`CIT-005` 组织。文献用于方法背景和定位，不替代本文结果证据（引用 `CLM-003`、`CIT-001`..`CIT-006`）。
- 无 `GAP-DATA` 或 `GAP-INTERP` 阻塞当前写作；若 paper-02 后续返工改变结果范围，摘要和结论随 paper-02 返工同步更新。

## 2. 章节与 Skill 映射

- `SEC-001`（摘要）：`paper-writing-section`（abstract），输入 paper-01/02 正文；双语摘要覆盖问题、模型、观测量、变分电路、真机方法、比较协议和当前冻结状态，不引入 D07/D08 具体结果。
- `SEC-002`（结论）：`paper-writing-section`（conclusion），输入全文已建立内容；双语结论复述工作贡献、可复现协议和结果框架，遵守 `CLM-002`，不扩大结论。
- `SEC-003`（Related Work 入引言）：`paper-writing-section`（Related Work 模式；PRA 不单列 Related Work），输入 `CIT-001`..`CIT-005` 已核验文献；按七个具体文献方向组织定位段，不把背景方法写成本文实验结果。
- `SEC-004`（统稿）：`paper-writing-section` + `paper-latex-formatting`，检查术语、符号、时态、章节边界、交叉引用和中英双版对应关系。
- 引用：`paper-zotero-hunter` 仅负责从已核验 Zotero 条目 harvest/bind；不新增 hunt，不手写 `references.bib` 条目。
- 格式：`paper-latex-formatting` 按 PRA 模板检查摘要、引言、结论、引用和既有图编号；本 feature 不制作新图。
- 打分 / 改文：`paper-self-review` 对 paper-03 范围打分；若有可修复问题再用 `paper-revision`，重新编译并复评。

## 3. LaTeX 工程结构

- 沿用 `docs/paper/`：`main.tex` 与 `main-zh.tex` 作为英文投稿版和中文归档版，正文继续使用 `sections/*.tex` 与 `\input`，共用 `references.bib` 和既有 `figures/`。
- 修改范围集中在摘要、`sections/00-introduction.tex` / `sections/00-introduction-zh.tex`、结论对应 section 文件以及必要的统稿位置；不改变 paper-01/02 的实验定义或图文件。
- 不新增图位、不复制或链接上游图文件；只检查既有图编号、标签和引用一致性。
- `references.bib` 由 Zotero citation workflow 维护；新增绑定只允许来自 `CIT-001`..`CIT-006` 已核验条目，禁止手写条目。
- 中文版使用 `xelatex`/`latexmk -xelatex` 编译，英文版使用项目现有 `latexmk` 流程。

## 4. 编译与评审方案

- `VAL-001`：逐项检查 `SEC-001`..`SEC-004` 均已成文，且 Related Work 并入 Introduction，不生成 PRA 独立章节。
- `VAL-002`：逐项回查 `CLM-001`..`CLM-003` 的证据绑定；摘要和结论不含 D07/D08 冻结的具体排名、趋势或数值。
- `VAL-003`：逐项检查 `CIT-001`..`CIT-006` 只使用已核验条目，引用用途与对应文献轴匹配。
- `VAL-004`：agent 直接执行英文和中文 `latexmk` 编译，并检查未定义引用、未定义交叉引用、缺图和 `git diff --check`。
- 评审：按 `paper-self-review` 对本 feature 打分；若发现问题，按 `paper-revision` 修改后重新执行 `VAL-001`..`VAL-004` 并复评。

## 5. 写作层未解决问题 / 延后工作

- paper-02 的 D07/D08 图和具体结果仍是其 Follow-up；本 feature 当前只保留框架表述。数据到位后，需通过 paper-02 返工流程判断是否同步更新摘要和结论。
- 结论中的引用数量和具体引用位置留到写作时按实际段落需要决定，不改变 `CIT-001`..`CIT-006` 的覆盖范围。
