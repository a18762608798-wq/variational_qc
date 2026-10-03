# Tasks: exp06 真机测量与比较

**Feature:** exp06

任务必须来源于 `spec.md` 和 `plan.md`。
不得在 tasks 阶段引入新的实验定义。

> 前置阻塞（analyze H1/M1）：
> - H1 已解决（spec §5 已加转译验路断言条目，plan §4 已加对应检查）——
>   T003/T007 转译门可按新条目执行。
> - M1 已解决（取证完成，证据见 plan §3 M1 取证结论；旧称统一为
>   `correct=False`）——T000 转为提交前复核：确认提交代码未改动
>   `correct` 默认（`False`）并留存参数。

## Implementation

- [x] T000 提交前复核 `correct` 默认（M1 取证已关闭）：确认提交代码
  未改动 `QuarkOptions.correct` 默认（`False`），提交参数逐批留存备查。
  完成条件：复核通过；若被改动则停，返工 plan，不进 T003。
- [x] T001 实现 `scripts/exp06_circuits.py`：`build_init(a*)`（单态/GHZ，
  与 psi0 解析式逐振幅对照）、`build_ansatz(theta,a*,p,delta)`
  （轨道配对/`δ=0` 减半/子层顺序/`RXX/RYY/RZZ` 单键，对应表写进 docstring）、
  `build_estimator_circuit`（+全 `Z` 测量）、`build_calib_circuits`
  （全 `0` / 全 `X`）。
  完成条件：模块可加载，a*=1/2/3 初态振幅正确（由 T006 锁定）。
- [x] T002 编写 `scripts/exp06_preview.py` 并执行离线预览：S03 读入 →
  稀疏过滤（`s_idx∈{1,4,…,97}`，198 组；S03 缺组标 invalid）→ 66 批划分
  （3 组/批，批次 id 固定）→ 账单（VQE 990 + 标定 132 = 1122 任务，
  快照/S03 引用，`confirmed=false`）。
  完成条件：账单已打印、经人工确认（确认记录留存），零机时，
  未确认前不得进入 T003。
- [ ] T003 编写 `scripts/exp06_submit.py`（转译 opt3/显式 coupling_map；
  对账补跑沿用 exp05 模式）并执行真机提交（人工确认 + T000 通过后）：
  逐批（VQE ×5 独立 tid + 标定 2，`correct=False` 参数留存），
  增量落盘 `data/exp06/batches/<bid>/`，中断续跑只补缺失。
  完成条件：66 批全收回（或明确标记），无静默丢弃，无已收回重提。
  转译门执行待 H1 解决（见文件头）。
- [ ] T004 编写 `scripts/exp06_assemble.py` 并组装产品：S05 矩阵 →
  Kronecker-`M⁻¹` 缓解 + 非负约束 → `S(π)`/string（公式只读复刻 Exp02）→
  写 `data/exp06/exp06_D11.npz`（缓解后均值/std/每重复三件套/S03 与 S05
  引用）+ `exp06_D12.npz`（D12 组装归本任务：D10 对应组引用值 + 各自
  min-max 归一化，区间记入 manifest）+ `exp06_manifest.json`
  （schema `exp06/v1`，含归一化区间记录）。
  完成条件：D11 + D12 + manifest 落盘，198 组齐全（invalid 组除外，
  另行标记）。
- [ ] T005 编写 `scripts/plot_D11D12.py` 并出图：D11 四面板
  （`2δ × {S(π), string}`，`p=1,2,3` 三色散点 + 误差棒）；
  D12 同版式归一化比较（只读 T004 的 D12 出图，不生产数据；
  真机组 + D10 引用线，归一化区间与 manifest 一致）；
  `figure_style.py` 风格，mathtext，矢量 PDF + 300dpi PNG 落 `figs/exp06/`。
  完成条件：组/误差棒与 npz 一致，D12 归一化可复算。

## Validation

- [x] T006 本地单元测试（`test/test_exp06_local.py`，pytest，全绿，
  零真机调用，建议 T002 前先行）：初态振幅对照；单键酉对照；
  **Aer 黄金交叉**（抽样点 vs D10，`1e-8`，不通过不得进 T003）；
  缓解恒等式；D12 归一化；manifest 必填字段。
- [ ] T007 生产断言（`scripts/verify_exp06.py`，对正式输出全量执行，
  逐条映射 spec §5）：每组 5 重复齐全；三件套存档完整性（逐组查 counts +
  缓解前 + 缓解后三样落盘，缺一报错）；`θ` 与 S03 逐元一致
  （`NaN`-pad 区除外）；S05 批次 id 同批；`correct=False` 留存可查；
  转译验路断言（边集落入允许集，见 spec §5）；对账一致；
  invalid 任一触发非零退出指明组；诊断输出
  （缓解前后差/离散度标记/D12 目检提示，只记录）。
  完成条件：全量通过。
