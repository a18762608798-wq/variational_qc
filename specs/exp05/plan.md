# Implementation Plan: exp05 真机优质比特

**Branch**: `specs/exp05` | **Date**: 2026-10-04 | **Spec**: `specs/exp05/spec.md`

**Input**: Feature specification from `specs/exp05/spec.md`

## Summary

沿两条产品线做真机实测筛选：`8` 链（Baihua + Shenglian，每芯片按静态边保真度
排序采样截断至多 `3000` 条，去重后计数）与 `10` 环（全枚举全测）。
每候选跑 `4` 个基准电路（`stab_g0` / `stab_g1` / `allzero` / `allone`，
shots `2048`），按 `score = 0.8·S̄ + 0.2·F_ro` 打分，
链环各自内部排序产出 D07a / D07b；冠军环内 `10` 条连续 `8`-子链 join 链 evidence
（缺失补测）产出 D07c；冠军链 + 冠军环（首名分差 `< 0.02` 并列全记）产出 S04。
技术路线：复用 `qmeas.benchmark` 内核（拓扑 / 电路 / 提交轮询 / 打分），
exp05 侧只写薄编排（预览 / 预筛 / 提交 / 组装 / 验证 / 出图），不建新框架、
不改 `qmeas`；离线预览打印账单→人工确认后才提交机时。

以上均为实现层选择；候选定义、基准电路、打分公式、shots、截断、并列阈值、
输出内容与验证条件沿用 spec，未改动实验语义。

## Technical Context

**Language/Version**: Python（真机提交只能经 Python 工具链；本实验零 Julia 新增）

**Primary Dependencies**: `qmeas.benchmark`（拓扑拉取 / 候选枚举 / 基准电路 /
提交轮询 / 打分；版本 `0.1.1` + git commit 一并记入 manifest）、
`quarkstudio` + `quarkcircuit`（经 qmeas env 间接依赖，版本记入 manifest）、
`numpy`（本地打分验算 / 组装）、`matplotlib`（出图，与项目 `figure_style.py` 一致）

**Storage**: 两层落盘——原始层复用 `qmeas.benchmark.io`
（`data/exp05/checkpoints_{chain,ring}/` 逐候选 JSON，中断续跑只补缺失）；
产品层本实验组装（`data/exp05/exp05_{D07a,D07b,D07c,S04}.npz` +
`exp05_manifest.json`，与 exp01–04 产品惯例一致，供 exp06 取用）

**Testing**: `pytest`（纯本地逻辑：去重 / 打分公式 / D07c join 匹配 / 并列判定 /
manifest schema；零真机调用）

**Target Platform**: Linux（本机编排）+ 远端超导芯片（Baihua、Shenglian，经工具链提交）

**Project Type**: 硬件实验编排（thin orchestration over `qmeas.benchmark`）

**Performance Goals**: N/A（机时由账单决定，不追求吞吐；预览账单链约
`2×3000×4 = 24000` 任务、`≈ 4.9×10⁷` shots，环待预览枚举后确定）

**Constraints**: 未人工确认账单不得提交（spec `INV-003` 两步闸门）；单候选 `4` 电路缺一不可；
转译不得引入候选子图之外的纠缠门（正确性门，非性能项）

**Scale/Scope**: 链候选 ≤ `6000` 条、环候选全枚举（量级十余）、D07c 子链 `10` 条
（+ 可能补测）、S04 冠军 `2` 项（+ 可能并列）

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- I（Spec 权威）：候选 / 电路 / 打分 / 截断 / 阈值 / 输出 / 验证全在 spec；
  本 plan 只定采样排序聚合函数、卫生过滤阈值、诊断阈值、记录方式等 spec
  明确授权 plan 的细则，不增删实验语义。PASS。
- II（分离）：不碰 `doc/theory/`；plan 只含实现决策。PASS。
- III（边界）：复用 `qmeas.benchmark` 而不在 exp05 内重实现枚举 / 电路 /
  打分；`qmeas` 侧轮询器 Failed 缺口不在本 feature 内修（见 §3 对账层），
  不建跨 feature 新共享框架。PASS。
- IV（可重复）：拓扑快照（含 `calibration_time`）+ 逐候选增量落盘 +
  manifest（芯片 / 快照标识 / 采样种子 / 过滤阈值 / shots / 栈版本 /
  schema `exp05/v1`）+ 提交/收回逐任务对账。PASS。
- V（正确性优先）：转译 pin 死 + CZ 一一保留检查为硬门；采样截断只减候选数，
  不改变单候选测量语义；预览零机时。PASS，无嵌套并行（提交并发由工具链
  内部控制，本侧不叠加线程池）。
- VI（风格）：Python 经统一解释器（见 §3 解释器决策）；出图走
  `scripts/figure_style.py`，mathtext，矢量 PDF + 300dpi PNG。PASS。

