# Tasks: exp02 拓扑物理量

**Feature:** exp02

任务必须来源于 `spec.md` 和 `plan.md`。
不得在 tasks 阶段引入新的实验定义。

## Implementation

- [x] T001 实现 `src/Exp02/Correlators.jl`：`zz_correlators(psi)`（`8×8` 实对称，
  对角构造性为 `1`）与 `structure_factor(C, q)` 纯内核；基矢约定运行时断言
  S01 manifest 一致。
  完成条件：模块可加载，直积态关联矩阵正确（由 T006 断言锁定）。
- [x] T002 实现 `src/Exp02/StringOrder.jl`：`string_order(psi)`（`d=3` 对角加权求和），
  纯内核。
  完成条件：S02 三点可出值且有限。
- [x] T003 实现 `src/Exp02/Panels.jl`：逐点组装 `(Sπ, Ostr, Q, Zt)`；
  `Q` 代数组合；`~Z_R` 只读调用 `Exp01.z_tilde`（不改 exp01 代码）。
  完成条件：单点四元组完整且 `Q` 恒等式在构造层成立。
- [x] T004 实现 `src/Exp02/Store.jl`：D04 按 `δ` 行分块 `.npz` + 完成表续算；
  D03 三曲线独立文件；组装 `exp02_D03.npz`、`exp02_D04.npz` + manifest。
  完成条件：中断续算一致（删块重跑组装不变）。
- [x] T005 编写 `scripts/run_exp02.jl`（S01 输入门控 → 模块 API → 分块落盘 → 组装）
  并执行全网格生产 + D03 三曲线计算。
  完成条件：D03/D04 文件 + manifest 落盘，形状与坐标与 S01 一致。
- [x] T006 出图（`scripts/plot_D03D04.py`）：D03 三线同图 + D04 四联热力图
  （`(a)–(d)` 按 outline 顺序，mathtext 标签，`figure_style.py` 风格，
  矢量 PDF + 300dpi PNG 落 `figs/exp02/`；D03 横坐标刻度为 `0, π/2, π, 3π/2, 2π`，
  保留 `q=π` 半截竖线（仅从峰值圆点向下）与峰值圆点标记，无额外 `π` 轴外文本）。
  完成条件：坐标系自检通过，三线标签与代表点对应，四联顺序正确，
  D03 刻度与标记检查通过，附 skill 风格检查报告块。

## Validation

- [x] T007 单元测试（`test/runtests.jl` 追加，全绿）：关联矩阵解析小例；
  string 小例；`q=π` 交错和恒等式；S01 输入门控拒绝路径。
- [x] T008 生产断言 [VAL-001..VAL-007]（对正式输出全量执行）：`S(q) ≥ −1e-12`；
  D03↔D04 `S(π)` bit 一致；`Q` 恒等式残差 `< 1e-12`；
  D04(d) 与 D01 逐点相等；无缺失、无 NaN；简并标记逐点一致。
