# Implementation Plan: exp04 模拟机 VQE

## 1. 实现思路

- 主要模块：`InitStates`（三初态构造）、`Ansatz`（orbit 电路态矢量作用）、
  `VQELoop`（代价 + 参数移位梯度 + 全局采样 + L-BFGS + 同路链式 warm start）、
  `Store`（按 `δ` 分块增量落盘 + 断点续算 + S06/S03 组装）、
  薄编排 `scripts/run_exp04.jl`、生产断言 `scripts/verify_exp04.jl`、
  出图 `scripts/plot_S06.py`（4 诊断图：`2δ × {S(π), string}`，`p=1,2,3` 同图，
  非论文产品）与
  示意 `scripts/plot_D06.py`（D06a–c 三分相拟设结构示意图，零数据输入）。
- 数据流：无外部输入（自含）→ 每 `(δ,s)` 三初态各一路：`p=1` 全局采样 +
  L-BFGS → 同路链式 warm `p=2,3` + 精修 → 取最小路 `(θ*,E*,a*)` →
  最优态上求 `S(π)`、string（只读复用 Exp02 内核）→ 分块落盘 →
  组装 S06 + S03（同一 `θ*` 的两种视图，非两次计算）→ Python 出图。
- 核心算法：定长 `L=8`（256 维）态矢量直演；单键酉
  `U_bond(t1,t2) = RXX(t1)RYY(t1)RZZ(t2)` 合成单个 `4×4` 后按比特对直接作用
  （`O(256)`/键）；能量经 `Shared01.Hamiltonian` 全矩阵期望；
  梯度用参数移位法则（`RXX/RYY/RZZ` 皆为 `exp(−iθP/2)` 形，共享参数的梯度为
  各 occurrence 移位贡献之和，精确无差分误差）；局域优化用 `Optim.jl` L-BFGS。
- 关键技术选择：不引入 Yao.jl（`L=8` 定长直演更快、零约定对齐风险；
  用户已授权二选一）；不 rewrite 观测量（`S(π)`、string 只读复用
  `Exp02.Correlators`/`StringOrder`，基矢约定同一）；
  不用有限差分梯度（参数移位精确）；`δ=0` 参数减半为结构式
  （参数化层面 `Nθ=Lp/2`，`θ1=θ2` 非事后约束）；
  数值全部在 Julia，出图全部在 Python，以 `.npz` 为界。

以上均为实现层选择；拟设、初态、代价策略、网格、输出内容与验证条件沿用 spec，
未改动实验语义。

## 2. 代码与模块结构

新增（全部归属本 feature，不建跨 feature 共享框架）：

- `src/Exp04.jl`：父模块（仿 `Exp02.jl` 体例）。
- `src/Exp04/InitStates.jl`：`psi_triv()`、`psi_topo()`、`psi_afm`
  （`256` 维，基矢约定与 `Shared01` 同字符串，运行时断言）；纯内核。
- `src/Exp04/Ansatz.jl`：轨道/子层元数据（`L=8`：奇 `2` 轨道、偶 `2` 轨道；
  子层顺序按初态 `F/S`）、`apply_circuit!(psi, θ, meta, p)`（单键 `4×4`
  按比特对作用）、`nparams(delta, p)`、`zero_theta` 即初态（恒等层）；纯内核。
- `src/Exp04/VQELoop.jl`：`energy(θ)`（`H` 期望，`H` 只读取自
  `Shared01.Hamiltonian`）、`pshift_gradient(θ)`（参数移位精确梯度）、
  `run_leg(...)`（全局采样 + 取优 + L-BFGS 精修，返回轨迹种子与收敛旗）、
  `run_point(...)`（三路 + 同路链式 warm `p=2,3` + 取最小路）；精修均为
  two-pass（首遍跑满未收敛则以其最小点重启 fresh L-BFGS 记忆再精修一遍，
  取两者较优，iters 累加；implement 实测单遍易陷平谷 stale 曲率）；种子规则见 §3。
