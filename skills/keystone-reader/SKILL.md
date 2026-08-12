---
name: keystone-reader
description: "Use for read-only orientation and work recovery from existing Keystone documents, including initialization-state reporting, relevant-source navigation, active work/active steps recovery, and context brief preparation. Do not use to edit files, inspect an uninitialized repository as a Keystone-specific procedure, assign workers, accept results, or perform deep Artifact Graph impact/stale/gap analysis."
---

<!-- keystone: id=key.skill.reader kind=output_artifact artifact_kind=skill_source -->
<!-- keystone: produced_from=key.work.skill-runtime-implementation.order -->
<!-- keystone: governed_by=key.standard.project key.standard.skill.reader -->

# keystone-reader

## Purpose

Read existing Keystone source documents to orient the main agent, find relevant standards and work
records, recover active work, and prepare a concise context brief. Remain read-only.

This installed contract is self-contained. A consuming project does not need a project-local Reader
standard or `standards/skills/reader/**`. Project source documents and accepted decisions define project
meaning when they exist; Reader output does not replace them or Main acceptance.

## Use Reader For

1. Keystone document orientation and navigation.
2. Active round, current work, zero-or-more equal active Steps, early work, and status-source recovery.
3. Finding relevant project standards, work orders, progress records, and decisions.
4. Preparing read-only context before document or implementation work.
5. Reporting mismatch between Keystone documents and repository evidence.
6. Starting docs-first context readiness and determining whether deeper owner/ref or Artifact Graph
   interpretation should pass to `keystone-linker`.

Do not use Reader to edit any file, create standards or work records, collect high-impact decisions,
assign workers, review worker reports, or accept results. Deep artifact impact, stale, reuse, and
metadata-gap interpretation belongs to Linker.

## Operating Emphasis

Choose one emphasis from the request without requiring the caller to name it:

- **Orientation**: report initialization, project meaning, active state, conflicts, and the next actor.
- **Navigation**: locate the smallest relevant standards, decisions, Work sources, and stable IDs.
- **Work preparation**: recover Goal, scope, gates, criteria, verification, and stop conditions for the
  selected Work without creating an assignment.

When no Work is active, report the empty active set and latest accepted Round. Do not invent a next
Round, priority, or Work merely to keep the workflow moving.

## Inputs and Authority

Use the user request, repository root, current instructions, available Keystone configuration, and
existing project documents. Resolve the document root in this order when evidence is available:

1. Current user instruction.
2. `.keystone/config.local.yaml`.
3. `.keystone/config.yaml`.
4. Explicit project-local agent setting.
5. A single conflict-free existing document convention.
6. Default candidate `00_docs`.

Do not require a work order, progress record, Artifact Graph, or local skill standard merely to run.
Treat absent material as unavailable context, not proof of project failure.

## Initialization Boundary

Determine state from actual settings and documents rather than a boolean flag:

- `uninitialized`: no authoritative document root or minimum Keystone structure is discoverable.
- `bootstrapping`: Init scaffold and R000 exist while the project standard is being established.
- `partial`: configuration, root, Context Map, standards/works indexes, decision record, project
  standard, or new-project R000 material exists but required parts are incomplete.
- `conflicted`: valid roots, settings, or document meanings conflict and cannot be chosen safely.
- `ready`: one authoritative root, Context Map, standards/works indexes, decision record, and accepted
  project meaning provide recoverable work context. Accepted project meaning comes from a current
  accepted project standard or an explicitly resolvable accepted baseline source. A new project also
  has an accepted R000; an adopted legacy corpus may be ready without retroactive config or R000.

Before initialization, do not create files and do not claim ownership of ordinary code, README,
configuration, or repository inspection. Main performs that general investigation without a
Keystone-specific Reader procedure.

If Reader is invoked before `ready`:

