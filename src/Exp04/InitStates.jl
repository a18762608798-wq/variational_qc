# Three VQE reference states for exp04 (doc/theory/psi0.md).
# All lie in the P=-2 sector. Basis convention identical to Shared01.Hamiltonian:
# site m (1-indexed) <-> bit (m-1), LSB = site 1, |0> = Z+1.
# Pure kernels, no I/O.

const LEG_LABELS = ["triv", "topo", "afm"]

"""Odd-bond singlet product (trivial s=0 reference). L even."""
function psi_triv(L::Integer)
    isodd(L) && throw(ArgumentError("L must be even, got $L"))
    psi = zeros(ComplexF64, 1 << L)
    for mask in 0:((1 << (L ÷ 2)) - 1)
        b = UInt64(0)
        sign = 1.0
        for j in 1:(L ÷ 2)
            a, c = 2j - 1, 2j  # sites; bits a-1 < c-1
            if ((mask >> (j - 1)) & 1) == 0
                b |= UInt64(1) << (c - 1)      # |01>: site a=0, site c=1
            else
                b |= UInt64(1) << (a - 1)      # |10>: sign flip
                sign = -sign
            end
        end
        psi[b + 1] = sign / sqrt(2.0^(L ÷ 2))
    end
    return psi
end

"""Bulk even-bond singlets + end singlet (1,L) (topological s=1 reference). L even."""
function psi_topo(L::Integer)
    isodd(L) && throw(ArgumentError("L must be even, got $L"))
    psi = zeros(ComplexF64, 1 << L)
    bonds = [(2j, 2j + 1) for j in 1:(L ÷ 2 - 1)]
    push!(bonds, (1, L))
    for mask in 0:((1 << length(bonds)) - 1)
        b = UInt64(0)
        sign = 1.0
        for (j, (a, c)) in enumerate(bonds)
            lo, hi = min(a, c), max(a, c)
            if ((mask >> (j - 1)) & 1) == 0
                b |= UInt64(1) << (hi - 1)
            else
                b |= UInt64(1) << (lo - 1)
                sign = -sign
            end
        end
        psi[b + 1] = sign / sqrt(2.0^length(bonds))
    end
    return psi
end

"""GHZ antiferromagnet (|0101..> + |1010..>)/√2, site-1-first ordering. L even."""
function psi_afm(L::Integer)
    isodd(L) && throw(ArgumentError("L must be even, got $L"))
    psi = zeros(ComplexF64, 1 << L)
    b1 = UInt64(0)
    for m in 1:L
        ((m - 1) % 2 == 1) && (b1 |= UInt64(1) << (m - 1))
    end
    b2 = ((UInt64(1) << L) - UInt64(1)) ⊻ b1
    psi[b1 + 1] = 1 / sqrt(2.0)
    psi[b2 + 1] = 1 / sqrt(2.0)
    return psi
end

"""Dispatch by leg label."""
function psi_init(leg::AbstractString, L::Integer)
    leg == "triv" && return psi_triv(L)
    leg == "topo" && return psi_topo(L)
    leg == "afm" && return psi_afm(L)
    throw(ArgumentError("unknown leg label: $leg"))
end
