# Internal Reference Index Runtime

The modules under `scripts/graph_runtime/` expose a package-internal, source-read-only owner/ref
readiness API. They do not make the SQLite generation authoritative.

## Entry points

- `readiness.context_readiness(...)` selects docs scope by default and repository scope only when
  `artifact_context=True`.
- `python3 -m graph_runtime.readiness_cli --request-json ... --response-json -` is the deterministic
  package-internal host wrapper. Its request supplies the same bounded inputs; when `cache_path` is
  omitted it derives an external cache under `CODEX_HOME/cache/keystone/<repository-hash>/`.
- `scanner.ReferenceScanner` discovers a bounded path set, hashes raw bytes, reconstructs owners,
  refs, diagnostics, document-backed Work/Step dependency evaluations, and an optional typed
  projection.
- `index_store.SQLiteIndexStore` accepts a caller-provided cache path outside the repository and
  retains up to four scope/freshness-keyed immutable generations inside `BEGIN IMMEDIATE`. A loaded payload is
  accepted only when its scope, worktree, entries, and recomputed digest exactly match the requested
  source generation. A separately stored SHA-256 binds the complete canonical payload, including
  owners, refs, diagnostics, typed edges, dependency evaluations, freshness, and schema.
- `query.owner_for(...)` returns `unique`, `missing`, or `ambiguous` with all candidates; duplicate
  owners therefore cannot silently select the first source. `query.refs_to(...)` queries reverse refs.

The caller supplies the repository root, external cache path, configured document root, and optional
repository include/exclude patterns. Cache freshness is the digest of worktree identity, scope name,
sorted relative path set, and each path's raw-byte SHA-256 digest. Git HEAD, timestamps, and mtimes are
not freshness evidence.

Discovery groups each logical source and its adjacent `.keystone.json` file into one SourceUnit before
parsing. Companion-only declarations are canonical, inline-only declarations are canonical, and dual
declarations emit `metadata_surface_conflict`; the index never merges both surfaces or counts the
companion as an independent owner source. A source-unit policy change increments the disposable cache
schema so an older graph view is rebuilt from source.

## Failure and trust boundary

Missing, stale, locked, unwritable, or corrupt cache state falls back to the current source scan and
returns `cache_unavailable`; it does not block Reader orientation. Source annotations and adjacent
companion metadata remain authoritative. Parsed source text is data only: the runtime never evaluates
instructions, imports project code, runs project commands, edits source, or grants acceptance.

Structural corruption and unsupported cache schemas are recoverable because the cache is disposable:
the store acquires a non-blocking target-file write lock, keeps the securely created sibling repair
file, builds a complete SQLite generation there, and performs a same-directory atomic replace. Repair
files and SQLite sidecars are removed on failure. If the platform cannot provide the recovery lock,
recovery stays fail-soft. `BEGIN IMMEDIATE`/`BEGIN EXCLUSIVE` busy or locked caches are never replaced;
that invocation remains source-only and a later invocation retries.

Docs readiness never materializes a typed graph. Repository enrichment may request one explicitly;
only declared parser relations are projected; inferred reverse provenance is excluded. Discovery
retains relative paths and the exact bytes covered by its freshness token. Scanning iterates only that
immutable snapshot, so replacing, deleting, or redirecting a discovered path cannot combine an old
token with newer source. `CallTrace` is serialized as JSON and rejects a lane
already present in the chain, allowing Reader → Linker once while blocking Reader → Linker → Reader.
Repository discovery applies default build/vendor exclusions, per-file/file-count/byte budgets, and
warning diagnostics when a scan is truncated. The readiness CLI exposes `complete` and a `coverage`
object containing discovered/parsed/skipped counts, the discovered-path digest, and each skipped path
with its reason; callers must not infer completeness from `status: pass` alone. `key.topic.*`,
`key.role.*`, and `key.boundary.*` refs are taxonomy/navigation refs and do not require an owner.
In docs scope, repository-owned `key.skill.*`, `key.code.*`, `key.config.*`, `key.schema.*`,
`key.api.*`, and `key.test.*` refs are explicit `out_of_scope_ref` warnings until lazy repository
resolution; other semantic owner refs remain exact.

## Dependency readiness wire

The readiness CLI response uses `schema_version: 2`. Its `dependency_evaluations` array preserves a
stable gate ID, source and dependency IDs, Step/work-completion scope, observed target status and
approval, canonical result, blocking/optional meaning, origin, reason, and deterministic cycle-event
evidence. The scanner derives the Work/Step registry only from the immutable discovery generation.
Legacy-only work dependencies become non-start-blocking work-completion candidates; invalid gates do
not mutate progress, assign work, cancel work, or grant acceptance. Flat `depends_on` metadata on a
non-Work artifact remains a typed semantic relation and never creates a legacy work-completion
candidate.


## R018 bounded request and v4 response

New routine calls explicitly select `discovery_mode: targeted`. Anchors carry an `id` and optional
repository-relative `path` and raw-byte `digest`; confirmed `source_paths` and `owner_paths` provide
additional locators. Expansion follows only caller-selected `relation_types` and `follow_refs`, within
`max_depth` (default 1, maximum 8), `max_files` (default 128), and `max_total_bytes` (default 50 MiB).
No known anchor/path returns `anchor_required` rather than an implicit scan. Supplying anchor/path
inputs without a mode also selects targeted behavior.

`lookup` requires exact anchor IDs and explicit `lookup_roots`. It returns admitted matching owners,
search roots, searched file/byte counts and a raw-byte `search_digest` that also binds negative search
evidence. It does not reconstruct a typed graph. `audit` retains full selected-scope inspection for an
explicit audit, release check or scope conflict. For explicit modes, include patterns with a literal
path prefix are root-anchored and prune disjoint subtrees before traversal. Mode-less legacy calls
preserve their existing suffix-glob behavior and v2/v3 wire; they are not the routine preparation path.

All explicit modes emit schema v4 with `discovery.mode`, `coverage_kind` (`bounded` or `scope`),
`complete`, and search cost evidence. Bounded completeness does not imply repository completeness.
Unresolved owners, stale anchors and omitted paths remain diagnostic; `status: pass` alone is not a
complete result. Targeted preparation uses current source bytes without accessing the external cache,
so missing/stale/corrupt/busy cache cannot enlarge its scope. Supplied owner hints are revalidated from
source. Legacy cache reuse and recovery remain available to existing v2/v3 callers and explicit audit.

SourceUnit preserves its original adapter and carries a request-local prepared lexical result.
Scanner parse results are keyed by exact source and companion bytes. Owner/ref and requested source
views reuse those results; reconstruction checks their raw-byte binding before reuse. No prepared
parse, graph view or discovery result becomes source authority.
