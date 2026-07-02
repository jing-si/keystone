---
name: keystone-linker
description: "Use for read-only Artifact Graph interpretation: artifact discovery, impact analysis, stale/gap review, reuse/test candidates, source-surface handoff seeds, and worker-assignment artifact context. Do not use to edit source documents, code/config/schema/API/test, make final decisions, or assign workers."
---

# keystone-linker

## Purpose

Interpret Keystone Artifact Graph evidence read-only. Linker discovers output artifact candidates, classifies impact, stale, and metadata gap candidates, reports reuse/test candidates, and prepares source/output-surface handoffs or worker-assignment seeds.

Source documents, accepted decisions, output artifacts, and verification evidence are the source of truth. Linker output does not replace source documents, source edits, or Main acceptance. Linker owns operational graph interpretation, not source edit authority.

## Required Source Documents

Read:

1. `00_docs/standards/01_key-project-standard.md`
2. `00_docs/standards/artifacts/key-standard-artifact-graph.md`
3. `00_docs/standards/skills/linker/key-standard-linker.md`
4. Related Reader, Author, Coordinator standards when preparing handoff.
5. Related work order, progress record, decisions, and known artifact seeds.

## When To Use

Use Linker when:

1. Source document, decision, or work order changes may affect output artifacts.
2. Output artifact changes may make source documents, decisions, or work orders stale.
3. Existing capabilities, APIs, reusable code, config, schema, tests, skill sources, or generated artifacts must be found before implementation.
4. Metadata gaps, mechanical stale, or semantic stale candidates must be reported.
5. Coordinator needs artifact context, reuse candidates, tests, stale risks, or metadata sync risks before a worker assignment.
6. Change Set impact seeds and required/optional/excluded candidates must be prepared.

## When Not To Use

Do not use Linker to:

1. Modify source documents.
2. Modify code, config, schema, API, tests, generated files, or anchors.
3. Collect or accept high-impact decisions.
4. Assign workers or accept worker reports.
5. Treat candidates as automatic edits or automatic acceptance.
6. Expand a simple filename search into an artifact graph workflow when metadata is irrelevant.

## Required Input

Require:

1. User request or main current task.
2. Configured document root.
3. Current work or change intent.
4. Related source documents, standards, work orders, progress, and decisions.
5. Known `key.id`, `key.refs`, capability, output artifact, code, config, schema, API, test, path, symbol, or keyword seeds.
6. Optional changed documents, output artifact files, or diff summary.
7. Optional Change Set or worker assignment preparation purpose.

## Workflow

1. Resolve the document root.
2. Read Artifact Graph and Linker standards.
3. Split input seeds into document, decision, work order, key metadata, output artifact, capability, API, code, config, schema, test, path, symbol, and keyword evidence.
4. Search Keystone metadata and code/config/schema/API/test anchors.
5. Check repository evidence without modifying files.
6. Separate declared, observed, and inferred relations.
7. Grade candidates as `required`, `strong_candidate`, `weak_candidate`, `informational`, or `excluded`.
8. Separate reuse candidates, test candidates, stale candidates, and metadata gaps.
9. Interpret source/output surfaces and handoff owners: Author for source documents, Main direct or Coordinator for repo-local skill source and other non-source output artifacts, Coordinator for repository source surfaces, Main/Clarify for decisions.
10. Recommend the next skill without performing edits.

## Routing Gate

Linker is read-only. It reports `source_document | decision | work_order -> output_artifact` relations and stale/gap candidates. `skill_source`, code, config, schema, API, test, and generated files are output artifact surfaces, not the core graph concept. File-changing follow-up requires Main to emit `keystone_routing_decision`; Author handles `source_document`, Main direct or Coordinator handles small non-source output artifacts such as `skill_source`, and Coordinator handles `repository_source`.

## Default User Response

By default, answer users with a concise human-facing brief instead of the full `linker_report`. Include graph interpretation status, required candidates, representative strong candidates, key stale/gap/reuse risks, handoff owners, recommended next action, and key source refs.

Do not silently hide required candidates. If candidate lists are large, summarize counts and representative evidence while keeping full payload availability explicit. Keep `linker_report` as an agent-facing structured payload. Emit the full payload only when the user asks for it, another Keystone skill needs it for handoff, or audit/debug/verification evidence requires it. Optional `keystone-viewer` may render the payload, but it must not change candidate grades, risks, handoff owners, or recommended next action.

## Output Contract

Use:

