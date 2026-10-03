#!/usr/bin/env python
"""task3 观测量：O_str / S(pi) / Q 的 LSB 序 Z-对角矩阵（doc/model/operator.md）.

- O_str(d=L/2-1=3) = (Z0+Z1)(-Z2 Z3)(-Z4 Z5)(Z6+Z7)，起点固定格点 0,1；
- S(pi) = (1/L) Σ_ij (-1)^{i-j} Zi Zj，L=8；
- 归一：O_norm = -O_str，S_norm = S(pi)/8；
- Q = (1-2*O_norm) - (4/3)*(S_norm-1/4)。
"""

import numpy as np

L = 8
D = L // 2 - 1  # 3


def _zvals() -> np.ndarray:
    """各计算基矢的 z_j 向量，形状 (256, 8)，LSB 序（格点 j = bit j）。"""
    idx = np.arange(2**L)
    bits = ((idx[:, None] >> np.arange(L)) & 1).astype(float)
    return 1.0 - 2.0 * bits  # |0> -> +1, |1> -> -1


def O_str_diag() -> np.ndarray:
    z = _zvals()
    mid = np.ones(2**L)
    for l in range(1, D):
        mid *= -(z[:, 2 * l] * z[:, 2 * l + 1])
    return (z[:, 0] + z[:, 1]) * mid * (z[:, 2 * D] + z[:, 2 * D + 1])


def S_pi_diag() -> np.ndarray:
    z = _zvals()
    phase = (-1.0) ** (np.arange(L)[:, None] - np.arange(L)[None, :])
    return np.einsum("ki,ij,kj->k", z, phase, z) / L


def normalized(psi: np.ndarray, diag: np.ndarray, scale) -> float:
    return float(np.real(np.vdot(psi, diag * psi))) * scale


def Q_of_state(psi: np.ndarray) -> tuple[float, float, float]:
    """返回 (Q, O_str_norm, S_pi_norm)。"""
    o_norm = normalized(psi, O_str_diag(), -1.0)
    s_norm = normalized(psi, S_pi_diag(), 1.0 / 8)
    q = (1 - 2 * o_norm) - (4.0 / 3.0) * (s_norm - 0.25)
    return q, o_norm, s_norm
