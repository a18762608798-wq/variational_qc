# Experiment 04 orchestration ONLY (Julia round, new H; scan lines δ=0,1).
#
# Frozen optimizer (doc/plan/experiment/04_ideal_vqe.md): p=1 DE+COBYLA
# n_seeds=3; p>=2 warm start + n_restarts=3 + clamp; box [-π,π];
# δ=0 halved (structural); δ=1 AFM first-layer two ZZ frozen 0; byte-exact seeds.
# S_REF imported from exp03 (scan-03-04 rule 1): 04 never regenerates s.

isdefined(Main, :SSHXXZ) ||
    include(joinpath(@__DIR__, "..", "src_jl", "SSHXXZ.jl"))
using .SSHXXZ
using Yao: apply, zero_state
include(joinpath(@__DIR__, "exp03_reference.jl"))

using Yao: apply, zero_state

const CODE_VERSION = "0.2.0-julia"
const TAU = 1e-6
const BRANCHES = ("trivial", "topological", "afm")
const DELTAS = (0.0, 0.85)
const DEPTHS = (1, 2, 3, 4, 5)

check_variational_principle(evar, e0, tau=TAU) =
    Float64(evar) >= Float64(e0) - tau ? "ok" : "failed"

function apply_nesting_clamp(candidates, baseline, tau=TAU)
    bx, bf = baseline
    pool = [(collect(Float64, bx), Float64(bf), true)]
    for (x, f) in candidates
        push!(pool, (collect(Float64, x), Float64(f), false))
    end
    return argmin(c -> c[2], pool)
end

function frozen_mask(L, p, delta, init)
    mask = falses(n_params(L, p, delta))
    if delta != 0 && init == "afm" && p >= 1
        # First layer, first even sublayer (F=e for AFM): the two ZZ orbit
        # params (θ2 of each even orbit) frozen to 0. Per-layer layout:
        # [F orbits (θ1,θ2)...][S orbits...]; even orbits first.
        mask[2] = true
        mask[4] = true
    end
    return mask
end

function _state_obs(L, p, d, branch, theta)
    psi = vec(apply(zero_state(L), full_circuit(L, p, d, branch, theta)).state)
    return Float64(s_pi(psi, L)), Float64(string_order(psi, L))
end

function _run_one_branch(L, s, d, p, branch, H, e_fn, prev_opt, de_budget)
    mask = frozen_mask(L, p, d, branch)
    free = findall(.!mask)
    seedt = (s, d, branch)
    if p == 1
        fn_free_p1(xf) = (th = zeros(n_params(L, p, d)); th[free] = xf; e_fn(th))
        mb, mf, _ = optimize_p1(fn_free_p1, length(free), seedt;
                                maxsteps=de_budget[1], popsize=de_budget[2])
        th = zeros(n_params(L, p, d))
        th[free] = mb
        return th, mf, 0, false
    end
    prev_th, _ = prev_opt
    base_full = embed_params(prev_th, L, p, d, branch)
    base_full[mask] .= 0.0
    f_base = e_fn(base_full)
    fn_free_warm(xf) = (th = copy(base_full); th[free] = xf; e_fn(th))
    new_start = n_params(L, p - 1, d)
    pos = [k for (k, gi) in enumerate(free) if gi > new_start]
    bx, bf, _, flag = optimize_warm(fn_free_warm, base_full[free], pos, seedt,
                                    (base_full[free], f_base))
    th = copy(base_full)
    th[free] = bx
    return th, bf, 0, flag
end

function run_one_chain(var_dir, L, d, s, branch, depths, de_budget)
    s, d = Float64(s), Float64(d)
    H = build_hamiltonian(L, s, d)
    prev = nothing
    for p in depths
        key = Dict("L" => L, "s" => s, "delta" => d, "p" => p,
                   "branch" => branch, "seed" => Int(derive_seed(s, d, branch, 0)))
        if point_exists(var_dir, "exp04b", key)
            rec = only([r for r in iter_points(var_dir, "exp04b")
                        if r["status"] == "ok" && r["s"] == s &&
                           r["delta"] == d && r["p"] == p && r["branch"] == branch])
            prev = (Vector{Float64}(vec(rec["theta"])), Float64(rec["Ebranch"]))
            continue
        end
        e_fn = make_energy_fn(L, p, d, branch, H)
        th, f, nexp, flag = _run_one_branch(L, s, d, p, branch, H, e_fn, prev,
                                            de_budget)
        save_point(var_dir, "exp04b",
                   merge(key, Dict("theta" => collect(th), "Ebranch" => Float64(f),
                                   "nevals" => Int(nexp),
                                   "from_baseline" => Bool(flag),
                                   "status" => "ok", "experiment" => "exp04",
                                   "backend" => "julia-yao",
                                   "code_version" => CODE_VERSION,
                                   "source" => "ideal-variational")))
        prev = (th, f)
    end
