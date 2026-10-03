# 全网格求解驱动：s×δ 网格对角化，只写基态存档（Julia→Python 跨语言 NPZ）。
# 用法（仓库根目录）：julia --project=. task1_baseline/numerics/solve.jl [ns ndelta out_npz]
# 行序：delta 外层、s 内层（与 CSV 契约同序）。默认 100×100。

include(joinpath(@__DIR__, "..", "..", "shared", "numerics", "hamiltonian.jl"))
include(joinpath(@__DIR__, "..", "..", "shared", "numerics", "ground_state.jl"))

using .Hamiltonian
using .GroundState
using NPZ
using LinearAlgebra

function main()
    ns = length(ARGS) >= 1 ? parse(Int, ARGS[1]) : 100
    ndelta = length(ARGS) >= 2 ? parse(Int, ARGS[2]) : 100
    out = length(ARGS) >= 3 ? ARGS[3] : "task1_baseline/data/interim/psi_archive.npz"
    ss = collect(range(0.0, 1.0; length = ns))
    ds = collect(range(-3.0, 3.0; length = ndelta))
    n = ns * ndelta
    psi = Matrix{ComplexF64}(undef, n, 256)
    energies = Vector{Float64}(undef, n)
    isdeg = Vector{Int}(undef, n)
    k = 0
    for delta in ds, s in ss
        k += 1
        gs = solve_ground_state(build_H(Float64(s), Float64(delta)))
        psi[k, :] = gs.psi
        energies[k] = gs.energy
        isdeg[k] = gs.is_degenerate ? 1 : 0
    end
    mkpath(dirname(out))
    npzwrite(out, Dict(
        "psi" => psi,
        "s_grid" => ss,
        "delta_grid" => ds,
        "energies" => energies,
        "is_degenerate" => isdeg,
    ))
    println("wrote $out ($n states: ns=$ns, ndelta=$ndelta)")
end

main()
