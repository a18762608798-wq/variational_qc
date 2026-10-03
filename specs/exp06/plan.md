# Implementation Plan: exp06 真机测量与比较

**Branch**: `specs/exp06` | **Date**: 2026-10-04 | **Spec**: `specs/exp06/spec.md`

**Input**: Feature specification from `specs/exp06/spec.md`

## Summary

在 S04 top1 比特上测 S03 最优电路的 `S(π)` 与 string：两线 × 每线 33 点
（`i=1,4,…,97`）× `p=1,2,3` = 198 组。关键简化（已由 theory 保证）：
`S(π)` 与 string 皆为全 `Z` 对角观测量，单组只需 **1 个 estimator 电路**
（VQE 态制备 + `Z` 基测量）× `5` 次独立重复；每 `3` 组一批 + `2` 个 S05
标定电路（全 `0` / 全 `X`）。技术路线：Python/Qiskit 复刻 exp04 拟设
（初态制备 + orbit 轨道电路，参数取 S03），先经 Aer 态矢量与 D10 黄金交叉
锁定电路构造器，再走真机提交（`correct=False`、opt3、显式 coupling_map）；
本地缓解（逐比特 `M⁻¹` + 非负约束）→ 组装 D11/S05 → D12 归一化比较 → 出图。

以上均为实现层选择；点位、比特、参数来源、shots/重复、标定批量度、
矫正开关、输出内容与验证条件沿用 spec，未改动实验语义。

## Technical Context

**Language/Version**: Python（Qiskit 电路构造 + 真机提交 + 本地缓解/组装；
本实验零 Julia 新增，只只读消费 npz）

**Primary Dependencies**: `qiskit==2.5.1`（电路 + 转译 opt3）+
`qiskit-aer==0.17.2`（黄金交叉态矢量仿真）+ `qmeas`（`quark_client` 提交/
轮询复用、`benchmark.io` checkpoints 思想复用；版本记入 manifest）+
`quarkstudio==7.3.9`（提交后端，`correct=False`）+ `numpy`（缓解/观测量）

**Storage**: 两层落盘——原始层 `data/exp06/batches/<batch_id>/` 逐任务 JSON
（counts + tid + 提交参数，增量落盘，中断续跑只补缺失）；产品层
`data/exp06/exp06_{D11,D12}.npz` + `exp06_manifest.json`
（schema `exp06/v1`，S05 矩阵随 D11 存档）

**Testing**: `pytest`（纯本地：初态/轨道电路酉对照、Aer 黄金交叉、
缓解恒等式、D12 归一化、manifest schema；零真机调用）

**Target Platform**: Linux（本机编排）+ Baihua 真机（两路 top1 皆 Baihua，
单芯片，无跨芯片批次）

**Project Type**: 硬件测量编排（thin orchestration；电路构造器为本 feature
内新写 Julia→Python 复刻，经黄金交叉锁定）

**Performance Goals**: 账单：198 组 ×5 重复 = 990 VQE 任务 + 66 批 ×2 标定
= **1122 任务** × 2048 shots ≈ **230 万 shots**（estimator 单电路/组，
见 §3；账单由 preview 打印、人工确认覆盖）

**Constraints**: bill 未人工确认不得提交；S03 无对应点判 invalid 不补优化；
平台矫正关闭（提交参数留存备查）；转译绕行仅 topo `0–7` link 允许，
其余候选外纠缠门仍判 invalid

**Scale/Scope**: 198 组、66 批、D11 198 点 ×3p？不——每点 3 个 p 各自独立组，
D11 共 198 点（`2×33×3`）；D12 四图（`δ × {S(π), string}`）

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- I（Spec 权威）：点位 / 比特 / 参数 / shots / 标定 / 开关全在 spec；
  本 plan 只定 `basis_gates`、归一化区间、诊断阈值、记录方式等实现细则。
  PASS。
- II（分离）：不碰 `doc/theory/`；Qiskit 电路复刻以 ansatz/psi0 为准，
  theory 不进代码注释外的定义。PASS。
- III（边界）：S03/D10/S04 只读消费，不复算；提交/轮询复用
  `qmeas.random.quark_client`，不重写；电路构造器归本 feature，
  不建跨 feature 共享框架。PASS。
- IV（可重复）：快照引用（S04）+ 逐任务增量落盘 + manifest（S03 记录引用、
  `θ` 快照、`rng`、标定批次、栈版本、转译参数、schema `exp06/v1`）+
  提交/收回对账 + 缓解前后值双存档。PASS。
- V（正确性优先）：Aer 黄金交叉先行（构造器锁定后才碰真机）；
  转译 opt3 是 spec 语义（用户确认），抽样审计 CZ 行为只记录；
  预览零机时；无嵌套并行（提交并发由工具链内部控制）。PASS。
- VI（风格）：Python 经 qmeas env 统一解释器；出图走
  `scripts/figure_style.py`，mathtext，矢量 PDF + 300dpi PNG。PASS。

## Project Structure

### Documentation (this feature)

```text
specs/exp06/
├── spec.md               # 实验定义（已定，Q1–Q5 全闭）
├── plan.md               # 本文件
└── tasks.md              # tasks 阶段产出（非本 plan 创建）
```

