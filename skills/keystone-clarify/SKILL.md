---
name: keystone-clarify
description: "Use for one topic at a time high-impact Keystone policy, scope, document-structure, modularization, or skill-contract decisions and author-ready edit plans. Do not use for routine edits, implementation work, broad document authoring, or worker orchestration."
---

# keystone-clarify

## Purpose

Clarify one high-impact Keystone decision topic at a time and produce an author-ready decision summary and edit plan. Use this skill before source documents are meaningfully changed when policy, scope, structure, skill contract, or modularization choices are unclear.

Source documents and accepted decisions are the source of truth. Clarify output does not replace source documents or Main/user acceptance until the decision is accepted and applied by the appropriate owner.

## Required Source Documents

Read the relevant subset:

1. `00_docs/standards/01_key-project-standard.md`
2. `00_docs/standards/skills/clarify/key-standard-clarify.md`
3. Related Author standard when producing an edit plan.
4. Related work order, progress record, and decision record.
5. Linker report, worker report, reviewer finding, or user evidence for modularization topics.

## When To Use

Use Clarify when:

1. A high-impact policy, scope, source document, skill-contract, or cross-document consistency decision is needed.
2. A source document change would be risky without user intent.
3. Initial Keystone setup needs document root, tracking policy, language policy, or storage decisions.
4. Existing source documents conflict with the current task direction.
5. A modularization decision is needed because reuse, extend, extract shared module, create new, or investigate first changes scope or verification.

## When Not To Use

Do not use Clarify to:

1. Perform routine edits or formatting.
2. Create or revise standards or work orders directly.
3. Implement code/config/schema/API/test changes.
4. Orchestrate worker assignments or report handling.
5. Decide repository similarity without evidence from Linker, worker report, reviewer finding, or user input.
6. Apply unaccepted decisions to source documents.

## Required Input

Require:

1. Current clarification topic.
2. Related source documents, standards, work orders, progress records, and decisions.
3. Mode context: `plan` for question collection or `default` for accepted decision handoff.
4. Known affected documents and output artifact candidates.
5. Approved target document/section when preparing Author handoff.
6. Risk context for sensitive data, local paths, setup config, or common/global instruction files.
7. Evidence source for modularization decisions.

## Workflow

1. Confirm the topic is one high-impact decision, not a bundle.
2. Read the relevant source documents.
3. If in Plan Mode, ask one focused question at a time and explain tradeoffs.
4. If the answer is insufficient, return an incomplete result with unresolved current-topic questions.
5. If sufficient, produce decision summary, rationale, affected documents/output artifacts, completeness check, recording hint, and edit plan.
6. For modularization topics, use only supplied evidence and report selected option or needed investigation.
7. For downstream file-changing work, identify target surfaces and required lanes, but do not perform the edit.
8. Hand off source document application to Author.
9. Hand off implementation, repository-source edits, and worker workflow to Coordinator.

## Routing Gate

Clarify can make an author-ready decision or edit plan, but that result is not edit authority. Before files change, Main must emit `keystone_routing_decision` and split `source_document`, `skill_source`, and `repository_source` surfaces into Author, Main direct, or Coordinator lane. If the target surface remains unclear, stop before editing.

## Default User Response

By default, answer users with a concise human-facing brief instead of the full `clarify_result`. Include the topic or decision, rationale, unresolved current-topic questions, author-ready status, affected key documents, and recommended next action.

Keep `clarify_result` as an agent-facing structured payload. Emit the full payload only when the user asks for it, Author needs it for handoff, or audit/debug/verification evidence requires it. Optional `keystone-viewer` may render the payload, but it must not change the decision summary, open questions, or author-ready judgment.

## Output Contract

Use:

```yaml
clarify_result:
  topic:
  decision_summary:
  rationale:
  working_assumptions:
  affected_documents:
    update_targets:
      - path:
        sections:
        reason:
        required_change:
    inspect_only_candidates:
      - path:
        reason:
        evidence:
    excluded:
      - path:
        reason:
  affected_artifact_candidates:
  edit_plan:
  routing_handoff:
    target_surfaces:
    recommended_lanes:
    required_reports:
  stop_conditions:
  open_questions:
    unresolved_current_topic:
      - question:
        reason:
    out_of_topic:
      - question:
        reason:
  decision_completeness_check:
    selected_option:
    rejected_options:
    rationale:
    affected_source_documents:
    affected_work_orders:
    affected_artifact_candidates:
    acceptance_or_status_impact:
    recording_scope: global | round | work | none | unresolved
    recording_reason:
    author_edit_ready: true | false
  decision_recording_hint:
    scope: global | round | work | none | unresolved
    recommended_path:
    reason:
    requires_author_update: true | false
  modularization_decision:
```