end

function select_one_point(var_dir, ref_dir, L, d, s, depths; branches=BRANCHES)
    s, d = Float64(s), Float64(d)
    ref = Dict((r["s"], r["delta"]) => r for r in iter_points(ref_dir, "exp03")
               if r["status"] == "ok")
    n = 0
    for p in depths
        sel_key = Dict("L" => L, "s" => s, "delta" => d, "p" => p)
        if point_exists(var_dir, "exp04s", sel_key)
            n += 1
            continue
        end
        brev = Dict(b => only([r for r in iter_points(var_dir, "exp04b")
                               if r["status"] == "ok" && r["s"] == s &&
                                  r["delta"] == d && r["p"] == p &&
                                  r["branch"] == b])["Ebranch"] for b in branches)
        bname, bf = select_branch(Dict(b => Float64(v) for (b, v) in brev))
        brec = only([r for r in iter_points(var_dir, "exp04b")
                     if r["status"] == "ok" && r["s"] == s &&
                        r["delta"] == d && r["p"] == p && r["branch"] == bname])
        eref = ref[(s, d)]
        stat = check_variational_principle(bf, Float64(eref["E0"]))
        spi_v, ostr_v = _state_obs(L, p, d, bname, Vector{Float64}(vec(brec["theta"])))
        save_point(var_dir, "exp04s",
                   merge(sel_key, Dict("branch" => bname, "Evar" => Float64(bf),
                                       "Spi" => Float64(spi_v),
                                       "Ostr" => Float64(ostr_v),
                                       "E0" => Float64(eref["E0"]),
                                       "check_vp" => stat,
                                       "status" => stat == "ok" ? "ok" : "failed",
                                       "experiment" => "exp04",
                                       "backend" => "julia-yao",
                                       "code_version" => CODE_VERSION,
                                       "source" => "ideal-variational")))
        n += 1
    end
    return n
end

function run_branches(var_dir, ref_dir; L=8, deltas=DELTAS, s_grid=S_REF,
                      depths=DEPTHS, branches=BRANCHES, de_budget=(300, 10))
    n_sel = 0
    for d in deltas, s in s_grid, branch in branches
        run_one_chain(var_dir, L, Float64(d), Float64(s), branch, depths,
                      de_budget)
    end
    for d in deltas, s in s_grid
        n_sel += select_one_point(var_dir, ref_dir, L, Float64(d), Float64(s),
                                  depths; branches=branches)
    end
    write_manifest(var_dir, "exp04",
                   Dict("schema" => "exp01-04/v2", "L" => L,
                        "depths" => collect(depths),
                        "code_version" => CODE_VERSION))
    return n_sel
end

function write_manifest_wrap(var_dir, depths)
    write_manifest(var_dir, "exp04",
                   Dict("schema" => "exp01-04/v2", "L" => 8,
                        "depths" => collect(depths),
                        "code_version" => CODE_VERSION))
end

function verify_selection(var_dir, ref_dir; tau=TAU)
    ref = Dict((r["s"], r["delta"]) => r for r in iter_points(ref_dir, "exp03")
               if r["status"] == "ok")
    sel = [r for r in iter_points(var_dir, "exp04s") if r["status"] in ("ok", "failed")]
    n_viol = count(r -> Float64(r["Evar"]) < Float64(ref[(r["s"], r["delta"])]["E0"]) - tau, sel)
    by_sd = Dict()
    for r in sel
        push!(get!(by_sd, (r["s"], r["delta"]), Dict()), r["p"] => Float64(r["Evar"]))
    end
    nest_viol = 0
    for (_, pd) in by_sd
        for p in sort(collect(keys(pd)))[2:end]
            pd[p] > pd[p - 1] + tau && (nest_viol += 1)
        end
    end
    return Dict("n_selected" => length(sel), "n_violations" => n_viol,
                "n_nesting_violations" => nest_viol)
end
