# Per-point symmetric-gap solver for exp03 (spec INV-001, INV-003).
# Δ_sec(L,s) = E1^{(P=-2)} - E0^{(P=-2)} at delta = 0 (Heisenberg point).
# Dense exact diagonalization of the small sector matrix: no iterative solver,
# no convergence parameters. Pure kernel, no I/O.

const DELTA_FIXED = 0.0  # spec PRE-001: all three D02 parts at δ = 0

# spec PRE-002 grids (same convention as S01: 101-partition minus boundaries).
const S_WIDE = [i / 100 for i in 1:99]                    # (i) s ∈ [0,1]
const S_NARROW = [0.45 + 0.15k / 100 for k in 1:99]       # (ii) s ∈ [0.45,0.6]

# Exact integer keys (denominator 10000): overlap <=> equal keys, no float compare.
key_wide(i::Integer) = 100 * i            # i/100 = key/10000
key_narrow(k::Integer) = 4500 + 15 * k     # 0.45+0.15k/100 = key/10000

"""Union of (i)+(ii) s-grids as (key, s) sorted by key.

Shared points take the canonical single-division value key/10000.0, which is
bit-identical to i/100 for the overlapping (i) points (both correctly rounded).
(iii) s = 0.5 is key 5000, i.e. the (i) i = 50 point: reused, never recomputed.
"""
function union_points()
    ks = union(Set(key_wide(i) for i in 1:99), Set(key_narrow(k) for k in 1:99))
    return [(key=k, s=k / 10000.0) for k in sort(collect(ks))]
end

struct GapResult
    E0::Float64
    E1::Float64
    delta_gap::Float64
end

const ARPACK_TOL = 1e-12     # eigensolver precision (plan §3)
const RESID_TOL = 1e-10      # per-pair residual hard assertion (plan §4)
const ARPACK_MAXITER = 1000
const ARPACK_NCV = 64        # Krylov subspace size (capped by n)

# ARPACK (Fortran, internal SAVE state) is not thread-safe: concurrent eigs
# calls from multiple Julia threads corrupt each other (observed as XYAUPD
# info=3 / segfaults). All eigs calls are serialized through this lock;
# assembly and residual checks stay parallel. Single eigs ≈ 0.1s, so the
# serial section costs ~30s total for the whole production.
const _ARPACK_LOCK = ReentrantLock()

"""Lowest two P=-2 sector eigenpairs and their gap at (L, s).

Sparse ARPACK path (plan §6): nev=2 smallest-real on the sparse Hermitian
sector matrix. Each returned pair must satisfy ‖Hv−λv‖ < RESID_TOL with
nconv ≥ 2, else the point is an invalid run (fail fast, never silent).
"""
function solve_gap(L::Integer, s::Real, delta::Real=DELTA_FIXED)
    H = sector_hamiltonian(L, s, delta)
    ncv = min(size(H, 1), ARPACK_NCV)
    r = lock(_ARPACK_LOCK) do
        eigs(H; nev=2, ncv=ncv, which=:SR, tol=ARPACK_TOL, maxiter=ARPACK_MAXITER)
    end
    d, v, nconv = r[1], r[2], r[3]
    nconv ≥ 2 || throw(ErrorException("ARPACK unconverged (nconv=$nconv) at L=$L s=$s"))
    order = sortperm(real.(d[1:2]))
    E = [real(d[order[1]]), real(d[order[2]])]
    for i in 1:2
        res = norm(H * v[:, order[i]] - E[i] * v[:, order[i]])
        res < RESID_TOL || throw(ErrorException("eigenpair residual $res ≥ $RESID_TOL at L=$L s=$s"))
    end
    return GapResult(E[1], E[2], E[2] - E[1])
end

