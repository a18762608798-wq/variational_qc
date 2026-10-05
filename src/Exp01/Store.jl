# Incremental persistence for exp01 (constitution IV: no all-in-memory + single-file finish).
# One chunk per δ row; resume skips completed rows; assembly is pure concatenation.
# I/O only; numerics live in the ReducedDensity/ZTilde implementation files.

const SCHEMA = "exp01/v1"
const CHUNKS_DIRNAME = "chunks"
const ROW_PREFIX = "row_"
const PROGRESS_NAME = "progress.json"
const D01_NPZ_NAME = "exp01_D01.npz"
const MANIFEST_NAME = "exp01_manifest.json"

_chunks(dir) = joinpath(dir, CHUNKS_DIRNAME)
_rowpath(dir, j) = joinpath(_chunks(dir), "$(ROW_PREFIX)$(lpad(j, 3, '0')).npz")

function _read_progress(dir)
    path = joinpath(dir, PROGRESS_NAME)
    isfile(path) || return Set{Int}()
    return Set{Int}(open(JSON3.read, path)["completed_rows"])
end

# Guards the progress-manifest read-modify-write against concurrent row writers.
const _PROGRESS_LOCK = ReentrantLock()

completed_rows(dir::AbstractString) = _read_progress(dir)

"""Persist one δ row (atomically) and record it in the progress manifest."""
function save_row(dir::AbstractString, j::Int, s_grid::Vector{Float64},
                  delta::Float64, res::Vector{ZTildeResult})
    mkpath(_chunks(dir))
    path = _rowpath(dir, j)
    tmp = path * ".tmp"
    NPZ.npzwrite(tmp, Dict(
        "s_grid" => s_grid,
        "delta" => delta,
        "z_R" => [r.z_R for r in res],
        "z_tilde" => [r.z_tilde for r in res],
        "rho_trace" => [r.rho_trace for r in res],
        "rho_min_eig" => [r.rho_min_eig for r in res],
        "denom" => [r.denom for r in res],
    ))
    mv(tmp, path; force=true)
    lock(_PROGRESS_LOCK) do
        done = _read_progress(dir)
        push!(done, j)
        open(joinpath(dir, PROGRESS_NAME), "w") do io
            JSON3.write(io, Dict("schema" => SCHEMA, "completed_rows" => sort(collect(done))))
        end
    end
    return path
end

"""
    assert_s01_gate(manifest, expected_basis)

Refuse to run on missing/wrong-schema S01 or a mismatched basis convention
(no silent adaptation). Returns the degenerate index set on success.
"""
function assert_s01_gate(manifest, expected_basis::AbstractString)
    manifest["schema"] == "shared01/v1" || throw(ErrorException("unexpected S01 schema"))
    manifest["basis_convention"] == expected_basis ||
        throw(ErrorException("S01 basis convention mismatch; refusing silent adaptation"))
    return Set{Tuple{Int,Int}}([(Int(p["grid_index"][1]), Int(p["grid_index"][2]))
                                for p in manifest["degenerate_points"]])
end

"""
    assemble_D01(dir, s_grid, delta_grid, s01_id, degenerate_set, thresholds) -> paths

Concatenate all 99 row chunks into the single D01 product + manifest.
"""
function assemble_D01(dir::AbstractString, s_grid::Vector{Float64}, delta_grid::Vector{Float64},
                      s01_id::AbstractString, degenerate_set::Set{Tuple{Int,Int}}, thresholds::Dict)
    ns, nd = length(s_grid), length(delta_grid)
    done = _read_progress(dir)
    length(done) == nd || throw(ErrorException("only $(length(done))/$nd rows complete; refusing assembly"))
    z_tilde = zeros(ns, nd)
    z_R = zeros(ns, nd)
    rho_trace = zeros(ns, nd)
    rho_min_eig = zeros(ns, nd)
    denom = zeros(ns, nd)
    for j in 1:nd
        c = NPZ.npzread(_rowpath(dir, j))
        vec(c["s_grid"]) == s_grid || throw(ErrorException("row $j s_grid mismatch"))
        c["delta"][] == delta_grid[j] || throw(ErrorException("row $j delta mismatch"))
        z_tilde[:, j] = vec(c["z_tilde"])
        z_R[:, j] = vec(c["z_R"])
        rho_trace[:, j] = vec(c["rho_trace"])
        rho_min_eig[:, j] = vec(c["rho_min_eig"])
        denom[:, j] = vec(c["denom"])
    end
    degenerate = falses(ns, nd)
    for (i, j) in degenerate_set
        degenerate[i, j] = true
    end
    npz_path = joinpath(dir, D01_NPZ_NAME)
    tmp = npz_path * ".tmp"
    NPZ.npzwrite(tmp, Dict(
        "s_grid" => s_grid,
        "delta_grid" => delta_grid,
        "z_tilde" => z_tilde,
        "z_R" => z_R,
        "rho_trace" => rho_trace,
        "rho_min_eig" => rho_min_eig,
        "denom" => denom,
        "degenerate" => Array{Bool}(degenerate),
    ))
    mv(tmp, npz_path; force=true)
    manifest = Dict(
        "schema" => SCHEMA,
        "input_S01" => s01_id,
        "grid" => "s = i/100, delta = j/50, i,j = 1..99 (same ordering as S01)",
        "thresholds" => thresholds,
        "n_degenerate_inherited" => length(degenerate_set),
        "julia_version" => string(VERSION),
    )
    manifest_path = joinpath(dir, MANIFEST_NAME)
    open(manifest_path, "w") do io
        JSON3.write(io, manifest)
    end
    return npz_path, manifest_path
end

