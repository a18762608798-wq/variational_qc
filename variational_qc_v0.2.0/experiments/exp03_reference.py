"""Experiment 03 orchestration ONLY: L=8 exact reference on frozen scan lines.

S_REF is the AUTHORITATIVE s array (AS-03.3): 04 MUST import it
(contracts/scan-03-04.md rule 1), never regenerate its own grid.
"""

import numpy as np

from ssh_xxz.core.hamiltonian import build_hamiltonian
from ssh_xxz.core.observables import s_pi, string_order
from ssh_xxz.ed.solver import ground_state
from ssh_xxz.io.store import iter_points, point_exists, save_point, write_manifest

S_REF = np.arange(1, 50) / 50.0
DELTAS = (1.0, 3.0)
CODE_VERSION = "0.1.0"


def _prov():
    return {"experiment": "exp03", "L": 8, "backend": "sparse-eigsh",
            "seed": "deterministic-n/a", "code_version": CODE_VERSION,
            "source": "exact"}


def run_one_ref_point(data_dir, L, s, d):
    """Single exact-ref point; True if computed now, False if resumed."""
    rec = {"L": L, "s": float(s), "delta": float(d), **_prov()}
    if point_exists(data_dir, "exp03", rec):
        return False
    try:
        H = build_hamiltonian(L, float(s), float(d))
        e0, psi = ground_state(H)
        rec.update({"E0": e0, "Spi": s_pi(psi, L),
                    "Ostr": string_order(psi, L),
                    "status": "ok"})
    except Exception as exc:  # noqa: BLE001
        rec.update({"status": "failed",
                    "reason": f"{type(exc).__name__}: {exc}"})
    save_point(data_dir, "exp03", rec)
    return True


def write_manifest_wrap(data_dir, L=8):
    write_manifest(data_dir, "exp03",
                   {"schema": "exp01-04/v1", "L": L, "scan": "2x49"})


def run_reference(data_dir, L=8, deltas=None, s_grid=None):
    deltas = DELTAS if deltas is None else deltas
    s_grid = S_REF if s_grid is None else s_grid
    n = 0
    for d in deltas:
        for s in s_grid:
            n += run_one_ref_point(data_dir, L, float(s), float(d))
    write_manifest(data_dir, "exp03",
                   {"schema": "exp01-04/v1", "L": L, "scan": "2x49"})
    return n


def iter_reference(data_dir):
    return [r for r in iter_points(data_dir, "exp03") if r.get("status") == "ok"]
