# T013: free-intercept polyfit post-processing via Python pipeline (CL-002).
# Narrow opening 2026-10-01: scripts_jl/ deleted; this test now drives the
# Python plotting fit (plotting/diagnostic/exp01_scaling.py) as a subprocess.
# src_jl/ implementations untouched.
using Test

const _PYBIN = normpath(joinpath(@__DIR__, "..", "..", ".CondaPkg", ".pixi",
                                 "envs", "default", "bin", "python"))
const _PYROOT = normpath(joinpath(@__DIR__, "..", ".."))

@testset "fit" begin
    code = "import sys; sys.path.insert(0, '" * _PYROOT * "'); " *
           "from plotting.diagnostic.exp01_scaling import fit_scaling; " *
           "a, b = fit_scaling([1/4, 1/8, 1/12, 1/16], " *
           "  [2.5/4 + 0.03, 2.5/8 + 0.03, 2.5/12 + 0.03, 2.5/16 + 0.03]); " *
           "assert abs(a - 2.5) < 1e-9 and abs(b - 0.03) < 1e-9, (a, b); " *
           "print('fit ok', a, b)"
    cmd = setenv(Cmd([_PYBIN, "-c", code]), Dict("PATH" => ENV["PATH"]))
    @test success(run(pipeline(cmd; stdout=devnull)))
end
