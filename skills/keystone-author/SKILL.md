---
name: keystone-author
description: "Create or revise Keystone source documents, standards, work orders, progress records, decisions, indexes, metadata, and Change Sets within a clear scope. Use for direct document requests and accepted Clarify results; hand off initialization when Keystone is absent. Do not use for unresolved user decisions, read-only orientation, code/config/schema/API/test edits, worker orchestration, or skill-source implementation."
---

<!-- keystone: id=key.skill.author kind=output_artifact artifact_kind=skill_source -->
<!-- keystone: produced_from=key.work.skill-runtime-implementation.order -->
<!-- keystone: governed_by=key.standard.project key.standard.skill.author -->
<!-- keystone: derived_from=key.work.decisions.dec-works-020 key.work.decisions.dec-works-034 -->

# keystone-author

## Review Policy and Step Definitions

For policy-relevant creation/closure, follow `references/management-review.md`. If mode is unset,
use the fixed package guidance, then preserve the selection. Plan a visible Round-scope connection
review Step, or full review at the top-level sprint termination. Record local Step definitions with
`key.defined_steps`; do not treat Progress step_ref as the definition or annotate unrelated old files.
Main accepts review results; Author records them and updates only processed occurrences via the state
API. Retain R027's question-by-question recording and selective-read boundaries.

## Purpose

Create and revise human-readable Keystone source documents within the user's request and accepted
decisions. Own standards, work orders, progress records, decision records, source-document metadata,
indexes, Change Sets, and approved Work-attached clarification logs. Main verifies and accepts the result.

Use this installed package as the complete Author runtime contract. Do not require a consuming project
to contain a project-local Author standard. Project documents define project meaning, while this
package defines Author behavior.

## Idea Notes Boundary

`keystone-ideas` owns direct CRUD of non-normative `ideas/key-ideas*.md` notes. Do not route
routine note edits through Author or require initialization, Work State, or graph checks for them.
For an explicit request to turn an idea into work, preserve the relevant meaning, title and recording
date in the Work Order. IDEA numbers can be reused after deletion: they are not stable graph IDs.
A note or a link to work does not authorize execution or establish completion.

## Initialization Gate

Resolve one document root and classify it as `uninitialized | partial | conflicted | bootstrapping |
ready` before editing.

- For `uninitialized` or `partial`, ask once whether to initialize or repair, hand off to Init, and
  preserve the original request and resume point.
- For `conflicted`, do not choose or overwrite. Send one material decision topic to Clarify.
- For `ready`, continue with the smallest relevant source set.
- Ordinary pre-initialization inspection of code, README, configuration, and repository structure
  belongs to Main and is valid Author input.

## When To Use

Use Author to create or revise:

1. Standards, work orders, progress records, decisions, indexes, and Context Map pointers.
2. Source-document metadata and independently addressable document-item metadata.
3. Accepted Clarify results and Main-accepted Step state.
4. A bounded Change Set when a large document-to-code/test change needs traceability.
5. A lightweight Q&A append to an approved Work-attached clarification log.

Do not use Author for code, config, schema, API, test, generated-file, skill-source edits, worker
orchestration, deep graph interpretation, or unresolved user decisions.

## Operating Modes

Select the smallest mode that fits the approved document change:

- `create`: create a new source document and its required index entry.
- `revise`: change existing accepted or pending meaning without rewriting unrelated history.
- `clarify_apply`: record one resolved Clarify decision and resume the interrupted document task.
- `clarify_log_append`: create the needed log or persist a question/answer, pending interpretation, or
  withdrawal without source application or workflow-state interpretation.
- `normalize`: align structure or metadata while preserving current meaning and authority.
- `progress_update`: record actual execution, evidence, blocker, or resume-point changes.
- `acceptance_finalize`: synchronize only the state and aggregate sources changed by Main acceptance.

Do not turn mode selection into a required routing artifact. A mode narrows the edit; it does not grant
acceptance, code-write authority, or permission to expand scope.

## Required Context

Use only the context needed for the edit:

1. User request or Main-approved instruction.
2. Document root and target documents.
3. Applicable standards, accepted decisions, work context, and current workspace state.
4. Scope, exclusions, existing-change risk, and verification expectation.
5. Linker evidence only when artifact impact, stale/gap meaning, or multi-surface graph synchronization
   is actually relevant.

A Work Order, Change Set, routing payload, external evidence directory, or finalization manifest is not
a prerequisite for a small explicit document edit.

