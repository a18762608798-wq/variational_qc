# Tasks: exp05 真机优质比特

**Feature:** exp05

任务必须来源于 `spec.md` 和 `plan.md`。
不得在 tasks 阶段引入新的实验定义。

## Implementation

- [x] T001 编写 `scripts/exp05_preview.py` 并执行离线预览：缓存优先拉拓扑
  （Baihua + Shenglian，快照记 `calibration_time`）→ 链枚举 + 无向去重 +
  边保真度均值排序截断（每芯片 ≤3000，去重后计数）→ 环全枚举 →
  `bill()` 打印账单（每芯片候选数 / 总任务数 / 总 shots / 快照标识）。
  完成条件：账单已打印、经人工确认（确认记录留存），零机时，
  未确认前不得进入 T003。
- [x] T002 编写 `scripts/exp05_prescreen.py` 并执行静态预筛：
  边保真度 `< 0.9` 所在候选剔除 → `data/exp05/prescreen_{chain,ring}.json`
  （survivors / 剔除清单 + 阈值 + 快照引用）。
  完成条件：清单落盘，剔除数与阈值可审计；过滤后不足 3000 不凑数。
- [x] T003 编写 `scripts/exp05_submit.py`（含 exp05 侧 Failed 对账层：
  tid 清单 vs 收回结果逐项对账，Failed 显式 query + 单条重跑，
  有 tid 只轮询不重提）并执行真机提交（人工确认后）：
  链 + 环每候选 4 电路（shots 2048），转译 pin 前置断言
  （CZ 数 == 边数且比特集 ⊆ 候选），增量落盘
  `data/exp05/checkpoints_{chain,ring}/`，中断续跑只补缺失。
  完成条件：survivors 全收回成功（或明确标记），无静默丢弃，
  无已收回重提。
- [x] T004 编写 `scripts/exp05_assemble.py` 并组装产品：
  `score_chain` 复算验算 → 链/环各自排序 → 前十 + 全量 evidence →
  并列判定（`0.02`）→ D07c join（冠军环 10 条滑窗子链，同芯片 + 序列/反转
  匹配引用，未命中走补测小批量，同电路/shots/对账）→ 写
  `data/exp05/exp05_{D07a,D07b,D07c,S04}.npz` + `exp05_manifest.json`
  （schema `exp05/v1`，含芯片/快照标识/`rng_seed`/过滤阈值/shots/
  栈名与版本/解释器路径）。
  完成条件：四产品 + manifest 落盘，D07c 每条子链来源可追溯，
  S04 比特表与快照拓扑相容。
- [x] T005 编写 `scripts/plot_D07.py` 并出图：
  D07a/D07b 前十排名图（score + `S̄`/`F_ro` 分解，冠军/并列高亮），
  D07c 十条子链排名图（来源标注引用/补测）；
  `figure_style.py` 风格，mathtext，矢量 PDF + 300dpi PNG 落 `figs/exp05/`。
  完成条件：榜单与 npz 一致，D07c 来源标注正确。

## Validation

- [x] T006 本地单元测试（`test/test_exp05_local.py`，pytest，全绿，
  零真机调用，建议 T001 前先行）：链无向去重、环旋转/翻转去重、
  `score_chain` 手算对照、D07c 滑窗（含闭合段）与反转匹配、
  并列边界（`0.0199` 并列 / `0.0201` 不并列）、manifest 必填字段。
- [x] T007 生产断言（`scripts/verify_exp05.py`，对正式输出全量执行，
  逐条映射 spec §5）：每候选 4 电路齐全，无缺失/NaN；
  `S̄ ∈ [-1,1]`，`F_ro ∈ [0,1]`；快照含 `calibration_time`；
  tid 清单 == 收回成功集 + 明确标记集；checkpoints 与 npz evidence
  逐候选一致（复算比对）；转译门（CZ 数与比特集）留存可查；
  D07c 来源可追溯；并列复算（`0.02`）；诊断输出（冠军 `S̄ > 0.95`
  可疑标记、退化单调性、稳定子–读出相关系数，只记录）。
  完成条件：全量通过，任一 invalid 非零退出并指明候选 id，
  不得出图/入库。
