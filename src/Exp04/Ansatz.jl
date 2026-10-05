# Orbit ansatz circuit for exp04 (doc/theory/ansatz.md), fixed statevector action.
#
# Odd bonds O_j=(2j-1,2j) pair as O_j <-> O_{M+1-j}; even bonds E_j=(2j,2j+1)
# pair as E_j <-> E_{M-j} (at most one self-mirror bond). Per orbit one (tx,tz)
# pair (δ=0: single t, structural halving). Sublayer order pairs with the init
# state: triv/afm legs apply even first (F=e), topo leg odd first (F=o).
# Each bond realizes RXX(tx)RYY(tx)RZZ(tz) fused into one 4x4.
# Basis convention identical to Shared01.Hamiltonian (LSB = site 1).
# Pure kernel, no I/O.

struct AnsatzMeta
    L::Int
    leg::String
    odd_orbits::Vector{Vector{Tuple{Int,Int}}}   # bonds per odd orbit (deterministic order)
    even_orbits::Vector{Vector{Tuple{Int,Int}}}  # bonds per even orbit
    order::Vector{Symbol}                        # sublayer application order, first acts first
    bond_bases::Dict{Tuple{Int,Int},Vector{Int}} # (a,b) -> 64 base indices (bit pair zero)
end

"""Mirror partner of odd bond O_j: O_{M+1-j} = (L-2j+1, L-2j+2)."""
_odd_mirror(L, j) = (L - 2j + 1, L - 2j + 2)

"""Mirror partner of even bond E_j: E_{M-j} = (L-2j, L-2j+1)."""
_even_mirror(L, j) = (L - 2j, L - 2j + 1)

function _orbits(bonds::Vector{Tuple{Int,Int}}, partners::Vector{Tuple{Int,Int}})
    seen = Set{Tuple{Int,Int}}()
    orbits = Vector{Tuple{Int,Int}}[]
    for (bond, partner) in zip(bonds, partners)
        bond in seen && continue
        if partner == bond || partner in seen
            push!(orbits, [bond])
        else
            push!(orbits, [bond, partner])
        end
        push!(seen, bond)
        push!(seen, partner)
    end
    return orbits
end

"""Build orbit metadata for even L and a leg label (F/S order bound to the leg)."""
function build_meta(L::Integer, leg::AbstractString)
    iseven(L) || throw(ArgumentError("L must be even, got $L"))
    leg in ("triv", "topo", "afm") || throw(ArgumentError("unknown leg: $leg"))
    M = L ÷ 2
    odd_bonds = [(2j - 1, 2j) for j in 1:M]
    even_bonds = [(2j, 2j + 1) for j in 1:(M - 1)]
    oo = _orbits(odd_bonds, [_odd_mirror(L, j) for j in 1:M])
    eo = _orbits(even_bonds, [_even_mirror(L, j) for j in 1:(M - 1)])
    length(oo) + length(eo) == M || throw(ErrorException("orbit count != M"))
    order = leg == "topo" ? [:odd, :even] : [:even, :odd]
    bases = Dict{Tuple{Int,Int},Vector{Int}}()
    for orb in oo, bond in orb
        bases[bond] = bond_bases(Int(L), bond[1], bond[2])
    end
    for orb in eo, bond in orb
        bases[bond] = bond_bases(Int(L), bond[1], bond[2])
    end
    return AnsatzMeta(Int(L), String(leg), oo, eo, order, bases)
end

"""64 base indices (1-based) with the (a,b) bit pair zero, for branch-free apply."""
function bond_bases(L::Integer, a::Integer, b::Integer)
    sa, sb = UInt64(1) << (a - 1), UInt64(1) << (b - 1)
    out = Int[]
    for x in UInt64(0):((UInt64(1) << L) - UInt64(1))
        ((x & sa) | (x & sb)) == UInt64(0) && push!(out, Int(x) + 1)
    end
    return out
end

"""Params per layer: L (δ≠0) or L/2 (δ=0, structural halving)."""
nparams(meta::AnsatzMeta, delta::Real, p::Integer) =
    (abs(Float64(delta)) < 1e-15 ? (meta.L ÷ 2) : meta.L) * Int(p)

"""1-based tx index of orbit oi within a layer block (tz follows, unless halved)."""
function _orbit_base(meta::AnsatzMeta, halved::Bool, isodd::Bool, oi::Integer)
    no = length(meta.odd_orbits)
    if isodd
        return halved ? oi : 2oi - 1
    else
        off = halved ? no : 2no
        return off + (halved ? oi : 2oi - 1)
    end
end

"""Occurrence layout for p layers: occurrence idx -> θ index (shared params repeat).

Iteration order (layer-major, sublayers in meta.order, orbits/bonds stored order,
XX/YY/ZZ per bond) is the consumption order of apply_occ!; θ indices are
positional within each layer block (odd orbits then even orbits); paired bonds
of one orbit share the same θ indices (one occurrence entry per bond).
"""
function occ_layout(meta::AnsatzMeta, delta::Real, p::Integer)
    halved = abs(Float64(delta)) < 1e-15
    npl = halved ? meta.L ÷ 2 : meta.L
    occ = Int[]
    for l in 1:Int(p)
        base = (l - 1) * npl
        for sub in meta.order
            orbs = sub == :odd ? meta.odd_orbits : meta.even_orbits
            for (oi, orb) in enumerate(orbs)
                b = base + _orbit_base(meta, halved, sub == :odd, oi)
                for _ in orb  # one XX/YY/ZZ triple per bond; orbit mates share θ
                    append!(occ, halved ? (b, b, b) : (b, b, b + 1))
                end
            end
        end
    end
    return occ
