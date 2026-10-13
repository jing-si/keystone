---
name: keystone-linker
description: "Use for Artifact Graph interpretation and graph-relevant document or artifact deltas: discovery, impact, stale/gap review, reuse/test candidates, canonical mutation planning, source-surface handoffs, and worker context. Do not use to edit source surfaces, make user decisions, or assign workers."
---

<!-- keystone: id=key.skill.linker kind=output_artifact artifact_kind=skill_source -->
<!-- keystone: produced_from=key.work.skill-runtime-implementation.order -->
<!-- keystone: governed_by=key.standard.project key.standard.skill.linker -->
<!-- keystone: derived_from=key.work.decisions.dec-works-020 -->

# keystone-linker

## Step Definition Evidence

A Work Order may declare `key.defined_steps: [S01, S02, ...]`. Validate local unique Step IDs there.
A Progress step_ref is a state reference, not a definition. Without declared definitions report
work_gate_step_unidentified and request bounded Reader/AI source interpretation; do not infer absence.
With an explicit definition list, a missing target is work_gate_step_invalid. This does not authorize
full-text semantic parsing, corpus annotation, status changes, or acceptance. Follow the management
review workflow for source-snapshot boundaries and input expansion to required counterpart documents.

## Purpose

Interpret the canonical Artifact Graph reconstructed from current repository source. Provide bounded
impact, stale/gap, reuse/test-candidate, and canonical mutation guidance. Linker is always read-only:
source owners apply changes and Main accepts results.

This package is the complete Linker runtime contract. Project standards define project meaning; they do
not need to duplicate Linker behavior.

## When To Use

Use Linker for:

1. Discovery from an artifact, document, stable ID, symbol, path, or Work item.
2. Impact analysis for metadata, relation, lifecycle, or cross-surface changes.
3. Stale/gap review and reuse or test candidates.
4. Canonical multi-surface mutation planning.
5. A bounded context brief for Main, Coordinator, or Author.
6. Affected-scope or repository graph validation.

Do not use Linker to edit files, decide user intent, accept a result, initialize Keystone, assign a
worker, or require external verification artifacts for ordinary work.

## Managed Work State

With `{document_root}/state/manifest.json` set to `{"schema_version":1,"mode":"managed"}`, packaged
Work State schema v6 is the only current Round/Work/Step state authority.
The only current-status source is `state/current.json` (wire v2, `states: {execution: [entries]}`);
closed entries are removed and dated changes stay in Work Orders. Never create per-Round state files.
 Dependency readiness uses
that same evaluator as Reader/Coordinator and binds the result to state/plan/history raw-byte digests.
It bypasses the legacy dependency cache so state-only edits cannot reuse stale gate results. It never
falls back to Aggregate Progress or Work Index statuses on errors. Existing legacy dependency ownership
instructions apply only without this marker; standard/decision document lifecycle and approval remain
source metadata. Do not infer work acceptance from inherited document approval.

Only registered plans and exact `work_state_targets` dependency locators may supply execution context.
A closed dependency satisfies a required gate only with a matching `closed:complete` event and complete,
accepted result; cancelled/skipped/superseded or missing evidence does not satisfy it. State evidence is
added to freshness without widening the caller's artifact graph owner scope. A graph scan of a historical
closed Work is historical artifact context, not permission to resurrect its execution gates.

## Operating Modes

Choose the smallest mode needed by the caller:

- **Discovery**: resolve an ID, path, symbol, Work item, owner, or relation anchor.
- **Impact**: return direct and bounded transitive candidates for the relevant relation types.
- **Stale/Gap review**: separate mechanical conflicts, semantic review candidates, missing metadata,
  unsupported surfaces, and unresolved identity.
- **Worker context**: return only evidence, reusable artifacts, tests, owners, and stop conditions needed
  for a bounded implementation scope; never assign the worker.
- **Graph synchronization**: plan exact canonical mutations and owner patches only when multiple source
  surfaces must change together.