## Workflow

1. Resolve initialization state and one document root.
2. Classify the request as `create | revise | clarify_apply | clarify_log_append | normalize |
   progress_update | acceptance_finalize`.
3. Read only the relevant project sources and preserve unrelated changes.
4. Use an Author Edit Contract only for a large or ambiguous multi-document change.
5. Edit the approved source documents.
6. Check actual impact on standards, Work/Progress, decisions, indexes, Context Map, and Change Set.
   For a changed implementation plan or a standards conflict, apply Standards Realignment During
   Implementation below before handing the affected implementation back to its executor.
7. Use Linker for graph interpretation; hand repository-output edits to Main or a permitted Coordinator.
8. Run verification proportional to the changed surface and report residual risk.

## Round Creation and Execution Boundary

Use Round and Step as the primary user-facing execution terms. A Work Order is the source document
that preserves a Round's Goal, Scope, completion criteria, and verification; do not present Work Order
creation as a separate execution phase.

Keep these three constraints invariant while allowing the Round topology to fit its Goal:

1. **Separate creation from execution.** When the user asks only to create a Round or Work Order,
   create the Round Index, Work Order, Progress, and required navigation sources as
   `planned / pending` with no Active Step. Report the created Round and stop.
2. **Use standards-first for durable production implementation.** If the Round will leave production
   code, config, schema, API, generated/codegen, or skill-source changes in the repository, place a
   standards-alignment Step before the first production implementation Step. Check intended behavior,
   scope, boundaries, verification expectations, and the accepted standard baseline. When the accepted
   standards already express the agreed meaning, record a reasoned `no_change` instead of forcing a
   meaningless edit.
3. **Verify before closure.** Before completing the Round, verify alignment among accepted standard
   meaning, the resulting implementation, and the necessary verification evidence.

Creation and execution may be authorized together. For example, `작업서 생성 이후 작업을 바로
진행해주세요` or “create the Round and proceed immediately” authorizes Author to create the Round and
then continue from its first executable Step. A later explicit request to proceed with the Round,
Step, or implementation has the same effect.

Do not infer execution authority from plan approval, acceptance of the Round's contents, a simple
positive response, confirmation that creation succeeded, or a request to revise the newly created
documents. For a document-revision request, edit only the approved document scope and keep the Round
planned unless execution is also explicit. If the intent is ambiguous, stop after creation.

The three constraints above do not impose one fixed pipeline. Step names and counts, implementation
and verification splits, and parallel independent Steps may vary by Goal. A document-only Round needs
no implementation Step. An investigation or experiment Round may end with findings and a user decision
when it does not accept durable production implementation. Any durable production implementation still
requires standards alignment before implementation and verification before closure.

## Standards Realignment During Implementation

Reassess applicable standards when an implementation plan changes its goal, scope, behavior, or
completion criteria, or when standards conflict with each other or the implementation. A completed
initial alignment Step covers only the requirements reviewed then, not later changes.

1. Identify the changed requirement or conflict and the affected standard clauses and implementation
   Steps. Distinguish a defect against a valid standard from a needed policy change. Do not rewrite a
   standard merely to legitimize the current implementation; return unresolved policy or scope choices
   to Main/User before applying them.
2. When standards need revision, add a standards-alignment Step to the existing authorized Work Order.
   Give it the normal Goal, Scope, Source Context, Completion Criteria, Stop Conditions, Verification,
   and Expected Output. Explicitly sequence it before the affected implementation resumes and record
   that implementation's blocking prerequisite. Preserve existing Step IDs and completed/accepted
   history; adding a higher-numbered Step alone does not establish execution precedence.
3. Keep the affected implementation on hold until the additional Step's standards and Work Order
   alignment, verification, and Main acceptance are complete. Unaffected independent work may continue
   within its approved scope. Register the new Step and any actual hold/resume transitions through the
   project's existing state owner; do not introduce another status store or reopen the completed
   initial alignment Step just to represent the new change.
4. Preserve the trigger and reason, target documents/clauses, before/after meaning, affected Steps,
   verification and acceptance evidence, and resume conditions in the Work Order and its durable work
   records. In managed mode, use Work Order history and the existing state API; in legacy mode use
   the applicable Progress ownership rules. Return exact record/Step references to the executor.
