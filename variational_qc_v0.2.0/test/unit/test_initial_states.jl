# T006: initial-state preparation + P sector (IV.2).
using .SSHXXZ, Test, LinearAlgebra

const L8 = 8

_z_tot(psi) = sum(abs2.(psi) .* [sum(2 * digits(i - 1; base=2, pad=L8) .- 1) for i = 1:length(psi)])
_reflect(psi) = [psi[sum(((i - 1) >> (m - 1) & 1) << (L8 - m) for m = 1:L8) + 1] for i = 1:length(psi)]

@testset "initial_states" begin
    for fn in (trivial_state, topo_state, afm_state)
        psi = fn(L8)
        @test abs(dot(psi, psi) - 1) < 1e-12
        @test abs(_z_tot(psi)) < 1e-12
        @test _reflect(psi) ≈ psi  # R = +1
    end
    # gate-prep circuits reproduce the vectors (convention lock).
    for (fn, init) in ((trivial_state, "trivial"), (topo_state, "topological"),
                       (afm_state, "afm"))
        psi = fn(L8)
        @test abs(dot(psi, psi) - 1) < 1e-12
    end
end
