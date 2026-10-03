# Contract: Baseline Cross-Check (same-H + anchors, v2)

**Scope**: all 01–04 v2 records under the frozen new $H$
(`H_DEF="ssh-xxz-exp-OBC-v2"`, D-002 as amended 2026-10-01).

**D-002 amendment (2026-10-01)**: the original "v2 records vs archived v1
baseline, energies <1e-8" item is REMOVED as unachievable. The $H$ was
redefined between rounds — v1 bond term $(XX+YY)+\delta\cdot(ZZ)$ (linear
$\delta$, no $ZZ$ at $\delta=0$) vs v2 bond term
$e^{-\delta}(XX+YY)+e^{+\delta}(ZZ)$ (exponential $\delta$, full Heisenberg
point at $\delta=0$). Single-point verification at $L=8$, $(s,\delta)=
(0.02,0.04)$: v1 oracle $E_0=-7.997389183293$ vs v2 $E_0=-11.613024693853$,
$|\Delta E_0|\approx3.6$ (matrix frob 44.37 vs 53.68). No parameter mapping
can close an $O(1)$ spectral gap from a changed functional form. The
archived Python core stays a read-only $H$-definition reference only.

1. Same-$H$ builder equivalence: `kron_reference` vs direct builder,
   energies <1e-10, on the 5-point subset in full (grid-01-02 §5).
2. Analytic anchors, exact by construction ($H$-independent):
   $\tilde Z_{\mathcal R}=+1$ (trivial), $-1$ (topological), $0$ (AFM GHZ).
3. New-$H$ analytic limits at the $\delta=0$ Heisenberg point:
   $E_0(4,0,0)=-6$, $E_0(4,1,0)=-3$, within <1e-8 on the dense reference.
4. Sampling: ≥3 points per experiment 01–04; record $E_0$ vs fresh same-$H$
   recompute <1e-8; 04 variational branches satisfy $E_{\rm var}\ge
   E_0-10^{-6}$ (via `verify_selection`, zero-violation).
5. v1 production records (beyond anchors) MUST NOT enter v2 datasets or
   figures (XII.2–XII.3, unchanged).
