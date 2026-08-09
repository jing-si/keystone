# R010/S05 Actual Agent Behavior Evaluation Design

Date: 2026-08-09

Status: user-approved design, pending implementation plan

Authority: R010/S05 Work Order remains canonical; this document records the approved implementation
design for the Superpowers workflow and does not replace Keystone source authority.

## Goal

Build a reproducible, fail-closed evaluation lifecycle that runs the twelve R010 agent-behavior
scenarios through actual skill/model invocations, captures tool and transcript evidence plus complete
isolated fixture snapshots, obtains a separately executed reviewer disposition, and emits externally
stored signed evidence that the validator and release gate can independently verify.

The minimum live matrix is exactly:

- two declared model/reasoning settings;
- two repeats for each setting;
- twelve canonical scenarios;
- forty-eight unique evaluator cells in total.

The implementation and deterministic local tests may proceed without model calls. Live evaluator and
reviewer calls require a separate user authorization after their exact model settings, maximum call
count, time limit, and cost/token budget are known.

## Non-goals

- Do not implement R010/S04 work-state, R010/S06 whole-flow, or R010/S07 release-closure behavior.
- Do not add a provider SDK or make one provider a repository dependency.
- Do not persist provider credentials, reviewer credentials, raw secrets, or live evidence in the
  repository.
- Do not treat fixture-adapter output, hand-built JSON, or a successful local unit test as actual
  behavior evidence.
- Do not claim organizational reviewer independence from HMAC verification alone.
- Do not change the twelve scenario meanings or weaken their scope and authority invariants.

## Accepted Design Decisions

### Provider-neutral execution boundary

The runner owns a strict command-adapter protocol. It launches an adapter with an argument vector,
never a shell command string, in an isolated fixture directory and with a small allowlisted
environment. The adapter reads one canonical JSON request and returns JSONL events followed by one
canonical result envelope.

The repository will include the minimum Codex CLI adapter needed for the approved live execution.
Codex remains a runtime choice behind the protocol, not a Python dependency or the schema authority.
The exact Codex model and reasoning values are external run configuration and are bound into the
evidence before execution.

### Separation of evaluation and review

The evaluator runner does not produce its own passing reviewer disposition and never reads or writes
the reviewer key. It sends redacted, digest-bound review requests to a separately launched reviewer
adapter. Reviewer configuration supplies the hidden variation and external trust material without
placing either in the evaluator request.

The default live review layout is four bounded batches, one for each setting/repeat pair. Each batch
contains twelve cells and a seeded negative control. A batch is valid only when the reviewer emits one
disposition for every cell, rejects the negative control, proves the hidden variation was used without
returning its contents, and returns a canonical signed response. Batch size is fixed before the live
run and cannot change during resume. After all four batches pass, the reviewer adapter performs one
non-model final signing operation over the assembled suite manifest. The default live plan therefore
contains forty-eight evaluator model calls, four reviewer model calls, and one local cryptographic
signing operation, plus an explicitly authorized capability probe before the matrix if needed.

### External evidence and trust material

All live transcripts, snapshots, attachments, review responses, redaction manifests, and signed result
manifests live under a caller-selected evidence root that is disjoint from the repository. Reviewer
key material lives outside both roots, is current-user-owned, single-link, owner-only, and at least 32
bytes. The final HMAC covers the canonical result manifest without its attestation field.

HMAC proves exact result bytes and possession of the pinned key. The operational record must separately
state who controlled evaluator and reviewer configuration and whether that separation is sufficient
for Main acceptance.

## Architecture

The implementation follows a functional-core/imperative-shell split.

### Scenario and matrix specification

`scripts/agent_eval_scenarios.json` moves to schema version 2. It contains:

- the unchanged ordered twelve scenario definitions;
- two or more setting identifiers with bounded public configuration;
- two or more repeat identifiers;
- suite and per-cell attempt, timeout, token, cost, and wall-clock limits;
- allowed output paths and snapshot exclusions with reasons;
- redaction rule identifiers, never secret values;
- the adapter protocol version and reviewer batch policy.

The specification declares the exact Cartesian product. The validator derives expected coordinates
from the specification rather than trusting a results count.

### Evaluation core

A standard-library-only core module owns immutable coordinate, budget, identity, attachment, snapshot,
redaction, and diagnostic values plus canonical JSON and digest functions. It validates data before it
reaches subprocess or filesystem code. Public functions have typed inputs and deterministic output.

### Runner shell

`scripts/run_agent_evals.py` performs the lifecycle:

1. Parse and validate the specification and live run configuration.
2. Confirm that the selected adapter can expose every required prompt/tool/provider/usage field; stop
   before the matrix when a required capability is unavailable.
