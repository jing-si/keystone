# Coordinator closure validator

`scripts/validate_closure.py` validates that implementation received bounded Main and Keystone context
and that document, metadata, graph, verification, and finalization evidence is complete for the current
closure phase. It is diagnostic-only and never edits sources, creates graph mutations, grants Main
acceptance, or performs Author finalization.

Run:

```bash
python3 <keystone-coordinator-package>/scripts/validate_closure.py \
  --manifest <coordinator-closure-manifest.json>
```

Exit codes:

- `0`: valid for the declared closure phase
- `1`: valid JSON input with one or more contract diagnostics
- `2`: manifest could not be read or parsed

Every result uses:

```json
{
  "schema_version": 1,
  "status": "pass | fail | error",
  "diagnostics": [],
  "summary": {"errors": 0, "warnings": 0}
}
```

The manifest has two phases:

1. `pre_acceptance`: complete Context Pack, worker report, verification, and document/metadata/graph
   sync evidence may produce `accept_candidate`.
2. `post_acceptance`: every decision, including repair, escalation, or block, requires
   `keystone_closure.acceptance_ref` and non-empty `acceptance_evidence`. Only a ready Context Pack,
   ready canonical report (including scope and verification), closed sync, and Author finalization
   `complete | waived` may produce `closure_complete`. A `waived` finalization includes a concrete
   `waiver_reason`.

Execution modes:

- `direct_execution`: only `keystone-default-bounded-worker` may be selected.
- `orchestration`: at least one external skill must be selected and that worker owns implementation.

The Context Pack explicitly declares its Main checkpoint, work refs and Steps, source documents,
applicable standards, accepted-decisions array (empty only when explicit), completion criteria, scope
boundaries, forbidden changes, verification expectations, and artifact/Reader/Author context status and
evidence. It also preserves canonical `dependency_status`, explicit `active_step_gates`, and explicit
`work_completion_gates`. Each gate retains its ID, source, target, scope, result, and blocking value.
`ready` and `not_applicable` context states require evidence; `blocked` is non-ready. A required
active-Step gate whose result is not `satisfied` prevents `accept_candidate`; work-completion gates
remain separately visible and do not become an automatic Step-start block. Active-Step
`invalid | unresolvable | unknown` evidence requires repair or additional evidence even when the gate
was declared optional; optional `waiting` remains non-blocking.

Only worker report status `DONE` is accepted for `accept_candidate`; `DONE_WITH_CONCERNS`,
`NEEDS_CONTEXT`, `NEEDS_SCOPE_CHANGE`, and `BLOCKED` are non-ready. The report execution mode matches
the manifest. `changed_files` and `artifact_deltas` are explicit arrays (`[]` is genuine no-change), and
each changed file has exactly one `kind: artifact_delta` delta.

Every sync result must declare
`required | not_applicable | deferred`, a compatible state, a concrete reason, and evidence. Required
graph sync closes only at `verified`; required document and metadata sync close at `complete`.
`deferred`, missing, incompatible, or evidence-free results prevent `accept_candidate`.
