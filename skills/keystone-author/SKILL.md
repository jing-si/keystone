---
name: keystone-author
description: "Create or revise Keystone source documents, standards, work orders, progress records, decisions, indexes, metadata, and Change Sets within a clear scope. Use for direct document requests and accepted Clarify results; hand off initialization when Keystone is absent. Do not use for unresolved user decisions, read-only orientation, code/config/schema/API/test edits, worker orchestration, or skill-source implementation."
---

<!-- keystone: id=key.skill.author kind=output_artifact artifact_kind=skill_source -->
<!-- keystone: produced_from=key.work.skill-runtime-implementation.order -->
<!-- keystone: governed_by=key.standard.project key.standard.skill.author -->
<!-- keystone: derived_from=key.work.decisions.dec-works-020 -->

# keystone-author

## Purpose

Create and revise human-readable Keystone source documents within the user's request and accepted decisions. Own standards, work orders, progress records, decision records, source-document metadata, indexes, and Change Sets. Edit source documents only; Main verifies and accepts the result.

This installed contract is self-contained. Never require a consuming project to contain `standards/skills/author/**` or another project-local skill standard. Project documents define project meaning, not Author's runtime behavior.

## Initialization Gate

Detect the document root and initialization state before editing:

- `uninitialized`: no resolvable Keystone root or foundation structure.
- `partial`: only part of the required configuration or document structure exists.
- `conflicted`: multiple roots or existing-file meanings cannot be reconciled safely.
- `bootstrapping`: R000 exists and the project standard is being established.
- `ready`: one authoritative root, accepted project standard, indexes, decisions, and recoverable work exist. An adopted legacy corpus may be ready without retroactive config or R000.

For `uninitialized` or `partial`, ask once whether to initialize or repair and then continue the original writing request. Do not repeat the question in the same conversation and scope when consent already exists. Preserve the original request, caller, handoff reason, resume point, accepted decisions, and existing-file risks for `keystone-init`.

For `conflicted`, do not choose or overwrite. Send one actual decision topic to Clarify when project meaning or document adoption is at stake. Resume after the decision. If initialization is refused, make no files and explain the current limitation.

Before Keystone exists, code, README, configuration, and repository inspection belong to Main's normal capabilities. Accept that evidence as Author input; do not make Reader a prerequisite.

## Required Context

Use the minimum available context:

1. User request or Main-accepted edit instruction.
2. Document root or initialization state.
3. Target document/section or the purpose of a new document.
4. Applicable project standards, accepted decisions, and existing source documents when present.
5. Scope, acceptance boundary, workspace state, and existing-change risk.
6. Accepted Clarify result when a user decision was required.
7. Linker report, graph-relevance assessment, or pending graph transaction resume evidence when graph
   interpretation or synchronization matters.

A work order and progress record improve recoverability but are not artificial prerequisites for a small, valid, explicit document request. Record routing context only for multiple surfaces, authority boundaries, or real audit/handoff needs.

## Workflow

1. Detect initialization state and resolve one document root.
2. Handoff to Init or Clarify when the Initialization Gate requires it, then resume here.
3. Classify the request as `create`, `revise`, `clarify_apply`, `normalize`, `progress_update`, or
   `acceptance_finalize`. Main acceptance automatically selects `acceptance_finalize`; do not wait for
   a second user request to synchronize the accepted result.
4. Read only the relevant project standards, decisions, work context, target documents, and indexes.
5. Confirm that requested targets are Keystone source documents and that the scope is clear. Treat an explicit edit request as authority within its stated scope.
6. For a large or multi-document change, prepare an Author Edit Contract containing targets, allowed changes, impact candidates, exclusions, forbidden changes, progress policy, and verification. Skip this ceremony for a small unambiguous edit.
7. If project purpose, scope, policy, terminology, authority, sensitive data, destructive migration, or conflicting valid alternatives require user judgment, hand off exactly one topic to Clarify. Do not ask about built-in metadata, filenames, routing, or safe defaults.
8. Edit only approved source documents, apply the temporal and document-item metadata rules below, and preserve unrelated user or agent changes.
9. Check affected indexes, Context Map, decisions, progress, and Change Set needs. A relation is an impact candidate, not automatic edit authority.
10. Use the source-write-free Linker when artifact relations, stale metadata, gaps, or canonical graph
    mutations need interpretation. Defer code/config/schema/API/test/skill-source changes to Main direct
    or a user-permitted Coordinator scope.
