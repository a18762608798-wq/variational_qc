# Incremental persistence for exp03 (constitution IV).
# Chunks: one .npz per (L, s-block) + progress manifest + D02 assembly.
# I/O only; physics lives in GapSolver/CrossFit.

module Store

using NPZ, JSON3, Dates
using Shared01: H_DEF_ID  # provenance only; load Shared01 first
using ..SectorBasis: sector_basis
using ..GapSolver: GapResult, union_points, key_wide, key_narrow, DELTA_FIXED,
                    ARPACK_TOL, RESID_TOL, ARPACK_NCV
using ..CrossFit: crossings, linear_fit

export save_chunk, completed_chunks, assemble_D02, chunk_id,
       save_extra, EXTRA_ID, EXTRA_LS,
       SCHEMA, LS, BLOCK, D02_NPZ_NAME, MANIFEST_NAME,
       GAP_MIN_TOL, FIT_TOL

const SCHEMA = "exp03/v1"
const LS = (8, 12, 16)
const EXTRA_LS = (20, 24)  # (iii) extra points at (δ=0, s=0.5): independent solve_gap
const EXTRA_ID = "extra-iii"
const BLOCK = 50  # s-points per chunk file
const CHUNKS_DIRNAME = "chunks"
const PROGRESS_NAME = "progress.json"
const D02_NPZ_NAME = "exp03_D02.npz"
const MANIFEST_NAME = "exp03_manifest.json"

const GAP_MIN_TOL = -1e-12  # roundoff allowance on spec Δ ≥ 0
const FIT_TOL = 1e-12       # fit recompute consistency

chunk_id(L::Integer, ib::Integer) = "L$(L)-b$(ib)"
_chunks(dir) = joinpath(dir, CHUNKS_DIRNAME)
_chunkpath(dir, L, ib) = joinpath(_chunks(dir), "gap_$(chunk_id(L, ib)).npz")
_extrapath(dir) = joinpath(_chunks(dir), "extra_iii.npz")

function _read_progress(dir)
    path = joinpath(dir, PROGRESS_NAME)
    isfile(path) || return Set{String}()
    return Set{String}(open(JSON3.read, path)["completed_chunks"])
end

completed_chunks(dir::AbstractString) = _read_progress(dir)

const _PROGRESS_LOCK = ReentrantLock()

"""Persist one (L, s-block) chunk (atomically) and record it in the progress file."""
function save_chunk(dir::AbstractString, L::Integer, ib::Integer,
                    keys::Vector{Int}, s::Vector{Float64}, res::Vector{GapResult})
    mkpath(_chunks(dir))
    path = _chunkpath(dir, L, ib)
    tmp = path * ".tmp"
    NPZ.npzwrite(tmp, Dict(
        "L" => L,
        "keys" => keys,
        "s" => s,
        "E0" => [r.E0 for r in res],
        "E1" => [r.E1 for r in res],
        "Delta" => [r.delta_gap for r in res],
    ))
    mv(tmp, path; force=true)
    lock(_PROGRESS_LOCK) do
        done = _read_progress(dir)
        push!(done, chunk_id(L, ib))
        open(joinpath(dir, PROGRESS_NAME), "w") do io
            JSON3.write(io, Dict("schema" => SCHEMA, "completed_chunks" => sort(collect(done))))
        end
    end
    return path
end

"""Persist the (iii) extra points (atomically) and record them in the progress file."""
function save_extra(dir::AbstractString, Ls::Vector{Int}, res::Vector{GapResult})
    mkpath(_chunks(dir))
    path = _extrapath(dir)
    tmp = path * ".tmp"
    NPZ.npzwrite(tmp, Dict(
        "Ls" => Ls,
        "s" => 0.5,
        "delta" => DELTA_FIXED,
        "E0" => [r.E0 for r in res],
        "E1" => [r.E1 for r in res],
        "Delta" => [r.delta_gap for r in res],
    ))
    mv(tmp, path; force=true)
    lock(_PROGRESS_LOCK) do
        done = _read_progress(dir)
        push!(done, EXTRA_ID)
        open(joinpath(dir, PROGRESS_NAME), "w") do io
            JSON3.write(io, Dict("schema" => SCHEMA, "completed_chunks" => sort(collect(done))))
        end
    end
    return path
end

"""Read all chunks of one L into key => (E0, E1, Δ)."""
function _read_L(dir::AbstractString, L::Integer, npts::Integer)
    nblocks = cld(npts, BLOCK)
    got = Dict{Int,Tuple{Float64,Float64,Float64}}()
    for ib in 1:nblocks
        c = NPZ.npzread(_chunkpath(dir, L, ib))
        Int(c["L"][]) == L || throw(ErrorException("chunk L mismatch: $(_chunkpath(dir, L, ib))"))
        keys = vec(c["keys"])
        E0, E1, D = vec(c["E0"]), vec(c["E1"]), vec(c["Delta"])
        for t in eachindex(keys)
            got[Int(keys[t])] = (Float64(E0[t]), Float64(E1[t]), Float64(D[t]))
        end
    end
    return got
end

