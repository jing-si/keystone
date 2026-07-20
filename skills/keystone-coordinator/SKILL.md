---
name: keystone-coordinator
description: "Coordinate bounded worker delegation, multiple workers, formal review or verification, and worker-report handling only with user permission for the current work scope. Direct invocation grants permission for that scope; do not ask again within it, but ask again when scope or risk meaningfully expands. Prefer Main direct for small, clear work. Do not use to replace Main acceptance or when the work cannot be safely bounded."
---

<!-- keystone: id=key.skill.coordinator kind=output_artifact artifact_kind=skill_source -->
<!-- keystone: produced_from=key.work.skill-runtime-implementation.order -->
<!-- keystone: governed_by=key.standard.project key.standard.skill.coordinator -->

# keystone-coordinator

## Purpose

Broker bounded worker assignments while Main remains supervisor and acceptance owner. Turn recovered work steps, Reader context briefs, Linker reports, and Author Change Sets into assignments; then review worker reports for scope, verification, repair, escalation, and Main acceptance readiness.

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
- Prefer Main direct for small, clear work that does not benefit from delegation or formal report handling.

## When To Use

Use Coordinator, with permission, when one or more of these are needed:

1. Delegate a recovered work step as a bounded Goal unit.
2. Coordinate multiple workers or distinct implementation, review, and verification assignments.
3. Build a Context Pack with explicit authority, scope, forbidden changes, verification, and return-report requirements.
4. Inject a requested domain or coding skill without letting it replace Keystone boundaries.
5. Convert a Linker report or Author Change Set into assignment context or reviewer focus.
6. Review worker reports and choose an accept candidate, repair, review, verify, escalate, or block action.
7. Preserve formal work state across delegation while Main retains final acceptance.

## When Not To Use

Do not use Coordinator when:

1. Main can safely complete a small, clear task directly.
2. The main task is source-document scope design or authoring; use Author.
3. A high-impact user decision is missing; use Clarify for one actual decision topic.
4. The main task is read-only Keystone navigation; use Reader.
5. Artifact impact, stale, or gap evidence needs interpretation; use Linker first.
6. The current work, completion criteria, scope, authority, or verification path cannot be recovered.
7. A document workflow lacks an Author Edit Contract or approved edit scope.
8. The work cannot be bounded without overwriting existing changes or expanding authority.

## Fail-Soft Recovery

Do not invent an active round, work ID, current step, source authority, or acceptance criteria.

When context cannot be recovered, do not create a worker assignment. Report what is missing and recommend the narrowest next action:

- Use Init when Keystone is uninitialized or partially initialized and the user permits initialization or repair.
- Use Reader when Keystone documents exist but active work navigation is unclear.
- Use Author when a work order, Change Set, or document edit scope must be created or revised.
- Use Clarify only when an actual user decision blocks recovery.
- Return to Main for a small direct task or when no delegated workflow is warranted.

Absence of a project-local Coordinator standard is never a missing-context error.

## Required Assignment Context

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

Include `routing_context_ref` only when multiple surfaces, an authority boundary, or an audit requirement makes an explicit routing record useful. Do not require a routing payload for ordinary assignments.

## Workflow