## Project Structure

### Documentation (this feature)

```text
specs/exp05/
├── spec.md               # 实验定义（已定，Q1–Q6 全闭）
├── plan.md               # 本文件
└── tasks.md              # tasks 阶段产出（非本 plan 创建）
```

### Source Code (repository root)

```text
scripts/
├── exp05_preview.py      # 离线预览：拉拓扑（缓存优先）→ 枚举 → 采样截断 → 打印账单（零机时）
├── exp05_prescreen.py    # 静态预筛：边保真度卫生过滤 → survivors/剔除清单
├── exp05_submit.py       # 真机提交：人工确认后提交 → 增量落盘 → 对账 → Failed 重跑
├── exp05_assemble.py     # 组装：checkpoints → 打分验算 → D07a/D07b/D07c/S04.npz + manifest
├── verify_exp05.py       # 生产断言（见 §4，对正式输出全量执行）
├── plot_D07.py             # D07a/D07b 前十排名图 + D07c 子链排名图 → figs/exp05/
data/exp05/
├── topology_cache/       # 拓扑快照（文件名含 calibration_time）
├── checkpoints_chain/    # 链逐候选结果（复用 qmeas io，中断续跑只补缺失）
├── checkpoints_ring/     # 环逐候选结果（同上）
├── exp05_D07a.npz / exp05_D07b.npz / exp05_D07c.npz / exp05_S04.npz
└── exp05_manifest.json   # schema exp05/v1（见 §2）
figs/exp05/
test/
└── test_exp05_local.py   # pytest：去重/打分/join/并列/manifest（零真机调用）
```

**Structure Decision**: 单项目薄编排结构。Julia 侧（`src/`）零新增——本实验无数值
内核；Python 侧 6 个脚本各司一职，不抽公共库（`qmeas.benchmark` 即公共层，
不再包一层 wrapper 模块，避免抽象提前）。产品层 npz 落 `data/exp05/`，
与 exp01–04（`data/expXX/`）同惯例。

## 1. 实现思路

- 数据流：拓扑拉取（缓存优先，命中零请求；快照记 `calibration_time`）→
  链 `sample_chains` 枚举 + 无向去重 → 按静态边保真度排序截断（每芯片 ≤3000，
  去重后计数；不足则有多少测多少）→ 环 `find_rings` 全枚举（旋转/翻转去重
  由内核保证）→ 预筛卫生过滤（见 §3 阈值）→ 预览打印账单（任务数 / shots 总数 /
  快照标识）→ **人工确认** → 提交（`run_benchmark`，逐候选 4 电路，shots 2048，
  checkpoints 增量落盘）→ 对账层（tid 清单 vs 收回结果，Failed 显式 query +
  单条重跑；checkpoint 只记收回成功者，已收回永不重提）→ 组装
  （`score_chain` 复算验算 + 排名 + 并列判定 + D07c join/补测 + S04）→
  verify 全量断言 → 出图。
- D07c join：冠军环的 10 条连续 8-子链（环顺序滑窗，含跨起点/终点闭合段），
  逐条在链 evidence 中匹配（同芯片 + 序列相等或反转相等）→ 命中则引用
  （记来源 + 被引用候选 id，可追溯）；未命中则走补测小批量（同基准电路与
  shots，同样提交/对账/落盘），来源记补测。
- S04：冠军 8 链 + 冠军 10 环各自（芯片，物理比特表，拓扑快照标识）；
  首名分差 `< 0.02` 时并列者全部记入（链 / 环各自判定）。

## 2. 代码与模块结构

- `scripts/exp05_preview.py`：`fetch_topology(force=False)`（缓存优先）→
  `build_chains`/`find_rings` → 去重计数 → 排序截断 → `bill()` 打印账单
  （每芯片候选数 / 总任务数 / 总 shots / 快照 `calibration_time`）；只读，
  不提交、不落盘（除拓扑缓存命中写入）。
- `scripts/exp05_prescreen.py`：`usable_edges` + `chain_is_valid`/`ring_is_valid`
  静态过滤（阈值见 §3）→ `data/exp05/prescreen_{chain,ring}.json`
 （survivors / 剔除清单 + 阈值 + 快照引用）。
- `scripts/exp05_submit.py`：读 survivors → `build_circuits(n, ring)` →
  转译 pin（`coupling_map` 即候选边，`optimization_level` 不许吃 CZ，见 §3）→
  `run_benchmark` → 对账层（§3）→ checkpoints；支持中断续跑（只补缺失）。
- `scripts/exp05_assemble.py`：读 checkpoints → `score_chain` 复算
  （与落盘值比对，不一致报错）→ 链 / 环各自排序 → 前十 + 全量 evidence →
  并列判定（`0.02`，spec `POST-005`）→ D07c join/补测清单 → 写
  `exp05_{D07a,D07b,D07c,S04}.npz` + `exp05_manifest.json`
 （含芯片、快照标识、`rng_seed`、过滤阈值、shots、`w_stab/w_ro`、
  工具栈名与版本、schema `exp05/v1`）。
