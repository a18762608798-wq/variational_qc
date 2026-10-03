# T010: byte-exact seed derivation (vectors from the archived Python baseline).
using .SSHXXZ, Test

@testset "seeds" begin
    @test derive_seed(0.5, 1.0, "trivial", 0) == 0xae15d0fd  # 2920665341
    @test derive_seed(0.5, 1.0, "topological", 2) == 69715836
    @test derive_seed(0.98, 0.06, "afm", 1) == 4265875871
    @test derive_seed(0.5, 1.0, "trivial", 0) == derive_seed(0.5, 1.0, "trivial", 0)
    s = Set(derive_seed(0.5, 1.0, b, r) for b in ("trivial", "topological", "afm") for r in 0:2)
    @test length(s) == 9
end
