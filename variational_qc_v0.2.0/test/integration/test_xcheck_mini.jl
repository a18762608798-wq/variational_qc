# T043: mini cross-check vs archived baseline (xcheck contract, D-002).
# Anchors are exact by construction; analytic H limits cross-check the port.
using .SSHXXZ, Test, LinearAlgebra

@testset "xcheck-mini" begin
    # analytic anchors through the Julia stack.
    @test z_tilde_R(trivial_state(8), 8) == 1.0
    @test z_tilde_R(topo_state(8), 8) == -1.0
    @test z_tilde_R(afm_state(8), 8) == 0.0
    # new-H analytic limits (E<1e-8 scale check on dense reference).
    @test abs(minimum(eigvals(Matrix(build_hamiltonian(4, 0.0, 0.0)))) + 6.0) < 1e-8
    @test abs(minimum(eigvals(Matrix(build_hamiltonian(4, 1.0, 0.0)))) + 3.0) < 1e-8
end
