---
name: keystone-linker
description: "Use for Artifact Graph interpretation and graph-relevant document or artifact deltas: discovery, impact, stale/gap review, reuse/test candidates, canonical mutation planning, source-surface handoffs, and worker context. Do not use to edit source surfaces, make user decisions, or assign workers."
---

<!-- keystone: id=key.skill.linker kind=output_artifact artifact_kind=skill_source -->
<!-- keystone: produced_from=key.work.skill-runtime-implementation.order -->
<!-- keystone: governed_by=key.standard.project key.standard.skill.linker -->

# keystone-linker

## Purpose

Interpret Keystone Artifact Graph evidence without writing source surfaces. Discover output artifacts,
classify impact, stale, and metadata-gap candidates, report reuse/test candidates, prepare handoffs,
and decide canonical graph mutations for graph-relevant synchronization transactions.

Source documents, accepted decisions, output artifacts, and verification evidence are the source of
truth. Linker output does not replace them or Main acceptance. Linker is the sole canonical graph
mutation decision owner, but is source-write-free: exact patches are attested and applied only by the
owner of each source surface.

## Runtime Authority

Use this installed package as the complete Linker runtime contract. Never require a consuming
project to contain `standards/skills/linker/**` or another project-local skill standard. Keystone
source-repository skill standards are development specifications, not runtime prerequisites.

Read project-local material only as project evidence when it exists:

1. Configured document root and Context Map.
2. Relevant project standards, decisions, work orders, and progress records.
3. Project-specific Artifact Graph policy and declared `key.*` metadata.
4. Repository paths, symbols, APIs, config, schemas, tests, diffs, and other observed evidence.

Main may invoke Linker without separate user permission because Linker never writes source surfaces.
Canonical mutation planning does not grant edit authority or widen the current scope. Do not infer
an adoption profile from graph coverage; Keystone uses one operating model.

## Graph Interpretation Rules

Apply these rules without depending on project-local Linker instructions:

1. Prefer `source_document | decision | work_order -> output_artifact` as the core graph relation.
2. Treat skill source, code, config, schema, API, test, generated file, and document artifact as
   output-artifact surfaces.
3. Read typed relations from `produces`, `provides`, `uses`, `implements`,
   `requires_verification_of`, `verifies`,
   `governed_by`, `documents`, `supersedes`, `derived_from`, and `depends_on`.
   `requires_verification_of` runs from an acceptance criterion or claim -> target. When that target
   changes, review the requirement and verification plan; the relation is not proof that verification
   ran. `verifies` runs from a test artifact or verification result -> target and records actual
   verification evidence.
4. Treat `key.refs` as navigation evidence, not automatic impact propagation.
5. Keep stable identity separate from path, symbol, test name, config key, or schema locator.
6. Treat API artifacts as contracts by default. Do not infer that an API provides a capability
   without an accepted exception; find its implementers and providers instead.
7. Distinguish declared metadata, observed repository evidence, and semantic inference.
8. Grade candidates as `required`, `strong_candidate`, `weak_candidate`, `informational`, or
   `excluded`; candidate discovery never authorizes edits or acceptance.
9. Separate mechanical stale evidence, semantic stale candidates, and metadata gaps.
10. Treat generated indexes as derived evidence, never as the source of truth. Linker may refresh only
    its disposable cache outside the repository; it never writes a repository source surface.
11. Treat independently referenceable Markdown headings, list items, table rows, decisions,
    claims, and acceptance items as document-item nodes when they declare stable item metadata.
12. Inherit document and section authority, `governed_by`, and lifecycle into an item when they are
    not overridden, but never inherit `id` or `supersedes`.
13. Interpret a partial decision replacement through `key.claim.* -> supersedes -> key.claim.*`;
    never promote it into whole-document supersession without evidence.
14. Treat `legacy_terms` as search evidence, not a typed relation, and classify matches by the
    containing item's effective authority and lifecycle.
15. Treat output `authority.produced_from` as provenance and derive `<source> produces <output>` only
    as generated/inferred reverse evidence. Do not normalize `produced_from` as a typed relation;
    report a missing target as unresolved provenance or a metadata gap.
16. Treat `revised_by` as revision-history evidence, not a typed relation or proof of authority,
    impact, supersession, production, or governance. Report ambiguous evidence as informational or unknown.

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
8. Reader or another Keystone skill needs internal owner/ref readiness.

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
5. `Owner/Ref Index Readiness`: refresh or reuse a bounded derived index for context discovery.
6. `Graph Synchronization`: decide canonical mutations and exact owner-applied patches, reconcile
   attestation and apply results, then reconstruct and mechanically validate the transaction.

