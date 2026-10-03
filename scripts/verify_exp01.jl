# T007 production assertions against the exp01 D01 output (row chunks + assembly).
# Fails (nonzero exit) on any violation.

push!(LOAD_PATH, joinpath(@__DIR__, "..", "src"))
using LinearAlgebra
using Shared01
using Shared01.GroundStates: S_GRID, DELTA_GRID
using Shared01.Store: load_shared01
using Exp01
using Exp01.Store: CHUNKS_DIRNAME, ROW_PREFIX, PROGRESS_NAME
using NPZ, JSON3

const DATA = joinpath(@__DIR__, "..", "data", "exp01")
failures = String[]

function check(cond::Bool, msg::String)
    cond || push!(failures, msg)
    println((cond ? "PASS " : "FAIL ") * msg)
end

# --- assembly-level checks ---
arrays = NPZ.npzread(joinpath(DATA, "exp01_D01.npz"))
manifest = open(JSON3.read, joinpath(DATA, "exp01_manifest.json"))
zt, z_R, deg = arrays["z_tilde"], arrays["z_R"], arrays["degenerate"]
check(size(zt) == (99, 99), "z_tilde shape 99x99")
check(vec(arrays["s_grid"]) == collect(Float64, S_GRID), "s_grid matches S01")
check(vec(arrays["delta_grid"]) == collect(Float64, DELTA_GRID), "delta_grid matches S01")
check(all(isfinite, zt), "no missing/NaN in z_tilde")

s01_arrays, s01_manifest = load_shared01(joinpath(@__DIR__, "..", "data", "shared01"))
s01_deg = Set([(Int(p["grid_index"][1]), Int(p["grid_index"][2]))
               for p in s01_manifest["degenerate_points"]])
d01_deg = Set([(i, j) for j in 1:99 for i in 1:99 if deg[i, j]])
check(s01_deg == d01_deg, "degeneracy flags 1:1 with S01 ($(length(d01_deg)) points)")

# --- per-point numeric checks from row chunks ---
function row_stats(DATA, zt)
    worst_tr, worst_eig, worst_denom = 0.0, 0.0, Inf
    for j in 1:99
        c = NPZ.npzread(joinpath(DATA, CHUNKS_DIRNAME, "$(ROW_PREFIX)$(lpad(j, 3, '0')).npz"))
        tr = vec(c["rho_trace"])
        me = vec(c["rho_min_eig"])
        dn = vec(c["denom"])
        worst_tr = max(worst_tr, maximum(abs.(tr .- 1.0)))
        worst_eig = max(worst_eig, -minimum(me))
        worst_denom = min(worst_denom, minimum(dn))
        check(vec(c["z_tilde"]) == zt[:, j], "row $j chunk/assembly agreement")
    end
    return worst_tr, worst_eig, worst_denom
end
worst_tr, worst_eig, worst_denom = row_stats(DATA, zt)
check(worst_tr < 1e-10, "max |Trρ-1| = $worst_tr < 1e-10")
check(worst_eig < 1e-10, "min eig violation = $worst_eig < 1e-10")
check(worst_denom > 1e-12, "min denom = $worst_denom > 1e-12")

if isempty(failures)
    println("VERIFY-EXP01-OK")
else
    println("VERIFY-EXP01-FAILURES: ", length(failures))
    exit(1)
end
