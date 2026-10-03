"""Experiment 04 orchestration ONLY: ideal variational runs + selection + checks.

Frozen optimizer (doc/plan/experiment/04_ideal_vqe.md): p=1 DE+COBYLA
n_seeds=3; p>=2 warm start + U(-0.3,0.3) + n_restarts=3 + clamp; box [-pi,pi];
delta=1 halved; delta=3 AFM first-layer two ZZ frozen to 0; byte-exact seeds.
S_REF imported from exp03 (scan-03-04 rule 1): 04 never regenerates s.
"""

import numpy as np

from experiments.exp03_reference import S_REF
from ssh_xxz.core.ansatz import embed_params, n_params
from ssh_xxz.core.cost import select_branch
from ssh_xxz.core.hamiltonian import build_hamiltonian
from ssh_xxz.core.observables import s_pi, string_order
from ssh_xxz.io.store import iter_points, point_exists, save_point, write_manifest
from ssh_xxz.vqe.optimizer import (
    BOX,
    N_RESTARTS,
    N_SEEDS,
    make_energy_fn,
    optimize_p1,
    optimize_warm,
)
from ssh_xxz.vqe.seeds import derive_seed

CODE_VERSION = "0.1.0"
TAU = 1e-6
BRANCHES = ("trivial", "topological", "afm")
DELTAS = (1.0, 3.0)
DEPTHS = (1, 2, 3, 4, 5)


def check_variational_principle(evar, e0, tau=TAU):
    """AS-04.4: 'ok' iff Evar >= E0 - tau, else 'failed'."""
    return "ok" if float(evar) >= float(e0) - tau else "failed"


def apply_nesting_clamp(candidates, baseline, tau=TAU):
    """AS-04.5: argmin over candidates + embedded baseline.

    candidates: [(x, f)], baseline: (x_base, f_base).
    Returns (x, f, from_baseline: bool).
    """
    bx, bf = baseline
    pool = [(np.asarray(bx, dtype=float), float(bf), True)]
    pool += [(np.asarray(x, dtype=float), float(f), False) for x, f in candidates]
    best = min(pool, key=lambda c: c[1])
    return best


def frozen_mask(L, p, delta, init):
    """Boolean mask (True=frozen to 0). δ=3 AFM: first-layer first-even-sublayer
    two ZZ orbit params (indices 1 and 3 of layer 0)."""
    mask = np.zeros(n_params(L, p, delta), dtype=bool)
    if delta != 1 and init == "afm" and p >= 1:
        per_layer = n_params(L, 1, delta)
        mask[1] = True
        mask[3] = True
    return mask


def _run_one_branch(L, s, d, p, branch, H, e_fn, prev_opt, de_budget):
    mask = frozen_mask(L, p, delta=d, init=branch)
    free = np.where(~mask)[0]
    seedt = (s, d, branch)
    if p == 1:
        def fn_free(xf):
            th = np.zeros(n_params(L, p, d))
            th[free] = xf
            return e_fn(th)

        mb, mf, mn = optimize_p1(fn_free, len(free), seedt,
                                 de_maxiter=de_budget[0], de_popsize=de_budget[1])
        th = np.zeros(n_params(L, p, d))
        th[free] = mb
        return th, mf, mn, False
    # p>=2 warm start from previous optimum; perturb only the new layer.
    prev_th, _ = prev_opt
    base_full = embed_params(prev_th, L, p, d, branch)
    base_full[mask] = 0.0
    f_base = e_fn(base_full)

    def fn_free(xf):
        th = base_full.copy()
        th[free] = xf
        return e_fn(th)

    new_start = n_params(L, p - 1, d)
    pos = [k for k, gi in enumerate(free) if gi >= new_start]
    bx, bf, bn, flag = optimize_warm(
        fn_free, base_full[free], pos, seedt, (base_full[free], f_base))
    th = base_full.copy()
    th[free] = bx
    return th, bf, bn, flag


def _state_obs(L, p, d, branch, theta, sim):
    from ssh_xxz.vqe.optimizer import full_circuit as _fc

    circ = _fc(L, p, d, branch, np.asarray(theta, dtype=float))
    circ.save_statevector()
    psi = np.asarray(sim.run(circ).result().get_statevector())
    return float(s_pi(psi, L)), float(string_order(psi, L))


