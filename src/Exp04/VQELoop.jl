# VQE loop for exp04 (spec PRE-001..PRE-003, INV-001..INV-002; docs/theory/cost_fun.md).
#
# Per (δ,s) point and init leg: p=1 global random sampling (+ zero vector) with
# top-K L-BFGS refinement; p=2,3 same-leg chained warm start + L-BFGS refine.
# Winner leg by min energy. Gradients by the parameter-shift rule (exact).
# Pure kernels (no I/O); threading lives in the run script (one point per task).

const MASTER_SEED = 20261004  # recorded in manifest (plan §3)
const N_GLOBAL = 64           # random samples per (p=1) leg, plus the zero vector
const TOP_K = 4               # refined samples per (p=1) leg
const G_TOL = 1e-8            # gradient-norm stop
const X_TOL = 1e-10           # parameter-stagnation stop (slow-tail valleys)
const F_TOL = 1e-10           # energy-stagnation stop
const MAX_ITERS = 1000
const STAG_WINDOW = 200       # ratchet gate: trailing window for ΔE
const STAG_TOL = 1e-4         # ratchet gate: ΔE threshold over the window
                              # (calibration, plan §6: observed valley crawl is
                              # ~1e-6/200iters; 1e-4 sits 100× above the crawl yet
                              # 10×+ below the finest S06 feature ~1e-3 and far
                              # below hardware noise; spec leaves the value to plan)
const STAG_E_TOL = 1e-8       # ratchet gate: E ≤ prev-level E* + this
const SAMPLE_RANGE = 4pi      # uniform [0, 4π): full period of primitive rotations

struct LegStep
    theta::Vector{Float64}
    energy::Float64
    converged::Bool
    stagnant::Bool   # ratchet acceptance (p>1 only; see run_leg)
    iters::Int
    dtail::Float64   # |f[end] - f[end-STAG_WINDOW]|: stagnation audit quantity
    seed::UInt64
    nsamples::Int
end

struct PointResult
    delta::Float64
    s::Float64
    steps::Dict{String,Vector{LegStep}}       # leg -> [p=1, p=2, p=3]
    best::Dict{Int,Tuple{String,Vector{Float64},Float64}}  # p -> (a*, θ*, E*)
    e0_exact::Float64                          # brute-force ground energy (plan §4)
end

"""Deterministic per-job seed from integers (stable across runs in this env)."""
_derive_seed(di::Integer, si::Integer, p::Integer, li::Integer) =
    hash((MASTER_SEED, Int(di), Int(si), Int(p), Int(li)))

"""Energy ⟨ψ(θ)|H|ψ(θ)⟩ with work buffers (caller-owned, thread-local)."""
function energy_of(theta::AbstractVector, H::Matrix{ComplexF64},
                   psi_init::Vector{ComplexF64}, meta::AnsatzMeta,
                   p::Integer, delta::Real, buf::Vector{ComplexF64})
    apply_circuit!(buf, psi_init, theta, meta, p, delta)
    return real(dot(buf, H * buf))
end

"""Exact gradient by the parameter-shift rule over gate occurrences."""
function pshift_gradient(theta::AbstractVector, H::Matrix{ComplexF64},
                         psi_init::Vector{ComplexF64}, meta::AnsatzMeta,
                         p::Integer, delta::Real, buf::Vector{ComplexF64})
    occ = occ_layout(meta, delta, p)
    base = Float64.(theta)[occ]
    n = length(theta)
    g = zeros(n)
    trial = similar(base)
    for j in eachindex(occ)
        copyto!(trial, base)
        trial[j] += pi / 2
        apply_occ!(buf, psi_init, trial, meta, p, delta)
        ep = real(dot(buf, H * buf))
        trial[j] -= pi
        apply_occ!(buf, psi_init, trial, meta, p, delta)
        em = real(dot(buf, H * buf))
        g[occ[j]] += (ep - em) / 2
    end
    return g
end