3. Freeze the complete execution plan and its digest before the first invocation.
4. Create one fresh temporary fixture, cache, and invocation directory per matrix cell.
5. Materialize the canonical scenario fixture and capture a complete before snapshot.
6. Invoke the selected command adapter within cell and suite budgets.
7. Capture JSONL transcript/tool events, provider assertions, usage, and termination status.
8. Capture the complete after snapshot and enforce the allowed-output policy.
9. Redact all persistent attachments and verify that configured sensitive probes no longer occur.
10. Write a digest-bound unsigned cell record through an atomic temporary-file replacement.
11. Build four redacted reviewer requests and invoke the separately configured reviewer adapter.
12. Verify reviewer coverage, hidden-variation commitment, and negative-control rejection.
13. Assemble the unsigned final result manifest and send its canonical digest to the reviewer adapter
    for one non-model final HMAC operation.
14. Re-run the standalone validator against the completed external evidence before returning success.

Resume is coordinate-based. A cell may be reused only when its frozen-plan digest, subject, adapter,
fixture, prompt/tool schema, snapshots, attachment digests, budget record, and reviewer batch identity
all match. Otherwise the cell is rerun; partially written or unsigned data never counts as complete.

### Codex CLI adapter

The Codex adapter converts the neutral request to a non-interactive, ephemeral Codex CLI invocation.
It uses an isolated scenario working directory, the requested model/reasoning configuration, a bounded
sandbox, JSON event output, and no approval bypass. It records:

- adapter ID, protocol version, executable bytes/version, configuration digest, and invocation ID;
- complete system, developer, user, and tool-schema digests;
- requested model claim separately from the provider-asserted model identity;
- ordered assistant/tool events and the final response;
- process exit, timeout, attempts, wall-clock duration, and provider usage/cost fields.

Missing provider identity, missing tool events where required, unavailable usage/cost accounting,
noncanonical output, timeout, or partial process output makes the cell fail. The adapter does not
translate these states into a passing response. A live preflight also rejects the adapter when Codex
cannot expose all prompt layers and the complete tool schema required by the S05 contract. Opaque
built-in prompts or tools are bound to executable/config identity for diagnostics but are not falsely
reported as complete prompt or tool-schema evidence.

The frozen run configuration supplies a model-specific pricing table and its digest. Cost is computed
from provider-reported usage against those immutable rates; a missing usage field, missing rate, or
unknown model makes the affected cell and suite accounting fail. Evaluator and reviewer usage both
count toward the suite budget.

### Fixture and snapshot layer

Each cell uses a new temporary root and deterministic fixture materialization. The snapshot contains
every discovered relative path and supported path type, raw-byte or symlink-target digest, executable
bit, complete path-set digest, snapshot-policy digest, entry count, and completeness flag. Discovery
drift, unsupported entries, path collisions, truncation, or an exceeded entry budget fails the cell.

The after snapshot is compared with the cell's allowed-output paths. A scenario may intentionally
exercise bounded writes, but an unlisted change is always an authority violation. No fixture, cache,
or invocation context is shared between cells.

### Transcript capture and redaction

Transcript schema version 2 stores ordered event objects for user, assistant, and tool activity. Tool
events retain tool name, canonical argument digest, result-status digest, and timing while redacted
content is stored only where permitted. Prompt and tool schemas are stored as redacted attachments and
bound by digest.

Redaction occurs before any persistent evidence or signing operation. The redaction manifest records
rule IDs, source and redacted digests, match counts, output attachment paths, and a manifest digest.
Raw secret values and reversible mappings are never written. Tests use explicit sensitive probes to
prove that the persisted tree contains no original bytes.

### Reviewer adapter

The reviewer adapter receives only the redacted batch request. It independently checks expected
outcomes, required checks, authority and scope boundaries, transcript/tool consistency, and snapshot
deltas. Hidden variation is loaded from reviewer-owned configuration and is represented in the result
only by its ID and digest.

The reviewer response has a disposition for each coordinate, one negative-control disposition, reviewer
identity, reviewer invocation identity, timestamps, and a batch attestation. Evaluator and reviewer
identity or invocation reuse is invalid. Any pass on the seeded negative control fails the entire suite.
After the four batches pass, a separate reviewer signing operation checks their digests and signs the
final suite manifest without invoking the model again.

### Results validator

`scripts/validate_agent_evals.py` becomes the independent schema-v2 validator. It reconstructs and
checks:

- exact setting/repeat/scenario Cartesian coverage and tuple uniqueness;
- specification, subject HEAD/package tree, frozen-plan, fixture, adapter, prompt, tool, and invocation
  bindings;
