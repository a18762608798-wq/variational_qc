"""QS-3 verifier (T044b): 03/04 linkage checks over saved manifests.

Asserts 98 exact / 490 selected / 3-branch provenance / Evar>=E0-tau /
nesting+from_baseline; prints summary; nonzero exit on failure (ERROR gate).
"""

import sys

import experiments.exp04_ideal as e4
from ssh_xxz.io.store import iter_points


def main(argv):
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True)
    ap.add_argument("--var", required=True)
    ap.add_argument("--tau", type=float, default=1e-6)
    a = ap.parse_args(argv)
    ref = [r for r in iter_points(a.ref, "exp03") if r.get("status") == "ok"]
    sel = [r for r in iter_points(a.var, "exp04s")]
    br = [r for r in iter_points(a.var, "exp04b") if r.get("status") == "ok"]
    rep = e4.verify_selection(a.var, a.ref, tau=a.tau)
    ok = (len(ref) == 98 and rep["n_selected"] == 490
          and rep["n_violations"] == 0 and rep["n_nesting_violations"] == 0
          and len(br) == 490 * 3)
    print(f"exact={len(ref)} selected={rep['n_selected']} branches={len(br)} "
          f"violations={rep['n_violations']} nesting={rep['n_nesting_violations']}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
