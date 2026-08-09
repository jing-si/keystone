# Coordinator actual-state closure validator

`scripts/validate_closure.py` is a diagnostic-only verifier. It never edits sources, creates graph
mutations, grants Main acceptance, or performs Author finalization. Coordinator assignment and closure
manifest schema v3 bind a closure decision to a complete repository snapshot and a parent-linked actor
phase chain.

## Contents

- Running the validator
- Complete assignment snapshot
- Phase-separated actual state
- Worker, Linker, and Author authority
- Compatibility and version domains

## Running the validator

Capture the T0 assignment snapshot with the package-owned entrypoint before any worker write:

```bash
python3 <keystone-coordinator-package>/scripts/capture_assignment_snapshot.py \
  --root <repository-root> \
  --policy <snapshot-policy-v3.json> \
  --phase-id assignment \
  --parent-snapshot-digest absent \
  --parent-evidence-digest absent \
  --assignment-id <assignment-id> \
  --assignment-subject-digest sha256:<non-circular-assignment-core> \
  --context-digest sha256:<canonical-context-pack> \
  --evidence-root <external-evidence-directory> \
  --capture-evidence-path <assignment-capture.json> \
  --capture-authority-key <external-coordinator-key> \
  --trusted-capture-authority-key-sha256 sha256:<pinned-key-bytes>
```

The capture command emits diagnostic envelope schema 1 with an embedded canonical repository snapshot
schema 3 and a `{path,digest}` reference to a newly created, single-link canonical phase-capture file.
Use the same command with phase IDs `worker`, `pre_acceptance_closure`, and `post_acceptance`, always
passing the preceding snapshot digest and preceding evidence raw-byte digest as parents. Only a passing
package-owned capture can establish a
phase boundary. The immutable assignment embeds the exact T0 snapshot and capture reference. Each
capture file binds repository root, policy, assignment ID, non-circular assignment authority core,
Context Pack digest, phase, parent, result,
UTC capture time, current package command digest, disjoint evidence root, random nonce and protected-key
HMAC with `trust_model: trusted-host-hmac-sha256`; times must increase strictly across the chain.

The capture key is an absolute, owner-private, single-link regular file of at least 32 raw bytes outside
both repository and evidence root. Its independently pinned SHA-256 fingerprint is host input, never a
manifest field. The HMAC proves possession of that protected host key and prevents repository/evidence
authors without the key from hand-writing a passing receipt. It does not prove an independently
controlled clock, binary execution, OS-user separation, or organizational independence. The trusted
Coordinator still owns the live-boundary invocation and protects the key and disjoint evidence root.

After Main accepts the pre-acceptance subject and before Author finalization writes, record a separate
acceptance event with a distinct Main key:

```bash
python3 <keystone-coordinator-package>/scripts/record_acceptance_event.py \
  --root <repository-root> \
  --evidence-root <external-evidence-directory> \
  --acceptance-event-path <main-acceptance.json> \
  --assignment-id <assignment-id> \
  --assignment-digest sha256:<raw-assignment-bytes> \
  --context-digest sha256:<canonical-context-pack> \
  --policy-digest sha256:<snapshot-policy> \
  --closure-target step \
  --closure-step-ref R010/S02 \
  --pre-snapshot-path <pre-acceptance-snapshot.json> \
  --pre-snapshot-digest sha256:<pre-acceptance-snapshot> \
  --parent-evidence-digest sha256:<pre-capture-raw-bytes> \
  --acceptance-ref R010/S02/main-acceptance \
  --accepted-step R010/S02 \
  --accepted-by main \
  --acceptance-authority-key <external-main-key> \
  --trusted-acceptance-authority-key-sha256 sha256:<pinned-main-key-bytes>
```

The Main key follows the same filesystem controls and must differ from the Coordinator capture key.
`--pre-snapshot-path` names a single-link canonical RepositorySnapshot-v3 JSON file below the external
evidence root. The runner parses that exact wire, recaptures the live repository with its embedded
policy and expected-absence set, and refuses acceptance unless the complete observed wire and digest
equal the pre-acceptance snapshot. This prevents a finalization or other write made before the Main
event from being relabeled as a post-acceptance delta.
The post-acceptance capture receipt names the acceptance-event raw digest as its evidence parent, which
forms `pre capture -> Main acceptance -> post capture` ordering.

