# Formal production run for exp03 (T005).
# Thin orchestration only: module APIs -> chunked persist -> assembly.
# Experiment conditions come from specs/exp03/spec.md; nothing is redefined here.
# Production order L = 8 -> 12 -> 16 (plan §3): cheap sizes validate the chain first.

push!(LOAD_PATH, joinpath(@__DIR__, "..", "src"))
using LinearAlgebra
BLAS.set_num_threads(1)  # point-level threading only (constitution V)
using Shared01  # load order: Exp03 reuses Shared01.Hamiltonian read-only
using Exp03
using Exp03.GapSolver: GapResult, solve_gap, union_points
using Exp03.Store: save_chunk, completed_chunks, assemble_D02, chunk_id, LS, BLOCK,
                    save_extra, EXTRA_ID, EXTRA_LS

const OUT_DIR = joinpath(@__DIR__, "..", "data", "exp03")

function main()
    println("threads: ", Threads.nthreads())
    flush(stdout)
    pts = union_points()
    println("union points per L: ", length(pts))
    flush(stdout)
    nblocks = cld(length(pts), BLOCK)
    for L in LS
        done = completed_chunks(OUT_DIR)
        todo = [ib for ib in 1:nblocks if chunk_id(L, ib) ∉ done]
        println("L=$L blocks to compute: $(length(todo))/$nblocks")
        flush(stdout)
        t0 = time()
        for ib in todo
            lo = (ib - 1) * BLOCK + 1
            hi = min(ib * BLOCK, length(pts))
            idx = collect(lo:hi)
            res = Vector{GapResult}(undef, length(idx))
            Threads.@threads for t in eachindex(idx)
                g = idx[t]
                res[t] = solve_gap(L, pts[g].s)
            end
            save_chunk(OUT_DIR, L, ib, [pts[g].key for g in idx],
                       [pts[g].s for g in idx], res)
            println("L=$L block $ib/$nblocks done")
            flush(stdout)
        end
        println("L=$L done in $(round(time() - t0, digits=1))s")
        flush(stdout)
    end
    # (iii) extra points at (δ=0, s=0.5) for L=20,24 (spec PRE-004; serial, L=24 ~2min).
    if EXTRA_ID ∉ completed_chunks(OUT_DIR)
        t0 = time()
        res = [solve_gap(L, 0.5) for L in EXTRA_LS]
        save_extra(OUT_DIR, collect(EXTRA_LS), res)
        println("extra points done in $(round(time() - t0, digits=1))s")
        flush(stdout)
    else
        println("extra points: already complete")
        flush(stdout)
    end
    npz_path, manifest_path = assemble_D02(OUT_DIR)
    println("wrote: $npz_path")
    println("wrote: $manifest_path")
end

main()
