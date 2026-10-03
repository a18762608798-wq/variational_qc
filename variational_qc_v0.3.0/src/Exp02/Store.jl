# Incremental persistence for exp02 (constitution IV).
# D04: one chunk per δ row + progress manifest + assembly.
# D03: three small curves, written directly (computed alongside rows).
# I/O only.

module Store

using NPZ, JSON3
using ..Panels: PanelPoint

export save_row, completed_rows, save_d03, assemble_D04,
       CHUNKS_DIRNAME, ROW_PREFIX, PROGRESS_NAME,
       D03_NAME, D04_NPZ_NAME, MANIFEST_NAME, SCHEMA

const SCHEMA = "exp02/v1"
const CHUNKS_DIRNAME = "chunks"
const ROW_PREFIX = "row_"
const PROGRESS_NAME = "progress.json"
const D03_NAME = "exp02_D03.npz"
const D04_NPZ_NAME = "exp02_D04.npz"
const MANIFEST_NAME = "exp02_manifest.json"

_chunks(dir) = joinpath(dir, CHUNKS_DIRNAME)
_rowpath(dir, j) = joinpath(_chunks(dir), "$(ROW_PREFIX)$(lpad(j, 3, '0')).npz")

function _read_progress(dir)
    path = joinpath(dir, PROGRESS_NAME)
    isfile(path) || return Set{Int}()
    return Set{Int}(open(JSON3.read, path)["completed_rows"])
end

completed_rows(dir::AbstractString) = _read_progress(dir)

const _PROGRESS_LOCK = ReentrantLock()

"""Persist one δ row (atomically) and record it in the progress manifest."""
function save_row(dir::AbstractString, j::Int, s_grid::Vector{Float64},
                  delta::Float64, pts::Vector{PanelPoint})
    mkpath(_chunks(dir))
    path = _rowpath(dir, j)
    tmp = path * ".tmp"
    NPZ.npzwrite(tmp, Dict(
        "s_grid" => s_grid,
        "delta" => delta,
        "s_pi" => [p.s_pi for p in pts],
        "o_str" => [p.o_str for p in pts],
        "q_val" => [p.q_val for p in pts],
        "z_tilde" => [p.z_tilde for p in pts],
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

"""Persist the D03 curves (small; written directly, no chunking).
Labels travel in a JSON sidecar (NPZ has no string arrays)."""
function save_d03(dir::AbstractString, q_grid::Vector{Float64},
                  curves::Matrix{Float64}, rep_labels::Vector{String})
    mkpath(dir)
    path = joinpath(dir, D03_NAME)
    tmp = path * ".tmp"
    NPZ.npzwrite(tmp, Dict("q_grid" => q_grid, "curves" => curves))
    mv(tmp, path; force=true)
    open(joinpath(dir, "exp02_D03_meta.json"), "w") do io
        JSON3.write(io, Dict("rep_labels" => rep_labels,
                             "q_grid" => "q = 2πk/100, k = 1..99 (includes q=π at k=50)"))
    end
    return path
end

"""Assemble all 99 row chunks into the single D04 product + manifest."""
function assemble_D04(dir::AbstractString, s_grid::Vector{Float64}, delta_grid::Vector{Float64},
                      s01_id::AbstractString, degenerate_set::Set{Tuple{Int,Int}},
                      extra::Dict)
    ns, nd = length(s_grid), length(delta_grid)
    done = _read_progress(dir)
    length(done) == nd || throw(ErrorException("only $(length(done))/$nd rows complete"))
    panels = Dict{String,Matrix{Float64}}()
    for key in ("s_pi", "o_str", "q_val", "z_tilde")
        mat = zeros(ns, nd)
        for j in 1:nd
            c = NPZ.npzread(_rowpath(dir, j))
            vec(c["s_grid"]) == s_grid || throw(ErrorException("row $j s_grid mismatch"))
            c["delta"][] == delta_grid[j] || throw(ErrorException("row $j delta mismatch"))
            mat[:, j] = vec(c[key])
        end
        panels[key] = mat
    end
    degenerate = falses(ns, nd)
    for (i, j) in degenerate_set
        degenerate[i, j] = true
    end
    npz_path = joinpath(dir, D04_NPZ_NAME)
    tmp = npz_path * ".tmp"
    NPZ.npzwrite(tmp, merge(Dict(
        "s_grid" => s_grid,
        "delta_grid" => delta_grid,
        "degenerate" => Array{Bool}(degenerate),
    ), panels))
    mv(tmp, npz_path; force=true)
    manifest = merge(Dict(
        "schema" => SCHEMA,
        "input_S01" => s01_id,
        "grid" => "s = i/100, delta = j/50, i,j = 1..99 (same ordering as S01)",
        "n_degenerate_inherited" => length(degenerate_set),
        "julia_version" => string(VERSION),
    ), extra)
    manifest_path = joinpath(dir, MANIFEST_NAME)
    open(manifest_path, "w") do io
        JSON3.write(io, manifest)
    end
    return npz_path, manifest_path
end

end # module
