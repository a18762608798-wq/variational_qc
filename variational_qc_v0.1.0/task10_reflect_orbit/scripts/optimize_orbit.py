#!/usr/bin/env python
"""task10 orbit 两步优化（depth1）与 warm-start 优化（depth>=2）.

- depth1 two_step：differential_evolution（有界 [0,2pi)^{8n}，每层 8 参数）+ COBYLA polish；
- depth>=2 warm_start：浅层最优垫底 + 均匀微扰 + COBYLA polish；
- seed 按坐标确定性派生（hashlib，跨进程稳定），保证同配置两次逐位一致；
- 预算由 pilot 结论经参数传入，此处只给占位默认（8 维 pilot 起点：light 30/15/300）。
"""

import hashlib

import numpy as np
from scipy.optimize import differential_evolution, minimize

from ansatz_orbit import build_vqe_circuit, statevector_of, expectation

DEFAULT_BUDGET_D1 = {
    "de_maxiter": 30,
    "de_popsize": 15,
    "de_seed": 0,  # 被派生 seed 覆盖，仅作回落
    "cobyla_maxiter": 300,
}

DEFAULTS_WARM = {
    "perturb_scale": 0.3,  # rad，均匀微扰半宽（pilot 定）
    "cobyla_maxiter": 500,
}


def _stable_seed(*parts) -> int:
    """跨进程稳定的 31-bit seed（不用内置 hash：str hash 受 PYTHONHASHSEED salt 影响）。"""
    blob = "|".join(repr(p) for p in parts).encode()
    return int(hashlib.sha256(blob).hexdigest()[:8], 16) % (2**31)


def derive_seed_d1(base: int, s: float, delta: float, init_name: str,
                   restart: int = 0) -> int:
    """depth1 坐标确定性 seed（32 bit）。"""
    return _stable_seed(base, round(float(s), 8), round(float(delta), 8),
                        init_name, int(restart))


def derive_seed(base: int, depth: int, s: float, delta: float, init_name: str,
                restart: int = 0) -> int:
    """depth>=2 坐标确定性 seed（32 bit）。"""
    return _stable_seed(base, int(depth), round(float(s), 8), round(float(delta), 8),
                        init_name, int(restart))


def make_objective(init_name: str, H: np.ndarray, n_layers: int):
    def fun(theta):
        psi = statevector_of(build_vqe_circuit(init_name, theta, n_layers=n_layers))
        return expectation(psi, H)

    return fun


def two_step(
    init_name: str,
    H: np.ndarray,
    seed: int,
    budget: dict | None = None,
    n_layers: int = 1,
) -> dict:
    """返回 {'global_x','global_fun','x','fun'}（fun 均为 min H，绝对能量）。"""
    b = dict(DEFAULT_BUDGET_D1)
    if budget:
        b.update(budget)
    n = 8 * n_layers
    fun = make_objective(init_name, H, n_layers)
    de = differential_evolution(
        fun,
        bounds=[(0.0, 2 * np.pi)] * n,
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
    scale = DEFAULTS_WARM["perturb_scale"] if perturb_scale is None else perturb_scale
    maxiter = DEFAULTS_WARM["cobyla_maxiter"] if cobyla_maxiter is None else cobyla_maxiter
    base = np.asarray(base_theta, dtype=float)
    assert base.size == 8 * (n_layers - 1), (
        f"orbit warm-start dim mismatch: base has {base.size} params, "
        f"depth {n_layers} needs {8 * (n_layers - 1)} (uniform thetas must NOT be reused)")
    rng = np.random.default_rng(int(seed))
    pad = np.zeros(8) if scale == 0 else rng.uniform(-scale, scale, 8)
    x0 = np.concatenate([base, pad])
    fun = make_objective(init_name, H, n_layers)
    loc = minimize(fun, x0=np.asarray(x0), method="COBYLA",
                   options={"maxiter": int(maxiter)})
    return {"x": np.asarray(loc.x), "fun": float(loc.fun)}
