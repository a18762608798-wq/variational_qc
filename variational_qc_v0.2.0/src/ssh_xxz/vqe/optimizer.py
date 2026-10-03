"""Ideal optimizer. Frozen settings: doc/plan/experiment/04_ideal_vqe.md.

p=1: differential_evolution + COBYLA polish, n_seeds=3, seeds derived.
p>=2: warm start + U(-0.3,0.3) new layer, n_restarts=3, COBYLA polish,
      clamp to baseline when worse. Box [-pi, pi]. Ideal statevector only.
"""

import numpy as np
from scipy.optimize import differential_evolution, minimize

from ssh_xxz.core.ansatz import build_circuit
from ssh_xxz.core.initial_states import afm_state, topo_state, trivial_state
from ssh_xxz.vqe.seeds import derive_seed

INIT_STATES = {"trivial": trivial_state, "topological": topo_state,
               "afm": afm_state}

BOX = (-np.pi, np.pi)
N_SEEDS = 3
N_RESTARTS = 3
PERTURB = 0.3


def full_circuit(L, p, delta, init, theta):
    """Ansatz acting on the reference initial state: |ψ(θ)> = U(θ)|ψ_init>.

    Qiskit little-endian (qubit m = LSB) matches the core site<->bit
    convention, so the dense init vector initializes directly.
    """
    from qiskit import QuantumCircuit

    circ = QuantumCircuit(L)
    circ.initialize(INIT_STATES[init](L).tolist(), range(L))
    return circ.compose(build_circuit(L, p, delta, init, theta))


def make_energy_fn(L, p, delta, init, H):
    """Statevector energy fn(theta) for U(θ)|ψ_init> (ideal, no shots)."""
    from qiskit_aer import AerSimulator

    sim = AerSimulator(method="statevector")

    def fn(theta):
        circ = full_circuit(L, p, delta, init, np.asarray(theta, dtype=float))
        circ.save_statevector()
        psi = np.asarray(sim.run(circ).result().get_statevector())
        return float((psi.conj() @ (H @ psi)).real)

    return fn


def _polish(energy_fn, x0):
    r = minimize(energy_fn, np.asarray(x0, dtype=float), method="COBYLA",
                 options={"maxiter": 2000})
    return np.asarray(r.x), float(r.fun), int(r.nfev)


def optimize_p1(energy_fn, dim, seed_tuple, de_maxiter=300, de_popsize=10):
    """Global DE + COBYLA polish over N_SEEDS derived seeds; returns best."""
    s, delta, init = seed_tuple
    best = (None, float("inf"), 0)
    for r in range(N_SEEDS):
        seed = derive_seed(s, delta, init, r)
        de = differential_evolution(
            energy_fn, [BOX] * dim, seed=seed % (2**32 - 1),
            maxiter=de_maxiter, popsize=de_popsize, tol=1e-7, polish=False)
        x, f, n = _polish(energy_fn, de.x)
        if f < best[1]:
            best = (x, f, int(de.nfev) + n)
    return best


def optimize_warm(energy_fn, x0_free, perturb_pos, seed_tuple, baseline,
                  n_restarts=N_RESTARTS, width=PERTURB):
    """Warm-start restarts plus embedded baseline; argmin wins (clamp).

    x0_free: free-index vector (baseline embedded); perturb_pos: positions
    (into x0_free) re-randomized per restart (the new layer); baseline =
    (x_free, f_base). Returns (x, f, nfev, from_baseline).
    """
    s, delta, init = seed_tuple
    bx, bf = baseline
    cands = [(np.asarray(bx, dtype=float), float(bf), 0, True)]
    pos = np.asarray(list(perturb_pos), dtype=int)
    for r in range(n_restarts):
        rng = np.random.default_rng(derive_seed(s, delta, init, 1000 + r))
        x0 = np.asarray(x0_free, dtype=float).copy()
        x0[pos] = rng.uniform(-width, width, pos.size)
        x, f, n = _polish(energy_fn, np.clip(x0, *BOX))
        cands.append((x, f, n, False))
    return min(cands, key=lambda c: c[1])
