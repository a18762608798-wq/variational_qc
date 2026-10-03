"""T008: observable evaluation conventions (IV.2). FAIL-first."""

import numpy as np
import pytest

from ssh_xxz.core.initial_states import afm_state
from ssh_xxz.core.observables import q_diagnostic, s_pi, string_order, structure_factor


def test_afm_ghz_observables():
    # |0101..>+|1010..> : <ZiZj>=(-1)^{i-j} -> S(pi)=L, Ostr known pattern.
    L = 8
    psi = afm_state(L)
    assert s_pi(psi, L) == pytest.approx(8.0)
    q = 2.0 * np.pi * np.arange(L) / L
    sq = structure_factor(psi, L, q)
    assert np.argmax(sq) == 4  # q=pi peak


def test_q_is_derived_only():
    assert q_diagnostic(8.0, 0.5) == 4.0 / 3.0 + 2 * 0.5 - 8.0 / 6.0


def test_string_order_finite():
    L = 8
    psi = afm_state(L) / np.linalg.norm(afm_state(L))
    assert np.isfinite(string_order(psi, L))