- **Context readiness**: provide docs-first owner/ref discovery and expand to repository scope lazily.

Do not combine modes merely to produce a larger report. A single-surface refresh stays outside a graph
transaction, and a session view stays outside persistent source or cache authority.

## Source of Truth

The graph is reconstructed from current repository source surfaces and supported adjacent companion
metadata. A cache is disposable and optional. When a cache is absent, stale, outside the accessible
workspace, or unreadable, scan source directly without asking for additional folder access.

Document and artifact lifecycle domains remain separate. Typed relations are semantic candidates, not
automatic permission to edit every reachable node.

## Core Workflow

1. Resolve the repository/document root and current source set.
2. Reconstruct the smallest useful graph scope.
3. Resolve identifiers and paths; report ambiguity instead of guessing.
4. Traverse only relation types relevant to the question.
5. Classify affected, unaffected, stale, gap, reuse, and test candidates with source evidence.
6. When a canonical multi-surface change is required, produce a deterministic transaction plan with
   exact owners, baselines, patches, and expected results.
7. After owners apply, reconstruct current source and run transaction-scope mechanical validation.
8. Return a concise handoff; do not dump the full graph unless explicitly requested.

## Current Apply and Verification

For current transactions:

- every physical surface has one owner and one expected baseline;
- the owner rechecks current bytes immediately before apply;
- mismatch returns `stale_baseline` without writing;
- the owner reports `applied | failed | stale_baseline` plus the resulting digest or state;
- Linker compares the actual result with the planned result;
- Linker reconstructs affected current source and verifies canonical mutations and relations;
- current graph success requires no HMAC receipt, owner key, external evidence root, or assignment
  snapshot.

A schema-v1 validation manifest or direct `--transaction` is the current structural/current-state path.
Schema-v2 application-evidence manifests are historical compatibility inputs. If their external
evidence root, owner key, receipt producer, or package identity is unavailable, validate the readable
manifest, transaction, source reconstruction, and current result; emit `historical_structure_only` and
do not claim legacy application authority.

Historical evidence cannot authorize a new current apply, closure, or release result.

## Graph Relevance

Run graph synchronization when a change affects stable IDs, locators, typed relations, lifecycle,
provenance, metadata ownership, generated/source authority, or canonical meaning across surfaces.

For a clearly plain new file or a source change with no graph declaration or relation impact, a bounded
classification may return `not_applicable`. Do not run a repository-wide graph pass merely because any
file changed.

## Transaction Contract

Canonical transaction schema v2 remains the executable planning wire:

- exact input deltas and scope;
- canonical mutations with `operation`, `entity`, `before`, `after`, evidence, and reason;
- owner-specific surface patches with baseline and expected-after digests;
- reconstruction baseline and result when mutations are present;
- apply results and mechanical validation;
- `proposed | applied | verified | failed` state.

Descriptive schema-v1 transactions remain historical compatibility only. Required mutation patches
cannot be optional. An ancillary optional patch is validated only when applied.

## Source Surfaces

- Supported text sources use first-effective-token Keystone declarations.
- Unsupported or binary sources use `<source>.keystone.json` companion metadata.
- If inline and companion metadata both declare authority, emit `metadata_surface_conflict`.
- An undecodable source without a valid companion emits `unsupported_encoding`.
- Never merge ambiguous metadata anchors or infer ownership from arbitrary prose.
- Raw source digests bind current baselines and companion identity.

## Impact Output

Return only what the caller needs:

1. Anchor and reconstructed source scope.
2. Direct and transitive affected candidates with relation evidence.
3. Stale/gap findings and confidence.
4. Reuse and test candidates.
5. Required owner handoffs and canonical mutation plan, if any.
6. Validation result and residual uncertainty.

Label inference explicitly. Keep mechanical findings separate from user or policy decisions.

## Verification Tiers

1. **Default Work**: affected source reconstruction, transaction-scope checks, and related tests.
2. **Escalated**: affected Linker package suites or repository-scope validation when Linker runtime,
   metadata schema, or repository-wide relations changed.