## Owner/Ref Index Readiness

This is a permissionless internal mode, not a user-facing command. Reader and other Keystone skills may
request it without Coordinator permission because it has no repository source-write authority.

1. Collect declared owner IDs and refs from meaningful source artifacts. Diagnose duplicate owners,
   unresolved refs, and locator gaps without requiring every artifact to have a typed relation.
2. Store the reverse index only in a disposable cache outside the repository, with a single writer.
   Source annotations, standards, and companion metadata remain authoritative; cache data is never
   acceptance or transaction evidence.
3. Freshness requires worktree identity, the discovery scope name, the sorted path set, and every
   source file's raw-byte SHA-256 digest. Git HEAD, mtime, or a timestamp is insufficient.
4. Docs scope discovers the configured document root. Repository scope uses explicit include/exclude
   rules and supported source/companion discovery, and runs lazily only when artifact context is needed.
5. Cache failure returns fail-soft diagnostics and raw source results; it does not block orientation.
6. Build an optional typed graph projection only for multi-hop, semantic-role, dependency,
   verification, or reuse queries. Broad similarity never creates a canonical edge.
7. Honor the serialized recursion guard. Reader-to-Linker and Linker-to-Reader chains must not re-enter
   the initiating lane.

## Workflow

1. Resolve an authoritative document root when the requested analysis depends on Keystone
   documents; otherwise work from the explicit seed and repository evidence.
2. Split seeds into documents, document items, decisions, claims, acceptance items, work orders,
   metadata, output artifacts, capabilities, APIs, code, config, schemas, tests, paths, symbols,
   visible item IDs, and keywords.
3. Search existing Keystone metadata, item comments, anchors, and repository evidence without
   modifying files.
4. Reconstruct only relations supported by declared, observed, or clearly labeled inferred
   evidence.
5. Read relation direction from source to target. Treat `produces`, `implements`, and `verifies`
   targets as `required` review seeds when their governing source or contract changes. Treat
   `uses`, `provides`, `governed_by`, `documents`, `supersedes`, and `derived_from` according to
   direction and evidence strength. Never promote filename or keyword overlap into a declared
   typed relation.
   Interpret `depends_on` as source-to-target semantic evidence and keep `work_gates` as separate
   execution evidence. Prefer structured metadata over legacy HTML dependency evidence and report conflicts.
6. Separate reuse candidates, test candidates, mechanical stale, semantic stale, and metadata gaps.
7. Apply fail-soft handling when graph evidence is absent or sparse: return a partial report with
   inspected evidence, uninspectable areas, and gaps. Do not fail initialization, claim a missing
   profile, call Coordinator automatically, or block the user's task merely for missing graph data.
8. Classify handoff owners: Author for source-document metadata; Main direct or a user-permitted
   Coordinator for output artifacts and repository-source surfaces; Main/Clarify for actual
   decisions.
9. Recommend the narrowest next action without performing edits, assignment, or acceptance.

## Graph Synchronization Mode

Use this mode only when multiple source surfaces must change together to close canonical meaning. A
single-surface owner/ref or metadata change stays in the surface owner's direct lane and only requires
index refresh and validation. A `document_delta` or `artifact_delta` with `graph_relevant: true` requests
classification; it does not by itself force a transaction.
The trigger does not create or expand user-approved scope, Coordinator permission, worker authority,
or acceptance. A safe `not_required` conclusion needs a concrete graph-relevance reason tied to the
changed locators and semantic summary; finalization records that outcome as `not_applicable`.

1. Reconstruct the graph from canonical source metadata, never from a derived cache alone.
2. Admit `declared` evidence. Admit `observed` evidence only after the owning surface confirms its
   meaning. Keep `inferred` evidence as a candidate and exclude it from canonical mutations.
3. Normalize capability-first. A bounded direct document-item-to-artifact relation is allowed only
   for a single schema constraint or policy implementation and records `direct_relation_reason`.
4. Decide canonical node/relation/provenance/locator/lifecycle mutations and an exact patch for every
   affected source surface. Each patch has one `author | main | coordinator` owner and its own raw-byte
   SHA-256 baseline. Linker never applies a patch.
5. Move `proposed -> awaiting_attestation`. Each owner returns exactly one patch decision:
   `confirm | reject | needs_revision`, with evidence. Reject or revision makes the transaction
   `conflicted`; all required confirms make it `ready_to_apply`.
6. Owners recheck their patch baseline immediately before write and return
   `applied | failed | stale_baseline`, a resulting digest for `applied`, and evidence. A stale baseline
   is never written. Preserve partial success as `partially_applied`.
