"""T031: Q reconstruction-only contract (q-reconstruction rules 1-5). FAIL-first."""

import numpy as np

from ssh_xxz.core.observables import q_diagnostic


def test_same_path_bitwise_identity():
    a = q_diagnostic(3.0, 0.25)
    b = q_diagnostic(3.0, 0.25)
    assert a == b  # float64 bitwise identity, same code path


def test_q_uses_only_spi_ostr():
    # Q must be a pure function of (S(pi), Ostr): no hidden third input.
    import inspect

    assert list(inspect.signature(q_diagnostic).parameters) == ["s_pi_val", "ostr_val"]


def test_qgrid_contract_values():
    from ssh_xxz.io.grids import q_grid

    q = q_grid()
    assert len(q) == 49
    assert np.pi in q  # explicit pi grid point