Run canonical schema-v3 closure validation with host-supplied paths:

```bash
python3 <keystone-coordinator-package>/scripts/validate_closure.py \
  --root <repository-root> \
  --assignment <pre-work-assignment-v3.json> \
  --manifest <coordinator-closure-v3.json> \
  --evidence-root <external-evidence-directory> \
  --capture-authority-key <external-coordinator-key> \
  --trusted-capture-authority-key-sha256 sha256:<pinned-key-bytes> \
  --owner-key author=<external-author-apply-key> \
  --owner-key-sha256 author=sha256:<pinned-owner-key-bytes>
```

Post-acceptance validation also requires `--acceptance-authority-key` and
`--trusted-acceptance-authority-key-sha256`. Pre-acceptance validation never requires the Main key.
Repeat `--owner-key OWNER=PATH` and `--owner-key-sha256 OWNER=sha256:...` once for each owner with an
applied graph patch; valid owners are `author`, `main`, and `coordinator`. The exact closure-validator
flag surface is `--manifest`, `--root`, `--assignment`, `--evidence-root`, `--linker-runner`,
`--author-runner`, `--timeout-seconds`, `--capture-authority-key`,
`--trusted-capture-authority-key-sha256`, `--acceptance-authority-key`,
`--trusted-acceptance-authority-key-sha256`, repeatable `--owner-key`, and repeatable
`--owner-key-sha256`.

`--linker-runner`, `--author-runner`, and `--timeout-seconds` are host integration/test options. A
manifest cannot select executable commands. By default the validator invokes the sibling installed
Linker and Author runners. Graph and Author manifests are read once through a stable no-follow
descriptor; their digest and parsed object come from those same bytes, and the child runner receives a
private immutable copy of that captured generation. The repository root must be an existing directory. The host-controlled
evidence root must be an existing directory disjoint from the repository tree.

Every output keeps diagnostic envelope schema 1:

```json
{
  "schema_version": 1,
  "status": "pass | fail | error",
  "diagnostics": [],
  "summary": {"errors": 0, "warnings": 0}
}
```

Exit `0` means the declared phase chain passed. Exit `1` means valid inputs produced deterministic
closure diagnostics. Exit `2` means required input could not be read or parsed. Repository/evidence read
failures, unavailable or timed-out runners, malformed runner output, and a child-runner `error` envelope
also remain `status: error`/exit `2`.

## Complete assignment snapshot

The immutable assignment uses `schema_version: 3`. In addition to identity, execution mode, purpose,
authority, exact goal, Context Pack, injected skills, and normalized scope, it contains:

```yaml
snapshot_policy:
  schema_version: 3
  include_paths:
    - .
  exclusions:
    - path:
      reason:
  entry_budget:
document_root: 00_docs # exact configured document root; "." is explicit repository root
assignment_phase:
  phase_id: assignment
  actor: coordinator
  authority: verification
  capture_evidence: {path:, digest:}
  result_snapshot:
    schema_version: 3
    policy: # exact snapshot_policy value
    policy_digest:
    discovered_path_count:
    path_set_digest:
    complete: true
    truncated: false
    entries:
      - path:
        path_type: regular_file | directory | symlink
        raw_byte_digest: # regular_file only
        executable: # regular_file only
        symlink_target_b64: # symlink only
        entry_digest:
    expected_absences:
      - path/to/expected-absent-target
    expected_absence_count:
    expected_absence_path_set_digest:
    expected_absences_complete: true
    snapshot_digest:
phase_authorities:
  worker: {authority:, allowed_edit_scope: [], excluded_scope: []}
  author: {authority: document_edit, allowed_edit_scope: [], excluded_scope: []}
  repository_owner: {authority: bounded_edit, allowed_edit_scope: [], excluded_scope: []}
  linker: {authority: read_only, allowed_edit_scope: [], excluded_scope: []}
```

`document_root` must equal `.keystone/config.yaml` when that config exists, or the standard `00_docs`
default otherwise. The configured directory must exist inside the repository. Author allowed-edit
selectors stay at or below this independently resolved root. Worker and repository-owner allowed-edit
selectors must not equal, contain, or sit below the document root; an assignment cannot relabel a
document path as worker-owned or a code path as an Author document surface. With explicit
`document_root: .`, every write actor scope must be empty because schema v3 cannot distinguish a
root-wide document surface from code and repository-owner surfaces.

