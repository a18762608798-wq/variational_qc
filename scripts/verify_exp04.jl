# Production assertions for exp04 (T008): full-output checks on data/exp04/.
# Locks every spec Contract F condition (VAL-001..VAL-008); failure => invalid run.
# Prints VERIFY-EXP04-OK plus diagnostics on success.

push!(LOAD_PATH, joinpath(@__DIR__, "..", "src"))
using LinearAlgebra
using Statistics
BLAS.set_num_threads(1)
using Shared01  # load order for Exp04
using Shared01.Hamiltonian: H_DEF_ID
using Exp01
using Exp02
using Exp04
using Exp04.Store: SCHEMA, DELTAS, S_GRID, THETA_MAX
using NPZ, JSON3

const DATA_DIR = joinpath(@__DIR__, "..", "data", "exp04")

const FIELDS = ("theta_star", "E_star", "a_star", "spi", "ostr", "e0",
                "leg_E", "theta_leg", "conv", "stagn", "dtail", "einit", "sym")

function check_line(d10, tag::String, delta::Real, stag_tol::Real)
    c = Dict(k => d10["$(tag)_$(k)"] for k in FIELDS)
    ns = 99
    @assert size(c["theta_star"]) == (ns, 3, THETA_MAX)
    @assert size(c["theta_leg"]) == (ns, 3, 3, THETA_MAX)
    @assert size(c["E_star"]) == (ns, 3)
    npl = delta == 0.0 ? [4, 8, 12] : [8, 16, 24]
    for i in 1:ns, p in 1:3
        row = vec(c["theta_star"][i, p, :])
        @assert count(isfinite, row) == npl[p]  # NaN pad beyond Nθ
        @assert all(isfinite, [c["E_star"][i, p], c["spi"][i, p], c["ostr"][i, p]])
        for li in 1:3
            @assert c["conv"][i, li, p] || c["stagn"][i, li, p]
            if c["stagn"][i, li, p]  # ratchet gate re-derived from the archive
                @assert p > 1
                @assert c["dtail"][i, li, p] < stag_tol
                @assert c["leg_E"][i, li, p] ≤ c["leg_E"][i, li, p - 1] + 1e-8
            end
        end
        a = Int(c["a_star"][i, p])
        @assert 1 ≤ a ≤ 3
        @assert isequal(vec(c["theta_leg"][i, a, p, :]), vec(c["theta_star"][i, p, :]))
        @assert c["leg_E"][i, a, p] == minimum(vec(c["leg_E"][i, :, p]))  # winner = min leg
        @assert c["E_star"][i, p] ≤ c["einit"][i, a] + 1e-8  # VQE never worsens init
        @assert c["E_star"][i, p] ≥ c["e0"][i] - 1e-8        # variational principle
        @assert maximum(vec(c["sym"][i, p, :])) < 1e-8       # symmetry preserved
    end
end

function main()
    d10 = NPZ.npzread(joinpath(DATA_DIR, "exp04_S06.npz"))
    s03 = NPZ.npzread(joinpath(DATA_DIR, "exp04_S03.npz"))
    manifest = open(JSON3.read, joinpath(DATA_DIR, "exp04_manifest.json"))
    stag_tol = manifest["stag_tol"]  # single source: same threshold as production gate
    @assert manifest["schema"] == SCHEMA == "exp04/v1"
    @assert manifest["H_def"] == H_DEF_ID
    @assert vec(d10["deltas"]) == collect(DELTAS)
    check_line(d10, "d0", 0.0, stag_tol)
    check_line(d10, "d085", 0.85, stag_tol)

    # S03: 594 groups reference the same S06 values.
    th, meta = s03["theta"], s03["meta"]
    @assert size(th) == (594, THETA_MAX) && size(meta) == (594, 4)
    r = 0
    for (di, tag) in enumerate(["d0", "d085"])
        c = Dict(k => d10["$(tag)_$(k)"] for k in FIELDS)
        for i in 1:99, p in 1:3
            r += 1
            @assert vec(meta[r, :]) == [di, i, p, Int(c["a_star"][i, p])]
            @assert isequal(vec(th[r, :]), vec(c["theta_star"][i, p, :]))
        end
    end

    # Diagnostics (recorded only, no pass thresholds per spec VAL-007).
    for (tag, delta) in [("d0", 0.0), ("d085", 0.85)]
        c = Dict(k => d10["$(tag)_$(k)"] for k in FIELDS)
        mono = sum(c["E_star"][i, p + 1] > c["E_star"][i, p] + 1e-8
                   for i in 1:99 for p in 1:2)
        gap = vec(c["E_star"]) - vec(repeat(vec(c["e0"]), 1, 3))
        println("δ=$delta: p-monotonicity violations=$mono, " *
                "max(E*-E0)=$(maximum(gap)), median=$(median(vec(gap)))")
        println("δ=$delta: a* counts=$( [[sum(vec(c["a_star"][:, q]) .== a) for a in 1:3] for q in 1:3] ) per p")
        println("δ=$delta: stagnant legs=$(sum(vec(c["stagn"])))")
    end
    println("VERIFY-EXP04-OK")
end

main()
