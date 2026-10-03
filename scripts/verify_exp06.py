"""exp06 T007 生产断言（零机时）：对正式输出全量执行，逐条映射 spec §5。

任一硬门失败即非零退出并指明组；诊断只记录。
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from exp06_common import (  # noqa: E402
    DATA_DIR,
    read_json,
)
from exp06_submit import allowed_edges  # noqa: E402

FAIL: list[str] = []


def hard(cond: bool, msg: str) -> None:
    print(("PASS " if cond else "FAIL ") + msg, flush=True)
    if not cond:
        FAIL.append(msg)


def main() -> None:
    manifest = read_json(DATA_DIR / "exp06_manifest.json")
    hard(manifest.get("schema") == "exp06/v1", "manifest schema exp06/v1")
    bill = read_json(DATA_DIR / "bill.json")
    hard(bool(bill.get("confirmed", False)), "bill 已人工确认")

    d11 = np.load(DATA_DIR / "exp06_D11.npz", allow_pickle=True)
    G = len(d11["s_idx"])
    hard(G == 198, f"D11 组数 {G} == 198")

    s03 = np.load(DATA_DIR.parent / "exp04" / "exp04_S03.npz")
    meta, th = s03["meta"], s03["theta"]
    th_map = {}
    for r in range(len(meta)):
        di, si, p, a = (int(v) for v in meta[r])
        npl = 4 if di == 1 else 8
        th_map[(di, si, p)] = th[r][:npl * p]
    ok_th = True
    for i in range(G):
        key = (int(d11["delta_idx"][i]), int(d11["s_idx"][i]),
               int(d11["p"][i]))
        ref = th_map.get(key)
        if ref is None or not np.allclose(d11["theta"][i][:len(ref)], ref,
                                          equal_nan=True):
            ok_th = False
            print(f"  θ 不一致组 {key}", flush=True)
    hard(ok_th, "θ 与 S03 同组逐元一致")

    # 三件套：counts + 缓解前 + 缓解后（H3）。
    pre_ok = bool(np.all(np.isfinite(d11["spi_pre"]))) and bool(
        np.all(np.isfinite(d11["ostr_pre"])))
    post_ok = bool(np.all(np.isfinite(d11["spi_post"]))) and bool(
        np.all(np.isfinite(d11["ostr_post"])))
    hard(pre_ok and post_ok, "三件套：缓解前/后全有限（counts 见 batches）")
    batches = read_json(DATA_DIR / "batches.json")["batches"]
    counts_ok = True
    for bid, batch in enumerate(batches):
        st = read_json(DATA_DIR / "batches" / f"{bid:03d}" / "state.json")
        for gi in range(len(batch)):
            for r in range(5):
                c = st["counts"].get(f"g{gi}_rep{r}", {})
                if not c or sum(c.values()) == 0:
                    counts_ok = False
        for k in ("cal_zero", "cal_one"):
            if not st["counts"].get(k):
                counts_ok = False
    hard(counts_ok, "三件套：原始 counts 全存档（990 VQE + 132 标定）")

    # S05 同批 + correct 留存 + 转译验路。
    batch_ok, s05_ok, route_ok = True, True, True
    for bid, batch in enumerate(batches):
        st = read_json(DATA_DIR / "batches" / f"{bid:03d}" / "state.json")
        for gi, g in enumerate(batch):
            idx = None
            for i in range(G):
                if (int(d11["delta_idx"][i]) == g["delta_idx"]
                        and int(d11["s_idx"][i]) == g["s_idx"]
                        and int(d11["p"][i]) == g["p"]):
                    idx = i
            if idx is None or int(d11["batch_id"][idx]) != bid:
                batch_ok = False
            for r in range(5):
                key = f"g{gi}_rep{r}"
                sp = st["submit_params"].get(key, {})
                if sp.get("correct") is not False:
                    s05_ok = False
                tr = st["transpile"].get(key, {})
                if not tr.get("in_allowed", False):
                    route_ok = False
                    print(f"  转译验路失败 batch {bid} {key}", flush=True)
                edges = {tuple(e) for e in tr.get("cz_edges", [])}
                if not edges <= allowed_edges(g["a_star"]):
                    route_ok = False
                    print(f"  边集越界 batch {bid} {key}", flush=True)
    hard(batch_ok, "S05 批次 id 同批（3 组一批）")
    hard(s05_ok, "提交参数 correct=False 留存可查")
    hard(route_ok, "转译验路断言：CZ 边集 ⊆ 允许集")

    # 对账：无 invalid 残留。
    import glob as _glob
    inv = _glob.glob(str(DATA_DIR / "batches" / "*" / "invalid.json"))
    hard(not inv, "无 invalid 残留标记")

    # 诊断（只记录）。
    print(f"诊断：缓解前后 |ΔS(π)| 均值 = "
          f"{np.nanmean(np.abs(d11['spi_post'] - d11['spi_pre'])):.4f}")
    for di in (1, 2):
        for p in (1, 2, 3):
            m = (d11["delta_idx"] == di) & (d11["p"] == p)
            sd = d11["spi_std"][m]
            med = np.median(sd)
            flag = np.nonzero(sd > 5 * med)[0]
            if len(flag):
                print(f"诊断：δ{di} p{p} 离散度异常组（>5×中位数）{len(flag)} 个")
    print("诊断：D12 真机–模拟机趋势一致性请目检出图")

    if FAIL:
        print(f"VERIFY-EXP06-FAIL：{len(FAIL)} 项", flush=True)
        raise SystemExit(1)
    print("VERIFY-EXP06-OK", flush=True)


if __name__ == "__main__":
    main()
