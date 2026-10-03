# Contract: Q Reconstruction-Only

**Scope**: Experiment 02 observable $Q$.

1. $Q$ has NO independent physical definition in this cycle. It is stored ONLY
   as a value derived from the same point's saved $S(\pi)$ and $O_{\rm str}$
   (AS-02.3), with `{S_pi_ref, Ostr_ref}` links (data-model.md §1).
2. The derivation formula is owned by `doc/plan/theory/topological_op.md`
   ($Q=4/3+2O_{\rm str}-S(\pi)/6$); this contract does not redefine it.
3. Reconstruction test: recompute $Q$ from stored $S(\pi),O_{\rm str}$ and
   require float64 bitwise identity with the stored $Q$ on the same code path;
   cross-builder comparison uses $10^{-10}$ tolerance (see grid-01-02 §3/§5);
   mismatch is a contract failure, never silently corrected.
4. Observable convention ($S(q),S(\pi),O_{\rm str},Q,\tilde Z_{\mathcal R}$)
   is identical across all experiments (FR-004); convention changes require a
   spec amendment, not a code shortcut.
5. q-grid (binding; R2 amended 2026-09-30 for curve readability): 49 points
   `q_k = 2πk/48`, $k=0,\dots,48$ over $[0,2\pi]$ ($q=\pi$ at $k=24$,
   explicit). The identical array is used for all three representative
   curves and saved in each record; supersedes the earlier 8-point
   allowed-momenta grid (same dual constraint, finer sampling).
