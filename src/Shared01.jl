# Parent module for the shared-01 task-local implementation.
# Kernels stay importable/testable without I/O or orchestration.

module Shared01

using LinearAlgebra
using NPZ, JSON3, Dates

export build_hamiltonian, odd_bonds, even_bonds, H_DEF_ID,
       L_SYS, S_GRID, DELTA_GRID, REP_POINTS, REP_LABELS,
       solve_point, solve_grid, DEGENERACY_TOL,
       save_shared01, load_shared01, point_at, NPZ_NAME, MANIFEST_NAME, SCHEMA

include("Shared01/Hamiltonian.jl")
include("Shared01/GroundStates.jl")
include("Shared01/Store.jl")

end # module