def run_one_chain(var_dir, L, d, s, branch, depths, de_budget):
    """One (s,δ,branch) depth chain with warm-start chaining across depths.

    Unit of parallel work for run_all (T054). Writes branch records only.
    """
    s, d = float(s), float(d)
    H = build_hamiltonian(L, s, d)
    prev = None
    for p in depths:
        # seed upfront: existence hash matches save hash (resume bugfix).
        key = {"L": L, "s": s, "delta": d, "p": p, "branch": branch,
               "seed": int(derive_seed(s, d, branch, 0))}
        if point_exists(var_dir, "exp04b", key):
            rec = next(r for r in iter_points(var_dir, "exp04b")
                       if r.get("status") == "ok" and r["s"] == s
                       and r["delta"] == d and r["p"] == p
                       and r["branch"] == branch)
            prev = (np.asarray(rec["theta"]), float(rec["Ebranch"]))
            continue
        e_fn = make_energy_fn(L, p, d, branch, H)
        th, f, nexp, flag = _run_one_branch(
            L, s, d, p, branch, H, e_fn, prev, de_budget)
        seed = derive_seed(s, d, branch, 0)
        save_point(var_dir, "exp04b",
                   {**key, "theta": np.asarray(th),
                    "Ebranch": float(f), "nevals": int(nexp),
                    "seed": int(seed), "from_baseline": bool(flag),
                    "status": "ok", "experiment": "exp04",
                    "backend": "statevector-exact",
                    "code_version": CODE_VERSION,
                    "source": "ideal-variational"})
        prev = (th, f)


def select_one_point(var_dir, ref_dir, L, d, s, depths, sim=None, branches=None):
    """Argmin selection + exact join + observables for one (s,δ)."""
    from qiskit_aer import AerSimulator

    branches = BRANCHES if branches is None else branches

    s, d = float(s), float(d)
    sim = sim or AerSimulator(method="statevector")
    ref = {(r["s"], r["delta"]): r for r in iter_points(ref_dir, "exp03")
           if r.get("status") == "ok"}
    n = 0
    for p in depths:
        sel_key = {"L": L, "s": s, "delta": d, "p": p}
        if point_exists(var_dir, "exp04s", sel_key):
            n += 1
            continue
        brev = {b: next(r for r in iter_points(var_dir, "exp04b")
                        if r.get("status") == "ok" and r["s"] == s
                        and r["delta"] == d and r["p"] == p
                        and r["branch"] == b)["Ebranch"]
                for b in branches}
        bname, bf = select_branch({b: float(v) for b, v in brev.items()})
        brec = next(r for r in iter_points(var_dir, "exp04b")
                    if r.get("status") == "ok" and r["s"] == s
                    and r["delta"] == d and r["p"] == p
                    and r["branch"] == bname)
        eref = ref[(s, d)]
        stat = check_variational_principle(bf, float(eref["E0"]))
        spi_v, ostr_v = _state_obs(L, p, d, bname, np.asarray(brec["theta"]), sim)
        save_point(var_dir, "exp04s",
                   {**sel_key, "branch": bname, "Evar": float(bf),
                    "Spi": float(spi_v), "Ostr": float(ostr_v),
                    "E0": float(eref["E0"]),
                    "check_vp": stat,
                    "status": "ok" if stat == "ok" else "failed",
                    "experiment": "exp04",
                    "backend": "statevector-exact",
                    "code_version": CODE_VERSION,
                    "source": "ideal-variational"})
        n += 1
    return n


def write_manifest_wrap(var_dir, depths):
    write_manifest(var_dir, "exp04",
                   {"schema": "exp01-04/v1", "L": 8, "depths": list(depths)})


def run_branches(var_dir, ref_dir, L=8, deltas=None, s_grid=None, depths=None,
                 branches=None, de_budget=(300, 10)):
    """Serial driver (tests/T044): chains per branch, then selects per point."""
    deltas = DELTAS if deltas is None else deltas
    s_grid = S_REF if s_grid is None else s_grid
    depths = DEPTHS if depths is None else depths
    branches = BRANCHES if branches is None else branches
    n_sel = 0
    for d in deltas:
        for s in s_grid:
            for branch in branches:
                run_one_chain(var_dir, L, float(d), float(s), branch,
                              depths, de_budget)
            n_sel += select_one_point(var_dir, ref_dir, L, float(d), float(s),
                                      depths, branches=branches)
    write_manifest(var_dir, "exp04",
                   {"schema": "exp01-04/v1", "L": L, "depths": list(depths)})
    return n_sel


def verify_selection(var_dir, ref_dir, tau=TAU):
    """SC-004/005 + AS-04.4/04.5 verification over saved records."""
    ref = {(r["s"], r["delta"]): r for r in iter_points(ref_dir, "exp03")
           if r.get("status") == "ok"}
    sel = [r for r in iter_points(var_dir, "exp04s") if r.get("status") in ("ok", "failed")]
    n_viol = 0
    for r in sel:
        e0 = float(ref[(r["s"], r["delta"])]["E0"])
        if float(r["Evar"]) < e0 - tau:
            n_viol += 1
    # nesting: accepted(p) <= accepted(p-1) + tau per (s,delta)
    nest_viol = 0
    by_sd = {}
    for r in sel:
        by_sd.setdefault((r["s"], r["delta"]), {})[r["p"]] = float(r["Evar"])
    for sd, pd in by_sd.items():
        for p in sorted(pd)[1:]:
            if pd[p] > pd[p - 1] + tau:
                nest_viol += 1
    return {"n_selected": len(sel), "n_violations": n_viol,
            "n_nesting_violations": nest_viol}
