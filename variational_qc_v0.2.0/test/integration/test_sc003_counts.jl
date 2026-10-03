# T037: SC-003 count integration (mini subset).
include("../../experiments_jl/exp03_reference.jl")
using Test

@testset "sc003" begin
    data = mktempdir()
    n = run_reference(data; deltas=[0.0], s_grid=[0.1, 0.5, 0.9])
    @test n == 3
    recs = collect(iter_reference(data))
    @test length(recs) == 3
    @test all(all(k in keys(r) for k in ("E0", "Spi", "Ostr")) for r in recs)
end
