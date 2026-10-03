# T042: SC-004/005 mini integration (1 point, 1 branch, tiny DE budget).
include("../../experiments_jl/exp03_reference.jl")
include("../../experiments_jl/exp04_ideal.jl")
using Test

@testset "sc004" begin
    ref = mktempdir()
    var = mktempdir()
    run_reference(ref; deltas=[0.0], s_grid=[0.5])
    n = run_branches(var, ref; deltas=[0.0], s_grid=[0.5], depths=[1],
                     branches=["trivial"], de_budget=(5, 5))
    @test n == 1
    rep = verify_selection(var, ref; tau=1e-6)
    @test rep["n_selected"] == 1
    @test rep["n_violations"] == 0
end