11. Validate links, document and item identifiers, temporal metadata, item inheritance and relations,
    lifecycle/approval/work-state separation, terminology, and Markdown.
12. Report changes, intentional exclusions, verification, residual risk, and next action. Main accepts only after checking actual results and verification.

## Acceptance Finalization Runtime

After Main accepts one or more processed Steps, automatically run one bounded finalization for that
acceptance event:

1. Record every accepted Step execution as `work_status: complete` and approval as
   `approval.state: accepted`, then set every applicable owning Progress and Change Set
   frontmatter `finalization.state` and shared `acceptance_ref` to `in_progress`. Do not introduce a
   global `finalized` lifecycle value or infer state from body examples.
2. Change status directly only for each Step Main actually accepted. Evaluate the owning Work, Round,
   root works index, and Context Map against their own completion and representation conditions; never
   infer sibling or future-Step transitions.
3. Represent concurrent work as a zero-or-more `active_steps` list of equal Step refs. Never create or
   preserve a singular `current_step` claim as authoritative state. Record partial future-Step work as
   `early_work` with cause, completed scope, remaining scope, and `status_effect: none`; this does not
   activate that Step.
4. Build an impact-candidate manifest covering at least every owning Progress, Work Order/Change Set,
   work index, round index, root works index, Context Map, related standards/decisions/plans, recovery
   text, implementation gates, residual/deferred risks, and shared physical namespaces when applicable.
   Give every candidate one disposition: `updated`, `no_change`, `historical`, `out_of_scope`,
   `clarification_required`, or `integration_gate`, with a reason. Use `historical` only for genuinely
   immutable history, never to exempt a live recovery or status claim. For namespace collisions, record
   each owner and the current Work's integration action; do not edit another Work without authority.
5. Invoke the bundled runner described in
   [references/finalization-validator.md](references/finalization-validator.md). The command is
   diagnostic-only; Author interprets its evidence and retains all edit, acceptance, and transition
   authority.
6. Map a missing command to `validator_unavailable`. Map process-start failure, timeout, exit `2`, or
   unreadable output to `validator_execution_failed`. Exit `1` preserves the diagnostics. All three
   outcomes keep `finalization.state: in_progress`; record the reason and resume point instead of
   reporting success.
7. Set `finalization.state: complete` only after required candidate dispositions, source edits, core
   validator exit `0`, semantic review, and Main's post-edit verification are all evidenced. Initial
   Step acceptance starts this process but is not post-edit verification. Use `waived` only for
   an explicitly recorded bootstrap or not-applicable case with reason and follow-up.
8. Emit new finalization manifest `schema_version: 4`. Bind each accepted Step to its Progress
   `finalization_state` and `finalization_acceptance_ref`; bind `global_state.active_round`,
   `global_state.latest_accepted_round`, and `global_state.active_steps` to distinct typed work-index, round-index, root-index,
   and Context Map sources with their frontmatter `key.id`. Assess `graph_sync` as `required`,
   `not_applicable`, or `deferred`, with a reason. Required graph sync needs a bundled Linker validation
   manifest and matching verified transaction before finalization can complete. Version 1 is diagnostic
   compatibility for existing in-progress records only and can never approve `complete`. Version 2 is
   also compatibility-only for unfinished records and cannot approve a new `complete` finalization.
   Version 3 remains the compatibility wire for previously completed records; do not rewrite historical
   acceptance or graph evidence merely to make it current-state replayable.
   Use `global_state.active_round: none` only when `active_steps` is empty.

The finalization hard gate is scoped: while a Work has an incomplete required finalization, block only
that same Work's next implement assignment, transition to `in_progress`, next-Step Main acceptance,
and Work closure. Allow documentation repair, investigation, verification, and finalization resume.
Do not serialize independent Work or equal active Steps.

