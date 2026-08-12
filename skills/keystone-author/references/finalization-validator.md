# Acceptance finalization compatibility validator

`scripts/run_finalization_validation.py` and `scripts/validate_finalization.py` are read-only
compatibility adapters for historical finalization manifests. They never edit files, grant Main
acceptance, update Work State, or create graph authority.

## Current completion

New work does not create a finalization manifest. Main acceptance is closed by synchronizing only the
sources whose state or meaning changed:

1. The accepted Step and owning Work/Progress when their state changed.
2. Work, round, root, and Context Map indexes only when aggregate state or active pointers changed.
3. Work State only when Work/Step status or recovery pointers changed.
4. Linker affected-scope validation only for graph-relevant metadata, relation, or multi-surface meaning.
5. Targeted tests and current diff review for the actual implementation surface.

The durable Progress record is the normal current completion evidence. External evidence roots, owner
keys, HMAC receipts, snapshot chains, and generated acceptance-event artifacts are not prerequisites.

## Historical invocation

Use the adapter only when an existing historical manifest must be inspected:

```bash
python3 <keystone-author-package>/scripts/run_finalization_validation.py \
  --root <repository-or-document-root> \
  --manifest <historical-finalization-manifest.json>
```

The runner may invoke the sibling Linker compatibility validator when the historical manifest declares
graph evidence. A project extension is additive and cannot weaken core structural checks.

Exit codes are:

- `0`: the historical input passed the checks that were available;
- `1`: deterministic structural or semantic findings were reported;
- `2`: the input or required executable could not be read or invoked.

Stdout is one diagnostic JSON envelope with `schema_version`, `status`, `diagnostics`, and `summary`.

## Compatibility boundary

Schemas v1-v6 remain readable for existing records. They are not templates for new work and cannot
create current completion, apply, or release authority. Previously completed records remain historical
facts; rerunning a validator neither reaccepts nor cancels them.

When historical trust material, a retired producer, or an external evidence root is unavailable, the
adapter should validate readable manifest structure, referenced repository sources, and current source
state where possible. It reports `historical_structure_only` and does not ask the user to recreate keys,
receipts, snapshots, or external evidence.

An unavailable historical dependency is not a current-work failure. It also must not be represented as
a full historical authority pass.

## Safety properties

- Read referenced files without following unsafe links.
- Keep package validation deterministic and standard-library-only.
- Do not mutate acceptance, work status, finalization state, graph state, or indexes.
- Do not infer that a stored `complete` label proves current source equality.
- Do not run compatibility suites unless the adapter or release surface itself changed.
