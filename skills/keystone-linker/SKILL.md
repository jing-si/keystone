---
name: keystone-linker
description: "Use for read-only Artifact Graph interpretation: artifact discovery, impact analysis, stale/gap review, reuse/test candidates, source-surface handoff seeds, and worker-assignment artifact context. Do not use to edit source documents, code/config/schema/API/test, make final decisions, or assign workers."
---

<!-- keystone: id=key.skill.linker kind=output_artifact artifact_kind=skill_source -->
<!-- keystone: produced_from=key.work.skill-runtime-implementation.order -->
<!-- keystone: governed_by=key.standard.project key.standard.skill.linker -->

# keystone-linker

## Purpose

Interpret Keystone Artifact Graph evidence read-only. Discover output artifacts, classify impact,
stale, and metadata-gap candidates, report reuse/test candidates, and prepare source-surface
handoffs or worker-assignment seeds.

Source documents, accepted decisions, output artifacts, and verification evidence are the source of truth. Linker output does not replace source documents, source edits, or Main acceptance. Linker owns operational graph interpretation, not source edit authority.

## Runtime Authority

Use this installed package as the complete Linker runtime contract. Never require a consuming
project to contain `standards/skills/linker/**` or another project-local skill standard. Keystone
source-repository skill standards are development specifications, not runtime prerequisites.

Read project-local material only as project evidence when it exists:

1. Configured document root and Context Map.
2. Relevant project standards, decisions, work orders, and progress records.
3. Project-specific Artifact Graph policy and declared `key.*` metadata.
4. Repository paths, symbols, APIs, config, schemas, tests, diffs, and other observed evidence.

Main may invoke Linker without separate user permission because Linker is read-only. Do not infer
an adoption profile from graph coverage; Keystone uses one operating model.

## Graph Interpretation Rules

Apply these rules without depending on project-local Linker instructions:

1. Prefer `source_document | decision | work_order -> output_artifact` as the core graph relation.
2. Treat skill source, code, config, schema, API, test, generated file, and document artifact as
   output-artifact surfaces.
3. Read typed relations from `produces`, `provides`, `uses`, `implements`, `verifies`,
   `governed_by`, `documents`, `supersedes`, and `derived_from`.
4. Treat `key.refs` as navigation evidence, not automatic impact propagation.
5. Keep stable identity separate from path, symbol, test name, config key, or schema locator.
6. Treat API artifacts as contracts by default. Do not infer that an API provides a capability
   without an accepted exception; find its implementers and providers instead.
7. Distinguish declared metadata, observed repository evidence, and semantic inference.
8. Grade candidates as `required`, `strong_candidate`, `weak_candidate`, `informational`, or
   `excluded`; candidate discovery never authorizes edits or acceptance.
9. Separate mechanical stale evidence, semantic stale candidates, and metadata gaps.
10. Treat generated indexes as derived evidence, never as the source of truth or a Linker write
    target.

## When To Use

Use Linker when:

1. Source document, decision, or work order changes may affect output artifacts.
2. Output artifact changes may make source documents, decisions, or work orders stale.
3. Existing capabilities, APIs, reusable code, config, schema, tests, skill sources, or generated artifacts must be found before implementation.
4. Metadata gaps, mechanical stale, or semantic stale candidates must be reported.
5. Coordinator needs artifact context, reuse candidates, tests, stale risks, or metadata sync risks before a worker assignment.
6. Change Set impact seeds and required/optional/excluded candidates must be prepared.
7. Main needs read-only graph interpretation and chooses to use Linker without a separate approval
   ceremony.

## When Not To Use

Do not use Linker to:

1. Modify source documents.
2. Modify code, config, schema, API, tests, generated files, or anchors.
3. Collect or accept high-impact decisions.
4. Assign workers or accept worker reports.
5. Treat candidates as automatic edits or automatic acceptance.
6. Expand a simple filename search into an artifact graph workflow when metadata is irrelevant.
7. Make ordinary pre-initialization repository inspection a Keystone-owned prerequisite.

## Input

Use the evidence available for the request:

1. User request or Main's current task.
2. Current work or change intent, when known.
3. Any existing source documents, decisions, work records, and graph metadata.
4. Known `key.id`, `key.refs`, capability, artifact, path, symbol, or keyword seeds.
5. Changed files, a diff summary, Change Set, or assignment-preparation purpose when provided.