## Output Examples

```yaml
clarify_result:
  topic: S08 SKILL.md trigger boundaries
  decision_summary: Each skill description must include both trigger and non-trigger boundaries.
  rationale: Frontmatter description is the primary trigger surface.
  affected_documents:
    update_targets:
      - path: 00_docs/works/r001-bootstrap-keystone/skill-creation/key-work-skill-creation.md
        sections: [Completion Criteria, Verification]
        reason: S08 generation guardrail.
        required_change: Require concrete description and output-shape checks.
    inspect_only_candidates: []
    excluded: []
  affected_artifact_candidates:
    - artifact: skills/keystone-reader/SKILL.md
      artifact_kind: skill_source
      produced_from: 00_docs/works/r001-bootstrap-keystone/skill-creation/key-work-skill-creation.md
    - artifact: skills/keystone-author/SKILL.md
      artifact_kind: skill_source
      produced_from: 00_docs/works/r001-bootstrap-keystone/skill-creation/key-work-skill-creation.md
  edit_plan:
    - Add description quality criteria.
    - Add validation commands for role boundaries.
  routing_handoff:
    target_surfaces:
      - source_document
      - skill_source
    recommended_lanes:
      - keystone-author
      - main_direct
    required_reports:
      - author_patch_report
      - main_direct_change_report
  open_questions:
    unresolved_current_topic: []
    out_of_topic: []
  decision_completeness_check:
    selected_option: strengthen_s08_generation_template
    rejected_options: []
    rationale: Prevent runtime trigger collisions.
    affected_source_documents:
      - 00_docs/works/r001-bootstrap-keystone/skill-creation/key-work-skill-creation.md
    affected_work_orders:
      - S08
    affected_artifact_candidates:
      - artifact: skills/*/SKILL.md
        artifact_kind: skill_source
        relation: produced_by_s08_work_order
    acceptance_or_status_impact: no accepted status before Main acceptance
    recording_scope: work
    recording_reason: S08-specific generation guidance.
    author_edit_ready: true
  decision_recording_hint:
    scope: work
    recommended_path: 00_docs/works/r001-bootstrap-keystone/skill-creation/key-work-skill-creation.md
    reason: Applies to S08 only.
    requires_author_update: true
```

## Boundaries

1. Clarify handles one topic at a time.
2. Clarify does not apply non-trivial source document edits directly.
3. Clarify does not implement repository changes.
4. Clarify does not orchestrate workers.
5. Clarify does not infer high-impact decisions from vague delegation.
6. Clarify does not decide modularization without evidence.

## Stop Conditions

Stop when:

1. The topic contains multiple high-impact decisions.
2. User answers conflict with each other or source documents.
3. Target documents or sections are unclear.
4. The change would alter scope, acceptance criteria, or status semantics without approval.
5. Sensitive or local-only information may need to be recorded.
6. Implementation or repository-source edits are required before the decision can be made.
7. Modularization evidence is insufficient.
8. Downstream file-changing target surfaces cannot be separated for routing.

## Verification

Verify Clarify behavior by checking:

1. Plan Mode and Default Mode are distinct.
2. Incomplete answers produce `author_edit_ready: false`.
3. Decision recording hint is a handoff hint, not write authority.
4. Affected documents and output artifacts are separated.
5. Modularization decisions use evidence and handoff boundaries.
6. Default user response summarizes decision, rationale, open questions, affected documents, and next action without dumping the full structured payload.
7. File-changing handoff separates Author, Coordinator, and Main direct lanes and requires routing before editing.

Suggested checks:

```bash
rg --files 00_docs
rg -n "decision_completeness_check|decision_recording_hint|modularization_decision|author_edit_ready" 00_docs/standards/skills/clarify/key-standard-clarify.md
```

## Related Source Documents

- `00_docs/standards/01_key-project-standard.md`
- `00_docs/standards/skills/clarify/key-standard-clarify.md`
- `00_docs/standards/skills/author/key-standard-author.md`
- `00_docs/standards/skills/linker/key-standard-linker.md`