`include_paths` and exclusion selectors are normalized repository-relative paths. Every exclusion, including a
runtime-generated path, is assignment-owned and carries a reason; there is no implicit cache, build,
coverage, or IDE ignore list. Existing entries and expected absences are separate sets. A nonexistent
path can appear only in `expected_absences`, never as a discovered entry with type `absent`.

Snapshot capture independently discovers the path set before, between, and after two full entry reads,
never follows a symlink, and rejects Unicode-normalized case-fold collisions. The two entry captures
must be byte-for-byte equal. Regular files use no-follow open plus pre/post `fstat`; directories and
symlinks use no-follow identity checks. Size, mtime, ctime, inode, global entry, path-set, or type drift,
unreadable paths, budget exhaustion, or truncation trigger a bounded retry and then fail closed. The
canonical snapshot digest binds the normalized policy, complete
typed path set, raw-byte digests, executable bits, symlink targets, expected-absence set, counts, and
complete/truncated state. All later phase snapshots use the same policy digest.
An allowed selector equal to, below, or above an escaping symlink fails closed. A safe in-root symlink
whose resolved target is excluded or outside the include policy also fails closed.

The CLI hashes the assignment's raw bytes. Worker report and Coordinator review repeat the assignment ID
and digest, and the report carries the canonical Context Pack digest. Unknown fields in every
authority-bearing schema-v3 object are errors.
Each capture also binds `assignment_subject_digest`, derived from every assignment field except the
circular `assignment_phase`: schema/id/mode/purpose/authority/goal/context/injected skills/scope,
document root, snapshot policy and phase authorities. Reassigning actor authority after capture fails.

## Phase-separated actual state

The closure manifest uses `schema_version: 3` and carries this exact top-level phase shape:

```yaml
schema_version: 3
closure_stage: pre_acceptance | post_acceptance
closure_target: step | work
closure_step_ref:
worker_report:
worker_phase:
  phase_id: worker
  baseline_snapshot_digest:
  result_snapshot:
  capture_evidence: {path:, digest:}
  actor_delta:
    actor: worker
    authority:
    allowed_edit_scope: []
    excluded_scope: []
    changed_paths: []
    artifact_deltas: []
pre_acceptance_closure_phase:
  phase_id: pre_acceptance_closure
  baseline_snapshot_digest:
  result_snapshot:
  capture_evidence: {path:, digest:}
  actor_deltas: []
post_acceptance_phase: null # required object when closure_stage is post_acceptance
keystone_closure:
coordinator_review:
```

The post-acceptance object uses this exact additional shape:

```yaml
post_acceptance_phase:
  phase_id: post_acceptance
  baseline_snapshot_digest:
  result_snapshot:
  capture_evidence: {path:, digest:}
  acceptance_ref:
  acceptance_event: {path:, digest:}
  accepted_steps: []
  author_evidence_binding:
    finalization_manifest_digest:
    runner_envelope_digest:
    source_snapshot_digest:
  actor_deltas: []
```

`worker_phase.baseline_snapshot_digest` equals the assignment result digest;
`pre_acceptance_closure_phase.baseline_snapshot_digest` equals the worker result digest; and the
post-acceptance baseline equals the pre-acceptance result digest. These digest equalities are the parent
links; v3 does not add a separate `parent_phase_id`. The current repository must equal the terminal phase
result. Each adjacent snapshot delta is added, modified, deleted, or `type_replaced` and belongs to
exactly one actor delta. The union of actor changed paths must equal the independently derived phase
delta; overlap, omission, an extra path, or an inter-phase generation fails closed.

An actor delta records actor identity/role, authority, normalized scope, changed paths, and exactly one
canonical artifact delta per changed source surface. The validator derives scope and before/after values
from adjacent snapshots rather than trusting `scope_check`. Worker writes stay inside assignment edit
scope. Author writes stay on Author-owned document/metadata surfaces. A repository owner writes only its
assigned repository surface. Post-acceptance Author finalization cannot precede Main acceptance and uses
the same acceptance ref throughout.

```yaml
changed_paths:
  - path:
    change_kind: added | modified | deleted | type_replaced
    before_entry_digest: sha256:<64-lowercase-hex> | absent
    after_entry_digest: sha256:<64-lowercase-hex> | absent
```

