# Internal Reference Index Runtime

The modules under `scripts/graph_runtime/` expose a package-internal, source-read-only owner/ref
readiness API. They are not a user-facing command and do not make the SQLite generation authoritative.

## Entry points

- `readiness.context_readiness(...)` selects docs scope by default and repository scope only when
  `artifact_context=True`.
- `scanner.ReferenceScanner` discovers a bounded path set, hashes raw bytes, reconstructs owners,
  refs, diagnostics, and an optional typed projection.
- `index_store.SQLiteIndexStore` accepts a caller-provided cache path outside the repository and
  replaces one immutable generation inside `BEGIN IMMEDIATE`.
- `query.owner_for(...)` and `query.refs_to(...)` query immutable results without touching source.

The caller supplies the repository root, external cache path, configured document root, and optional
repository include/exclude patterns. Cache freshness is the digest of worktree identity, scope name,
sorted relative path set, and each path's raw-byte SHA-256 digest. Git HEAD, timestamps, and mtimes are
not freshness evidence.

## Failure and trust boundary

Missing, stale, locked, unwritable, or corrupt cache state falls back to the current source scan and
returns `cache_unavailable`; it does not block Reader orientation. Source annotations and adjacent
companion metadata remain authoritative. Parsed source text is data only: the runtime never evaluates
instructions, imports project code, runs project commands, edits source, or grants acceptance.

Docs readiness never materializes a typed graph. Repository enrichment may request one explicitly;
only declared parser relations are projected. `CallTrace` is serialized as JSON and rejects a lane
already present in the chain, allowing Reader → Linker once while blocking Reader → Linker → Reader.
