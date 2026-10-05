"""exp06 T004 组装（零机时）：batches → S05 缓解 → 观测量 → D08 + manifest。

mitigate_counts / minmax_norm / obs_from_probs / obs_basis_arrays /
pooled_shot_se / pick_pstar / build_manifest 可被
test_exp06_local.py 直接 import（零真机调用）。
qiskit counts 键约定：左起最高位 = qubit L-1（大端字符串），整数值按小端解。
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from exp06_common import DATA_DIR, read_json, write_json  # noqa: E402

L = 8
SCHEMA = "exp06/v1"


def mitigate_counts(counts: dict[str, int], Ms: list, n: int = L) -> np.ndarray:
    """逐比特独立缓解：p_mit = (⊗_q M_q⁻¹) p_meas，负值截零重归一。"""
    Minvs = [np.linalg.inv(np.asarray(M, dtype=float)) for M in Ms]
    K = Minvs[n - 1]
    for q in range(n - 2, -1, -1):
        K = np.kron(K, Minvs[q])
    p = np.zeros(1 << n)
    for key, c in counts.items():
        p[int(key, 2)] += c
    p = K @ p
    p = np.clip(p, 0, None)
    s = p.sum()
    return p / s if s > 0 else p


def obs_from_probs(probs: np.ndarray) -> tuple[float, float]:
    """S(π) 交错和 + string 对角加权（定义同 Exp02，只读复刻）。"""
    o_spi, o_ostr = obs_basis_arrays()
    return float(np.asarray(probs) @ o_spi), float(np.asarray(probs) @ o_ostr)


def obs_basis_arrays() -> tuple[np.ndarray, np.ndarray]:
    """每基矢观测量值 o_spi[b]、o_ostr[b]（L=8，256 态；与上式同定义）。"""
    o_spi = np.zeros(1 << L)
    o_ostr = np.zeros(1 << L)
    for b in range(1 << L):
        z = [1 - 2 * ((b >> q) & 1) for q in range(L)]
        s = 0.0
        for i in range(L):
            for j in range(L):
                s += ((-1) ** (i - j)) * z[i] * z[j]
        o_spi[b] = s / L
        o = 0.0
        for a in (0, 1):
            for c in (6, 7):
                o += z[a] * z[2] * z[3] * z[4] * z[5] * z[c]
        o_ostr[b] = o
    return o_spi, o_ostr


def minmax_norm(x: np.ndarray) -> np.ndarray:
    lo, hi = float(np.min(x)), float(np.max(x))
    if hi == lo:
        return np.zeros_like(x, dtype=float)
    return (np.asarray(x, dtype=float) - lo) / (hi - lo)


def pooled_shot_se(sum_p: np.ndarray, n: int, obs: np.ndarray,
                   shots: int) -> tuple[float, float]:
    """全并 multinomial 解析 SE：w̄ = 缓解后分布按批平均（sum_p 已累加），
    mu = Σw̄o，SE² = (Σw̄o² − mu²)/N，N = n×shots。n 为有效批数。
    """
    w = sum_p / n
    mu = float(w @ obs)
    var = max(float(w @ (obs * obs)) - mu * mu, 0.0)
    return mu, math.sqrt(var / (n * shots))


def pick_pstar(hw_n: np.ndarray, ref_n: np.ndarray, s_idx: np.ndarray,
               p_arr: np.ndarray, panel: np.ndarray) -> int:
    """p*（spec POST-002）：归一化后真机 p 层 vs 归一化模拟机同层 p 曲线，
    33 点平均 |A_p−B_p| 最小；按 s_idx 对齐；并列取小 p。
    输入须为同面板归一化数组（含 NaN padding 区，掩码内须有限）。
    """
    best, best_v = 1, float("inf")
    for p in (1, 2, 3):
        mp = panel & (p_arr == p)
        o = np.argsort(s_idx[mp])
        a = hw_n[mp][o]
        b = ref_n[mp][o]
        v = float(np.mean(np.abs(a - b)))
        if v < best_v:
            best, best_v = p, v
    return best


MANIFEST_KEYS = {"schema", "s03_ref", "s04_ref", "s06_ref", "points",
                 "shots", "reps", "batch_size", "basis_gates",
                 "optimization_level", "correct", "p_star", "stderr_def",
                 "norm_intervals", "toolchain", "python"}


def build_manifest(**kw) -> dict:
    m = {"schema": SCHEMA}
    m.update(kw)
    missing = MANIFEST_KEYS - set(m)
    if missing:
        raise ValueError(f"manifest 缺字段 {missing}")
    return m


def pkg_versions() -> dict:
    import importlib.metadata as md

    def ver(pkg: str) -> str:
        try:
            return md.version(pkg)
        except Exception:
            return "unknown"

    import qmeas as _qmeas
    root = Path(_qmeas.__file__).resolve().parent.parent.parent
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                                capture_output=True, text=True,
                                cwd=root).stdout.strip() or "unknown"
    except Exception:
        commit = "unknown"
    return {"qmeas": ver("qmeas"), "qmeas_git": commit,
            "quarkstudio": ver("quarkstudio"),
            "quarkcircuit": ver("quarkcircuit"),
            "qiskit": ver("qiskit"), "qiskit_aer": ver("qiskit-aer")}


def group_Ms(cal_counts: dict, phys: list[int]) -> list:
    """一批的 S05：全 0 / 全 X 电路给出 8 比特各自 2×2 矩阵。

    counts 键比特位 ↔ target_qubits 位置对应（qiskit 大端字符串）。
    M[q] = [[P(0|0), P(0|1)], [P(1|0), P(1|1)]]。
    """
    n = len(phys)
    c0, c1 = cal_counts["cal_zero"], cal_counts["cal_one"]
    s0 = sum(c0.values()) or 1
    s1 = sum(c1.values()) or 1
    Ms = []
    for i in range(n):
        q = n - 1 - i  # 字符串位 i ↔ qubit q
        p0m = sum(c for k, c in c0.items() if k[i] == "0") / s0
        p1m = sum(c for k, c in c1.items() if k[i] == "1") / s1
        Ms.append([[p0m, 1 - p1m], [1 - p0m, p1m]])
    return Ms


def main() -> None:
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from exp06_common import REPS as _REPS, SHOTS as _SHOTS  # noqa: E402

    info = read_json(DATA_DIR / "batches.json")
    batches = info["batches"]
    s03 = np.load(DATA_DIR.parent / "exp04" / "exp04_S03.npz")
    meta, th = s03["meta"], s03["theta"]
    theta_map: dict = {}
    for r in range(len(meta)):
        di, si, p, a = (int(v) for v in meta[r])
        npl = 4 if di == 1 else 8
        theta_map[(di, si, p)] = (th[r][:npl * p], a)
    phys_of = {1: info["chain_top1"], 3: info["chain_top1"],
               2: info["subchain_top1"]}

    G = 198
    assert sum(len(b) for b in batches) == G
    order = [g for b in batches for g in b]
    O_SPI, O_OSTR = obs_basis_arrays()
    spi_post = np.full((G, _REPS), np.nan)
    ostr_post = np.full((G, _REPS), np.nan)
    spi_pre = np.full((G, _REPS), np.nan)
    ostr_pre = np.full((G, _REPS), np.nan)
    sum_p = np.zeros((G, 1 << L))
    rep_counts = []
    Ms_all = []
    batch_id = np.zeros(G, dtype=np.int64)
    for bid, batch in enumerate(batches):
        st = read_json(DATA_DIR / "batches" / f"{bid:03d}" / "state.json")
        first_a = batch[0]["a_star"]
        Ms = group_Ms({k: st["counts"][k] for k in ("cal_zero", "cal_one")},
                      phys_of[first_a])
        Ms_all.append(Ms)
        for gi, g in enumerate(batch):
            idx = order.index(g)
            batch_id[idx] = bid
            for r in range(_REPS):
                key = f"g{gi}_rep{r}"
                counts = st["counts"][key]
                rep_counts.append(counts)
                pre = obs_from_probs(_probs_of_counts(counts))
                p_mit = mitigate_counts(counts, Ms)
                post = (float(p_mit @ O_SPI), float(p_mit @ O_OSTR))
                sum_p[idx] += p_mit
                spi_pre[idx, r], ostr_pre[idx, r] = pre
                spi_post[idx, r], ostr_post[idx, r] = post

    arr = lambda k: np.array([g[k] for g in order])
    di_arr = arr("delta_idx")
    si_arr = arr("s_idx")
    p_arr = arr("p")
    a_arr = arr("a_star")
    th_full = np.full((G, 24), np.nan)
    for idx, g in enumerate(order):
        th, _ = theta_map[(g["delta_idx"], g["s_idx"], g["p"])]
        th_full[idx, :len(th)] = th
    # 全并解析误差棒：5 批缓解后分布平均 + multinomial SE（N=批数×shots）。
    mu_spi = np.full(G, np.nan)
    se_spi = np.full(G, np.nan)
    mu_ostr = np.full(G, np.nan)
    se_ostr = np.full(G, np.nan)
    for idx in range(G):
        n = int(np.sum(np.isfinite(spi_post[idx])))
        if n > 0:
            mu_spi[idx], se_spi[idx] = pooled_shot_se(
                sum_p[idx], n, O_SPI, _SHOTS)
            mu_ostr[idx], se_ostr[idx] = pooled_shot_se(
                sum_p[idx], n, O_OSTR, _SHOTS)
    # D08 叠放：S06 对应组引用 + 每面板 p* + 各自 min-max 归一化（33 点/面板）。
    s06 = np.load(DATA_DIR.parent / "exp04" / "exp04_S06.npz")
    ref_spi, ref_ostr = [], []
    for g in order:
        tag = "d0" if g["delta_idx"] == 1 else "d085"
        ref_spi.append(s06[f"{tag}_spi"][g["s_idx"] - 1, g["p"] - 1])
        ref_ostr.append(s06[f"{tag}_ostr"][g["s_idx"] - 1, g["p"] - 1])
    ref_spi = np.array(ref_spi)
    ref_ostr = np.array(ref_ostr)
    hw_spi = np.nanmean(spi_post, axis=1)
    hw_ostr = np.nanmean(ostr_post, axis=1)
    intervals = {}
    norm = {}
    p_star = {}
    for (di, name, hw, rf, d08) in ((1, "spi", hw_spi, ref_spi, "D08a"),
                                    (1, "ostr", hw_ostr, ref_ostr, "D08b"),
                                    (2, "spi", hw_spi, ref_spi, "D08c"),
                                    (2, "ostr", hw_ostr, ref_ostr, "D08d")):
        m = di_arr == di
        lo_h, hi_h = float(np.min(hw[m])), float(np.max(hw[m]))
        lo_r, hi_r = float(np.min(rf[m])), float(np.max(rf[m]))
        intervals[f"d{di}_{name}"] = {"hw": [lo_h, hi_h],
                                      "ref": [lo_r, hi_r]}
        full_h = np.full(G, np.nan)
        full_r = np.full(G, np.nan)
        full_h[m] = minmax_norm(hw[m])
        full_r[m] = minmax_norm(rf[m])
        norm[f"d{di}_{name}_hw"] = full_h
        norm[f"d{di}_{name}_ref"] = full_r
        p_star[d08] = pick_pstar(norm[f"d{di}_{name}_hw"],
                                 norm[f"d{di}_{name}_ref"],
                                 si_arr, p_arr, m)
    np.savez(DATA_DIR / "exp06_D08.npz",
             delta_idx=di_arr, s_idx=si_arr, p=p_arr, a_star=a_arr,
             s_grid=np.array([g["s"] for g in order]),
             deltas=np.array([g["delta"] for g in order]),
             theta=th_full, batch_id=batch_id,
             spi_mean=mu_spi, spi_std=se_spi,
             ostr_mean=mu_ostr, ostr_std=se_ostr,
             spi_pre=spi_pre, ostr_pre=ostr_pre,
             spi_post=spi_post, ostr_post=ostr_post,
             s05=np.array(Ms_all),
             ref_spi=ref_spi, ref_ostr=ref_ostr,
             hw_spi=hw_spi, hw_ostr=hw_ostr,
             p_star=np.array([p_star[k] for k in ("D08a", "D08b",
                                                 "D08c", "D08d")],
                             dtype=np.int64),
             **norm)

    manifest = build_manifest(
        s03_ref="data/exp04/exp04_S03.npz",
        s04_ref="data/exp05/exp05_S04.npz",
        s06_ref="data/exp04/exp04_S06.npz",
        points={"n_groups": G, "n_batches": len(batches),
                "sparse": "s_idx=1,4,…,97", "p_levels": [1, 2, 3]},
        shots=_SHOTS, reps=_REPS, batch_size=3,
        basis_gates=["rz", "rx", "ry", "cz"], optimization_level=3,
        correct=False, p_star=p_star, norm_intervals=intervals,
        stderr_def="pooled-multinomial-analytic",
        toolchain=pkg_versions(), python=sys.executable)
    write_json(DATA_DIR / "exp06_manifest.json", manifest)
    print(f"D08 真机图层 {G} 组，p*={p_star}，归一化 4 面板，manifest 落盘")


def _probs_of_counts(counts: dict) -> np.ndarray:
    p = np.zeros(256)
    for key, c in counts.items():
        p[int(key, 2)] += c
    s = p.sum()
    return p / s if s > 0 else p


if __name__ == "__main__":
    main()
