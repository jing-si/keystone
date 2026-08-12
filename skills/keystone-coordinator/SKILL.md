---
name: keystone-coordinator
description: "Provide bounded Keystone context, execute directly when no external coding skill is selected, or orchestrate an external-skill worker when one is selected. After implementation, supervise document, metadata, graph, verification, and finalization closure with Linker and Author while Main retains acceptance. Direct invocation grants permission only for the current scope."
---

<!-- keystone: id=key.skill.coordinator kind=output_artifact artifact_kind=skill_source -->
<!-- keystone: produced_from=key.work.skill-runtime-implementation.order -->
<!-- keystone: governed_by=key.standard.project key.standard.skill.coordinator -->
<!-- keystone: derived_from=key.work.decisions.dec-works-020 -->

# keystone-coordinator

## Purpose

Coordinate one bounded Keystone implementation from relevant source context through verified current
state. Execute directly when no external implementation skill is selected; otherwise give one worker a
minimal Context Pack and supervise the result. Main retains scope control, destructive-action approval,
result acceptance, and user communication.

This installed package is the complete Coordinator runtime contract. Project documents define project
meaning; they do not need to duplicate this package contract.

## When To Use

Use Coordinator when implementation is approved and Keystone context must remain connected to code,
tests, or generated artifacts. Direct invocation authorizes only the stated scope.

Do not use Coordinator for read-only orientation, unresolved product or policy decisions, standalone
document authoring, repository initialization, or broad release work that the user did not request.

## Inputs

Use the smallest reliable input set:

1. User-approved scope, goal, exclusions, and relevant project conventions.
2. Applicable standards, accepted decisions, active Work/Progress context, and current workspace state.
3. Exact files or selectors likely to change and known existing-change risk.
4. Verification expected for the changed surface.
5. Linker context only when graph relevance, cross-surface impact, stale/gap meaning, or reusable test
   candidates matter.
6. Active-Step and Work-completion gates that apply to the chosen execution unit.
7. A Main context checkpoint containing user intent, accepted decisions, current Work identity,
   exclusions, and existing-change preservation.

A Work Order, Change Set, external evidence root, HMAC key, assignment snapshot, acceptance-event file,
or raw internal routing payload is not a prerequisite for ordinary implementation.

## Operating Modes

### Direct execution

Use direct execution when no external implementation skill has been selected. Read the bounded context,
edit only approved non-document surfaces, run proportional checks, and return the actual diff and
verification result to Main.

### Worker orchestration

Use a worker only when an external coding skill is selected or delegation materially helps the approved
scope. Give it one Context Pack containing goal, authority, allowed and excluded scope, constraints,
current file state, acceptance conditions, and verification commands. One worker owns each writable
surface. Linker remains read-only and Author owns document-source edits.

Delegation is optional. Do not create worker reports, assignment manifests, or evidence artifacts when
direct execution is sufficient.

## Context Pack and Result Contract

Before direct or delegated execution, build one bounded Context Pack from the Main checkpoint, selected
Work/Step, applicable standards, accepted decisions, allowed and excluded surfaces, completion criteria,
stop conditions, current bytes, and verification. Include Reader or Linker context only when actually
used. Do not dump the whole Keystone corpus or ask the implementer to reinterpret the Work Order.

For orchestration, give one implementation owner each writable surface and include the selected external
skill's required workflow without letting it expand scope or create unsupervised subagents. Normalize
direct and delegated results to the same concise evidence: changed files, meaningful behavior, scope
check, verification, source conflicts, document/graph synchronization needs, and residual risk.

Treat worker `DONE`, review-clean, commit-ready, or branch-ready as report evidence only. They never
change Work status, approval, finalization, or Main acceptance by themselves.

## Workflow

1. Confirm implementation approval, initialization readiness, project conventions, and current diff.
2. Resolve the smallest relevant Keystone source set and implementation surface. For Work State schema
   v3, keep global Round identity on the parent and use `round_hierarchy`, `active_child_rounds`, and
   child Work/Step refs for the actual execution owner.
3. Ask Linker for impact context only when graph or cross-surface reasoning is relevant.
4. Evaluate Step gates separately from Work-completion gates, then choose direct execution or one
   bounded worker assignment.
5. Build the Context Pack and apply the smallest effective change without overwriting unrelated work.
6. Re-read the changed surfaces, inspect the current diff, and normalize the execution result.
7. Run verification selected by the changed surface and classify failures honestly.
8. Ask Linker to reconstruct and validate affected graph scope only when graph-relevant sources changed.
9. Ask Author to update only durable Work/Progress/index/context sources whose state or meaning changed.
10. Return evidence and residual risk to Main for acceptance, including the scope check and
    synchronization result.

## Dependency and Persistence Boundary

- Do not start an implementation assignment whose required Step gate is `waiting`. An approved
  investigation or verification may still proceed when its own scope is not blocked.
- Route `unresolvable | invalid | unknown` dependency results to Main, Author repair, or Linker evidence.
  Never mutate status, cancel Work, or grant acceptance from dependency evaluation alone.
