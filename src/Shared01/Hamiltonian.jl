# SSH XXZ Hamiltonian, OBC. Physics definition: docs/theory/H.md.
#
# H(s,δ) = (1-s) * Σ_odd h + s * Σ_even h,
# h_kl = e^{-δ} (XkXl + YkYl) + e^{+δ} ZkZl.
#
# Basis convention (recorded with data, see Store manifest):
# site m (1-indexed) <-> bit (m-1) of the basis index, LSB = site 1.
# |0> is the Z=+1 state. Achieved by kron(P_L, ..., P_1): site 1 varies fastest.

# Physics-definition identity for the manifest. MUST be bumped if and only if
# the Hamiltonian definition above changes.
const H_DEF_ID = "ssh-xxz-OBC-H-v1"

const _ID = ComplexF64[1 0; 0 1]

"""Odd bonds (2j-1, 2j) for an even-L open chain."""
odd_bonds(L::Integer) = [(2j - 1, 2j) for j in 1:(L ÷ 2)]

"""Even bonds (2j, 2j+1) for an even-L open chain (no wrap bond)."""
even_bonds(L::Integer) = [(2j, 2j + 1) for j in 1:(L ÷ 2 - 1)]

function _bond_term(L::Integer, a::Integer, b::Integer, delta::Real)
    b == a + 1 || throw(ArgumentError("bonds must join adjacent sites, got ($a, $b)"))
    jxx = exp(-delta)
    jz = exp(delta)
    # Two-site block h_ab in basis |n_b n_a> (site b slow, site a fast):
    # XX+YY = off-diagonal 2s on the {|01>,|10>} pair, ZZ = diag(1,-1,-1,1).
    # h is symmetric under a<->b, so the within-block order is immaterial.
    h4 = ComplexF64[jz 0 0 0; 0 -jz 2jxx 0; 0 2jxx -jz 0; 0 0 0 jz]
    # kron factors from site L (slowest) down to site 1 (fastest, LSB);
    # the adjacent pair (b, a) merges into the single 4x4 block.
    factors = Matrix{ComplexF64}[]
    m = L
    while m >= 1
        if m == b
            push!(factors, h4)
            m -= 2
        else
            push!(factors, _ID)
            m -= 1
        end
    end
    out = factors[1]
    for k in 2:length(factors)
        out = kron(out, factors[k])
    end
    return out
end

"""
    build_hamiltonian(L, s, delta) -> Matrix{ComplexF64}

Dense SSH XXZ Hamiltonian for even `L` with open boundaries.
Site numbering and bond sets follow `docs/theory/H.md`.
"""
function build_hamiltonian(L::Integer, s::Real, delta::Real)
    isodd(L) && throw(ArgumentError("L must be even, got $L"))
    dim = 1 << L
    Ho = zeros(ComplexF64, dim, dim)
    for (a, b) in odd_bonds(L)
        Ho += _bond_term(L, a, b, delta)
    end
    He = zeros(ComplexF64, dim, dim)
    for (a, b) in even_bonds(L)
        He += _bond_term(L, a, b, delta)
    end
    return (1 - s) * Ho + s * He
end
