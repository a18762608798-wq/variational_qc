# T031: Q reconstruction-only contract (q-reconstruction rules 1-5).
using .SSHXXZ, Test

@testset "q-reconstruction" begin
    a = q_diagnostic(3.0, 0.25)
    @test a == q_diagnostic(3.0, 0.25)  # same-path bitwise identity
    # Q is a pure function of (S(pi), Ostr): two-arg method only.
    @test length(methods(q_diagnostic)) == 1
    @test first(methods(q_diagnostic)).nargs == 3  # (f, s_pi, ostr)
    # q-grid contract: 49 points, pi explicit.
    q = q_grid()
    @test length(q) == 49
    @test any(abs.(q .- π) .< 1e-12)
end