Project adapters and repository hooks may call the same bundled validator and add stricter checks.
They cannot remove core manifest fields, convert a core failure to success, edit sources, accept work,
or mark finalization complete. Hook absence is distinct from validator unavailability.

## Document Delta and Graph Synchronization

After an approved document meaning or independently addressable metadata item changes, Author emits a
delta. `graph_relevant: true` invokes Linker classification; it does not automatically require a graph
synchronization transaction and does not
widen Author scope, create Coordinator permission, or grant acceptance. A safe `not_required`
assessment for `graph_relevant: false` requires a concrete reason and maps to finalization
`not_applicable`; it does not change the canonical delta shape.

```yaml
document_delta:
  kind: document_delta
  source_surface:
  changed_locators: []
  semantic_summary:
  baseline_digest: sha256:<64-lowercase-hex> | absent
  graph_relevant: true | false
graph_attestations:
  - patch_id:
    owner: author
    decision: confirm | reject | needs_revision
    evidence:
graph_apply_results:
  - patch_id:
    result: applied | failed | stale_baseline
    resulting_digest:
    evidence:
```

Linker alone decides canonical mutations and exact per-surface patches. Author compares only an
`owner: author` document-metadata patch with the intended document meaning. Author never independently
creates a typed relation, reinterprets Linker's mutation, or attests another surface. Apply only a
confirmed in-scope patch, rechecking the target's raw UTF-8 SHA-256 baseline immediately before write;
on mismatch, do not write and return `stale_baseline`.

Preserve every `applied | failed | stale_baseline` result. Partial success remains
`partially_applied`; a resume skips patches whose current digest equals their recorded resulting digest
and rechecks remaining baselines. Linker reconstructs the graph from source and runs mechanical
validation. Author cannot declare the transaction `verified` or finalization complete. A conflicted or
failed transaction requires Linker's new attempt with a new ID, preserved attempt history, and the
conflict-reason-specific baseline/mutation/patch change defined by Linker.

Progress and Change Sets retain `graph_sync` disposition/reason, transaction ID/state, delta and patch
references, owner attestations, apply results, reconstruction, mechanical validation, transaction
completeness, coverage debt, last successful event, and resume point. Full patch bodies may remain in
the Linker transaction artifact if Progress contains a resolvable locator to it.

## Document Rules

- Keep standards and works in index-based trees under the configured root.
- Start ordinary rounds at `R001` and every round's steps at `S01`.
- Reserve `R000 Project Foundation` for the special pre-standard foundation round; its first step is also `S01`.
- Give each new work node a `00_key-index.md`, `key-work-{slug}.md`, and `key-progress.md` unless an accepted project rule says otherwise.
- Keep `document_lifecycle` (`draft`, `active`, `superseded`, `archived`), `approval.state`
  (`pending`, `accepted`, `rejected` when needed), and `work_status` in separate fields.
- Do not mark work `accepted` or `complete` before Main acceptance. Worker `DONE` is not Main acceptance.
- Apply accepted Clarify results without inventing a new decision or expanding their edit plan.
- Use Change Sets for large changes or document-to-code/test impact that needs traceability.
- Use `key.refs` for navigation and typed relations for semantic relationships; do not infer automatic propagation.

## Dependency and Work Gates

- Write an accepted semantic dependency as `key.relations.depends_on` from source to target. Treat it
  as a relation, not as a scheduler command or automatic status transition.
- Write execution conditions separately in top-level `work_gates`. Require each gate dependency to
  name a declared `depends_on` target, and require at least one of `applies_to.steps` or
  `applies_to.work_completion`.
- Validate target existence, duplicate and self references, source step IDs, and condition values.
  Use `condition.work_status: complete` and `condition.approval_state: accepted` unless an accepted
  project rule defines another value.
- Do not newly write legacy `<!-- keystone: depends_on=... -->` syntax. When structured and legacy
  evidence coexist, preserve structured metadata as authoritative and report conflicts.
- Never turn a dependency evaluation into automatic progress mutation, assignment, cancellation, or acceptance.

