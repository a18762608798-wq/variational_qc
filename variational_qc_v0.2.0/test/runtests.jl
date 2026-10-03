# Julia test entry (T003). Suites mirror the Python round: unit → contract → integration.

using Test

const TESTDIR = @__DIR__

include(joinpath(TESTDIR, "..", "src_jl", "SSHXXZ.jl"))
using .SSHXXZ

for suite in ("unit", "contract", "integration")
    dir = joinpath(TESTDIR, suite)
    isdir(dir) || continue
    for f in sort(readdir(dir))
        endswith(f, ".jl") || continue
        @info "including $suite/$f"
        include(joinpath(dir, f))
    end
end