struct BondSched
    a::Int
    c::Int
    sa::Int   # stride 1<<(a-1), for index arithmetic
    sb::Int   # stride 1<<(c-1)
    pa::Int   # 0-based bit position a-1, for bit tests
    pb::Int   # 0-based bit position c-1
    idx::Vector{Int}
    kxx::Int
    kyy::Int
    kzz::Int
end

struct GradWork
    inw::Vector{Vector{ComplexF64}}
    m1w::Vector{Vector{ComplexF64}}
    m2w::Vector{Vector{ComplexF64}}
    final::Vector{ComplexF64}
    lam::Vector{ComplexF64}
end

"""Single L-BFGS refinement from θ0 (adjoint exact gradient).

Two-pass: if the first pass exhausts MAX_ITERS unconverged, restart a fresh
L-BFGS memory from its minimizer once (stale curvature estimates are the
usual stall cause in flat valleys; measured: pass-2 converges in ~270 iters
where pass-1 stalled 1000). Final = better of the two passes; iters summed.

Consistent pair: E* is ALWAYS re-evaluated at the reported θ* (Optim.minimum
can come from a rejected line-search trial and differ from f(minimizer) by
~1e-6; storing that pair would archive an energy no state attains).
Final gate: converged flag OR gradient norm at the reported θ* below G_TOL
(the gate's literal meaning: the archived point is stationary to tol).
"""
function _refine(theta0::Vector{Float64}, H::Matrix{ComplexF64},
                 psi_init::Vector{ComplexF64}, meta::AnsatzMeta,
                 p::Integer, delta::Real, seed::UInt64)
    buf = zeros(ComplexF64, length(psi_init))
    sched = bond_schedule(meta, Float64(delta), Int(p))
    W = make_gradwork(meta, Int(p), Float64(delta))
    f(th) = energy_of(th, H, psi_init, meta, p, delta, buf)
    function g!(G, th)
        adjoint_gradient!(G, th, H, psi_init, meta, p, delta, sched, W)
        return G
    end
    opts = Optim.Options(g_tol=G_TOL, x_abstol=X_TOL, f_abstol=F_TOL,
                         iterations=MAX_ITERS, store_trace=true)
    res1 = optimize(f, g!, Float64.(theta0), LBFGS(), opts)
    e1, c1, i1 = Float64(Optim.minimum(res1)), Optim.converged(res1),
                 Optim.iterations(res1)
    tr1 = Optim.trace(res1)
    fvals1 = Float64[t.value for t in tr1]
    dt1 = abs(fvals1[end] - fvals1[max(1, length(fvals1) - STAG_WINDOW)])
    if c1
        th = Vector{Float64}(Optim.minimizer(res1))
        return LegStep(th, f(th), true, false, i1, dt1, seed, 1)
    end
    res2 = optimize(f, g!, Vector{Float64}(Optim.minimizer(res1)), LBFGS(), opts)
    e2, c2, i2 = Float64(Optim.minimum(res2)), Optim.converged(res2),
                 Optim.iterations(res2)
    th2 = Vector{Float64}(Optim.minimizer(res2))
    tr2 = Optim.trace(res2)
    fvals2 = Float64[t.value for t in tr2]
    dt2 = abs(fvals2[end] - fvals2[max(1, length(fvals2) - STAG_WINDOW)])
    if e2 <= e1
        return _finalize(th2, f(th2), c2, i1 + i2, dt2, seed,
                         H, psi_init, meta, p, delta, sched, W)
    else
        th1 = Vector{Float64}(Optim.minimizer(res1))
        return _finalize(th1, f(th1), false, i1 + i2, dt1, seed,
                         H, psi_init, meta, p, delta, sched, W)
    end
end

