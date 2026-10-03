# Ideal optimizer. Frozen settings: doc/plan/experiment/04_ideal_vqe.md.
#
# p=1: BlackBoxOptim adaptive-DE + NLopt COBYLA polish, n_seeds=3.
# p>=2: warm start + U(-0.3,0.3) new layer, n_restarts=3, COBYLA polish,
# clamp to baseline when worse. Box [-π,π]. Ideal statevector only.

module Optimizer

# NOTE: include order matters — including files must include VQE/Seeds.jl
# and Core/Ansatz.jl BEFORE this file.
using BlackBoxOptim, NLopt, Yao, LinearAlgebra, Random
using ..Ansatz: build_ansatz_circuit, full_circuit, n_params
using ..Seeds: derive_seed
using Random

export make_energy_fn, optimize_p1, optimize_warm,
       BOX, N_SEEDS, N_RESTARTS, PERTURB

const BOX = (-π, π)
const N_SEEDS = 3
const N_RESTARTS = 3
const PERTURB = 0.3

function make_energy_fn(L, p, delta, init, H)
    function fn(theta)
        psi = vec(apply(zero_state(L), full_circuit(L, p, delta, init, theta)).state)
        return real(dot(psi, H * psi))
    end
    return fn
end

function _polish(energy_fn, x0; maxeval=2000)
    opt = Opt(:LN_COBYLA, length(x0))
    opt.min_objective = (x, g) -> energy_fn(x)
    opt.maxeval = maxeval
    opt.lower_bounds = fill(BOX[1], length(x0))
    opt.upper_bounds = fill(BOX[2], length(x0))
    minf, minx, _ = optimize(opt, collect(Float64, x0))
    return minx, minf
end

function optimize_p1(energy_fn, dim, seed_tuple; maxsteps=300, popsize=10)
    s, delta, init = seed_tuple
    best = (nothing, Inf, 0)
    for r in 0:(N_SEEDS - 1)
        Random.seed!(derive_seed(s, delta, init, r))
        res = bboptimize(energy_fn; SearchRange=fill(BOX, dim),
                         NumDimensions=dim, PopulationSize=popsize,
                         Method=:adaptive_de_rand_1_bin,
                         MaxSteps=maxsteps, TraceMode=:silent)
        x, f = _polish(energy_fn, best_candidate(res))
        if f < best[2]
            best = (x, f, 0)
        end
    end
    return best
end

function optimize_warm(energy_fn, x0_free, perturb_pos, seed_tuple, baseline;
                       n_restarts=N_RESTARTS, width=PERTURB)
    s, delta, init = seed_tuple
    bx, bf = baseline
    cands = [(collect(Float64, bx), Float64(bf), 0, true)]
    for r in 0:(n_restarts - 1)
        rng = Random.Xoshiro(derive_seed(s, delta, init, 1000 + r))
        x0 = collect(Float64, x0_free)
        x0[perturb_pos] .= clamp.(x0[perturb_pos] .+ rand(rng, length(perturb_pos)) .* 2width .- width, BOX[1], BOX[2])
        x, f = _polish(energy_fn, x0)
        push!(cands, (x, f, 0, false))
    end
    return argmin(c -> c[2], cands)
end

end # module
