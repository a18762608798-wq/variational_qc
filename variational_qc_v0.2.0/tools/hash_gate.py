"""SHA256SUMS hash gate for datasets + reference figures (SC-006 identity)."""

import hashlib
import pathlib
import sys


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_sums(root, out_name="SHA256SUMS"):
    root = pathlib.Path(root)
    lines = []
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.name != out_name:
            lines.append(f"{sha256_of(p)}  {p.relative_to(root)}")
    (root / out_name).write_text("\n".join(lines) + "\n")
    return str(root / out_name)


def check_sums(root, out_name="SHA256SUMS"):
    root = pathlib.Path(root)
    bad = []
    for line in (root / out_name).read_text().splitlines():
        h, _, rel = line.partition("  ")
        if sha256_of(root / rel) != h:
            bad.append(rel)
    return bad


if __name__ == "__main__":
    mode, root = sys.argv[1], sys.argv[2]
    if mode == "write":
        print(write_sums(root))
    elif mode == "check":
        bad = check_sums(root)
        print("MISMATCH:", bad if bad else "none")
        sys.exit(1 if bad else 0)
