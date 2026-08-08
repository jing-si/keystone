---
name: keystone-coordinator
description: "Provide bounded Keystone context, execute directly when no external coding skill is selected, or orchestrate an external-skill worker when one is selected. After implementation, supervise document, metadata, graph, verification, and finalization closure with Linker and Author while Main retains acceptance. Direct invocation grants permission only for the current scope."
---

<!-- keystone: id=key.skill.coordinator kind=output_artifact artifact_kind=skill_source -->
<!-- keystone: produced_from=key.work.skill-runtime-implementation.order -->
<!-- keystone: governed_by=key.standard.project key.standard.skill.coordinator -->

# keystone-coordinator

## Purpose

Turn recovered work steps, Main context, Reader briefs, Linker reports, and Author Change Sets into a
bounded execution context. When no external coding skill is selected, perform the approved repository
work directly under the default bounded-worker contract. When an external skill is selected, delegate
implementation to that worker and remain the orchestration and supervision owner.

After either execution mode, collect every changed surface and drive the Keystone closure workflow:
actual-state review, verification, Linker graph classification or synchronization, Author-owned source
document and metadata updates, Main acceptance readiness, and post-acceptance finalization.

Treat source documents and accepted decisions as project authority. Treat Coordinator payloads as runtime handoff records only. Never interpret worker `DONE` as Main acceptance.

## Runtime Authority

Use this installed package as the complete Coordinator runtime contract. Do not require a consuming project to contain `standards/skills/coordinator/**` or any other project-local skill standard. When such documents exist in the Keystone source repository, treat them as development specifications, not runtime prerequisites.

Read project-local documents only for project context:

1. User request and current Main task.
2. Configured document root and active round/work state, when present.
3. Relevant project standards, work order, progress record, and accepted decisions.
4. Reader brief, Linker report, Author Edit Contract, or Change Set, when relevant.
5. Completion criteria, verification expectations, existing-change risk, and host constraints.

## Permission Gate

Obtain user permission for each work scope before using Coordinator. Treat direct invocation of `$keystone-coordinator` as permission for the request's current scope.

- Do not ask again for assignment, review, verification, or repair inside the same scope.
- Ask again before meaningful scope or risk expansion, including new sensitive data, destructive changes, public release, external cost, or changed authority.
- Do not treat invocation of an external coding skill alone as Coordinator permission.
- A direct invocation may use `direct_execution` for small, bounded work without an external coding skill.

## Permissionless Linker Boundary

Coordinator permission governs file-changing worker delegation and scope-bearing orchestration. An
internal Linker scan, index refresh, graph interpretation, or validation with no source-write authority
does not require Coordinator permission.

1. Permissionless Linker is not a Coordinator worker. It cannot patch source, expand scope, create a
   worker, decide project meaning, or accept results.
2. Before an assignment, reuse a fresh Reader context token. If required artifact context is absent,
   request Linker's lazy repository scope and include its bounded evidence in the Context Pack.
3. After a file-changing worker report, invalidate the affected discovery scope. Review and verification
   use refreshed context, not the stale pre-write index.
4. Keep a small approved anchor update on one repository surface in that surface owner's direct lane.
   Require graph synchronization only when multiple source surfaces must change together.
5. Apply conflict-reason retry conditions and a new transaction ID with attempt history. Repository
   coverage debt does not widen the assignment or replace transaction scope validation.

## When To Use

Use Coordinator, with permission, when one or more of these are needed:

1. Delegate a recovered work step as a bounded Goal unit.
2. Coordinate multiple workers or distinct implementation, review, and verification assignments.
3. Build a Context Pack with explicit authority, scope, forbidden changes, verification, and return-report requirements.
4. Inject a requested domain or coding skill without letting it replace Keystone boundaries.
5. Convert a Linker report or Author Change Set into assignment context or reviewer focus.
6. Review worker reports and choose an accept candidate, repair, review, verify, escalate, or block action.
7. Preserve formal work state across delegation while Main retains final acceptance.
8. Execute bounded code/config/schema/API/test work directly when the user invoked Coordinator and no
   external coding skill is selected.
9. Ensure an external worker's implementation is not considered complete until required Keystone
   document, metadata, graph, and verification closure is ready for Main acceptance.

## When Not To Use

Do not use Coordinator when:

1. The request is not invoking Coordinator and Main can safely complete a small, clear task directly.
2. The main task is source-document scope design or authoring; use Author.
3. A high-impact user decision is missing; use Clarify for one actual decision topic.
4. The main task is read-only Keystone navigation; use Reader.
5. Artifact impact, stale, or gap evidence needs interpretation; use Linker first.
6. The current work, completion criteria, scope, authority, or verification path cannot be recovered.
7. A document workflow lacks an Author Edit Contract or approved edit scope.
8. The work cannot be bounded without overwriting existing changes or expanding authority.

## Fail-Soft Recovery

Do not invent an active round, work ID, active Step, source authority, or acceptance criteria.

When context cannot be recovered, do not create a worker assignment. Report what is missing and recommend the narrowest next action:

- Use Init when Keystone is uninitialized or partially initialized and the user permits initialization or repair.
- Use Reader when Keystone documents exist but active work navigation is unclear.
- Use Author when a work order, Change Set, or document edit scope must be created or revised.
- Use Clarify only when an actual user decision blocks recovery.
- Return to Main for a small direct task or when no delegated workflow is warranted.

