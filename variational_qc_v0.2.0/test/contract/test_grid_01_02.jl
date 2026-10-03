# T025: 01/02 grid identity contract (grid-01-02 rules 1-5).
using .SSHXXZ, Test

@testset "grid-01-02" begin
    @test length(S_GRID) == 49 && length(D_GRID) == 49
    @test S_GRID[1] == 0.02 && S_GRID[end] == 0.98
    @test D_GRID[1] == 0.04 && D_GRID[end] == 1.96
    @test 0.0 ∉ S_GRID && 1.0 ∉ S_GRID
    @test 0.0 ∉ D_GRID && 3.0 ∉ D_GRID
    # 5-point equivalence subset lives on the frozen grid.
    pts = [(0.02, 0.04), (0.98, 0.04), (0.50, 1.96), (0.50, 1.00), (0.98, 1.96)]
    for (s, d) in pts
        @test any(abs.(S_GRID .- s) .< 1e-12) && any(abs.(D_GRID .- d) .< 1e-12)
    end
end
