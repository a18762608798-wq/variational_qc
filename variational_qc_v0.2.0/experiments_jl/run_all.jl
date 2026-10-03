# Point-level parallel launcher (T051, R6 as amended).
#
# Threads.@threads over points/chains (NOT Distributed: module-closure
# serialization across processes proved fragile; threads share memory, which
# also suits the memory-tight box). BLAS single-threaded to avoid
# oversubscription; determinism comes from derived seeds, so threaded results
# equal serial ones. Selection stays serial (cheap).

using Base.Threads
using LinearAlgebra

const _ROOT = normpath(joinpath(@__DIR__, ".."))

# Top-level includes (world-age safe): functions exist before any task runs.
include(joinpath(_ROOT, "src_jl", "SSHXXZ.jl"))
using .SSHXXZ
include(joinpath(_ROOT, "experiments_jl", "exp01_phase.jl"))
include(joinpath(_ROOT, "experiments_jl", "exp02_observables.jl"))
include(joinpath(_ROOT, "experiments_jl", "exp03_reference.jl"))
include(joinpath(_ROOT, "experiments_jl", "exp04_ideal.jl"))

function _setup_threads()
    try
        LinearAlgebra.BLAS.set_num_threads(1)
    catch
    end
    return nthreads()
end

function run_01_grid(data_dir, s_grid, d_grid; L=8, workers=nthreads())
    jobs = [(Float64(s), Float64(d)) for s in s_grid for d in d_grid]
    _setup_threads()
    @threads for (s, d) in jobs
        run_one_grid_point(data_dir, L, s, d)
    end
    write_manifest_wrap(data_dir, L)
    return length(jobs)
end

function run_01_gaps(data_dir, Ls, s_grid; workers=nthreads())
    jobs = [(L, Float64(s)) for L in Ls for s in s_grid]
    _setup_threads()
    @threads for (L, s) in jobs
        run_one_gap_point(data_dir, L, s)
    end
    return length(jobs)
end

function run_02_heat(data_dir, s_grid, d_grid; L=8, workers=nthreads())
    jobs = [(Float64(s), Float64(d)) for s in s_grid for d in d_grid]
    _setup_threads()
    @threads for (s, d) in jobs
        run_one_heatmap_point(data_dir, L, s, d)
    end
    write_manifest_wrap(data_dir, L)
    return length(jobs)
end

function run_03_ref(data_dir, deltas, s_grid; L=8, workers=nthreads())
    jobs = [(Float64(s), Float64(d)) for d in deltas for s in s_grid]
    _setup_threads()
    @threads for (s, d) in jobs
        run_one_ref_point(data_dir, L, s, d)
    end
    write_manifest_wrap(data_dir, L)
    return length(jobs)
end

function run_04_chains(var_dir, ref_dir, deltas, s_grid, branches, depths,
                       de_budget=(300, 10); workers=nthreads())
    jobs = [(Float64(d), Float64(s), b) for d in deltas for s in s_grid
            for b in branches]
    _setup_threads()
    @threads for (d, s, b) in jobs
        run_one_chain(var_dir, 8, d, s, b, collect(depths), de_budget)
    end
    n = 0
    for d in deltas, s in s_grid
        n += select_one_point(var_dir, ref_dir, 8, Float64(d), Float64(s),
                              collect(depths); branches=branches)
    end
    write_manifest_wrap(var_dir, depths)
    return n
end
