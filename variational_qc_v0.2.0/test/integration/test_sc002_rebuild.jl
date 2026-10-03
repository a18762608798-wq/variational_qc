# T032: SC-002 rebuild via Python QS (mini 2x2 heat + sq curves).
# Narrow opening 2026-10-01: scripts_jl/ deleted; rebuilds driven through the
# Python plotting pipeline as subprocesses. src_jl/ implementations untouched.
include("../../experiments_jl/exp02_observables.jl")
using Test

const _PYBIN = normpath(joinpath(@__DIR__, "..", "..", ".CondaPkg", ".pixi",
                                 "envs", "default", "bin", "python"))
const _PYROOT = normpath(joinpath(@__DIR__, "..", ".."))

@testset "sc002" begin
    data = mktempdir()
    n = run_heatmaps(data; s_grid=[0.02, 0.5], d_grid=[0.04, 1.96])
    @test n == 4
    m = run_sq_curves(data)
    @test m == 3
    code = "import sys,os; sys.path.insert(0, '" * _PYROOT * "'); " *
           "os.environ['SOURCE_DATE_EPOCH']='0'; " *
           "import matplotlib; matplotlib.use('Agg'); " *
           "from plotting.diagnostic.exp02 import rebuild_all as rd; " *
           "from plotting.pra.exp02 import rebuild_all as rp; " *
           "rd('$data', '$data/d'); rp('$data', '$data/p')"
    run(pipeline(setenv(Cmd([_PYBIN, "-c", code]), Dict("PATH" => ENV["PATH"]));
                 stdout=devnull))
    nd = length(readdir(joinpath(data, "d")))
    np = length(readdir(joinpath(data, "p")))
    @test nd == 5
    @test np == 11  # 5 pdf + 5 png + pra_check.md
end
