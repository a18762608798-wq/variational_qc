# Implementation Plan: exp01 有限尺寸相图

## 1. 实现思路

- 主要模块：`ReducedDensity`（约化密度矩阵内核）、`ZTilde`（`Z_R` 与归一化）、
  `Store`（分块增量落盘 + 断点续算 + D01 组装）、薄编排脚本 `scripts/run_exp01.jl`、
  出图脚本 `scripts/plot_D01D05.py`（D01 裸图 + 三对标记与配对箭头叠加得 D05）。
- 数据流：S01（`data/shared01`，经 `Shared01.Store.load_shared01` 读取，
  shared-01 保持开放引用）→ 逐点求 `ρ_I`、`ρ_I1`、`ρ_I2` → `~Z_R` →
  按 `δ` 行分块增量落盘 → 组装 D01 单文件 + manifest → Python 出 D01 裸图，
  再叠加三对标记与配对箭头得 D05。
- 核心算法：对 `256` 维基态矢作显式偏迹（`I=(3,4,5,6)` 等定义见 spec `PRE-003`），
  `R_I` 中央键镜像交换收缩得 `Z_R`，再归一化；各点完全独立。
- 关键技术选择：数值全部在 Julia；出图全部在 Python（`scientific-figure-style`，
  经项目内 `scripts/figure_style.py` 统一风格），
  以 `.npz` 为界，Python 不重算任何物理量。

## 2. 代码与模块结构

新增（全部归属本 feature，不建跨 feature 共享框架）：

- `src/Exp01/ReducedDensity.jl`：`reduced_density_matrix(psi, keep_sites)` 纯内核，
  不含 I/O；基矢约定（`site m ↔ bit(m-1)`）运行时断言 S01 manifest 记录一致，
  不一致直接失败，不静默适配。
- `src/Exp01/ZTilde.jl`：`z_tilde(psi)` 返回 `(z_R, z_tilde, rho_trace, rho_min_eig, denom)`，
  诊断量随结果一并返回供验证使用。
- `src/Exp01/Store.jl`：按 `δ` 行（99 行）分块写 `.npz` + 完成表 manifest，
  续算跳过已完成行；全行完成后组装 `exp01_D01.npz`（`z_tilde[99,99]`、
  诊断数组、简并标记继承列）与 `exp01_manifest.json`（输入 S01 标识、阈值、schema）。
- `scripts/run_exp01.jl`：薄编排，只做输入校验、调模块 API、落盘，不含数值方法。
- `scripts/plot_D01D05.py`（替代旧 `plot_D05.py`）：读 D01 + 三对标记元数据，
  先出 D01 裸图（无标记热力图），再叠加三对标记与配对箭头出 D05；
  两图坐标系一致性由脚本自检（见 §4）；风格经 `figure_style.py` 统一（见 §3）。
- `scripts/figure_style.py`：出图风格助手的项目内同源拷贝（来源 skill 版本注记在案），
  出图脚本只调它，不手调 rcParams。
- `test/runtests.jl`：见第 4 节。
- S01 读取复用 `Shared01.Store.load_shared01`（kept-open 的生产者、schema 已 pin，
  行为有测试覆盖）；不复制一份 reader，不做跨 task 的新抽象。

## 3. 数值与技术决策

- 数值方法：稠密显式偏迹 + 直接收缩。理由：`256` 维下每点毫秒级，
  精确无近似；各点独立，天然可并行。
- 精度：`ComplexF64` 全程；硬断言阈值取 `|Trρ − 1| < 1e-10`、
  `ρ` 最小本征值 `> −1e-10`、分母 `> 1e-12`（能量/迹量级 O(1–10 下留足余量；
  纯实现层选择，不改变实验语义）。
- 并行：`Threads.@threads` 按行遍历，`BLAS.set_num_threads(1)`（宪法 V：
  禁止 Julia 线程 × BLAS 线程嵌套 oversubscription；shared-01 实测教训），
  输出按网格顺序确定，与线程数无关。
- 增量落盘（宪法 IV）：禁止全量驻内存 + 单文件收尾；按 `δ` 行分块 `.npz`
  即算即存，中断后凭完成表续算，最终再组装 D01 单文件（组装为纯拼接，
  不改变数值）。
- 出图（`scientific-figure-style`，实现层选择）：`figure_style.py` 统一风格，
  不手调 rcParams；轴标签用 mathtext（`$s$`、`$\delta$`、`$\tilde{Z}_R$`）；
  三对配对色取 Okabe-Ito 顺序，终点统一五角星（与起点圆点相异；
  对间区分靠配对色 + 箭头，用户既定样式）。
  导出矢量主件（PDF）+ 300dpi PNG 预览，落 `figs/exp01/`（D01 裸图与 D05 各一套）。
- 关键依赖：Julia `LinearAlgebra`（stdlib）、`NPZ.jl`、`JSON3.jl`（已冻结于
  `Project.toml`/`Manifest.toml`）；Python 侧 numpy + matplotlib（CondaPkg，
  implement 阶段如缺再补）。

以上均为实现层选择；网格、子系统取法、输出内容与验证条件沿用 spec，未改动实验语义。

## 4. 验证方案

spec 验证条件的落实（硬断言，失败即 invalid）：

- 输入门控：S01 文件存在且 schema 为 `shared01/v1`，基矢约定字符串与预期一致，
  否则拒绝执行。
- 逐点：`|Trρ_I − 1| < 1e-10`、`ρ_I` 最小本征值 `> −1e-10`、分母 `> 1e-12` 且有限；
  D01 无缺失、无 NaN；坐标与 S01 逐点一致；简并标记与 S01 manifest 逐点一致。
- D01 裸图：与数据集同坐标系（脚本自检断言），无缺失、无标记残留。
- D05：底图坐标系与 D01 一致（脚本自检断言）；三对标记坐标/配对与 spec `PRE-004` 一致；
  每对一起点一终点一箭头，无多标、无漏标。
- 单元测试：偏迹内核对直积态/已知小例的正确性；`R_I` 对合性（`R^2 = 1`）；
  S02 三点端到端（`load → z_tilde`）可运行。

诊断量（只记录、不设通过阈值）：

- `~Z_R` 全网格分布摘要（最小/最大/分位数），供相图解释参考。

出图风格检查（按 skill 报告块，出图后附）：palette / fonts / lines /
redundancy（色 + 形 + 箭头）/ export（PDF 矢量 + PNG 300dpi）/ remaining risk。

## 5. 未解决问题 / 延后工作

- 无阻塞实现的未解决问题（示范终点已随 spec 落定三对坐标）。
