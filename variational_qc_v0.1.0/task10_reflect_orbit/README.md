# task10: 反射对称 orbit 参数 VQE（模拟机，depth 1–3，δ=±1）

拟设：`doc/qc/evolution_qc.md` 反射对称 orbit 分组（`O_out/O_in/E_out/E_c`），
每轨道 `(θ_1,θ_2)` 双角（`XX/YY` 共 `θ_1`、`ZZ` 独立 `θ_2`），单层 8 参数，
1/2/3 层共 8/16/24 参数。三初态与子层配对沿用 task3，`P=−1`，裸 `H` statevector 精确期望。
脚本见 `scripts/`（`ansatz_orbit.py`、`optimize_orbit.py`、`sweep_orbit.py`、
`pilot_orbit.py`、`derive_orbit_qzr.py`、`plot_orbit.py`），配置见
`config/grid.toml`，pilot 结论见 `config/pilot.md`。

## 作废事件（必读）

本任务曾按旧版 doc（每键单转角、单层 4 参数）实现并跑出 depth1 全套数据与部分
depth2 ckpt，还做过一轮"orbit 全面输给 uniform"的对比分析。`doc/qc/evolution_qc.md`
修正为单层 8 参数后，上述产物与分析**全部作废并删除**，不作任何依据。
新数据以 `seed_base=20260929` 命名空间隔离；旧结论中"缺各向异性自由度"的机制
分析描述的是错误 ansatz 自身，不具物理意义。

## 优化链（pilot 锁定，见 config/pilot.md）

- depth1：DE 全局（light `{30,15,300}`）+ COBYLA polish，每点 3 seed 取最优；
- depth2/3：浅层最优垫底 + 微扰（scale 0.3）× 3 restart + polish，劣于垫底钳位；
- 单调性：depth2 相对 depth1 零退化（26/306 钳位），depth3 相对 depth2 零退化（21/306 钳位）；
- 变分上界三深度全成立；跨进程逐位确定性已验证（hashlib seed + 单线程 BLAS）。

## 结论：orbit（8 参数）vs uniform（task3/4 同深度）

min(VQE)−E0（102 点统计）：

| depth | orbit max/mean | uniform max/mean | orbit 更好点数 |
|---|---|---|---|
| 1 | 0.786 / 0.117 | 1.039 / 0.148 | 59/102 |
| 2 | 0.772 / 0.082 | 1.037 / 0.127 | 82/102 |
| 3 | 0.201 / 0.011 | 0.514 / 0.066 | 81/102 |

代表点（orbit gap / uniform gap）：δ=−1、s=0.5 处 d3 为 0.018/0.239；
δ=+1、s=0.5 处 d3 为 0.015/0.057；两端深相区两者都精确到 ~1e-6。

- depth1 两者接近（orbit 略好）；depth2 起 orbit 在过渡区系统性反超；
  depth3 orbit 平均 gap 0.011，约为 uniform（0.066）的 1/6。
- 获胜初态版图两边一致（s 小端 triv、s 大端 topo/afm），相归属不变。
- Q/ZR 相落点：depth3 的 `Q_vqe`/`ZR_vqe` 基本贴住解析线，过渡区有小幅抖动
  （Q 个别点上穿 1.0 不超过 0.5%，记为结论）；深相区贴合精确。
- GHZ 首层 2 个 `θ_2` 为平坦方向（已验证），其 theta 发散不计失败。

## 产物一览（每深度）

- `depth{K}/data/interim/vqe_L8_OBC.csv`（102 行）+ `vqe_thetas.json`
  + `vqe_Q_L8_OBC.csv` + `vqe_ZR_L8_OBC.csv`；
- `depth{K}/data/figures/`：min/Q/ZR × δ=±1 共 6 组画布（PNG + 同名 PDF），
  文件名含 `orbit_depth{K}` 标识。
