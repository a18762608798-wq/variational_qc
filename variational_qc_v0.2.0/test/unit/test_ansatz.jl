# T007: ansatz parameter count/order/halving + nesting (IV.2).
using .SSHXXZ, Test
using Yao: apply, zero_state

@testset "ansatz" begin
    @test n_params(8, 3, 2.0) == 24
    @test n_params(8, 3, 0.0) == 12  # δ=0 halved
    @test first_sublayer("trivial") == "e"
    @test first_sublayer("topological") == "o"
    @test first_sublayer("afm") == "e"
    # fixed alternating layer order F1,S1,F2,S2,...
    @test sublayer_seq(8, 2, "trivial") == ["e", "o", "e", "o"]
    # nesting: embedded p-1 state reproduces the p-1 statevector.
    th = collect(range(0.1, 0.5; length=n_params(8, 2, 2.0)))
    emb = embed_params(th, 8, 3, 2.0, "trivial")
    s2 = apply(zero_state(8), full_circuit(8, 2, 2.0, "trivial", th)).state
    s3 = apply(zero_state(8), full_circuit(8, 3, 2.0, "trivial", emb)).state
    @test s2 ≈ s3
end
