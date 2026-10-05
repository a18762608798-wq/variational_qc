# Persistence for S01/S02: one .npz (numpy-readable arrays) plus a JSON manifest
# carrying all provenance needed for reproducibility (shared-01 POST-001, POST-003).
# I/O lives here only; numerical kernels never touch files.

const SCHEMA = "shared01/v1"
const NPZ_NAME = "shared01_S01.npz"
const MANIFEST_NAME = "shared01_manifest.json"

function _grid_index(s::Real, delta::Real)
    i = round(Int, 100 * s)
    j = round(Int, 50 * delta)
    ok = 1 <= i <= length(S_GRID) && 1 <= j <= length(DELTA_GRID) &&
         S_GRID[i] == Float64(s) && DELTA_GRID[j] == Float64(delta)
    ok || throw(ArgumentError("($(s), $(delta)) is not an S01 grid point"))
    return i, j
end

"""
    save_shared01(dir, sol) -> (npz_path, manifest_path)

Persist the full 99×99 solution grid. Writes atomically (tmp + rename).
"""
function save_shared01(dir::AbstractString, sol::Matrix{PointSolution})
    mkpath(dir)
    ns, nd = length(S_GRID), length(DELTA_GRID)
    size(sol) == (ns, nd) || throw(ArgumentError("expected $((ns, nd)), got $(size(sol))"))

    E0 = [sol[i, j].E0 for i in 1:ns, j in 1:nd]
    E1 = [sol[i, j].E1 for i in 1:ns, j in 1:nd]
    psi = Array{ComplexF64}(undef, ns, nd, 1 << L_SYS)
    for j in 1:nd, i in 1:ns
        psi[i, j, :] = sol[i, j].psi0
    end

    npz_path = joinpath(dir, NPZ_NAME)
    tmp = npz_path * ".tmp"
    NPZ.npzwrite(tmp, Dict(
        "s_grid" => collect(S_GRID),
        "delta_grid" => collect(DELTA_GRID),
        "E0" => E0,
        "E1" => E1,
        "psi" => psi,
    ))
    mv(tmp, npz_path; force=true)

    deg = [(i, j) for j in 1:nd for i in 1:ns if sol[i, j].degenerate]
    reps = Dict(label => begin
        s, d = REP_POINTS[label]
        i, j = _grid_index(s, d)
        Dict("s" => s, "delta" => d, "grid_index" => [i, j], "E0" => sol[i, j].E0)
    end for label in REP_LABELS)

    manifest = Dict(
        "schema" => SCHEMA,
        "L" => L_SYS,
        "s_grid" => "i/100 for i = 1..99",
        "delta_grid" => "j/50 for j = 1..99",
        "sector" => "full Hilbert space, direct diagonalization of H (no H' penalty)",
        "basis_convention" => "site m (1-indexed) <-> bit (m-1) of basis index, LSB = site 1; |0> is Z=+1",
        "H_def_id" => H_DEF_ID,
        "solver" => "dense Hermitian eigen (LinearAlgebra.eigen), lowest two pairs",
        "precision" => "ComplexF64",
        "degeneracy_tol" => DEGENERACY_TOL,
        "degenerate_points" => [Dict("grid_index" => [i, j], "s" => S_GRID[i],
                                     "delta" => DELTA_GRID[j]) for (i, j) in deg],
        "representative_points_S02" => reps,
        "julia_version" => string(VERSION),
        "created_utc" => Dates.format(Dates.now(Dates.UTC), Dates.ISODateTimeFormat),
    )
    manifest_path = joinpath(dir, MANIFEST_NAME)
    open(manifest_path, "w") do io
        JSON3.write(io, manifest)
    end
    return npz_path, manifest_path
end

"""
    load_shared01(dir) -> (arrays::Dict, manifest::Dict)
"""
function load_shared01(dir::AbstractString)
    arrays = NPZ.npzread(joinpath(dir, NPZ_NAME))
    manifest = open(JSON3.read, joinpath(dir, MANIFEST_NAME))
    return arrays, manifest
end

"""
    point_at(arrays, s, delta) -> (E0, E1, psi0)

Retrieve one grid point by exact (s, δ) coordinates.
"""
function point_at(arrays::Dict, s::Real, delta::Real)
    i, j = _grid_index(s, delta)
    return arrays["E0"][i, j], arrays["E1"][i, j], Vector{ComplexF64}(arrays["psi"][i, j, :])
end