"""Consistent-pair finalization: E* re-evaluated at θ*; gate checked at θ*."""
function _finalize(th::Vector{Float64}, E::Float64, conv::Bool, iters::Integer,
                   dtail::Float64, seed::UInt64, H::Matrix{ComplexF64},
                   psi_init::Vector{ComplexF64}, meta::AnsatzMeta,
                   p::Integer, delta::Real,
                   sched::Vector{BondSched}, W::GradWork)
    g = zeros(length(th))
    adjoint_gradient!(g, th, H, psi_init, meta, p, delta, sched, W)
    conv = conv || norm(g) < G_TOL
    return LegStep(th, E, conv, false, iters, dtail, seed, 1)
end

# --- adjoint (reverse-mode) exact gradient ----------------------------------
#
# Forward micro-states per bond: ψ_in --RXX--> m1 --RYY--> m2 --RZZ--> ψ_out.
# Backward: λ = H|ψ_final|; per bond (reversed):
#   g_zz += Im⟨λ|ZZ|m2⟩, λ ← RZZ†λ; same for YY/XX.
# Cost ≈ one forward + one backward pass (vs 2×#occurrences evals for shifts).

"""Static per-bond schedule (θ-independent part); angles read live from θ."""
function bond_schedule(meta::AnsatzMeta, delta::Real, p::Integer)
    occ = occ_layout(meta, delta, p)
    length(occ) % 3 == 0 || throw(ArgumentError("occurrence count not a triple"))
    bonds = Tuple{Int,Int}[]
    for l in 1:Int(p), sub in meta.order
        orbs = sub == :odd ? meta.odd_orbits : meta.even_orbits
        for orb in orbs, bond in orb
            push!(bonds, bond)
        end
    end
    length(bonds) * 3 == length(occ) || throw(ErrorException("schedule/order mismatch"))
    sched = BondSched[]
    for (j, (a, c)) in enumerate(bonds)
        push!(sched, BondSched(a, c, 1 << (a - 1), 1 << (c - 1), a - 1, c - 1,
                              meta.bond_bases[(a, c)],
                              occ[3j - 2], occ[3j - 1], occ[3j]))
    end
    return sched
end

"""Preallocated micro-state pool for one (meta, p, delta)."""
function make_gradwork(meta::AnsatzMeta, p::Integer, delta::Real)
    dim = 1 << meta.L
    nb = length(bond_schedule(meta, Float64(delta), Int(p)))
    return GradWork([zeros(ComplexF64, dim) for _ in 1:nb],
                    [zeros(ComplexF64, dim) for _ in 1:nb],
                    [zeros(ComplexF64, dim) for _ in 1:nb],
                    zeros(ComplexF64, dim), zeros(ComplexF64, dim))
end

"""Out-of-place bond application (read inn, write out)."""
function _apply_bond_to!(out::Vector{ComplexF64}, inn::Vector{ComplexF64},
                         idx::Vector{Int}, sa::Integer, sb::Integer,
                         U::Matrix{ComplexF64})
    copyto!(out, inn)
    u11, u12, u13, u14 = U[1, 1], U[1, 2], U[1, 3], U[1, 4]
    u21, u22, u23, u24 = U[2, 1], U[2, 2], U[2, 3], U[2, 4]
    u31, u32, u33, u34 = U[3, 1], U[3, 2], U[3, 3], U[3, 4]
    u41, u42, u43, u44 = U[4, 1], U[4, 2], U[4, 3], U[4, 4]
    @inbounds for t in eachindex(idx)
        i00 = idx[t]
        i10 = i00 + sa
        i01 = i00 + sb
        i11 = i01 + sa
        v00 = inn[i00]
        v10 = inn[i10]
        v01 = inn[i01]
        v11 = inn[i11]
        out[i00] = u11 * v00 + u12 * v10 + u13 * v01 + u14 * v11
        out[i10] = u21 * v00 + u22 * v10 + u23 * v01 + u24 * v11
        out[i01] = u31 * v00 + u32 * v10 + u33 * v01 + u34 * v11
        out[i11] = u41 * v00 + u42 * v10 + u43 * v01 + u44 * v11
    end
    return out
end

