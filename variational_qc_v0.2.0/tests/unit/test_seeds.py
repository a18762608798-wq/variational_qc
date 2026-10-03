"""T010: byte-exact seed derivation vectors (contract scan-03-04 §7). FAIL-first."""

from ssh_xxz.vqe.seeds import derive_seed


def test_deterministic_and_range():
    a = derive_seed(0.5, 1.0, "trivial", 0)
    assert a == derive_seed(0.5, 1.0, "trivial", 0)
    assert 0 <= a < 2**32


def test_distinct_inputs_distinct_seeds():
    seeds = {
        derive_seed(0.5, 1.0, b, r) for b in ("trivial", "topological", "afm") for r in range(3)
    }
    assert len(seeds) == 9


def test_encoding_spot_vector():
    # f"{s:.17g}|{delta:.17g}|{init}|{restart}" SHA256 -> first 4 bytes BE.
    import hashlib

    raw = hashlib.sha256("0.5|1|trivial|0".encode("utf-8")).digest()
    expect = int.from_bytes(raw[:4], "big")
    assert derive_seed(0.5, 1.0, "trivial", 0) == expect
