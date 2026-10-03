#!/usr/bin/env python
"""task8 计数分析：X/Y/Z 三基直方图 -> H 期望、Q、P 两项。

端序：qiskit/quark bitstring 最左字符为最高位经典比特；
measure(Qj -> Cj) 下反转后第 j 位即逻辑比特 j 的值（qmeas random/io.py 同款）。
z = +1（'0'）/ -1（'1'）；x/y 同理（已转基矢，读 Z 值即可）。
"""

L = 8
D = L // 2 - 1  # 3


def _shots(hist) -> list[list[int]]:
    """直方图 -> 逐 shot 逻辑比特值列表（0/1），顺序无关（只求平均）。"""
    out = []
    for bits, c in hist.items():
        v = [(0 if ch == "0" else 1) for ch in bits[::-1][:L]]
        out += [v] * int(c)
    return out


def H_from_counts(hx, hy, hz, s: float, delta: float) -> float:
    """<H> = Σ键 w*(jxx*(<XX>+<YY>) + jz*<ZZ>)，各基独立平均后合成。
    intra/inter 为逻辑键（sym-topo 环上与链相同：键只跑逻辑对）。"""
    from math import exp
    intra = [(0, 1), (2, 3), (4, 5), (6, 7)]
    inter = [(1, 2), (3, 4), (5, 6)]
    jxx, jz = exp(-delta), exp(delta)

    def corr(hist):
        shots = _shots(hist)
        n = len(shots)
        c = {}
        for v in shots:
            z = [1.0 - 2.0 * b for b in v]
            for k, l in intra + inter:
                c[(k, l)] = c.get((k, l), 0.0) + z[k] * z[l]
        return {k: v / n for k, v in c.items()}

    cx, cy, cz = corr(hx), corr(hy), corr(hz)
    e = 0.0
    for bonds, w in ((intra, 1 - s), (inter, s)):
        for k, l in bonds:
            e += w * (jxx * (cx[(k, l)] + cy[(k, l)]) + jz * cz[(k, l)])
    return e


def Q_from_counts(hz) -> tuple[float, float, float]:
    """返回 (Q, O_norm, S_norm)，与 task3 observables.py 同定义，逐 shot 平均。"""
    shots = _shots(hz)
    n = len(shots)
    to, ts = 0.0, 0.0
    for v in shots:
        z = [1.0 - 2.0 * b for b in v]
        mid = 1.0
        for l in range(1, D):
            mid *= -(z[2 * l] * z[2 * l + 1])
        ostr = (z[0] + z[1]) * mid * (z[2 * D] + z[2 * D + 1])
        to += -ostr
        s_pi = sum(
            ((-1.0) ** (i - j)) * z[i] * z[j]
            for i in range(L) for j in range(L)
        ) / L
        ts += s_pi / 8
    o_norm, s_norm = to / n, ts / n
    q = (1 - 2 * o_norm) - (4.0 / 3.0) * (s_norm - 0.25)
    return q, o_norm, s_norm


def P_terms_from_counts(hz, hx) -> tuple[float, float]:
    """返回 (<Z_tot^2>, <prod X>)，只记录不断言。"""
    sz, sx = _shots(hz), _shots(hx)
    zt2 = sum(sum(1.0 - 2.0 * b for b in v) ** 2 for v in sz) / len(sz)
    px = sum((-1) ** sum(v) for v in sx) / len(sx)
    return zt2, px
