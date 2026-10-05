# T006 full-grid assertions against the production output.
# Fails (nonzero exit) on any violation.

push!(LOAD_PATH, joinpath(@__DIR__, "..", "src"))
using LinearAlgebra
BLAS.set_num_threads(1)
using Shared01
using Shared01

const DATA = joinpath(@__DIR__, "..", "data", "shared01")
failures = String[]

function check(cond::Bool, msg::String)
    cond || push!(failures, msg)
    println((cond ? "PASS " : "FAIL ") * msg)
end

arrays, manifest = load_shared01(DATA)
E0, E1, psi = arrays["E0"], arrays["E1"], arrays["psi"]

check(size(E0) == (99, 99), "E0 shape 99x99")
check(size(E1) == (99, 99), "E1 shape 99x99")
check(size(psi) == (99, 99, 256), "psi shape 99x99x256")
check(vec(arrays["s_grid"]) == S_GRID, "s_grid matches spec")
check(vec(arrays["delta_grid"]) == DELTA_GRID, "delta_grid matches spec")
check(all(E1 .>= E0), "E1 >= E0 everywhere")
check(maximum(abs.(vec(mapslices(norm, psi, dims=3)) .- 1.0)) < 1e-12, "all psi normalized")

# S02 consistency: manifest rep E0 vs npz at rep grid indices
reps = manifest["representative_points_S02"]
for label in REP_LABELS
    s, d = REP_POINTS[label]
    i = round(Int, 100 * s)
    j = round(Int, 50 * d)
    check(reps[label]["E0"] == E0[i, j], "S02 $label manifest/npz E0 agreement")
end

# Degeneracy table completeness: recomputed set == manifest set
recomputed = Set([(i, j) for j in 1:99 for i in 1:99 if (E1[i, j] - E0[i, j]) < DEGENERACY_TOL])
listed = Set([(Int(p["grid_index"][1]), Int(p["grid_index"][2])) for p in manifest["degenerate_points"]])
check(recomputed == listed, "degeneracy table complete ($(length(listed)) points)")

# Full residual check (rebuild H per point, threaded, deterministic order)
res = zeros(99, 99)
Threads.@threads for j in 1:99
    for i in 1:99
        H = build_hamiltonian(8, S_GRID[i], DELTA_GRID[j])
        v = Vector{ComplexF64}(psi[i, j, :])
        res[i, j] = norm(H * v - E0[i, j] * v) / max(1.0, norm(H))
    end
end
check(maximum(res) < 1e-8, "max eigen residual $(maximum(res)) < 1e-8")

if isempty(failures)
    println("VERIFY-PRODUCTION-OK")
else
    println("VERIFY-PRODUCTION-FAILURES: ", length(failures))
    exit(1)
end