- `src/Exp04/Store.jl`：按 `δ` 分块 `.npz` + 完成表续算（同 exp01–03 模式，
  任务内实现）；组装 `exp04_S06.npz`（每 `(δ,s,p)`：`θ*`、`E*`、`a*`、
  `S(π)`、string、三路全量 `(θ*_a,E*_a)` + 收敛旗）与 `exp04_S03.npz`
  （全网格 `594` 组 `(δ,s,p,θ*,a*)` + 初态/拟设标识，与 S06 同值引用，
  非重算）+ `exp04_manifest.json`（`H_DEF_ID`、网格、采样数、种子主根、
  阈值、schema `exp04/v1`）。
- `scripts/run_exp04.jl`：薄编排（模块 API → 分块落盘 → 组装；生产顺序
  `δ=0 → 0.85`，点内三路、`p` 链按序，点间 `Threads.@threads`）。
- `scripts/verify_exp04.jl`：生产断言（见 §4，对正式输出全量执行）。
- `scripts/plot_S06.py`：4 诊断图 `(δ × {S(π), string})`，每图 `p=1,2,3` 三线同图
  （mathtext 标签，`figure_style.py` 风格，矢量 PDF + 300dpi PNG 落
  `figs/exp04/`）；坐标系自检见 §4。
- `scripts/plot_D06.py`：D06a–c 三分相拟设示意图（每相初态 + 所需拟设电路；
  `L=8` 轨道配对着色、一层内 `F→S` 子层（triv/afm 首动偶、topo 首动奇）、
  `p` 层堆叠、三初态图例；只画 ansatz.md 已定义元素，不虚构门）；
  保真检查为人工核对清单（见 §4）。
- `test/runtests.jl`：在既有文件追加 Exp04 testsets（见 §4）。

## 3. 数值与技术决策

- 数值方法：态矢量精确期望 + 参数移位精确梯度 + `Optim.jl` L-BFGS；
  无采样噪声、无近似。理由：`L=8` 下单次能量约微秒级，精度只受优化器收敛限制。
- 采样与种子：`p=1` 每路全局 `64` 随机点 + 零向量（spec 构造性要求），
  采样均匀分布 `[0, 4π)`（覆盖单键旋转 `4π` 周期）；
  取能最低 `4` 点各做 L-BFGS；  `p=2,3` 每路 1 个 warm 初值（旧块沿用同路最优，
  新增块置零）+ L-BFGS；种子由主根按 `(δ,s,p,a)` 确定性派生，全量记入 manifest。
- 棘轮接受门（spec §5，用户 2026-10-04 确认；仅 `p>1` 链）：精修跑满
  `MAX_ITERS` 仍未触发三判据时，若末 200 步 `ΔE < STAG_TOL=1e-4` 且
  `E ≤ 同路上一层 E* + 1e-8`，则接受并记旗 `stagnant`（`converged` 保持 false，
  两旗区分存档）；`p=1` 无此门。每步轨迹 `store_trace` 留存以供判定，
  轨迹本身不进 npz，只存 `dE_tail` 审计量。
  校准依据：实测平谷爬行约 `1e-6`/200步，`1e-4` 取其上 100 倍，
  仍比 S06 最细特征（`p` 间差 `~1e-3`）低一个量级、比真机噪声低数个量级；
  spec 把阈值授权 plan 定，此处为 plan 级校准（非降低 spec 硬门，
  `g_tol` 原封不动）。
- 收敛：L-BFGS `g_tol=1e-8` + `x_abstol=1e-10` + `f_abstol=1e-10`、最大 `1000` 迭代
  （三者任一达标即收敛，均为平稳性信号；慢尾山谷靠后两者及时止损，
  implement 实测 `p=3` 精修能量已到 `1e-4` 内但梯度长期不达标）；
  未达判据者判该路未收敛（spec invalid 门控；三路全灭则该点 invalid）。
- 精度：硬断言阈值 `E* ≤ E_init + 1e-8`（零向量采样 + 下降 refinements 的构造性落实，
  容限 cover 优化器终止抖动）；守恒量 `|⟨Z_tot⟩| < 1e-8`、
  `⟨ψ|X̄|ψ⟩` 与 `⟨ψ|R|ψ⟩` 偏离 `1` 小于 `1e-8`；拟合/恒等式无（本实验无此项）；
  S03 与 S06 `θ*` 逐点相等（同一值引用，纯实现层选择）。
