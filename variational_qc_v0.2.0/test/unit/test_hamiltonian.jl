# T005: Hamiltonian bond placement + OBC + exponential anisotropy (IV.2).
using .SSHXXZ, Test, LinearAlgebra

@testset "hamiltonian" begin
    H = build_hamiltonian(6, 0.37, 1.7)
    @test H ≈ H'  # Hermitian
    # s=0, δ=0: L/2 decoupled Heisenberg odd bonds, singlet -3 each → E0=-3L/2.
    Hd = build_hamiltonian(4, 0.0, 0.0; sparse=false)
    @test minimum(eigvals(Hd)) ≈ -6.0 atol = 1e-10
    # s=1, δ=0 OBC: L/2-1 even bonds (no wrap), E0=-3.
    Hd1 = build_hamiltonian(4, 1.0, 0.0; sparse=false)
    @test minimum(eigvals(Hd1)) ≈ -3.0 atol = 1e-10
    # sparse vs dense agree.
    @test Matrix(build_hamiltonian(6, 0.42, 2.1)) ≈
          build_hamiltonian(6, 0.42, 2.1; sparse=false)
    # optimized direct assembly vs kron reference (IV.7 regression).
    @test Matrix(build_hamiltonian(6, 0.42, 2.1)) ≈
          Matrix(kron_reference(6, 0.42, 2.1))
end
