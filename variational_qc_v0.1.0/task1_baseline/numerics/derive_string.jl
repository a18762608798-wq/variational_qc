# string operator 派生：只读基态存档，写 O_str CSV（与 ZR 派生同契约）。
# 用法（仓库根目录）：julia --project=. task1_baseline/numerics/derive_string.jl [archive_npz out_csv]

include(joinpath(@__DIR__, "..", "..", "shared", "numerics", "string_afm.jl"))

using .StringAFM
using NPZ
using Printf

function main()
    archive = length(ARGS) >= 1 ? ARGS[1] : "task1_baseline/data/interim/psi_archive.npz"
    out = length(ARGS) >= 2 ? ARGS[2] : "task1_baseline/data/interim/Ostr_L8_OBC.csv"
    d = npzread(archive)
    psi, ss, ds = d["psi"], vec(d["s_grid"]), vec(d["delta_grid"])
    isdeg = vec(d["is_degenerate"])
    ns, ndelta = length(ss), length(ds)
    @assert size(psi, 1) == ns * ndelta
    mkpath(dirname(out))
    k = 0
    open(out, "w") do io
        println(io, "s,delta,O_str,O_str_norm,is_degenerate")
        for (j, delta) in enumerate(ds), (i, s) in enumerate(ss)
            k += 1
            o = string_operator(Vector{ComplexF64}(psi[k, :]))
            @printf(io, "%.8f,%.8f,%.10f,%.10f,%d\n", s, delta, o, -o, isdeg[k])
        end
    end
    println("wrote $out ($k rows from $archive)")
end

main()
