# ZZ correlators and structure factor for exp02 (spec PRE-004, docs/theory/topological_op.md).
# Basis convention: site m (1-indexed) <-> bit (m-1), LSB = site 1 (asserted
# against the S01 manifest by the runner). Pure kernel: no I/O.

"""8×8 real symmetric C_ij = <Z_i Z_j>; diagonal is 1 by construction."""
function zz_correlators(psi::AbstractVector, L::Integer = 8)
    n = length(psi)
    1 << L == n || throw(ArgumentError("length $(n) is not 2^L"))
    p = abs2.(Vector{ComplexF64}(psi))
    # zvals[b, m]: Z eigenvalue of site m in basis state b (1-indexed).
    C = Matrix{Float64}(I(L))
    for a in 1:L, b in (a + 1):L
        c = 0.0
        for s in 0:(n - 1)
            za = ((s >> (a - 1)) & 1) == 0 ? 1.0 : -1.0
            zb = ((s >> (b - 1)) & 1) == 0 ? 1.0 : -1.0
            c += p[s + 1] * za * zb
        end
        C[a, b] = c
        C[b, a] = c
    end
    return C
end

"""S(q) = (1/L) Σ_ij e^{iq(i-j)} C_ij (real up to roundoff)."""
function structure_factor(C::AbstractMatrix, q::Real)
    L = size(C, 1)
    acc = 0.0im
    for i in 1:L, j in 1:L
        acc += cis(q * (i - j)) * C[i, j]
    end
    return real(acc) / L
end

