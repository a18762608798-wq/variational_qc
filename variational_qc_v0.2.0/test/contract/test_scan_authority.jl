# T036: 03->04 s-authority contract (AS-03.2, scan-03-04 rule 1).
include("../../experiments_jl/exp03_reference.jl")
using Test

@testset "scan-authority" begin
    @test S_REF == collect(1:49) ./ 50.0
    @test length(S_REF) == 49
end
