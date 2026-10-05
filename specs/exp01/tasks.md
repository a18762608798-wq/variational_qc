# Tasks: exp01 有限尺寸相图

**Feature:** exp01

任务必须来源于 `spec.md` 和 `plan.md`。
不得在 tasks 阶段引入新的实验定义。

## Implementation

- [x] T001 实现 `src/Exp01/ReducedDensity.jl`：`reduced_density_matrix(psi, keep_sites)`
  纯内核（无 I/O）；基矢约定运行时断言 S01 manifest 记录一致，不一致直接失败。
  完成条件：模块可加载，直积态偏迹得正确约化态（由 T006 断言锁定）。
- [x] T002 实现 `src/Exp01/ZTilde.jl`：`z_tilde(psi)` 返回
  `(z_R, z_tilde, rho_trace, rho_min_eig, denom)`；`R_I` 为中央键镜像交换。
  完成条件：S02 三点可端到端出值且诊断量随附。
- [x] T003 实现 `src/Exp01/Store.jl`：按 `δ` 行（99 行）分块 `.npz` 即算即存 +
  完成表 manifest，续算跳过已完成行；全行完成后组装 `exp01_D01.npz` 与
  `exp01_manifest.json`（输入 S01 标识、阈值、schema）。
  完成条件：中断模拟（先跑若干行后停）可续算且组装结果与一次跑通一致。
- [x] T004 编写 `scripts/run_exp01.jl`（薄编排：S01 输入门控 → 调模块 API →
  分块落盘 → 组装）并执行全 `99×99` 点生产。
  完成条件：`exp01_D01.npz` + manifest 落盘，形状 `99×99`、坐标与 S01 一致。
- [x] T005 出图（`scripts/plot_D01D05.py`，替代旧 `plot_D05.py`）：
  先将 skill 的 `figure_style.py` 同源拷贝进 `scripts/`（来源版本注记）；
  脚本读 D01 先出 D01 裸图，再叠加三对标记与配对箭头出 D05 定稿图
  （三对坐标/配对取自 spec `PRE-004`，三对各一色、终点三形互异、mathtext 轴标签）；
  输出 D01/D05 各一套矢量 PDF + 300dpi PNG，落 `figs/exp01/`；
  旧预览图与旧脚本归档或删除，不保留双轨。
  完成条件：两图坐标系自检通过，三对“一起点一终点一箭头”计数无误，
  附 skill 风格检查报告块。

## Validation

- [x] T006 单元测试（`test/runtests.jl`，全绿）：偏迹内核已知小例正确性；
  `R_I` 对合性（`R^2 = 1`）；S01 输入门控（缺失/schema 不符/基矢约定不符均拒绝）。
- [x] T007 生产断言 [VAL-001..VAL-005]（对正式 D01 输出全量执行）：逐点 `|Trρ − 1| < 1e-10`、
  `ρ` 最小本征值 `> −1e-10`、分母 `> 1e-12` 且有限；无缺失、无 NaN；
  简并标记与 S01 manifest 逐点一致。（D05 图核对移至 T005。）
