---
name: keystone-reader
description: "Use for read-only orientation and work recovery from existing Keystone documents, including initialization-state reporting, relevant-source navigation, active parent Round and active Step recovery, session Round focus, and context brief preparation. Do not use to edit files, inspect an uninitialized repository as a Keystone-specific procedure, assign workers, accept results, or perform deep Artifact Graph impact/stale/gap analysis."
---

<!-- keystone: id=key.skill.reader kind=output_artifact artifact_kind=skill_source -->
<!-- keystone: produced_from=key.work.skill-runtime-implementation.order -->
<!-- keystone: governed_by=key.standard.project key.standard.skill.reader -->
<!-- keystone: derived_from=key.claim.r012.current-round-authority key.claim.r012.round-session-focus key.claim.r012.worker-step-selection -->

# keystone-reader

## Purpose

Read existing Keystone source documents to orient the main agent, prepare a concise project brief,
find relevant standards and work records, recover active work, and prepare a proportional context
brief. Remain read-only.

This installed contract is self-contained. A consuming project does not need a project-local Reader
standard or `standards/skills/reader/**`. Project source documents and accepted decisions define project
meaning when they exist; Reader output does not replace them or Main acceptance.

## Use Reader For

1. Keystone document orientation and navigation.
2. Active parent Rounds, current Works, active Steps, early work, and status-source recovery.
3. Finding relevant project standards, work orders, progress records, and decisions.
4. Preparing read-only context before document or implementation work.
5. Reporting mismatch between Keystone documents and repository evidence.
6. Starting progressive context readiness from the Context Map and accepted top-level project standard.
7. Determining whether selected-Work artifact context needs bounded owner/ref or Artifact Graph
   interpretation from `keystone-linker`.

Do not use Reader to edit any file, create standards or work records, collect high-impact decisions,
assign workers, review worker reports, or accept results. Deep artifact impact, stale, reuse, and
metadata-gap interpretation belongs to Linker.

## Operating Emphasis

Choose one emphasis from the request without requiring the caller to name it:

- **Orientation**: report initialization, project meaning, active state, conflicts, and the next actor.
- **Navigation**: locate the smallest relevant standards, decisions, Work sources, and stable IDs.
- **Work preparation**: recover Goal, scope, gates, criteria, verification, and stop conditions for the
  selected Work without creating an assignment.

When no parent Round is active, report the empty active set. Read accepted history from parent Round
sources only when the request needs it. Do not invent a next Round, priority, or Work merely to keep
the workflow moving.

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
3. Read the accepted top-level project standard in full. If the current standard is pending, apply
   Pending Revision Readiness and keep the accepted baseline separate from the proposal.
4. Follow a child-standard index only for a concrete gap in project purpose, scope, document structure,
   or authority. Do not load the child tree for completeness.
5. Prepare `project_brief` with purpose, scope, document structure, authority, and important unknowns.
6. Run the package-local Work State runtime and use its passing projection to identify incomplete parent
   and child Rounds, active Works, and Steps. When the project-local session-title hook has already
   collected an explicit existing-Round assignment, follow that selected Round. Otherwise keep Reader
   in orientation, review, investigation, or status mode without silently selecting a sole active Round.
   A flat parent without `child_rounds` keeps the existing direct-Work flow. Treat a singular
   `current_step` claim as stale/conflicting evidence, not authority.
7. Use Work State schema v5 `round_hierarchy` and `active_child_rounds` for child navigation. Keep
   `active_rounds` and `accepted_rounds` parent-only. Treat singular `active_round` and historical
   acceptance data as compatibility context that cannot select current work or reinterpret a child
   acceptance as a global Round transition.
8. When no parent Round is active, report the empty active set and next actor without opening detailed
   Work sources, repository scope, or Linker readiness. For a selected or sole Round, read its Work
   order first. Apply Worktree Targeted Navigation before reading the selected Work's Progress,
   applicable standards, feature documents, or repository artifacts.
9. Treat document, section, and item-level `key.id`, `key.refs`, typed relations, visible row labels,
   paths, headings, and keywords as navigation evidence, not edit authority or automatic impact
   propagation. Item IDs may narrow a matched section, decision claim, acceptance criterion, or table row.
10. Only when the selected Work needs artifact context, owner/ref resolution, implementation/test
    candidates, or graph-relevant impact, recommend permissionless Linker readiness with the Work or
    document ID as its bounded anchor. Do not invoke Linker merely because Reader was invoked for initial
    orientation. Use a full graph only for an explicit graph audit, release verification, or scope conflict.
11. Report source conflicts; do not silently prefer documents over operative code or vice versa.
12. Recommend the next responsible actor without editing or requiring a routing ceremony for a small,
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