Absence of a project-local Coordinator standard is never a missing-context error.

## Required Execution Context

Before assigning a worker, recover or establish:

1. User-approved work scope.
2. Goal and completion criteria.
3. Purpose and authority.
4. Read scope, allowed edit scope, excluded scope, and conditional scope.
5. Applicable project sources and accepted decisions.
6. Forbidden changes and stop conditions.
7. Verification path and expected report.
8. Existing user or agent changes that must be preserved.
9. Injected skill contract.
10. Execution constraints supplied by the user, injected skill, or host.
11. Pre-implementation Linker graph context and any pending graph transaction when implementation or
    anchor meaning is graph-relevant.
12. A Main context checkpoint preserving global intent, accepted decisions, current work identity,
    source conflicts, and scope boundaries.

Include `routing_context_ref` only when multiple surfaces, an authority boundary, or an audit requirement makes an explicit routing record useful. Do not require a routing payload for ordinary assignments.

## Execution Modes

Choose exactly one mode before implementation:

1. `direct_execution`
   - Use when no external coding skill is selected.
   - Coordinator applies the `keystone-default-bounded-worker` contract to its own bounded repository
     edits and produces the same canonical report required from a delegated worker.
2. `orchestration`
   - Use when one or more external coding skills are selected.
   - Coordinator provides the Context Pack and delegates implementation. It does not duplicate the
     worker's implementation edits.
   - External orchestration procedures may propose task decomposition, but Coordinator owns every
     assignment and review boundary. Injected skills do not create unsupervised child workers.

External-skill `DONE`, task complete, review clean, commit-ready, or branch-ready is worker evidence
only. None of these values changes Keystone work status, grants Main acceptance, or completes
finalization.

## Pre-implementation Context Provisioning

Before direct work or delegation, create one bounded Context Pack that combines:

1. `main_context_checkpoint` with user intent, accepted decisions, scope, exclusions, and preserved
   existing changes.
2. Current round, Work, all active or assigned Step refs, dependency gates, completion criteria, and
   verification expectations.
3. The relevant source documents and applicable standards, not an unbounded corpus dump.
4. Reader recovery evidence when work state or navigation was recovered.
5. Linker artifact context, reuse/test candidates, metadata gaps, and any pending graph transaction
   when artifact meaning is relevant.
6. Author Change Set or document-edit boundary when source documents may need to change.

Do not start implementation while required context is missing or blocked. Main-provided context and
Keystone evidence are complementary and must survive the worker handoff.

## Workflow

1. Confirm permission for the current work scope.
2. Recover the document root, active round, work ID, all equal `active_steps`, recorded `early_work`,
   and workflow state when Keystone-managed work is claimed. Never collapse multiple active Steps into
   a primary Step, and never treat early work as activation.
3. Extract Goal, Scope, Source Context, Completion Criteria, Stop Conditions, Verification, and Expected Output.
4. Extract forbidden changes and accepted decisions from available project sources.
5. Recover dependency evaluations for every assigned or active Step and work completion. Keep semantic
   `depends_on` relations separate from `work_gates`; use structured evidence before legacy HTML.
6. Use a Linker report when artifact relations, impact candidates, stale/gap risks, reuse candidates, or anchor changes materially affect the assignment.
   Preserve its document-item and claim IDs, partial-supersession boundaries, legacy-term stale candidates,
   and metadata-gap classification without reinterpreting them.
7. Decide whether the work can be bounded and select `direct_execution` or `orchestration`.
8. Select a purpose and authority: `investigate/read_only`, `document_edit/bounded_edit`, `implement/bounded_edit`, `review/review_only`, or `verify/verification`.
9. In direct execution, use `keystone-default-bounded-worker`. In orchestration, select the explicitly
   requested or applicable external skill contract.
10. Keep `injected_skills` non-empty for every actual worker assignment.
11. Record only execution constraints supplied by the user, injected skill, or host; do not choose an isolation or concurrency strategy on Keystone's behalf.
12. Create the bounded execution record. Execute it directly or deliver the assignment and Context Pack
    to the external-skill worker according to the selected mode.
13. Inspect the returned report and actual state for scope, forbidden changes, verification, source conflicts, and preserved Main context.
14. When item-level metadata is in scope, reconcile changed item/claim IDs, metadata sync, legacy-term
    findings, and required verification closure against the supplied Linker or Author handoff.
15. Normalize direct or external output into the canonical worker report, including one artifact delta
    for every changed surface.
16. Complete the post-implementation Keystone closure gate below.
17. Choose the next action: accept candidate, repair, review, verify, escalate, or block.
18. Let Main make the acceptance decision. After that decision, route the accepted Step evidence to
    Author's `acceptance_finalize` runtime automatically; do not wait for another user command.

A required active-Step gate in `waiting` state blocks that Step's implement assignment, but may allow
bounded `investigate` or `verify` work. Treat optional gates and work-completion gates according to their
declared scope. Route `unresolvable`, `invalid`, and `unknown` to Main, Author repair, or Linker evidence;
never use dependency evaluation alone to mutate progress, cancel work, or grant acceptance.

