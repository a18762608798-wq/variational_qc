"""Experiment 02 orchestration ONLY: read config -> call core -> save.

Shares the canonical grid + state convention with 01 (grid-01-02);
Q stored derived-only (q-reconstruction); physics never reimplemented.
"""

import numpy as np

from ssh_xxz.core.hamiltonian import build_hamiltonian
from ssh_xxz.core.observables import (
    q_diagnostic,
    s_pi,
    string_order,
    structure_factor,
    z_tilde_R,
)
from ssh_xxz.ed.solver import ground_state
from ssh_xxz.io.grids import D_GRID, REPS, S_GRID, q_grid
from ssh_xxz.io.store import point_exists, save_point, write_manifest

CODE_VERSION = "0.1.1"  # ZtR mirror-contraction fix


def _prov(L):
    return {"experiment": "exp02", "L": L, "backend": "sparse-eigsh",
            "seed": "deterministic-n/a", "code_version": CODE_VERSION,
            "source": "exact"}


def run_one_heatmap_point(data_dir, L, s, d):
    """Single heatmap point; True if computed now, False if resumed."""
    rec = {"L": L, "s": float(s), "delta": float(d), **_prov(L)}
    if point_exists(data_dir, "exp02", rec):
        return False
    try:
        H = build_hamiltonian(L, float(s), float(d))
        e0, psi = ground_state(H)
        spi = s_pi(psi, L)
        ostr = string_order(psi, L)
        rec.update({"E0": e0, "Spi": spi, "Ostr": ostr,
                    "Q": q_diagnostic(spi, ostr),
                    "ZtR": z_tilde_R(psi, L),
                    "ZtR_ref": "exp01-canonical",
                    "status": "ok"})
    except Exception as exc:  # noqa: BLE001
        rec.update({"status": "failed",
                    "reason": f"{type(exc).__name__}: {exc}"})
    save_point(data_dir, "exp02", rec)
    return True


def write_manifest_wrap(data_dir, L=8):
    write_manifest(data_dir, "exp02",
                   {"schema": "exp01-04/v1", "L": L, "grid": "49x49-interior-shared", "code_version": CODE_VERSION})


def run_heatmaps(data_dir, L=8, s_grid=None, d_grid=None):
    s_grid = S_GRID if s_grid is None else s_grid
    d_grid = D_GRID if d_grid is None else d_grid
    n = 0
    for s in s_grid:
        for d in d_grid:
            n += run_one_heatmap_point(data_dir, L, float(s), float(d))
    write_manifest(data_dir, "exp02",
                   {"schema": "exp01-04/v1", "L": L, "grid": "49x49-interior-shared", "code_version": CODE_VERSION})
    return n


def run_sq_curves(data_dir, L=8):
    q = q_grid()
    n = 0
    for name, (s, d) in REPS.items():
        # q array included BEFORE point_exists (it is hashed; resume bugfix).
        rec = {"L": L, "s": float(s), "delta": float(d), "rep": name,
               "q": np.asarray(q)}
        if point_exists(data_dir, "exp02sq", rec):
            continue
        try:
            H = build_hamiltonian(L, float(s), float(d))
            _, psi = ground_state(H)
            rec.update({"q": q, "Sq": structure_factor(psi, L, q),
                        "status": "ok", **_prov(L)})
        except Exception as exc:  # noqa: BLE001
            rec.update({"status": "failed",
                        "reason": f"{type(exc).__name__}: {exc}", **_prov(L)})
        save_point(data_dir, "exp02sq", rec)
        n += 1
    return n
