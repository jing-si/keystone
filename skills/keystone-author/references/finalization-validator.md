# Acceptance Finalization Validator

`scripts/run_finalization_validation.py` is the fail-closed package entry point and invokes the
diagnostic-only `scripts/validate_finalization.py` command bundled with `keystone-author`.
It reads a JSON manifest and referenced Keystone documents; it never edits files or changes acceptance,
work status, or `finalization.state`.

## Invocation

```bash
python3 <keystone-author-package>/scripts/run_finalization_validation.py \
  --root <repository-or-document-root> \
  --manifest <finalization-manifest.json>
```

The runner evaluates the Author core first, then required Artifact Graph evidence with the installed
Linker runner, and finally an optional project extension. A failure at any stage stops later stages.
`--graph-runner` may override the sibling package path for an installed-layout adapter or test, but it
does not make graph validation optional.

An additive project validator may be supplied with `--extension <python-script>`. The package runner
always evaluates the core validator first and returns a core failure without invoking the extension,
so a project check cannot weaken or replace core rules. When a repository supports pre-commit or CI,
its hook may call `scripts/check_finalization_hook.sh` with the same arguments; this wrapper delegates
to the package runner and has no edit or acceptance authority.

Exit codes:

- `0`: required checks passed.
- `1`: deterministic validation findings were reported.
- `2`: invocation or execution input was unavailable or malformed.

Stdout is one JSON object containing `schema_version`, `status`, `diagnostics`, and `summary`. Each diagnostic has
`severity`, `code`, `message`, and an optional repository-relative `path`.

## Manifest

```json
{
  "schema_version": 3,
  "acceptance_ref": "R004/S02/main-acceptance",
  "steps": [
    {
      "ref": "R004/S02",
      "work_ref": "R004/finalization-runtime-validator",
      "status": "complete",
      "approval_state": "accepted",
      "progress_path": "00_docs/works/r004-acceptance-finalization/finalization-runtime-validator/key-progress.md"
    }
  ],
  "accepted_steps": ["R004/S02"],
  "execution_transitions": [
    {"ref": "R004/S02", "from": "in_progress", "to": "complete"}
  ],
  "approval_transitions": [
    {"ref": "R004/S02", "from": "pending", "to": "accepted", "evidence": "Main accepted the verified result."}
  ],
  "active_steps": [],
  "active_step_sources": [
    {"category": "work_index", "path": "00_docs/works/r004-acceptance-finalization/finalization-runtime-validator/00_key-index.md"},
    {"category": "round_index", "path": "00_docs/works/r004-acceptance-finalization/00_key-index.md"},
    {"category": "context_map", "path": "00_docs/key-context-map.md"}
  ],
  "early_work": [],
  "finalization": {
    "required": true,
    "state": "in_progress",
    "progress_path": "00_docs/works/r004-acceptance-finalization/finalization-runtime-validator/key-progress.md",
    "evidence": ["main_acceptance", "impact_dispositions", "source_updates", "semantic_review"]
  },
  "graph_sync": {
    "required": false,
    "disposition": "not_applicable",
    "reason": "No graph-relevant source changed."
  },
  "impact_candidates": [
    {
      "category": "round_index",
      "artifact": "R004 round index",
      "path": "00_docs/works/r004-acceptance-finalization/00_key-index.md",
      "disposition": "updated",
      "reason": "The owning round represents S02 activation."
    },
    {
      "category": "progress",
      "artifact": "S02 progress",
      "path": "00_docs/works/r004-acceptance-finalization/finalization-runtime-validator/key-progress.md",
      "disposition": "updated",
      "reason": "Progress records acceptance and finalization evidence."
    },
    {
      "category": "work_order_change_set",
      "artifact": "S02 work order and Change Set",
      "path": "00_docs/works/r004-acceptance-finalization/finalization-runtime-validator/key-work-finalization-runtime-validator.md",
      "disposition": "updated",
      "reason": "The implementation result and changed surfaces are recorded."
    },
    {
      "category": "work_index",
      "artifact": "S02 work index",
      "path": "00_docs/works/r004-acceptance-finalization/finalization-runtime-validator/00_key-index.md",
      "disposition": "updated",
      "reason": "The owning Work status was evaluated."
    },
    {
      "category": "root_index",
      "artifact": "root works index",
      "path": "00_docs/works/00_key-index.md",
      "disposition": "no_change",
      "reason": "R004 remains the active round."
    },
    {
      "category": "context_map",
      "artifact": "Context Map",
      "path": "00_docs/key-context-map.md",
      "disposition": "updated",
      "reason": "The active_steps representation changed."
    },
    {
      "category": "standard_decision_plan",
      "artifact": "accepted S01 sources",
      "path": "00_docs/works/key-decisions.md",
      "disposition": "no_change",
      "reason": "Runtime implements the accepted policy without changing its meaning."
    },
    {
      "category": "recovery",
      "artifact": "R004 recovery instructions",
      "path": "00_docs/works/r004-acceptance-finalization/00_key-index.md",
      "disposition": "updated",
      "reason": "Recovery starts from the remaining active_steps set."
    },
    {
      "category": "implementation_gate",
      "artifact": "S02 implementation gates",
      "path": "00_docs/works/r004-acceptance-finalization/finalization-runtime-validator/key-work-finalization-runtime-validator.md",
      "disposition": "no_change",
      "reason": "No unresolved implementation choice remains.",
      "gate_state": "resolved",
      "gate_scope": "R004/S02 implementation"
    },
    {
      "category": "residual_risk",
      "artifact": "S02 residual risks",
      "path": "00_docs/works/r004-acceptance-finalization/finalization-runtime-validator/key-progress.md",
      "disposition": "no_change",
      "reason": "No S02 residual risk requires a source update.",
      "risk_state": "none",
      "risk_items": []
    },
    {
      "category": "namespace",
      "artifact": "shared namespaces",
      "path": "00_docs/works/r004-acceptance-finalization/finalization-runtime-validator/key-progress.md",
      "disposition": "no_change",
      "reason": "No duplicate namespace/value ownership was found.",
      "namespace_state": "checked"
    }
  ],
  "namespace_entries": []
}
```