When an accepted Step's required `finalization.state` is not `complete` or explicitly `waived`, block
only the same Work's next implement assignment, transition to `in_progress`, next-Step Main acceptance,
and Work closure. Continue independent Work, equal active Steps, finalization repair, investigation,
review, and verification. Coordinator does not run source edits, reinterpret validator diagnostics as
acceptance, or mark finalization complete.

## Post-implementation Keystone Closure

Normalize direct and delegated implementation output into one closure record. A report is incomplete
until it contains changed files, one `artifact_delta` per changed surface, scope and forbidden-change
checks, verification evidence, and explicit document, metadata, and graph sync dispositions.

For each sync category use:

```yaml
sync_result:
  disposition: required | not_applicable | deferred
  state: complete | verified | not_applicable | pending | blocked
  reason:
  evidence: []
```

Apply these gates:

1. Ask Linker to classify every artifact delta. Coordinator never turns a worker's graph guess into a
   canonical relation.
2. Route required source-document or document-item changes to Author. Coordinator supervises the
   handoff but does not take Author's source-write authority.
3. Route required repository anchor patches through Linker's canonical mutation and the owning
   repository surface. Required graph sync closes only at `verified`.
4. A `not_applicable` disposition requires a concrete reason and evidence. Missing fields are not an
   implicit no-change result.
5. A `deferred`, pending, blocked, unclassified, or evidence-free required disposition prevents
   `accept_candidate`.
6. External-skill success never overrides this gate. Repair or collect evidence until pre-acceptance
   closure is complete, or report the actual blocker.
7. After Main acceptance, route Author finalization. Only `complete` or explicitly `waived`
   finalization with acceptance evidence produces Coordinator `closure_complete`.

Run the package-local validator described in
[references/closure-validator.md](references/closure-validator.md). It is diagnostic-only: it does not
edit sources, decide graph meaning, grant acceptance, or complete Author finalization.

New authority-bearing validation uses Coordinator assignment and closure manifest schema v3. Before
execution, persist an immutable validator assignment projection outside the repository source tree when
possible. It contains the assignment ID, execution mode, purpose, authority, exact goal, bounded Context
Pack, injected skill IDs/modes, normalized scope, a normalized `snapshot_policy`, and the root
`document_root` and `assignment_phase`. Snapshot policy and canonical repository snapshot are independently parsed schema-v3
objects. The assignment phase holds one complete, stable repository snapshot with a distinct
assignment-owned `expected_absences` collection inside that canonical snapshot. Existing entries
distinguish regular files, directories, and symlinks; regular-file raw bytes, executable bit, symlink
target, both path-set counts/digests, completeness, truncation, and stable-capture evidence are
authority-bearing.

Create that T0 snapshot with the package-owned `scripts/capture_assignment_snapshot.py` before any
worker write, then run the same entrypoint at worker, pre-acceptance, and post-acceptance boundaries.
Its diagnostic envelope remains schema v1 and embeds canonical repository snapshot schema v3 plus an
external single-link `{path,digest}` capture reference. Each capture binds repository/policy,
assignment ID, Context Pack digest, phase, snapshot/evidence parents, result snapshot, current package
command digest, disjoint evidence root, fresh nonce and a strictly increasing UTC time. It also binds
the canonical non-circular assignment authority core (every assignment field except
`assignment_phase`) so later scope/actor reassignment cannot reuse a capture. Each receipt is
HMAC-authenticated with an independently pinned, external owner-private Coordinator key. Embed the exact
T0 snapshot and reference in the immutable assignment bytes. The HMAC proves protected-key possession,
not independent binary execution, clock, OS-user or organizational identity.

After execution, invoke the validator with `--root`, `--assignment`, `--manifest`, and an existing
host-controlled external `--evidence-root`. The schema-v3 manifest links `worker_phase`,
`pre_acceptance_closure_phase`, and, after Main acceptance, `post_acceptance_phase`. Every non-root phase
binds its baseline snapshot digest to the previous phase result, records a complete result snapshot, and
attributes every changed path and artifact delta to one authorized writer. The worker report owns only
the worker phase. Author and repository-surface-owner writes are separate actor deltas; Linker supplies
classification, transaction, or validation evidence and never a source-write delta. The current root
must equal the terminal declared phase result, so an unrecorded inter-phase generation fails closed.
The assignment `document_root` must equal actual project configuration (or the standard default), and
Author scope must remain below it. Worker and repository-owner edit scopes cannot overlap that document
root. Explicit `document_root: .` is ambiguous with every other repository surface, so every write
actor scope must be empty until a deterministic document-surface registry exists.
Post-acceptance completion additionally binds the schema-v5 manifest,
Author runner envelope, post snapshot, and non-empty Author finalization delta. Before Author writes,
Main uses `scripts/record_acceptance_event.py` with a distinct pinned Main key. The exact evidence chain
is pre-capture digest -> Main acceptance-event digest -> post-capture digest; pre validation does not
require or receive the Main key. The acceptance runner reads the canonical pre snapshot from the
external evidence root and performs a fresh complete capture with the same policy and expected
absences. It emits no event unless the observed wire and digest equal the pre snapshot, so an Author
write cannot be moved retroactively across the Main boundary.

