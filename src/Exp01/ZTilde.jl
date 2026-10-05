# Normalized topological reflector ~Z_R for exp01 (spec POST-001, doc/theory/topological_op.md).
# I = sites (3,4,5,6); I1 = (3,4); I2 = (5,6); R_I = mirror about the central bond.
# Pure kernel: no I/O. Keep-site ordering matches ReducedDensity (ascending).

const I_SITES = [3, 4, 5, 6]
const I1_SITES = [3, 4]
const I2_SITES = [5, 6]

# Must equal the S01 manifest entry verbatim; the runner refuses to run otherwise.
const EXPECTED_BASIS_CONVENTION =
    "site m (1-indexed) <-> bit (m-1) of basis index, LSB = site 1; |0> is Z=+1"

"""16×16 central-bond mirror on sites (3,4,5,6): (b3,b4,b5,b6) -> (b6,b5,b4,b3)."""
function mirror_operator()
    R = zeros(ComplexF64, 16, 16)
    for old in 0:15
        b = [(old >> k) & 1 for k in 0:3]  # b[1] = site 3 (fastest)
        new = b[1] << 3 | b[2] << 2 | b[3] << 1 | b[4]
        R[new + 1, old + 1] = 1.0
    end
    return R
end

struct ZTildeResult
    z_R::Float64
    z_tilde::Float64
    rho_trace::Float64
    rho_min_eig::Float64
    denom::Float64
end

"""
    z_tilde(psi) -> ZTildeResult

`Z_R = Re Tr(ρ_I R_I)` (imaginary part is roundoff; asserted tiny in tests),
`~Z_R = Z_R / sqrt((Tr ρ_I1² + Tr ρ_I2²)/2)`.
"""
function z_tilde(psi::AbstractVector)
    rho_I = Matrix(reduced_density_matrix(psi, I_SITES))
    rho_I1 = Matrix(reduced_density_matrix(psi, I1_SITES))
    rho_I2 = Matrix(reduced_density_matrix(psi, I2_SITES))
    R = mirror_operator()
    z_R_full = tr(rho_I * R)
    p1 = real(tr(rho_I1 * rho_I1))
    p2 = real(tr(rho_I2 * rho_I2))
    denom = sqrt((p1 + p2) / 2)
    return ZTildeResult(real(z_R_full), real(z_R_full) / denom,
                        real(tr(rho_I)), minimum(real(eigvals(Hermitian(rho_I)))), denom)
end

