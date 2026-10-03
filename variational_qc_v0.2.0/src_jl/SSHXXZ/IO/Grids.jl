# Canonical frozen coordinate definitions (Binding Clarifications CL-001/1A).

module Grids

export S_GRID, D_GRID, REPS, q_grid

const S_GRID = collect(1:49) ./ 50.0
const D_GRID = 2.0 .* collect(1:49) ./ 50.0  # 2026-10-01: δ=2j/50 per current doc/

const REPS = Dict("trivial" => (0.02, 0.06),
                  "topological" => (0.98, 0.06),
                  "afm" => (0.50, 1.96))  # 2026-10-01: measured deep-AFM point

function q_grid(n_points=49)
    q = collect(range(0.0, 2π; length=n_points))
    @assert any(abs.(q .- π) .< 1e-12)  # explicit-pi binding constraint
    return q
end

end # module
