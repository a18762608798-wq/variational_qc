# T007 cross-check: v0.2.0 independent Hamiltonian vs v0.3.0 production E0.
# Run with: julia --project=<v02root> --startup-file=no scripts/xcheck_v02.jl
# (lives in v0.3.0 tree but executes in the v0.2.0 environment; read-only
# toward v0.2.0).

push!(LOAD_PATH, joinpath(@__DIR__, "..", "..", "variational_qc_v0.2.0", "src_jl"))
using SSHXXZ, LinearAlgebra, NPZ

const NPZ_PATH = joinpath(@__DIR__, "..", "data", "shared01", "shared01_S01.npz")

function main()
    arrays = NPZ.npzread(NPZ_PATH)
    E0 = arrays["E0"]
    worst = 0.0
    for (s, d) in [(0.01, 0.02), (0.5, 1.0), (0.99, 0.02), (0.5, 1.98), (0.99, 1.98)]
        H = Matrix(build_hamiltonian(8, s, d; sparse=true))
        ref = minimum(real(eigvals(Hermitian(H))))
        i, j = round(Int, 100 * s), round(Int, 50 * d)
        err = abs(ref - E0[i, j])
        worst = max(worst, err)
        println("s=$s d=$d v02E0=$ref prodE0=$(E0[i,j]) err=$err")
    end
    println(worst < 1e-8 ? "XCHECK-V02-OK" : "XCHECK-V02-MISMATCH")
    worst < 1e-8 || exit(1)
end

main()
