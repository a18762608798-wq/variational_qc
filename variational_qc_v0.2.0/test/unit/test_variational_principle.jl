# T040: tau violation flag (AS-04.4).
include("../../experiments_jl/exp04_ideal.jl")
using Test

@testset "vp" begin
    @test check_variational_principle(-3.0, -3.0, 1e-6) == "ok"
    @test check_variational_principle(-3.0 - 2e-6, -3.0, 1e-6) == "failed"
    @test check_variational_principle(-3.0 - 5e-7, -3.0, 1e-6) == "ok"
end