The validator checks actual baseline/resulting digests and actor-specific allowed/excluded scope, binds
report/review to assignment and Context Pack digests, matches `skill_usage` to injected skills, and
applies work-completion gates when `closure_target: work`. A Step closure names one assignment-scoped
`closure_step_ref`; Step-only and Work-only gate projections remain in their matching arrays, and
misfiled or duplicate gates fail closed. Required graph sync still accepts only a Linker graph
transaction schema v2 and invokes the package-owned Linker runner. Graph and Author manifest digest,
parse, and child-runner input must all use one stable captured byte generation. Every post-acceptance decision still
invokes the package-owned Author runner against canonical Author finalization schema v5.
Canonical transaction v2 remains unchanged and, by itself, proves only structural/replay validity and
current after-state. New required graph-sync authority needs canonical graph-validation manifest v2
with exact required fields `schema_version`, `sources`, `transaction`, `application_evidence` and only
optional `scope`, `coverage`. Manifest schema v1 remains historical/structural and cannot authorize a
new schema-v3 closure. The external aggregate's `transaction_digest` is computed only over the exact
immutable plan projection `schema_version`, `transaction_id`, `scope_ref`, `input_deltas`,
`canonical_mutations`, and `surface_patches`; apply-time `reconstruction` is excluded.

Require one HMAC-authenticated owner receipt for each applied required or optional patch and none for an
omitted optional. After a fresh passing Linker run, bind aggregate and receipt assignment IDs/digests to
the immutable assignment. Allow receipt phases only in `pre_acceptance_closure` then `post_acceptance`
order. Bind the former to its phase baseline and `worker_phase.capture_evidence.digest`, and the latter
to its phase baseline and `post_acceptance_phase.acceptance_event.digest`. Map owner `author` to actor
`author` and owner `main | coordinator` to actor `repository_owner`; rebuild scope as exact
`{allowed: allowed_edit_scope, excluded: excluded_scope}`. Reconstruct the entire owner request and
require its signed `request_digest`, phase/scope/root/transaction bindings, raw receipt chain, and the
one exact same-phase graph-relevant actor delta. See
[references/closure-validator.md](references/closure-validator.md) for the frozen wire.
Schema-v3 `not_applicable` is equally executable: record canonical classification input/output raw-byte
digests, exact delta-set and source-generation digests, and the runner-envelope digest. Coordinator
rebuilds the input from every worker/pre/post artifact or document delta and freshly invokes the canonical
sibling Linker `run_graph_classification.py` under isolated Python. Recorded and fresh strict schema-v1
outputs must be equal and both say `not_applicable`. Hand-written JSON, omitted/stale deltas, stale source
generation, caller `graph_relevant: false`, runner substitution, and malformed success envelopes fail.
The strict output also maps every excluded delta locator to the exact inspected source indexes and
`added_plain_unowned_source`; an empty set is the only case with `empty_delta_set` and no mapping.

Coordinator manifest schemas v1 and v2 remain readable for historical diagnostics, but neither can
authorize a new `accept_candidate` or `closure_complete`. Do not rewrite accepted v2 evidence; restart
unfinished authority-bearing work from a freshly captured v3 assignment because completeness and phase
provenance cannot be inferred retrospectively. The diagnostic envelope remains schema v1. Missing
roots/evidence, unavailable runners, timeouts, malformed output, and child runner execution errors remain
diagnostic `error` rather than an ordinary closure finding. Coordinator evidence strings never
substitute for these checks.

## Artifact Delta and Graph Synchronization

Within an already permitted implementation scope, collect one `artifact_delta` for every changed
repository behavior, artifact meaning, or anchor. Direct execution uses the same contract without a
delegated assignment. A graph-relevant delta invokes Linker classification as direct refresh
or multi-surface synchronization;
this does not create Coordinator permission, widen scope, raise worker authority, or grant acceptance.
A safe `not_required` assessment for a non-relevant delta records a concrete reason outside the
canonical delta and maps to finalization `not_applicable`.

```yaml
artifact_deltas:
  - kind: artifact_delta
    source_surface:
    change_kind: added | modified | deleted | type_replaced
    changed_locators:
      - path: src/example.py
        symbol: Example.run
    semantic_summary:
    baseline_digest: sha256:<64-lowercase-hex> | absent
    resulting_digest: sha256:<64-lowercase-hex> | absent
    graph_relevant: true | false
graph_attestations:
  - patch_id:
    owner: main | coordinator
    decision: confirm | reject | needs_revision
    evidence:
graph_apply_results:
  - patch_id:
    result: applied | failed | stale_baseline
    resulting_digest:
    evidence:
```

`changed_locators` is a non-empty array of canonical locator objects. Every locator requires
`path`; omit unused optional `heading`, `symbol`, `test_name`, `config_key`, and `schema_name`
fields. Plain locator strings are historical schema-v1 input only and cannot authorize schema-v3
closure.

Linker alone decides canonical mutations and exact patches. Coordinator or Main attests only the
repository patch it owns; document metadata patches go to Author. A confirmed patch may be assigned or
applied only inside the existing approved scope and after its raw-byte SHA-256 baseline is rechecked.
Never write a stale baseline. Preserve each result and partial success as `partially_applied`.

Apply a confirmed `owner: main | coordinator` patch only through the package-owned runner:

```sh
python3 scripts/run_owned_surface_apply.py \
  --root ROOT --request REQUEST --evidence-root EVIDENCE_ROOT --output RECEIPT \
  --authority-key EXTERNAL_OWNER_KEY --pinned-key-sha256 sha256:...
```

