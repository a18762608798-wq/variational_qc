# Physical SSH-XXZ Hamiltonian, OBC. Authoritative: doc/plan/theory/H.md.
#
# H(s,δ) = H_o + H_e with h_kl = e^{-δ}(XX+YY) + e^{+δ}(ZZ).
# δ=0 is the Heisenberg isotropic point; δ>0 leans Ising.
# Site m (1-indexed) <-> bit (m-1) of the basis index (LSB = site 1).

module Hamiltonian

using SparseArrays, LinearAlgebra

export build_hamiltonian, odd_bonds, even_bonds, kron_reference, H_DEF

# Physics-definition identity for cache keys (contracts/shared-basis.md rule 3).
# MUST be bumped if and only if the Hamiltonian definition changes.
const H_DEF = "ssh-xxz-exp-OBC-v2"

const _SX = sparse(ComplexF64[0 1; 1 0])
const _SY = sparse(ComplexF64[0 -im; im 0])
const _SZ = sparse(ComplexF64[1 0; 0 -1])
const _ID = sparse(ComplexF64[1 0; 0 1])

function _site_op(L, m, P)
    ops = [_ID for _ in 1:L]
    ops[m] = P
    out = ops[1]
    for k in 2:L
        out = kron(ops[k], out)  # kron(A,B): B fastest -> site 1 fastest
    end
    return out
end

odd_bonds(L) = [(2j - 1, 2j) for j in 1:(L ÷ 2)]
even_bonds(L) = [(2j, 2j + 1) for j in 1:(L ÷ 2 - 1)]  # OBC: no wrap bond

function _bond_term(L, a, b, delta)
    jxx, jz = exp(-delta), exp(delta)
    xa, xb = _site_op(L, a, _SX), _site_op(L, b, _SX)
    ya, yb = _site_op(L, a, _SY), _site_op(L, b, _SY)
    za, zb = _site_op(L, a, _SZ), _site_op(L, b, _SZ)
    return jxx * (xa * xb + ya * yb) + jz * (za * zb)
end

function build_hamiltonian(L, s, delta; sparse=true)
    isodd(L) && throw(ArgumentError("L must be even, got $L"))
    H = _direct_builder(L, s, delta)
    return sparse ? H : Matrix(H)
end

function _kron_builder(L, s, delta)
    # Reference implementation (IV.7): kept for regression testing only.
    H = spzeros(ComplexF64, 2^L, 2^L)
    for (a, b) in odd_bonds(L)
        H += (1.0 - s) * _bond_term(L, a, b, delta)
    end
    for (a, b) in even_bonds(L)
        H += s * _bond_term(L, a, b, delta)
    end
    return H
end

kron_reference(L, s, delta) = _kron_builder(L, s, delta)

_zval(bit) = bit == 0 ? 1.0 : -1.0  # matches _SZ = diag(1,-1)

function _direct_builder(L, s, delta)
    # O(N·bonds) COO assembly; identical matrix to _kron_builder.
    # (XX+YY) flips antiparallel bond pairs with amplitude 2; ZZ is diagonal.
    jxx, jz = exp(-delta), exp(delta)
    N = 2^L
    bonds = vcat([(a, b, 1.0 - s) for (a, b) in odd_bonds(L)],
                 [(a, b, s) for (a, b) in even_bonds(L)])
    I, J, V = Int[], Int[], ComplexF64[]
    for i in 0:(N - 1)
        d = 0.0
        for (a, b, c) in bonds
            ba, bb = (i >> (a - 1)) & 1, (i >> (b - 1)) & 1
            d += c * jz * _zval(ba) * _zval(bb)
            if ba != bb
                j = i ⊻ (1 << (a - 1)) ⊻ (1 << (b - 1))
                push!(I, i + 1)
                push!(J, j + 1)
                push!(V, 2.0 * c * jxx)
            end
        end
        push!(I, i + 1)
        push!(J, i + 1)
        push!(V, d)
    end
    return sparse(I, J, V, N, N)
end

end # module