5. If no standard revision is needed, record the reviewed clauses and the reason in the affected work
   record without adding an alignment Step. A valid-standard implementation defect stays an
   implementation repair. A sequencing-only edit need not create another alignment Step.
6. Tell the user which additional Step was added or why standards remain unchanged, and whether the
   affected implementation is held or can resume. A chat-only completion summary is not durable evidence.

## Worktree Locator Metadata

When Coordinator or Main has created or selected a linked worktree, Author owns the canonical Work
Order metadata write before substantive repository edits.

1. Accept only an exact canonical absolute root that Coordinator or Main verified against the same Git
   common directory as the current repository.
2. Write the value as document-level `key.worktree.path` on the canonical Work Order that is readable
   from the session control plane. Do not substitute a target-branch-only copy, Progress, or an index.
3. The metadata is valid only for `doc_type: work_order`; `worktree` contains only `path`. Do not add a
   branch, HEAD, claim, lock, or registry field.
4. When no linked worktree was selected, do not add the field. Do not infer a replacement or remove a
   historical value without an accepted instruction.
5. Re-read the current Work Order after applying the edit and return the exact recorded path to
   Coordinator or Main for fresh confirmation. Author does not create or select worktrees and does not
   begin implementation edits.

## Current Acceptance and Progress Synchronization

After Main acceptance, synchronize only sources whose meaning or state changed:

1. Record the accepted Step as `work_status: complete` and `approval.state: accepted` when those
   transitions are part of the accepted result.
2. Update the owning Step Progress and Aggregate Work Progress according to the ownership contract
   below. Update round/root indexes and Context Map only when their aggregate state or active pointers
   changed.
   For a child Step, update the child Work/Progress and child Round index only; child acceptance does
   not create a global acceptance event or advance `latest_accepted_round`. Accept a parent Round only
   after every ordered declared child is resolved and locally accepted.
3. Keep sibling or future Steps unchanged. Record genuine early work with `status_effect: none`.
4. Run Work State only when Work/Step or active-pointer state changed.
5. Run Linker affected-scope reconstruction only when metadata, relation, or multi-surface canonical
   meaning changed.
6. Record only actual state, verification, residual risk, and resume-point changes in Progress.

Current completion does not require a new finalization manifest, external evidence root, owner key,
HMAC receipt, snapshot chain, or acceptance-event artifact. Existing `finalization.state` may remain a
recoverable Progress substate, but its current evidence is the synchronized source, Work State when
applicable, targeted verification, and Main post-edit review.

## Terminal Status Reconciliation

Run a bounded terminal reconciliation only after `work_status`, `approval.state`, `round_status`, or
`active_steps` actually changes. Ordinary document edits with no state transition skip this check.

1. Resolve the changed state from owning Aggregate/Step Progress and the Round Index before inspecting
   projections. Work/round indexes and Context Map summaries never override those sources.
2. Search only the owning Round subtree, root works index, and Context Map locations containing the
   exact changed Round/Step ref. Do not scan-and-rewrite the document root or require a generic Markdown
   table updater.
3. A missing optional projection is valid. An existing non-historical current/navigation projection
   that disagrees with owning source is a stale conflict.
4. Preserve historical Progress, acceptance evidence, as-of snapshots, and past-tense narrative. If
   current and historical meaning cannot be separated safely, report the location and residual action
   instead of rewriting it.
5. Reconcile a Step only with its Step Progress and actually affected aggregate/navigation sources;
   reconcile a Work with Aggregate Progress and its existing Work/Round projections.
6. Keep child Round closure local, then reevaluate only the parent's declared child gate. Transition a
   parent Round and its root/Context summaries only after every declared Step and child is resolved and
   accepted.
7. Do not report closure complete while a non-historical projection conflict remains. Fix it inside the
   approved boundary or record the conflict and next action in Progress.
8. Verify with exact-ref search, source comparison, Work State when state changed, and focused contract
   tests. Do not make full graph, package, repository, or installer verification the default.

## Clarification Log and Group Application

Treat per-answer log persistence and per-group source application as separate write boundaries.

1. For recording-required Q&A, create the log and first question entry before that question is asked.
   An important decision or later evidence need warrants a log even for one question; low-importance
   ordinary Q&A need not have one. If it becomes important later, preserve the relevant earlier context
   without inventing timestamps. For an existing or concurrently approved Round/Work order, use
   `<work-order-directory>/clarify/{YYYYMMDDTHHmmssZ}-{topic-slug}.md`, UTC and lower-case kebab-case.
   Reuse the same file for every group in that broad subject. With neither an order location nor a
   separately approved path, return unresolved location/authority to the caller; do not invent a path,
   create a Work, or silently skip required recording. Respect explicit user no-write instructions.