A configured document root, work record, or graph metadata is not universally required. If the
available seed cannot support a requested conclusion, report the limitation and the smallest next
investigation instead of inventing a relation.

## Modes

Choose the narrowest mode that answers the request:

1. `Artifact Discovery`: find related capabilities, output surfaces, evidence, and reuse candidates.
2. `Impact Analysis`: rank artifacts affected by a source or output change.
3. `Stale/Gap Review`: separate mechanical stale evidence, semantic stale candidates, and missing
   metadata.
4. `Worker Assignment Seed`: package artifact context, reuse/test candidates, and sync risks for a
   permitted Coordinator assignment.

## Workflow

1. Resolve an authoritative document root when the requested analysis depends on Keystone
   documents; otherwise work from the explicit seed and repository evidence.
2. Split seeds into documents, decisions, work orders, metadata, output artifacts, capabilities,
   APIs, code, config, schemas, tests, paths, symbols, and keywords.
3. Search existing Keystone metadata, anchors, and repository evidence without modifying files.
4. Reconstruct only relations supported by declared, observed, or clearly labeled inferred
   evidence.
5. Read relation direction from source to target. Treat `produces`, `implements`, and `verifies`
   targets as `required` review seeds when their governing source or contract changes. Treat
   `uses`, `provides`, `governed_by`, `documents`, `supersedes`, and `derived_from` according to
   direction and evidence strength. Never promote filename or keyword overlap into a declared
   typed relation.
6. Separate reuse candidates, test candidates, mechanical stale, semantic stale, and metadata gaps.
7. Apply fail-soft handling when graph evidence is absent or sparse: return a partial report with
   inspected evidence, uninspectable areas, and gaps. Do not fail initialization, claim a missing
   profile, call Coordinator automatically, or block the user's task merely for missing graph data.
8. Classify handoff owners: Author for source-document metadata; Main direct or a user-permitted
   Coordinator for output artifacts and repository-source surfaces; Main/Clarify for actual
   decisions.
9. Recommend the narrowest next action without performing edits, assignment, or acceptance.

## Initialization and Handoff Boundary

Normal inspection of code, README, configuration, and repository structure before Keystone exists
belongs to Main's ordinary capabilities. Do not require Reader or Linker for that orientation.

If Linker is invoked before initialization, stay read-only and report only graph-relevant evidence
that actually exists. Missing Keystone documents or graph metadata is a limitation, not an error.
Suggest Init only when establishing Keystone documents would help; never create them.

Do not require a routing payload for follow-up edits. Main may record routing context when multiple
surfaces, authority boundaries, or audit needs make it useful. Hand off source-document metadata to
Author. Hand off skill source, code, config, schema, API, test, generated, or other repository
outputs to Main direct or a Coordinator that has user permission for that work scope.

## Default User Response

By default, answer users with a concise human-facing brief instead of the full `linker_report`. Include graph interpretation status, required candidates, representative strong candidates, key stale/gap/reuse risks, handoff owners, recommended next action, and key source refs.

Do not silently hide required candidates. If candidate lists are large, summarize counts and representative evidence while keeping full payload availability explicit. Keep `linker_report` as an agent-facing structured payload. Emit the full payload only when the user asks for it, another Keystone skill needs it for handoff, or audit/debug/verification evidence requires it. Optional `keystone-viewer` may render the payload, but it must not change candidate grades, risks, handoff owners, or recommended next action.

