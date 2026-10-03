"""v2 record reader for plotting (schema exp01-04/v2).

v2 layout per point: <exp>_<hash>.npz (numeric arrays, NPZ.jl) +
<exp>_<hash>.json (scalars/meta/strings, JSON3). Complex arrays are stored
as [re..., im...] with a "__complex__<key>" length flag in the sidecar.
The archived `ssh_xxz.io.store` (v1 layout) is NEVER used here.
"""

import json

import numpy as np


def load_point(npz_path):
    import pathlib

    npz_path = str(npz_path)
    js_path = npz_path[:-4] + ".json" if npz_path.endswith(".npz") else npz_path + ".json"
    with np.load(npz_path, allow_pickle=False) as z:
        raw = {k: z[k] for k in z.files}
    with open(js_path) as fh:
        meta = json.load(fh)
    out = {}
    for k, v in raw.items():
        flag = f"__complex__{k}"
        if k == "__payload_empty__":
            continue
        if flag in meta:
            n = int(meta.pop(flag))
            arr = np.asarray(v).ravel()
            out[k] = arr[:n] + 1j * arr[n:]
        else:
            out[k] = v
    for k, v in meta.items():
        out[k] = v
    return out


def iter_points(data_dir, exp):
    import pathlib

    out = []
    for f in sorted(pathlib.Path(data_dir).glob(f"{exp}_*.npz")):
        try:
            out.append(load_point(f))
        except FileNotFoundError:
            continue  # sidecar missing -> skip, never crash a rebuild
    return out


def iter_reference(data_dir):
    """exp03 ground-truth records (replaces experiments.exp03_reference)."""
    return [r for r in iter_points(data_dir, "exp03") if r.get("status") == "ok"]


def read_manifest(data_dir, exp):
    import pathlib

    with open(pathlib.Path(data_dir) / f"{exp}_manifest.json") as fh:
        return json.load(fh)