2. Treat the log as a tracked, non-authoritative Work attachment. It needs no key prefix, lifecycle,
   approval, decision, work-status, or completion metadata.
3. Use `# {broad subject}`, `## G01 - {edit scope}`, and `### Q01 - {question summary}`. Base fields are
   `질문`, `답변`, and `답변일시`; a blank answer means unanswered. Known planned questions may be present;
   do not require a complete future questionnaire. Inside the answer, `[확인 대기]` identifies an
   interpretation awaiting confirmation and `[폐기]` a withdrawn question with its cause and reason.
   These are record distinctions, not workflow status or evaluation.
4. On each answer, recheck current bytes and the exact group/question locator and save that entry.
   Clear yes/no or explicit choices need no reconfirmation. If the caller must interpret the conversation,
   save its interpretation as pending before it asks for confirmation. A confirmation or unambiguous
   correction finalizes the same entry; do not number confirmation as a derived question. Do not invent
   intent, duplicate an answer, or add a remaining-question section.
5. Add optional question-level key metadata only when the answer actually affects a source document.
   Treat it as navigation evidence, never source authority, edit permission, evaluation, or acceptance.
6. Do not add `Group Decision`, `Author Application`, sufficiency, evaluation, score, group-completion,
   or work-status fields. Link the log from a Work Order only when it materially informs scope,
   criteria, or a recorded decision.
7. Close `clarify_log_append` by rereading the target entry and return successful persistence before the
   caller asks its next question. On failure or conflicting bytes, preserve the received content/locator
   and stop further questions and dependent source application until retry succeeds. Recheck the entry
   on retry: if already applied, return success without duplicating it. Never ask the user to reconstruct
   an available answer. Do not run Progress updates, Work State, graph reconstruction, package/repository
   tests, or source-document application for the append alone.
8. Apply source documents only after all material questions in the current group are resolved and the
   consolidated handoff is Author-ready. Apply that group's affected source scope exactly once; do not
   include another group or a future edit plan.
9. Return the apply result to the caller so it can continue the next group or resume the original task.
   Clarify never writes either the log or source documents, and the user need not reinvoke either skill.
10. Keep base question IDs unique across the file. Use uppercase Excel-column suffixes for derived
    questions (`Q01-A`, `Q01-B`, ... `Q01-Z`, `Q01-AA`). Further derivation uses the next unused suffix
    under the base question and names the direct cause, not Q01-A-A. Never renumber or reuse IDs. Place
    related questions nearby in the same group; if application scopes differ, use the correct group and
    a causal link. Number adjacency does not define source-application scope.
11. Question-structure changes are withdraw and add. Preserve original questions. For unanswered or
    pending entries, write `[폐기]` plus causal question and reason in the answer and retain relevant
    pending text. Add replacements with new IDs linking both cause and replaced question; simple derived
    additions do not withdraw the original. Preserve finalized answers and record a later change of mind
    in a new linked question/answer. Return already-applied source impact to the caller for review.
12. Use the actual user-answer time, or confirmation time for an interpretation that becomes final.
    Unknown historical timestamps are `미상`; never substitute current save time. An AI withdrawal note
    is not a user answer, so leave its timestamp blank when no previous user answer exists.
13. Before/after-write entry checks are required, but a new session or routine status query does not
    require reading logs. Read relevant records only for missing Q&A context, past-answer evidence, or a
    user request. Do not re-ask finalized answers or recover withdrawn questions as unanswered. Logs
    never replace source/progress authority.

## Resumable Finalization

1. Resume only a current `finalization.state: in_progress` Progress with a recorded blocker and resume
   point. A complete or waived finalization is not a resume candidate.
2. Recheck the recorded blocker against current source and the current accepted contract. Keep
   `blocked` when it remains, use `unknown` when it cannot be decided, and accept a Reader `resumable`
   candidate only with concrete evidence.
3. For `resolved_by_source_change`, run only the current targeted verification named by the resume
   action and synchronize sources whose actual state changed.
4. For `resolved_by_contract_change`, confirm that the former requirement is no longer current
   authority, preserve the old failure as history, and run the current targeted verification instead.