- Keep Context Packs, assignments, reports, and reviewer briefs as runtime output by default. Persist
  one only when the user requests it, a rerun needs durable handoff, or a real audit requirement exists.
- Invalidate affected pre-write Reader/Linker context after a source write; review current source rather
  than a stale cache or pre-edit projection.

## Current-State Authority

Current implementation and closure authority comes from:

1. The user-approved scope and current repository bytes.
2. The pre-edit/current diff and owner baseline/result checks for each changed surface.
3. Targeted tests, static checks, and affected-scope source reconstruction.
4. Durable Progress and Work State only where status or active pointers changed.
5. Main's post-edit review and acceptance.

Current closure does not require a cryptographic receipt, external evidence directory, full repository
snapshot chain, package-produced acceptance event, or finalization manifest. Do not request access to an
external folder merely to create verification evidence.

## Closure Review

Before returning an acceptance candidate, confirm:

- changed files are inside the approved scope;
- excluded and user-owned unrelated changes remain untouched;
- the current diff implements the accepted requirement;
- directly related verification passed, or failures and environmental limits are explicit;
- graph reconstruction ran when metadata, relations, or canonical multi-surface meaning changed;
- Progress records only actual work, evidence, residual risk, and the resume point;
- no generated artifact was created solely to prove the workflow ran.

The bundled `scripts/validate_closure.py` schema-v1 path is the current no-secret diagnostic contract.
It checks a caller-supplied current-state report and never edits sources or grants acceptance. Schema-v2
and schema-v3 inputs are historical compatibility formats. Missing historical producers, keys, or
external evidence roots must produce `historical_structure_only` diagnostics where structural reading
is possible; they must not trigger a producer run or permission request.

## Ownership and Apply

- Main or the direct Coordinator owns approved code/config/test/skill-source edits.
- Author owns Keystone document-source edits.
- Linker plans graph-relevant canonical mutations and validates reconstructed current state; it never
  writes source surfaces.
- Before applying a patch, compare the expected baseline with current bytes. On mismatch, stop with
  `stale_baseline` and replan instead of overwriting.
- After apply, re-read the target and compare the resulting digest or semantic state with the plan.
- A concise current diff and verification result replace current HMAC owner receipts.

Historical owner-apply/application-evidence adapters may parse prior records for migration or audit.
They are read-only compatibility surfaces and cannot create current apply, closure, or release authority.

## Verification Tiers

1. **Default Work**: changed-surface tests or checks, current diff/scope review, and directly relevant
   document readiness.
2. **Escalated**: affected package suites, Linker reconstruction, Work State, repository readiness, or
   installer staging when those surfaces changed.
3. **Release**: the canonical release plan only when release/publish/install verification is explicitly
   requested.

The release plan is: preflight, package tests, shared skills tests, compileall, document and repository
readiness, Work State, repository graph validation, installer staging/parity/rollback, postflight.
Historical finalization suites remain package compatibility tests; agent-eval evidence, Coordinator
snapshot/HMAC phases, and dedicated finalization manifests are not independent release gates.

## Failure Handling

Classify a failure as:

- `implementation_failure`: changed behavior is wrong;
- `verification_failure`: a relevant deterministic check found a defect;
- `environment_failure`: required tooling or access is unavailable;
- `stale_baseline`: target bytes changed after planning;
- `historical_structure_only`: a legacy record can be inspected structurally but its retired trust
  material or producer is unavailable;
- `scope_blocked`: completion requires an unapproved surface.
- `work_order_restructure`: the plan would require a third Round depth and must return
  `NEEDS_SCOPE_CHANGE` for Author/Main plan simplification instead of creating deeper hierarchy.

Fail soft for missing optional caches and historical trust material. Never convert unavailable evidence
into a passing result, but do not treat it as a requirement for current work.

## Output

Return a concise result containing:

1. Goal and scope executed.
2. Files changed and meaningful behavior change.
3. Verification commands and observed outcomes.
4. Graph/Work/Progress synchronization actually performed.
5. Residual risks, blockers, and Main's next action.

Do not dump raw worker, Linker, Author, closure, or graph payloads by default.

## Stop Conditions

Stop when approval, scope, authority, convention, current file state, or a material product decision is
unresolved; when a user-owned change would be overwritten; or when the required next edit is outside the
approved scope. Also stop before creating a child below a child: report that the plan has become too
complex and request `work_order_restructure`. Ask Main for the smallest missing authority or decision.

## Verification

Verify that:

1. Direct execution works without worker assignment artifacts.
2. Current closure works without HMAC keys, external evidence roots, snapshots, or acceptance events.
3. Delegated edits remain inside one explicit ownership lane.
4. A stale baseline prevents overwrite and a successful apply is checked against current state.
5. Graph and document synchronization run only when their source meaning changed.
6. Historical schema-v2/v3 inputs cannot authorize current completion.
7. Verification tier follows the changed surface and release gates run only on explicit release work.
8. Parent/child recovery preserves parent-only global status and acceptance, child-local execution, and
   the two-level maximum without inventing a deeper Round.
