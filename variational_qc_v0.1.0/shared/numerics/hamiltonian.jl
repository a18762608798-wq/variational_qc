# OBC AHC 哈密顿量构造（doc/model/H.md，OBC 取值见 specs）。
#
# 约定（全仓库统一）：
# - 格点 1-indexed：Julia 格点 j 对应文档格点 j-1，L=8 即 1..8。
# - kron 左起第 j 个因子即格点 j；计算基比特 b1(MSB)..bL，Z=diag(1,-1)，|0> 为 +1 本征态。

module Hamiltonian

using LinearAlgebra

export bond_list_OBC, build_H, embed1, build_P, build_Hp

const SX = ComplexF64[0 1; 1 0]
const SY = ComplexF64[0 -im; im 0]
const SZ = ComplexF64[1 0; 0 -1]
const ID2 = ComplexF64[1 0; 0 1]

"""OBC 键表（1-indexed）。intra=(1,2),(3,4),(5,6),(7,8)；inter=(2,3),(4,5),(6,7)，无 (8,1) 缠绕键。"""
function bond_list_OBC(L::Int)
    @assert iseven(L) && L % 4 == 0
    intra = [(2i + 1, 2i + 2) for i in 0:(L ÷ 2 - 1)]
    inter = [(2i + 2, 2i + 3) for i in 0:(L ÷ 2 - 2)]
    return intra, inter
end

"""单格点算符嵌入全链（其余格点恒等）。"""
function embed1(A::Matrix{ComplexF64}, k::Int, L::Int)
    @assert 1 <= k <= L
    ops = [ID2 for _ in 1:L]
    ops[k] = A
    M = ops[1]
    for j in 2:L
        M = kron(M, ops[j])
    end
    return M
end

"""格点 k,l 上的双体算符嵌入全链（其余格点恒等）。"""
function embed2(Ak::Matrix{ComplexF64}, Al::Matrix{ComplexF64}, k::Int, l::Int, L::Int)
    @assert 1 <= k < l <= L
    ops = [ID2 for _ in 1:L]
    ops[k] = Ak
    ops[l] = Al
    M = ops[1]
    for j in 2:L
        M = kron(M, ops[j])
    end
    return M
end

"""h_{k,l}(δ) = e^{-δ}(X_k X_l + Y_k Y_l) + e^{+δ} Z_k Z_l。"""
function bond_term(k::Int, l::Int, delta::Float64, L::Int)
    jxx = exp(-delta)
    jz = exp(delta)
    return jxx * (embed2(SX, SX, k, l, L) + embed2(SY, SY, k, l, L)) +
           jz * embed2(SZ, SZ, k, l, L)
end

"""H(s,δ)：intra 键权重 (1-s)，inter 键权重 s，OBC。返回 Hermitian 矩阵。"""
function build_H(s::Float64, delta::Float64; L::Int = 8)
    intra, inter = bond_list_OBC(L)
    H = zeros(ComplexF64, 2^L, 2^L)
    for (k, l) in intra
        H .+= (1 - s) * bond_term(k, l, delta, L)
    end
    for (k, l) in inter
        H .+= s * bond_term(k, l, delta, L)
    end
    return Hermitian(H)
end

"""对称性项系数 λ（硬编码为 1，不做扫描轴，见 task2 change）。"""
const LAMBDA_P = 1.0

"""P = Z_tot^2 - ∏X（doc/model/ref/symmetry.md）。返回 Hermitian 矩阵。"""
function build_P(; L::Int = 8)
    Ztot = sum(embed1(SZ, j, L) for j in 1:L)
    prodX = reduce(kron, (SX for _ in 1:L))
    return Hermitian(Ztot^2 - prodX)
end

"""H'(s,δ) = H(s,δ) + λP，λ=1。返回 Hermitian 矩阵。"""
function build_Hp(s::Float64, delta::Float64; L::Int = 8)
    return Hermitian(Matrix(build_H(s, delta)) + LAMBDA_P * Matrix(build_P(; L = L)))
end

end # module