## Document Item Metadata

Apply item metadata on approved Keystone source-document surfaces when a heading, list item, decision
claim, work or acceptance criterion, capability or contract row can be referenced, changed, superseded,
or verified independently. Do not annotate every sentence, explanatory bullet, example, or repeated
summary. Existing unannotated corpus is not a bulk-migration requirement unless the approved scope says
otherwise.

- Use stable semantic IDs such as `key.rule.*`, `key.claim.*`, and `key.acceptance.*`; visible numbers,
  row labels, paths, and line numbers are locators rather than substitutes for `key.id`.
- Put a compact or multiline key comment immediately above a heading or list item. Prefer compact form
  when `id` and a small relation set are sufficient; use multiline form for list-valued metadata such as
  `legacy_terms`:

  ```markdown
  <!-- key: id=key.rule.verification.graph-validation -->
  - Artifact Graph가 관련되면 graph validation을 verification 후보에 포함한다.
  ```

- For a Markdown table row, keep the table intact by placing a compact comment in the first cell;
  do not insert a standalone comment between rows:

  ```markdown
  | <!-- key: id=key.acceptance.worker.planning-grouping requires_verification_of=key.claim.worker.planning-boundary --> `PA-PLAN-01` | 입력 | 기대 결과 |
  ```

- Write declared metadata only. Compute effective metadata by inheriting the parent document or section's
  `governed_by`, source authority, `document_lifecycle`, and approval by default.
  Never inherit `id` or `supersedes`. Declare item lifecycle only when it differs from the parent, and
  never use a child declaration to widen or replace parent source authority.
- When an entire decision is one replacement unit, use a decision ID. When only part of a decision is
  replaced and the rest remains authoritative, give that meaning a `key.claim.*` ID and declare
  `supersedes` from the new claim to the old claim. Do not model partial replacement as a document-level
  supersession.
- Use `legacy_terms` only on an item that has `supersedes` or an explicitly deprecated/removed lifecycle.
  Record only exact searchable former names, identifiers, routes, tables, or columns. Do not register
  broad standalone words such as `batch`, `handler`, or `plan`, and do not treat `legacy_terms` as a
  typed relation.
- Use `refs` for navigation. Use `requires_verification_of` when an acceptance criterion or claim states
  a verification requirement; reserve `verifies` for evidence performed by a test artifact or
  verification result. Use typed item relations such as `governed_by` and `supersedes` for declared
  semantics. A relation remains an impact candidate rather than automatic permission to
  edit another source surface.

Before writing metadata, inspect the parent document and section so the item declaration does not
duplicate inherited fields or conflict with their authority. If stale meaning, reverse impact,
historical exceptions, or metadata-gap interpretation is needed, preserve the approved source edit and
request Linker evidence rather than inventing a graph conclusion.

For one approved document surface, apply the source edit directly and notify Linker to invalidate or
refresh the affected discovery scope. Do not edit the external cache. Require a graph synchronization
transaction only when multiple source surfaces must change together. Downstream skills must not reuse a
stale pre-write context token.

## Temporal Metadata

- Give every new Keystone source document an immutable `created_at: "YYYY-MM-DD"` using its actual creation date.
- When Main or an authorized user accepts the current document meaning, record that result as `approval.state: accepted` with `approval.accepted_at: "YYYY-MM-DD"`. Author records acceptance; it does not invent or grant it.
- For a semantic revision, set approval to `pending` and remove the current `accepted_at` until the revised meaning is accepted. Preserve both approval and `accepted_at` for a verified non-semantic formatting change.
- Give every newly recorded decision a `결정일: YYYY-MM-DD`. Add `기록일`, `대체일`, `effective_from`, or `superseded_at` only when their distinct meaning is needed.
- Do not add a general `updated_at`. Do not infer or bulk-backfill legacy dates; use a verified repository-history date only within an explicitly approved, bounded migration.
- Use date-only values for document governance. Use a full ISO 8601 timestamp with an explicit timezone only for a separate execution event whose precise order matters.
- Never treat a newer date as higher authority. Resolve authority through lifecycle, approval, source authority, and typed relations such as `supersedes`.

