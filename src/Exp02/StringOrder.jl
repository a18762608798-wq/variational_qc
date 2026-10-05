# String order parameter for exp02 (docs/theory/topological_op.md).
# L=8 -> d = L/2-1 = 3:
#   O_str = <(Z1+Z2)(Z3Z4)(Z5Z6)(Z7+Z8)>
# (the two minus signs in Π_{l=1}^{2}(−Z_{2l+1}Z_{2l+2}) cancel).
# Diagonal in the Z basis: expectation = Σ_basis |ψ|² × eigenvalue.
# Pure kernel: no I/O.

function string_order(psi::AbstractVector, L::Integer = 8)
    n = length(psi)
    1 << L == n || throw(ArgumentError("length $(n) is not 2^L"))
    L == 8 || throw(ArgumentError("d=3 form is L=8 specific, got L=$L"))
    p = abs2.(Vector{ComplexF64}(psi))
    acc = 0.0
    for s in 0:(n - 1)
        z = ntuple(m -> ((s >> (m - 1)) & 1) == 0 ? 1.0 : -1.0, L)
        v = (z[1] + z[2]) * (z[3] * z[4]) * (z[5] * z[6]) * (z[7] + z[8])
        acc += p[s + 1] * v
    end
    return acc
end

