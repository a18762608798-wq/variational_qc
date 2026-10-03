# Data Model: Julia Rewrite (schema `exp01-04/v2`)

Storage: per-point `.npz` (NPZ.jl) + JSON manifest. Every record carries
explicit coordinates (FR-009 spirit) and provenance (VI.3); failures are
explicit states (FR-008 spirit), never silent. v1 records are NOT migrated.

## Provenance block (all entities)

`{experiment, stage, L, phys_params, depth?, branch?, optimizer/backend,
seed, code_version, julia_manifest, source}` —
`source ∈ {exact, ideal-variational}`;
`backend ∈ {julia-krylovkit, julia-yao}` (VI.4; no other values this round).

## Failure state

`status ∈ {ok} ∪ {failed: {reason, stage, detail_ref}}`. Failed points keep
coordinates + diagnostics; plotting distinguishes failed from missing.

## Entities (v2)

### 1. PhaseGridPoint — $(L{=}8,s_i,\delta_j)$, $s_i=i/50$, $\delta_j=3j/50$;
01 → $\tilde Z_{\mathcal R}$; 02 → $S(\pi), O_{\rm str}, Q_{\rm derived},
\tilde Z_{\mathcal R}$ ($Q$ derived-only with `{S_pi_ref, Ostr_ref}` links).

### 2. FiniteSizeGapPoint — $(L\in\{8,12,16\},s,\delta{=}0,E_0,E_1,
\Delta_{\rm raw}{=}E_1-E_0)$; raw full-Hilbert-space definition.

### 3. ExactReferencePoint — $(L{=}8,s,\delta\in\{0,0.85\},E_0,
S_{\rm exact}(\pi),O_{{\rm str},{\rm exact}})$; 98 records; join key for 04.

### 4. VariationalBranchResult — $(s,\delta,p,{\rm branch})$ + optimized
parameters + final energy + `nevals` + `seed` (byte-exact derivation carried
over) + `from_baseline∈{0,1}` + status.

### 5. SelectedVariationalResult — argmin-energy branch + $(E_{\rm var},
S_{\rm var}(\pi),O_{{\rm str},{\rm var}})$ + exact-record coordinates link;
490 records; $E_{\rm var}\ge E_0-\tau$ ($\tau=10^{-6}$);
`accepted(p) ≤ baseline(p-1)+τ`.

## Relationships

PhaseGridPoint(01) $\xrightarrow{\text{same coordinates}}$ PhaseGridPoint(02);
ExactReferencePoint $\xleftarrow{\text{join on }(s,\delta)}$
SelectedVariationalResult $\xleftarrow{\text{min over}}$ VariationalBranchResult
(×3, full provenance or failure). Cross-check links (contracts/xcheck-baseline)
join v2 records to archived v1 anchors by coordinates.