`post_acceptance_phase` is explicit `null` for a pre-acceptance manifest and a required object for
post-acceptance closure. It then carries `phase_id: post_acceptance`, baseline/result snapshot, capture
evidence, acceptance ref/event, accepted Steps, `author_evidence_binding`, and actor deltas.
`author_evidence_binding` repeats the finalization manifest digest, Author runner-envelope digest, and
post snapshot digest. Closure completion requires a non-empty Author delta after acceptance; every
accepted-Step progress/finalization progress source must change, and every actual post-acceptance Author
change must be declared by the schema-v6 manifest and its complete Work State Runtime binding. A
pre-acceptance no-write phase may use empty actor
deltas but still supplies matching complete baseline/result snapshots and required capture evidence.

## Worker, Linker, and Author authority

The worker report is evidence for `worker_phase` only. Its changed files and artifact deltas must equal
that phase's actual delta and cannot claim subsequent document sync, repository-owner repair, Main
acceptance, or finalization writes.

Linker is source-write-free. Its classification, graph validation, or verified transaction is stored in
`keystone_closure.graph_sync`, never as a source artifact delta. If a phase contains a Linker actor
entry, both changed paths and artifact deltas are empty. Required graph sync remains bound to an exact
artifact-delta-set digest and a canonical Linker graph transaction `schema_version: 2`; the package-owned
Linker runner must pass.

For schema-v3 `graph_sync.disposition: required`, the exact graph-sync fields remain `disposition`,
`state`, `reason`, `validation_manifest_path`, `validation_manifest_digest`, `transaction_id`,
`delta_set_digest`, and `envelope_digest`. The referenced graph-validation manifest must be canonical
raw-byte schema v2 with exact required fields `schema_version`, `sources`, `transaction`, and
`application_evidence`, plus only optional `scope` and `coverage`. Its canonical transaction remains
schema v2 and `state: verified`; its input deltas must equal every phase artifact/document delta.
Standalone transaction-v2 validation is structural/current-after evidence only. Graph-validation
manifest schema v1 remains readable historical/structural evidence but cannot authorize this new v3
required success.

The manifest's `application_evidence` is exact `{path,digest}` under the external evidence root. Its
canonical aggregate schema v1 contains exactly `schema_version`, `transaction_id`,
`transaction_digest`, `repository_root_digest`, `assignment_id`, `assignment_digest`, and ordered
`receipts`; each receipt reference is exact `{path,digest}`. `transaction_digest` is the canonical JSON
SHA-256 of the exact immutable transaction projection `schema_version`, `transaction_id`, `scope_ref`,
`input_deltas`, `canonical_mutations`, and `surface_patches`; apply-time `reconstruction` is excluded.
Each applied required or optional patch has exactly one owner confirmation, applied result, and
authenticated receipt. An omitted optional has none.

After the fresh package Linker runner passes and its envelope digest matches, Coordinator reads the
same aggregate/receipts again and binds them to authoritative assignment and phase evidence. Only
`pre_acceptance_closure` and `post_acceptance` receipt phases are allowed, and a pre-acceptance receipt
cannot follow a post-acceptance receipt. For `pre_acceptance_closure`, signed phase baseline equals
`pre_acceptance_closure_phase.baseline_snapshot_digest` and signed parent evidence equals
`worker_phase.capture_evidence.digest`. For `post_acceptance`, they equal
`post_acceptance_phase.baseline_snapshot_digest` and `post_acceptance_phase.acceptance_event.digest`.
Owner `author` maps to phase actor `author`; owners `main | coordinator` map to `repository_owner`.

Coordinator reconstructs signed scope exactly as `{allowed: allowed_edit_scope, excluded:
excluded_scope}` from that actor's authoritative `assignment.phase_authorities` and requires the signed
`scope_digest` to match. It reconstructs the complete owner-apply request schema v1 with exact fields
`schema_version`, `transaction_id`, `transaction_digest`, `assignment_id`, `assignment_digest`,
`phase_id`, `phase_baseline_snapshot_digest`, `phase_parent_evidence_digest`,
`repository_root_digest`, `owner`, `scope`, `scope_digest`, `prior_receipt_digest`, and `patch`; the
signed `request_digest` must equal its canonical digest. Exactly one same-phase actor artifact delta must
name the patch's logical source, including stripping `.keystone.json` for a companion target, and bind
`baseline_digest`, `resulting_digest == expected_after_digest`, and `graph_relevant: true`.

