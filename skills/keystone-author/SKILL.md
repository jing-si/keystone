---
name: keystone-author
description: "Create or revise Keystone source documents, standards, work orders, progress records, decisions, indexes, metadata, and Change Sets within a clear scope. Use for direct document requests and accepted Clarify results; hand off initialization when Keystone is absent. Do not use for unresolved user decisions, read-only orientation, code/config/schema/API/test edits, worker orchestration, or skill-source implementation."
---

<!-- keystone: id=key.skill.author kind=output_artifact artifact_kind=skill_source -->
<!-- keystone: produced_from=key.work.skill-runtime-implementation.order -->
<!-- keystone: governed_by=key.standard.project key.standard.skill.author -->

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
7. Linker report or impact seed only when graph interpretation matters.

A work order and progress record improve recoverability but are not artificial prerequisites for a small, valid, explicit document request. Record routing context only for multiple surfaces, authority boundaries, or real audit/handoff needs.

## Workflow

1. Detect initialization state and resolve one document root.
2. Handoff to Init or Clarify when the Initialization Gate requires it, then resume here.
3. Classify the request as `create`, `revise`, `clarify_apply`, `normalize`, or `progress_update`.
4. Read only the relevant project standards, decisions, work context, target documents, and indexes.
5. Confirm that requested targets are Keystone source documents and that the scope is clear. Treat an explicit edit request as authority within its stated scope.
6. For a large or multi-document change, prepare an Author Edit Contract containing targets, allowed changes, impact candidates, exclusions, forbidden changes, progress policy, and verification. Skip this ceremony for a small unambiguous edit.
7. If project purpose, scope, policy, terminology, authority, sensitive data, destructive migration, or conflicting valid alternatives require user judgment, hand off exactly one topic to Clarify. Do not ask about built-in metadata, filenames, routing, or safe defaults.
8. Edit only approved source documents and preserve unrelated user or agent changes.
9. Check affected indexes, Context Map, decisions, progress, and Change Set needs. A relation is an impact candidate, not automatic edit authority.
10. Use Linker read-only when artifact relations, stale metadata, or gaps need interpretation. Defer code/config/schema/API/test/skill-source changes to Main direct or a user-permitted Coordinator scope.
11. Validate links, identifiers, metadata, lifecycle/approval/work-state separation, terminology, and Markdown.
12. Report changes, intentional exclusions, verification, residual risk, and next action. Main accepts only after checking actual results and verification.

## Document Rules

- Keep standards and works in index-based trees under the configured root.
- Start ordinary rounds at `R001` and every round's steps at `S01`.
- Reserve `R000 Project Foundation` for the special pre-standard foundation round; its first step is also `S01`.
- Give each new work node a `00_key-index.md`, `key-work-{slug}.md`, and `key-progress.md` unless an accepted project rule says otherwise.
- Keep lifecycle (`draft`, `active`, `superseded`, `archived`), approval (`pending`, `accepted`, `rejected` when needed), and work status in separate fields.
- Do not mark work `accepted` or `complete` before Main acceptance. Worker `DONE` is not Main acceptance.
- Apply accepted Clarify results without inventing a new decision or expanding their edit plan.
- Use Change Sets for large changes or document-to-code/test impact that needs traceability.
- Use `key.refs` for navigation and typed relations for semantic relationships; do not infer automatic propagation.

## Boundaries

Do not:

1. Edit implementation code, config, schema, API, tests, generated files, code anchors, or `skills/**`.
2. Create user decisions, change scope/acceptance/status semantics/source authority, or approve project meaning.
3. Perform deep Artifact Graph interpretation or orchestrate workers and reports.
4. Require mandatory routing payloads, project-local Author standards, or a particular workspace/worktree strategy.
5. Overwrite existing changes or migrate/rename paths without explicit authority.

If delegation would help, Main may ask the user. Coordinator requires permission for that work scope; direct Coordinator invocation counts as permission. Linker is read-only and may be used without separate approval.

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
    output_artifact_changes_deferred:
    linker_report_required:
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
5. Rounds and steps follow `R001`/`S01`, with only the R000 foundation exception.
6. No mandatory routing, host mode, profile, or workspace strategy was introduced.
7. The default response hides structured payloads while preserving material risks and status.
