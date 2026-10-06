# Writing Plan: paper-02 Results and Discussion

## 1. 写作思路

- 顺序：先 `SEC-001`（比较协议，不依赖图，可先行）→ `SEC-002`（D07 排名，图位空位、结论冻结）→ `SEC-003`（D08 比较，图位空位、结论冻结）。
- 数据流：大纲比较协议 + exp06 `POST-002/003` → SEC-001；D07a/b/c + S04（以最新落盘为准）→ SEC-002；D08 + S06 → SEC-003。
- 缺件安排：`GAP-001-DATA`（D07 图）、`GAP-002-DATA`（D08 图）均为 non-blocking，只冻结对应结论，保留图位空位；`SEC-001` 协议文字先行。
- S04 取值跟随 exp05 最新落盘，不冻结旧快照；`p*` 最优层待 D08 落定后按 `POST-002` 复算，不预填。

## 2. 章节与 Skill 映射

- `SEC-001`（比较协议）：`paper-writing-section`（results），输入大纲 + exp06 定义；沿用旧口径（同图叠放、各自归一化、误差棒一句话）。
- `SEC-002`（D07 排名）：`paper-writing-section`（results），输入 D07a/b/c + S04；只写图位与冻结论述。
- `SEC-003`（D08 比较）：`paper-writing-section`（results），输入 D08 + S06；只写图位与冻结论述。
- 图位：`paper-figure-layout`（`FIG-001` D07 三图一起呈现；`FIG-002` D08 四占位 2×2）。
- 引用：复用 R3 硬件谱系与 paper-01 已验证条目；`CIT-001` 按需复用，不新增 hunt。
- 格式：`paper-latex-formatting`（PRA 版式 + 引用/图位检查）。
- 打分 / 改文：`paper-self-review` / `paper-revision`（只验收本 feature，不把 D07/D08 缺图当 Methods 缺陷）。

## 3. LaTeX 工程结构

- 沿用 `docs/paper/`（`main.tex` / `main-zh.tex` + `sections/` + `references.bib` + `figures/`）；中文版 xelatex。
- D07/D08 图位以 `[TODO(GAP-001/002)]` 空位标记进文，不复制不存在的图文件。
- 上游图到后：复制进 `docs/paper/figures/`（复制不链接），替换空位。
- `references.bib` 由 skill 维护，手写条目禁入；本 feature 不新增 key（复用）。

## 4. 编译与评审方案

- `VAL-001`：`SEC-001` 协议节齐套。
- `VAL-002`：`FIG-001/002` 空位标记存在。
- `VAL-003`：`CLM-001` 有据；`CLM-002..006` 冻结无事实语气。
- `VAL-004`：agent 直接 `latexmk` 编译 + 引用/缺图预检。
- 评审：`paper-self-review` 按本 feature 边界打分 → 有问题 `paper-revision` → 重编译 → 再打分。

## 5. 写作层未解决问题 / 延后工作

- `p*` 待 D08 落定后复算（`OQ-001`，非阻塞）。
- S04 若更新，具体比特表跟随最新落盘（非阻塞）。
- D07/D08 图到后填图并解冻结论，届时走返工流程更新本 feature。