## Boundaries

Do not:

1. Edit implementation code, config, schema, API, tests, generated files, code anchors, or `skills/**`.
2. Create user decisions, change scope/acceptance/status semantics/source authority, or approve project meaning.
3. Perform deep Artifact Graph interpretation or orchestrate workers and reports.
4. Require mandatory routing payloads, project-local Author standards, or a particular workspace/worktree strategy.
5. Overwrite existing changes or migrate/rename paths without explicit authority.

If delegation would help, Main may ask the user. Coordinator requires permission for that work scope;
direct Coordinator invocation counts as permission. Source-write-free Linker analysis and mutation
planning may be used without separate approval, but it grants no edit authority.

## Handoff and Output

Keep `author_edit_contract` and `author_patch_report` agent-facing. A report may include:

```yaml
author_patch_report:
  contract_id:
  routing_context_ref: # optional
  edits:
    - path:
      section:
      change_type: create | revise | progress_update | decision_record | index_update
      reason:
      source_decision:
  no_edit_candidates: []
  progress_updates: []
  graph_handoff_result:
    source_document_metadata_applied:
    document_item_metadata_applied:
    metadata_gap_candidates_deferred:
    output_artifact_changes_deferred:
    linker_report_required:
    document_delta:
    graph_sync:
      disposition: required | not_applicable | deferred
      reason:
      transaction_id:
      state:
      transaction_ref:
      resume_point:
  verification:
    checks: []
    result:
  residual_risk:
  recommended_next_action:
```

Apply the Payload Disclosure Gate before responding. By default, do not print raw `*_output`, `*_result`, `*_report`, `worker_assignment`, or `keystone_routing_decision` blocks. Summarize changed documents, intentional no-edit candidates, verification, residual risk, next action, and key sources. Show the full payload only when the user requests it or handoff/audit/debug/verification actually needs it.

## Stop Conditions

Stop or request the appropriate handoff when:

1. The document root, target, edit scope, or source authority remains unclear.
2. A required user decision or unresolved source conflict affects the edit.
3. Existing changes could be overwritten.
4. The task requires non-document surfaces or destructive migration.
5. Index/progress/decision impact cannot be bounded safely.
6. Formal delegation is needed but Coordinator permission is absent.

## Verification

Check that:

1. The installed contract works without project-local skill standards.
2. Init handoff preserves and resumes the original request.
3. Only source documents changed and existing edits were preserved.
4. Relevant links, indexes, Context Map, identifiers, decisions, and statuses remain consistent.
5. New or changed independent items have stable, unique IDs when admission rules require them; heading
   and list comments are immediately above their target and table-row comments remain in the first cell.
6. Item relations resolve to declared targets where the approved source set can establish them;
   `id`/`supersedes` are not inherited, partial supersession uses claims, and `legacy_terms` satisfies its
   lifecycle or supersession restriction without broad generic terms.
7. New documents have immutable creation dates, accepted meaning has a traceable acceptance date, and new decisions have decision dates without speculative legacy backfill.
8. Rounds and steps follow `R001`/`S01`, with only the R000 foundation exception.
9. No mandatory routing, host mode, profile, or workspace strategy was introduced.
10. The default response hides structured payloads while preserving material risks and status.
11. Structured dependencies and `work_gates` use separate relation/execution fields, valid targets and
    step IDs, and do not cause automatic work-state changes.
12. Main acceptance automatically starts finalization; all active Steps are represented as a list,
    early work has no status effect, every impact candidate has a disposition, and no live source keeps
    a singular current-step claim.
13. The bundled validator command exists, returns parseable diagnostics, and exits `0` before required
    finalization completes; unavailable or failed execution remains fail-closed and resumable.
14. Graph-relevant document deltas automatically reach Linker; Author attests and applies only its own
    baseline-matched patch and never declares verified independently.
15. New finalization uses schema version 4, separates execution and approval transitions, validates
    every accepted Progress and four-source global state, records graph_sync disposition, and accepts
    only bundled verified transaction evidence for required synchronization.