- before/after snapshot completeness and allowed-output closure;
- transcript, tool event, provider identity, and required-check integrity;
- per-cell and suite budget accounting;
- redaction-before-persistence/signing evidence;
- reviewer separation, complete batch coverage, hidden-variation commitment, and negative-control
  rejection;
- attachment path safety, raw-byte digests, freshness, and final HMAC.

Schema-v1 input is recognized only to emit a stable `legacy_schema_not_admissible` diagnostic. It
cannot satisfy S05 completion or a new RC run.

### Release-gate consumption

The release gate continues to call the standalone validator through the isolated Python launcher. Its
command shape is migrated to schema v2 and includes the selected result, external evidence root,
reviewer identity/key fingerprint, and bounded freshness/run-duration policy. The release gate does
not invoke models; it only consumes already generated current-subject evidence.

## Result Wire

The schema-v2 result manifest has exact top-level fields for:

- schema and suite identity;
- specification and frozen execution-plan references;
- current repository HEAD and package-tree subject;
- matrix settings, repeats, and budgets;
- forty-eight ordered cell records;
- four ordered reviewer-batch records;
- redaction summary;
- suite start/completion timestamps and accounting;
- final reviewer attestation.

Each cell is keyed by the tuple `(setting_id, repeat_id, scenario_id)` and binds its own adapter,
fixture, prompts, tool schema, request/provider identities, before/after snapshots, transcript,
expected-check evidence, budget result, and reviewer-batch ID. Arrays use specification order; maps and
digests use canonical JSON with sorted keys and compact separators.

## Failure Model

The runner and validator fail closed for:

- incomplete, duplicate, reordered, or extra matrix coordinates;
- adapter protocol mismatch, malformed JSONL, nonzero exit, timeout, or partial invocation;
- missing or conflicting request/provider/executable/config identity;
- snapshot drift, truncation, cross-cell reuse, or a change outside allowed paths;
- sensitive bytes surviving redaction or any signing before redaction completion;
- missing/unknown token or cost accounting and any fixed budget overrun;
- reviewer/evaluator identity reuse, missing cell disposition, leaked hidden variation, or accepted
  negative control;
- stale, forged, self-reviewed, symlinked, hard-linked, or repository-internal evidence;
- subject, attachment, execution-plan, or HMAC digest mismatch.

Expected external failures produce stable diagnostics and nonzero exit codes. Internal invariant
violations raise explicit exceptions and cannot create an evidence manifest marked pass.

## Verification Strategy

Implementation follows test-first slices:

1. Characterize the existing schema-v1 rejection/security behavior that must remain fail-closed.
2. Add matrix-spec tests for exact 2 × 2 × 12 coverage, order, uniqueness, and legacy rejection.
3. Add command-adapter protocol tests for valid JSONL, missing tools, timeout, partial output, identity,
   and budget accounting.
4. Add isolated fixture and snapshot tests for complete capture, cross-cell contamination, path escape,
   drift, and allowed-output enforcement.
5. Add byte-level redaction tests proving no sensitive probe survives in persisted evidence.
6. Add reviewer tests for identity separation, hidden-variation non-disclosure, complete dispositions,
   seeded-control rejection, and HMAC verification.
7. Add an end-to-end deterministic fixture-adapter run that produces schema-v2 evidence but is marked
   non-live and therefore inadmissible for S05 completion.
8. Add release-gate tests proving schema-v2 current evidence passes and schema-v1, stale, incomplete,
   forged, or self-reviewed evidence fails.
9. Run focused suites, package suites, cross-skill contracts, repository readiness/full graph,
   external-cache compileall, and `git diff --check`.
10. After separate user authorization, execute the frozen live Codex/reviewer matrix and validate its
    external evidence against the exact implementation subject.

## Scope and Safety

Likely implementation surfaces are limited to the S05 runner/core/adapters, scenario specification,
validator, release-gate consumer, focused/cross-skill tests, the relevant README/runtime contract, and
the S05 Keystone Progress/closure documents required after implementation. Existing S03/S04 changes
must be preserved and are not implementation cleanup targets.

No browser verification, publishing, provider dependency installation, credential creation in the
repository, merge, or push is part of this design. Live model execution, its external cost, and the
operational sufficiency of reviewer separation remain explicit Main/user gates.

## Acceptance Boundary

Local implementation and tests can make the code an acceptance candidate, but they cannot complete
R010/S05. S05 becomes Main-acceptance-ready only after the actual forty-eight-cell matrix, independent
review batches, negative control, validator/release consumption, affected package/cross-skill tests,
Keystone document/metadata/graph synchronization, and residual-risk review all pass for one exact
subject. Main acceptance remains distinct from Author finalization.
