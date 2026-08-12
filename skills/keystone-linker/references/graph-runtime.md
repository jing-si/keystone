# Artifact Graph runtime and validator

The Linker package reconstructs the canonical Artifact Graph from current repository sources. It is
Python 3.9 standard-library-only, read-only, and independent of Author. It never edits a source surface,
selects project meaning, expands scope, or grants acceptance.

## Current source path

Use repeatable `--source` inputs for affected scope or `--scope repository` for an explicit repository
check. A schema-v1 manifest or direct `--transaction` supplies an optional current transaction.

```sh
python3 scripts/validate_graph.py --root REPOSITORY --source 00_docs/key-context-map.md
python3 scripts/validate_graph.py --root REPOSITORY --manifest graph-validation.json
python3 scripts/validate_graph.py --root REPOSITORY --transaction transaction.json
python3 scripts/validate_graph.py --root REPOSITORY --scope repository
```

Current validation reconstructs source, validates metadata/relations/lifecycle, replays planned
patches, compares the current result with expected results, and checks canonical mutations. It does not
require an external evidence root, owner key, HMAC receipt, assignment snapshot, or package identity
receipt.

## Sources and companions

Supported text sources use first-effective-token Keystone declarations. Unsupported or binary sources
use `<source>.keystone.json` companion metadata bound to the raw source digest. Inline and companion
authority cannot both be selected; emit `metadata_surface_conflict` instead of merging. An undecodable
source without a valid companion emits `unsupported_encoding`.

GraphSnapshot v2 separates document, artifact, and relation lifecycle domains. Typed relations retain
their own provenance and lifecycle. Document authority inheritance crosses only document-domain parent
boundaries; output artifacts do not inherit document approval or governance automatically.

## Current transaction

Canonical transaction schema v2 contains exact input deltas, canonical mutations, owner-specific
surface patches, reconstruction when mutations exist, apply results, mechanical validation, and state.
Each patch binds its target, baseline content/digest, exact patch, and expected-after digest.

Current owners:

1. Recheck target bytes immediately before apply.
2. Return `stale_baseline` without writing on mismatch.
3. Apply only their owned surface.
4. Re-read and report the resulting digest or semantic state.

Linker then reconstructs affected current source and verifies the result. Required mutation patches are
never optional. Applied ancillary patches receive the same current-result checks.

## Graph relevance

Graph synchronization is required for stable-ID, locator, relation, lifecycle, provenance, metadata
authority, generated/source ownership, or canonical multi-surface meaning changes. A bounded classifier
may return `not_applicable` for an empty delta set or a clearly plain new source without graph ownership.
It must not trust a caller's `graph_relevant: false` without inspecting current source.

## Historical application evidence

Schema-v2 graph-validation manifests with `application_evidence` are historical compatibility inputs.
Their receipt/HMAC, owner-key, package-identity, evidence-root, and phase fields can be inspected when the
original inputs remain available.

When a historical evidence root, key, receipt, or retired producer is missing, validate the readable
manifest, transaction, repository sources, replay, reconstruction, and current result. Emit
`historical_structure_only` and skip unavailable trust-material validation. Do not ask the user to
recreate external evidence or run a retired producer. A structural result neither proves full historical
application authority nor authorizes current apply, closure, or release.

Application authority flags remain invalid for ordinary schema-v1/current validation.

## Envelope and exit codes

The core and package runner emit one JSON envelope with `schema_version`, `status`, `diagnostics`, and
`summary`.

- exit `0`: available checks passed;
- exit `1`: deterministic graph findings;
- exit `2`: invocation or unreadable input prevented evaluation.

An additive extension cannot weaken core checks. When no cache is available, reconstruct from raw source
without requesting access to another folder.

## Safety properties

- Read-only validation and deterministic output.
- Stable ID/ref and lifecycle diagnostics remain source-derived.
- Current source equality, not a stored state label, controls current success.
- Historical compatibility never becomes current authority.
- Repository-wide validation runs only when its wider cost is justified or explicitly requested.
