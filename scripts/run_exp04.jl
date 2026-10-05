# Formal production run for exp04 (T005).
# Thin orchestration only: module APIs -> per-δ chunked persist -> assembly.
# Experiment conditions come from specs/exp04/spec.md; nothing is redefined here.
# Production order δ = 0 -> 0.85 (plan §3).

push!(LOAD_PATH, joinpath(@__DIR__, "..", "src"))
using LinearAlgebra
BLAS.set_num_threads(1)  # point-level threading only (constitution V)
using Shared01  # load order: Exp04 reuses Shared01.Hamiltonian read-only
using Shared01.Hamiltonian: build_hamiltonian
using Exp01  # load order: Exp02 reuses Exp01 read-only
using Exp02
using Exp02.Correlators: zz_correlators, structure_factor
using Exp02.StringOrder: string_order
using Exp04
using Exp04: LEG_LABELS, psi_init
using Exp04: build_meta, nparams, apply_circuit!
using Exp04: run_point, expect_ztot, overlap_xbar, overlap_reflect
using Exp04: save_line, completed_lines, assemble_S06_S03,
              DELTAS, S_GRID, THETA_MAX, LINE_ID

const OUT_DIR = joinpath(@__DIR__, "..", "data", "exp04")

"""Evaluate winner-state observables + symmetry diagnostics for one (δ,s,p)."""
function eval_best(delta::Real, a_star::String, theta_star::Vector{Float64}, p::Integer)
    meta = build_meta(8, a_star)
    psi0 = psi_init(a_star, 8)
    psi = apply_circuit!(zeros(ComplexF64, 256), psi0, theta_star, meta, p, Float64(delta))
    C = zz_correlators(psi)
    spi = structure_factor(C, pi)
    ostr = string_order(psi)
    zt = abs(expect_ztot(psi, 8))
    xb = abs(overlap_xbar(psi, 8) - 1)
    xr = abs(overlap_reflect(psi, 8) - 1)
    return spi, ostr, zt, xb, xr
end

function run_line(delta::Real)
    ns = length(S_GRID)
    theta_star = fill(NaN, ns, 3, THETA_MAX)
    E_star = zeros(ns, 3)
    a_star = zeros(Int, ns, 3)
    spi = zeros(ns, 3)
    ostr = zeros(ns, 3)
    e0 = zeros(ns)
    leg_E = zeros(ns, 3, 3)
    conv = falses(ns, 3, 3)
    stagn = falses(ns, 3, 3)
    dtail = zeros(ns, 3, 3)
    theta_leg = fill(NaN, ns, 3, 3, THETA_MAX)  # [point, leg, p, params]
    einit = zeros(ns, 3)
    sym = zeros(ns, 3, 3)
    Threads.@threads for i in 1:ns
        s = S_GRID[i]
        H = build_hamiltonian(8, s, Float64(delta))
        e0[i] = minimum(eigvals(Hermitian(H)))
        pr = run_point(Float64(delta), s, H, e0[i])
        for (li, leg) in enumerate(LEG_LABELS)
            psi0 = psi_init(leg, 8)
            einit[i, li] = real(dot(psi0, H * psi0))
            for p in 1:3
                st = pr.steps[leg][p]
                leg_E[i, li, p] = st.energy
                conv[i, li, p] = st.converged
                stagn[i, li, p] = st.stagnant
                dtail[i, li, p] = st.dtail
                thv = Vector{Float64}(st.theta)
                theta_leg[i, li, p, 1:length(thv)] = thv
            end
        end
        for p in 1:3
            a, th, E = pr.best[p]
            li = findfirst(==(a), LEG_LABELS)
            a_star[i, p] = li
            E_star[i, p] = E
            thv = Vector{Float64}(th)
            theta_star[i, p, 1:length(thv)] = thv
            sp, os, zt, xb, xr = eval_best(Float64(delta), a, thv, p)
            spi[i, p] = sp
            ostr[i, p] = os
            sym[i, p, :] = [zt, xb, xr]
        end
    end
    return Dict("theta_star" => theta_star, "E_star" => E_star, "a_star" => a_star,
                "spi" => spi, "ostr" => ostr, "e0" => e0, "leg_E" => leg_E,
                "theta_leg" => theta_leg,
                "conv" => conv, "stagn" => stagn, "dtail" => dtail,
                "einit" => einit, "sym" => sym)
end

function main()
    println("threads: ", Threads.nthreads())
    flush(stdout)
    for delta in DELTAS
        done = completed_lines(OUT_DIR)
        if LINE_ID(delta) in done
            println("δ=$delta: already complete")
            flush(stdout)
            continue
        end
        t0 = time()
        payload = run_line(Float64(delta))
        save_line(OUT_DIR, Float64(delta), payload)
        println("δ=$delta done in $(round(time() - t0, digits=1))s")
        flush(stdout)
    end
    s06, s03, manifest = assemble_S06_S03(OUT_DIR)
    println("wrote: $s06")
    println("wrote: $s03")
    println("wrote: $manifest")
end

main()
