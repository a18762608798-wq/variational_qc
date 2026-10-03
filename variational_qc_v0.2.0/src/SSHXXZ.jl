# Package entry shim for Pkg.test() infra (T054 gate; 2026-10-01).
# Real implementation lives in src_jl/SSHXXZ.jl (included directly by
# test/runtests.jl); this file only satisfies Pkg's src/<name>.jl requirement.
# Fully qualified: precompile sandbox modules may lack `using Base`.
Base.include(@__MODULE__, (@__DIR__) * "/../src_jl/SSHXXZ.jl")
