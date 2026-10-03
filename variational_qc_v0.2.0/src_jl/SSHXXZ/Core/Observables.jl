# Observables. Authoritative: doc/plan/theory/topological_op.md.
#
# S(q) = (1/L) Σ_ij e^{iq(i-j)} <ZiZj>; O_str(d=L/2-1); Q derived only;
# Z̃R with middle-2n block (n=L/4), explicit in-block mirror permutation.
# Site m (1-indexed) <-> bit (m-1).

module Observables

using LinearAlgebra

export zz_corr, structure_factor, s_pi, string_order, q_diagnostic, z_tilde_R

function _bits(L)
    N = 2^L
    return [((i - 1) >> (m - 1)) & 1 == 1 ? 1.0 : -1.0
            for i in 1:N, m in 1:L]
end

function zz_corr(psi, L)
    probs = abs2.(psi)
    z = _bits(L)
    return transpose(z) * (probs .* z)
end

function structure_factor(psi, L, qs)
    C = zz_corr(psi, L)
    i = collect(1:L)
    return [real(sum(exp(im * q * (a - b)) * C[a, b] for a in i, b in i)) / L
            for q in qs]
end

s_pi(psi, L) = structure_factor(psi, L, [Float64(π)])[1]

function string_order(psi, L)
    d = L ÷ 2 - 1
    z = _bits(L)
    N = size(z, 1)
    val = z[:, 1] + z[:, 2]
    for l in 1:(d - 1)
        val = val .* (-z[:, 2l + 1] .* z[:, 2l + 2])
    end
    val = val .* (z[:, 2d + 1] .+ z[:, 2d + 2])
    return sum(abs2.(psi) .* val)
end

q_diagnostic(s_pi_val, ostr_val) = 4 / 3 + 2 * ostr_val - s_pi_val / 6

function z_tilde_R(psi, L)
    n = L ÷ 4
    block = collect((L ÷ 2 - n + 1):(L ÷ 2 + n))
    rest = [m for m in 1:L if m ∉ block]
    N = 2^L
    bits = [((i - 1) >> (m - 1)) & 1 for i in 1:N, m in 1:L]
    pw = 1 .<< collect(0:(length(block) - 1))
    RI = vec(sum(bits[:, block] .* pw', dims=2))
    P = psi * psi'
    dim = 2^length(block)
    rho = zeros(ComplexF64, dim, dim)
    for i in 1:N, j in 1:N
        all(bits[i, m] == bits[j, m] for m in rest) || continue
        rho[RI[i] + 1, RI[j] + 1] += P[i, j]
    end
    nb = length(block)
    rev = [parse(Int, reverse(bitstring(b - 1)[end-nb+1:end]); base=2) + 1
           for b in 1:dim]
    z_r = sum(rho[rev[b], b] for b in 1:dim)
    h = nb ÷ 2
    d = 2^h
    # r4[a,b,a',b'] (1-indexed): row = (a-1)+d*(b-1). Partial trace needs the
    # DIAGONAL sum over b (np.trace semantics); a plain sum over dims (2,4)
    # would sum all (b,b') pairs and is WRONG.
    r4 = reshape(rho, (d, d, d, d))
    rho1 = [sum(r4[a, b, ap, b] for b in 1:d) for a in 1:d, ap in 1:d]
    rho2 = [sum(r4[a, b, a, bp] for a in 1:d) for b in 1:d, bp in 1:d]
    p1 = real(tr(rho1 * rho1))
    p2 = real(tr(rho2 * rho2))
    return real(z_r / sqrt((p1 + p2) / 2))
end

end # module
