# T026: SC-001 rebuild via Python QS (2x2 mini grid + gaps, Julia runners).
# Narrow opening 2026-10-01: scripts_jl/ deleted; rebuilds driven through the
# Python plotting pipeline as subprocesses. src_jl/ implementations untouched.
include("../../experiments_jl/exp01_phase.jl")
using Test

const _PYBIN = normpath(joinpath(@__DIR__, "..", "..", ".CondaPkg", ".pixi",
                                 "envs", "default", "bin", "python"))
const _PYROOT = normpath(joinpath(@__DIR__, "..", ".."))

function _pyrebuild_qs1(data, out)
    code = "import sys,os; sys.path.insert(0, '" * _PYROOT * "'); " *
           "os.environ['SOURCE_DATE_EPOCH']='0'; " *
           "import matplotlib; matplotlib.use('Agg'); " *
           "from plotting.diagnostic.exp01 import rebuild_all as rd; " *
           "from plotting.pra.exp01 import rebuild_all as rp; " *
           "rd('$data', '$out/d'); rp('$data', '$out/p')"
    run(pipeline(setenv(Cmd([_PYBIN, "-c", code]), Dict("PATH" => ENV["PATH"]));
                 stdout=devnull))
    nd = length(readdir(joinpath(out, "d")))
    np = length(readdir(joinpath(out, "p")))
    return (nd, np)
end

@testset "sc001" begin
    data = mktempdir()
    n = run_grid(data; s_grid=[0.5, 0.52], d_grid=[0.96, 1.02])
    @test n == 4
    m = run_gaps(data; Ls=[4, 8], s_grid=[0.5, 0.52])
    @test m == 4
    out = mktempdir()
    nd, np = _pyrebuild_qs1(data, out)
    @test nd == 3
    @test np == 7  # 3 pdf + 3 png + pra_check.md
end
