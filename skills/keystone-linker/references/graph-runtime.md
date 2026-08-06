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

The canonical node fields are `id`, `kind`, `artifact_kind`, `locator`, `lifecycle`, and `provenance`.
Markdown nodes with declared or inherited document metadata also carry `parent_id`, `declared_metadata`,
and `effective_metadata` for lifecycle, approval, governance, and source authority.
The canonical relation fields are `source`, `relation`, `target`, `evidence`, `provenance`, and
`lifecycle`. Transaction fields and all eight states follow the accepted Artifact Graph standard.
`inferred` evidence is excluded from canonical mutations. A verified transaction uses
`reconstruction: {baseline: <GraphSnapshot>, result: <GraphSnapshot>}`. Applying every canonical
mutation to `baseline` must produce exactly `result`, which must also equal source-only reconstruction.

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

Diagnostics have stable `code`, `severity`, `message`, and an optional repository `path`/`locator`.
Exit 0 means pass, 1 means mechanical findings, and 2 means invocation, execution, timeout, missing
validator/source, or malformed input/output. The runner executes core first. A project `--extension`
is additive: its diagnostics are appended and it cannot remove or suppress core diagnostics.

## Authority, cache, and verification

Source and companion metadata are authoritative. A derived cache/reverse index is optional and
non-authoritative; validation never requires it and reconstructs from source if it is absent, malformed,
or differs. Transaction state, attestation, application results, baseline digests, reconstruction,
mechanical validation, and acceptance evidence cannot be supplied by a cache. The validator checks only
mechanical facts such as shape/vocabulary/direction, duplicate or unresolved IDs, mechanically observable
locator paths, supersession cycles, lifecycle references, and verified-transaction closure.
