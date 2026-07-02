---
name: keystone-author
description: "Use to create or revise Keystone source documents, standards, work orders, progress records, decisions, indexes, and Change Sets within an approved scope. Do not use for high-impact clarification, code/config/schema/API/test edits, worker orchestration, or repo-local skill source implementation."
---

# keystone-author

## Purpose

Create or revise Keystone source documents within an approved scope. Author owns standards, work orders, progress records, decision records, source-document metadata, indexes, and Change Sets.

Source documents and accepted decisions are the source of truth. Author output does not replace Main/user acceptance. If the requested edit conflicts with source authority, scope, status semantics, or acceptance criteria, stop and ask for a decision.

## Required Source Documents

Read the minimum relevant set:

1. `00_docs/standards/01_key-project-standard.md`
2. `00_docs/standards/skills/author/key-standard-author.md`
3. Related child standards for the target document.
4. Related work order, progress record, and decision record.
5. Accepted Clarify result when applying a high-impact decision.
6. Linker report or handoff seed when Artifact Graph impact is involved.

## When To Use

Use Author when the task requires:

1. Creating a standard, work order, progress record, decision record, index, or Change Set.
2. Revising source documents according to an approved instruction or accepted decision.
3. Applying an accepted Clarify result to source documents.
4. Creating or updating source-document metadata such as Markdown frontmatter `key.id`, `key.refs`, or section key comments.
5. Writing an Author Edit Contract before a larger document edit.
6. Recording document impact seeds or Linker handoff requirements.

## When Not To Use

Do not use Author to:

1. Ask high-impact clarification questions or accept decisions.
2. Perform read-only project orientation.
3. Orchestrate worker assignments, report review, verification, repair, or acceptance flow.
4. Edit code, config, schema, API, tests, generated files, or code anchors.
5. Implement repo-local `skills/*/SKILL.md` files. S08 skill source creation is a Main direct task or a Coordinator bounded worker task, not Author source-document authoring.
6. Change scope, acceptance criteria, source authority, or status semantics without approval.

## Required Input

Require:

1. User request or main-approved edit instruction.
2. Configured document root.
3. Target document and section, or purpose of the new source document.
4. Approved scope and acceptance boundary.
5. Applicable standards and work order context.
6. Accepted Clarify result when relevant.
7. Linker report or handoff seed when artifact impact is involved.
8. `keystone_routing_decision` selecting `source_document` and `keystone-author` for file-changing work.
9. Workspace state and existing-change risk.

## Workflow

1. Resolve the document root.
2. Read project standard and relevant Author/child standards.
3. Confirm `keystone_routing_decision` selected Author lane for `source_document` changes.
4. Classify mode: `create`, `revise`, `clarify_apply`, `normalize`, or `progress_update`.
5. Identify target source documents and sections.
6. Confirm approved scope and impact boundaries.
7. If a high-impact decision is missing, stop and recommend Clarify.
8. For larger edits, write or reconstruct an Author Edit Contract.
9. Edit only approved source documents.
10. Check affected indexes, context map, progress, decisions, and Change Set needs.
11. Use Linker reports for artifact impact or metadata gap evidence; do not perform deep graph interpretation yourself.
12. If code/config/schema/API/test or repo-local skill source changes are needed, split or defer to the proper lane.
13. Report changed files, no-edit candidates, verification, and residual risk.

## Routing Gate

Author may edit only Keystone source documents under `00_docs/**` after Main selects Author lane in `keystone_routing_decision`. Reading Author guidance does not count as executing Author lane. If target surfaces include `skill_source` or `repository_source`, split them into Main direct or Coordinator lane and list them as no-edit candidates in `author_patch_report`.

## Default User Response

By default, answer users with a concise human-facing brief instead of the full `author_patch_report`. Include changed source documents, intentional no-edit candidates, verification, residual risk, and recommended next action.

Keep `author_patch_report` and `author_edit_contract` as agent-facing structured payloads. Emit the full payload only when the user asks for it, another Keystone skill needs it for handoff, or audit/debug/verification evidence requires it. Optional `keystone-viewer` may render the payload, but it must not change source authority, progress status, or edit meaning.

