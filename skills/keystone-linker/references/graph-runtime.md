# Artifact Graph runtime and validator

The Linker package reconstructs the canonical Artifact Graph directly from repository source surfaces.
It is Python 3.9 standard-library-only and does not import the Author package. It never edits source,
selects semantic relations, expands scope, or decides acceptance.

## Input

Use repeatable `--source <repository-relative-path>` values, or `--manifest <json>`. Transaction scope
validates only those sources. `--scope repository` discovers supported repository sources and adjacent
companions automatically. A repository manifest may declare `coverage: full | subset`; omitted sources
are errors for `full` and separately reported coverage-debt warnings for `subset`. A manifest has
`{"schema_version":1,"scope":"transaction|repository","coverage":"full|subset","sources":[...],"transaction":{...}}`;
`transaction` is optional. An explicit
`--transaction <json>` replaces the manifest transaction. Unsupported source surfaces use the
source-adjacent `<source>.keystone.json` companion containing `schema_version`, `source`, `nodes`, and
`relations`. Its `source` object records repository-relative `path`, `surface`, and the raw-byte
`sha256:<64-lowercase-hex>` digest, or `absent` for a new source.

For a companion-backed artifact, the logical source identity is `<source>` while the owner-applied
physical patch target is `<source>.keystone.json`. Transaction omission and observed-mutation matching
normalize the companion target to the logical identity; attestation, baseline, application, and
resulting-digest checks remain bound to the physical companion bytes. Binary source bytes are never
decoded as text. Only the companion JSON must be UTF-8.

Scanner, readiness, reconstruction, and validation use one SourceUnit selection policy. An adjacent
companion with no inline Keystone declarations is canonical even for a supported text extension. An
inline declaration without a companion is canonical. If both surfaces declare Keystone metadata, the
runtime emits `metadata_surface_conflict` and does not merge or choose one silently.
If a supported source cannot be decoded as UTF-8, a valid companion remains canonical and its baseline
stays bound to the original raw source bytes; without a companion, the runtime emits
`unsupported_encoding`. Generic source adapters mask strings, template/raw strings, heredocs, and block
comments and accept only a real line comment at the first effective token position. An unterminated
lexical region containing metadata-like text emits `ambiguous_metadata_anchor`, creates no declared
node, and blocks implicit companion precedence. If JavaScript or TypeScript source bytes contain both
`${` and a metadata-like first-token comment, the bounded adapter does not infer its lexical position:
the entire source follows this fail-closed disposition and requires companion metadata.

GraphSnapshot v1 writes the strict node core `id`, `kind`, `artifact_kind`, `locator`, `lifecycle`, and
`provenance`; its permissive reader also accepts historical `parent_id`, `declared_metadata`, and
`effective_metadata`. Canonical v2 adds those metadata fields when applicable and always adds
`lifecycle_domain: document | artifact`.
The canonical relation fields are `source`, `relation`, `target`, `evidence`, `provenance`, and
`lifecycle`; v2 also requires `lifecycle_domain: relation`. Document lifecycle is
`draft | active | superseded | archived`, artifact lifecycle is `active | deprecated | removed`, and
relation lifecycle is `active | deprecated | archived | removed`. V1→v2 migration derives the domain
from node kind and fails on incompatible lifecycle combinations instead of guessing.
Document lifecycle, approval, source authority, and effective `governed_by` inherit only across a
document-domain parent/child boundary. An output artifact declared inside a document inherits none of
those fields and defaults to artifact lifecycle `active` unless it declares another artifact-domain
state. An output-artifact heading does not become the inheritance parent of later document items.
Source-derived relation lifecycle is normalized separately from node lifecycle:
`draft | active -> active`, `superseded | archived -> archived`, and `deprecated | removed` retain
their value. A canonical active document replacement targets `superseded`; a canonical active
artifact replacement targets `deprecated | removed`.
`inferred` evidence is excluded from canonical mutations. A verified transaction uses
`reconstruction: {baseline: <GraphSnapshot>, result: <GraphSnapshot>}`. Applying every canonical
mutation to `baseline` must produce exactly `result`, which must also equal source-only reconstruction.