3. **Release**: full package, repository, and installer validation only for an explicit release request.

Repository locator gaps and unsupported surfaces remain visible diagnostics. They do not justify
generating evidence artifacts or editing unrelated sources.

## Dependency State Owner

Treat `depends_on` as semantic source-to-target evidence and `work_gates` as condition and scope only.
For a Work target, resolve execution and approval state from the aggregate `key-progress.md` in the
same Work directory. Use `00_key-index.md` only as a legacy fallback, and a Work Order state only when
neither canonical surface exists. A conflicting projection is stale evidence; it never overrides the
aggregate Progress or mutates source state.

## Source-derived Semantic Views

Materialize criterion, effective Decision, and Work artifact summaries only when the caller requests
`include_source_views`.

1. Reuse the same reconstructed `GraphSnapshot` and relation/lifecycle admission used by source
   validation. Bind every response to its `source_generation`.
2. Join acceptance criteria through `requires_verification_of` and active admitted `verifies`
   evidence. `verified` describes the joined evidence; it is never automatic acceptance or approval.
3. Derive effective Decisions from active accepted Decision/claim nodes and admitted `supersedes`
   relations. Keep pending Decisions separate.
4. Derive direct Work outputs and tests from active `produces` relations. Use normal impact traversal
   for transitive impact instead of expanding this compact view.
5. Keep this projection source-bound and session-only. Bypass the disposable cache for the request,
   leave default readiness unchanged, and do not persist a view, manifest, receipt, key, or HMAC.
6. Reuse existing acceptance-event and finalization digest/generation bindings when historical
   snapshot evidence is needed; do not create another evidence system.

## Boundaries and Stop Conditions

Stop and return to Main when identity is ambiguous, sources conflict, a required semantic relation is a
user decision, current bytes differ from the planned baseline, or the needed edit lacks an owner. Do
not invent a relation, broaden scope, write source, or turn a warning into authority.

## Verification

Verify that:

1. Current source reconstruction works without a cache or external evidence directory.
2. Affected-scope validation checks the actual current result.
3. Current apply uses owner baseline/result checks without HMAC receipts.
4. Historical application-evidence inputs downgrade to structural diagnostics when trust material is
   unavailable.
5. Linker never edits source or grants acceptance.
6. Graph synchronization is conditional on graph relevance.
7. Output stays bounded to evidence, candidates, handoffs, and residual risk.

## Keymeta-First Bounded Discovery (R018)

Routine context readiness explicitly uses `discovery_mode: targeted`. Its internal request accepts
`anchors` (`id`, optional repository-relative `path` and raw-byte `digest`), confirmed `source_paths`,
ID-to-path `owner_paths`, selected `relation_types`, `follow_refs` and `max_depth` (0–8). Paths are
locator hints, not authority: re-read current source and verify owner admission. Unknown locators return
`owner_unresolved`; omitted or stale evidence makes bounded coverage incomplete.

Use `lookup` only with explicit `lookup_roots` and exact owner IDs. Report searched files and bytes;
byte matches are candidates that must pass canonical metadata admission. Do not build a typed graph
for lookup. Use `audit` for explicit full graph audit, release verification or scope conflict only.
Cache failure never promotes a targeted request to lookup or audit. The bounded source path works
without opening or creating a persistent cache; fresh locator evidence can be passed through
`owner_paths`, and all admitted files are rebound to current raw bytes.

The bounded default budgets are 128 files and 50 MiB, adjustable within the scanner hard limits using
`max_files` and `max_total_bytes`. Return v4 mode, scope, bounded completeness, diagnostics and freshness;
never claim repository completeness from a bounded result. Mode-less v2/v3 requests retain their
legacy scan and wire behavior for compatibility, but new routine callers must use explicit targeted
requests. Removing that compatibility path requires a separate migration check. Lexical admission,
owner/ref parsing and requested source views reuse one request-local parsed source snapshot.
