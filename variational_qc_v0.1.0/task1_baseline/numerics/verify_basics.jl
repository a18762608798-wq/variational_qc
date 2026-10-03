# 任务 2.1–2.3 验收：键表/厄米/线性、基态归一与最低能量、ZR 公式链。
# 用法（仓库根）：julia --project=. task1_baseline/numerics/verify_basics.jl，全部通过则无报错退出。

include(joinpath(@__DIR__, "..", "..", "shared", "numerics", "hamiltonian.jl"))
include(joinpath(@__DIR__, "..", "..", "shared", "numerics", "ground_state.jl"))
include(joinpath(@__DIR__, "..", "..", "shared", "numerics", "zr.jl"))

using .Hamiltonian
using .GroundState
using .ZR
using LinearAlgebra
using Printf

# ---- 2.1 OBC 哈密顿量 ----
intra, inter = bond_list_OBC(8)
@assert intra == [(1, 2), (3, 4), (5, 6), (7, 8)]
@assert inter == [(2, 3), (4, 5), (6, 7)]  # 无 (8,1) 缠绕键
H0 = Matrix(build_H(0.0, 0.5))
H1 = Matrix(build_H(1.0, 0.5))
Hs = Matrix(build_H(0.3, 0.5))
@assert norm(Hs - Hs') == 0.0  # 厄米
@assert norm(Hs - ((1 - 0.3) * H0 + 0.3 * H1)) < 1.0e-10  # 仅两类键，按 s 线性
@assert norm(H0 - H0') == 0.0 && norm(H1 - H1') == 0.0
println("2.1 OK: bonds + Hermitian + linear-in-s")

# ---- 2.2 基态 ----
gs = solve_ground_state(Hermitian(Hs))
@assert abs(norm(gs.psi) - 1.0) < 1.0e-8
emin = minimum(eigvals(Hermitian(Hs)))
@assert abs(gs.energy - emin) < 1.0e-8
@printf("2.2 OK: norm=1, E=%.8f == emin, gap=%.3e, degen=%s\n", gs.energy, gs.gap, gs.is_degenerate)

# ---- 2.3 ZR：排序约定检验 ----
# 乘积态 |0>_3|1>_4|0>_5|1>_6（其余 |0>）：ρ_I 应为 diag、唯一非零在 bits 0101（1-based 指标 6）；
# 0101 逆序为 1010，正交 → Z_R=0。
psi_prod = zeros(ComplexF64, 256)
bits = [0, 0, 0, 1, 0, 1, 0, 0]  # 格点 1..8 比特
idx = sum(bits[j] << (8 - j) for j in 1:8)
psi_prod[idx + 1] = 1.0
zp = tilde_ZR_value(psi_prod)
@assert abs(zp.ZR) < 1.0e-12
println("2.3a OK: product-state ordering, Z_R=0 as expected")

# 对称态 (|0101>+|1010>)/√2（I 上，其余 |0>）：R 本征值 +1 → Z_R=1；
# 两半纯度各 0.5 → tilde=√2（合成态校验公式，不套用 [-1.2,1.2] 物理带）。
psi_sym = zeros(ComplexF64, 256)
b_0101 = [0, 0, 0, 1, 0, 1, 0, 0]
b_1010 = [0, 0, 1, 0, 1, 0, 0, 0]
i1 = sum(b_0101[j] << (8 - j) for j in 1:8)
i2 = sum(b_1010[j] << (8 - j) for j in 1:8)
psi_sym[i1 + 1] = 1 / sqrt(2)
psi_sym[i2 + 1] = 1 / sqrt(2)
zs = tilde_ZR_value(psi_sym)
@assert abs(zs.ZR - 1.0) < 1.0e-12
@assert abs(zs.tilde - sqrt(2)) < 1.0e-12
println("2.3b OK: symmetric-state Z_R=1, tilde=√2")

# 独立交叉验证：<ψ|S|ψ>（全链交换）应等于约化矩阵路线的 Z_R。
S = fullchain_swap()
cross = real(ComplexF64(dot(gs.psi, S * gs.psi)))
@assert abs(cross - tilde_ZR_value(gs.psi).ZR) < 1.0e-8
println("2.3c OK: full-chain-swap cross-check matches reduced-DM route")

# 端点物理方向：s=0 平庸为正，s=1 拓扑为负；物理基态落在 [-1.2,1.2]。
for (s, want) in ((0.0, 1), (1.0, -1))
    g = solve_ground_state(build_H(s, 0.0))
    z = tilde_ZR_value(g.psi)
    @assert -1.2 <= z.tilde <= 1.2
    @assert sign(z.tilde) == want
    @printf("endpoint s=%.1f: tilde_ZR=%+.6f (E=%.6f, gap=%.2e)\n", s, z.tilde, g.energy, g.gap)
end
println("ALL BASICS PASSED")
