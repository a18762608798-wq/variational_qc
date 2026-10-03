"""Physical cost + selection. Authoritative: doc/plan/theory/cost_fun.md.

C_a(θ) = <ψ_a(θ)|H|ψ_a(θ)>; reported optimum = min over branches,
and min over restarts within a branch.
"""

BRANCHES = ("trivial", "topological", "afm")


def select_branch(branch_energies, restarts=None):
    """Return (key, min_energy) over branches; restarts narrow one branch."""
    if restarts is not None:
        key = next(iter(branch_energies))
        return key, float(min(restarts))
    best = min(branch_energies.items(), key=lambda kv: kv[1])
    return best[0], float(best[1])
