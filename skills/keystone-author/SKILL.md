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

Create and revise human-readable Keystone source documents within the user's request and accepted
decisions. Own standards, work orders, progress records, decision records, source-document metadata,
indexes, and Change Sets. Edit source documents only; Main verifies and accepts the result.

Use this installed package as the complete Author runtime contract. Do not require a consuming project
to contain a project-local Author standard. Project documents define project meaning, while this
package defines Author behavior.

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

Do not use Author for code, config, schema, API, test, generated-file, skill-source edits, worker
orchestration, deep graph interpretation, or unresolved user decisions.

## Operating Modes

Select the smallest mode that fits the approved document change:

- `create`: create a new source document and its required index entry.
- `revise`: change existing accepted or pending meaning without rewriting unrelated history.
- `clarify_apply`: record one resolved Clarify decision and resume the interrupted document task.
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
2. Classify the request as `create | revise | clarify_apply | normalize | progress_update |
   acceptance_finalize`.
3. Read only the relevant project sources and preserve unrelated changes.
4. Use an Author Edit Contract only for a large or ambiguous multi-document change.
5. Edit the approved source documents.
6. Check actual impact on standards, Work/Progress, decisions, indexes, Context Map, and Change Set.
7. Use Linker for graph interpretation; hand repository-output edits to Main or a permitted Coordinator.
8. Run verification proportional to the changed surface and report residual risk.

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
  `R[0-9]{3,}`; child refs use one lower-case suffix such as `R010-a`, and the child index lives at
  `works/r010-parent/r010-a/00_key-index.md`. The parent owns ordered `child_rounds` and umbrella scope;
  each child owns its local status, Work, Step, and Progress.
- Do not create `R010-a-a`, a child below a child, or a sibling-root substitute for a declared child.
  When a third level appears necessary, stop with `NEEDS_SCOPE_CHANGE / work_order_restructure` and ask
  Main to simplify, split sibling children, or create a separate parent Round.
- Keep `document_lifecycle`, `work_status`, `approval.state`, and optional finalization substate
  separate.
- Use Change Sets only for large changes or document-to-code/test impact that materially benefits from
  a durable trace.
- Use `key.refs` for navigation and typed relations for semantic relationships. A relation is an impact
  candidate, not automatic edit permission.
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
