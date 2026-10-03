# Reference initial states. Authoritative: doc/plan/theory/psi0.md.
#
# All three live in the P=-2 sector for L=4k. Site m (1-indexed) <-> bit (m-1).

module InitialStates

export trivial_state, topo_state, afm_state

_bit(i, m) = (i >> (m - 1)) & 1  # i 0-based full index, m 1-indexed site

function _product_singlets(L, pairs)
    psi = zeros(ComplexF64, 2^L)
    for i in 0:(2^L - 1)
        amp = 1.0 + 0.0im
        ok = true
        for (a, b) in pairs
            ba, bb = _bit(i, a), _bit(i, b)
            ba == bb && (ok = false; break)
            amp *= (ba == 0 ? 1 : -1) / sqrt(2.0)  # |01>-|10>: + for (0,1)
        end
        ok && (psi[i + 1] = amp)
    end
    return psi
end

trivial_state(L) = _product_singlets(L, [(2j - 1, 2j) for j in 1:(L ÷ 2)])

function topo_state(L)
    pairs = vcat([(1, L)], [(2j, 2j + 1) for j in 1:(L ÷ 2 - 1)])
    return _product_singlets(L, pairs)
end

function afm_state(L)
    psi = zeros(ComplexF64, 2^L)
    ia = sum((m % 2) << (m - 1) for m in 1:L)          # |0101..> (site1=0)
    ib = sum(((m + 1) % 2) << (m - 1) for m in 1:L)    # |1010..>
    psi[ia + 1] = 1 / sqrt(2.0)
    psi[ib + 1] = 1 / sqrt(2.0)
    return psi
end

end # module
