"""Regression: energy_fn acts on the reference initial state (not |0...0>).

theta=0 must reproduce <psi_init|H|psi_init> for every branch; otherwise the
VQE optimizes the wrong sector and returns unphysically high energies.
"""

import numpy as np

from ssh_xxz.core.hamiltonian import build_hamiltonian
from ssh_xxz.core.initial_states import afm_state, topo_state, trivial_state
from ssh_xxz.vqe.optimizer import full_circuit, make_energy_fn

INITS = {"trivial": trivial_state, "topological": topo_state, "afm": afm_state}


def test_zero_theta_is_init_energy():
    L = 8
    H = build_hamiltonian(L, 0.5, 1.0)
    for name, fn in INITS.items():
        psi = fn(L)
        expect = float((psi.conj() @ (H @ psi)).real)
        got = make_energy_fn(L, 1, 1.0, name, H)(np.zeros(4))
        assert got == expect


def test_full_circuit_zero_is_init_state():
    from qiskit_aer import AerSimulator

    sim = AerSimulator(method="statevector")
    L = 8
    for name, fn in INITS.items():
        circ = full_circuit(L, 1, 2.0, name, np.zeros(8))
        circ.save_statevector()
        psi = np.asarray(sim.run(circ).result().get_statevector())
        assert np.allclose(psi, fn(L))