5. Do not recreate legacy manifests, snapshots, HMAC receipts, keys, or evidence roots solely to resume
   unfinished current state.
6. Completion still requires current source synchronization, applicable Work State or focused checks,
   and Main post-edit review. A resolved blocker must never complete automatically or imply acceptance.
7. If the evidence is `blocked` or `unknown`, keep `finalization.state: in_progress` and update the
   durable resume point only when its actual evidence or next action changed.

## Work/Step Progress Ownership

In managed projects, this contract overrides the legacy Current Acceptance, Terminal Reconciliation,
Resumable Finalization, and numbered Progress ownership rules below. Those rules apply only when
`state/manifest.json` is absent. Standard/decision document approval and lifecycle remain source-owned;
work execution, work approval, and finalization belong only to `state/current.json`.
This is one file, wire v2: `{"schema_version":2,"states":{"planned":[...],"in_progress":[...]}}`.
Group by execution state, then list Round/Work/Step entries; omit `execution` from persisted rows.
Never split current state by Round or store closed entries. An empty facade remains `states: {}`.

Use bundled `managed_work_state.py --root ROOT [--document-root DOCS] create|update|close|reopen`
with `--entry-json FILE --expected-digest TOKEN` (`none` only for an absent current.json).
The exact entry fields are `ref`, `kind` (`round|work|step`), `parent`, `order_path`, `execution`,
`approval`, and `finalization`. Round parent is null; Work parent is the Round; Step parent is its Work.
Paths are repository-relative Work Orders. Execution is `planned|in_progress|blocked|complete|cancelled|superseded`,
approval is `pending|accepted|rejected`, finalization is null or `pending|in_progress|complete|waived`.
Use `inspect --ref REF --order-path PATH` for the expected whole-file digest and exact history.

- Register parent Round, Work, and mandatory Steps at creation as planned/pending with null finalization.
  Keep static `key.id`, `doc_type: work_order`, and `### R024/S01` plan headings in the Work Order.
  Events require `--at` (ISO date or timezone timestamp) and a meaningful `--note`.
- `update --at DATE --note REASON` moves the entry to its execution group and atomically appends
  an `updated` event with before/result snapshots to its Work Order. Approval/finalization changes also
  log an event; unchanged updates add none. Main acceptance updates approval explicitly; implementation
  completion never implies acceptance. Record important evidence/blockers in the Work Order as history.
  Do not copy current status into indexes, Context Map, Work Orders, or Progress.
- `close --reason complete|skipped|cancelled|superseded` appends a dated closure with its result and removes
  the entry. Complete closure requires complete execution, accepted approval, settled finalization,
  and satisfied required Work-completion gates. Close children before parents. Explain skip/cancellation.
- `reopen` preserves all old facts and appends a reopen event with the new registered state. There is no
  mutable open/closed field. A missing item without closure evidence is missing/unknown, never complete.
- Read plans' existing `key.relations.depends_on` and `work_gates`. When a dependency may close, preserve
  an exact navigation locator in Work Order frontmatter `work_state_targets`, mapping its stable ID to
  `{ref: R001/work-slug, order_path: 00_docs/works/.../key-work-....md}`. This records identity, not status.
  Missing locator yields an unresolved gate; never scan all archived work to guess it.
- Pending partial transitions require explicit `recover`; external edits are conflicts. A busy writer
  lock is not permission to delete another writer's lock. Keep historical dates factual.

Migration is an explicitly authorized document task, not part of skill installation. Prepare state and
creation/state-change/closure/reopen evidence, preserve history, remove old current-state copies and align affected
text, then verify `work_state_runtime.py --managed`. Finally add `state/manifest.json` with exactly
`{"schema_version":1,"mode":"managed"}`. Do not infer a switch merely from a state directory. After
activation ordinary runtime calls use v6 and errors never fall back to old status owners. The marker is
mode configuration, not another current-state record. Nonempty v1 `state/rounds/` is rejected with
`state_layout_legacy`; explicitly convert and validate old data before removing the old layout. New projects can use the same activation sequence.

Ordinary finalization needs current Work State, scoped verification, historical evidence and Main review,
not a new manifest. If an existing automation explicitly needs one, optional finalization v7 has exactly
`schema_version: 7`, `document_root`, `acceptance_ref`, `accepted_refs: [{ref, order_path}]`, and
`work_state_runtime: {policy_digest, result_digest, source_generation, path_set_digest, complete}`.
Copy binding values from the fresh runtime envelope. `validate_finalization.py` verifies targets against
current state or exact complete-closure history; v1-v6 manifests remain legacy-only. Passing is not Main acceptance.

