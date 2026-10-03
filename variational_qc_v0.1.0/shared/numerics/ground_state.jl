# 基态求解：QuantumToolbox.jl eigenstates（稠密精确对角化，L=8 维数 256）。
module GroundState

using LinearAlgebra
using QuantumToolbox

export solve_ground_state

"""
solve_ground_state(H) -> (; energy, psi, gap, is_degenerate, excited)

- energy：基态能量（实数，最小本征值）；
- psi：归一化基态矢量；
- gap：第一激发隙 vals[2]-vals[1]；
- is_degenerate：gap < deg_tol 时为 true（此时返回简并子空间中确定性的一支）。
- excited：第一激发态能量（实数，第二本征值，即 energy + gap）。
"""
function solve_ground_state(H::Hermitian{ComplexF64,Matrix{ComplexF64}}; deg_tol::Float64 = 1.0e-10)
    n = size(H, 1)
    L = round(Int, log2(n))
    @assert 2^L == n
    d = ntuple(_ -> 2, L)
    Hq = QuantumObject(Matrix(H); type = Operator(), dims = (d, d))
    vals, vecs = eigenstates(Hq)
    psi = Vector(vecs[1].data)
    psi ./= norm(psi)
    gap = vals[2] - vals[1]
    return (; energy = real(vals[1]), psi = psi, gap = gap, is_degenerate = (gap < deg_tol), excited = real(vals[2]))
end

end # module
