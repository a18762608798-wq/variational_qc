# Formal production run for exp01 (T004).
# Thin orchestration only: S01 input gating -> module APIs -> chunked persist -> assembly.
# Experiment conditions come from specs/exp01/spec.md; nothing is redefined here.

push!(LOAD_PATH, joinpath(@__DIR__, "..", "src"))
using LinearAlgebra
BLAS.set_num_threads(1)  # grid-level threading only (constitution V)
using Shared01
using Shared01: S_GRID, DELTA_GRID
using Shared01: load_shared01
using Exp01
using Exp01: z_tilde, EXPECTED_BASIS_CONVENTION
using Exp01: save_row, completed_rows, assemble_D01, assert_s01_gate

const S01_DIR = joinpath(@__DIR__, "..", "data", "shared01")
const OUT_DIR = joinpath(@__DIR__, "..", "data", "exp01")
const THRESHOLDS = Dict("trace_tol" => 1e-10, "min_eig_tol" => -1e-10, "denom_min" => 1e-12)

function main()
    println("threads: ", Threads.nthreads())
    flush(stdout)
    arrays, manifest = load_shared01(S01_DIR)
    deg = assert_s01_gate(manifest, EXPECTED_BASIS_CONVENTION)
    s01_id = "shared01/v1 created $(manifest["created_utc"])"
    println("S01 gate OK; degenerate points: $(length(deg))")
    flush(stdout)

    psi_all = arrays["psi"]
    todo = setdiff(Set(1:99), completed_rows(OUT_DIR))
    println("rows to compute: $(length(todo))")
    flush(stdout)
    t0 = time()
    Threads.@threads for j in collect(todo)
        res = [z_tilde(Vector{ComplexF64}(psi_all[i, j, :])) for i in 1:99]
        save_row(OUT_DIR, j, collect(Float64, S_GRID), Float64(DELTA_GRID[j]), res)
    end
    println("rows done in $(round(time() - t0, digits=1))s")
    flush(stdout)
    npz_path, manifest_path = assemble_D01(OUT_DIR, collect(Float64, S_GRID),
        collect(Float64, DELTA_GRID), s01_id, deg, THRESHOLDS)
    println("wrote: $npz_path")
    println("wrote: $manifest_path")
end

main()