1. Resolve the document root and minimum initialization evidence. Read `key-context-map.md`, then read
   the accepted top-level project standard in full. Follow child-standard indexes only for concrete
   gaps in project purpose, scope, document structure, or authority. Prepare `project_brief` with those
   four fields and important unknowns before recovering current Work State.
2. Run the package-local `scripts/work_state_runtime.py --root ROOT` and recover initialization,
   active parent Rounds, child hierarchy, active child Rounds/Works/Steps, accepted parent Round history,
   dependency/finalization gates, diagnostics, and source generation from its passing envelope. Do not
   replace a failed or incomplete envelope with manual pointer agreement. Use the cited
   parent/child/work indexes and active Progress for narrative context after the canonical projection
   succeeds.
3. Apply the session focus gate immediately after a passing Work State projection. In an opted-in trusted
   project, the project-local `UserPromptSubmit` hook may already have collected either an explicit
   existing-Round assignment or a free-form review/status request before Reader starts. Honor that
   context without asking again. Do not infer selection merely because one active Round exists.
4. Treat the selection as non-authoritative session context. When the user answers, resume automatically
   with the selected Round. Keep unselected Rounds unchanged and never persist the selection in project
   source, a cache, or a canonical pointer.
5. Skip the focus question when there are no incomplete Rounds or the request asks for review,
   investigation, confirmation, status, all active Rounds, or a cross-Round comparison. With no active
   parent Rounds, report the empty set and next actor without detailed Work reading or Linker. A sole
   active Round is reported but never selected automatically.
6. After the Round focus gate is resolved or skipped, inform the user of the current in-progress Steps
   in the explicitly selected Round. Do not ask the user to choose a Step. Without an explicit Step
   request, select the lowest-numbered executable active Step using dependency evaluations and
   `work_gates`. If the lowest-numbered Step is blocked, explain the blocker and select the next
   executable Step. Do not change Step status or priority through this session choice.
7. When `.codex/config.toml` opts in, its project-local `UserPromptSubmit` hook runs the package-local
   `scripts/keystone_session_title.py --hook` before the first Reader request is accepted. A bare Reader
   request lists non-terminal parent and child Rounds in ascending parent number order, nesting each
   child immediately below its parent in Excel-column suffix order. Exclude `complete`, `accepted`, and
   `cancelled`. Show at most twenty Round entries in total and summarize the remainder as `외 N개`; never
   auto-select a sole candidate. Never emit a terminal parent as a grouping header. If only its child
   remains, render that child as a numbered entry with its full local ref.
8. Whether the candidate list comes from the hook or Reader's own fail-open response, start with
   `Keystone ready · 미완료 Round N개` and render an open-left selection box headed by
   `╭─ Round 선택`. Use one line per Round in the stable form
   `{Round ref} · {status} · {title}`, number parent or standalone entries, and prefix a nested child
   with `└─`. Separate parent groups with a blank `│` line, use no right border or width padding, and
   close with `╰─ 어느 Round에 집중할까요?`. Do not add separate Step, gate, baseline, source, or
   rationale lines to the candidate list. The pre-model hook uses the concise canonical source title.
   When Reader itself renders a fail-open list, render the title in the project's preferred language;
   if needed, translate only the title instead of adding an explanation.
9. When the user explicitly assigns an incomplete existing Round with execution language such as
   proceed, start, continue, switch, undertake, or execute, the hook uses `codex queue` to place an
   equivalent marked request back into the same session. Its title hint is `{local Round ref}:{phrase}`
   without a `프로그래스` prefix, and the phrase describes the work in the user's primary language using
   five characters or fewer.
10. Treat an explicit start of Work Order creation, writing, revision, or amendment as assignment too.
   For an existing Round, use its exact local ref. For a new child, derive the next Excel-column suffix
   from every declared child of the named parent, including terminal children. For a new parent, derive
   the next number from every declared parent. The derived ref is a non-authoritative provisional value,
   is never reserved in project source, and must be rechecked by Author immediately before the write.
11. A Round mention in dependency completion, review, investigation, confirmation, or status context is
   not assignment and receives no Keystone title hint. Free-form follow-up is queued with the original
   Reader request.
12. The hook must fail open: if Work State evaluation, temporary state, or `codex queue` is unavailable,
   allow the original Reader request to continue. Reader must never propose `/rename` or claim that a
   title changed without native confirmation. Never edit Codex SQLite, rollout, or config state directly,
   and never persist Round priority or rename another thread or project.
