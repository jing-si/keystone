# R010/S06 Standards-to-Product Core Simplification Design

Date: 2026-08-10
Status: Proposed implementation baseline; project meaning is governed by `DEC-WORKS-029` and the
R010/S06 Work Order.

## Context

Keystone's product goal is standards-to-code traceability, standards-led project management, and
recoverable delivery state. R010/S01-S04 added correctness controls, but current release, graph apply,
Coordinator closure, and Author finalization accumulated HMAC keys, external evidence roots, snapshot
chains, receipt producers, and actual-agent evaluation requirements that do not directly serve that
goal.

The accepted R010/S05 direction is:

- keep source-owned ID/ref discovery, Artifact Graph source reconstruction, stale/impact analysis,
  transaction correctness, and repository-derived Work State;
- make the core/default workflow usable without secrets, external reviewers, or evidence storage;
- keep only bounded structural read compatibility for historical closure/finalization/application
  evidence;
- do not merge the frozen actual-agent branch and do not create an optional audit module in R010.

## Goals

1. Align package contracts and operational documentation with the no-secret current standards.
2. Remove actual-agent evidence as a required release step or input.
3. Remove current owner-apply HMAC producers and installer coupling.
4. Simplify Coordinator closure and Author post-acceptance synchronization to current repository
   evidence, verification, durable Progress, Work State, and graph validation.
5. Preserve the retained Artifact Graph and Work State behaviors and supported historical readers.

## Non-goals

- No change to R011 documents or semantics.
- No merge or recreation of the frozen S05 actual-agent implementation.
- No live model, reviewer, network, credential, or external evidence-root execution.
- No publication, version release, dependency addition, rename, or unrelated refactor.
- No deletion of historical R010 evidence JSON or accepted S01-S05 history.
- No direct write to `${CODEX_HOME:-~/.codex}/skills`; installer verification uses temporary staging.

## Architecture

### Current graph application

Linker continues to own canonical mutation and exact patch planning while remaining source-write-free.
Each source owner confirms only its own patch, rechecks the raw-byte baseline immediately before write,
applies it in its existing edit lane, and returns `applied | failed | stale_baseline` plus the resulting
digest. Current success requires current source reconstruction, canonical transaction equality, and
repository graph validation. SHA-256 identifies byte/generation equality; it is not encryption,
identity, or organizational independence proof.

### Current Coordinator closure

Coordinator closure uses the immutable assignment boundary, starting Git/diff baseline, fresh current
diff, worker report, verification evidence, document/metadata/graph dispositions, and durable Progress.
After Main acceptance, Author synchronizes Work, Progress, indexes, and Context Map, then validates Work
State and the graph when applicable. Current closure does not require HMAC keys, complete snapshot chains,
acceptance-event producers, or a new finalization manifest.

### Historical compatibility

Closure v1-v3, finalization v1-v6, graph-validation v2, and application-evidence inputs may still be read
by bounded adapters and fixtures. These paths may return structural or diagnostic evidence but cannot
authorize a new current apply, completion, acceptance, or release success. New keys, receipts, snapshots,
or finalization envelopes are not produced.

### Current release plan

The canonical release order is:

1. preflight and workspace isolation checks;
2. package tests;
3. shared skill tests;
4. external-cache compileall;
5. docs and repository readiness;
6. repository-derived Work State;
7. repository graph validation;
8. temporary installer staging, parity, and rollback checks;
9. postflight cleanliness checks.

Actual-agent evaluation, reviewer keys, price/token budgets, score gates, Coordinator v2/v3 production,
and current-finalization production are absent from the default plan.

## Implementation phases

### Phase A — Package contracts and README

Align these outputs with the accepted current standards:

- `skills/keystone-author/SKILL.md`
- `skills/keystone-author/references/finalization-validator.md`
- `skills/keystone-coordinator/SKILL.md`
- `skills/keystone-coordinator/references/closure-validator.md`
- `skills/keystone-linker/SKILL.md`
- `skills/keystone-linker/references/graph-runtime.md`
- `README.md`

Contract examples and verification language must distinguish current no-secret authority from historical
read compatibility. Historical CLI details may remain only where an adapter still supports them.

### Phase B — Remove agent-evaluation release authority

First add or revise release regressions so a canonical release succeeds without agent/reviewer evidence.
Then remove the `agent_behavior_evidence` step and its inputs from `scripts/run_release_gate.py`, and align
the README and security tests. After a fresh consumer search proves zero current consumers, delete:

- `scripts/agent_eval_scenarios.json`
- `scripts/validate_agent_evals.py`
- `skills/tests/test_agent_eval_security.py`

Do not rename remaining tests in this phase.

### Phase C — Remove current HMAC producers

Add tests for owner-direct apply and current graph validation before removing the producer/runtime and
installer coupling:

- `scripts/generate_owned_surface_apply_runtimes.py`
- `scripts/owned_surface_apply_runtime.py`
- Author and Coordinator `owned_surface_apply_runtime.py` / `run_owned_surface_apply.py`
- `skills/tests/test_owned_surface_apply_runtime.py`
- matching installer required/parity/help blocks

Keep application/transaction evidence parsers only as historical structural readers. Default graph
validation must not require owner keys or an external evidence root.

### Phase D — Simplify closure and finalization consumption

Make the no-secret base closure manifest and durable document closure the current Coordinator contract.
After historical reader fixtures are fixed, remove current package/installer production of assignment
snapshots and acceptance events. Keep closure and finalization validators as historical readers, but
remove them from current release and success prerequisites.

### Phase E — Retained-core and full verification

Do not reduce SourceUnit, metadata, scanner, lifecycle, impact, classification, planner, reconciler,
transaction/wire validation, or Work State behavior. Only caller/import changes needed to decouple retired
current producers are allowed. Run the complete release order and exact changed-path scope check.

## Error handling and deletion gates

- A missing or still-live current consumer blocks deletion.
- A baseline mismatch returns `stale_baseline` and performs no write.
- A historical reader that cannot validate retired cryptographic authority without its producer/key must
  fail closed as structural-only; it must not manufacture current success.
- Any retained graph or Work State regression stops the current phase.
- Any need to change R011, historical evidence, public compatibility beyond the recorded boundary, or
  add a dependency requires new approval.
- Each phase is independently reviewable and reversible; behavior changes and file renames are not mixed.

## Testing strategy

All behavior changes follow RED → GREEN → refactor:

1. Release tests prove agent evidence is optional/absent in the default plan.
2. Graph integration tests prove current owner-direct apply and reconstruction without keys/receipts.
3. Closure tests prove current success from scope, diff, verification, dispositions, and Progress only.
4. Historical fixtures prove retired wires are readable but non-authoritative.
5. Existing retained Artifact Graph and Work State suites prevent capability loss.
6. Package and cross-skill tests check contract/runtime consistency.
7. Final checks cover compileall, readiness, Work State, repository graph validation, installer staging,
   `git diff --check`, and exact changed paths.

## Completion criteria

- Package contracts, README, runtime, and tests express the same current no-secret meaning.
- Default apply/closure/release requires no HMAC/reviewer key or external evidence root.
- Actual-agent evidence is not a current release input or step.
- Historical readers cannot create new current success authority.
- Artifact Graph and Work State retained regressions pass.
- Changed paths stay within the accepted S06 Change Set and preserve all unrelated user changes.

## Rollback

Each phase is committed only after its focused and compatibility suites pass. A failing later phase rolls
back only its own commit or is repaired in place; earlier green phases and historical evidence are not
rewritten. Deletion occurs only after zero-current-consumer evidence, so rollback restores the last
phase without reconstructing hidden external state.