7. Resume partial application by comparing already-applied patches with their recorded resulting
   digests and remaining patches with their baselines. Never blindly reapply a successful patch.
8. After apply, reconstruct from sources without cache and compare the result with the canonical
   mutation. Run the bundled validator described in
   [references/graph-runtime.md](references/graph-runtime.md). Only complete required confirmations,
   apply results, matching reconstruction, and passing mechanical validation produce `verified`.
9. A `conflicted` or `failed` transaction resumes through a new attempt with a new transaction ID and
   preserved attempt history. For `stale_baseline`, at least one baseline must change. For `reject` or
   `needs_revision`, the same baseline is allowed when the mutation or exact patch changes. For
   `reconstruction_mismatch`, change a baseline, mutation, or patch. A verified
   `transient_application_failure` may retry the same patch.
10. Treat transaction scope validation as the current-work gate. Report repository scope coverage debt
    separately; gaps outside the transaction do not widen or block the current work.

```yaml
graph_synchronization:
  schema_version: 1
  graph_relevance:
    relevant: true | false
    disposition: required | not_applicable | deferred
    reason:
  transaction: <canonical graph_transaction below>
  prior_attempts:
    - <canonical graph_transaction from an earlier attempt>

graph_transaction:
  schema_version: 1
  transaction_id:
  scope_ref:
  input_deltas:
    - kind: document_delta | artifact_delta
      source_surface:
      changed_locators: []
      semantic_summary:
      baseline_digest: sha256:<64-lowercase-hex> | absent
      graph_relevant: true | false
  canonical_mutations:
    - operation: add | update | remove
      entity: node | relation
      before:
      after:
      evidence: declared | observed
      direct_relation_reason:
  surface_patches:
    - patch_id:
      owner: author | main | coordinator
      surface: document_metadata | code_anchor | config_anchor | schema_anchor | api_anchor | test_anchor | companion_metadata
      target_path:
      baseline_digest: sha256:<64-lowercase-hex> | absent
      exact_patch:
      required: true | false
  attestations:
    - patch_id:
      owner: author | main | coordinator
      decision: confirm | reject | needs_revision
      evidence:
  apply_results:
    - patch_id:
      result: applied | failed | stale_baseline
      resulting_digest:
      evidence:
  state: proposed | awaiting_attestation | ready_to_apply | applying | partially_applied | verified | conflicted | failed
  reconstruction:
  mechanical_validation:
  coverage_debt: []
```

`graph_relevance` is finalization/report evidence and `prior_attempts` is retry-history evidence; neither
is a canonical transaction field. The bundled runtime serializes the current `transaction` and every
`prior_attempts` entry with the same exact `graph_transaction` wire. `reconstruction` is either `null` or
`{baseline: <GraphSnapshot>, result: <GraphSnapshot>}`. `mechanical_validation` is the validator's
schema-versioned diagnostic envelope, not a bare diagnostic array. A CLI manifest passes only the current
canonical transaction in its `transaction` field; it does not silently discard synchronization-envelope
fields.

## Document Item Metadata

Parse document items from these Markdown surfaces:

1. A compact or multiline `key` comment immediately above a heading.
2. A compact or multiline `key` comment immediately above a list item.
3. A compact `key` comment in the first cell of a Markdown table row; keep the visible row ID as a
   locator rather than treating it as stable identity.

Recognize `key.rule.*`, `key.claim.*`, and `key.acceptance.*` as item namespaces in addition to
document, decision, work, capability, and output-artifact namespaces. Do not require metadata on
every sentence, bullet, or row. An existing independently meaningful item without metadata is a
metadata-gap candidate when the available evidence shows it must be referenced, replaced, or
verified separately.

Resolve effective item metadata in this order: document, enclosing section, item. Inherit source
authority, `governed_by`, and lifecycle. Compute effective `governed_by` as an ordered union of the
parent effective set and child declarations; emit typed relations only for targets declared on that
node. Child declarations must not silently expand source authority or approval. Never inherit `id`,
`supersedes`, or `legacy_terms`. Preserve locators such as path, heading, list position, and visible
row ID separately from stable identity.

When an accepted decision replaces only one claim while retaining its other meanings, follow the
declared claim-level `supersedes` edge. If either side lacks a claim node, report a metadata gap and
do not infer whole-decision or whole-document replacement.

Use `legacy_terms` only when attached to a replacement item with `supersedes` or to an explicitly
deprecated or removed item. Reject broad standalone terms such as `batch`, `handler`, or `plan` as
insufficient stale evidence. Classify an exact legacy-term match as follows:

