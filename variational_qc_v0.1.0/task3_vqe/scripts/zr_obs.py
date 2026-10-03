#!/usr/bin/env python
"""task3 ZR 观测量：tilde_Z_R 的 LSB 序实现（对标 shared/numerics/zr.jl）.

- I = {2,3,4,5}（0-indexed；Julia I_ALL=(3,4,5,6) 1-indexed），
  I1 = {2,3}，I2 = {4,5}；
- R_I 为 I 上 4 比特逆序置换；
- Z_R = Tr(rho_I R)，tilde = Z_R / sqrt((p1+p2)/2)。
"""

import numpy as np

L = 8
SUB = (2, 3, 4, 5)  # I 的格点，顺序固定（首位为"MSB"侧，仅需自洽）
SUB1 = (2, 3)
SUB2 = (4, 5)
COMP = tuple(j for j in range(L) if j not in SUB)
COMP1 = tuple(j for j in range(L) if j not in SUB1)
COMP2 = tuple(j for j in range(L) if j not in SUB2)


def _embed(sub: tuple, x: int, comp: tuple, c: int) -> int:
    """把子系统比特 x 与环境比特 c 拼回全链整数索引（LSB 序）。"""
    idx = 0
    for k, j in enumerate(sub):
        idx |= ((x >> (len(sub) - 1 - k)) & 1) << j
    for k, j in enumerate(comp):
        idx |= ((c >> (len(comp) - 1 - k)) & 1) << j
    return idx


def _rho(psi: np.ndarray, sub: tuple, comp: tuple) -> np.ndarray:
    n = 2 ** len(sub)
    m = 2 ** len(comp)
    full = np.empty((n, m), dtype=complex)
    for x in range(n):
        for c in range(m):
            full[x, c] = psi[_embed(sub, x, comp, c)]
    return full @ full.conj().T


def _rev4(x: int) -> int:
    return (((x & 1) << 3) | ((x & 2) << 1) | ((x & 4) >> 1) | ((x & 8) >> 3))


def tilde_ZR_of_state(psi: np.ndarray) -> tuple[float, float, float, float]:
    """返回 (tilde, ZR, purity_I1, purity_I2)。分母 <= 0 时抛错。"""
    rhoI = _rho(psi, SUB, COMP)
    R = np.zeros((16, 16))
    for b in range(16):
        R[_rev4(b), b] = 1.0
    zr = float(np.real(np.trace(rhoI @ R)))
    p1 = float(np.real(np.trace(_rho(psi, SUB1, COMP1) @ _rho(psi, SUB1, COMP1))))
    p2 = float(np.real(np.trace(_rho(psi, SUB2, COMP2) @ _rho(psi, SUB2, COMP2))))
    denom = np.sqrt((p1 + p2) / 2)
    if denom <= 0:
        raise ValueError(f"tilde_ZR: non-positive purity denominator (p1={p1}, p2={p2})")
    return zr / denom, zr, p1, p2