The exact canonical request-v1 fields are `schema_version`, `transaction_id`, `transaction_digest`,
`assignment_id`, `assignment_digest`, `phase_id`, `phase_baseline_snapshot_digest`,
`phase_parent_evidence_digest`, `repository_root_digest`, `owner`, `scope`, `scope_digest`,
`prior_receipt_digest`, and `patch`; `scope` is exact `{allowed,excluded}`, and `patch` is the complete
transaction-v2 patch object. The runner performs baseline check, write, reread and receipt creation as
one operation; failure rolls back safely where possible and leaves no receipt. It accepts only
`owner: main | coordinator` with `code_anchor | config_anchor | schema_anchor | api_anchor | test_anchor`
or a non-document source's `companion_metadata`. Its diagnostic envelope maps pass/fail/error to exit
`0/1/2`.
For an existing target, same-directory atomic exchange preserves the displaced live entry and compares
its exact bytes/type/identity with the planned baseline. If the OS/filesystem exchange primitive is not
available, fail with `atomic_exchange_unavailable` and leave source and receipt unauthoritative.
Rollback and receipt cleanup never unlink a public name directly: atomically move it with no-replace to
a same-directory high-entropy quarantine, delete only a private entry matching the recorded
runner-owned identity/bytes/mode, and restore or preserve every mismatch as recovery evidence while
failing with `rollback_failed`.

Closure validation uses `scripts/validate_closure.py` with `--manifest MANIFEST`, `--root ROOT`,
`--assignment ASSIGNMENT`, `--evidence-root EVIDENCE_ROOT`, capture/acceptance key flags, and repeatable
`--owner-key OWNER=PATH` plus `--owner-key-sha256 OWNER=sha256:...`; it also accepts
`--linker-runner`, `--author-runner`, and `--timeout-seconds`. Capture, acceptance, and distinct applied
owner lanes require distinct external pinned keys outside repository/evidence roots. The trusted-host
HMAC proves exact bytes and protected-key possession, not independent execution, external time,
OS-user/organization identity, or protection from a later authorized write.

For schema-v2 transactions, every canonical mutation has a required owning patch and a mutation-bearing
optional patch is invalid. Optional patches are ancillary only. Omission does not block completion, but
an actually applied optional follows the same owner-confirm, apply-time baseline,
expected/resulting/current digest, resume, and final verification rules as a required patch. Canonical
mutation objects use only `operation`, `entity`, `before`, `after`, `evidence`, and
`direct_relation_reason`; direct input cannot bypass Linker relation/lifecycle/surface policy.

Resume verifies recorded resulting digests for successful patches and baselines for remaining patches,
without blind reapplication. Rejected or revision-needed attestations and stale baselines are
`conflicted`; failed apply is `failed`. Linker creates a new attempt with a new transaction ID, preserved
attempt history, and conflict-reason-specific baseline/mutation/patch changes. Coordinator may prepare
`accept_candidate`, but only Linker reconstruction plus the
bundled mechanical validator can make the transaction `verified`; Main retains acceptance and Author
retains finalization authority.

## Execution Environment

Treat `execution_environment` as constraints received from the user, an injected skill, or the host. Keystone does not prescribe worktree, branch, workspace layout, worker count, concurrency, or integration strategy.

Require each worker to:

1. Stay within the allowed edit scope.
2. Preserve existing user and agent changes.
3. Never overwrite, revert, normalize, or clean unrelated changes.
4. Avoid destructive workspace operations without explicit user permission.
5. Report actual conflicts rather than choosing an unapproved resolution.
6. Include changed files, scope check, forbidden-change check, verification, and conflicts in the report.

## Injected Skill Contract

Use injected skills as bounded guidance. They never increase authority or replace the assignment's goal, scope, forbidden changes, execution constraints, verification, or report contract.

- Use `keystone-default-bounded-worker` when no other skill applies.
- When the user explicitly requests an external skill, inject it with the narrowest applicable mode.
- Do not inject the default contract redundantly when an external skill already provides the worker procedure; retain all assignment boundaries.
- If an injected procedure requires authority, scope, external state, publishing, dependency changes, or additional workers beyond the assignment, require a `NEEDS_SCOPE_CHANGE` or `NEEDS_CONTEXT` report. Coordinator may translate an approved decomposition into separate bounded assignments; the injected worker may not create them independently.
- Require the report to identify the skill, mode, outputs used, and limits encountered.

Default contract:

```yaml
injected_skill:
  skill_id: keystone-default-bounded-worker
  mode: default
  authority_ceiling: assignment_authority
  allowed_use:
    - assignment-local planning
    - provided context and read scope
  required_output:
    - skill_usage
    - scope_check
    - forbidden_change_check
    - verification
    - residual_risk
  forbidden_use:
    - scope expansion
    - authority escalation
    - unsupervised child subagent creation
    - Main acceptance
  stop_conditions:
    - missing source context
    - unclear scope or authority
    - missing verification path
```

## Output Contract

Use the following shape for an actual worker assignment. Omit `routing_context_ref` unless its stated conditions apply.

