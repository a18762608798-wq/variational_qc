# T041: nesting clamp (AS-04.5).
include("../../experiments_jl/exp04_ideal.jl")
using Test

@testset "clamp" begin
    x, f, flag = apply_nesting_clamp([(ones(8), -2.5)], (zeros(8), -3.0), 1e-6)
    @test f == -3.0 && flag == true
    x, f, flag = apply_nesting_clamp([(ones(8), -3.5)], (zeros(8), -3.0), 1e-6)
    @test f == -3.5 && flag == false
end
