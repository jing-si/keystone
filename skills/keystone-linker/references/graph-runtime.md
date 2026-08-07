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

GraphSnapshot v1 writes the strict node core `id`, `kind`, `artifact_kind`, `locator`, `lifecycle`, and
`provenance`; its permissive reader also accepts historical `parent_id`, `declared_metadata`, and
`effective_metadata`. Canonical v2 adds those metadata fields when applicable and always adds
`lifecycle_domain: document | artifact`.
The canonical relation fields are `source`, `relation`, `target`, `evidence`, `provenance`, and
`lifecycle`; v2 also requires `lifecycle_domain: relation`. Document lifecycle is
`draft | active | superseded | archived`, artifact lifecycle is `active | deprecated | removed`, and
relation lifecycle is `active | deprecated | archived | removed`. V1→v2 migration derives the domain
from node kind and fails on incompatible lifecycle combinations instead of guessing.
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
