"""Schema-versioned per-point persistence. Schema exp01-04/v1.

Atomic tmp+rename checkpoint; idempotent reruns (III.7): same coords +
same data -> path returned; same coords + different data -> ValueError
(no silent incompatible overwrite). Caller-side mutation never leaks back:
fresh objects on every load (FR-006 raw immutability).
"""

import hashlib
import json
import os

import numpy as np

SCHEMA = "exp01-04/v1"
COORD_KEYS = {"L", "s", "delta", "p", "branch", "init", "restart", "seed", "q", "exp"}


def _canon(obj):
    if isinstance(obj, dict):
        return {k: _canon(obj[k]) for k in sorted(obj)}
    if isinstance(obj, (np.ndarray,)):
        return {"__ndarray__": True, "data": obj.tolist()}
    if isinstance(obj, (np.integer, np.floating, np.bool_)):
        return obj.item()
    if isinstance(obj, (list, tuple)):
        return [_canon(x) for x in obj]
    return obj


def _restore(obj):
    if isinstance(obj, dict) and obj.get("__ndarray__"):
        return np.array(obj["data"])
    if isinstance(obj, dict):
        return {k: _restore(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_restore(x) for x in obj]
    return obj


def _split(rec):
    coords = {k: v for k, v in rec.items() if k in COORD_KEYS}
    return coords


def config_hash(rec):
    canon = json.dumps(_canon(_split(rec)), sort_keys=True)
    return hashlib.sha256(canon.encode()).hexdigest()[:16]


def _path(data_dir, exp, rec):
    import pathlib

    return pathlib.Path(data_dir) / f"{exp}_{config_hash(rec)}.npz"


def _pack(rec):
    flat = {}
    for k, v in rec.items():
        flat[k] = np.asarray(v) if not isinstance(v, str) else np.array(v)
    return flat


def _records_equal(a, b, rtol=1e-9, atol=1e-12):
    """Scientific equality: floats compare with tolerance.

    Rationale: sparse ARPACK starts from a random vector, so recomputed
    energies/observables differ at ~1e-14 even for identical inputs.
    Bitwise identity would turn every resume/repair into a false conflict.
    """
    if set(a) != set(b):
        return False
    for k in a:
        va, vb = a[k], b[k]
        if isinstance(va, np.ndarray) or isinstance(vb, np.ndarray):
            aa = np.asarray(va)
            bb = np.asarray(vb)
            if aa.shape != bb.shape or aa.dtype.kind != bb.dtype.kind:
                return False
            if aa.dtype.kind in "fc":
                if not np.allclose(aa, bb, rtol=rtol, atol=atol, equal_nan=True):
                    return False
            elif not np.array_equal(aa, bb):
                return False
        elif isinstance(va, float) or isinstance(vb, float):
            if not np.isclose(va, vb, rtol=rtol, atol=atol, equal_nan=True):
                return False
        elif va != vb:
            return False
    return True


def save_point(data_dir, exp, rec):
    """Atomic save; idempotent on identical data; ValueError on conflict."""
    import pathlib

    path = _path(data_dir, exp, rec)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if _records_equal(load_point(path), rec):
            return path
        raise ValueError(f"incompatible result for {path}; refusing overwrite")
    tmp = path.with_name(path.name + ".part")
    with open(tmp, "wb") as fh:
        np.savez(fh, **_pack(rec))
    os.replace(tmp, path)
    return path


def load_point(path):
    with np.load(path, allow_pickle=False) as z:
        out = {}
        for k in z.files:
            v = z[k]
            out[k] = v.item() if v.shape == () else v.copy()
    return out


def point_exists(data_dir, exp, rec):
    return _path(data_dir, exp, rec).exists()


def iter_points(data_dir, exp):
    """Yield saved records for experiment `exp` (glob *.npz by prefix)."""
    import pathlib

    for path in sorted(pathlib.Path(data_dir).glob(f"{exp}_*.npz")):
        yield load_point(path)


def write_manifest(data_dir, exp, meta):
    import pathlib

    name = f"{exp}_manifest.json"
    _dir = pathlib.Path(data_dir)
    _dir.mkdir(parents=True, exist_ok=True)
    (_dir / name).write_text(json.dumps(meta, indent=2))
    return name