The Linker verifier authenticates the exact receipt envelope/full patch, raw receipt chain, nonce,
evidence-root, package owner runner/runtime digests, current target equality, and externally pinned owner
HMAC. Each applied owner key must be an external, current-user-owned, owner-only, single-link regular
file with no symlink path component, outside repository/evidence roots, and at least 32 raw bytes.
Capture, acceptance, and every distinct owner-apply lane require distinct pinned key fingerprints. This
trusted-host proof establishes protected-key possession and exact signed bytes, not independent binary
execution, external clock, OS-user/organization separation, or absence of a later authorized write.

For schema-v3 `graph_sync.disposition: not_applicable`, the exact object fields are
`disposition`, `state`, `reason`, `classification_input_path`, `classification_input_digest`,
`classification_path`, `classification_digest`, `delta_set_digest`, `source_generation_digest`, and
`envelope_digest`. Both paths are normalized relative files under the disjoint evidence root and both
raw byte generations are immutable single-link regular files. Coordinator rebuilds strict classification
schema-v1 input from all phase artifact/document deltas, verifies the recorded input/output, then runs
the canonical sibling Linker `run_graph_classification.py` with `python -I` and a sanitized environment.
A pass requires fresh `not_applicable`, exact delta/source-generation/envelope digests, and recorded
output equality. The output's `exclusion_evidence` must cover every exact delta locator and point only to
its inspected source/companion indexes with `added_plain_unowned_source`; an empty delta set instead uses
`empty_delta_set` and an empty mapping. `modified | type_replaced` without baseline graph evidence remains `required`; only an
empty set or added baseline-absent plain/unowned sources can take the positive not-applicable lane.

Every post-acceptance closure records a raw-byte-digested Author finalization manifest and expected
runner envelope. The HMAC-authenticated Main acceptance event binds the exact assignment bytes,
Context Pack, policy, closure target, pre-acceptance snapshot, ref and accepted Steps. Its timestamp must
be strictly after the pre capture and before the post capture. Closure, phase, event, finalization, and
Author acceptance refs must be equal. Accepted Steps
remain inside assignment scope. New authority requires Author finalization `schema_version: 6`, a
complete package-local Work State Runtime policy/result/source-generation binding, and a
passing package-owned Author runner. `complete` or an explicitly evidenced `waived` state can close the
phase; a waiver still requires a concrete reason.

Step closure names one `closure_step_ref` inside assignment `work_context.step_refs`. A work closure
applies required work-completion gates; a step closure applies active-Step gates. Misfiled, duplicate,
out-of-assignment, invalid, unresolved, unknown, or evidence-free blocking gates fail closed. Optional
waiting gates remain non-blocking.

## Compatibility and version domains

| Domain | Current authority version | Compatibility rule |
|---|---:|---|
| Coordinator diagnostic envelope | 1 | Output/exit-code contract remains unchanged. |
| Snapshot policy | 3 | Embedded by value and digest in every assignment/phase snapshot. |
| Trusted-host phase-capture receipt / embedded snapshot | 1 / 3 | Every phase binds assignment/context, evidence parent, command digest, key fingerprint, time, and exact snapshot. |
| Main acceptance event / host receipt | 1 / 1 | A distinct pinned Main key binds the exact pre-acceptance subject before Author writes. |
| Coordinator assignment and closure manifest | 3 | Only v3 can authorize new acceptance readiness or closure completion. |
| Coordinator manifest v1/v2 | historical | Readable diagnostics only; authority decisions receive `legacy_schema_not_authoritative`. |
| Linker graph snapshot/transaction | 2 | Unchanged and independently versioned. |
| Author finalization | 5 | Required for new post-acceptance Coordinator closure. |

Do not rewrite previously accepted v2 evidence. An unfinished v1/v2 authority attempt must restart from
a new v3 assignment and complete snapshot; a complete path set and actor phase chain cannot be inferred
from the old single baseline/current diff. Diagnostic envelope, Coordinator manifest, snapshot-policy,
Linker transaction, and Author finalization versions are deliberately separate contracts.
