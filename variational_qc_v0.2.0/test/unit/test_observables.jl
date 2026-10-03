# T008: observable conventions + ZtR analytic anchors (IV.2, XII.3).
using .SSHXXZ, Test

@testset "observables" begin
    psi = afm_state(8)
    @test s_pi(psi, 8) ≈ 8.0
    q = 2π * collect(0:7) ./ 8
    sq = structure_factor(psi, 8, q)
    @test argmax(sq) == 5  # q=π peak (1-indexed)
    @test q_diagnostic(8.0, 0.5) ≈ 4 / 3 + 2 * 0.5 - 8 / 6
    # XII.3 analytic anchors (exact).
    @test z_tilde_R(trivial_state(8), 8) == 1.0
    @test z_tilde_R(topo_state(8), 8) == -1.0
    @test z_tilde_R(afm_state(8), 8) == 0.0
end
