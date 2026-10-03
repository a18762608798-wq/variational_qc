# Formal production run for shared-01 (T005).
# Thin orchestration only: assemble grid -> call module APIs -> persist.
# Experiment conditions come from specs/shared-01/spec.md; nothing is
# redefined here.

push!(LOAD_PATH, joinpath(@__DIR__, "..", "src"))
using LinearAlgebra
BLAS.set_num_threads(1)  # parallelism is over grid points (Julia threads)
using Shared01
using Shared01.GroundStates, Shared01.Store

const OUT_DIR = joinpath(@__DIR__, "..", "data", "shared01")

function main()
    println("threads: ", Threads.nthreads())
    t0 = time()
    sol = solve_grid()
    println("solve: $(round(time() - t0, digits=1))s for $(length(sol)) points")
    ndeg = count(s -> s.degenerate, sol)
    println("degenerate-flagged points: $ndeg")
    npz_path, manifest_path = save_shared01(OUT_DIR, sol)
    println("wrote: $npz_path")
    println("wrote: $manifest_path")
end

main()