Schema versions 1 and 2 are diagnostic compatibility paths for existing unfinished finalization only.
The live validator never returns success for a version-1 or version-2 `finalization.state: complete`,
and version 1 cannot contain `graph_sync`. Previously completed
R004 records are historical acceptance evidence: rerunning this validator does not newly approve
their completion, cancel their acceptance, or require a retroactive state edit. Any new completion or
graph-relevant finalization must use version 3. Author emits schema version 3 for every new
finalization. Version 3 requires one graph assessment:

```json
{
  "graph_sync": {
    "required": true,
    "disposition": "required",
    "reason": "Document metadata changed.",
    "validation_manifest_path": ".keystone/graph-validation.json",
    "transaction_id": "graph-tx-..."
  }
}
```

`disposition` is `required`, `not_applicable`, or `deferred`. `required` is true for `required` and
`deferred`, and false for `not_applicable`. A required finalization may remain `in_progress` without
transaction evidence so repair can resume. `complete` requires `not_applicable`, or a required graph
validation manifest whose inline transaction ID matches `transaction_id` and whose bundled Linker
validation proves the transaction's full `verified` closure. The Author core independently requires
the bound transaction state to be exactly `verified`; every non-verified state fails closed before
completion. The sibling Linker runner then verifies attestations, application results, digests,
reconstruction, and mechanical evidence instead of trusting that state label alone. `deferred` always
blocks `complete`. A stored state string, cache, or evidence label cannot replace rerunning Linker
validation.

The manifest must contain all core categories: `progress`, `work_order_change_set`, `work_index`,
`round_index`, `root_index`, `context_map`, `standard_decision_plan`, `recovery`,
`implementation_gate`, `residual_risk`, and `namespace`.

Allowed candidate dispositions are `updated`, `no_change`, `historical`, `out_of_scope`,
`clarification_required`, and `integration_gate`. Every candidate requires a reason. Candidates that
claim `updated`, `no_change`, or `historical` also require an existing path under `--root`.

Each Step ref, Work ref, and status must match the referenced Progress `step_ref`, `work_ref`, and
`work_status`. The work index, round index, and Context Map active-step sources must each contain the
same `active_steps` set as the manifest. Every `active_steps` ref must resolve
to a declared Step with an active status. Execution and approval transitions must name refs in
`accepted_steps`.
Every accepted Step has exactly one `in_progress` to `complete` execution transition and
exactly one `pending` to `accepted` approval transition with evidence.
Future-Step partial work
belongs in `early_work` with a declared target, cause, completed and remaining scope, and
`status_effect: none`. Duplicate namespace/value claims by different owners are validation failures.
Non-historical Markdown candidates are scanned for singular current-step claims because recoverable
state must be represented by `active_steps`.

## Authority and fail-closed mapping

Author owns manifest preparation, source edits, finalization transitions, and interpretation of the
diagnostics. The runner maps a missing core validator to `validator_unavailable`; a process start failure,
timeout, validator exit `2`, or unreadable output to `validator_execution_failed`. Exit `1` preserves
`finalization.state: in_progress` with the reported findings. Project adapters may add checks but cannot
remove core fields, turn a core failure into success, or gain source-edit or acceptance authority.

A missing Linker runner maps to `graph_validator_unavailable`; an outer timeout maps to
`graph_validation_timeout`; malformed JSON or an invalid Linker envelope maps to
`graph_validation_output_malformed`; and a process start failure maps to
`graph_validation_execution_failed`. A valid Linker exit-2 diagnostic keeps its Linker reason code.
Core, graph, and extension diagnostics are additive. Graph findings or execution failures prevent the
extension from running. None of these outcomes cancels Main acceptance or rewrites progress. Resume
reuses preserved applied results for a `partially_applied` transaction; a revised `conflicted` or
`failed` attempt records a new transaction ID, updates the graph evidence reference, and reruns the same
finalization command.
