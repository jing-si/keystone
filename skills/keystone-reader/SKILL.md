---
name: keystone-reader
description: "Use for read-only Keystone document orientation, source document navigation, active work/current step recovery, and context brief preparation. Do not use to edit documents, assign workers, accept reports, or perform deep artifact impact/stale/gap analysis."
---

# keystone-reader

## Purpose

Prepare read-only Keystone context from source documents. Use this skill to orient to a project, find relevant standards and work orders, recover the active round/current step, and produce a context brief for the main agent.

Source documents and accepted decisions are the source of truth. Reader output does not replace source documents, accepted decisions, or Main acceptance. If source documents conflict with repository evidence, report the conflict and recommended next action instead of changing either side.

## Required Source Documents

Read only the documents needed for the request, starting from:

1. `00_docs/key-context-map.md`
2. `00_docs/standards/00_key-index.md`
3. `00_docs/standards/01_key-project-standard.md`
4. `00_docs/works/00_key-index.md`
5. Active round index, usually `00_docs/works/r001-bootstrap-keystone/00_key-index.md`
6. Current work node index, work order, and progress record
7. Related child standards only when the current request needs them

## When To Use

Use Reader when the user or main agent needs:

1. Project orientation from Keystone documents.
2. The active work round, current work, current step, or status sources.
3. Relevant standards, work orders, progress records, or decisions for a request.
4. A pre-implementation or pre-edit source context brief.
5. Read-only mismatch reporting between source documents and repository state.
6. A recommendation for whether Reader, Clarify, Author, Linker, or Coordinator should handle the next step.

## When Not To Use

Do not use Reader to:

1. Modify source documents, code, config, generated files, progress records, or decisions.
2. Create or revise standards or work orders.
3. Collect or accept high-impact decisions.
4. Assign workers, finalize handoffs, review worker reports, or decide Main acceptance.
5. Perform deep Artifact Graph impact, stale, or metadata gap analysis. Hand that off to `keystone-linker`.

## Required Input

Require:

1. User request or main-agent current task.
2. Repository root.
3. Current instruction context.
4. Configured document root or enough context to resolve it.
5. Optional mode: `orientation`, `navigator`, or `work_prep`.

If input is insufficient, report `risks_and_gaps`; do not guess and do not edit.

## Workflow

1. Resolve the configured document root.
2. Read `key-context-map.md` first when present.
3. Read standards and works indexes to recover active round and current work.
4. Read the active work node index, work order, and progress record when current step recovery is needed.
5. Follow only relevant child-standard indexes.
6. Use `key.id`, `key.refs`, paths, headings, and keywords as navigation evidence, not automatic edit authority.
7. If capability/code/config/schema/API/test impact, stale, or gap analysis is needed, set `artifact_graph_needed: true` and recommend `keystone-linker`.
8. Include `sources_read`, `assumptions`, `risks_and_gaps`, and `recommended_next_action` in every output.

## Routing Gate

Reader never edits files. If the request shifts from orientation, navigation, or work prep into file-changing work, stop at a recommendation for Main to emit `keystone_routing_decision` and select Author, Coordinator, or Main direct lane. Reading Reader output or a context brief does not execute that lane.

## Default User Response

By default, answer users with a concise human-facing brief instead of the full `reader_output` payload. Include only current status, key finding, top risks or mismatches, recommended next action, and key source refs.

Keep `reader_output` and `keystone_context_brief` as agent-facing structured payloads. Emit the full payload only when the user asks for it, another Keystone skill needs it for handoff, or audit/debug/verification evidence requires it. Optional `keystone-viewer` may render the payload, but it must not change Reader's read-only judgment, risks, or recommended next action.

## Output Contract

For orientation, include:

```yaml
reader_output:
  mode: orientation
  document_root:
  project_summary:
  repository_snapshot:
  active_document_map:
  artifact_graph_summary:
  active_round:
  round_id:
  round_index:
  work_id:
  current_step:
  current_work_status:
  status_sources:
  status_authority_order:
  status_conflicts:
  recommended_read_order:
  operational_boundaries:
  risks_and_gaps:
  recommended_next_action:
  keystone_context_brief:
  sources_read:
  assumptions:
```