1. Report the actual state and evidence used.
2. Provide orientation only from Keystone material that exists.
3. List Keystone context that could not be recovered.
4. Suggest `keystone-init inspect`, `initialize`, or `repair` as appropriate.
5. If the user refuses initialization, make no changes and explain the resulting limits and later Init
   option.

Missing work/progress records or graph evidence alone do not make the project `partial`. Conflicting
valid document roots are a real decision topic; Reader reports the conflict without choosing one.

## Pending Revision Readiness

A pending standard revision does not change `initialization_state` by itself. Keep structural
initialization separate from whether the affected policy scope is ready to drive implementation.

1. Read the current source `approval.state` from frontmatter. Pending text is proposal and navigation
   evidence, never accepted authority.
2. Count an accepted baseline only when a current accepted source, decision, claim, or preserved
   accepted version is explicitly identified and resolvable. A Context Map or index `accepted`
   projection cannot override pending source frontmatter.
3. Report `pending_with_baseline` when that accepted baseline is resolvable. Use only the accepted
   baseline for authority and list the pending delta as non-authoritative review context.
4. Report `pending_without_baseline` when accepted history is asserted but its authoritative meaning
   cannot be recovered. Do not silently treat the pending document or repository history as the
   baseline.
5. Stop only implementation or acceptance that depends on the unresolved affected scope. Unaffected
   accepted work may continue.
6. Route `pending_without_baseline` to Author or Main to restore an explicit baseline, review the
   revision, or obtain acceptance. Do not call Init for a revision-authority gap in an otherwise usable
   Keystone foundation.
7. Report `conflicted` when two resolvable accepted meanings disagree and the conflict affects the
   request; use Clarify only if an actual user decision remains.
8. Build the view deterministically from source entries bound by stable `key.id`, path, current
   `approval.state`, and raw-byte digest. Accepted entries form the effective authority; pending entries
   are a review overlay and never replace that authority. Sort and deduplicate by stable ID and path.
9. Do not persist this readiness result, create a compatibility manifest, or rewrite project status.
   It is session context derived from source evidence.

## Resumable Finalization Candidates

When the selected Work's current Progress has `finalization.state: in_progress` and a recorded blocker,
Reader may return one read-only resume candidate.

1. A complete or waived finalization is not a resume candidate. Preserve its former blocker as history.
2. Recheck only the recorded blocker condition against current source and the current accepted contract.
   Do not rerun an obsolete producer merely because the historical record names it.
3. Classify the candidate as `blocked | resumable | unknown`. `blocked` means the condition still
   exists; `unknown` means current source cannot decide it safely.
4. Use `resumable` only with concrete evidence and record the resolution as
   `resolved_by_source_change` or `resolved_by_contract_change`.
5. Return an Author resume action containing the affected Progress, resolution evidence, the smallest
   current check to run, and remaining source synchronization. Do not execute the write action.
6. Never complete finalization automatically, change Work/Step status, or infer Main acceptance from a
   resolved blocker.
7. Do not request an external evidence folder, key, receipt, snapshot, or compatibility artifact to
   classify the candidate. If current source is insufficient, return `unknown`.

## Workflow

1. Detect initialization state and resolve or narrow the document-root candidates.
2. If present, read `key-context-map.md` first.
3. Follow the project standards and works indexes that actually exist.
4. For work recovery, read each active parent Round index and use the passing Work State projection to
   identify active children and Works. Apply the multi-active session-focus gate before opening the Work
   order/Progress for every candidate. After focus is known, follow only the selected Work's ordered
   `child_rounds`, Work order, and Progress unless the request explicitly needs a cross-Work view. A flat
   parent without `child_rounds` keeps the existing direct-Work flow. Treat a singular `current_step`
   claim as stale/conflicting evidence, not authority.
5. Use Work State schema v3 `round_hierarchy` and `active_child_rounds` for child navigation. Keep
   `active_rounds`, `active_round`, `accepted_rounds`, and `latest_accepted_round` parent-only; do not
   reinterpret a child acceptance as a global Round transition.