Planner calls default to transaction schema version 2. Every surface patch carries
`patch_format: unified_diff | full_replacement`, identical `exact_patch`/`patch_body`, UTF-8
`baseline_content` (or null when `baseline_digest: absent`), and `expected_after_digest`. Validation
recomputes the baseline digest, replays the patch without relying on current file bytes, and checks the
expected digest. Each physical `target_path` appears at most once, and an applied
`resulting_digest` must equal the planned `expected_after_digest` as well as the actual file digest.
A failed v2 transaction carries `failure_reason`; only `transient_io` admits an unchanged-input retry.
Transaction schema version 1 remains the explicit-opt-in compatibility wire for historical descriptive
patches; descriptive/executable mixed transactions are invalid.

In schema v2 every canonical mutation has at least one required owning patch, and a mutation-bearing
patch cannot be optional. Optional patches are ancillary only. Omission of an ancillary optional does
not block verification, but if it is applied it must be owner-confirmed, baseline-checked immediately
before application, and end with `resulting_digest == expected_after_digest == current source digest`.
Final verification covers every applied patch. Canonical mutation objects use the exact fields
`operation`, `entity`, `before`, `after`, `evidence`, and `direct_relation_reason`; direct input is
rechecked for relation direction, lifecycle domain, bounded direct-relation policy, and owning surface.

Authority-bearing `not_applicable` classification uses:

```sh
python3 scripts/run_graph_classification.py --root REPOSITORY --manifest classification-input.json
```

The exact schema-v1 input is:

```yaml
schema_version: 1
delta_set_digest: sha256:<canonical ordered deltas>
deltas:
  - kind: document_delta | artifact_delta
    source_surface: src/example.py
    change_kind: added | modified | deleted | type_replaced
    changed_locators:
      - path: src/example.py
        symbol: Example.run
    semantic_summary: <non-empty text>
    baseline_digest: sha256:<64-lowercase-hex> | absent
    resulting_digest: sha256:<64-lowercase-hex> | absent
    graph_relevant: true | false
source_context:
  repository_root_digest: sha256:<resolved-root-json-digest>
  coverage:
    mode: delta_set
    complete: true
    source_count: 1
    source_path_digest: sha256:<sorted-source-array-digest>
  sources: [src/example.py]
```

Every object uses its exact field set; sources and locators are canonical, sorted, and unique. Added
deltas require an absent baseline, deleted deltas require an absent result, and modified/type-replaced
deltas require both SHA-256 values. The schema-v1 input is the exact ordered delta set plus its digest and a complete root-bound delta-source
coverage object. The strict output contains `status`, `disposition`, the same delta digest, a repository
graph/source generation digest, inspected physical sources, `exclusion_evidence`, reason codes,
diagnostics, and summary. Each positive added-source exclusion records its exact delta/locator indexes,
canonical locator, `added_plain_unowned_source`, and the inspected source indexes that support it; an
empty delta set uses `empty_delta_set` with an empty exclusion array.
The runner independently inspects current source, companion, and repository graph ownership. It never
uses a caller `graph_relevant: false` as authority. A modified or type-replaced source without baseline
graph evidence is `required`; an empty set or a newly added baseline-absent plain/unowned source is the
only positive `not_applicable` lane.

## Application evidence authority

Canonical transaction schema v2 is unchanged. A standalone `--transaction`, or a transaction inside a
schema-v1 validation manifest, proves only structural/replay validity and equality with the current
after-state. It does not prove that an owning surface performed the write. New application authority
requires a canonical raw-byte graph-validation manifest schema v2. Its required exact fields are
`schema_version`, `sources`, `transaction`, and `application_evidence`; only `scope` and `coverage` are
optional. `application_evidence` is exactly `{path,digest}` and names a canonical aggregate below the
external `--evidence-root`. Schema-v1 manifests remain readable structural evidence but cannot authorize
a new Coordinator-v3 required graph-sync success.

