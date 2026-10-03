# Implementation Plan: exp02 拓扑物理量

## 1. 实现思路

- 主要模块：`Correlators`（`ZZ` 关联矩阵 + `S(q)`）、`StringOrder`（`O_str` 对角期望）、
  `Panels`（四联组装：`S(π)` / string / `Q` / `~Z_R`）、`Store`（分块增量落盘 +
  断点续算 + D03/D04 组装）、薄编排 `scripts/run_exp02.jl`、出图
  `scripts/plot_D03D04.py`（D03 三线图 + D04 四联热力图）。
- 数据流：S01（经 `Shared01.Store` 读取）→ 逐点求关联矩阵 → `S(π)`、string、
  `Q` 代数组合；`~Z_R` 复用 `Exp01.ZTilde` 内核独立重算（定义同一，数值必一致）；
  D03 取 S02 三坐标条目在 q 网格上求值 → 分块落盘 → 组装 → Python 出图。
- 核心算法：`Z` 型算符在计算基下对角，期望化为振幅模方加权求和——
  `C_ij` 为 64 个 `±1` 加权和，`S(q)` 为 `C` 的离散傅里叶加权，
  string 为串算符本征值加权和，`Q` 为三数代数组合；各点完全独立。
- 关键技术选择：数值全部在 Julia；出图全部在 Python（`figure_style.py` 已收编），
  以 `.npz` 为界，Python 不重算任何物理量。

## 2. 代码与模块结构

新增（全部归属本 feature，不建跨 feature 共享框架）：

- `src/Exp02/Correlators.jl`：`zz_correlators(psi)`（`8×8` 实对称，`C_ii = 1` 构造性保证）、
  `structure_factor(C, q)` 纯内核，不含 I/O；基矢约定复用 S01 manifest 断言
  （与 exp01 同字符串，不一致直接失败）。
- `src/Exp02/StringOrder.jl`：`string_order(psi)`，`d = L/2−1 = 3`，
  按 `O_str` 定理对角本征值加权求和；纯内核。
- `src/Exp02/Panels.jl`：逐点组装 `(Sπ, Ostr, Q, Zt)` 四元组；
  `Q = 4/3 + 2 O_str − S(π)/6`；`~Z_R` 调用 `Exp01.ZTilde.z_tilde`（只读复用，
  不修改 exp01 代码；定义同一保证 D04(d) 与 D01 数值一致）。
- `src/Exp02/Store.jl`：D04 按 `δ` 行分块 `.npz` + 完成表（同 exp01 模式，
  任务内实现）；D03 三曲线独立小文件；组装 `exp02_D03.npz`、`exp02_D04.npz` +
  `exp02_manifest.json`（输入 S01 标识、q 网格、阈值、schema）。
- `scripts/run_exp02.jl`：薄编排（S01 输入门控 → 模块 API → 分块落盘 → 组装）。
- `scripts/plot_D03D04.py`：D03 三线同图 + D04 四联热力图（`(a)–(d)` 按 outline 顺序），
  风格经 `figure_style.py`，mathtext 标签，矢量 PDF + 300dpi PNG，落 `figs/exp02/`；
  坐标系自检见 §4。
- `test/runtests.jl`：在既有文件追加 Exp02 testsets（见 §4）。

## 3. 数值与技术决策

- 数值方法：对角期望直接振幅求和 + 小矩阵代数，无稠密大矩阵、无近似；
  `~Z_R` 沿用已验证内核。理由：`L=8` 下精确且每点毫秒级。
- 精度：`ComplexF64` 振幅，关联量取实部（虚部为 roundoff，测试中断言量级）；
  硬断言阈值 `|S(q)|负值容限 < 1e-12`、D03↔D04 `S(π)` 逐点相等（同一内核，
  bit 一致）、`Q` 恒等式残差 `< 1e-12`、D04(d) 与 D01 逐点相等
  （同一内核同一输入；纯实现层选择，不改变实验语义）。
- 并行：`Threads.@threads` 按行遍历，`BLAS.set_num_threads(1)`（宪法 V）。
- 增量落盘（宪法 IV）：D04 按 `δ` 行分块即算即存 + 完成表续算，组装为纯拼接；
  D03 量小（3×99），随行计算、独立成文件。
- 出图：matplotlib + `figure_style.py`，只读 D03/D04 与版式元数据。
- 关键依赖：Julia `LinearAlgebra`（stdlib）、`NPZ.jl`、`JSON3.jl`（已冻结）；
  Python 侧沿用 CondaPkg（numpy + matplotlib，现成）。

以上均为实现层选择；网格、观测量定义、输出内容与验证条件沿用 spec，未改动实验语义。

## 4. 验证方案

spec 验证条件的落实（硬断言，失败即 invalid）：

- 输入门控：S01 存在且 schema 为 `shared01/v1`，基矢约定一致，否则拒绝执行。
- 逐点/逐曲线：`S(q) ≥ −1e-12`；`C` 实对称且对角为 `1`；
  D03 代表点 `q=π` 取值与 D04(a) 同坐标条目 bit 一致；
  `Q − (4/3 + 2O_str − S(π)/6)` 残差 `< 1e-12`；
  D04(d) 与 D01 `z_tilde` 逐点相等；无缺失、无 NaN；简并标记与 S01 逐点一致。
- 出图：D03 三线与代表点/相标签对应；D04 `(a)–(d)` 顺序与版式一致；
  底图坐标系与 D04 数据一致（脚本自检断言）。
- 单元测试：直积态/单态对的关联矩阵与 `S(q)` 解析值；string 小例；
  `q=π` 退化为交错和恒等式。

诊断量（只记录、不设通过阈值）：

- D03 三曲线峰位摘要；D04(d)−D01 差值摘要（预期为零，作一致性证据）。

出图风格检查（按 skill 报告块，出图后附）。

## 5. 未解决问题 / 延后工作

- 无阻塞实现的未解决问题。