"""⟨λ|ZZ|m⟩ with ZZ diagonal (+1 equal bits, −1 different); pa/pb bit positions."""
function _zz_dot(lam::Vector{ComplexF64}, m::Vector{ComplexF64}, pa::Integer, pb::Integer)
    acc = ComplexF64(0)
    @inbounds for b in 0:(length(m) - 1)
        s = (((b >> pa) & 1) == ((b >> pb) & 1)) ? 1.0 : -1.0
        acc += conj(lam[b + 1]) * s * m[b + 1]
    end
    return acc
end

"""⟨λ|XX|m⟩ (bit-pair flip, no phase)."""
function _xx_dot(lam::Vector{ComplexF64}, m::Vector{ComplexF64}, flip::Integer)
    acc = ComplexF64(0)
    @inbounds for b in 0:(length(m) - 1)
        acc += conj(lam[b + 1]) * m[(b ⊻ flip) + 1]
    end
    return acc
end

"""⟨λ|YY|m⟩ (bit-pair flip, −1 on equal bits, +1 on different); pa/pb positions."""
function _yy_dot(lam::Vector{ComplexF64}, m::Vector{ComplexF64},
                 pa::Integer, pb::Integer, flip::Integer)
    acc = ComplexF64(0)
    @inbounds for b in 0:(length(m) - 1)
        s = (((b >> pa) & 1) == ((b >> pb) & 1)) ? -1.0 : 1.0
        acc += conj(lam[b + 1]) * s * m[(b ⊻ flip) + 1]
    end
    return acc
end

"""Exact gradient by one forward + one backward pass. g filled in place."""
function adjoint_gradient!(g::AbstractVector, theta::AbstractVector, H::Matrix{ComplexF64},
                           psi_init::Vector{ComplexF64}, meta::AnsatzMeta,
                           p::Integer, delta::Real,
                           sched::Vector{BondSched}, W::GradWork)
    nb = length(sched)
    fill!(g, 0.0)
    copyto!(W.inw[1], psi_init)
    for (j, s) in enumerate(sched)
        txx, tyy, tzz = theta[s.kxx], theta[s.kyy], theta[s.kzz]
        _apply_bond_to!(W.m1w[j], W.inw[j], s.idx, s.sa, s.sb, prim_unitary(:XX, txx))
        _apply_bond_to!(W.m2w[j], W.m1w[j], s.idx, s.sa, s.sb, prim_unitary(:YY, tyy))
        out = j == nb ? W.final : W.inw[j + 1]
        _apply_bond_to!(out, W.m2w[j], s.idx, s.sa, s.sb, prim_unitary(:ZZ, tzz))
    end
    mul!(W.lam, H, W.final)
    for j in nb:-1:1
        s = sched[j]
        txx, tyy, tzz = theta[s.kxx], theta[s.kyy], theta[s.kzz]
        flip = s.sa | s.sb
        # ket states are POST-gate (|u> = U_occ|w>); λ is pre-R† (gates-after only)
        postzz = j == nb ? W.final : W.inw[j + 1]
        g[s.kzz] += imag(_zz_dot(W.lam, postzz, s.pa, s.pb))
        apply_bond_vec!(W.lam, s.idx, s.sa, s.sb, prim_unitary(:ZZ, -tzz))
        g[s.kyy] += imag(_yy_dot(W.lam, W.m2w[j], s.pa, s.pb, flip))
        apply_bond_vec!(W.lam, s.idx, s.sa, s.sb, prim_unitary(:YY, -tyy))
        g[s.kxx] += imag(_xx_dot(W.lam, W.m1w[j], flip))
        apply_bond_vec!(W.lam, s.idx, s.sa, s.sb, prim_unitary(:XX, -txx))
    end
    return g
end