- `scripts/verify_exp05.py`：见 §4。
- `scripts/plot_D07.py`：三排名图（前十 score + `S̄`/`F_ro` 分解；
  D07c 十条子链 + 来源标注引用/补测；冠军/并列高亮）。
- `test/test_exp05_local.py`：链无向去重、环旋转/翻转去重、`score_chain`
  手算对照、D07c 滑窗（含闭合段）与反转匹配、并列边界（`0.0199` 并列 /
  `0.0201` 不并列）、manifest 必填字段。

## 3. 数值与技术决策

- 解释器：真机相关脚本（preview / prescreen / submit）必须用 qmeas env python
  （`03_tools_practice/qmeas/.CondaPkg/.pixi/envs/default/bin/python`，
  含 qmeas editable + quarkstudio/quarkcircuit），不另建环境；
  v0.3.0 自有 env 无 qiskit/quarkstudio，不可用。
  纯本地脚本（assemble / verify / plot / pytest）统一用同一 qmeas env，
  保证 import 一致。manifest 记录解释器路径 + `qmeas` 版本 + git commit +
  `quarkstudio`/`quarkcircuit` 版本（Q6 落实：沿用现有工具链，只记录版本）。
- 采样排序聚合函数：链按其 7 条边静态保真度的**均值**降序（plan 级细则；
  备选最小值过于保守，均值与旧经验一致，记入 manifest 以保可重复）。
  `sample_chains` 的 `rng_seed` 固定（具体值 implement 定，记入 manifest）；
  先去重后截断（spec `PRE-001`：去重后计数）。
- 卫生过滤阈值：静态边保真度 `< 0.9` 的边所在候选剔除（plan 级细则；
  spec 授权 plan 定；阈值与剔除数记入 prescreen 清单 + manifest）。
  过滤后不足 3000 即有多少测多少，不降阈凑数。
- 转译 pin：`coupling_map` 取候选边集，逻辑比特按候选顺序映射；
  提交前断言转译后 CZ 数 == 候选边数（链 7 / 环 10）且作用比特集 ⊆ 候选
  （verify 硬门，见 §4）；优化器吃掉任一 CZ 即判该候选转译 invalid，不送测。
- Failed 对账层（exp05 侧加固，不改 `qmeas`，宪法 III）：
  维护（芯片，候选 id）→ tid 清单；收回后逐项对账；平台 `result()` 对 Failed
  返回空（与排队中不可区分）→ 显式 query 任务状态，Failed 单条重跑；
  重跑仍 Failed 则标记（verify 判 invalid，不静默丢弃）。
  历史教训（重启 resume 重提旧任务）→ 本侧规则：有 tid 只轮询不重提，
  checkpoint 以收回成功为准。
- 可信度诊断阈值（spec 授权 plan，只记录不作硬门）：冠军 `S̄` 若 `> 0.95`
  （与理想值 `1.0` 偏离不足）则标记可疑（疑似 CZ 未真实执行），需人工核查；
  全榜 `S̄` 按 score 单调退化检查， Spearman 系数记入诊断（不设门）。
- D07c 闭合段：环滑窗 10 条含跨接缝段（如比特 `[138,125,...]`），匹配时同样
  适用反转等价；补测候选同样先过转译 pin 断言。

## 4. 验证方案（覆盖 spec Contract F）

- `verify_exp05.py` 对正式输出全量执行，逐条映射 spec `VAL-001..VAL-008`：
  - 每候选 4 电路齐全，无缺失/NaN；`S̄ ∈ [-1,1]`，`F_ro ∈ [0,1]`；
    快照含 `calibration_time`。
  - 提交/收回对账：tid 清单 == 收回成功集 + 明确标记集；无静默丢弃；
    checkpoints 与 npz evidence 逐候选一致（`score_chain` 复算比对）。
  - 转译门：每候选转译后 CZ 数 == 边数且比特集 ⊆ 候选（由 submit 侧留存
    转译后电路摘要供查）。
  - D07c 每条子链来源可追溯（引用链候选 id / 补测任务 tid）。
  - 并列判定复算（阈值 `0.02`）。
  - 诊断输出（非门）：冠军 `S̄` 可疑标记（`> 0.95`）、退化单调性、
    稳定子–读出相关系数（权重事后验证线索）。
- invalid 触发任一条即相关候选（或整批）判 invalid，不得出图/入库；
  verify 非零退出并指明候选 id。
- 出图前人工核对：D07a/D07b 榜单与 npz 一致、D07c 来源标注正确、S04 比特表
  与快照拓扑相容（候选边确为可用边）。

## Complexity Tracking

本次 plan 无宪法违反，无需记录。
