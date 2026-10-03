# task1 谱扫描：H 在 δ=±1 上切 s 轴，记录 E0/E1（绝对能量）。
# 用法（仓库根目录）：julia --project=. task1_baseline/numerics/scan_spectra.jl [ns out_csv]
# 行序：delta 外层、s 内层（与 CSV 契约同序）。默认 ns=201。
# δ=±1 为硬编码常量（见 spectra-at-delta-pm1 change），不做扫描轴。

include(joinpath(@__DIR__, "..", "..", "shared", "numerics", "hamiltonian.jl"))
include(joinpath(@__DIR__, "..", "..", "shared", "numerics", "ground_state.jl"))

using .Hamiltonian
using .GroundState
using Printf

const DELTAS = (-1.0, 1.0)

function main()
    ns = length(ARGS) >= 1 ? parse(Int, ARGS[1]) : 201
    out = length(ARGS) >= 2 ? ARGS[2] : "task1_baseline/data/interim/spectra_L8_OBC.csv"
    ss = collect(range(0.0, 1.0; length = ns))
    mkpath(dirname(out))
    open(out, "w") do io
        println(io, "s,delta,E0,E1")
        k = 0
        for delta in DELTAS, s in ss
            k += 1
            gs = solve_ground_state(build_H(Float64(s), Float64(delta)))
            @printf(io, "%.8f,%.8f,%.10f,%.10f\n", s, delta, gs.energy, gs.excited)
        end
        println("wrote $out ($k rows)")
    end
end

main()
