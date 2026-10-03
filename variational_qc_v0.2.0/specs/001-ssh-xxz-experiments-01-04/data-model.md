# Data Model: SSH-XXZ Experiments 01–04

**Schema**: `exp01-04/v1` | **Storage**: per-point `.npz` + JSON manifest.
Every record carries explicit coordinates (FR-009) and provenance (VI.3);
failures are explicit states (FR-008), never silent.

## Provenance block (all entities)

`{experiment, stage, L, phys_params, depth?, branch?, optimizer/backend,
seed, code_version, source}` — `source ∈ {exact, ideal-variational}` (VI.4;
no finite-shot/hardware value exists in this cycle).

## Failure state (FR-008)

`status ∈ {ok} ∪ {failed: {reason, stage, detail_ref}}`. Failed points keep
their coordinates + diagnostics; plotting must distinguish failed from missing.

## Entities

### 1. PhaseGridPoint (01/02 grid)

Fields: $(L{=}8, s_i, \delta_j)$ with $s_i=i/50$, $\delta_j=3j/50$
($i,j=1..49$); observables per experiment: 01 → $\tilde Z_{\mathcal R}$;
02 → $S(\pi), O_{\rm str}, Q_{\rm derived}, \tilde Z_{\mathcal R}$.
Validation: coordinates on frozen grid (contract grid-01-02); $Q$ stored ONLY
as derived value with `{S_pi_ref, Ostr_ref}` links (AS-02.3).

### 2. FiniteSizeGapPoint (01 appendix)

Fields: $(L\in\{4,8,12,16\}, s_i, \delta{=}1, E_0, E_1, \Delta_{\rm raw}{=}E_1-E_0)$.
Validation: full-Hilbert-space definition (physical $H$, no $P$ penalty);
$s\to1$ collapse preserved raw; $s$ uses the R1 49-point set.

### 3. ExactReferencePoint (03)

Fields: $(L{=}8, s_i, \delta\in\{1,3\}, E_0, S_{\rm exact}(\pi),
O_{{\rm str},{\rm exact}})$. 98 records target (SC-003). Serves as the join key
for every SelectedVariationalResult (contract scan-03-04).

### 4. VariationalBranchResult (04, per branch)

Fields: $(s_i, \delta, p, branch\in\{{\rm triv},{\rm topo},{\rm AFM}\},
\theta^*, E_{\rm branch}, n_{\rm evals}, n_{\rm restarts}, seed,
from\_baseline\in\{0,1\}, status)$.
Validation: $\theta^*$ within $[-\pi,\pi]$ box and frozen
freezing/halving rules applied; seed derivation per
`contracts/scan-03-04.md` §7 (byte-exact); counts per §6
($n_{\rm seeds}=3$, $n_{\rm restarts}=3$).

### 5. SelectedVariationalResult (04, per $(s,\delta,p)$)

Fields: branch pointer to the min-energy VariationalBranchResult +
$(E_{\rm var}, S_{\rm var}(\pi), O_{{\rm str},{\rm var}})$ +
exact-record coordinates link. 490 records target (SC-004).
Validation: selection = argmin physical energy (AS-04.2);
$E_{\rm var}\ge E_0-\tau$, $\tau=10^{-6}$ (AS-04.4);
`accepted(p) ≤ baseline(p-1)+τ` (AS-04.5, clamp by construction).

## Relationships

PhaseGridPoint(01) $\xrightarrow{\text{same coordinates}}$ PhaseGridPoint(02);
ExactReferencePoint $\xleftarrow{\text{join on }(s,\delta)}$
SelectedVariationalResult $\xleftarrow{\text{min over}}$ VariationalBranchResult
($\times3$ branches, each with full provenance or failure).
