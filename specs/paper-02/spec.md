# Feature: paper-02 Results and Discussion

> 本 spec 分为两部分：
>
> - **Part I — Paper Description**：说明主张、证据、上游输入与缺件，面向作者阅读。
> - **Part II — Specification Contract**：定义章节、图位、主张绑定、缺件与引用需求，作为可检查的规范性约束。
>
> 两部分必须一致；若存在冲突，应先澄清并修正 spec。

## Part I — Paper Description

### 1. Objective

写出论文的 Results and Discussion 部分，集中报告优质比特筛选的具体排名结论与真机-模拟机对比的实验结论。筛选协议、读出缓解流程等机制已在 paper-01 Methods 定义，本 feature 不重复，只写：

- D07a/b/c 的具体排名与 S04 目标比特结论；
- D08 比较协议（同图叠放、各自 `0–1` 归一化、比趋势不比绝对值）与四面板比较结论。

目标 venue：PRA（regular article）。读者读完应相信：冠军比特选得有据，真机趋势复现模拟机，误差棒与归一化口径交代清楚。D07/D08 图未出时，具体排名与趋势结论冻结，只保留图位与协议文字。

不要在这里写 LaTeX 实现或验收细节。

### 2. Upstream Inputs

- 实验定义：
  - `specs/exp05/spec.md`：D07a/b/c 排名与 S04 目标比特（数据部分落定：`data/exp05/bill.json`、候选 evidence、`topology_cache`；图文件未出）。
  - `specs/exp06/spec.md`：D08 真机图层（`p=1,2,3` 全量测量 + `p*` 选取规则 `POST-002` + 叠放归一化 `POST-003`；`data/exp06/batches` 已有，图文件未出）。
  - `specs/exp04/spec.md`：S06 模拟机图层底数与 S03 最优参数（D08 模拟机曲线只消费不复算）。
- 共享输出：S04（目标比特，取值以 exp05 最新落盘为准，不在本 feature 冻结旧快照值）。
- 数据产物：D07a/b/c（排名数据部分可用，图待出）、D08（batches 部分可用，图待出）。
- 论文大纲：`docs/paper-outline.md`“真机优质比特选择方法介绍”中的排名呈现条目与“实验结果展示”节。
- 已有正文：paper-01 Methods（筛选协议、比较口径引用源，不重复定义）。

### 3. Claims & Evidence

- `CLM-001`：比较协议（真机 `p*` 散点与模拟机 `p=1,2,3` 曲线同图叠放、各自内部 `0–1` 归一化、比趋势不比绝对值、误差棒为 estimator 标准差）← 大纲 + exp06 `POST-002/003`（协议可先行，不依赖图）。
- `CLM-002`：8 链评分排名前十与冠军链结论 ← D07a（`GAP-001-DATA`：图未出，具体比特表冻结）。
- `CLM-003`：10 环评分排名前十与冠军环结论 ← D07b（`GAP-001-DATA`：图未出，具体比特表冻结）。
- `CLM-004`：冠军环内十条 8-子链排名与 S04 目标比特结论 ← D07c + S04（`GAP-001-DATA`：图未出，子链表冻结；S04 取值以最新落盘为准）。
- `CLM-005`：`δ=0` 下 AFM 与 string 的真机-模拟机趋势一致 ← D08a/b（`GAP-002-DATA`：图未出，冻结）。
- `CLM-006`：`δ=0.85` 下 AFM 与 string 的真机-模拟机趋势一致 ← D08c/d（`GAP-002-DATA`：图未出，冻结）。

### 4. Sections

- `SEC-001` 比较协议与归一化口径（正文，可先行；误差棒一句话，不展开 multinomial 公式）。
- `SEC-002` D07 排名结论（正文，图位先留空，具体排名冻结）。
- `SEC-003` D08 四面板比较（正文，图位先留空，趋势结论冻结）。

### 5. Gaps（缺件表）

- `GAP-001-DATA [non-blocking]`：D07a/b/c 三张排名图未出（无 `figs/exp05/`）；`SEC-002` 留图空位，`CLM-002/003/004` 冻结；`SEC-001` 协议先行不受影响。
- `GAP-002-DATA [non-blocking]`：D08a–d 四张对比图未出（无 `figs/exp06/`）；`SEC-003` 留图空位，`CLM-005/006` 冻结；`SEC-001` 协议先行不受影响。
- S04 若随 exp05 重跑更新，具体比特表以最新落盘为准，不在本 feature 冻结旧值。

