---
name: keystone-reader
description: "Use for read-only orientation and work recovery from existing Keystone documents, including initialization-state reporting, relevant-source navigation, active work/current step recovery, and context brief preparation. Do not use to edit files, inspect an uninitialized repository as a Keystone-specific procedure, assign workers, accept results, or perform deep Artifact Graph impact/stale/gap analysis."
---

<!-- keystone: id=key.skill.reader kind=output_artifact artifact_kind=skill_source -->
<!-- keystone: produced_from=key.work.skill-runtime-implementation.order -->
<!-- keystone: governed_by=key.standard.project key.standard.skill.reader -->

# keystone-reader

## Purpose

Read existing Keystone source documents to orient the main agent, find relevant standards and work
records, recover active work, and prepare a concise context brief. Remain read-only.

This installed contract is self-contained. A consuming project does not need a project-local Reader
standard or `standards/skills/reader/**`. Project source documents and accepted decisions define project
meaning when they exist; Reader output does not replace them or Main acceptance.

## Use Reader For

1. Keystone document orientation and navigation.
2. Active round, current work, current step, and status-source recovery.
3. Finding relevant project standards, work orders, progress records, and decisions.
4. Preparing read-only context before document or implementation work.
5. Reporting mismatch between Keystone documents and repository evidence.
6. Determining whether deeper Artifact Graph interpretation should pass to `keystone-linker`.

Do not use Reader to edit any file, create standards or work records, collect high-impact decisions,
assign workers, review worker reports, or accept results. Deep artifact impact, stale, reuse, and
metadata-gap interpretation belongs to Linker.

## Inputs and Authority

Use the user request, repository root, current instructions, available Keystone configuration, and
existing project documents. Resolve the document root in this order when evidence is available:

1. Current user instruction.
2. `.keystone/config.local.yaml`.
3. `.keystone/config.yaml`.
4. Explicit project-local agent setting.
5. A single conflict-free existing document convention.
6. Default candidate `00_docs`.

Do not require a work order, progress record, Artifact Graph, or local skill standard merely to run.
Treat absent material as unavailable context, not proof of project failure.

## Initialization Boundary

Determine state from actual settings and documents rather than a boolean flag:

- `uninitialized`: no authoritative document root or minimum Keystone structure is discoverable.
- `bootstrapping`: Init scaffold and R000 exist while the project standard is being established.
- `partial`: configuration, root, Context Map, standards/works indexes, decision record, project
  standard, or new-project R000 material exists but required parts are incomplete.
- `conflicted`: valid roots, settings, or document meanings conflict and cannot be chosen safely.
- `ready`: one authoritative root, Context Map, standards/works indexes, decision record, and an accepted
  project standard provide recoverable work context. A new project also has an accepted R000; an adopted
  legacy corpus may be ready without retroactive config or R000.

Before initialization, do not create files and do not claim ownership of ordinary code, README,
configuration, or repository inspection. Main performs that general investigation without a
Keystone-specific Reader procedure.

If Reader is invoked before `ready`:

1. Report the actual state and evidence used.
2. Provide orientation only from Keystone material that exists.
3. List Keystone context that could not be recovered.
4. Suggest `keystone-init inspect`, `initialize`, or `repair` as appropriate.
5. If the user refuses initialization, make no changes and explain the resulting limits and later Init
   option.

Missing work/progress records or graph evidence alone do not make the project `partial`. Conflicting
valid document roots are a real decision topic; Reader reports the conflict without choosing one.

## Workflow

1. Detect initialization state and resolve or narrow the document-root candidates.
2. If present, read `key-context-map.md` first.
3. Follow the project standards and works indexes that actually exist.
4. For work recovery, read the active round index and current work node's order and progress record.
5. Follow only child indexes and references relevant to the request.
6. Treat `key.id`, `key.refs`, typed relations, paths, headings, and keywords as navigation evidence,
   not edit authority or automatic impact propagation.
7. When code/config/schema/API/test impact, stale, reuse, or gap analysis must go beyond navigation,
   recommend Linker and pass the observed seeds without confirming graph conclusions.
8. Report source conflicts; do not silently prefer documents over operative code or vice versa.
9. Recommend the next responsible actor without editing or requiring a routing ceremony for a small,
   already-scoped task.

Use an orientation, navigation, or work-preparation emphasis as the request requires; do not require
the caller to name a mode.

## Result Contract

Keep the internal result proportional to available evidence. Include:

```yaml
reader_output:
  initialization_state:
  document_root:
  request_summary:
  project_summary:
  active_round:
  current_work:
  current_step:
  current_work_status:
  status_sources:
  status_conflicts:
  matched_documents:
  unavailable_keystone_context:
  artifact_graph_needed:
  artifact_seed_candidates:
  operational_boundaries:
  risks_and_gaps:
  recommended_next_action:
  sources_read:
  assumptions:
```

For work preparation, also include Goal, Scope, applicable standards, completion criteria, stop
conditions, and verification when recoverable. Any handoff remains preparatory; Reader does not create
a final worker assignment.

## Default User Response

Give a concise human-facing brief with the initialization/work state, key finding, unavailable context
or conflict, recommended next action, and key sources. Do not expose the full `reader_output` or context
brief unless the user requests it or a handoff, audit, debugging, or verification need requires it.

Apply the Payload Disclosure Gate before responding: do not print raw `*_output`, `*_result`,
`*_report`, `worker_assignment`, or routing payload blocks by default. Summarize their meaning without
changing the underlying risks or recommendation.

## Boundaries and Stop Conditions

1. Never write files or change project state.
2. Never turn partial navigation evidence into a confirmed Artifact Graph relation.
3. Never make a high-impact project decision for the user.
4. Stop and report when conflicting valid roots prevent safe reading.
5. Stop and report when source conflict or sensitive/local-only access could change the task direction.
6. Do not stop merely because work records, progress records, graph evidence, or local skill standards
   are absent; return the useful partial result instead.

## Verification

Check that Reader:

1. Runs without a consuming-project `standards/skills/reader/**` document.
2. Produces no file changes before or after initialization.
3. Does not take ownership of general pre-initialization repository inspection.
4. Reports uninitialized, partial, conflicted, and ready evidence without guessing.
5. Recovers work when records exist and fails softly when they do not.
6. Hands deep graph interpretation to Linker.
7. Hides structured payloads by default.
