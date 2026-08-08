# Coordinator actual-state closure validator

`scripts/validate_closure.py` is a diagnostic-only verifier. It never edits sources, creates graph
mutations, grants Main acceptance, or performs Author finalization. Manifest schema v2 binds a closure
decision to an immutable assignment and the repository's current raw bytes.

Run canonical schema v2 validation with host-supplied paths:

```bash
python3 <keystone-coordinator-package>/scripts/validate_closure.py \
  --root <repository-root> \
  --assignment <pre-work-assignment-v2.json> \
  --manifest <coordinator-closure-v2.json> \
  --evidence-root <external-evidence-directory>
```

`--linker-runner`, `--author-runner`, and `--timeout-seconds` are host options for package integration
and tests. A manifest cannot select executable commands. By default the validator invokes the sibling
installed Linker and Author runners. The repository root must resolve to an existing directory, and the
evidence root must be an existing host-controlled directory disjoint from the repository tree.

Every output keeps diagnostic envelope schema 1:

```json
{
  "schema_version": 1,
  "status": "pass | fail | error",
  "diagnostics": [],
  "summary": {"errors": 0, "warnings": 0}
}
```

Exit `0` means the declared phase passed. Exit `1` means valid inputs produced deterministic closure
diagnostics. Exit `2` means required input could not be read or parsed, including missing v2 runtime
context. Repository/evidence read failures, unavailable or timed-out runners, malformed runner output,
and a child runner `error` envelope also remain `status: error`/exit `2`.

## Immutable assignment

The separate assignment is captured before work and uses `schema_version: 2`. It contains:

- assignment ID, execution mode, purpose, authority, and exact goal;
- the complete bounded Context Pack and injected skill IDs/modes;
- normalized repository-relative read, allowed-edit, and excluded scopes;
- a full pre-work path/raw-byte SHA-256 snapshot, excluding only `.git` internals.

The validator hashes the assignment's raw bytes. Worker report and Coordinator review must repeat the
same assignment ID and digest. The report also carries the canonical JSON digest of the Context Pack.
Unknown fields in authority-bearing schema-v2 objects are errors. Direct library callers are a trusted
host boundary: they must supply the raw-byte assignment digest in canonical SHA-256 form; the CLI
computes it instead of trusting manifest input.

## Actual changed state

The validator snapshots `--root` without following symlinks and derives every added, modified, and
deleted file. The derived sorted path set must exactly equal `changed_files`; every path has exactly one
artifact delta with:

```yaml
kind: artifact_delta
source_surface:
change_kind: added | modified | deleted
changed_locators:
  - path: src/example.py
    symbol: Example.run
semantic_summary:
baseline_digest: sha256:<64-lowercase-hex> | absent
resulting_digest: sha256:<64-lowercase-hex> | absent
graph_relevant: true | false
```

`changed_locators` must be a non-empty array of canonical locator objects. Each object requires a
repository-relative `path`; unused optional `heading`, `symbol`, `test_name`, `config_key`, and
`schema_name` fields are omitted. Plain strings remain schema-v1 diagnostic compatibility only and
cannot authorize schema-v2 closure.

Baseline and resulting digests are recomputed from assignment and current bytes. Changed paths are
checked against allowed and excluded scope. Read-only, review-only, and verification authority cannot
carry actual changes. An allowed scope containing a symlink that escapes the repository fails closed.
This includes a selector equal to or below the escaping symlink, not only an ancestor selector.
`scope_check` is compared with the derived result rather than trusted.

`skill_usage` must exactly match the assignment's injected skill IDs and modes. A `work` closure target
applies required work-completion gates; a `step` target applies active-Step gates. Invalid,
unresolvable, and unknown gates remain fail-closed, while optional waiting gates remain non-blocking.
Step closure declares one `closure_step_ref` inside assignment `work_context.step_refs`. The schema-v2
projection keeps Step-only gates in `active_step_gates` and Work-only gates in
`work_completion_gates`; misfiled, duplicate, out-of-assignment, or evidence-free non-satisfied gate
summaries fail closed.

## Linker and Author runner binding

Required graph sync records a raw-byte-digested Linker validation manifest, verified transaction ID,
exact artifact-delta-set digest, and expected runner-envelope digest. The transaction input deltas must
equal the report projection, the transaction must be canonical schema v2, and the package-owned Linker
runner must return a passing envelope.
`not_applicable` graph sync requires a digested Linker classification bound to the same delta-set
digest; a reason string alone is insufficient.

Every post-acceptance closure records a digested Author finalization manifest and expected runner
envelope. Closure, finalization, and Author acceptance refs must be equal. Author accepted Steps must
equal the closure event's Steps and remain inside assignment scope. The authority-bearing manifest must
use Author schema v5; schema v4 remains historical Author read compatibility only. Only a passing Author
runner and `complete | waived` evidence can produce `closure_complete`; waiver still requires a concrete
reason.

## Compatibility

Manifest schema v1 remains readable for historical diagnostics, but `accept_candidate` and
`closure_complete` receive `legacy_schema_not_authoritative`. New authority-bearing closure evidence
must use schema v2. Diagnostic-envelope version and manifest version are deliberately separate.
