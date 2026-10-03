# Tasks

## 0. 作废数据清理（4 参数单转角版产物）

- [x] 0.1 删除无效数据并验证清空：`depth1/data/interim/` 全套、`depth2/data/interim/sweep_ckpt.json`、`depth1/data/figures/`、`config/pilot.csv`、`config/pilot_warm.csv`、两份 sweep log；验证上述路径为空且 `config/grid.toml` 与 `scripts/` 原地保留，误删任一脚本或配置即视为失败

## 1. 骨架与 orbit 拟设

- [x] 1.1 建 `task10_reflect_orbit/{config,scripts,depth1,depth2,depth3}` 目录与 `config/grid.toml`（depths=[1,2,3]、δ=±1、s 51 点、路径模板、优化初值），验证目录结构与 toml 可解析且路径模板指向本任务专属目录
- [x] 1.2 重写 `scripts/ansatz_orbit.py` 为双角 orbit 子层（同 orbit 键 `RXX(θ_1)RYY(θ_1)` + `RZZ(θ_2)`，每层 8 参数，`build_vqe_circuit(init,x,n_layers)` 首层配对+层间交替、复用初态语义与裸 H），验证随机参数下 P 期望为 −1（浮点舍入内）、镜面对映键共用同一 `(θ_1,θ_2)` 且单层恰 8 参数、同参两次 statevector 逐位一致
- [x] 1.3 重写优化与扫描脚本（depth1 8 维全局+polish、depth2/3 warm-start 垫底+微扰+polish 钳位、新层垫 8 参数、`seed_base=20260929`、增量 ckpt、任一格点失败非零退出且不写 CSV），验证 `--help` 可用、单点 smoke 运行通过、递推来源硬检查拒绝跨任务（uniform）thetas 且断言 `len(x)==8k`

## 2. Pilot 门控与逐深度扫描

- [x] 2.1 重跑 depth1 pilot（8 维；3~5 个 s 点 × 三初态，覆盖深相端/过渡区/简并区；两档预算起点 light `{de_maxiter=30, popsize=15, cobyla=300}` vs base `{50, 20, 500}`）并落盘新 `config/pilot.md`（全局预算、多 seed 极差、polish 增益、深层微扰/restart 取值、GHZ 首层 2 个 `θ_2` 平坦方向说明），验证 pilot.md 存在且全量配置与之对应一致，否则不得进入 2.2
- [x] 2.2 全量扫描 depth1（102 行目标值 CSV 表头 `s,delta,E_triv,E_topo,E_afm`、行序 delta 外层 s 内层、thetas 存档），验证行数 102、s 端点覆盖 0 与 1、同 seed 两次逐位一致（含跨进程）、每行满足变分上界 `E_init ≥ E0−1e-6`（对照 task1 解析谱）
- [x] 2.3 全量扫描 depth2（由本任务 depth1 thetas 递推），验证 thetas 向量维度为 16、零微扰起点与 depth1 最优目标值一致（容差 1e-12）、深度单调性如实记录（退化记为失败线索复核）
- [x] 2.4 全量扫描 depth3（由本任务 depth2 thetas 递推），验证同 2.3（维度为 24）且三深度 CSV 齐全

## 3. Q/ZR 纯后处理派生

- [x] 3.1 实现并运行逐深度 `derive_orbit_qzr.py`（逐点 argmin 获胜 thetas 重建 orbit 电路、复用 task3 `Q_of_state`/`tilde_ZR_of_state`，输出 `vqe_Q_L8_OBC.csv` 表头 `s,delta,Q_vqe` 与 `vqe_ZR_L8_OBC.csv` 表头 `s,delta,ZR_vqe`），验证每文件 102 行同行序、同一 thetas 跑两次逐位一致、输入缺失时非零退出且不写文件

## 4. 画布与验收

- [x] 4.1 渲染逐深度×逐 δ 三画布（min-energy 三线、Q 双线、ZR 双线；3 深度 × 2 δ × 3 类，PNG 必选 + PDF 同名，标题与文件名含 orbit 与深度标识），验证文件清单无混淆（不覆盖 task3/4）、同一输入两次逐像素一致、缺列时非零退出且无残缺图
- [x] 4.2 验收对照（脚本化检查 + 目视）：min(VQE-orbit) 逐点不高于任一初态线且不低于 E0−1e-6，Q∈[-1,1]、ZR∈[-1.2,1.2] 同语言可比，与 task3/4 同深度 uniform 画布并排可判读 orbit 增益/偏移，验证检查脚本全过且结论记入任务 README 或 figures 说明