Legacy ownership (only without the activation marker):

1. Aggregate Work Progress `key-progress.md` owns the Work-level `work_status`, `approval.state`,
   optional `finalization.state`, actual evidence, and resume point as the `aggregate Progress
   authority`.
2. Step Progress `key-progress-{step-slug}.md` owns one `step_ref` and that Step's execution, approval,
   optional finalization, verification evidence, and resume point.
3. A single compatible `key-progress.md` may also carry `step_ref` while the Work and current Step state
   tuple is identical and no independently accepted Step record must be preserved. 두 상태가 갈라질 때만
   Aggregate Work Progress와 Step Progress를 분리하고 모든 Step 파일을 미리 만들지 않는다.
4. When a Step becomes `complete/accepted` while the Work remains `in_progress/pending`, write the Step
   result to `key-progress-{step-slug}.md`; never replace the Aggregate Work Progress tuple with that
   accepted Step tuple.
5. Once any Step Progress exists, omit `step_ref` from Aggregate Work Progress. Do not bulk-rewrite
   completed historical records only to adopt this layout.
6. Work Index `work_status`/`approval` and Context Map or Index `global_state` are an
   `optional compatibility projection`. They may be absent. If present and stale, report the
   projection conflict without replacing aggregate Progress authority.
7. Work State joins Work identity from the Work Index with Work state from Aggregate Progress and Step
   state from a compatible combined or Step Progress record. Fall back to Work Index state only for a
   legacy Work that has no Aggregate Progress.
8. 기본 recovery를 위해 새 persistent projection artifact를 만들지 않는다. Add an optional
   generated block only when a human-facing rendered view is actually needed, and bind it to a bounded
   marker and freshness generation without overwriting human history or rationale.

## Document Delta and Graph Synchronization

A single approved document surface stays in Author's direct-write lane. Recheck the target immediately
before writing and preserve the resulting current diff.

1. Use ID/ref refresh for a single-surface metadata change.
2. Ask Linker for a synchronization transaction only when multiple source surfaces must change
   together to close canonical meaning.
3. Linker decides canonical mutations and exact patches; Author confirms and applies only an
   `owner: author` document patch.
4. Recheck the raw-byte baseline immediately before apply. Return `stale_baseline` without writing when
   it differs.
5. Return `applied | failed | stale_baseline` and the resulting digest for an applied patch.
6. Linker reconstructs current source and runs transaction-scope mechanical validation. Author does not
   declare the transaction verified independently.

External owner-apply keys, HMAC receipts, and disjoint evidence roots are not current apply authority.
Historical finalization v1-v6 and owner-apply/application-evidence inputs may be read by their bundled
compatibility adapters. Missing legacy producers or trust material yields structural diagnostics; it
does not trigger a new producer run or external-folder permission request.

## Document Rules

- Keep standards and works in index-based trees under the configured root.
- Start ordinary rounds at `R001` and every round's steps at `S01`; reserve `R000` for Project
  Foundation.
- A hierarchical plan uses one parent plus one direct child level only. Parent refs remain
  `R[0-9]{3,}`. A `-` introduces a direct child session, whose suffix uses uppercase Excel-column
  numbering: `A` through `Z`, then `AA`, `AB`, ... `AZ`, `BA`, ... `ZZ`, `AAA`. Thus a child Round is
  `R010-A`, a child Step is `R010/S01-A`, a Step inside that child Round is `R010-A/S01`, and its child
  Step is `R010-A/S01-A`. The matching child index lives at
  `works/r010-parent/r010-A/00_key-index.md`. The parent owns ordered `child_rounds` and umbrella scope;
  each child owns its local status, Work, Step, and Progress.
- For new child sessions, do not use digits, letter-number mixtures, lower-case letters, or semantic
  labels as suffixes. Existing one-letter lower-case child Round refs such as `R010-a` are historical
  compatibility inputs only: read them without renaming them, but never emit them for new work.
- Do not create `R010-A-A`, a child below a child, or a sibling-root substitute for a declared child.
  When a third level appears necessary, stop with `NEEDS_SCOPE_CHANGE / work_order_restructure` and ask
  Main to simplify, split sibling children, or create a separate parent Round.
