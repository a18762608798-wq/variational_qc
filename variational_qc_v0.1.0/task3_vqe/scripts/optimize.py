#!/usr/bin/env python
"""task3 两步优化：differential_evolution（有界 [0,2pi)^4）+ COBYLA polish.

seed 按 (s, delta, init, restart) 确定性派生，保证同配置两次逐位一致。
预算（maxiter/popsize/tol）由 pilot 结论经 --config 传入，此处只给占位默认。
"""

import numpy as np
from scipy.optimize import differential_evolution, minimize

from ansatz import build_vqe_circuit, statevector_of, expectation

BOUNDS = [(0.0, 2 * np.pi)] * 4

DEFAULT_BUDGET = {
    "de_maxiter": 50,
    "de_popsize": 10,
    "de_seed": 0,  # 被派生 seed 覆盖，仅作回落
    "cobyla_maxiter": 500,
}


def derive_seed(base: int, s: float, delta: float, init_name: str, restart: int = 0) -> int:
    """坐标确定性 seed（32 bit）。"""
    h = hash((base, round(float(s), 8), round(float(delta), 8), init_name, int(restart)))
    return h % (2**31)


def make_objective(init_name: str, H: np.ndarray):
    def fun(theta):
        psi = statevector_of(build_vqe_circuit(init_name, theta))
        return expectation(psi, H)

    return fun


def two_step(
    init_name: str,
    H: np.ndarray,
    seed: int,
    budget: dict | None = None,
) -> dict:
    """返回 {'global_x','global_fun','x','fun'}（fun 均为 min H，绝对能量）。"""
    b = dict(DEFAULT_BUDGET)
    if budget:
        b.update(budget)
    fun = make_objective(init_name, H)
    de = differential_evolution(
        fun,
        bounds=BOUNDS,
        maxiter=int(b["de_maxiter"]),
        popsize=int(b["de_popsize"]),
        seed=int(seed),
        polish=False,
        updating="deferred",
        workers=1,
    )
    loc = minimize(
        fun,
        x0=np.asarray(de.x),
        method="COBYLA",
        options={"maxiter": int(b["cobyla_maxiter"])},
    )
    return {
        "global_x": np.asarray(de.x),
        "global_fun": float(de.fun),
        "x": np.asarray(loc.x),
        "fun": float(loc.fun),
    }