"""Assemble all chunks into the single D02 product + manifest (hard asserts inside)."""
function assemble_D02(dir::AbstractString)
    pts = union_points()
    npts = length(pts)
    perL = Dict{Int,Dict{Int,Tuple{Float64,Float64,Float64}}}()
    for L in LS
        got = _read_L(dir, L, npts)
        length(got) == npts || throw(ErrorException("L=$L incomplete: $(length(got))/$npts"))
        perL[L] = got
    end
    s_wide = [key_wide(i) / 10000.0 for i in 1:99]
    s_narrow = [key_narrow(k) / 10000.0 for k in 1:99]
    D_wide = zeros(length(LS), 99)   # (i) Δ_sec per L
    A_narr = zeros(length(LS), 99)   # (ii) A = Δ·L per L
    for (r, L) in enumerate(LS)
        for i in 1:99
            D_wide[r, i] = perL[L][key_wide(i)][3]
        end
        for k in 1:99
            A_narr[r, k] = perL[L][key_narrow(k)][3] * L
        end
    end
    all(isfinite, D_wide) || throw(ErrorException("non-finite Δ in D_wide"))
    all(isfinite, A_narr) || throw(ErrorException("non-finite A in D_narrow"))
    minimum(D_wide) ≥ GAP_MIN_TOL || throw(ErrorException("Δ below tolerance: $(minimum(D_wide))"))
    # (ii) crossings per pair (spec PRE-003 + Q5); each pair must bracket at least once.
    pairs = [(1, 2), (1, 3), (2, 3)]
    cross_s = zeros(length(pairs))
    cross_A = zeros(length(pairs))
    for (p, (r1, r2)) in enumerate(pairs)
        cs = crossings(s_narrow, A_narr[r1, :], A_narr[r2, :])
        isempty(cs) && throw(ErrorException("no bracketing for pair $(LS[r1])-$(LS[r2]): invalid run"))
        cross_s[p], cross_A[p] = cs[1][1], cs[1][2]
    end
    # (iii) Δ vs 1/L at s = 0.5 over five L; fit uses L=20,24 only (spec PRE-004).
    # L=8/12/16 reuse the (i) i = 50 point; L=20/24 come from the extra chunk.
    isfile(_extrapath(dir)) || throw(ErrorException("extra_iii chunk missing: invalid run"))
    e = NPZ.npzread(_extrapath(dir))
    vec(e["Ls"]) == collect(EXTRA_LS) || throw(ErrorException("extra Ls mismatch"))
    e["s"][] == 0.5 || throw(ErrorException("extra s mismatch"))
    extra_D = Float64.(vec(e["Delta"]))
    all(isfinite, extra_D) || throw(ErrorException("non-finite extra Δ"))
    minimum(extra_D) ≥ GAP_MIN_TOL || throw(ErrorException("extra Δ below tolerance"))
    fit_Ls = [collect(LS); collect(EXTRA_LS)]
    ys = [[D_wide[r, 50] for r in 1:length(LS)]; extra_D]
    xs = [1.0 / L for L in fit_Ls]
    fit = linear_fit([1.0 / L for L in EXTRA_LS], extra_D)
    (isfinite(fit.a) && isfinite(fit.b)) || throw(ErrorException("non-finite fit coefficients"))
    npz_path = joinpath(dir, D02_NPZ_NAME)
    tmp = npz_path * ".tmp"
    NPZ.npzwrite(tmp, Dict(
        "s_wide" => s_wide,
        "s_narrow" => s_narrow,
        "Ls" => collect(LS),
        "D_wide" => D_wide,
        "A_narrow" => A_narr,
        "cross_pairs" => [p[1] * 100 + p[2] for p in pairs],  # e.g. 102 = L8-L12
        "cross_s" => cross_s,
        "cross_A" => cross_A,
        "fit_Ls" => fit_Ls,
        "fit_x" => xs,
        "fit_y" => ys,
        "fit_a" => fit.a,
        "fit_b" => fit.b,
    ))
    mv(tmp, npz_path; force=true)
    githead = try
        readchomp(`git rev-parse --short HEAD`)
    catch
        "unknown"
    end
    manifest = Dict(
        "schema" => SCHEMA,
        "H_def" => H_DEF_ID,
        "sector_basis" => "Z_tot=0 orbits under {I, Xbar, R, XbarR}, all-+ symmetrized",
        "sector_dims" => Dict(string(L) => length(sector_basis(L).members) for L in (8, 12, 16, 20, 24)),
        "delta" => DELTA_FIXED,
        "grid_wide" => "s = i/100, i = 1..99 (101-partition minus boundaries)",
        "grid_narrow" => "s = 0.45+0.15k/100, k = 1..99 (shared points: canonical key/10000)",
        "union_points_per_L" => npts,
        "fit" => "least squares Δ = a·(1/L)+b over L=20,24 only",
        "solver" => "sparse ARPACK eigs(nev=2, which=:SR)",
        "arpack_tol" => ARPACK_TOL,
        "arpack_ncv" => ARPACK_NCV,
        "resid_tol" => RESID_TOL,
        "gap_min_tol" => GAP_MIN_TOL,
        "fit_tol" => FIT_TOL,
        "julia_version" => string(VERSION),
        "git_head" => githead,
        "created_utc" => string(Dates.now(Dates.UTC)),
    )
    manifest_path = joinpath(dir, MANIFEST_NAME)
    open(manifest_path, "w") do io
        JSON3.write(io, manifest)
    end
    return npz_path, manifest_path
end

end # module