- 并行：`Threads.@threads` 按 `(δ,s)` 点遍历，`BLAS.set_num_threads(1)`
  （宪法 V；主算为自研比特循环，BLAS 只进 `H` 期望与 Optim 内积）。
- 增量落盘（宪法 IV）：按 `δ` 分块（每块 `99` 点全量）即算即存 + 完成表续算，
  组装为纯拼接；总量：`198` 点 × 三路 ×（`p` 链），中断可恢复。
- 出图：matplotlib + `figure_style.py`，S06 只读数据；D06a–c 零数据输入。
- 关键依赖：新增 `Optim.jl`（L-BFGS；`Pkg.add`，`Project`/`Manifest` 更新冻结）；
  其余沿用（`NPZ.jl`、`JSON3.jl`、CondaPkg Python 侧）。

## 4. 验证方案

spec 验证条件的落实（硬断言，失败即 invalid）：

- 初态门控：三初态范数为 `1`、`Z_tot=0`、`X̄/R` 本征 `+1`（构造性断言，
  测试层 + 生产前冒烟）。
- 逐点/逐路：`E*_a ≤ E_a(init) + 1e-8`；终态守恒量三项容限内；
  `δ=0` 参数计数 `= Lp/2`（结构式）；收敛旗全真（任一路未收敛即该路 invalid，
  三路全灭则点 invalid）；无缺失、无 NaN；`a*` 为三路最小能量对应路
  （并列取首个，能量差 `< 1e-12` 时记诊断）；
  精确 energies 交叉：每点经 `build_hamiltonian(8)` 暴力本征值得精确 `E0`
  （`L=8` 下毫秒级），硬断言 `E* ≥ E0 − 1e-8`（变分原理，只读复用
  `Shared01.Hamiltonian`，不属新实验），`E*−E0` 分布记诊断（解质量度量）；
  收敛旗逐路断言 `converged || stagnant`，`stagnant` 仅出现在 `p>1` 且须同时
  满足 `dE_tail < 1e-8` 与棘轮不等式（由存档值重算锁定）。
- 组装：S03 `594` 组形状与 `(δ,s,p)` 网格一致；S03 `θ*` 与 S06 同点值相等；
  manifest 主根/采样数/阈值齐全。
- 出图：S06 四诊断图顺序与版式一致（`(δ,观测量)` 与 D08 四面板一一对应，
  为其模拟机图层）；
  曲线坐标系与 S06 数据一致（脚本自检断言）；D06a–c 人工保真核对
  （轨道数/配对/子层顺序/`p` 堆叠与 ansatz.md 一致，无虚构门）。
- 单元测试：单键酉与 kron 参考一致；零参数即初态；三初态对称性；
  参数移位梯度与有限差分一致（随机点，`< 1e-6`）；`δ=0` 参数计数；
  warm 链单调不增（smoke 点，容限内）；输入门控拒绝路径（非法 `p`/`L`）。

诊断量（只记录、不设通过阈值）：

- `p` 单调性违反计数（spec 诊断要求）；`E*−E0` 精确 gap 分布（解质量度量，
  若系统性偏大则回 plan 加采样数，不动 spec）；`a*` 分布（三路获胜直方图/线）；
  L-BFGS 迭代数分布；invalid 点清单（若有）。

出图风格检查（按 skill 报告块，出图后附）。

## 5. 未解决问题 / 延后工作

- 无阻塞实现的未解决问题（Yao 与否已定：不用 Yao，用定长直演）。

## 6. 修订记录

- 2026-10-04：一致对 `(θ*,E*)` + 终点梯度复核 + 两遍精修。原因有三：
  (1) 发现 `Optim.minimum` 可来自被拒线搜索试验点、与 `f(minimizer)` 差约
  `1e-6`，存档对必须自洽，故 `E*` 一律在报告点重算；(2) 单遍 L-BFGS 在平谷
  因 stale 曲率估计停滞，加一遍 fresh-memory 重精修，
  实测可转正；(3) 终点加梯度复核（门字面含义：报告点平稳即收敛）。
  棘轮门保留作后备。spec §5（棘轮门）与本修订兼容，无需再改 spec。
