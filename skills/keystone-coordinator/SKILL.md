---
name: keystone-coordinator
description: "Use to turn recovered Keystone work steps, context briefs, Linker reports, and Change Sets into bounded worker assignments, injected skill contracts, report review, verification, and main-acceptance coordination. Do not use when current step/scope/verification cannot be recovered or to replace Main acceptance."
---

# keystone-coordinator

## Purpose

Broker bounded worker assignments while the main agent remains supervisor. Coordinator turns recovered work steps, Reader context briefs, Linker reports, and Author Change Sets into worker assignments, then reviews worker reports for scope, verification, repair, escalation, and Main acceptance readiness.

Source documents and accepted decisions are the source of truth. Coordinator runtime output does not replace source documents, worker reports do not replace progress state, and `DONE` does not replace Main acceptance.

## Required Source Documents

Read:

1. `00_docs/standards/01_key-project-standard.md`
2. `00_docs/standards/subagents/key-standard-subagents.md`
3. `00_docs/standards/skills/coordinator/key-standard-coordinator.md`
4. Active work node index, work order, and progress record.
5. Reader context brief, Linker report, Author Edit Contract, or Change Set when provided.
6. Related decisions and verification expectations.

## When To Use

Use Coordinator when:

1. A current work step must be executed as a Goal unit.
2. Main needs a bounded worker assignment.
3. Worker assignment needs context pack, purpose, authority, scope, injected skill contract, workspace guard, verification, and return report contract.
4. A worker report must be reviewed for accept candidate, repair, review, verify, escalate, or block.
5. Keystone work includes code/config/schema/API/test edits and needs bounded implementation routing.
6. An external coding skill is explicitly requested and must be injected without replacing Keystone boundaries.
7. Linker report must be converted into assignment artifact context or review focus.

## When Not To Use

Do not use Coordinator when:

1. Current step, completion criteria, applicable standards, scope, or verification cannot be recovered.
2. The main task is source document authoring scope design. Use Author.
3. The main task is high-impact decision collection. Use Clarify.
4. The main task is read-only navigation. Use Reader.
5. Artifact impact/stale/gap candidates need interpretation before assignment. Use Linker.
6. Work is high-risk and lacks Main/user decision.
7. A document workflow lacks an Author Edit Contract or approved edit scope.

## Required Input

Require:

1. User request or main current task.
2. Document root and active work state.
3. Goal, scope, completion criteria, stop conditions, verification.
4. Applicable standards and accepted decisions.
5. Workspace state and existing-change risk.
6. Linker report, impact seeds, artifact candidates, or Change Set when artifact graph is involved.
7. Author Edit Contract for document formal workflow.
8. Explicit external coding skill request, if any.
9. Single workspace guard for file-writing workers.

## Workflow

1. Recover document root, active round, work ID, and current step.
2. Extract Goal, Scope, Source Context, Completion Criteria, Stop Conditions, Verification, and Expected Output.
3. Extract forbidden changes and verification expectations from standards.
4. Require Linker report when artifact candidates, stale/gap risks, or anchor changes matter.
5. Decide whether the work can be bounded.
6. Select purpose preset and authority from subagent standards.
7. Select injected skill contract. If no domain-specific or explicit external skill applies, use `keystone-default-bounded-worker`.
8. Keep `injected_skills` non-empty.
9. If external coding skill is requested, add it as an injected skill. Do not let it replace Coordinator scope, authority, workspace guard, verification, or report contract.
10. Create worker assignment and workspace guard.
11. Review returned worker report against actual state, scope, forbidden changes, verification, source conflicts, and main context checkpoint.
12. Decide next action: accept candidate, repair, review, verify, escalate, or block.
13. Do not mark progress accepted until Main acceptance conditions are satisfied.

## Output Contract

Worker assignment:

```yaml
worker_assignment:
  assignment_id:
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
  workspace_guard:
  return_report_contract:
```

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

## Output Examples

```yaml
worker_assignment:
  assignment_id: s08-skill-source-create
  goal: Create repo-local Keystone SKILL.md files.
  completion_criteria:
    - five skill directories exist
    - each SKILL.md has name and description
    - descriptions expose trigger and non-trigger boundaries
  intent_summary: Implement S08 Skill Creation from accepted S01-S07 standards.
  purpose: implement
  authority: bounded_edit
  source_documents:
    - 00_docs/works/r001-bootstrap-keystone/skill-creation/key-work-skill-creation.md
  applicable_standards:
    - 00_docs/standards/01_key-project-standard.md
    - 00_docs/standards/subagents/key-standard-subagents.md
  context_pack:
    required_sources:
      - 00_docs/standards/skills/reader/key-standard-reader.md
    artifact_context: []
    reuse_candidates: []
    test_candidates: []
    document_sync_candidates: []
    metadata_sync_risks: []
  injected_skills:
    - skill_id: keystone-default-bounded-worker
      mode: default
      authority_ceiling: assignment_authority
      allowed_use:
        - assignment-local planning
      required_output:
        - skill_usage
        - scope_check
        - forbidden_change_check
        - verification
        - residual_risk
      forbidden_use:
        - scope expansion
        - Main acceptance
        - child subagent creation
      stop_conditions:
        - source context missing
  scope:
    read_scope:
      - 00_docs
    allowed_edit_scope:
      - skills/keystone-*/SKILL.md
    excluded_scope:
      - installed external skills
  workspace_guard:
    model: single_workspace
    active_file_writer_policy: exclusive
    existing_changes_policy: do_not_overwrite_unlisted_changes
```

## Boundaries

1. Coordinator brokers assignments; it does not replace Main.
2. Coordinator does not create high-impact decisions.
3. Coordinator does not design source document edit scope without Author Edit Contract.
4. Coordinator does not interpret artifact graph candidates without Linker.
5. Coordinator does not mark progress accepted before Main acceptance.
6. Coordinator allows only one file-writing worker in a single workspace.
7. External coding skills are injected guidance only. They do not raise authority or change scope.

## Stop Conditions

Stop when:

1. Current step, completion criteria, applicable standard, scope, or verification cannot be recovered.
2. Work cannot be bounded into an assignment.
3. File-writing work lacks workspace guard.
4. High-risk implementation lacks Main/user decision.
5. Existing changes could be overwritten.
6. `injected_skills` would be empty.
7. A new reusable artifact is needed but no Linker report or reuse discovery exists.
8. External coding skill requirements conflict with assignment boundaries.
9. Worker report requires scope, source authority, acceptance criteria, or status semantics changes.

## Verification

Verify Coordinator behavior by checking:

1. Worker assignment and worker report contracts are distinct.
2. `injected_skills` is non-empty.
3. Default worker contract is used when no explicit external skill applies.
4. External coding skill is injected, not a replacement.
5. Worker `DONE` is not Main acceptance.
6. Single workspace guard limits file-writing work.

Suggested checks:

```bash
rg --files 00_docs
rg -n "worker_assignment|worker_report|worker_report_review|injected_skills|keystone-default-bounded-worker|single workspace" 00_docs/standards/skills/coordinator/key-standard-coordinator.md
```

## Related Source Documents

- `00_docs/standards/01_key-project-standard.md`
- `00_docs/standards/subagents/key-standard-subagents.md`
- `00_docs/standards/skills/coordinator/key-standard-coordinator.md`
- `00_docs/standards/skills/linker/key-standard-linker.md`