```yaml
worker_assignment:
  assignment_id:
  execution_mode: direct_execution | orchestration
  # routing_context_ref: optional; include only for multiple surfaces, authority boundaries, or audit
  goal:
  completion_criteria:
  intent_summary:
  purpose: investigate | document_edit | implement | review | verify
  role_hint:
  authority: read_only | bounded_edit | review_only | verification
  source_documents:
  accepted_decisions:
  applicable_standards:
  context_pack:
    main_context_checkpoint:
    work_context:
      round_ref:
      work_ref:
      step_refs: []
    source_documents: []
    applicable_standards: []
    accepted_decisions: [] # explicit; [] means no accepted decisions apply
    completion_criteria: []
    scope_boundaries:
      read_scope: []
      allowed_edit_scope: []
      excluded_scope: []
    forbidden_changes: []
    verification_expectations: []
    artifact_context:
      status: ready | not_applicable | blocked
      evidence: []
      anchor_change_context:
        allowed_anchor_changes:
          - artifact_id:
            surface: code_anchor | config_anchor | schema_anchor | api_anchor | test_anchor
            relation:
            reason:
            linker_report_ref:
        forbidden_anchor_changes:
        verification_required:
    reader_context:
      status: ready | not_applicable | blocked
      evidence: []
    author_context:
      status: ready | not_applicable | blocked
      evidence: []
    required_sources:
    optional_sources:
    reuse_candidates:
    test_candidates:
    document_sync_candidates:
    metadata_sync_risks:
    affected_item_or_claim_ids:
    partial_supersession_boundaries:
    legacy_term_stale_candidates:
    metadata_gaps:
    dependency_status:
    active_step_gates:
    work_completion_gates:
    graph_transaction_ref:
    allowed_graph_patch_ids:
  injected_skills:
    - skill_id:
      mode:
      authority_ceiling:
      allowed_use:
      required_output:
      forbidden_use:
      stop_conditions:
  scope:
    read_scope:
    allowed_edit_scope:
    excluded_scope:
    conditional_scope:
  forbidden_changes:
  stop_conditions:
  verification:
    required_closure:
      - target_item_or_claim_id:
        expectation:
        evidence_required:
  execution_environment:
    constraints:
    supplied_by: user | injected_skill | host | combined
  return_report_contract:
    artifact_deltas:
    document_sync:
    metadata_sync:
    graph_sync:
    graph_attestations:
    graph_apply_results:
    graph_resume_evidence:
```

Use `context_pack.main_context_checkpoint` to preserve global intent, accepted decisions, current work
identity, source conflicts, scope boundaries, and Main acceptance ownership across handoffs. The Context
Pack must explicitly carry its accepted-decisions array (use `[]` only when none apply), completion
criteria, scope boundaries, forbidden changes, verification expectations, and artifact/Reader/Author
context status plus evidence. `ready` and `not_applicable` require evidence; `blocked` prevents readiness.

The rich `worker_assignment` above remains the agent-facing handoff. The schema-v3 closure validator
uses a strict immutable projection with only the fields defined by the validator reference, including
the assignment identity and authority, `context_pack`, injected skill IDs/modes, normalized `scope`,
`snapshot_policy`, and root `assignment_phase`. The full worker report is projected only into
the strict top-level `worker_report` and validated only against `worker_phase`; it cannot claim later
Author, repository-owner, Linker, acceptance, or finalization work.
Unknown authority-bearing fields must not be smuggled into any assignment, phase, actor-delta, report,
review, snapshot, or expected-absence object.

Worker report:

```yaml
worker_report:
  assignment_id:
  assignment_digest:
  context_digest:
  execution_mode: direct_execution | orchestration
  status: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | NEEDS_SCOPE_CHANGE | BLOCKED
  status_reason:
  reason_code:
  purpose:
  authority:
  goal:
  scope_summary:
  sources_read:
  skill_usage:
    - skill_id:
      mode:
      outputs_used:
      candidates_found:
      limits_hit:
  changed_key_ids:
  changed_item_or_claim_ids:
  changed_capabilities:
  changed_files: [] # explicit; worker-phase repository changes only
  artifact_deltas: [] # explicit; one kind: artifact_delta entry per worker-phase changed file
  graph_attestations:
  graph_apply_results:
  graph_transaction_state:
  graph_resume_evidence:
  local_decisions:
    - decision:
      reason:
      evidence:
  scope_check:
  forbidden_change_check:
  verification:
  document_sync_needed:
  metadata_sync_needed:
  document_sync:
    disposition: required | not_applicable | deferred
    state: complete | not_applicable | pending | blocked
    reason:
    evidence: []
  metadata_sync:
    disposition: required | not_applicable | deferred
    state: complete | not_applicable | pending | blocked
    reason:
    evidence: []
  graph_sync:
    disposition: required | not_applicable | deferred
    state: verified | not_applicable | pending | blocked
    reason:
    evidence: []
  legacy_term_findings:
  verification_closure:
    - target_item_or_claim_id:
      result: pass | fail | not_run | inconclusive
      evidence:
  source_conflicts:
  main_context_checkpoint_check:
  workspace_conflicts:
  residual_risk:
  recommended_next_action:
```

Worker report review:

