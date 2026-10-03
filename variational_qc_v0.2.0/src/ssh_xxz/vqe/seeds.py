"""Deterministic seed derivation. Binding: contracts/scan-03-04.md §7.

Tuple order (s, delta, init, restart) encoded as UTF-8
f"{s:.17g}|{delta:.17g}|{init}|{restart}" -> SHA256 -> first 4 bytes
big-endian -> uint32. Stored per branch record.
"""

import hashlib


def derive_seed(s, delta, init, restart):
    raw = f"{s:.17g}|{delta:.17g}|{init}|{restart}".encode("utf-8")
    digest = hashlib.sha256(raw).digest()
    return int.from_bytes(digest[:4], "big")
