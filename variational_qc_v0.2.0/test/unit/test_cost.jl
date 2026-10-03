# T009: physical cost + min-over-branches/restarts selection.
using .SSHXXZ, Test

@testset "cost" begin
    @test select_branch(Dict("trivial" => 1.5, "topological" => 0.5, "afm" => 2.0)) ==
          ("topological", 0.5)
    @test select_branch(Dict("a" => 1.0), [1.0, 0.7, 0.9]) == ("a", 0.7)
end