1. Confirm permission for the current work scope.
2. Recover the document root, active round, work ID, current step, and workflow state when Keystone-managed work is claimed.
3. Extract Goal, Scope, Source Context, Completion Criteria, Stop Conditions, Verification, and Expected Output.
4. Extract forbidden changes and accepted decisions from available project sources.
5. Use a Linker report when artifact relations, impact candidates, stale/gap risks, reuse candidates, or anchor changes materially affect the assignment.
6. Decide whether delegation is useful and whether the work can be bounded. Return to Main direct when it is not.
7. Select a purpose and authority: `investigate/read_only`, `document_edit/bounded_edit`, `implement/bounded_edit`, `review/review_only`, or `verify/verification`.
8. Select an injected skill contract. Use `keystone-default-bounded-worker` when no domain-specific or explicitly requested external skill applies.
9. Keep `injected_skills` non-empty for every actual worker assignment.
10. Record only execution constraints supplied by the user, injected skill, or host; do not choose an isolation or concurrency strategy on Keystone's behalf.
11. Create the bounded assignment and deliver it to the worker.
12. Inspect the returned report and actual state for scope, forbidden changes, verification, source conflicts, and preserved Main context.
13. Choose the next action: accept candidate, repair, review, verify, escalate, or block.
14. Let Main make the acceptance decision; update progress to accepted only after that decision.

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
- If an injected procedure requires authority, scope, external state, publishing, dependency changes, or additional workers beyond the assignment, require a `NEEDS_SCOPE_CHANGE` or `NEEDS_CONTEXT` report.
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
    - child subagent creation
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
    required_sources:
    optional_sources:
    artifact_context:
      anchor_change_context:
        allowed_anchor_changes:
          - artifact_id:
            surface: code_anchor | config_anchor | schema_anchor | api_anchor | test_anchor
            relation:
            reason:
            linker_report_ref:
        forbidden_anchor_changes:
        verification_required:
    reuse_candidates:
    test_candidates:
    document_sync_candidates:
    metadata_sync_risks:
  main_context_checkpoint:
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
  execution_environment:
    constraints:
    supplied_by: user | injected_skill | host | combined
  return_report_contract:
```

Use `main_context_checkpoint` to preserve global intent, accepted decisions, current work identity, source conflicts, scope boundaries, and Main acceptance ownership across handoffs.

Worker report:

```yaml
worker_report:
  assignment_id:
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
  changed_files:
  changed_key_ids:
  changed_capabilities:
  local_decisions:
    - decision:
      reason:
      evidence:
  scope_check:
  forbidden_change_check:
  verification:
  document_sync_needed:
  metadata_sync_needed:
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
  source_conflict_result:
  main_context_preserved: true | false
  reason_codes:
  review_required: true | false
  verification_required: true | false
  repair_required: true | false
  escalation_required: true | false
  coordinator_decision: accept_candidate | repair | review | verify | escalate | block
  main_acceptance_allowed: true | false
  residual_risk:
  next_action:
```

Keep report status separate from work-progress status. Treat `accept_candidate` as readiness for Main review, not acceptance.

## Current Example

```yaml
worker_assignment:
  assignment_id: r002-s02-coordinator-runtime
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
5. Separate source conflicts, stale work orders, stale progress records, and unpropagated accepted decisions.
6. Assign separate review or verification only when it materially improves confidence.
7. Use `accept_candidate` only when Main can make an informed acceptance decision.
8. Leave acceptance to Main. Worker `DONE`, Coordinator review, and successful verification do not independently accept work.

## Default User Response

By default, answer users with a concise human-facing brief instead of dumping `worker_assignment`, `worker_report`, or `worker_report_review`. Include workflow decision, goal/scope summary, verification result, Main acceptance readiness, residual risk, and recommended next action.

Keep worker assignment/report payloads as agent-facing runtime contracts. Emit the full payload only when the user asks for it, a worker handoff needs it, or audit/debug/verification evidence requires it. Optional `keystone-viewer` may render the payload, but it must not change scope, authority, verification result, report status, or Main acceptance readiness.

Before sending a user-facing response, apply the Payload Disclosure Gate: do not print raw `*_output`, `*_result`, `*_report`, `worker_assignment`, or `keystone_routing_decision` blocks by default. Summarize the payload as workflow decision, scope summary, verification result, Main acceptance readiness, residual risk, recommended next action, and key source refs; mention full payload availability only when useful.

## Boundaries

1. Broker assignments; do not replace Main.
2. Do not create high-impact decisions or expand accepted scope.
3. Do not design source-document edit scope without an Author Edit Contract.
4. Do not interpret artifact-graph candidates without Linker evidence.
5. Do not mark progress accepted before Main acceptance.
6. Do not choose workspace isolation, concurrency, or integration strategy on Keystone's behalf.
7. Do not let injected skills raise authority, change scope, or create child workers.
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
9. A report requires source authority, acceptance criteria, status semantics, or meaningful scope/risk changes.
10. Host constraints or concurrent edits make the assignment unsafe.

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