```yaml
linker_report:
  request_summary:
  mode:
  seed_artifacts:
    - key_id:
      locator:
      reason:
  affected_capabilities:
    required:
    strong_candidates:
    weak_candidates:
  output_artifact_candidates:
    required:
    strong_candidates:
    weak_candidates:
    informational:
  code_candidates:
    required:
    strong_candidates:
    weak_candidates:
  api_candidates:
    required:
    strong_candidates:
    weak_candidates:
  config_candidates:
    required:
    strong_candidates:
    weak_candidates:
  schema_candidates:
    required:
    strong_candidates:
    weak_candidates:
  test_candidates:
    required:
    strong_candidates:
    weak_candidates:
  document_candidates:
    required:
    strong_candidates:
    weak_candidates:
  reuse_candidates:
    - key_id:
      locator:
      evidence:
      reuse_decision_hint:
      modularization_decision_needed: true | false
      modularization_reason:
  metadata_gaps:
    - artifact:
      expected_metadata:
      reason:
  stale_candidates:
    mechanical:
    semantic:
  excluded_candidates:
    - artifact:
      reason:
  relations:
    declared:
    observed:
    inferred:
  graph_interpretation:
    status: ok | partial | blocked
    basis:
      - artifact_graph_standard
      - project_standard
    evidence_mode:
      declared:
      observed:
      inferred:
  source_surface_handoffs:
    author:
      - artifact:
        surface: source_document_frontmatter | section_comment | decision_record | api_contract_source_section
        recommended_change:
        reason:
    coordinator:
      - artifact:
        surface: code_anchor | config_anchor | schema_anchor | api_anchor | test_anchor
        recommended_change:
        reason:
    main_direct_or_coordinator:
      - artifact:
        surface: output_artifact | skill_source | generated_file | repository_source
        recommended_change:
        reason:
    main_or_clarify:
      - topic:
        reason:
        suggested_decision_options:
          - reuse_existing
          - extend_existing
          - extract_shared_module
          - create_new
          - investigate_first
  graph_owner_note:
    interpretation_owned_by: keystone-linker
    edit_authority: author_main_direct_or_coordinator_only
  candidate_budget:
    applied: true | false
    truncated:
      required:
      strong_candidates:
      weak_candidates:
      informational:
    omitted_summary:
  risks_and_gaps:
  recommended_next_action:
    skill:
    reason:
```

## Output Examples

```yaml
linker_report:
  request_summary: Check whether S08 source documents still match their produced skill source output.
  mode: Impact Analysis
  seed_artifacts:
    - key_id: key.work.skill-creation.order
      locator:
        path: 00_docs/works/r001-bootstrap-keystone/skill-creation/key-work-skill-creation.md
      reason: S08 work order drives generated skill source.
  affected_capabilities:
    required: []
    strong_candidates: []
    weak_candidates: []
  output_artifact_candidates:
    required:
      - artifact: skills/keystone-reader/SKILL.md
        artifact_kind: skill_source
        produced_from:
          - 00_docs/works/r001-bootstrap-keystone/skill-creation/key-work-skill-creation.md
        reason: S08 work order produces repo-local Keystone skill source outputs.
    strong_candidates: []
    weak_candidates: []
    informational: []
  code_candidates:
    required: []
    strong_candidates: []
    weak_candidates: []
  metadata_gaps: []
  stale_candidates:
    mechanical: []
    semantic: []
  relations:
    declared: []
    observed: []
    inferred: []
  graph_interpretation:
    status: ok
    basis:
      - artifact_graph_standard
      - project_standard
    evidence_mode:
      declared: []
      observed:
        - skills/keystone-reader/SKILL.md
      inferred: []
  source_surface_handoffs:
    author: []
    coordinator: []
    main_direct_or_coordinator:
      - artifact: skills/keystone-reader/SKILL.md
        surface: skill_source
        recommended_change: Align produced skill source output with governing source documents.
        reason: Skill source is an output artifact produced from S08, not an Author source document.
    main_or_clarify: []
  graph_owner_note:
    interpretation_owned_by: keystone-linker
    edit_authority: author_main_direct_or_coordinator_only
  candidate_budget:
    applied: false
  risks_and_gaps: []
  recommended_next_action:
    skill: keystone-coordinator
    reason: Bounded implementation may be needed if repository-source files require edits.
```

## Boundaries

1. Linker is read-only.
2. Linker may recommend source-surface handoffs but must not perform edits.
3. Linker does not make final decisions or Main acceptance decisions.
4. Linker does not assign workers.
5. Linker does not hide required candidates when applying candidate budgets.
6. Linker treats generated indexes as derived evidence, not source of truth.

## Stop Conditions

Stop when:

1. Document root cannot be resolved.
2. Seeds are too ambiguous to grade candidates meaningfully.
3. Sensitive or local-only data is needed without policy.
4. Candidate analysis requires unapproved execution, build, tests, or network access.
5. Artifact Graph mismatch could change task direction.
6. Stale/gap candidates require source authority or acceptance criteria changes.
7. Direct document or repository edits would be required.
8. Output artifact stale/gap candidates require edits before a routing decision exists.

## Verification

Verify Linker behavior by checking:

1. Four modes are distinct.
2. Operational graph interpretation does not imply edit authority.
3. Mechanical stale, semantic stale, and metadata gaps are separated.
4. Source surface handoff owners are separated.
5. Required candidates are not silently omitted.
6. Default user response summarizes candidates, risks, handoff owners, and next action without dumping the full structured payload.
7. `skill_source` candidates are reported as output artifact surfaces but never edited by Linker.

Suggested checks:

```bash
rg --files 00_docs
rg -n "source_surface_handoffs|graph_interpretation|graph_owner_note|candidate_budget" 00_docs/standards/skills/linker/key-standard-linker.md
```

## Related Source Documents

- `00_docs/standards/01_key-project-standard.md`
- `00_docs/standards/artifacts/key-standard-artifact-graph.md`
- `00_docs/standards/skills/linker/key-standard-linker.md`
- `00_docs/standards/skills/coordinator/key-standard-coordinator.md`