13. Read the selected Work order first. When its document-level `key.worktree.path` is present, confirm
   that the exact path exists, is accessible, and belongs to the same Git common directory as the current
   repository. Restrict subsequent selected-Work navigation to that exact path. When the field is absent,
   use the current worktree. A missing, inaccessible, or different-common-directory value is `stale` or
   `mismatch`: report it and stop targeted navigation. Never enumerate registered worktrees or traverse
   sibling directories as fallback.
14. After resolving the execution location, read the selected Work order, Progress, applicable standards, and feature documents
   before artifact discovery. Do not treat initial orientation as an artifact-context trigger.
15. Request permissionless Linker readiness only when selected-Work artifact context, owner/ref resolution,
   implementation/test candidates, graph-relevant impact, or an explicit graph audit is needed. Anchor
   the bounded scope at the selected Work or document ID and pass the worktree identity, sorted path set,
   and each file's raw-byte SHA-256 digest. Use a full graph only for an explicit graph audit, release
   verification, or scope conflict.
16. Request a lazy repository scope only when code/config/schema/test artifact context is actually needed.
   If bounded search finds no linked implementation, report `implementation unavailable` or `possibly
   unimplemented`. Report a metadata gap only when a code candidate exists but its relation is missing.
17. Reuse a fresh external index. If it is missing, stale, corrupt, or cannot be locked or written, fall
   back fail-soft to source discovery; a cache problem is not a user decision.
18. Include the freshness token, discovery scope, source citations, and unresolved gaps in the internal
   context brief. Downstream skills may reuse a fresh token; after a source write they invalidate the
   affected discovery scope.
19. Request `include_source_views` only when the selected context needs criterion verification,
   effective Decision, or Work output/test summaries. This is a source-bound, session-only projection
   from Linker's same reconstructed `GraphSnapshot`; request repository scope when output/test targets
   are needed. Preserve its `source_generation` and unresolved diagnostics, and never treat a
   `verified` view as automatic acceptance. Default readiness remains the lighter owner/ref result.
20. Pass a serialized recursion guard with `initiator: reader`. The called Linker must not call Reader
   again in the same chain; a Linker-initiated Reader chain applies the inverse rule.
21. Keep raw readiness and index payloads agent-facing and hidden from the user by default.

## Result Contract

Keep the internal result proportional to available evidence. Include:

```yaml
reader_output:
  initialization_state:
  document_root:
  request_summary:
  project_brief:
    purpose:
    scope:
    document_structure:
    authority:
    important_unknowns: []
  project_summary:
  active_rounds: []
  active_child_rounds: []
  round_hierarchy: []
  active_works: []
  active_steps: []
  execution_location:
    source: current_worktree | work_order
    path:
    status: current | recorded | stale | mismatch
  session_focus:
    state: not_required | selection_required | selected
    candidates: []
    selected_round:
    authority: non_authoritative
  step_execution:
    in_progress_steps: []
    selected_step:
    selection_reason: user_specified | lowest_executable | next_executable_after_blocker | none
    authority: non_authoritative
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
    linker_trigger:
    anchor:
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
7. Stop targeted Work navigation when a recorded worktree path is stale, inaccessible, or belongs to a
   different Git common directory. Do not search other worktrees to repair the record implicitly.
8. Do not stop merely because work records, progress records, graph evidence, or local skill standards
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
10. Builds a project brief from the Context Map and accepted top-level project standard before Work
    State, and reads child standards only for concrete project-understanding gaps.
11. Treats a downstream source-owner write as invalidating the affected Reader context token and
    prevents Reader-Linker recursion in one call chain; Reader itself remains source read-only.
12. Keeps global Round identity on the parent while preserving child-local status, Work ownership,
    active Steps, declared order, and unresolved child evidence from Work State schema v5.
13. Lists incomplete parent and child Rounds before a bare Reader turn, never auto-selects a sole
    candidate, and preserves free-form review, investigation, confirmation, and status requests.
14. Informs the user of in-progress Steps, selects the lowest executable Step without asking, and
    explains a blocked-lowest fallback without changing Step status or priority.
15. Defers Linker during initial orientation, invokes bounded permissionless readiness only from a
    selected Work or document anchor, and expands to lazy repository scope only for artifact context.
16. Distinguishes a missing linked implementation from a relation metadata gap and uses full graph only
    for explicit audit, release verification, or scope conflict.
17. Uses a selected Work's recorded exact worktree path before artifact discovery, falls back only to the
    current worktree when the field is absent, and reports stale/mismatch without global worktree search.
18. Adds one prefix-free, five-character-or-shorter native title hint only for explicit execution of an
    incomplete existing Round or actual Work Order authoring, derives but never reserves a new Round ref,
    limits the candidate list to ten, and never persists selection or proposes a manual rename fallback.
