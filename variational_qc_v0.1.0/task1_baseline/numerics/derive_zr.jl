# ZR 派生：只读基态存档，重算 tilde Z_R 写 CSV（与旧 scan.jl 直算链同格式）。
# 用法（仓库根目录）：julia --project=. task1_baseline/numerics/derive_zr.jl [archive_npz out_csv]

include(joinpath(@__DIR__, "..", "..", "shared", "numerics", "zr.jl"))

using .ZR
using NPZ
using Printf

function main()
    archive = length(ARGS) >= 1 ? ARGS[1] : "task1_baseline/data/interim/psi_archive.npz"
    out = length(ARGS) >= 2 ? ARGS[2] : "task1_baseline/data/interim/tilde_ZR_L8_OBC.csv"
    d = npzread(archive)
    psi, ss, ds = d["psi"], vec(d["s_grid"]), vec(d["delta_grid"])
    isdeg = vec(d["is_degenerate"])
    ns, ndelta = length(ss), length(ds)
    @assert size(psi, 1) == ns * ndelta
    mkpath(dirname(out))
    k = 0
    open(out, "w") do io
        println(io, "s,delta,tilde_ZR,is_degenerate,Z_R,purity_I1,purity_I2")
        for (j, delta) in enumerate(ds), (i, s) in enumerate(ss)
            k += 1
            z = tilde_ZR_value(Vector{ComplexF64}(psi[k, :]))
            @printf(
                io,
                "%.8f,%.8f,%.10f,%d,%.10f,%.10f,%.10f\n",
                s,
                delta,
                z.tilde,
                isdeg[k],
                z.ZR,
                z.purity_I1,
                z.purity_I2
            )
        end
    end
    println("wrote $out ($k rows from $archive)")
end

main()