For navigation, include:

```yaml
reader_output:
  mode: navigator
  request_summary:
  key_ref_queries:
  matched_documents:
    - path:
      reason:
  artifact_seed_candidates:
  key_ref_matched_candidates:
  artifact_graph_needed:
  mismatches:
  active_round:
  round_id:
  round_index:
  work_id:
  status_sources:
  status_conflicts:
  recommended_read_order:
  why_each_document_matters:
  missing_or_ambiguous_documents:
  risks_and_gaps:
  recommended_next_action:
  sources_read:
  assumptions:
```

For work preparation, include:

```yaml
reader_output:
  mode: work_prep
  active_round:
  round_id:
  work_id:
  goal:
  source_context:
  applicable_standards:
  impact_seeds:
  artifact_graph_needed:
  artifact_seed_candidates:
  current_step:
  current_work_status:
  status_sources:
  status_authority_order:
  status_conflicts:
  scope:
  completion_criteria:
  verification:
  stop_conditions:
  risks_and_gaps:
  recommended_next_action:
  final_handoff_ready: false
  sources_read:
  assumptions:
```

## Output Examples

```yaml
keystone_context_brief:
  document_root: 00_docs
  active_round: R001 Bootstrap Keystone
  current_work: Skill Creation
  current_step: S08
  current_work_status: in_progress
  status_sources:
    context_map: 00_docs/key-context-map.md
    root_works_index: 00_docs/works/00_key-index.md
    active_round_index: 00_docs/works/r001-bootstrap-keystone/00_key-index.md
    work_progress: 00_docs/works/r001-bootstrap-keystone/skill-creation/key-progress.md
  status_authority_order:
    - root_works_index
    - active_round_index
    - work_progress
    - context_map
  human_intent_summary: Create repo-local Keystone skill source files.
  applicable_standards:
    - 00_docs/standards/01_key-project-standard.md
    - 00_docs/standards/skills/00_key-index.md
  artifact_graph_needed: false
  artifact_seed_candidates: []
  recommended_next_action:
    skill: keystone-coordinator
    reason: S08 skill source creation can proceed as a bounded implementation task after source context recovery.
  risks_and_gaps: []
  final_handoff_ready: false
```

## Boundaries

1. Reader is read-only.
2. Reader may identify artifact graph need, but must not finalize impact/stale/gap candidates.
3. Reader does not modify source documents or repository artifacts.
4. Reader does not produce final worker assignments.
5. Reader does not accept reports or mark progress accepted.

## Stop Conditions

Stop or ask main/user for a decision when:

1. The document root cannot be resolved.
2. Active round, current step, completion criteria, or applicable standards cannot be recovered.
3. Source documents conflict with the current user direction.
4. The next action requires source document, skill source, or repository-source edits before a routing decision exists.
5. Sensitive or local-only paths would be needed without clear policy.
6. Artifact graph mismatch could change the task direction.

## Verification

Verify Reader behavior by checking that:

1. Trigger and non-trigger boundaries are clear.
2. Output is explicitly read-only and does not replace source documents.
3. Work Prep output can feed Coordinator but keeps `final_handoff_ready: false`.
4. Artifact graph work is handed off to Linker.
5. Default user response summarizes status, risks, next action, and key sources without dumping the full structured payload.
6. File-changing next actions point to `keystone_routing_decision` instead of implying Reader edit authority.

Suggested checks:

```bash
rg --files 00_docs
rg -n "keystone-reader|Work Prep|final_handoff_ready|artifact_graph_needed" 00_docs/standards
```

## Related Source Documents

- `00_docs/standards/01_key-project-standard.md`
- `00_docs/standards/skills/reader/key-standard-reader.md`
- `00_docs/works/00_key-index.md`
- `00_docs/works/r001-bootstrap-keystone/00_key-index.md`