6. Treat document, section, and item-level `key.id`, `key.refs`, typed relations, visible row labels,
   paths, headings, and keywords as navigation evidence, not edit authority or automatic impact
   propagation. Item IDs may narrow a matched section, decision claim, acceptance criterion, or table row.
7. When code/config/schema/API/test impact, stale, reuse, or gap analysis must go beyond navigation,
   recommend Linker and pass the observed document/item IDs and locators as handoff seeds without
   confirming graph conclusions, supersession closure, legacy-term status, or inheritance validity.
8. Report source conflicts; do not silently prefer documents over operative code or vice versa.
9. Recommend the next responsible actor without editing or requiring a routing ceremony for a small,
   already-scoped task.

For work recovery, read structured `key.relations.depends_on` and `work_gates` before legacy HTML
dependency evidence. Separate gates that apply to each active Step from work-completion gates. Report
each dependency as `satisfied`, `waiting`, `unresolvable`, `invalid`, or `unknown`, with its target,
condition evidence, and blocking scope. Treat missing, cancelled, superseded, conflicting, or
insufficiently evidenced targets as fail-soft risks; never mutate work status or assign work from the
evaluation.

## Session Context Readiness

When the user explicitly invokes Reader at the start of a Codex session, Reader is the orientation and
context-readiness entry point, not the cache owner.

1. Run the package-local `scripts/work_state_runtime.py --root ROOT` first and recover initialization,
   active parent Round(s), child hierarchy, active child Rounds/Works/Steps, latest accepted parent
   Round, dependency/finalization gates, diagnostics, and source generation from its passing envelope.
   Do not replace a failed or incomplete envelope with manual pointer agreement. Use the cited
   parent/child/work indexes and active Progress for narrative context after the canonical projection
   succeeds.
2. Apply the session focus gate immediately after a passing Work State projection. When there are two
   or more active Works and the user's request does not identify one Work or ask for a cross-Work view,
   show only a compact candidate list from `active_works`: Work ref, parent/local Round, status, active
   Step refs or unresolved reason. Ask exactly one focused question about which Work to handle in this
   session. Do not read every candidate Work order or Progress before the answer. Do not start Linker
   docs readiness before the answer.
3. Treat the selection as non-authoritative session context. When the user answers, resume automatically
   with the selected Work. Never mark unselected Works inactive or lower priority, mutate project state,
   or persist the selection as a canonical pointer.
4. Skip the focus question when there are zero or one active Work, the request explicitly identifies a
   Work, or the request asks for all active Works or a cross-Work comparison.
5. After the focus gate is resolved or skipped, request permissionless Linker readiness for the docs discovery scope. Pass
   worktree identity, the sorted path set, and each file's raw-byte SHA-256 digest.
6. Request a lazy repository scope only when code/config/schema/test artifact context is actually needed.
7. Reuse a fresh external index. If it is missing, stale, corrupt, or cannot be locked or written, fall
   back fail-soft to source discovery; a cache problem is not a user decision.
8. Include the freshness token, discovery scope, source citations, and unresolved gaps in the internal
   context brief. Downstream skills may reuse a fresh token; after a source write they invalidate the
   affected discovery scope.
9. Request `include_source_views` only when the selected context needs criterion verification,
   effective Decision, or Work output/test summaries. This is a source-bound, session-only projection
   from Linker's same reconstructed `GraphSnapshot`; request repository scope when output/test targets
   are needed. Preserve its `source_generation` and unresolved diagnostics, and never treat a
   `verified` view as automatic acceptance. Default readiness remains the lighter owner/ref result.
10. Pass a serialized recursion guard with `initiator: reader`. The called Linker must not call Reader
   again in the same chain; a Linker-initiated Reader chain applies the inverse rule.
11. Keep raw readiness and index payloads agent-facing and hidden from the user by default.

## Result Contract

Keep the internal result proportional to available evidence. Include:

```yaml
reader_output:
  initialization_state:
  document_root:
  request_summary:
  project_summary:
  active_round:
  active_rounds: []
  active_child_rounds: []
  round_hierarchy: []
  active_works: []
  active_steps: []
  session_focus:
    state: not_required | selection_required | selected
    candidates: []
    selected_work:
    authority: non_authoritative
  latest_accepted_round:
  revision_readiness:
    state: not_applicable | pending_with_baseline | pending_without_baseline | conflicted
    pending_sources: []
    accepted_baseline_sources: []
    affected_scope: []
  finalization_resume_candidates:
    - state: blocked | resumable | unknown
      progress_path:
      recorded_blocker:
      resolution: unresolved | resolved_by_source_change | resolved_by_contract_change
      author_resume_action:
  early_work: []
  current_work_status:
  dependency_status:
  active_step_gates:
  work_completion_gates:
  status_sources:
  status_conflicts:
  matched_documents:
  matched_item_seeds:
  unavailable_keystone_context:
  artifact_graph_needed:
  artifact_seed_candidates:
  operational_boundaries:
  risks_and_gaps:
  recommended_next_action:
  sources_read:
  assumptions:
  context_readiness:
    discovery_scope:
    freshness_token:
    cache_status:
    recursion_guard:
```

For work preparation, also include Goal, Scope, applicable standards, completion criteria, stop
conditions, and verification when recoverable. Any handoff remains preparatory; Reader does not create
a final worker assignment.

## Default User Response

Give a concise human-facing brief with the initialization/work state, key finding, unavailable context
or conflict, recommended next action, and key sources. When multi-active session focus is required,
return the compact candidate list and one focus question instead of a deep context brief. Do not expose
the full `reader_output` or context brief unless the user requests it or a handoff, audit, debugging, or
verification need requires it.

Apply the Payload Disclosure Gate before responding: do not print raw `*_output`, `*_result`,
`*_report`, `worker_assignment`, or routing payload blocks by default. Summarize their meaning without
changing the underlying risks or recommendation.

## Boundaries and Stop Conditions

1. Never write files or change project state.
2. Never turn partial navigation evidence into a confirmed Artifact Graph relation.
3. Never interpret an item ID, `supersedes`, inherited field, or `legacy_terms` occurrence as proof of
   authority, impact, stale state, removal completeness, or a metadata gap; pass it to Linker when that
   interpretation matters.
4. Never make a high-impact project decision for the user.
5. Stop and report when conflicting valid roots prevent safe reading.
6. Stop and report when source conflict or sensitive/local-only access could change the task direction.
7. Do not stop merely because work records, progress records, graph evidence, or local skill standards
   are absent; return the useful partial result instead.

## Verification

Check that Reader:

1. Runs without a consuming-project `standards/skills/reader/**` document.
2. Produces no file changes before or after initialization.
3. Does not take ownership of general pre-initialization repository inspection.
4. Reports uninitialized, partial, conflicted, and ready evidence without guessing.
5. Recovers work when records exist and fails softly when they do not.
6. Hands deep graph interpretation to Linker.
7. Uses item IDs and their locators only to narrow navigation or prepare handoff seeds, without deciding
   partial supersession, inheritance, legacy-term stale status, or metadata gaps.
8. Hides structured payloads by default.
9. Recovers structured and legacy dependencies with explicit evaluation and scope without changing work state.
10. Starts docs-scope readiness, expands to repository scope lazily, and never becomes cache owner.
11. Treats a downstream source-owner write as invalidating the affected Reader context token and
    prevents Reader-Linker recursion in one call chain; Reader itself remains source read-only.
12. Keeps global Round identity on the parent while preserving child-local status, Work ownership,
    active Steps, declared order, and unresolved child evidence from Work State schema v3.
13. Asks for non-authoritative session focus before multi-Work deep reading, skips the question for an
    explicit or cross-Work request, and never changes unselected Work status or priority.