"""One leg: p=1 global sampling + top-K refine, then chained warm p=2,3."""
function run_leg(H::Matrix{ComplexF64}, psi_init::Vector{ComplexF64},
                 meta::AnsatzMeta, delta::Real, di::Integer, si::Integer, li::Integer)
    n1 = nparams(meta, delta, 1)
    buf = zeros(ComplexF64, length(psi_init))
    seed1 = _derive_seed(di, si, 1, li)
    rng = MersenneTwister(seed1)
    cands = [SAMPLE_RANGE .* rand(rng, n1) for _ in 1:N_GLOBAL]
    push!(cands, zeros(n1))  # zero vector = init state itself (spec constructive guarantee)
    Es = [energy_of(th, H, psi_init, meta, 1, delta, buf) for th in cands]
    order = sortperm(Es)
    refined = [_refine(cands[k], H, psi_init, meta, 1, delta, seed1) for k in order[1:TOP_K]]
    best1 = refined[argmin([r.energy for r in refined])]
    steps = LegStep[LegStep(best1.theta, best1.energy, best1.converged, false,
                            best1.iters, best1.dtail, seed1, N_GLOBAL + 1)]
    prev = best1.theta
    prevE = best1.energy
    for p in (2, 3)
        npl = nparams(meta, delta, 1)
        θ0 = [prev; zeros(npl)]
        st = _refine(θ0, H, psi_init, meta, p, delta, seed1)
        # Ratchet gate (spec INV-002, p>1 only): exhausted but stagnant and no worse.
        stagn = (!st.converged) && st.iters >= MAX_ITERS &&
                st.dtail < STAG_TOL && st.energy <= prevE + STAG_E_TOL
        push!(steps, LegStep(st.theta, st.energy, st.converged, stagn,
                             st.iters, st.dtail, seed1, 1))
        prev = st.theta
        prevE = st.energy
    end
    return steps
end

"""Full point: three legs + per-p winner. H cached by caller; e0_exact computed here."""
function run_point(delta::Real, s::Real, H::Matrix{ComplexF64}, e0_exact::Real)
    steps = Dict{String,Vector{LegStep}}()
    for (li, leg) in enumerate(LEG_LABELS)
        meta = build_meta(8, leg)
        psi_init_state = psi_init(leg, meta.L)
        di = round(Int, 100 * Float64(delta))
        si = round(Int, 100 * Float64(s))
        steps[leg] = run_leg(H, psi_init_state, meta, Float64(delta), di, si, li)
    end
    best = Dict{Int,Tuple{String,Vector{Float64},Float64}}()
    for p in (1, 2, 3)
        cand = [(leg, steps[leg][p].theta, steps[leg][p].energy) for leg in LEG_LABELS]
        i = argmin([c[3] for c in cand])
        best[p] = cand[i]
    end
    return PointResult(Float64(delta), Float64(s), steps, best, Float64(e0_exact))
end

# --- symmetry diagnostics (validation) --------------------------------------

"""⟨Z_tot⟩ with |0>=Z+1: Z_tot(b) = L - 2*popcount(b)."""
function expect_ztot(psi::AbstractVector, L::Integer)
    acc = 0.0
    for b in 0:((1 << L) - 1)
        acc += abs2(psi[b + 1]) * (L - 2 * count_ones(UInt(b)))
    end
    return acc
end

"""Overlap ⟨ψ|Xbar|ψ⟩ (global spin flip; +1 sector check)."""
function overlap_xbar(psi::AbstractVector, L::Integer)
    full = (UInt(1) << L) - UInt(1)
    return sum(conj(psi[b + 1]) * psi[(b ⊻ full) + 1] for b in UInt(0):full)
end

"""Overlap ⟨ψ|R|ψ⟩ (chain reflection; +1 sector check)."""
function overlap_reflect(psi::AbstractVector, L::Integer)
    acc = ComplexF64(0)
    for b in UInt(0):((UInt(1) << L) - UInt(1))
        r = UInt(0)
        for i in 0:(L - 1)
            ((b >> i) & UInt(1)) == UInt(1) && (r |= UInt(1) << (L - 1 - i))
        end
        acc += conj(psi[Int(b) + 1]) * psi[Int(r) + 1]
    end
    return acc
end