- Keep `document_lifecycle`, `work_status`, `approval.state`, and optional finalization substate
  separate.
- Use Change Sets only for large changes or document-to-code/test impact that materially benefits from
  a durable trace.
- Keep clarification logs under the owning Work's `clarify/` directory. They are explicit non-source
  attachments and therefore do not use the Keystone source-document key prefix.
- Use `key.refs` for navigation and typed relations for semantic relationships. A relation is an impact
  candidate, not automatic edit permission.
- Use `key.worktree.path` only as Work Order operational navigation metadata under the Worktree Locator
  Metadata contract. It is not a typed relation or Artifact Graph locator.
- Do not add or update a document merely to report that it was unaffected.

## Document Item Metadata

Annotate a heading, list item, decision claim, acceptance row, or contract row only when it must be
referenced, changed, superseded, or verified independently.

- Use stable semantic IDs such as `key.rule.*`, `key.claim.*`, and `key.acceptance.*`.
- Put heading/list metadata immediately above its item; keep table-row metadata in the first cell.
- Inherit document authority, lifecycle, approval, and `governed_by` only for document-domain children.
  Never inherit `id`, `supersedes`, or `legacy_terms`.
- Use claim-level `supersedes` for partial replacement.
- Use `requires_verification_of` for a requirement and `verifies` only for performed verification.
- Do not bulk-annotate an existing corpus without explicit scope.

## Dependency and Temporal Rules

- Keep semantic `depends_on` separate from execution `work_gates`.
- Validate dependency targets, Step IDs, duplicates, self-reference, and conditions without mutating
  status, assigning work, cancelling, or accepting.
- Give new documents their actual `created_at` date and accepted meaning its traceable acceptance date.
- Give newly recorded decisions a decision date. Do not add generic `updated_at` or speculate about
  legacy dates.
- Authority comes from lifecycle, approval, source ownership, and relations—not a newer date.

## Verification Tiers

1. **Default Work**: relevant-document search, scope/diff check, Markdown/metadata checks, and directly
   related verification.
2. **Escalated**: affected Linker review for metadata/relation or multi-surface meaning; Work State for
   status/recovery changes; package/historical tests only for those changed adapters.
3. **Release**: full package, repository, and installer verification only when release/publish/install
   verification is explicitly requested.

Disposable cache is optional. If an external cache path is absent or inaccessible, use raw source
without asking for trust/evidence-folder access.

## Output and Boundaries

Report:

1. Changed source documents and reasons.
2. Accepted decisions or assumptions used.
3. Intentionally unchanged related documents.
4. Verification performed and residual risk.
5. Required output-artifact handoff and next action.

Do not dump internal routing or report payloads by default. Do not edit non-document surfaces, invent
decisions, expand scope, grant Main acceptance, or overwrite existing changes.

## Stop Conditions

Stop when the document root, target, authority, scope, or required decision is unresolved; when existing
changes would be overwritten; or when completion requires non-document edits outside the permitted
Coordinator/Main scope.

## Verification

Verify that:

1. The package works without project-local Author standards.
2. Small edits do not require Work Orders, Change Sets, manifests, external keys, or routing payloads.
3. Only sources with changed meaning, status, evidence, resume point, or active pointers are updated.
4. IDs, relations, temporal metadata, dependencies, and Markdown remain valid.
5. Current apply uses owner baseline/result checks and source reconstruction without HMAC receipts.
6. Historical adapters cannot create current completion, apply, or release authority.
7. Default, Escalated, and Release verification are selected from the changed surface.
8. Child acceptance remains local, parent acceptance is gated by all declared children, and no child
   completion creates a new historical finalization or acceptance-event artifact.
9. Terminal reconciliation runs only on an actual state transition, preserves absent optional and
   historical projections, and cannot close over a stale current/navigation projection.
10. Clarification logging starts before the first recording-required question, saves and rereads every
    answer before the next question, confirms only interpretations, preserves withdrawal/derivation and
    answer-change history, and separates persistence from source application per completed group.
11. A linked-worktree handoff writes only the exact canonical Work Order path before implementation and
    returns it for fresh Coordinator/Main confirmation without taking execution ownership.
12. Round creation stops at `planned / pending` with no Active Step unless execution is explicit, accepts
    combined create-and-proceed requests, applies standards-first only to durable production
    implementation, verifies before closure, and preserves Goal-specific Step topology.
