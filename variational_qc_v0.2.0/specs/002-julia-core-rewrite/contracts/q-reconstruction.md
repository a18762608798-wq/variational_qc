# Contract: Q Reconstruction-Only (v2)

**Scope**: Experiment 02 observable $Q$ (new $H$).

1. $Q$ has NO independent physical definition. Stored ONLY as derived from
   the same point's saved $S(\pi)$ and $O_{\rm str}$, with reference links.
2. The derivation formula is owned by `doc/plan/theory/topological_op.md`;
   this contract does not redefine it.
3. Reconstruction test: same-code-path float64 bitwise identity;
   cross-builder comparison at $10^{-10}$; mismatch is a contract failure.
4. Observable convention identical across experiments; changes need a spec
   amendment.
5. q-grid: 49 points $q_k=2\pi k/48$ over $[0,2\pi]$ ($q=\pi$ at $k=24$,
   explicit); identical array for all three representative curves, saved per
   record.
