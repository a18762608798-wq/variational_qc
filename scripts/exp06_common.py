"""exp06 共享常量与落盘 helpers（零真机调用）。"""

from __future__ import annotations

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "exp06"
FIGS_DIR = Path(__file__).resolve().parent.parent / "figs" / "exp06"

MASTER_SEED = 20261004
SHOTS = 2048
REPS = 5
BATCH_GROUPS = 3


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)