### Source Code (repository root)

```text
scripts/
├── exp06_circuits.py     # 初态制备 + orbit 拟设 Qiskit 构造器（θ,S03,a*→电路；§3）
├── exp06_preview.py      # 离线：S03 点位映射 → 批量划分（3组/批）→ 账单（零机时）
├── exp06_submit.py       # 真机提交：转译（opt3/coupling_map）→ 提交 → 对账 → 补跑
├── exp06_assemble.py     # 本地缓解（S05 M⁻¹+非负）→ 观测量 → D11/S05.npz + manifest
├── verify_exp06.py       # 生产断言（见 §4）
├── plot_D11D12.py        # D11 散点+误差棒 + D12 归一化比较 → figs/exp06/
data/exp06/
├── batches/<bid>/        # 逐任务 JSON（counts/tid/提交参数；中断续跑只补缺失）
├── exp06_D11.npz / exp06_D12.npz / exp06_manifest.json
figs/exp06/
test/
└── test_exp06_local.py   # pytest（零真机调用；Aer 黄金交叉为核心门）
```

**Structure Decision**: 薄编排 + 单一新构造器。Julia 侧零新增；`qmeas.estimator`
runner 不直接复用（其按 Pauli 分组提交多电路；本实验全 `Z` 对角只需单电路，
自写更薄的提交循环，但提交/轮询原语复用 `quark_client`）。

## 1. 实现思路

- 数据流：读 S03（`meta=(δ_idx,s_idx,p,a*)`，`a*∈{1,2,3}=triv/topo/afm`；
  `θ` 行 `NaN`-pad，`δ=0` 时有效 `Lp/2`）→ 稀疏点过滤
  （`s_idx∈{1,4,…,97}`，`2×33×3=198` 组；S03 缺点直接标 invalid）→
  每 3 组一批（66 批，批次 id 固定排序）→ preview 账单 → **人工确认** →
  电路构造（§3）→ Aer 黄金交叉（见下，通过后才提交）→ 转译抽样审计 →
  提交（VQE 电路 ×5 重复 + 每批 2 标定，同批；`correct=False`）→
  对账补跑 → 本地缓解 → 组装 D11（均值/标准差/原始重复/缓解前后/S03 与 S05
  引用）→ D12（D10 对应点引用 + 各自归一化）→ verify → 出图。
- Aer 黄金交叉（构造器锁定门，零机时）：对每 `(a*,p,δ∈{0,0.85})` 抽样点，
  Qiskit 电路经 Aer 态矢量仿真求 `S(π)`/string/能量，与 D10 同点值比对
  （容限 `1e-8`，转译前逻辑电路比对，绕开硬件噪声）；任一超差即停，
  修构造器（多半是轨道配对/子层顺序/`δ=0` 减半映射问题）。
- 缓解：每批由 2 标定电路得 8 比特各自 `M`（全 `0` 电路给 `P(·|0)` 列，
  全 `X` 给 `P(·|1)` 列）；对 256 维经验分布做 Kronecker-`M⁻¹`
  （逐比特独立），负值截零重归一；缓解前后观测量双存档。
- D12：真机（D11 均值）与模拟机（D10 同 33 点引用值）按 `(δ,观测量)` 面板
  各自 min-max 归一化到 `0–1`（区间即该面板 33 点，like-for-like，
  plan 级细则，记入 manifest），同图比较趋势。

## 2. 代码与模块结构

- `scripts/exp06_circuits.py`：`build_init(a*)`（单态：`X+H+CX` 相位正确；
  GHZ：`H` + CNOT 链；与 `Exp04.InitStates` 逐振幅对照测试）、
  `build_ansatz(theta,a*,p,delta)`（轨道配对 `O_j↔O_{M+1-j}` /
  `E_j↔E_{M-j}`、`δ=0` 参数减半映射、子层顺序按初态 `F/S`、
  每键 `RXX(t1)RYY(t1)RZZ(t2)`；与 `Exp04.Ansatz` 语义逐项对应，
  对应表写进模块 docstring）、`build_estimator_circuit(...)`
  （初态 + 拟设 + 全 `Z` 测量；topo 用环状 coupling 信息仅作逻辑标注，
  物理映射在 submit 侧）、`build_calib_circuits(n)`（全 `0` / 全 `X`）。
- `scripts/exp06_preview.py`：S03 读入 → 稀疏过滤 → 66 批划分 →
  账单（VQE 990 + 标定 132 = 1122 任务，≈230 万 shots，快照/S03 引用）→
  `bill.json`（`confirmed=false`）。
- `scripts/exp06_submit.py`：读 `bill.json`（须 confirmed）→ 转译抽样审计
  （opt3 下记录 CZ 数/深度行为，topo 绕行预期内）→ 逐批提交（VQE ×5 + 标定 2，
  `correct=False` 参数留存）→ checkpoints 增量落盘 → 对账补跑
  （exp05 同模式：有 tid 只轮询不重提，Failed 显式 query）。
  转译后电路摘要（CZ 边集）随 checkpoints 留存，供 verify 验路断言。