Before sending a user-facing response, apply the Payload Disclosure Gate: do not print raw `*_output`, `*_result`, `*_report`, `worker_assignment`, or `keystone_routing_decision` blocks by default. Summarize the payload as graph interpretation status, required candidate counts, representative evidence, stale/gap risks, handoff owners, recommended next action, and key source refs; mention full payload availability only when useful.

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
      - installed_linker_contract
      - project_artifact_policy_if_present
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
    main_direct_or_permitted_coordinator:
      - artifact:
        surface: output_artifact | skill_source | repository_source | generated_file | code_anchor | config_anchor | schema_anchor | api_anchor | test_anchor
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
    edit_authority: author_or_main_direct_or_permitted_coordinator_only
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
  request_summary: Check whether the R002 S02 work order still matches its Linker skill output.
  mode: Impact Analysis
  seed_artifacts:
    - key_id: key.work.skill-runtime-implementation.order
      locator:
        path: 00_docs/works/r002-bootstrap-runtime-independence/skill-runtime-implementation/key-work-skill-runtime-implementation.md
      reason: R002 S02 produces the runtime-independent Keystone skill sources.
  affected_capabilities:
    required: []
    strong_candidates: []
    weak_candidates: []
  output_artifact_candidates:
    required:
      - artifact: skills/keystone-linker/SKILL.md
        artifact_kind: skill_source
        produced_from:
          - 00_docs/works/r002-bootstrap-runtime-independence/skill-runtime-implementation/key-work-skill-runtime-implementation.md
        reason: R002 S02 requires the Linker runtime contract to be self-contained and fail-soft.
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
      - installed_linker_contract
      - project_artifact_policy_if_present
    evidence_mode:
      declared: []
      observed:
        - skills/keystone-linker/SKILL.md
      inferred: []
  source_surface_handoffs:
    author: []
    main_direct_or_permitted_coordinator:
      - artifact: skills/keystone-linker/SKILL.md
        surface: skill_source
        recommended_change: Align produced skill source output with governing source documents.
        reason: Skill source is an output artifact produced from R002 S02, not an Author source document.
    main_or_clarify: []
  graph_owner_note:
    interpretation_owned_by: keystone-linker
    edit_authority: author_or_main_direct_or_permitted_coordinator_only
  candidate_budget:
    applied: false
  risks_and_gaps: []
  recommended_next_action:
    skill: main_or_permitted_keystone-coordinator
    reason: Main may edit a clear bounded output directly; delegated work requires Coordinator permission.
```

## Boundaries

1. Linker is read-only.
2. Linker may recommend source-surface handoffs but must not perform edits.
3. Linker does not make final decisions or Main acceptance decisions.
4. Linker does not assign workers.
5. Linker does not hide required candidates when applying candidate budgets.
6. Linker treats generated indexes as derived evidence, not source of truth.
7. Linker does not require a project-local Linker standard, graph profile, or routing payload.

## Stop Conditions

Stop when:

1. Conflicting document roots prevent identifying authoritative Keystone evidence needed by the
   requested analysis.
2. Seeds are too ambiguous to grade candidates meaningfully after bounded discovery.
3. Sensitive or local-only data is needed without authority.
4. Candidate analysis requires unapproved execution, builds, tests, network access, or another
   state-changing action.
5. Artifact Graph mismatch could materially change the task direction and cannot be reported as a
   bounded candidate.
6. A stale/gap conclusion would require Linker to decide source authority or acceptance criteria.
7. The request requires Linker itself to edit, assign, or accept work.

Do not stop solely because graph metadata, anchors, work records, project-local skill standards, or
a resolved document root are absent. Return a partial evidence report when useful.

## Verification

Verify Linker behavior by checking:

1. Four modes are distinct.
2. Operational graph interpretation does not imply edit authority.
3. Mechanical stale, semantic stale, and metadata gaps are separated.
4. Source surface handoff owners are separated.
5. Required candidates are not silently omitted.
6. Default user response summarizes candidates, risks, handoff owners, and next action without dumping the full structured payload.
7. `skill_source` candidates are reported as output artifact surfaces but never edited by Linker.
8. Missing graph evidence produces a partial fail-soft result rather than a profile or initialization failure.
9. Repository-source changes are handed to Main direct or a user-permitted Coordinator.
10. Ordinary pre-init repository orientation does not require Reader or Linker.

Suggested checks:

```bash
rg --files 00_docs
rg -n "source_surface_handoffs|graph_interpretation|graph_owner_note|candidate_budget" 00_docs/standards/skills/linker/key-standard-linker.md
```

## Development Traceability

These paths are source-repository development references, not consuming-project runtime inputs:

- `00_docs/standards/01_key-project-standard.md`
- `00_docs/standards/artifacts/key-standard-artifact-graph.md`
- `00_docs/standards/skills/linker/key-standard-linker.md`
- `00_docs/standards/skills/coordinator/key-standard-coordinator.md`