```yaml
worker_report_review:
  assignment_id:
  report_status:
  actual_state_confirmed: true | false
  scope_result: within_scope | out_of_scope | unclear
  forbidden_change_result: none | found | unclear
  verification_result: pass | fail | not_run | inconclusive
  item_metadata_result: pass | fail | not_applicable | inconclusive
  legacy_term_stale_result: pass | fail | not_applicable | inconclusive
  verification_closure_complete: true | false
  graph_sync_result:
  graph_transaction_state:
  graph_reconstruction_result: pass | fail | not_run | inconclusive
  graph_mechanical_validation_result: pass | fail | not_run | inconclusive
  graph_transaction_complete: true | false
  document_sync_result: complete | not_applicable | pending | blocked
  metadata_sync_result: complete | not_applicable | pending | blocked
  keystone_closure_stage: pre_acceptance | post_acceptance
  finalization_result: not_started | in_progress | complete | waived | blocked
  source_conflict_result:
  main_context_preserved: true | false
  reason_codes:
  review_required: true | false
  verification_required: true | false
  repair_required: true | false
  escalation_required: true | false
  coordinator_decision: accept_candidate | closure_complete | repair | review | verify | escalate | block
  main_acceptance_allowed: true | false
  residual_risk:
  next_action:
```

Keep report status separate from work-progress status. Treat `accept_candidate` as readiness for Main review, not acceptance.
`document_sync_needed` and `metadata_sync_needed` are compatibility hints only. New reports must use
the structured `document_sync`, `metadata_sync`, and `graph_sync` results above.

Only `DONE` is ready for an `accept_candidate`. `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`,
`NEEDS_SCOPE_CHANGE`, and `BLOCKED` remain non-ready until their named concern or blocker is resolved.
The worker report's `execution_mode` must match its assignment. `changed_files` and `artifact_deltas`
are explicit arrays; genuine no-change uses `[]` for both. Each worker-phase changed file has exactly
one delta with `kind: artifact_delta`, `change_kind`, baseline/resulting digests, and `graph_relevant`.
Schema-v3 validation derives every phase change set from adjacent complete snapshots instead of trusting
`scope_check` or attributing later Author/finalization writes to the worker.

For every post-acceptance decision, record acceptance separately from finalization:

```yaml
keystone_closure:
  acceptance_ref:
  acceptance_event: {path:, digest:} # schema-v3 authority; legacy schemas keep text evidence
  accepted_steps: []
  finalization:
    state: complete | waived | blocked
    acceptance_ref:
    evidence: []
    manifest_path:
    manifest_digest:
    envelope_digest:
    runner_status: pass | fail | error
    waiver_reason: # required when state is waived
```

## Current Example

```yaml
worker_assignment:
  assignment_id: r002-s02-coordinator-runtime
  execution_mode: direct_execution
  goal: Align the Coordinator runtime skill with accepted R002 standards.
  completion_criteria:
    - Coordinator permission is scoped and explicit
    - runtime does not require project-local skill standards
    - execution strategy is host or injected-skill owned
  purpose: implement
  authority: bounded_edit
  source_documents:
    - 00_docs/works/r002-bootstrap-runtime-independence/skill-runtime-implementation/key-work-skill-runtime-implementation.md
  accepted_decisions:
    - DEC-WORKS-017
    - DEC-WORKS-018
    - DEC-WORKS-019
  injected_skills:
    - skill_id: keystone-default-bounded-worker
      mode: default
      authority_ceiling: bounded_edit
  scope:
    read_scope:
      - 00_docs
      - skills/keystone-coordinator/SKILL.md
    allowed_edit_scope:
      - skills/keystone-coordinator/SKILL.md
    excluded_scope:
      - other skill sources
      - project standards
  forbidden_changes:
    - overwrite existing user or agent changes
    - destructive workspace operations
  verification:
    - validate skill package
    - check diff whitespace
  execution_environment:
    constraints:
      - preserve existing changes
    supplied_by: user

worker_report:
  assignment_id: r002-s02-coordinator-runtime
  assignment_digest: sha256:<immutable-assignment-bytes>
  context_digest: sha256:<canonical-context-pack>
  execution_mode: direct_execution
  status: DONE
  scope_check: within_scope
  forbidden_change_check: none
  verification:
    result: pass
  residual_risk: Main acceptance remains pending.
  recommended_next_action: Main reviews the diff and verification evidence.
```

## Review and Acceptance

Review every worker report against actual state, not just its claimed status.

1. Confirm completion criteria and scope.
2. Confirm that no forbidden or unrelated change occurred.
3. Confirm verification results or record why verification was unavailable.
4. Confirm that existing changes and Main context were preserved.
5. For item-level work, confirm changed item/claim IDs, partial-supersession boundaries, metadata sync,
   and legacy-term findings against Linker or Author evidence; do not interpret the graph independently.
6. Require closure evidence for each assigned item/claim verification target before treating verification
   as complete.
7. Separate source conflicts, stale work orders, stale progress records, and unpropagated accepted decisions.
8. Assign separate review or verification only when it materially improves confidence.
9. Use `accept_candidate` only when Main can make an informed acceptance decision.
10. Require complete pre-acceptance document, metadata, graph, and verification closure before
    `accept_candidate`.
11. Leave acceptance to Main. Worker `DONE`, Coordinator review, and successful verification do not independently accept work.
12. Every schema-v3 post-acceptance record, including repair, escalation, and block decisions, carries
    `keystone_closure.acceptance_ref` and a HMAC-authenticated `acceptance_event` reference. Historical
    schema-v1/v2 diagnostics retain `acceptance_evidence`. `closure_complete` also
    requires ready Context Pack/report/scope/verification/sync evidence and Author finalization evidence.
    Finalization may be `complete` or explicitly `waived`; a waiver states a concrete `waiver_reason`.