- Active or pending authoritative item: semantic stale candidate, normally required review.
- Archived, rejected, superseded, removed, or explicit history evidence: informational or excluded
  historical evidence.
- Unknown containing item or ambiguous authority/lifecycle: metadata gap plus semantic review
  candidate.
- A progress or verification record claims removal while an active authoritative item still
  matches: semantic stale contradiction.

Do not treat a legacy term itself as an edge, silently suppress historical evidence, or require a
zero-match search across the entire corpus.

## Dependency Interpretation

Validate dependency target existence, duplicate and self references, gate scope and condition, source
step IDs, and structured/legacy conflicts. Evaluate each dependency as `satisfied`, `waiting`,
`unresolvable`, `invalid`, or `unknown`. A legacy work-level dependency without an explicit gate does
not block source start; treat it as a work-completion gate candidate. For step gates, confirm cycles
only from an expanded event graph of source step start/completion, target condition satisfaction, and
source work completion—not from a work-node graph alone. Do not mutate status, assign, cancel, or accept work.

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
      item_locator:
      expected_metadata:
      reason:
  stale_candidates:
    mechanical:
      - artifact:
        item_locator:
        evidence:
        reason:
    semantic:
      - artifact:
        item_key_id:
        item_locator:
        effective_lifecycle:
        legacy_term:
        classification: active_stale | removal_contradiction | ambiguous_review
        evidence:
  excluded_candidates:
    - artifact:
      item_locator:
      reason:
  relations:
    declared:
    observed:
    inferred:
  dependency_evaluation:
    - source:
      target:
      status: satisfied | waiting | unresolvable | invalid | unknown
      gate_scope:
      evidence:
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
        surface: source_document_frontmatter | section_comment | document_item_comment | decision_record | api_contract_source_section
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
    limit:
    counts:
      total:
      returned:
      required:
      strong_candidates:
      weak_candidates:
      informational:
    truncated:
      required:
      strong_candidates:
      weak_candidates:
      informational:
    omitted_summary:
      - grade: strong_candidate | weak_candidate | informational
        count:
        evidence_type:
        keyword_range: {first:, last:}
        path_range: {first:, last:}
        reason: candidate_budget
  risks_and_gaps:
  recommended_next_action:
    skill:
    reason:
  graph_synchronization:
    # Use the Graph Synchronization Mode wire above when a delta was assessed.
```

`candidate_budget_projection` sorts candidates deterministically by grade, stable ID, locator, and
traversal path. It always returns every `required` candidate even when that makes `returned` exceed
`limit`; only `strong_candidate`, `weak_candidate`, and `informational` entries may be truncated.
`truncated.required` is therefore always zero. When no entry is omitted, `applied` is false and
`omitted_summary` is empty.

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

1. Linker is source-write-free but is the sole canonical graph mutation decision owner.
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

1. Six modes are distinct.
2. Operational graph interpretation does not imply edit authority.
3. Mechanical stale, semantic stale, and metadata gaps are separated.
4. Source surface handoff owners are separated.
5. Required candidates are not silently omitted.
6. Default user response summarizes candidates, risks, handoff owners, and next action without dumping the full structured payload.
7. `skill_source` candidates are reported as output artifact surfaces but never edited by Linker.
8. Missing graph evidence produces a partial fail-soft result rather than a profile or initialization failure.
9. Repository-source changes are handed to Main direct or a user-permitted Coordinator.
10. Ordinary pre-init repository orientation does not require Reader or Linker.
11. Heading, list-item, and first-cell table-row metadata are parsed without conflating visible IDs
    with stable `key.id` values.
12. Parent authority, `governed_by`, and lifecycle inheritance is applied while `id`, `supersedes`,
    and `legacy_terms` remain item-local.
13. Partial decision replacement follows claim-level supersession and missing claim metadata is
    reported as a gap.
14. Active legacy-term matches, historical matches, ambiguous matches, and removal contradictions
    receive distinct classifications.
15. Duplicate item IDs, malformed item metadata, unknown relations, missing relation targets, and
    supersession cycles are mechanical stale evidence.
16. Dependency relations and gate evidence remain separate, legacy conflicts are reported, and cycles
    require expanded-event evidence without automatic work-state mutation.
17. Graph-relevant deltas are classified as direct refresh or multi-surface synchronization without
    widening scope or permission.
18. Only owner attestations, baseline-safe apply results, source reconstruction, and mechanical
    validation can produce a verified transaction; partial apply and new attempts remain resumable.

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
