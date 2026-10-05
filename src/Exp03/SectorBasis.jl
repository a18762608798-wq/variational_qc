# P=-2 sector orbit basis for exp03 (spec §3; doc/theory/H.md, doc/theory/gap.md).
#
# P = Z_tot^2 - Xbar - R = -2  <=>  Z_tot = 0, Xbar = +1, R = +1, where
# Xbar = prod_m X_m (global spin flip) and R is chain reflection (m <-> L+1-m).
# Basis states are all-+ symmetrized orbits of Z_tot=0 bitstrings under
# {I, Xbar, R, Xbar*R}. Pure kernel, no I/O.
#
# Basis convention identical to Shared01.Hamiltonian (recorded with data):
# site m (1-indexed) <-> bit (m-1), LSB = site 1, |0> = Z+1.
# Hence Z_tot = (#0 - #1) = L - 2*popcount, and Z_tot = 0 <=> popcount = L/2.

module SectorBasis

using LinearAlgebra
using SparseArrays
using Shared01: odd_bonds, even_bonds, H_DEF_ID  # read-only; load Shared01 first

export SectorBasisData, sector_basis, sector_hamiltonian,
       flip_all, reflect_bits, canonical_key,
       EXPECTED_BASIS_CONVENTION, H_DEF_ID, MAX_L

const EXPECTED_BASIS_CONVENTION = "site m <-> bit (m-1), LSB = site 1, |0> = Z+1"

# Orbit enumeration is O(2^L); spec needs L ≤ 24, cap above with margin.
# Pure resource guard, not experiment semantics.
const MAX_L = 26

"""Global spin flip Xbar: flip all L bits."""
flip_all(b::UInt64, L::Integer) = b ⊻ ((UInt64(1) << L) - UInt64(1))

"""Chain reflection R (site m <-> L+1-m): reverse the L-bit order."""
function reflect_bits(b::UInt64, L::Integer)
    r = UInt64(0)
    for i in 0:(L - 1)
        ((b >> i) & UInt64(1)) == UInt64(1) && (r |= UInt64(1) << (L - 1 - i))
    end
    return r
end

"""Canonical orbit key: min over {b, Xb, Rb, XRb}."""
function canonical_key(b::UInt64, L::Integer)
    f = flip_all(b, L)
    r = reflect_bits(b, L)
    return min(b, f, r, flip_all(r, L))
end

struct SectorBasisData
    L::Int
    members::Vector{Vector{UInt64}}  # orbit member strings per basis state
    index::Dict{UInt64,Int}          # member string -> basis-state index
end

"""All-+ symmetrized Z_tot=0 orbits: the exact P=-2 sector basis."""
function sector_basis(L::Integer)
    iseven(L) || throw(ArgumentError("L must be even, got $L"))
    (2 ≤ L ≤ MAX_L) || throw(ArgumentError("L out of supported range 2..$MAX_L, got $L"))
    Ll = Int(L)
    half = Ll ÷ 2
    buckets = Dict{UInt64,Vector{UInt64}}()
    full = (UInt64(1) << Ll) - UInt64(1)
    for b in UInt64(0):full
        count_ones(b) == half || continue  # Z_tot = 0 (with |0> = Z+1)
        c = canonical_key(b, Ll)
        push!(get!(buckets, c, UInt64[]), b)
    end
    members = [buckets[c] for c in sort(collect(keys(buckets)))]
    index = Dict{UInt64,Int}()
    for (a, mem) in enumerate(members)
        for b in mem
            index[b] = a
        end
    end
    return SectorBasisData(Ll, members, index)
end

"""Sector Hamiltonian matrix: bond terms act directly on member bitstrings.

h_kl = e^{-δ}(XkXl + YkYl) + e^{+δ}ZkZl with bond weights (1-s)/s,
same bond sets, weights and basis convention as Shared01.Hamiltonian.
"""
function sector_hamiltonian(L::Integer, s::Real, delta::Real)
    basis = sector_basis(L)
    n = length(basis.members)
    Is = Int[]
    Js = Int[]
    Vs = ComplexF64[]
    jxx = exp(-Float64(delta))
    jz = exp(Float64(delta))
    w_odd = 1.0 - Float64(s)
    w_even = Float64(s)
    bonds = Tuple{Int,Int,Float64}[]
    for (a, b) in odd_bonds(L)
        push!(bonds, (a, b, w_odd))
    end
    for (a, b) in even_bonds(L)
        push!(bonds, (a, b, w_even))
    end
    for a in 1:n
        mem = basis.members[a]
        wa = 1.0 / sqrt(length(mem))
        for b in mem
            d = 0.0
            for (p, q, w) in bonds
                bp = (b >> (p - 1)) & UInt64(1)
                bq = (b >> (q - 1)) & UInt64(1)
                if bp == bq
                    d += w * jz
                else
                    d -= w * jz
                    c = b ⊻ ((UInt64(1) << (p - 1)) | (UInt64(1) << (q - 1)))
                    idx = basis.index[c]
                    nc = length(basis.members[idx])
                    push!(Is, idx)
                    push!(Js, a)
                    push!(Vs, (w * 2 * jxx * wa) / sqrt(nc))
                end
            end
            push!(Is, a)
            push!(Js, a)
            push!(Vs, d * wa * wa)
        end
    end
    return Hermitian(sparse(Is, Js, Vs, n, n))  # duplicate triplets sum: one entry per ⟨c|H|b⟩ term
end

end # module
