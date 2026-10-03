# T012: QMeasPort minimal-port equivalence (D-003).
# Initial states are H-independent: Julia port MUST match the archived Python
# baseline bit-for-bit (<1e-12) via black-box subprocess oracle. H builder is
# checked against analytic limits (new H differs from round-1 physics).
using .SSHXXZ, Test, LinearAlgebra, JSON

const PYREPO = normpath(joinpath(@__DIR__, "..", ".."))
const PYBIN = joinpath(PYREPO, ".CondaPkg", ".pixi", "envs", "default", "bin", "python")

function py_state(kind, L)
    code = "import sys,json; sys.path.insert(0, '" * PYREPO * "/src'); " *
           "from ssh_xxz.core.initial_states import $(kind)_state; " *
           "import numpy as np; psi=$(kind)_state($L); " *
           "print(json.dumps([float(x.real) for x in psi]))"
    out = read(`$PYBIN -c $code`, String)
    return JSON.parse(out)
end

@testset "qmeasport" begin
    # H builder vs analytic new-H limits (s=0,δ=0 → -3L/2; s=1,δ=0 OBC → -3(L/2-1)).
    @test minimum(eigvals(Matrix(port_hamiltonian(4, 0.0, 0.0)))) ≈ -6.0 atol = 1e-10
    @test minimum(eigvals(Matrix(port_hamiltonian(4, 1.0, 0.0)))) ≈ -3.0 atol = 1e-10
    # Initial states vs archived Python oracle (<1e-12, H-independent).
    for (kind, jl) in (("trivial", port_trivial_state),
                       ("topo", port_topo_state), ("afm", port_afm_state))
        py = py_state(kind, 8)
        @test maximum(abs.(jl(8) .- py)) < 1e-12
    end
end
