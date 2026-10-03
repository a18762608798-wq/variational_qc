# T052 — Baseline Cross-Check Report (D-002 amended, 2026-10-01)

Contract: `contracts/xcheck-baseline.md` (amended); grid identity
`contracts/grid-01-02.md` §5 (re-mapped). Method: same-$H$ checks only.

## 1. H before/after (why vs-v1 comparison was removed)

| | v1 archived baseline (`src/ssh_xxz`, read-only) | v2 Julia (`H_DEF="ssh-xxz-exp-OBC-v2"`) |
|---|---|---|
| bond term | $(XX+YY)+\delta\cdot(ZZ)$ | $e^{-\delta}(XX+YY)+e^{+\delta}(ZZ)$ |
| $\delta$ role | linear coefficient | exponential |
| $\delta=0$ | $XX+YY$ only (no $ZZ$) | full Heisenberg point |
| single point $L=8,(0.02,0.04)$ | $E_0=-7.997389183293$ (frob 44.37) | $E_0=-11.613024693853$ (frob 53.68) |

## 2. D-002 unachievability statement

Original D-002 ("v2 records vs archived v1 baseline, energies <1e-8") is
unachievable: the $H$ functional form changed between rounds, producing an
$O(1)$ spectral gap ($|\Delta E_0|\approx3.6$ at the probe point, and the
two definitions do not even coincide at $\delta=0$). No parameter mapping
can close it. Removed from the contract 2026-10-01; the archived core
remains a read-only $H$-definition reference. v1 production records stay
out of v2 (XII.2–XII.3).

## 3. Old-new 5-point mapping (v1 $\delta=3j/50$ grid → frozen $\delta=2j/50$)

| v1 (off-grid now) | v2 (on frozen grid) |
|---|---|
| (0.02, 0.06) | (0.02, 0.04) |
| (0.98, 0.06) | (0.98, 0.04) |
| (0.50, 2.94) | (0.50, 1.96) = AFM rep |
| (0.50, 1.02) | (0.50, 1.00) |
| (0.98, 2.94) | (0.98, 1.96) |

## 4. Same-$H$ trio results (all PASS)

- Builder equivalence (`kron_reference` vs direct, dense, L=8, 5 pts):
  $|\Delta E_0| = 0.0$ exact at all 5 points (<1e-10 ✓).
- Anchors exact: $\tilde Z_{\mathcal R}$ = +1.0 trivial / −1.0 topo / 0.0 AFM ✓.
- New-$H$ analytic limits ($\delta=0$ Heisenberg): $E_0(4,0,0)=-6.0$,
  $E_0(4,1,0)=-3.0$ exact (<1e-8 ✓).

## 5. Sampling (record vs fresh same-$H$ dense recompute, L=8)

01: (0.02,0.04) 2.0e-14; (0.50,1.00) 1.8e-14; (0.98,1.96) 1.2e-13 ✓
02: same 3 pts 2.0e-14 / 1.8e-14 / 1.2e-13; 01-vs-02 $|01-02| = 0.0$ (§2 ✓)
03: (0.02,0.0) 1.4e-14; (0.50,0.85) 1.8e-14; (0.98,0.0) 1.6e-14 ✓
04 (variational bound $E_{\rm var}\ge E_0-10^{-6}$):
(0.26,0.0) margin +2.7e-4; (0.44,0.0) +3.3e-4; (0.56,0.0) +1.5e-4 ✓
(full 490: `verify_selection` 0 violations / 0 nesting, PROD04 log.)

Verdict: T052 PASS under the amended contract. No v1 energy enters v2.
