# Exact diagonalization. Production = sparse; dense = small-L reference only.

module EDSolver

using KrylovKit, LinearAlgebra, SparseArrays

export ground_state, lowest_two, dense_energies

const TOL = 1e-10

function ground_state(H; tol=TOL)
    vals, vecs, _ = eigsolve(H, 1, :SR; tol=tol)
    v = vecs[1] / norm(vecs[1])
    return real(vals[1]), Vector{ComplexF64}(v)
end

function lowest_two(H; tol=TOL)
    vals, vecs, _ = eigsolve(H, 2, :SR; tol=tol)
    o = sortperm(real.(vals))
    return (real(vals[o[1]]), real(vals[o[2]]),
            Vector{ComplexF64}(vecs[o[1]] / norm(vecs[o[1]])),
            Vector{ComplexF64}(vecs[o[2]] / norm(vecs[o[2]])))
end

dense_energies(H, k=2) = sort(eigvals(Matrix(H)))[1:k]

end # module