## Default User Response

By default, answer users with a concise human-facing brief instead of dumping `worker_assignment`, `worker_report`, or `worker_report_review`. Include workflow decision, goal/scope summary, verification result, Main acceptance readiness, residual risk, and recommended next action.

Keep worker assignment/report payloads as agent-facing runtime contracts. Emit the full payload only when the user asks for it, a worker handoff needs it, or audit/debug/verification evidence requires it. Optional `keystone-viewer` may render the payload, but it must not change scope, authority, verification result, report status, or Main acceptance readiness.

Before sending a user-facing response, apply the Payload Disclosure Gate: do not print raw `*_output`, `*_result`, `*_report`, `worker_assignment`, or `keystone_routing_decision` blocks by default. Summarize the payload as workflow decision, scope summary, verification result, Main acceptance readiness, residual risk, recommended next action, and key source refs; mention full payload availability only when useful.

## Boundaries

1. Own execution routing and Keystone closure supervision; do not replace Main acceptance.
2. Do not create high-impact decisions or expand accepted scope.
3. Do not design source-document edit scope without an Author Edit Contract.
4. Do not interpret artifact-graph candidates without Linker evidence.
5. Do not mark progress accepted before Main acceptance.
6. Do not choose workspace isolation, concurrency, or integration strategy on Keystone's behalf.
7. Do not let injected skills raise authority, change scope, or create unsupervised child workers.
8. Do not persist assignment or reviewer documents unless a user, audit policy, or rerun requirement needs them.

## Stop Conditions

Stop assignment or continuation when:

1. Permission for the current work scope is absent.
2. Current work, completion criteria, applicable project authority, scope, or verification cannot be recovered.
3. Work cannot be bounded into an assignment.
4. A high-risk implementation lacks the necessary Main or user decision.
5. Existing user or agent changes would have to be overwritten, reverted, normalized, or discarded.
6. `injected_skills` would be empty.
7. A new reusable artifact needs reuse discovery or Linker evidence that is unavailable.
8. An injected skill conflicts with assignment authority, scope, execution constraints, verification, or report contract.
9. Item/claim scope, partial-supersession meaning, or legacy-term stale classification requires graph
   interpretation not supplied by Linker or an accepted Author handoff.
10. A report requires source authority, acceptance criteria, status semantics, or meaningful scope/risk changes.
11. Host constraints or concurrent edits make the assignment unsafe.
12. Any changed surface lacks an artifact delta or a required document, metadata, graph, verification,
    or finalization result lacks evidence.

Apply fail-soft recovery instead of inventing missing context. Ask the user only when an actual decision or permission boundary remains.

## Verification

Verify Coordinator behavior by checking:

1. Direct invocation grants permission only for the stated work scope.
2. Permission is not repeated inside that scope and is requested again after meaningful expansion.
3. Small, clear work can remain Main direct.
4. No project-local Coordinator standard is required.
5. Worker assignment and worker report contracts remain distinct.
6. Every actual assignment has a non-empty injected skill contract.
7. External skills remain bounded guidance rather than authority or Coordinator replacements.
8. Execution constraints come from the user, injected skill, or host.
9. Existing changes are preserved and conflicts are reported.
10. Worker `DONE` remains distinct from Main acceptance.
11. Default user responses hide structured payloads while preserving decisions, scope, verification, risks, and next action.
12. Item/claim IDs, legacy-term stale risks, metadata sync, and per-target verification closure survive
    assignment, report, and review without Coordinator inventing graph conclusions.
13. Required waiting gates block only their declared implement scope, while unresolved evaluations cause
    no automatic status mutation, assignment, cancellation, or acceptance.
14. Graph-relevant repository deltas automatically reach Linker without creating permission, scope,
    assignment, acceptance, or status authority.
15. Worker/Main reports preserve owner attestations, apply results, partial resume evidence, and the
    distinction between Coordinator accept-candidate readiness and Linker-verified graph closure.
16. Direct execution is selected only without an external coding skill; orchestration is selected when
    an external skill performs implementation.
17. Main and Keystone context are both present in the bounded Context Pack before implementation.
18. External `DONE` cannot pass an incomplete document, metadata, graph, verification, or finalization
    closure gate.
19. The package-local closure validator returns a diagnostic envelope and fail-closed exit code.
20. `scripts/capture_assignment_snapshot.py` returns a passing diagnostic envelope schema v1 with one
    complete canonical snapshot schema v3 before worker execution, and immutable assignment bytes embed
    and bind that exact snapshot. Every phase receipt verifies against an independently pinned external
    Coordinator key and its preceding evidence raw digest.
21. Parent-linked worker, pre-acceptance, and post-acceptance phases derive every change from adjacent
    complete snapshots and attribute it to one authorized writer; Linker owns no source-write delta.
22. Coordinator manifest v1/v2 remains historical diagnostic compatibility while only schema v3 can
    authorize a new acceptance candidate or closure completion.
23. `scripts/record_acceptance_event.py` binds Main acceptance to exact assignment/context/policy,
    pre-acceptance snapshot, closure target, accepted Steps and a distinct pinned Main key before the
    post-acceptance Author delta. It recaptures the live root under the same policy and expected
    absences and refuses to emit the event unless that complete wire equals the pre snapshot.
