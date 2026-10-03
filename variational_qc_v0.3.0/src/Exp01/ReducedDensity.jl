# Partial-trace kernel for exp01 (spec §3).
# Basis convention: site m (1-indexed) <-> bit (m-1), LSB = site 1,
# asserted at runtime against the S01 manifest (see ZTilde/runner).
# Pure kernel: no I/O, no globals.

module ReducedDensity

using LinearAlgebra

export reduced_density_matrix

"""
    reduced_density_matrix(psi, keep_sites) -> Matrix{ComplexF64}

Reduced density matrix of `psi` (length `2^L` state vector) on `keep_sites`
(sorted ascending internally; returned rows/cols follow that order).
Result is bit-exact Hermitian by construction (`m * m'`).
"""
function reduced_density_matrix(psi::AbstractVector, keep_sites::Vector{Int})
    n = length(psi)
    L = Int(round(log2(n)))
    1 << L == n || throw(ArgumentError("length $(n) is not 2^L"))
    keep = sort(keep_sites)
    all(1 .<= keep .<= L) || throw(ArgumentError("sites out of range: $keep_sites"))
    traced = setdiff(collect(1:L), keep)
    t = reshape(Vector{ComplexF64}(psi), fill(2, L)...)
    tp = isempty(traced) ? t : permutedims(t, [keep; traced])
    m = reshape(tp, 1 << length(keep), 1 << length(traced))
    return Hermitian(Matrix(m * m'))
end

end # module
