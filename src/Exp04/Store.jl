# Incremental persistence for exp04 (constitution IV).
# Chunks: one .npz per δ line + progress manifest + D10/S03 assembly.
# I/O only; physics lives in InitStates/Ansatz/VQELoop (+ read-only Exp02 kernels).

module Store

using NPZ, JSON3
using Shared01.Hamiltonian: H_DEF_ID  # provenance only; load Shared01 first
using ..VQELoop: PointResult, MASTER_SEED, N_GLOBAL, TOP_K, G_TOL, X_TOL, F_TOL,
                  MAX_ITERS, SAMPLE_RANGE, STAG_WINDOW, STAG_TOL, STAG_E_TOL

export save_line, completed_lines, assemble_D10_S03,
       SCHEMA, DELTAS, S_GRID, THETA_MAX,
       LINE_ID, D10_NPZ_NAME, S03_NPZ_NAME, MANIFEST_NAME

const SCHEMA = "exp04/v1"
const DELTAS = (0.0, 0.85)
const S_GRID = [i / 100 for i in 1:99]  # spec §3: same convention as S01
const THETA_MAX = 24                     # max Nθ (δ≠0, p=3); shorter padded with NaN
const CHUNKS_DIRNAME = "chunks"
const PROGRESS_NAME = "progress.json"
const D10_NPZ_NAME = "exp04_D10.npz"
const S03_NPZ_NAME = "exp04_S03.npz"
const MANIFEST_NAME = "exp04_manifest.json"

LINE_ID(delta::Real) = delta == 0.0 ? "d000" : "d085"
_chunks(dir) = joinpath(dir, CHUNKS_DIRNAME)
_linepath(dir, delta) = joinpath(_chunks(dir), "line_$(LINE_ID(delta)).npz")

function _read_progress(dir)
    path = joinpath(dir, PROGRESS_NAME)
    isfile(path) || return Set{String}()
    return Set{String}(open(JSON3.read, path)["completed_lines"])
end

completed_lines(dir::AbstractString) = _read_progress(dir)

const _PROGRESS_LOCK = ReentrantLock()

"""Persist one δ line (atomically) and record it in the progress file.

Payload dict arrays (ns = 99 points):
  theta_star [ns,3,THETA_MAX] NaN-padded, E_star [ns,3], a_star [ns,3] (1..3),
  spi [ns,3], ostr [ns,3], e0 [ns], leg_E [ns,3,3], conv [ns,3,3] (leg×p),
  stagn [ns,3,3] (ratchet flags), dtail [ns,3,3] (stagnation audit),
  einit [ns,3] (zero-θ energy per leg), sym [ns,3,3] (|ztot|,|xbar-1|,|r-1|).
"""
function save_line(dir::AbstractString, delta::Real, payload::Dict)
    mkpath(_chunks(dir))
    path = _linepath(dir, delta)
    tmp = path * ".tmp"
    NPZ.npzwrite(tmp, merge(Dict("delta" => Float64(delta), "s_grid" => S_GRID), payload))
    mv(tmp, path; force=true)
    lock(_PROGRESS_LOCK) do
        done = _read_progress(dir)
        push!(done, LINE_ID(delta))
        open(joinpath(dir, PROGRESS_NAME), "w") do io
            JSON3.write(io, Dict("schema" => SCHEMA, "completed_lines" => sort(collect(done))))
        end
    end
    return path
end

"""Assemble both line chunks into D10 + S03 products + manifest (hard asserts inside)."""
function assemble_D10_S03(dir::AbstractString)
    done = _read_progress(dir)
    length(done) == length(DELTAS) ||
        throw(ErrorException("only $(length(done))/$(length(DELTAS)) lines complete"))
    lines = Dict{Float64,Any}()
    for delta in DELTAS
        c = NPZ.npzread(_linepath(dir, delta))
        vec(c["s_grid"]) == S_GRID || throw(ErrorException("s_grid mismatch line $delta"))
        lines[delta] = c
    end
    for (delta, c) in lines
        @assert size(c["theta_star"]) == (99, 3, THETA_MAX)
        @assert size(c["E_star"]) == (99, 3)
        all(isfinite, vec(c["E_star"])) || throw(ErrorException("non-finite E_star line $delta"))
        all(isfinite, vec(c["spi"])) || throw(ErrorException("non-finite spi line $delta"))
        all(isfinite, vec(c["ostr"])) || throw(ErrorException("non-finite ostr line $delta"))
        minimum(vec(c["E_star"]) - vec(repeat(vec(c["e0"]), 1, 3))) ≥ -1e-8 ||
            throw(ErrorException("variational violation line $delta"))
    end
    d10_path = joinpath(dir, D10_NPZ_NAME)
    tmp = d10_path * ".tmp"
    flat = Dict{String,Any}("s_grid" => S_GRID, "deltas" => collect(DELTAS))
    for (delta, tag) in [(0.0, "d0"), (0.85, "d085")]
        for k in ("theta_star", "E_star", "a_star", "spi", "ostr", "e0",
                  "leg_E", "theta_leg", "conv", "stagn", "dtail", "einit", "sym")
            flat["$(tag)_$(k)"] = lines[delta][k]
        end
    end
    NPZ.npzwrite(tmp, flat)
    mv(tmp, d10_path; force=true)
    # S03: flat 594 groups (δ,s,p,θ*,a*) referencing the same D10 values.
    th = zeros(2 * 99 * 3, THETA_MAX) .* NaN
    meta_rows = zeros(Int, 2 * 99 * 3, 4)  # (δ_idx, s_idx, p, a*)
    r = 0
    for (di, delta) in enumerate(DELTAS)
        c = lines[delta]
        for i in 1:99, p in 1:3
            r += 1
            th[r, :] = vec(c["theta_star"][i, p, :])
            meta_rows[r, :] = [di, i, p, Int(c["a_star"][i, p])]
        end
    end
    s03_path = joinpath(dir, S03_NPZ_NAME)
    tmp = s03_path * ".tmp"
    NPZ.npzwrite(tmp, Dict("theta" => th, "meta" => meta_rows,
                           "deltas" => collect(DELTAS), "s_grid" => S_GRID))
    mv(tmp, s03_path; force=true)
    manifest = Dict(
        "schema" => SCHEMA,
        "H_def" => H_DEF_ID,
        "L" => 8,
        "deltas" => collect(DELTAS),
        "grid" => "s = i/100, i = 1..99 (same convention as S01)",
        "p_levels" => [1, 2, 3],
        "legs" => ["triv", "topo", "afm"],
        "strategy" => "p=1 global random + L-BFGS; p>1 same-leg chained warm + L-BFGS",
        "master_seed" => MASTER_SEED,
        "n_global" => N_GLOBAL,
        "top_k" => TOP_K,
        "sample_range" => "uniform [0, 4π)",
        "g_tol" => G_TOL,
        "x_abstol" => X_TOL,
        "f_abstol" => F_TOL,
        "stag_window" => STAG_WINDOW,
        "stag_tol" => STAG_TOL,
        "stag_e_tol" => STAG_E_TOL,
        "max_iters" => MAX_ITERS,
        "julia_version" => string(VERSION),
    )
    manifest_path = joinpath(dir, MANIFEST_NAME)
    open(manifest_path, "w") do io
        JSON3.write(io, manifest)
    end
    return d10_path, s03_path, manifest_path
end

end # module
