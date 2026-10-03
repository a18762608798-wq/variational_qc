# Design

## Context

- 现状：绿地首个增量，仅有 `doc/model/H.md`（AHC 哈密顿量）与 `doc/model/operator.md`（ZR 定义与 `L=8/OBC` 特殊值）为依据；无既有代码、无 specs。见 `proposal.md` 动机。
- 约束：用户已定 `OBC + 密网格`、`只画 tilde Z_R`、`CSV/NPZ 文件衔接`；Julia 用 QuantumToolbox.jl，Python 负责绘图，环境创建参考 `env-python` skill；`H.md` 写的是周期边界，`operator.md` 的 ZR 取值按 OBC 给出，本增量统一按 OBC 实现（差值在设计决策中显式记录）。
- 规模：`L=8` 希尔伯特维数 256，精确对角化极廉价，`100×100=10000` 点单机一次可跑完（按实测约 0.3s/点，约 50 分钟），无需 HPC/分布式。

## Goals / Non-Goals

**Goals:**

- 给出 Julia→Python 的文件契约与双语言仓库骨架，使后续增量（变分电路、quafu 制备测量、string/AFM 量）能复用目录约定与数据接口。
- 锁定 OBC 键列表、`tilde Z_R` 公式链、默认密网格三处易错点，使实现无歧义。

**Non-Goals:**

- 不接入 quafu 硬件、不做变分优化、不实现随机测量版 ZR（原文 Eq.(3) Hamming 加权）与 string/AFM 量——这些是后续 `openspec update` 的增量。
- 不做性能优化（缓存本征态、并行扫描列入实现自由，不在本设计约束）。

## Decisions

### 1. 以 CSV 为主契约，NPZ 仅可选

- 内容：表头 `s,delta,tilde_ZR[,is_degenerate[,Z_R,purity_I1,purity_I2]]`，UTF-8，确定性行序（`δ` 外层、`s` 内层），由 Julia 端一次写全。
- 为何不用 `juliacall`/Python 直调 Julia：解耦双环境（Julia 与 Python 版本/依赖独立演进）、绘图机可无 Julia、产物可审计复现；代价是多一份中间文件，但在 1681 行规模可忽略。
- 为何 CSV 必选而 NPZ 可选：CSV 人可读、可 `git diff` 抽查、可被任何语言读取；NPZ 只作为大网格加速的可选项，不替代契约。替代方案（Arrow/Parquet/HDF5）对本规模过重，否决。

### 2. OBC 定义显式化（与 H.md 周期描述的差值）

- OBC 键列表：`L=8` 链 `0-1-…-7`，内胞 `(0,1),(2,3),(4,5),(6,7)` 权重 `(1-s)`，间胞 `(1,2),(3,4),(5,6)` 权重 `s`，删除 `(7,0)` 键。
- 理由：`operator.md` 的 `I={2,3,4,5}` 与 `3-4` 反射中心是 OBC 语境；用户已确认 OBC。若后续要与 `H.md` 的 PBC 对照，另起增量加 `pbc` 开关，本增量不留模糊分支。

### 3. 只算 `tilde Z_R`，`n=2` 锁定

- `ρ_I` 对 `I` 之外 4 比特求偏迹，`R_I` 为 16 维逆序置换，`tilde` 分母为两侧纯度均值开方；零分母必须报错。
- 原始 `Z_R` 可作为调试列输出但不绘图；不实现随机么正版本（那是硬件链路的事）。

### 4. 默认密网格 `100×100`，配置可调

- `s∈[0,1]`、`δ∈[-3,3]` 等距含端点；默认 `ns=ndelta=100`。`L=8` 下 10000 点单机约 50 分钟可接受；需要更密时只改配置不改代码。
- 稀疏试算网格（如 `11×11`）作为冒烟测试保留，不作为交付产物。

### 5. 仓库骨架：只表达本次真实边界，不预设未来

本次只有两个实现单元（Julia 数值求解、Python 绘图）加一次文件交接，
骨架只设三块，不照搬示例里的 `app/domains/features/infrastructure`：

```text
src/
  numerics/               # Julia：hamiltonian.jl / ground_state.jl / zr.jl / scan.jl
  viz/                    # Python：plot_heatmap.py（只读 CSV）
  shared/                 # 跨语言契约（本次真实共享，仅两项）：
    io/csv_schema.md      #   CSV 列定义与行序
    config/grid.toml      #   网格范围、默认分辨率、容差、产物路径
data/
  interim/                # CSV/NPZ 中间数据
  figures/                # PNG(+PDF) 热力图
```

- `Project.toml` / `CondaPkg.toml` 置仓库根（Julia 项目根），以便
  `env-python` skill 的向上查找逻辑与 CondaPkg 共用同一根；不另设嵌套项目根。
- 为何只有 `shared/` 共享：CSV schema 与网格配置是 Julia 写/Python 读的
  真实跨语言契约，去掉任一语言后依然说得通，符合收入 `shared` 的判断标准。
- 为何没有 `app/` 与 `infrastructure/`：本次入口就是 `scan.jl` 与
  `plot_heatmap.py` 本身，组装层与环境文档都是 speculative；后续增量若真出现
  第二个求解器/第二个数据源，再按“第三次重复才提取”建目录，不提前占位。
- 反模式：`common/shared/utils/helpers/misc` 并存——本设计只允许一个 `shared/`。

### 6. 环境与依赖

- Python 环境创建全程遵循 `env-python` skill（优先其 `julia-condapkg` 方式，以支持后续 Julia+Python 协同）；Julia `Project.toml` 锁定 QuantumToolbox.jl。
- Python 绘图栈默认 `numpy+matplotlib`（pandas 可选），不引入重型可视化框架。

## Risks / Trade-offs

- [Risk] OBC 与 `H.md` 周期表述不一致 → Mitigation：本设计显式定义 OBC 键表并在 spec 场景中锁定；PBC 对照留待后续增量。
- [Risk] `s=1` 深拓扑端有限尺寸下 `tilde Z_R` 未严格到 `-1` → Mitigation：spec 只要求符号相反与趋势正确，不写死数值阈值；实现任务含端点打印供人眼确认。
- [Risk] 密网格全量跑通前难发现公式 bug → Mitigation：先 `11×11` 冒烟 + 端点断言，再全量 `100×100`。
- [Risk] `shared/` 膨胀成 utils 垃圾场 → Mitigation：本增量 `shared` 仅 `io/config` 两项，新增共享需经“三次重复”评审。
- [Trade-off] 文件衔接多一次落盘 vs 直调：换来环境解耦与可审计性，本规模下 I/O 可忽略。

## Migration Plan

- 绿地新增，无迁移、无回滚需求；若 CSV schema 变更，后续增量以新 `specs` delta 声明并保留旧 CSV 读取兼容或文档化破坏（**BREAKING** 标记）。

## Open Questions

- 无必须前置的问题。以下可在实现时按文档声明解决，不改变 specs/approach/tasks：Python 绘图默认色标（`coolwarm` vs `RdBu`）与 DPI；CSV 是否附带 `Z_R`/纯度调试列。
