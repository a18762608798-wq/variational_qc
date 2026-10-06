# Feature: paper-06 实验结果展示

> 本 spec 分为两部分：
>
> - **Part I — Paper Description**：说明主张、证据、上游输入与缺件，面向作者阅读。
> - **Part II — Specification Contract**：定义章节、图位、主张绑定、缺件与引用需求，作为可检查的规范性约束。
>
> 两部分必须一致；若存在冲突，应先澄清并修正 spec。

## Part I — Paper Description

### 1. Objective

写出实验结果展示节：真机-模拟机对比四张图（`δ=0` / `0.85` × AFM 结构因子 /
string operator，真机与模拟机结果置于同一图）。每张图叠放模拟机 `p=1,2,3`
曲线与真机最优层 `p*` 散点（含每个 estimator 的标准差误差棒）；
真机与模拟机各自内部作 `0–1` 归一化后比较变化趋势，不比绝对数值。

目标 venue：PRA（regular article）。读者读完应相信：真机趋势复现模拟机，
误差棒与归一化口径交代清楚。

不要在这里写 LaTeX 实现或验收细节。

### 2. Upstream Inputs

- 实验定义：`specs/exp06/spec.md`（S04 真机目标比特上 VQE 最优电路观测量测量，
  自含 S05；依赖 S03/S04/S06；与 exp04 共建 D08）、
  `specs/exp04/spec.md`（S06 模拟机全结果，D08 模拟机图层底数）。
- 数据产物：D08（真机图层 + 模拟机图层；**图文件未出**）。
- 论文大纲：`docs/paper-outline.md`“实验结果展示”节（四图布局、叠放规则、归一化口径）。
- 已有正文：`docs/paper/main.tex`（paper-01~05 内容，本节在其后；
  读出缓解与 VQE 方法已落定，可直接引用）。

### 3. Claims & Evidence

- `CLM-001`：比较协议（同图叠放、各自 `0–1` 归一化、比趋势不比绝对值、
  误差棒为 estimator 标准差）← 大纲 + exp06 定义（可先行）
- `CLM-002`：`δ=0` 下 AFM 与 string 的真机-模拟机趋势一致 ← D08a/b（`GAP-001-DATA`：图未出，冻结）
- `CLM-003`：`δ=0.85` 下 AFM 与 string 的真机-模拟机趋势一致 ← D08c/d（`GAP-001-DATA`：图未出，冻结）

### 4. Sections

- `SEC-001` 比较方法与归一化口径（正文，可先行；误差棒一句话带过，不展开 multinomial 公式，user 2026-10-05 定）
- `SEC-002` 四张对比图（正文，图位先留空，结果论述冻结）

### 5. Gaps（缺件表）

- `GAP-001-DATA [blocking]`：D08a–d 四张对比图未出（`figs/exp06/` 不存在）。
  `SEC-002` 留图空位，`CLM-002/003` 冻结；`SEC-001` 方法口径先行。

### 6. Citation Needs

- R3 硬件谱系背景（已 hunt + verify + bind，无新主张）：`colless2018robust`、
  `hempel2018quantum`、`kandala2017hardware`、`google2020hartree`、`yu2023simulating`
 （读出缓解与 VQE 方法引用仍复用 paper-03/05，不重复引）。

### 7. Open Questions（按需）

- 无（比较协议见大纲与 exp06 定义，无歧义）。

---

## Part II — Specification Contract

本部分只记录具有规范性、可检查意义的约束。每条独立约束使用稳定 ID。

### A. Boundary

#### In Scope

- `BND-001` 比较方法与归一化口径正文
- `BND-002` 四张对比图图位 + 空位（图到后填）

#### Out of Scope

- `BND-003` 作图本身（exp06 侧出，不管）
- `BND-004` 真机执行细节（已在 paper-04/05，不重复）

#### Dependencies

- `DEP-001` 上游 `specs/exp06`（D08 真机图层定义）
- `DEP-002` 上游 `specs/exp04`（S06 模拟机图层底数）
- `DEP-003` `docs/paper-outline.md`“实验结果展示”节
- `DEP-004` paper-03/05 正文（VQE 与读出缓解方法已落定）

### B. Sections

- `SEC-001`（比较方法）：输入大纲 + exp06 定义 → 输出正文段落（先行）
- `SEC-002`（四张对比图）：输入 D08（待图）→ 输出图位空位 + 冻结论述（后填）

### C. Figures

- `FIG-001`：D08a–d 四占位预排为 2×2 `figure*`（minipage 手工 (a)(b)(c)(d) 编号 + 联合 caption；图到后原图一像素不改，直接替换各框为 `\includegraphics` 即成 subfigure 版式）→ `[TODO(GAP-001): 待 D08a–d 图]`
- 四图论文中一起呈现（版式待图到后定）

### D. Claim Binding

- `CLM-001` ← evidence [大纲比较协议, exp06 spec 定义]
- `CLM-002` ← evidence [D08a/b，`GAP-001-DATA` 图待出，冻结]
- `CLM-003` ← evidence [D08c/d，`GAP-001-DATA` 图待出，冻结]

### E. Gaps

- `GAP-001-DATA [blocking]`：D08a–d 图未出；`SEC-002` 留空位，`CLM-002/003` 冻结；
  `SEC-001` 先行不受影响

### F. Citation Requirements

- R3 硬件谱系背景 5 篇（见 §6 清单，均已 hunt + verify + bind，无新主张）；
  读出缓解与 VQE 方法引用复用 paper-03/05；未验证引用不得合稿

### G. Acceptance

- `VAL-001` → verifies [`SEC-001`]：方法口径节齐套，与大纲/exp06 一致
- `VAL-002` → verifies [`FIG-001`]：四占位合一空位标记存在（图到后填图并恢复版式）
- `VAL-003` → verifies [`CLM-001`]：协议主张有证据；`CLM-002/003` 保持冻结
- `VAL-004` → verifies [compile]：中英双版编译通过，无未定义引用
