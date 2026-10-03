# T055: canonical shared-basis store (contracts/shared-basis.md).
using .SSHXXZ, Test, LinearAlgebra

@testset "basis-cache" begin
    dir = mktempdir()
    # miss then hit; compute called exactly once.
    calls = Ref(0)
    function compute()
        calls[] += 1
        H = build_hamiltonian(4, 0.5, 0.0)
        e0, psi = ground_state(H)
        return (psi, e0)
    end
    r1 = get_or_compute_basis(dir, 4, 0.5, 0.0, compute;
                              code_version="test", h_def=H_DEF)
    r2 = get_or_compute_basis(dir, 4, 0.5, 0.0,
                              () -> error("must not recompute");
                              code_version="test", h_def=H_DEF)
    @test calls[] == 1
    @test r1[2] ≈ r2[2]
    @test r1[1] ≈ r2[1]
    # key includes code_version: different version misses (no aliasing).
    hit = load_basis(dir, 4, 0.5, 0.0; code_version="other", h_def=H_DEF)
    @test hit === nothing
    # key includes H definition: H_DEF exposed and stable.
    @test H_DEF isa String && !isempty(H_DEF)
end
