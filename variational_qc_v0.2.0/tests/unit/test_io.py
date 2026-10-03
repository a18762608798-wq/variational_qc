"""T011: NPZ schema + atomic write + hash idempotency + raw immutability. FAIL-first."""

import json

import numpy as np

from ssh_xxz.io.store import config_hash, load_point, point_exists, save_point, write_manifest


def test_roundtrip_and_idempotent(tmp_data_dir):
    rec = {"s": 0.5, "delta": 1.0, "E0": -3.25, "status": "ok"}
    p = save_point(tmp_data_dir, "exp03", rec)
    assert point_exists(tmp_data_dir, "exp03", rec)
    assert load_point(p)["E0"] == -3.25
    # Same config must NOT be silently overwritten with different data.
    try:
        save_point(tmp_data_dir, "exp03", {**rec, "E0": 0.0})
    except ValueError:
        pass
    assert load_point(p)["E0"] == -3.25


def test_raw_immutable(tmp_data_dir):
    # FR-006/V.5: post-processing must not mutate stored raw bytes.
    rec = {"s": 0.5, "raw": np.array([1.0, 2.0])}
    p = save_point(tmp_data_dir, "exp01", rec)
    before = p.read_bytes()
    d = load_point(p)
    d["raw"][0] = 99.0  # caller-side mutation must not leak back
    assert p.read_bytes() == before


def test_manifest(tmp_data_dir):
    m = write_manifest(tmp_data_dir, "exp01", {"schema": "exp01-04/v1"})
    assert json.loads((tmp_data_dir / m).read_text())["schema"] == "exp01-04/v1"


def test_config_hash_stable():
    assert config_hash({"b": 1, "a": 2}) == config_hash({"a": 2, "b": 1})