- `scripts/exp06_assemble.py`：读 batches → S05 矩阵 → 缓解 → 观测量
  （`S(π)` 交错和、string 对角加权，定义同 Exp02，只读复刻公式）→
  写 `exp06_D11.npz` + `exp06_manifest.json`（schema `exp06/v1`：
  S03/S04 引用、点位、`θ` 快照、批次表、转译参数、栈版本、归一化区间）。
- `scripts/plot_D11D12.py`：D11 四面板散点 + 误差棒（`2δ × {S(π), string}`，
  `p=1,2,3` 三色）；D12 同版式归一化比较（真机点 + 模拟机线）。
- `test/test_exp06_local.py`：初态振幅对照（vs 解析式）、单键酉对照、
  Aer 黄金交叉（抽样点 vs D10，`1e-8`）、缓解恒等式（无噪声分布缓解不变；
  已知误读率合成数据恢复）、D12 归一化、manifest 必填字段。

## 3. 数值与技术决策

- 解释器：全 Python 经 qmeas env（Qiskit + Aer + qmeas 同 env，
  与 exp05 一致）；manifest 记解释器路径 + `qiskit`/`qiskit-aer`/
  `qmeas`(git commit)/`quarkstudio` 版本。
- `basis_gates`：`["rz", "rx", "ry", "cz"]`（与 exp05 同；单/双比特门集
  覆盖单态制备与 `RXX/RYY/RZZ` 分解；记入 manifest）。
- 物理比特映射：逻辑 `0..7` 按 S04 序列映射物理比特（链 top1
  `[77,…,70]`；topo 用 D09 Rank1 子链 `[84,83,82,69,70,71,72,73]`，
  Baihua）；topo 转译 `coupling_map` = 子链 7 边 + `0–7` 闭合边
  （首尾 `84↔73` 经剩余比特 `85–86` 绕行由优化器定，见 §1 link 语义；
  preview 打印映射表备查）。
- GHZ 初态采用中间发起版（手写，逻辑同
  `qmeas.models.xxz.get_initial_state(8, pidx=0)`：H 打中间比特、两路 CNOT
  向左右散开、翻奇位；纠缠级联深度 `~n/2`，真机退相干更小）。手写而不用
  qmeas 原函数的原因：三初态构造器保持零外部依赖、单源可审计，避免只有
  GHZ 一路依赖 qmeas 的不对称。替换原因：端点起链版深度 `~n`，中间发起减半；
  已逐振幅比对 `doc/theory/psi0.md` 解析式一致（`{85,170}` 均为 `+1/√2`）。
  不得回退到端点版（以 psi0 解析式为准）。
- 重复策略：5 次重复为独立任务提交（不同 tid，自然时间错开），
  标准差含漂移成分——这是 D11 误差棒的本意（估计标准差，非纯 shot 噪声）。
- 缓解数值：`M` 条件数检查（`cond > 1e6` 标可疑，诊断不设硬门）；
  Kronecker 逆经 `numpy`，256 维可忽略。
- 离散度诊断阈值（spec 授权 plan，只记录）：某点 5 次重复标准差
  超同 `(δ,p)` 中位数 `5` 倍则标记（需人工看是否为批次漂移）。
- D12 归一化：min-max 按面板（`δ × 观测量`）各自 33 点（plan 级细则）。
- M1 取证结论（2026-10-04 已办，T000 关闭）：平台读出矫正开关是 task
  payload 的 `options.correct`（quark `quafu.py` 任务文档：
  `'correct': False, # readout error correction`），与
  `QuarkOptions.mitigation` 无关；`submit_quark`
  （`qmeas/random/quark_client.py:104`）已透传 `"correct": opts.correct`，
  默认 `False` 即关闭。exp06 提交保持默认并留存参数，verify 查
  `correct=False`；spec/plan/tasks 内旧称 `mitigation=False` 一律改
  `correct=False`（术语修正，语义不变）。

## 4. 验证方案（覆盖 spec §5）

- `test_exp06_local.py` 先行全绿（含 Aer 黄金交叉门），否则不得提交。
- `verify_exp06.py` 对正式输出全量执行：
  - 每点 5 重复齐全；缓解前后双存档；`θ` 与 S03 同点逐元一致
    （`NaN`-pad 区除外）；S05 批次 id 与 VQE 同批（3 点一批）；
    提交参数 `correct=False` 留存可查。
  - 转译验路断言（spec §5 新增条目）：转译后电路的 `CZ` 边集须落入
    允许集（链：子链相邻 `7` 边；topo：子链 `7` 边 + `0–7` 绕行
    `0-10-9-7`），边集由 checkpoints 留存的转译摘要重算比对；
    未落入即相关点 invalid。
  - 对账：任务数 == 收回数 + 明确标记；无静默丢弃；无已收回重提。
  - invalid 任一触发即相关点判 invalid，非零退出指明点位。
  - 诊断输出：缓解前后差值分布、离散度标记、D12 目检提示。
- 出图前人工核对：D11 点位/误差棒与 npz 一致、D12 归一化区间记录正确。

## Complexity Tracking

本次 plan 无宪法违反，无需记录。
