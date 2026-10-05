# Parent module for the exp03 task-local implementation.
# Load order: Shared01 (read-only semantic reuse), then Exp03.

module Exp03

using LinearAlgebra
using SparseArrays
using Arpack
using NPZ, JSON3, Dates
using Shared01: odd_bonds, even_bonds, H_DEF_ID  # read-only; load Shared01 first

export SectorBasisData, sector_basis, sector_hamiltonian,
       flip_all, reflect_bits, canonical_key,
       EXPECTED_BASIS_CONVENTION, H_DEF_ID, MAX_L,
       GapResult, solve_gap, union_points, key_wide, key_narrow, S_WIDE, S_NARROW,
       ARPACK_TOL, RESID_TOL, ARPACK_MAXITER, ARPACK_NCV,
       crossings, linear_fit,
       save_chunk, completed_chunks, assemble_D02, chunk_id,
       save_extra, EXTRA_ID, EXTRA_LS,
       SCHEMA, LS, BLOCK, D02_NPZ_NAME, MANIFEST_NAME,
       GAP_MIN_TOL, FIT_TOL

include("Exp03/SectorBasis.jl")
include("Exp03/GapSolver.jl")
include("Exp03/CrossFit.jl")
include("Exp03/Store.jl")

end # module
