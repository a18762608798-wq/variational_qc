# Production assertions for exp03 (T008): full-output checks on data/exp03/.
# Re-derives crossings/fit from the archived arrays and locks every spec Contract F condition (VAL-001..VAL-005).
# Failure => invalid run. Prints VERIFY-EXP03-OK plus diagnostics on success.

push!(LOAD_PATH, joinpath(@__DIR__, "..", "src"))
using LinearAlgebra
BLAS.set_num_threads(1)
using Shared01  # load order for Exp03
using Shared01: H_DEF_ID
using Exp03
using Exp03: sector_basis, sector_hamiltonian
using Exp03: key_wide, key_narrow
using Exp03: crossings, linear_fit
using Exp03: SCHEMA, LS, GAP_MIN_TOL, FIT_TOL
using NPZ, JSON3

const DATA_DIR = joinpath(@__DIR__, "..", "data", "exp03")

function main()
    d = NPZ.npzread(joinpath(DATA_DIR, "exp03_D02.npz"))
    manifest = open(JSON3.read, joinpath(DATA_DIR, "exp03_manifest.json"))
    @assert manifest["schema"] == SCHEMA == "exp03/v1"
    @assert manifest["H_def"] == H_DEF_ID
    @assert vec(d["Ls"]) == collect(LS)

    s_wide, s_narrow = vec(d["s_wide"]), vec(d["s_narrow"])
    @assert s_wide == [key_wide(i) / 10000.0 for i in 1:99]
    @assert s_narrow == [key_narrow(k) / 10000.0 for k in 1:99]
    D_wide = d["D_wide"]
    A_narr = d["A_narrow"]
    @assert size(D_wide) == (5, 99) && size(A_narr) == (5, 99)
    @assert all(isfinite, D_wide) && all(isfinite, A_narr)
    @assert minimum(D_wide) ≥ GAP_MIN_TOL

    # Sector dims re-derived (constructive check, L=16 enumeration is trivial).
    for (r, L) in enumerate(LS)
        @assert manifest["sector_dims"][string(L)] == length(sector_basis(L).members)
    end

    # Crossings re-derived from archived A grids; must match the archived table.
    @assert vec(d["cross_pairs"]) == [102, 103, 104, 105, 203, 204, 205, 304, 305, 405]
    pairs = [(1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5), (3, 4), (3, 5), (4, 5)]
    for (p, (r1, r2)) in enumerate(pairs)
        cs = crossings(s_narrow, A_narr[r1, :], A_narr[r2, :])
        @assert !isempty(cs)
        @assert abs(cs[1][1] - d["cross_s"][p]) == 0.0
        @assert abs(cs[1][2] - d["cross_A"][p]) == 0.0
    end

    # (iii): five points over L=8/12/16/20/24; fit uses L=20,24 only (spec PRE-004).
    # All five points reuse the (i) s = 0.5 (i = 50) values (extra_iii retired, Q8).
    fit_Ls = [8, 12, 16, 20, 24]
    @assert vec(d["fit_Ls"]) == fit_Ls
    xs = [1.0 / L for L in fit_Ls]
    ys = [D_wide[r, 50] for r in 1:5]
    @assert vec(d["fit_x"]) == xs && vec(d["fit_y"]) == ys
    fit = linear_fit(xs[4:5], ys[4:5])
    @assert abs(fit.a - d["fit_a"][]) < FIT_TOL
    @assert abs(fit.b - d["fit_b"][]) < FIT_TOL

    # Diagnostics (recorded only, no pass thresholds per spec VAL-004).
    println("fit: a = $(d["fit_a"][]), b = $(d["fit_b"][])")
    for (r, L) in enumerate(LS)
        m, i = findmin(D_wide[r, :])
        println("L=$L: min Δ = $m at s = $(s_wide[i])")
    end
    println("crossings s: ", vec(d["cross_s"]))
    println("VERIFY-EXP03-OK")
end

main()
