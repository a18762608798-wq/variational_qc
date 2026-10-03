"""T007: ansatz parameter count/order + nesting (IV.2). FAIL-first."""

import numpy as np

from ssh_xxz.core.ansatz import build_circuit, embed_params, layer_order, n_params


def test_param_counts():
    assert n_params(8, 3, 2.0) == 8 * 3
    assert n_params(8, 3, 1.0) == 8 * 3 // 2
    assert n_params(8, 5, 3.0) == 40


def test_first_sublayer_rule():
    assert layer_order("trivial")[0] == "e"
    assert layer_order("topological")[0] == "o"
    assert layer_order("afm")[0] == "e"


def test_fixed_layer_order_alternates():
    # F1,S1,F2,S2,... pattern encoded in circuit metadata.
    circ = build_circuit(8, 2, 2.0, "trivial", np.zeros(n_params(8, 2, 2.0)))
    assert circ.metadata["sublayer_seq"] == ["e", "o", "e", "o"]


def test_nesting_zero_pad_identity():
    # p-1 params embedded with zero new layer reproduce the p-1 state.
    rng = np.random.default_rng(0)
    th = rng.uniform(-np.pi, np.pi, n_params(8, 2, 2.0))
    emb = embed_params(th, 8, 3, 2.0, "trivial")
    c2 = build_circuit(8, 2, 2.0, "trivial", th)
    c3 = build_circuit(8, 3, 2.0, "trivial", emb)
    assert c2.metadata["state_key"] == c3.metadata["state_key"]
