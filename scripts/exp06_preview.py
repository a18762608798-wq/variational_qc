"""exp06 T002 离线预览（零机时）：S03 点位映射 → 批量划分 → 打印账单。

198 组 = 2δ × 33 点(s_idx=1,4,…,97) × 3p；每 3 组一批 → 66 批；
每批任务 = 3 组 × 15 重复 VQE + 2 标定。
产物：data/exp06/batches.json + data/exp06/bill.json（confirmed=false）。
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from exp06_common import (  # noqa: E402
    BATCH_GROUPS,
    DATA_DIR,
    REPS,
    SHOTS,
    read_json,
    write_json,
)

CHAIN_TOP1 = [77, 76, 75, 74, 73, 72, 71, 70]
SUBCHAIN_TOP1 = [84, 83, 82, 69, 70, 71, 72, 73]  # D07c Rank1（Baihua 冠军环内）


def main() -> None:
    s03 = np.load(DATA_DIR.parent / "exp04" / "exp04_S03.npz")
    meta = s03["meta"]
    s_grid = s03["s_grid"]
    sparse = list(range(1, 100, 3))  # s_idx 1-based：1,4,…,97 → 33 点
    assert len(sparse) == 33

    groups = []  # (δ_idx, s_idx, p, a*)
    for r in range(len(meta)):
        di, si, p, a = (int(v) for v in meta[r])
        if si in sparse:
            groups.append({"delta_idx": di, "s_idx": si, "p": p, "a_star": a,
                           "s": float(s_grid[si - 1]),
                           "delta": float(s03["deltas"][di - 1])})
    assert len(groups) == 2 * 33 * 3 == 198, len(groups)
    n_triv = sum(1 for g in groups if g["a_star"] in (1, 3))
    n_topo = sum(1 for g in groups if g["a_star"] == 2)
    assert n_triv + n_topo == 198

    batches = [groups[i:i + BATCH_GROUPS]
               for i in range(0, len(groups), BATCH_GROUPS)]
    assert len(batches) == 66
    n_vqe = 198 * REPS
    n_cal = 66 * 2
    total = n_vqe + n_cal
    print(f"组：{len(groups)}（开链 {n_triv} / 环 {n_topo}）→ {len(batches)} 批")
    print("---- 账单 ----")
    print(f"VQE：{n_vqe} 任务 × {SHOTS} shots")
    print(f"标定：{n_cal} 任务 × {SHOTS} shots")
    print(f"合计：{total} 任务，{total * SHOTS} shots")
    print(f"链 top1：{CHAIN_TOP1}；环内最优 8 子链：{SUBCHAIN_TOP1}（Baihua）")
    write_json(DATA_DIR / "batches.json",
               {"batches": batches, "chain_top1": CHAIN_TOP1,
                "subchain_top1": SUBCHAIN_TOP1, "chip": "Baihua"})
    write_json(DATA_DIR / "bill.json",
               {"n_groups": len(groups), "n_batches": len(batches),
                "vqe_tasks": n_vqe, "calib_tasks": n_cal,
                "total_tasks": total, "shots_per_task": SHOTS,
                "total_shots": total * SHOTS,
                "s03_ref": "data/exp04/exp04_S03.npz",
                "s04_ref": "data/exp05/exp05_S04.npz",
                "confirmed": False,
                "note": "人工确认后置 confirmed=true 才可 submit"})
    print("账单已落盘 data/exp06/bill.json（confirmed=false），待人工确认。")


if __name__ == "__main__":
    main()
