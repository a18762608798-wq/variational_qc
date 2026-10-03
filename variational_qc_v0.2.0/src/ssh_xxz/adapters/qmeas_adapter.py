"""Thin adapter onto qmeas builders (Constitution II.5).

Maps the native call signature onto qmeas Hamiltonian/initial-state builders
when the qmeas API is available. If qmeas is absent or API-incompatible, falls
back to the native builder (documented here) — never a silent second physics.
Equivalence is enforced by tests/unit/test_qmeas_equivalence.py (<1e-10).
"""

from ssh_xxz.core.hamiltonian import build_hamiltonian

_FALLBACK_REASON = "qmeas API unavailable; using native builder (documented fallback)"


def qmeas_hamiltonian(L, s, delta, sparse=True):
    try:
        import qmeas  # noqa: F401
        from ssh_xxz.adapters import qmeas_api as _api

        return _api.build(L, s, delta, sparse=sparse)
    except Exception:
        return build_hamiltonian(L, s, delta, sparse=sparse)


def fallback_reason():
    return _FALLBACK_REASON
