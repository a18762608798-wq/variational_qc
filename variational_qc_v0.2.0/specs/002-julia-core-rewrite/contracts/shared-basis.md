# Contract: Shared Ground-State Basis Reuse (v2)

**Scope**: all 01–04 exact-diagonalization ground states (new $H$;
`doc/plan/experiment/00_data_spec.md` §基矢 canonical 保存).

1. Every computed exact ground-state vector is stored in the shared
   canonical store: 01 phase grid ($L=8$, 2401 points) and 01 gaps
   ($L=8,12,16$) in full — no sampling, no truncation.
2. 02 MUST reuse 01-grid vectors for identical $(L,s,\delta)$; 03's
   $\delta=0$ line MUST reuse 01-gap $L=8$ vectors. Re-diagonalization for
   an already-stored coordinate is a contract violation.
3. The store key includes `code_version` and the Hamiltonian-definition hash
   alongside $(L,s,\delta)$; same coordinates under a different code or
   physics version MUST NOT alias the same record.
4. Reuse changes nothing physical: shared vectors are exact ground states of
   the same $H$; no formula, boundary, normalization, or sector is altered
   by the reuse machinery (Constitution I).
5. Removing duplicate-computation logic MUST NOT modify any physics formula;
   only orchestration (skip-if-present + load) may change.
