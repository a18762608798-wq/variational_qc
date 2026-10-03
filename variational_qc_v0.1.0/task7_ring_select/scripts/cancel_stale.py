"""一次性运维脚本：取消提速重启前 orphaned 的旧 tid（平台侧仍在排队）。

逻辑：query 两机 Submitted/Pending/Running → 过滤 task7_ring_select 前缀 →
排除 checkpoints 现有 tids（新一批要保留的）→ cancel + delete 其余。
Finished/Failed 不碰（已执行或已终态，取消无意义）。

运行（项目根）：
  $QPY task7_ring_select/scripts/cancel_stale.py [--dry-run]
"""

import argparse
import glob
import json
from pathlib import Path

HERE = Path(__file__).resolve()
TASK6 = HERE.parent.parent

from quark import Task
from qmeas.random import QuarkOptions
from qmeas.random.quark_client import abandon_quark_task, quark_token

PREFIX = "task7_ring_select"
PENDING = ["Submitted", "Pending", "Running", "Transpiled"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    keep = set()
    for p in glob.glob(str(TASK6 / "data" / "checkpoints" / "*.json")):
        with open(p, encoding="utf-8") as f:
            keep.update(json.load(f).get("tids", {}).values())

    tmgr = Task(quark_token(QuarkOptions(chip="Baihua")))
    stale = []
    for chip in ["Baihua", "Shenglian"]:
        for st in PENDING:
            off = 0
            while True:
                r = tmgr.query(chips=chip, status=st, limit=100, offset=off)
                items = r.get("items", [])
                if not items:
                    break
                for it in items:
                    if not str(it.get("taskName", "")).startswith(PREFIX):
                        continue
                    if it.get("taskId") not in keep:
                        stale.append((chip, it.get("status"), it.get("taskId"),
                                      it.get("taskName"), it.get("submitTime")))
                off += 100
                if off > 10000:
                    break
    print(f"checkpoints 现有 tids: {len(keep)}；待取消 stale: {len(stale)}")
    if args.dry_run:
        for row in stale[:10]:
            print("  DRY", row)
        return
    for i, (chip, st, tid, name, ts) in enumerate(stale):
        abandon_quark_task(tmgr, tid)
        if (i + 1) % 200 == 0:
            print(f"  已取消 {i + 1}/{len(stale)}")
    print(f"取消完毕：{len(stale)} 个 stale tids")


if __name__ == "__main__":
    main()
