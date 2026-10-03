#!/usr/bin/env python
"""task4 warm-start 优化：浅层最优垫底 + 微扰 + COBYLA polish.

- 起点 x0 = base_theta（浅层最优）垫底 + 均匀微扰；
- seed 按 (depth, s, delta, init, restart) 确定性派生；
- 微扰尺度与 polish 预算由 pilot 结论经配置传入，此处只给占位默认。
"""

import numpy as np
from scipy.optimize import minimize

from ansatz import build_vqe_circuit, statevector_of, expectation

DEFAULTS = {
    "perturb_scale": 0.2,  # rad，均匀微扰半宽（pilot 定）
    "cobyla_maxiter": 500,
}


def derive_seed(base: int, depth: int, s: float, delta: float, init_name: str,
                restart: int = 0) -> int:
    """坐标确定性 seed（32 bit）。"""
    h = hash((base, int(depth), round(float(s), 8), round(float(delta), 8),
              init_name, int(restart)))
    return h % (2**31)


def make_objective(init_name: str, H: np.ndarray, n_layers: int):
    def fun(theta):
        psi = statevector_of(build_vqe_circuit(init_name, theta, n_layers=n_layers))
        return expectation(psi, H)

    return fun


def warm_start(
    init_name: str,
    H: np.ndarray,
    n_layers: int,
    base_theta,
    seed: int,
    perturb_scale: float | None = None,
    cobyla_maxiter: int | None = None,
) -> dict:
    """返回 {'x','fun'}（fun 为 min H，绝对能量）。"""
    scale = DEFAULTS["perturb_scale"] if perturb_scale is None else perturb_scale
    maxiter = DEFAULTS["cobyla_maxiter"] if cobyla_maxiter is None else cobyla_maxiter
    base = np.asarray(base_theta, dtype=float)
    assert base.size == 4 * (n_layers - 1), (base.size, n_layers)
    rng = np.random.default_rng(int(seed))
    pad = np.zeros(4) if scale == 0 else rng.uniform(-scale, scale, 4)
    x0 = np.concatenate([base, pad])
    fun = make_objective(init_name, H, n_layers)
    loc = minimize(fun, x0=np.asarray(x0), method="COBYLA",
                   options={"maxiter": int(maxiter)})
    return {"x": np.asarray(loc.x), "fun": float(loc.fun)}
