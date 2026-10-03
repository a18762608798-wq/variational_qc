# Physical cost + selection. Authoritative: doc/plan/theory/cost_fun.md.

module Cost

export select_branch, BRANCHES

const BRANCHES = ("trivial", "topological", "afm")

function select_branch(branch_energies::Dict, restarts=nothing)
    if restarts !== nothing
        k = first(keys(branch_energies))
        return k, Float64(minimum(restarts))
    end
    best = argmin(branch_energies)
    return best, Float64(branch_energies[best])
end

end # module
