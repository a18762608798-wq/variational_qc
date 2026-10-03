# T027: scaling rebuild consumes v2 gap records + Python fit (CL-002).
# Narrow opening 2026-10-01: scripts_jl/ deleted; fit asserted through the
# Python plotting fit. src_jl/ implementations untouched.
include("../../experiments_jl/exp01_phase.jl")
using Test

const _PYBIN = normpath(joinpath(@__DIR__, "..", "..", ".CondaPkg", ".pixi",
                                 "envs", "default", "bin", "python"))
const _PYROOT = normpath(joinpath(@__DIR__, "..", ".."))

@testset "sc001-scaling" begin
    data = mktempdir()
    run_gaps(data; Ls=[4, 8], s_grid=[0.5])
    code = "import sys,os,glob; sys.path.insert(0, '" * _PYROOT * "'); " *
           "os.environ['SOURCE_DATE_EPOCH']='0'; " *
           "import matplotlib; matplotlib.use('Agg'); " *
           "from plotting.diagnostic.exp01 import rebuild_all as rd; " *
           "made = rd('$data', '$data/fig'); " *
           "assert any('scaling' in f for f in made), made; print('scaling ok')"
    run(pipeline(setenv(Cmd([_PYBIN, "-c", code]), Dict("PATH" => ENV["PATH"]));
                 stdout=devnull))
    @test isfile(joinpath(data, "fig", "scaling_diag.png"))
end