For schema-v2 authority validation, the validator restores every applied physical surface's
pre-application bytes from the authenticated receipt's full patch `baseline_content` and
`baseline_digest`. It reconstructs a baseline GraphSnapshot through the same SourceUnit policy, requires
exact equality with transaction `reconstruction.baseline`, and applies node and relation mutation
`before` values sequentially against that snapshot. Without this receipt-bound baseline, standalone
transaction-v2 validation is structural/current-after evidence only.

The manifest transaction's `transaction_digest` is the SHA-256 of canonical JSON containing exactly
these immutable plan fields: `schema_version`, `transaction_id`, `scope_ref`, `input_deltas`,
`canonical_mutations`, and `surface_patches`. It intentionally excludes reconstruction, attestations,
apply results, state, failure reason, mechanical validation, and coverage debt.

Aggregate application evidence schema v1 contains exactly `schema_version`, `transaction_id`,
`transaction_digest`, `repository_root_digest`, `assignment_id`, `assignment_digest`, and `receipts`.
Every receipt reference contains exactly `path` and `digest`. The ordered receipt array equals the
transaction's ordered `apply_results` projection whose `result` is `applied`: each applied required or
optional patch has exactly one matching owner `confirm` and one receipt, and an omitted optional has no
applied result and no receipt. Duplicate or extra paths, patch IDs, or nonces fail. The first signed
`prior_receipt_digest` is `absent`; each later value equals the previous receipt's canonical raw-byte
digest.

Each receipt envelope contains exactly `schema_version`, `producer`, `status`, `subject`, and `receipt`.
The fixed values are producer `keystone-owned-surface-apply`, status `applied`, receipt
`schema_version: 1`, trust model `trusted-host-hmac-sha256`, and command ID
`keystone-owned-surface-apply-v1`. `subject` contains exactly `transaction_id`, `transaction_digest`,
`assignment_id`, `assignment_digest`, `phase_id`, `phase_baseline_snapshot_digest`,
`phase_parent_evidence_digest`, `repository_root_digest`, `owner`, and `scope_digest`. `receipt` contains
exactly `schema_version`, `trust_model`, `command_id`, `runner_executable_digest`, `runtime_digest`,
`evidence_root_digest`, `request_digest`, `prior_receipt_digest`, `nonce`,
`authority_key_fingerprint`, `patch_receipt`, and `mac`. `patch_receipt` is exactly
`{patch,result,resulting_digest}`; `patch` is the full exact transaction-v2 patch object and `result` is
`applied`. The receipt admits no separate caller-supplied observed-baseline, current, or alternate
resulting field; its `resulting_digest` comes from the owner runner's target reread.
For an existing target, the owner runner uses a same-directory atomic exchange, retains the displaced
live entry through receipt completion, and compares its exact bytes/type/identity with the planned
baseline. Missing OS/filesystem exchange support is the fail-closed `atomic_exchange_unavailable`
execution error, not a fallback replacement success. Absent targets keep no-clobber publication.
Rollback and receipt cleanup never unlink a public name directly. They atomically move it with
no-replace to a same-directory high-entropy quarantine, delete only a private entry matching the
recorded runner-owned identity/bytes/mode, and restore or retain mismatches as recovery evidence while
returning `rollback_failed`.

Validation is read-only. It verifies canonical single-link aggregate/receipt files with no-follow
descriptor reads, raw-byte digests, order/cardinality/chain, exact transaction and assignment/root
subjects, no-follow single-link current target equality, pinned package runner/runtime byte digests, and
the exact HMAC. Each
applied owner needs one external key path and pinned SHA-256; unexpected owner bindings fail and distinct
owners require distinct key fingerprints. Each key must be an absolute, symlink-free, single-link
regular file outside both repository and evidence roots, owned by the current OS user, have no
group/world mode bits, and contain at least 32 raw bytes. This trusted-host proof authenticates exact
bytes and protected-key possession; it does not establish independent binary execution, an external
clock, OS-user/organization separation, or absence of later authorized source changes.

Package identity is owner-specific: `author` receipts bind the current
`keystone-author/scripts/run_owned_surface_apply.py` and generated runtime, while `main | coordinator`
receipts bind the corresponding `keystone-coordinator` files.

