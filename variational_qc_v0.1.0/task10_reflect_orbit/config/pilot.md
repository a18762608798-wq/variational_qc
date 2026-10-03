# pilot 结论（vqe-reflect-orbit-sweep task 2.1，8 参数双角版）

pilot 范围：`δ=+1` 上 `s ∈ {0.0, 0.5, 0.98}` × 三初态 × 3 seed × 两档预算
（light: de_maxiter=30/popsize=15/cobyla=300；base: 50/20/500），共 54 runs；
depth2 探针：每 `(s,init)` 取 light 最优 seed 为垫底，微扰尺度 `{0.1, 0.3}` × 2 restart，
共 36 runs。产物：`task10_reflect_orbit/config/pilot.csv`、`pilot_warm.csv`。
（旧 4 参数单转角版 pilot 数据已随作废声明删除，不作依据。）

## 结论

1. **预算取 light 档**：9 个点-初态中 3 个两档 6 位小数一致；其余 6 个差值 0.002~0.033，
   但 base 好 5 个、light 好 2 个（`s=0.98 triv` light 好 0.024），无系统性方向，
   差值落在 seed 极差带内（0.001~0.05），即档间差 = 采样噪声而非预算增益。
   决定性论据：**在逐点获胜初态上**（s=0 triv、s=0.5 afm、s=0.98 topo），
   light vs base 差值 ≤ 0.0025（0.0000 / 0.0025 / 0.0020），远小于待分辨的物理 gap；
   大差值（0.024~0.033）全落在非获胜初态，不影响 `min(VQE)`。全量用 light（单点 ~110s，
   base ~250s，2.3 倍成本无对应收益）。
2. **必须 3 seed 取最优**：`s=0.5 triv` 极差 0.025、`s=0.98 afm` 极差 light 0.018 / base 0.050，
   单 seed 全量不可接受；取最优后获胜初态极差 ≤ 0.012。
3. **polish 恒有效**：全局解→polish 增益最小 1e-4、最大 0.55，无一恶化（容差内）。
4. **变分上界全成立**：全部 54 runs 满足 `fun ≥ E0 − 1e-6`（对照 task1 解析谱）。
5. **depth2 探针**：36 runs 增益全 ≥ 0（钳位语义下无退化）；`scale=0.3` 与 `0.1` 最优值
   一致，无一例 0.3 系统性差于 0.1（`s=0.5 afm` 最好增益 0.122 出自 0.1，0.3 为 0.109，
   同量级）。深层取 `perturb_scale=0.3`（沿用 task4 惯例）、`n_restarts=3`
   （相对探针的 2 restart 保守加一）。
   最大增益 `s=0 afm`（1.47：depth1 afm 在 s=0 处远离基态，depth2 大幅追回）、
   `s=0.5 afm` 0.122、`s=0.98 afm` 0.046——深层确有表达空间。
6. **GHZ 首层平坦方向**：单元 smoke 已证（afm 初态首作用子层 E 的 2 个 `θ_2`
   任取不改目标值，容差内精确；首子层 `θ_1` 与后子层 `θ_2` 反例均改变能量）。
   pilot 的 afm fun 极差不受平坦方向污染（平坦方向 fun 恒等），验收时该两方向的
   theta 发散单独记录、不计失败。
7. **物理预览**（light 获胜值 vs 解析）：s=0 triv 贴 E0 到 1e-6；s=0.98 topo 距 E0 2.8e-3；
   s=0.5 afm 距 E0 0.158——与 task3 uniform 单层同点的 0.156 同量级（8 参数 orbit
   在过渡区不再系统性差于 uniform，与作废的 4 参数版结论相反；最终比较以全量为准）。
8. **确定性边界**：同 task3/4，全量脚本钉死
   `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`，seed 派生用
   `hashlib`（跨进程稳定，旧 `hash()` salt 问题已修），
   且"逐位一致"断言只在同线程环境下有意义。

## 锁定全量配置

- depth1: budget = light（de_maxiter=30, de_popsize=15, cobyla_maxiter=300）
- seeds/restarts = 3（`derive_seed[_d1](base, …)`，`base=20260929`），逐点取最优
- depth2/3: perturb_scale=0.3, cobyla_maxiter=500, n_restarts=3
- seed_base = 20260929，workers = 8
- 预计 depth1: 306 runs × ~110s / 8 ≈ 70 min；depth2/3 每层 306 warm runs × ~30s / 8 ≈ 20 min
