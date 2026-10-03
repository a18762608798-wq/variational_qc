"""Experiment 01 orchestration ONLY: read config -> call core -> save -> (plot trigger).

Reads the canonical grid (contracts/grid-01-02.md); never reimplements physics.
"""

from ssh_xxz.core.hamiltonian import build_hamiltonian
from ssh_xxz.core.observables import z_tilde_R
from ssh_xxz.ed.solver import ground_state, lowest_two
from ssh_xxz.io.grids import D_GRID, S_GRID
from ssh_xxz.io.store import point_exists, save_point, write_manifest

CODE_VERSION = "0.1.1"  # ZtR mirror-contraction fix


def _prov(exp, L, backend):
    return {"experiment": exp, "L": L, "backend": backend,
            "seed": "deterministic-n/a", "code_version": CODE_VERSION,
            "source": "exact"}


def run_one_grid_point(data_dir, L, s, d):
    """Single Z~R point; True if computed now, False if resumed. Unit for run_all."""
    # NOTE: full coord set (incl. seed via _prov) BEFORE point_exists, so the
    # existence hash is identical to the one save_point will use (resume bugfix).
    rec = {"L": L, "s": float(s), "delta": float(d),
           **_prov("exp01", L, "sparse-eigsh")}
    if point_exists(data_dir, "exp01", rec):
        return False
    try:
        H = build_hamiltonian(L, float(s), float(d))
        e0, psi = ground_state(H)
        rec.update({"E0": e0, "ZtR": z_tilde_R(psi, L), "status": "ok"})
    except Exception as exc:  # noqa: BLE001 - failure must be recorded
        rec.update({"status": "failed", "reason": f"{type(exc).__name__}: {exc}"})
    save_point(data_dir, "exp01", rec)
    return True


def run_one_gap_point(data_dir, L, s):
    """Single δ=1 gap point; True if computed now, False if resumed."""
    rec = {"L": L, "s": float(s), "delta": 1.0,
           **_prov("exp01gap", L, "sparse-eigsh")}
    if point_exists(data_dir, "exp01gap", rec):
        return False
    try:
        H = build_hamiltonian(L, float(s), 1.0)
        e0, e1, _, _ = lowest_two(H)
        rec.update({"E0": e0, "E1": e1, "draw": e1 - e0, "status": "ok"})
    except Exception as exc:  # noqa: BLE001
        rec.update({"status": "failed", "reason": f"{type(exc).__name__}: {exc}"})
    save_point(data_dir, "exp01gap", rec)
    return True


def write_manifest_wrap(data_dir, L=8):
    write_manifest(data_dir, "exp01",
                   {"schema": "exp01-04/v1", "L": L, "grid": "49x49-interior", "code_version": CODE_VERSION})


def run_grid(data_dir, L=8, s_grid=None, d_grid=None):
    """2401-point Z~R grid (AS-01.1). Idempotent resume via point_exists."""
    s_grid = S_GRID if s_grid is None else s_grid
    d_grid = D_GRID if d_grid is None else d_grid
    n = 0
    for s in s_grid:
        for d in d_grid:
            n += run_one_grid_point(data_dir, L, float(s), float(d))
    write_manifest(data_dir, "exp01",
                   {"schema": "exp01-04/v1", "L": L, "grid": "49x49-interior", "code_version": CODE_VERSION})
    return n


def run_gaps(data_dir, Ls=(4, 8, 12, 16), s_grid=None):
    """Raw full-Hilbert-space gaps on the δ=1 line (AS-01.2, R1 s reuse)."""
    s_grid = S_GRID if s_grid is None else s_grid
    n = 0
    for L in Ls:
        for s in s_grid:
            n += run_one_gap_point(data_dir, L, float(s))
    return n
