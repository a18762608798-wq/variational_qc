# string operator 与 AFM 结构因子（doc/model/operator.md，OBC，L=8）。
# 输入为基态 ψ（与 hamiltonian.jl 同一排序约定：格点 j ↔ 第 j 个 kron 因子，
# j=1 为 MSB；Z=diag(1,-1)，比特 0 → +1）。`1/4` 归一从略，与 ZR 约定一致。
#
# 文档格点 0-indexed → Julia 格点 = 文档 +1：
#   O_str(d) = (Z1+Z2)[Π_{l=1}^{d-1}(-Z_{2l+1}Z_{2l+2})](Z_{2d+1}+Z_{2d+2})，d=L/2-1；
#   S(π) = (1/L)Σ_{i,j}(-1)^{i-j}<Z_i Z_j>，i,j 为 1-indexed 格点（(-1)^{i-j} 与 0-indexed 一致）。

module StringAFM

using LinearAlgebra

export string_operator, afm_structure_factor

"""格点 j（1-indexed）在基指标 a 中的 Z 本征值（+1/-1）。"""
@inline function zb(a::Int, j::Int, L::Int)
    return ((a >> (L - j)) & 1) == 0 ? 1.0 : -1.0
end

"""O_str：全 Z 乘积，期望即按 |ψ|² 加权。"""
function string_operator(psi::Vector{ComplexF64}; L::Int = 8)
    @assert iseven(L) && L % 4 == 0
    d = L ÷ 2 - 1
    n = 2^L
    @assert length(psi) == n
    acc = 0.0
    for a in 0:(n - 1)
        p = abs2(psi[a + 1])
        p == 0.0 && continue
        lam = zb(a, 1, L) + zb(a, 2, L)
        for l in 1:(d - 1)
            lam *= -(zb(a, 2l + 1, L) * zb(a, 2l + 2, L))
        end
        lam *= zb(a, 2d + 1, L) + zb(a, 2d + 2, L)
        acc += p * lam
    end
    return acc
end

"""S(π)：先算概率分布，再组装 Z_i Z_j 关联。"""
function afm_structure_factor(psi::Vector{ComplexF64}; L::Int = 8)
    n = 2^L
    @assert length(psi) == n
    probs = abs2.(psi)
    s = 0.0
    for i in 1:L, j in 1:L
        cij = 0.0
        for a in 0:(n - 1)
            c = probs[a + 1]
            c == 0.0 && continue
            cij += c * zb(a, i, L) * zb(a, j, L)
        end
        s += (-1)^(i - j) * cij
    end
    return s / L
end

end # module
