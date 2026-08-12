# Coordinator current-state closure validator

`scripts/validate_closure.py` is a read-only diagnostic verifier. It never edits source, assigns a
worker, creates graph mutations, performs Author synchronization, or grants Main acceptance.

## Current schema-v1 path

Schema v1 is the current no-secret closure report. It describes the approved scope, current diff or
artifact results, directly relevant verification, optional context/impact entries, and only the
Keystone synchronization categories that actually changed.

Run it with repository-local inputs:

```bash
python3 <keystone-coordinator-package>/scripts/validate_closure.py \
  --root <repository-root> \
  --manifest <current-closure-report.json>
```

The current path does not accept or require an assignment snapshot, external evidence root, capture
key, acceptance key, owner key, HMAC receipt, or package-produced acceptance event. Main reviews the
actual diff and observed verification after this diagnostic result.

The output remains:

```json
{
  "schema_version": 1,
  "status": "pass | fail | error",
  "diagnostics": [],
  "summary": {"errors": 0, "warnings": 0}
}
```

Exit `0` means the available current-state checks passed, exit `1` means deterministic findings, and
exit `2` means invocation or unreadable input prevented evaluation.

## Minimal current report

A current report should contain only material facts:

- identity and approved scope;
- current implementation artifacts or diff summary;
- verification observations;
- review stage and, after acceptance, the Main acceptance reference;
- Progress synchronization evidence;
- Work/Step, index, Context Map, Change Set, or graph synchronization entries only when applicable.

`not_applicable` categories need a reason, not a synthetic evidence artifact. A report must not list
every possible category merely to say it was unaffected.

Pre-acceptance validation can establish an acceptance candidate but cannot grant acceptance.
Post-acceptance validation requires the Main acceptance reference and durable Progress synchronization.

## Historical schema-v2/v3 path

Schemas v2 and v3 remain read-only compatibility formats for prior snapshot, phase-chain,
application-evidence, and acceptance-event records. Their validators may inspect structural fields and
repository-local references but cannot authorize new current closure.

If a historical producer, HMAC key, owner key, or external evidence root is unavailable, do not execute
the retired producer and do not request access merely to satisfy the old format. Report
`historical_structure_only` when the remaining manifest and repository sources can be read. This is a
compatibility diagnostic, not a full trust validation and not a current-work failure.

## Current authority

Current closure authority is the combination of:

1. User-approved scope and current repository bytes.
2. Scope-safe current diff and owner baseline/result checks.
3. Directly relevant tests, static checks, and affected graph reconstruction.
4. Durable Work/Progress and Work State where status changed.
5. Main's post-edit review and acceptance.

No generated closure artifact can substitute for these observations.

## Safety properties

- Standard-library-only and deterministic diagnostics.
- No repository writes.
- No raw routing-payload dump in ordinary output.
- Missing optional cache falls back to current source.
- Historical adapters fail soft without claiming authority.
- Unknown or contradictory current scope facts fail honestly.