## Output Contract

Report:

```yaml
author_patch_report:
  contract_id:
  routing_decision_ref:
  edits:
    - path:
      section:
      change_type: create | revise | progress_update | decision_record | index_update
      reason:
      source_decision:
  no_edit_candidates:
    - path:
      reason:
  progress_updates:
    - path:
      before:
      after:
      main_acceptance_evidence:
  graph_handoff_result:
    source_document_metadata_applied:
    code_config_schema_api_test_anchor_deferred_to_coordinator:
    linker_report_required:
  verification:
    commands_or_checks:
    result:
  residual_risk:
  recommended_next_action:
```

When preparing a larger edit, use:

```yaml
author_edit_contract:
  contract_id:
  accepted_instruction:
  target_documents:
    - path:
      sections:
      allowed_change:
  affected_document_candidates:
    - path:
      reason:
      action: edit | inspect_only | exclude
  forbidden_changes:
    - scope_change
    - acceptance_criteria_change
    - status_semantics_change
    - code_change
  progress_update_policy:
    may_update_progress: true
    forbidden_statuses_before_main_acceptance:
      - accepted
      - complete
  verification:
    - check_index_links
    - check_context_map_if_affected
    - check_decision_record_if_affected
```

## Output Examples

```yaml
author_patch_report:
  contract_id: author-edit-s08-skill-creation
  routing_decision_ref: keystone-routing-s08-output-policy
  edits:
    - path: 00_docs/works/r001-bootstrap-keystone/skill-creation/key-work-skill-creation.md
      section: Verification
      change_type: revise
      reason: Strengthen S08 SKILL.md validation.
      source_decision: user-approved S08 execution
  no_edit_candidates:
    - path: README.md
      reason: Not required for S08 source generation.
  graph_handoff_result:
    source_document_metadata_applied: false
    code_config_schema_api_test_anchor_deferred_to_coordinator: []
    linker_report_required: false
  verification:
    commands_or_checks:
      - rg --files 00_docs
    result: pass
  residual_risk: Main acceptance still required before progress accepted.
```

## Boundaries

1. Author edits source documents only.
2. Author does not edit implementation code, config, schema, API, tests, generated files, or code anchors.
3. Author does not collect high-impact decisions.
4. Author does not orchestrate workers or accept worker reports.
5. Author does not mark progress `accepted` or `complete` before Main acceptance.
6. Author does not treat repo-local skill implementation files as Author-owned source documents.

## Stop Conditions

Stop when:

1. Document root or target section is unclear.
2. Approved scope is unclear or conflicts with source documents.
3. A high-impact decision is needed but no accepted Clarify result exists.
4. The edit would change scope, acceptance criteria, status semantics, or source authority.
5. The edit requires code/config/schema/API/test changes.
6. Existing user or agent changes could be overwritten.
7. Formal reviewer/verifier/report acceptance workflow is needed.
8. No `keystone_routing_decision` selected Author lane for the source document edit.

## Verification

Verify Author behavior by checking:

1. Trigger and non-trigger boundaries.
2. Source-document-only edit authority.
3. Author Edit Contract completeness.
4. Progress update boundary and Main acceptance separation.
5. Linker/Coordinator handoff for Artifact Graph or repository-source edits.
6. Default user response summarizes changes, verification, risks, and next action without dumping the full structured payload.
7. `author_patch_report` references the routing decision and does not claim ownership of `skills/keystone-*/SKILL.md`.

Suggested checks:

```bash
rg --files 00_docs
rg -n "author_edit_contract|author_patch_report|graph_handoff_result" 00_docs/standards/skills/author/key-standard-author.md
```

## Related Source Documents

- `00_docs/standards/01_key-project-standard.md`
- `00_docs/standards/skills/author/key-standard-author.md`
- `00_docs/standards/subagents/key-standard-subagents.md`
- `00_docs/standards/skills/linker/key-standard-linker.md`