end

# --- two-qubit bond unitary -------------------------------------------------

"""RXX(x)RYY(y)RZZ(z) fused 4x4 in |n_b n_a> basis (b slow, a fast)."""
function _bond_unitary(x::Real, y::Real, z::Real)
    cx, sx = cos(x / 2), sin(x / 2)
    cy, sy = cos(y / 2), sin(y / 2)
    RXX = ComplexF64[cx 0 0 -im*sx; 0 cx -im*sx 0; 0 -im*sx cx 0; -im*sx 0 0 cx]
    RYY = ComplexF64[cy 0 0 im*sy; 0 cy -im*sy 0; 0 -im*sy cy 0; im*sy 0 0 cy]
    e1, e2 = exp(-im * z / 2), exp(im * z / 2)
    RZZ = ComplexF64[e1 0 0 0; 0 e2 0 0; 0 0 e2 0; 0 0 0 e1]
    return RZZ * RYY * RXX
end

"""Primitive rotation unitary: sym in (:XX, :YY, :ZZ)."""
function prim_unitary(sym::Symbol, t::Real)
    c, s = cos(t / 2), sin(t / 2)
    if sym == :XX
        return ComplexF64[c 0 0 -im*s; 0 c -im*s 0; 0 -im*s c 0; -im*s 0 0 c]
    elseif sym == :YY
        return ComplexF64[c 0 0 im*s; 0 c -im*s 0; 0 -im*s c 0; im*s 0 0 c]
    else
        e1, e2 = exp(-im * t / 2), exp(im * t / 2)
        return ComplexF64[e1 0 0 0; 0 e2 0 0; 0 0 e2 0; 0 0 0 e1]
    end
end

"""Apply one bond unitary over precomputed base indices (branch-free, SIMD)."""
function apply_bond_vec!(psi::Vector{ComplexF64}, idx::Vector{Int},
                         sa::Integer, sb::Integer, U::Matrix{ComplexF64})
    u11, u12, u13, u14 = U[1, 1], U[1, 2], U[1, 3], U[1, 4]
    u21, u22, u23, u24 = U[2, 1], U[2, 2], U[2, 3], U[2, 4]
    u31, u32, u33, u34 = U[3, 1], U[3, 2], U[3, 3], U[3, 4]
    u41, u42, u43, u44 = U[4, 1], U[4, 2], U[4, 3], U[4, 4]
    @inbounds @simd for t in eachindex(idx)
        i00 = idx[t]
        i10 = i00 + sa
        i01 = i00 + sb
        i11 = i01 + sa
        v00 = psi[i00]
        v10 = psi[i10]
        v01 = psi[i01]
        v11 = psi[i11]
        psi[i00] = u11 * v00 + u12 * v10 + u13 * v01 + u14 * v11
        psi[i10] = u21 * v00 + u22 * v10 + u23 * v01 + u24 * v11
        psi[i01] = u31 * v00 + u32 * v10 + u33 * v01 + u34 * v11
        psi[i11] = u41 * v00 + u42 * v10 + u43 * v01 + u44 * v11
    end
    return psi
end

"""Apply the full p-layer circuit to psi_init (result in psi)."""
function apply_circuit!(psi::Vector{ComplexF64}, psi_init::Vector{ComplexF64},
                        theta::AbstractVector, meta::AnsatzMeta, p::Integer, delta::Real)
    length(theta) == nparams(meta, delta, p) ||
        throw(ArgumentError("θ length mismatch: $(length(theta)) vs $(nparams(meta, delta, p))"))
    copyto!(psi, psi_init)
    halved = abs(Float64(delta)) < 1e-15
    npl = halved ? meta.L ÷ 2 : meta.L
    for l in 1:Int(p)
        blk = @view theta[(l - 1) * npl + 1:l * npl]
        for sub in meta.order
            orbs = sub == :odd ? meta.odd_orbits : meta.even_orbits
            for (oi, orb) in enumerate(orbs)
                b = _orbit_base(meta, halved, sub == :odd, oi)
                tx = Float64(blk[b])
                tz = halved ? tx : Float64(blk[b + 1])
                U = _bond_unitary(tx, tx, tz)
                for (a, c) in orb
                    apply_bond_vec!(psi, meta.bond_bases[(a, c)],
                                    1 << (a - 1), 1 << (c - 1), U)
                end
            end
        end
    end
    return psi
end

"""Apply with per-occurrence angles (parameter-shift engine).

occ_angles[j] is the angle of occurrence j in occ_layout order
(XX/YY/ZZ of each bond); shifted evaluations perturb one entry.
"""
function apply_occ!(psi::Vector{ComplexF64}, psi_init::Vector{ComplexF64},
                    occ_angles::AbstractVector, meta::AnsatzMeta, p::Integer, delta::Real)
    occ = occ_layout(meta, delta, p)
    length(occ_angles) == length(occ) || throw(ArgumentError("occurrence length mismatch"))
    copyto!(psi, psi_init)
    pos = 1
    for l in 1:Int(p)
        for sub in meta.order
            orbs = sub == :odd ? meta.odd_orbits : meta.even_orbits
            for orb in orbs
                for (a, c) in orb
                    txx = Float64(occ_angles[pos])
                    tyy = Float64(occ_angles[pos + 1])
                    tzz = Float64(occ_angles[pos + 2])
                    pos += 3
                    U = _bond_unitary(txx, tyy, tzz)
                    apply_bond_vec!(psi, meta.bond_bases[(a, c)],
                                    1 << (a - 1), 1 << (c - 1), U)
                end
            end
        end
    end
    return psi
end