At this layer `phase_id`, phase-parent/baseline digests, `scope_digest`, and `request_digest` are signed
and shape-checked, but their semantic source is not inferred. Coordinator v3 reconstructs the exact
request from its immutable assignment, authoritative phase actor scope, phase snapshot/evidence chain,
and transaction patch, then compares the signed values. A Linker pass alone must not substitute for
that Coordinator binding.

Core authority validation accepts these exact flags:

```sh
python3 scripts/validate_graph.py \
  --root REPOSITORY \
  [--source SOURCE ...] \
  --manifest graph-validation-v2.json \
  [--transaction transaction.json] \
  [--scope transaction|repository] \
  --evidence-root EXTERNAL_EVIDENCE_ROOT \
  [--owner-key OWNER=ABSOLUTE_KEY_PATH ...] \
  [--owner-key-sha256 OWNER=sha256:... ...]
```

If `--transaction` accompanies a schema-v2 manifest it must equal the inline transaction. Application
authority options are invalid for any manifest other than schema v2, and schema v2 always requires
`--evidence-root`. `scripts/run_graph_validation.py` accepts and forwards the same flags plus
`--validator`, `--extension`, and `--timeout-seconds`. Whenever authority is requested, it pins the
package core validator, forbids `--extension` and validator substitution, and runs isolated Python.

The Python model is converted with `transaction_wire(transaction, baseline_snapshot=...)`. It emits only
the accepted canonical transaction fields and always represents `mechanical_validation` as
`{schema_version,status,diagnostics,summary}`. A non-null reconstruction requires its baseline and emits
`{baseline,result}`; proposed and other unfinished states remain unchanged and are never promoted by
serialization. `attempt_history_wire(...)` is the separate synchronization/report envelope:

```json
{"schema_version":1,"graph_relevance":{"relevant":true,"disposition":"required","reason":"..."},"transaction":{"schema_version":1},"prior_attempts":[]}
```

`graph_relevance` and `prior_attempts` are deliberately outside the canonical transaction. For CLI
validation, pass the envelope's current `transaction` object through manifest `transaction` or
`--transaction`; report-only fields are not extra transaction fields and are not implicitly ignored.

## Commands and envelope

```sh
python3 scripts/validate_graph.py --root REPOSITORY --source 00_docs/key-context-map.md
python3 scripts/validate_graph.py --root REPOSITORY --scope repository
python3 scripts/run_graph_validation.py --root REPOSITORY --manifest graph-validation.json
python3 scripts/run_graph_classification.py --root REPOSITORY --manifest classification-input.json
bash scripts/check_graph_hook.sh --root REPOSITORY --manifest graph-validation.json
```

Output is one JSON object:

```json
{"schema_version":1,"status":"pass|fail|error","diagnostics":[],"summary":{"errors":0,"warnings":0}}
```

Repository validation adds a `coverage` object with `mode`, `complete`, `path_digest`, source lists,
and counts for discovered, parsed, omitted, declared-only, and skipped sources. `coverage: full`
promotes scan truncation, oversized files, unreadable sources, omitted discovered sources, and
declared-only manifest paths to errors. `coverage: subset` keeps those gaps explicit as warnings and
never represents skipped or omitted sources as complete. The core runner preserves this object.

Diagnostics have stable `code`, `severity`, `message`, and an optional repository `path`/`locator`.
Exit 0 means pass, 1 means mechanical findings, and 2 means invocation, execution, timeout, missing
validator/source, or malformed input/output. The runner executes core first. A project `--extension`
is additive: its diagnostics are appended and it cannot remove or suppress core diagnostics.

## Authority, cache, and verification

Source and companion metadata are authoritative. A derived cache/reverse index is optional and
non-authoritative; validation never requires it and reconstructs from source if it is absent, malformed,
or differs. One validation captures source and companion raw bytes before reconstruction and compares
the same physical paths after validation; a change produces `source_generation_changed` instead of a
mixed-generation success. Transaction state, attestation, application results, baseline digests, reconstruction,
mechanical validation, and acceptance evidence cannot be supplied by a cache. The validator checks only
mechanical facts such as shape/vocabulary/direction, duplicate or unresolved IDs, mechanically observable
locator paths, supersession cycles, lifecycle references, and verified-transaction closure.