### 6. Citation Needs（按需）

- 无新增 hunt 需求：硬件谱系背景（R3 已 hunt + verify + bind）复用；VQE/读出缓解引用复用 paper-01 Methods 已验证条目。
- `CIT-001`：D07/S04 若需补充筛选方法背景，按需复用 cluster/基准测试方向已验证条目，不新增 hunt。

### 7. Open Questions

- `OQ-001 [non-blocking]`：`p*` 最优层选取需 D08 数据落定后按 exp06 `POST-002` 复算，不在本 feature 预填。

---

## Part II — Specification Contract

本部分只记录具有规范性、可检查意义的约束。每条独立约束使用稳定 ID。

### A. Boundary

#### In Scope

- `BND-001` D07a/b/c 排名结论正文 + 图位空位（图到后填）。
- `BND-002` D08 比较协议正文 + 四面板图位空位（图到后填）。
- `BND-003` S04 目标比特结论（取值跟随最新落盘）。

#### Out of Scope

- `BND-004` 筛选协议、读出缓解机制本身（已在 paper-01，不重复）。
- `BND-005` 作图本身（exp05/exp06 侧出，不管）；摘要结论统稿（归 paper-03）。

#### Dependencies

- `DEP-001` 上游 `specs/exp05`（D07a/b/c 定义、排名数据、S04）。
- `DEP-002` 上游 `specs/exp06`（D08 真机图层、`p*` 规则、叠放归一化）。
- `DEP-003` 上游 `specs/exp04`（S06 模拟机图层底数，只消费）。
- `DEP-004` paper-01 Methods 正文（协议引用源）。
- `DEP-005` `docs/paper-outline.md` 排名呈现与实验结果展示条目。

### B. Sections

- `SEC-001`（比较协议）：输入大纲 + exp06 定义 → 输出正文段落（先行；叠放规则、归一化口径、误差棒说明）。
- `SEC-002`（D07 排名）：输入 D07a/b/c + S04 → 输出图位空位 + 冻结论述（后填）。
- `SEC-003`（D08 比较）：输入 D08 → 输出四面板图位空位 + 冻结论述（后填）。

### C. Figures

- `FIG-001`：D07a/b/c 三图（待 `figs/exp05/`）→ `[TODO(GAP-001): 待 D07a–c 图]`，论文中一起呈现。
- `FIG-002`：D08a–d 四占位预排为 2×2 `figure*`（图到后原图替换）→ `[TODO(GAP-002): 待 D08a–d 图]`。
- S04 比特表不单独成图，随排名文字给出。

### D. Claim Binding

- `CLM-001` ← evidence [大纲比较协议, exp06 `POST-002/003`]
- `CLM-002` ← evidence [D07a 数据，`GAP-001-DATA` 图待出，冻结]
- `CLM-003` ← evidence [D07b 数据，`GAP-001-DATA` 图待出，冻结]
- `CLM-004` ← evidence [D07c + S04，`GAP-001-DATA` 图待出，冻结]
- `CLM-005` ← evidence [D08a/b，`GAP-002-DATA` 图待出，冻结]
- `CLM-006` ← evidence [D08c/d，`GAP-002-DATA` 图待出，冻结]

### E. Gaps

- `GAP-001-DATA [non-blocking]`：D07a/b/c 图未出；`SEC-002` 留空位，`CLM-002/003/004` 冻结；`SEC-001` 先行不受影响。
- `GAP-002-DATA [non-blocking]`：D08a–d 图未出；`SEC-003` 留空位，`CLM-005/006` 冻结；`SEC-001` 先行不受影响。
- 不得用猜测填充具体排名或趋势结论；图到后先更新 spec，再写入正文。

### F. Citation Requirements

- 复用 R3 已验证硬件谱系背景与 paper-01 Methods 已验证条目；`CIT-001` 按需复用，不新增 hunt。
- 未验证引用不得合稿。

### G. Acceptance

- `VAL-001` → verifies [`SEC-001`]：协议节齐套，与大纲/exp06 一致。
- `VAL-002` → verifies [`FIG-001`, `FIG-002`]：空位标记存在（图到后填图）。
- `VAL-003` → verifies [`CLM-001`]：协议主张有证据；`CLM-002..006` 保持冻结（无陈述句级无据主张）。
- `VAL-004` → verifies [compile]：中英双版编译通过，无未定义引用。
