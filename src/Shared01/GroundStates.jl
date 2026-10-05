# S01/S02 ground-state grid and dense-ED solve kernel.
# Grids owned by shared-01 spec PRE-002; this file only executes them.

const L_SYS = 8

# s = i/100, δ = j/50, i,j = 1..99 (101-point uniform partition minus boundaries).
const S_GRID = collect(1:99) ./ 100.0
const DELTA_GRID = collect(1:99) ./ 50.0

# Representative points (subset of the S01 grid): label => (s, δ).
const REP_POINTS = Dict(
    "trivial" => (0.01, 0.02),
    "topological" => (0.99, 0.02),
    "afm" => (0.50, 1.98),
)
const REP_LABELS = ("trivial", "topological", "afm")

# Energies are O(10); 1e-8 leaves ample margin above dense-solver roundoff.
# Pure implementation-layer choice; does not change experiment semantics.
const DEGENERACY_TOL = 1e-8

struct PointSolution
    s::Float64
    delta::Float64
    E0::Float64
    E1::Float64
    psi0::Vector{ComplexF64}
    degenerate::Bool
end

"""
    solve_point(s, delta) -> PointSolution

Full-space dense diagonalization of H(s, δ); lowest eigenpair is the ground
state. `degenerate` flags E1 - E0 < DEGENERACY_TOL per the spec invalid-run rule.
"""
function solve_point(s::Real, delta::Real)
    H = build_hamiltonian(L_SYS, s, delta)
    F = eigen(Hermitian(H))
    E0, E1 = F.values[1], F.values[2]
    psi0 = Vector{ComplexF64}(F.vectors[:, 1])
    return PointSolution(Float64(s), Float64(delta), E0, E1, psi0,
                         (E1 - E0) < DEGENERACY_TOL)
end

"""
    solve_grid() -> Matrix{PointSolution}

Solve all 99×99 points. Threaded over rows; output order is deterministic
(independent of thread count).
"""
function solve_grid()
    ns, nd = length(S_GRID), length(DELTA_GRID)
    out = Matrix{PointSolution}(undef, ns, nd)
    Threads.@threads for j in 1:nd
        delta = DELTA_GRID[j]
        for i in 1:ns
            out[i, j] = solve_point(S_GRID[i], delta)
        end
    end
    return out
end
