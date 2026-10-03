# 归一化 ZR（doc/model/operator.md OBC 特殊值，L=8）：
#   I  = 文档 {2,3,4,5} → Julia (3,4,5,6)，I1=(3,4)，I2=(5,6)；
#   R_I 为计算基逆序置换（3-4 键镜像），Z_R=Tr(ρ_I R_I)，
#   tilde = Z_R / sqrt((Tr(ρ_I1^2)+Tr(ρ_I2^2))/2)。
# 排序约定与 hamiltonian.jl 一致：ptrace 结果因子序 = sel 序，首个 sel 为 MSB。

module ZR

using LinearAlgebra
using QuantumToolbox

export tilde_ZR_value, reflection_matrix_I, fullchain_swap

const L0 = 8
const I_ALL = (3, 4, 5, 6)
const I1 = (3, 4)
const I2 = (5, 6)

"""4 比特逆序置换矩阵（基序 b3 b4 b5 b6，b3=MSB）：|b3 b4 b5 b6> -> |b6 b5 b4 b3>。"""
function reflection_matrix_I()
    R = zeros(ComplexF64, 16, 16)
    for b in 0:15
        b3 = (b >> 3) & 1
        b4 = (b >> 2) & 1
        b5 = (b >> 1) & 1
        b6 = b & 1
        br = (b6 << 3) | (b5 << 2) | (b4 << 1) | b3
        R[br + 1, b + 1] = 1.0
    end
    return R
end

"""全链交换算符：交换格点对 [(3,6),(4,5)]（即文档 2<->5, 3<->4），其余恒等。
用于独立交叉验证：<ψ|S|ψ> 应等于经由约化矩阵算出的 Z_R。"""
function fullchain_swap(; L::Int = L0)
    n = 2^L
    S = zeros(ComplexF64, n, n)
    for a in 0:(n - 1)
        bits = [(a >> (L - j)) & 1 for j in 1:L]  # bits[j] = 格点 j 比特，j=1 为 MSB
        bits[3], bits[6] = bits[6], bits[3]
        bits[4], bits[5] = bits[5], bits[4]
        b = 0
        for j in 1:L
            b = (b << 1) | bits[j]
        end
        S[b + 1, a + 1] = 1.0
    end
    return S
end

"""由基态 ψ 计算 tilde Z_R。分母 <= 0 时抛错（不输出 NaN 蒙混）。"""
function tilde_ZR_value(psi::Vector{ComplexF64}; L::Int = L0)
    d = ntuple(_ -> 2, L)
    ket = QuantumObject(psi; type = Ket(), dims = (d, (1,)))
    rhoI = Matrix(ptrace(ket, I_ALL).data)
    rhoI1 = Matrix(ptrace(ket, I1).data)
    rhoI2 = Matrix(ptrace(ket, I2).data)
    R = reflection_matrix_I()
    zr = real(tr(rhoI * R))
    p1 = real(tr(rhoI1 * rhoI1))
    p2 = real(tr(rhoI2 * rhoI2))
    denom = sqrt((p1 + p2) / 2)
    denom <= 0 && error("tilde_ZR: non-positive purity denominator (p1=$p1, p2=$p2)")
    return (; tilde = zr / denom, ZR = zr, purity_I1 = p1, purity_I2 = p2)
end

end # module
