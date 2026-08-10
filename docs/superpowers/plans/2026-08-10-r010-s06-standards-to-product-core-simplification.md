# R010/S06 Standards-to-Product Core Simplification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Keystone's current graph apply, Coordinator closure, and release path work from repository state and ordinary verification without HMAC keys, reviewer evidence, or external evidence roots, while preserving Artifact Graph, Work State, and bounded historical readers.

**Architecture:** Current authority comes from an immutable assignment boundary, immediate raw-byte baseline checks, current source reconstruction, canonical transaction equality, durable Progress, Work State, and repository graph validation. SHA-256 is used only for byte/generation equality. Closure v1-v3, finalization v1-v6, graph-validation v2, and application-evidence wires remain structural historical inputs and cannot create current success.

**Tech Stack:** Python 3.9+, standard-library `unittest`, Bash installer/release launchers, Markdown, JSON.

## Global Constraints

- Implement only the accepted R010/S06 Change Set and the approved design at `docs/superpowers/specs/2026-08-10-r010-s06-standards-to-product-core-simplification-design.md`.
- Do not modify `00_docs/works/r011-work-model-evolution/**`, historical R010 evidence JSON, the frozen S05 branch, `${CODEX_HOME:-~/.codex}/skills`, package version, dependencies, or unrelated formatting.
- Preserve SourceUnit, metadata, scanning, lifecycle, impact, classification, planning, reconciliation, transaction/wire validation, Work State, and graph validation behavior.
- Follow RED -> GREEN -> refactor for every behavior change. Record the exact failing assertion before implementation and rerun the same command after implementation.
- Delete a producer only after current consumers are removed and an explicit `rg` consumer check is clean. Historical fixture strings are allowed only in historical adapters/tests.
- Keep current and historical meanings explicit: historical structural validation must never return or imply current apply, completion, acceptance, or release authority.
- Work in an isolated implementation worktree created from the committed plan. Stage and commit only each task's owned paths. Do not stage the dirty R010 documentation or untracked R011 files in the primary worktree.
- Record the worktree starting commit once as `S06_IMPLEMENTATION_BASE` in the Coordinator Context Pack and use that exact value for every cumulative scope check.
- Do not run a model, reviewer, network, credential, external evidence-root, browser, or Playwright workflow.

---

### Task 1: Align package contracts with the accepted no-secret current model

**Files:**

- Modify: `skills/keystone-author/SKILL.md`
- Modify: `skills/keystone-author/references/finalization-validator.md`
- Modify: `skills/keystone-coordinator/SKILL.md`
- Modify: `skills/keystone-coordinator/references/closure-validator.md`
- Modify: `skills/keystone-linker/SKILL.md`
- Modify: `skills/keystone-linker/references/graph-runtime.md`
- Modify: `README.md`
- Modify: `skills/tests/test_s03_runtime_contracts.py`
- Modify: `skills/tests/test_coordinator_keystone_closure_contracts.py`

- [ ] **Step 1: Add failing contract assertions**

Replace assertions that require schema-v6 finalization, snapshot/acceptance producers, HMAC receipts, or owner-apply runners with assertions for the current contract:

```python
def test_current_contract_is_repository_derived_and_no_secret(self):
    author = read("skills/keystone-author/SKILL.md")
    coordinator = read("skills/keystone-coordinator/SKILL.md")
    linker = read("skills/keystone-linker/SKILL.md")
    combined = "\n".join((author, coordinator, linker))
    for phrase in (
        "raw-byte baseline",
        "stale_baseline",
        "current source reconstruction",
        "durable Progress",
        "Work State",
        "historical structural",
    ):
        self.assertIn(phrase, combined)
    for phrase in (
        "trusted-host-hmac-sha256",
        "capture_assignment_snapshot.py",
        "record_acceptance_event.py",
        "run_owned_surface_apply.py",
    ):
        self.assertNotIn(phrase, combined)
```

The README contract must list the canonical no-secret release order and state that SHA-256 is equality/freshness evidence, not encryption or identity proof.

- [ ] **Step 2: Run the focused contract tests and capture RED**

```bash
python3 -m unittest skills.tests.test_s03_runtime_contracts skills.tests.test_coordinator_keystone_closure_contracts -v
```

Expected: failures on the old HMAC/finalization/producer requirements and missing current no-secret wording.

- [ ] **Step 3: Make the package contract edits**

Document these exact current responsibilities:

```text
Linker: plan canonical mutation and exact patch; never write source.
Source owner: recheck the raw-byte baseline immediately before its ordinary edit, then report
              applied | failed | stale_baseline and the resulting digest.
Coordinator: bind scope and starting Git/diff state; collect current diff, worker report,
             verification, document/metadata/graph dispositions, and durable Progress.
Author after Main acceptance: synchronize Work/Progress/index/Context Map and run Work State plus
                              repository graph validation when applicable.
Historical adapters: read supported legacy structures diagnostically; never authorize current success.
```

Remove current/default instructions to create or require HMAC keys, external evidence roots, assignment snapshot receipts, acceptance-event receipts, owner-apply receipts, or new finalization manifests. Keep historical CLI details only in clearly labeled historical compatibility sections.

- [ ] **Step 4: Run focused and adjacent contract tests**

```bash
python3 -m unittest skills.tests.test_s03_runtime_contracts skills.tests.test_coordinator_keystone_closure_contracts skills.tests.test_r006_context_readiness_contracts -v
git diff --check
```

Expected: PASS.

- [ ] **Step 5: Commit only Task 1 paths**

```bash
git add skills/keystone-author/SKILL.md skills/keystone-author/references/finalization-validator.md skills/keystone-coordinator/SKILL.md skills/keystone-coordinator/references/closure-validator.md skills/keystone-linker/SKILL.md skills/keystone-linker/references/graph-runtime.md README.md skills/tests/test_s03_runtime_contracts.py skills/tests/test_coordinator_keystone_closure_contracts.py
git commit -m "docs(r010): align package contracts to core model"
```

---

### Task 2: Remove actual-agent evidence from the canonical release path

**Files:**

- Modify: `scripts/run_release_gate.py`
- Modify: `scripts/run_release_gate.sh`
- Modify: `skills/tests/test_release_gate_agent_eval.py`
- Modify: `skills/tests/test_release_gate_security.py`
- Modify: `README.md`
- Delete: `scripts/agent_eval_scenarios.json`
- Delete: `scripts/validate_agent_evals.py`
- Delete: `skills/tests/test_agent_eval_security.py`

- [ ] **Step 1: Replace agent-validator tests with a failing no-agent release regression**

Keep the filename `test_release_gate_agent_eval.py`, but remove its import of `validate_agent_evals.py` and its validator fixtures. Add:

```python
def test_rc_and_production_plans_need_no_agent_evidence(self):
    for profile in ("rc", "production"):
        plan = RELEASE_GATE.build_plan(REPOSITORY_ROOT, profile=profile)
        identifiers = [step.identifier for step in plan]
        self.assertEqual("release_preflight", identifiers[0])
        self.assertEqual("release_postflight", identifiers[-1])
        self.assertNotIn("agent_behavior_evidence", identifiers)
```

Update security tests to call `build_plan(root, profile=...)` without evidence/key arguments and to expect no `agent` pass envelope.

- [ ] **Step 2: Run release tests and capture RED**

```bash
python3 -m unittest skills.tests.test_release_gate_agent_eval skills.tests.test_release_gate_security -v
```

Expected: `build_plan()` still requires `results_path`, the canonical plan still contains `agent_behavior_evidence`, and agent CLI/envelope assumptions remain.

- [ ] **Step 3: Remove agent authority from `run_release_gate.py` and launcher forwarding**

Change the public plan signature to:

```python
def build_plan(root: Path, *, profile: str = "production") -> Tuple[GateStep, ...]:
    ...
```

Remove the agent step, `KEYSTONE_AGENT_EVAL_*` bootstrap preservation, all `--agent-eval-*` arguments, evidence/key path resolution, agent command-shape validation, the `agent` envelope schema, duration/age parsers, and the agent branch in plan execution. Remove the seven launcher environment forwards while retaining isolated execution and ordinary argument forwarding.

- [ ] **Step 4: Prove current consumers are zero, then delete agent-only artifacts**

```bash
rg -n 'validate_agent_evals\.py|agent_eval_scenarios\.json|agent_behavior_evidence|KEYSTONE_AGENT_EVAL_|--agent-eval-' README.md scripts skills/tests
rg -n 'validate_agent_eval_results|expected_subject|release_package_tree_digest' scripts skills/tests
```

Expected before deletion: matches only in the three deletion candidates. Delete them with a reviewable patch, then rerun both commands and expect zero matches.

- [ ] **Step 5: Run focused tests and list both plans**

```bash
python3 -m unittest skills.tests.test_release_gate_agent_eval skills.tests.test_release_gate_security -v
/bin/sh scripts/run_release_gate.sh --profile rc --list
/bin/sh scripts/run_release_gate.sh --profile production --list
git diff --check
```

Expected: PASS; both listed plans omit agent evidence and external trust inputs.

- [ ] **Step 6: Commit only Task 2 paths**

```bash
git add scripts/run_release_gate.py scripts/run_release_gate.sh skills/tests/test_release_gate_agent_eval.py skills/tests/test_release_gate_security.py README.md scripts/agent_eval_scenarios.json scripts/validate_agent_evals.py skills/tests/test_agent_eval_security.py
git commit -m "fix(r010): remove agent release authority"
```

---

### Task 3: Add current no-secret graph validation before retiring owner-apply receipts

**Files:**

- Modify: `skills/keystone-linker/scripts/validate_graph.py`
- Modify: `skills/keystone-linker/scripts/run_graph_validation.py`
- Modify: `skills/keystone-linker/scripts/graph_runtime/application_evidence.py`
- Modify: `skills/keystone-linker/scripts/graph_runtime/transaction_lifecycle.py`
- Modify: `skills/keystone-linker/tests/test_validate_graph.py`
- Modify: `skills/keystone-linker/tests/test_application_evidence.py`
- Modify: `skills/keystone-linker/tests/test_graph_integration.py`

- [ ] **Step 1: Add failing current-path and historical-boundary tests**

Add a schema-v2/current fixture with transaction patch baselines and apply results but no `application_evidence`, evidence root, or owner keys:

```python
def test_schema2_current_validation_uses_transaction_baseline_without_keys(self):
    manifest = current_schema2_manifest(application_evidence=None)
    result = validate_manifest(self.root, manifest)
    self.assertEqual("pass", result["status"])

def test_historical_application_evidence_is_structural_only(self):
    result = validate_application_evidence(self.root, archived_manifest, None, {})
    self.assertFalse(result.authoritative)
    self.assertIn("historical_structure_only", diagnostic_codes(result))
```

Add failures for tampered current source, baseline content, patch replay, canonical mutation, and reconstruction result.

- [ ] **Step 2: Run Linker focused tests and capture RED**

```bash
PYTHONPATH=skills/keystone-linker/scripts python3 -m unittest discover -s skills/keystone-linker/tests -p 'test_validate_graph.py' -v
PYTHONPATH=skills/keystone-linker/scripts python3 -m unittest discover -s skills/keystone-linker/tests -p 'test_application_evidence.py' -v
PYTHONPATH=skills/keystone-linker/scripts python3 -m unittest discover -s skills/keystone-linker/tests -p 'test_graph_integration.py' -v
```

Expected: current schema-v2 validation still requires authenticated application evidence and external keys.

- [ ] **Step 3: Implement transaction-derived current validation**

Make `application_evidence` optional for current validation. Reconstruct each pre-application source from the transaction's exact surface patch baseline and structurally selected apply result, replay the patch, compare the resulting digest to current bytes, compare embedded reconstruction to canonical mutation application, then run repository graph validation.

Use this decision boundary:

```python
if manifest.get("application_evidence") is not None:
    historical = validate_application_evidence(...)
    diagnostics.extend(historical.diagnostics)
    # Historical evidence can explain an archived wire, but cannot set current success.

current_snapshot = reconstruct_current_sources(root, transaction)
validate_transaction_equality(transaction, current_snapshot, diagnostics)
```

Change isolated historical authority detection to depend on an actual historical `application_evidence` field, never schema version alone. Replace “authenticated pre-application source” wording with “transaction-derived pre-application source.”

- [ ] **Step 4: Run focused and retained transaction tests**

```bash
PYTHONPATH=skills/keystone-linker/scripts python3 -m unittest discover -s skills/keystone-linker/tests -p 'test_validate_graph.py' -v
PYTHONPATH=skills/keystone-linker/scripts python3 -m unittest discover -s skills/keystone-linker/tests -p 'test_application_evidence.py' -v
PYTHONPATH=skills/keystone-linker/scripts python3 -m unittest discover -s skills/keystone-linker/tests -p 'test_transaction_evidence.py' -v
PYTHONPATH=skills/keystone-linker/scripts python3 -m unittest discover -s skills/keystone-linker/tests -p 'test_transaction_lifecycle.py' -v
PYTHONPATH=skills/keystone-linker/scripts python3 -m unittest discover -s skills/keystone-linker/tests -p 'test_graph_integration.py' -v
git diff --check
```

Expected: PASS.

- [ ] **Step 5: Commit only Task 3 paths**

```bash
git add skills/keystone-linker/scripts/validate_graph.py skills/keystone-linker/scripts/run_graph_validation.py skills/keystone-linker/scripts/graph_runtime/application_evidence.py skills/keystone-linker/scripts/graph_runtime/transaction_lifecycle.py skills/keystone-linker/tests/test_validate_graph.py skills/keystone-linker/tests/test_application_evidence.py skills/keystone-linker/tests/test_graph_integration.py
git commit -m "fix(r010): validate current graph without receipts"
```

---

### Task 4: Retire owner-apply HMAC producers and installer coupling

**Files:**

- Modify: `reinstall-local-keystone-skills.sh`
- Modify: `skills/keystone-author/tests/test_graph_finalization_package_e2e.py`
- Modify: `skills/keystone-linker/tests/test_graph_integration.py`
- Modify: `skills/tests/test_coordinator_author_runner_integration.py`
- Modify: `skills/tests/test_coordinator_linker_runner_integration.py`
- Delete: `scripts/generate_owned_surface_apply_runtimes.py`
- Delete: `scripts/owned_surface_apply_runtime.py`
- Delete: `skills/keystone-author/scripts/owned_surface_apply_runtime.py`
- Delete: `skills/keystone-author/scripts/run_owned_surface_apply.py`
- Delete: `skills/keystone-coordinator/scripts/owned_surface_apply_runtime.py`
- Delete: `skills/keystone-coordinator/scripts/run_owned_surface_apply.py`
- Delete: `skills/tests/test_owned_surface_apply_runtime.py`

- [ ] **Step 1: Replace producer-chain tests with failing owner-direct tests**

In package and cross-skill tests, model the owner operation as an ordinary write lane with an immediate baseline check:

```python
before = source.read_bytes()
self.assertEqual(expected_baseline_digest, digest_bytes(before))
source.write_bytes(after)
apply_result = {
    "patch_id": patch_id,
    "status": "applied",
    "resulting_digest": digest_bytes(source.read_bytes()),
    "reason": "source owner applied after baseline recheck",
}
```

Assert the installed package has no owner-apply runner/runtime and the no-secret Linker runner validates the resulting transaction.

- [ ] **Step 2: Run affected integrations and capture RED**

```bash
python3 skills/keystone-author/tests/test_graph_finalization_package_e2e.py -v
python3 skills/tests/test_coordinator_linker_runner_integration.py -v
python3 skills/tests/test_coordinator_author_runner_integration.py -v
```

Expected: tests still invoke or require deleted/current receipt producers.

- [ ] **Step 3: Remove installer and integration coupling**

Remove owned-apply repository/staging/final variables, required-file checks, byte-parity checks, and `--help` smokes from the installer. Update integrations to construct structural apply results after an immediate baseline check and invoke graph validation without `--owner-key`, `--owner-key-sha256`, or `--evidence-root`.

- [ ] **Step 4: Prove current consumers are zero and delete producers**

```bash
rg -n --glob '!00_docs/**' --glob '!docs/**' 'generate_owned_surface_apply_runtimes\.py|owned_surface_apply_runtime\.py|run_owned_surface_apply\.py|from owned_surface_apply_runtime import|apply_owned_surface_patch' scripts skills reinstall-local-keystone-skills.sh
```

Expected before deletion: matches only in deletion candidates. Delete all seven producer/runtime/test files, rerun, and expect zero matches.

- [ ] **Step 5: Run graph/package/installer compatibility**

```bash
PYTHONPATH=skills/keystone-linker/scripts python3 -m unittest discover -s skills/keystone-linker/tests -p 'test_*.py'
python3 skills/keystone-author/tests/test_graph_finalization_package_e2e.py -v
python3 skills/tests/test_coordinator_linker_runner_integration.py -v
python3 skills/tests/test_coordinator_author_runner_integration.py -v
bash -n reinstall-local-keystone-skills.sh
git diff --check
```

Expected: PASS.

- [ ] **Step 6: Commit only Task 4 paths**

```bash
git add reinstall-local-keystone-skills.sh skills/keystone-author/tests/test_graph_finalization_package_e2e.py skills/keystone-linker/tests/test_graph_integration.py skills/tests/test_coordinator_author_runner_integration.py skills/tests/test_coordinator_linker_runner_integration.py scripts/generate_owned_surface_apply_runtimes.py scripts/owned_surface_apply_runtime.py skills/keystone-author/scripts/owned_surface_apply_runtime.py skills/keystone-author/scripts/run_owned_surface_apply.py skills/keystone-coordinator/scripts/owned_surface_apply_runtime.py skills/keystone-coordinator/scripts/run_owned_surface_apply.py skills/tests/test_owned_surface_apply_runtime.py
git commit -m "fix(r010): retire owner apply receipt producers"
```

---

### Task 5: Make closure v1-v3 and finalization v1-v6 explicitly historical readers

**Files:**

- Modify: `skills/keystone-coordinator/scripts/closure_v3.py`
- Modify: `skills/keystone-coordinator/scripts/validate_closure.py`
- Modify: `skills/keystone-coordinator/tests/test_validate_closure.py`
- Modify: `skills/keystone-coordinator/tests/test_validate_closure_v2.py`
- Modify: `skills/keystone-coordinator/tests/test_validate_closure_v3.py`
- Modify: `skills/keystone-author/scripts/run_finalization_validation.py`
- Modify: `skills/keystone-author/tests/test_validate_finalization.py`
- Modify: `skills/keystone-author/tests/test_finalization_integration.py`

- [ ] **Step 1: Add failing static historical-reader tests**

Replace dynamic producer/key-based “history” construction with compact archived dictionaries embedded in test fixtures. Require explicit non-authority:

```python
def test_schema_v3_archived_wire_is_structural_only_without_producers_or_keys(self):
    result = validate_manifest(archived_schema_v3_manifest(), root=self.root)
    self.assertNotEqual("closure_complete", result["decision"])
    self.assertIn("historical_structure_only", diagnostic_codes(result))

def test_schema_v1_through_v6_finalization_are_historical_diagnostics(self):
    for schema_version in range(1, 7):
        result = run_historical_fixture(schema_version)
        self.assertFalse(result.get("current_authority", False))
```

Keep Work State's historical manifest projection unchanged.

- [ ] **Step 2: Run historical adapter tests and capture RED**

```bash
python3 -m unittest discover -s skills/keystone-coordinator/tests -p 'test_validate_closure*.py' -v
python3 -m unittest discover -s skills/keystone-author/tests -p 'test_validate_finalization.py' -v
python3 -m unittest discover -s skills/keystone-author/tests -p 'test_finalization_integration.py' -v
```

Expected: schema-v3 reads still hash producer executables/verify HMAC keys, and finalization runner still exposes current graph evidence/key authority.

- [ ] **Step 3: Remove live producer-byte/key authority from historical reads**

In `closure_v3.py`, stop resolving the sibling producer executable and stop requiring external keys to interpret archived receipts. Validate only stable wire structure, canonical digests that can be recomputed from the wire, typed phase ordering, and internal references. Emit `historical_structure_only`; never emit a current success decision.

In the Author runner, preserve `--root` and `--manifest` historical validation. Remove current/default `--graph-evidence-root`, `--graph-owner-key`, and `--graph-owner-key-sha256` requirements; graph schema-v2/application evidence remains diagnostic historical input.

- [ ] **Step 4: Run historical and Work State regression suites**

```bash
python3 -m unittest discover -s skills/keystone-coordinator/tests -p 'test_*.py'
python3 -m unittest discover -s skills/keystone-author/tests -p 'test_finalization*.py'
python3 -m unittest skills.tests.test_work_state_runtime -v
git diff --check
```

Expected: PASS; historical records remain readable, and none authorizes a new current success.

- [ ] **Step 5: Commit only Task 5 paths**

```bash
git add skills/keystone-coordinator/scripts/closure_v3.py skills/keystone-coordinator/scripts/validate_closure.py skills/keystone-coordinator/tests/test_validate_closure.py skills/keystone-coordinator/tests/test_validate_closure_v2.py skills/keystone-coordinator/tests/test_validate_closure_v3.py skills/keystone-author/scripts/run_finalization_validation.py skills/keystone-author/tests/test_validate_finalization.py skills/keystone-author/tests/test_finalization_integration.py
git commit -m "fix(r010): isolate historical closure readers"
```

---

### Task 6: Remove current snapshot/finalization producers and dedicated release phases

**Files:**

- Modify: `scripts/run_release_gate.py`
- Modify: `skills/tests/test_release_gate_agent_eval.py`
- Modify: `skills/tests/test_release_gate_security.py`
- Modify: `reinstall-local-keystone-skills.sh`
- Modify: `skills/tests/test_coordinator_keystone_closure_contracts.py`
- Modify: `skills/tests/test_coordinator_author_runner_integration.py`
- Modify: `skills/tests/test_coordinator_linker_runner_integration.py`
- Modify: `skills/keystone-author/tests/test_graph_finalization_package_e2e.py`
- Delete: `skills/keystone-coordinator/scripts/capture_assignment_snapshot.py`
- Delete: `skills/keystone-coordinator/scripts/record_acceptance_event.py`
- Delete: `skills/keystone-coordinator/tests/test_capture_assignment_snapshot.py`
- Delete: `skills/keystone-coordinator/tests/test_record_acceptance_event.py`

- [ ] **Step 1: Add a failing minimal current closure integration**

Replace the authority chain with a fixture containing assignment scope, starting/current file digests, current diff paths, worker report, verification result, document/metadata/graph dispositions, and durable Progress:

```python
def test_current_closure_needs_no_receipt_or_finalization_manifest(self):
    closure = current_closure_fixture(
        assignment_scope=["src/example.py"],
        changed_paths=["src/example.py"],
        verification={"command": "python3 -m unittest ...", "status": "pass"},
        dispositions={"document": "not_applicable", "metadata": "not_applicable", "graph": "complete"},
        progress_path="00_docs/work/progress.md",
    )
    self.assertEqual("accept_candidate", validate_current_closure(closure)["decision"])
    self.assertNotIn("acceptance_event", closure)
    self.assertNotIn("finalization_manifest", closure)
```

Update release plan assertions so both profiles omit:

```python
for retired in (
    "historical_r008_r009_finalization",
    "current_repository_finalization",
    "coordinator_actual_state_v2",
    "coordinator_actual_state_v3",
    "coordinator_actual_state_self_check",
):
    self.assertNotIn(retired, identifiers)
```

- [ ] **Step 2: Run release/cross-package tests and capture RED**

```bash
python3 -m unittest skills.tests.test_release_gate_agent_eval skills.tests.test_release_gate_security skills.tests.test_coordinator_keystone_closure_contracts skills.tests.test_coordinator_author_runner_integration skills.tests.test_coordinator_linker_runner_integration -v
python3 skills/keystone-author/tests/test_graph_finalization_package_e2e.py -v
```

Expected: current release still runs historical/current finalization and Coordinator v2/v3 phases; packages still require snapshot/acceptance producers.

- [ ] **Step 3: Remove current release and installer consumers**

Remove `_historical_finalization_check`, `_current_finalization_check`, their two steps, all three Coordinator v2/v3/self-check steps, and dispatch branches from `run_release_gate.py`. Keep compatibility coverage in package tests. Remove capture/acceptance repository, staging, and final-install variables/checks/help smokes from the installer.

- [ ] **Step 4: Convert cross-package tests to the current minimal closure**

The current integration must use repository files and ordinary verification only. Keep separate historical tests for closure v2/v3 and finalization v1-v6. Installed package tests must assert the historical validators remain callable and the current producer files are absent.

- [ ] **Step 5: Prove producer consumers are zero and delete producers/tests**

```bash
rg -n 'capture_assignment_snapshot|record_acceptance_event' skills scripts reinstall-local-keystone-skills.sh README.md
rg -n 'CAPTURE_COMMAND_ID|ACCEPTANCE_COMMAND_ID|CAPTURE_EXECUTABLE_NAME|ACCEPTANCE_EXECUTABLE_NAME' skills/keystone-coordinator
rg -n 'current_repository_finalization|historical_r008_r009_finalization|coordinator_actual_state_v[23]|coordinator_actual_state_self_check' scripts skills/tests README.md
```

Expected before deletion: producer-name matches only in the four deletion candidates. Delete them, rerun, and expect zero current-consumer matches. Static archived fixture fields may remain only where explicitly labeled historical.

- [ ] **Step 6: Run focused release, closure, Author, and installer tests**

```bash
python3 -m unittest discover -s skills/keystone-coordinator/tests -p 'test_*.py'
python3 -m unittest discover -s skills/keystone-author/tests -p 'test_*.py'
python3 -m unittest skills.tests.test_release_gate_agent_eval skills.tests.test_release_gate_security skills.tests.test_coordinator_keystone_closure_contracts skills.tests.test_coordinator_author_runner_integration skills.tests.test_coordinator_linker_runner_integration -v
python3 scripts/run_release_gate.py --profile rc --list
python3 scripts/run_release_gate.py --profile production --list
bash -n reinstall-local-keystone-skills.sh
git diff --check
```

Expected: PASS.

- [ ] **Step 7: Commit only Task 6 paths**

```bash
git add scripts/run_release_gate.py skills/tests/test_release_gate_agent_eval.py skills/tests/test_release_gate_security.py reinstall-local-keystone-skills.sh skills/tests/test_coordinator_keystone_closure_contracts.py skills/tests/test_coordinator_author_runner_integration.py skills/tests/test_coordinator_linker_runner_integration.py skills/keystone-author/tests/test_graph_finalization_package_e2e.py skills/keystone-coordinator/scripts/capture_assignment_snapshot.py skills/keystone-coordinator/scripts/record_acceptance_event.py skills/keystone-coordinator/tests/test_capture_assignment_snapshot.py skills/keystone-coordinator/tests/test_record_acceptance_event.py
git commit -m "fix(r010): simplify current closure authority"
```

---

### Task 7: Verify the retained product core and exact scope

**Files:**

- Modify only if a directly caused regression requires it: retained core caller/import files already listed in the S06 Work Order
- Do not modify retained core algorithms merely to make broad tests pass

- [ ] **Step 1: Run retained Artifact Graph suites**

```bash
PYTHONPATH=skills/keystone-linker/scripts python3 -m unittest discover -s skills/keystone-linker/tests -p 'test_source_*.py'
PYTHONPATH=skills/keystone-linker/scripts python3 -m unittest discover -s skills/keystone-linker/tests -p 'test_graph_*.py'
PYTHONPATH=skills/keystone-linker/scripts python3 -m unittest discover -s skills/keystone-linker/tests -p 'test_transaction_*.py'
PYTHONPATH=skills/keystone-linker/scripts python3 -m unittest discover -s skills/keystone-linker/tests -p 'test_validate_graph.py'
```

Expected: PASS with no capability reduction.

- [ ] **Step 2: Run Work State and contract suites**

```bash
python3 scripts/generate_work_state_runtimes.py --check
python3 -m unittest skills.tests.test_work_state_runtime skills.tests.test_s03_runtime_contracts skills.tests.test_r006_context_readiness_contracts -v
```

Expected: PASS and byte parity for all Work State copies/manifests.

- [ ] **Step 3: Run all package and shared tests**

```bash
for package in skills/keystone-*/tests; do python3 -m unittest discover -s "$package" -p 'test_*.py' || exit 1; done
python3 -m unittest discover -s skills/tests -p 'test_*.py'
```

Expected: PASS.

- [ ] **Step 4: Run release readiness in canonical order**

```bash
python3 scripts/run_release_gate.py --profile rc --list
python3 scripts/run_release_gate.py --profile production --list
python3 skills/keystone-linker/scripts/graph_runtime/readiness.py --root . --scope docs
python3 skills/keystone-linker/scripts/graph_runtime/readiness.py --root . --scope repository
python3 scripts/work_state_runtime.py --root .
python3 skills/keystone-linker/scripts/validate_graph.py --root . --scope repository
```

Expected: both plans have the canonical nine phases; readiness, Work State, and repository graph validation pass without keys or external evidence.

- [ ] **Step 5: Run compile, installer, shell, and diff verification**

```bash
S06_PYCACHE_ROOT="$(mktemp -d)"
PYTHONPYCACHEPREFIX="$S06_PYCACHE_ROOT" python3 -m compileall -q scripts skills
bash -n scripts/run_release_gate.sh
bash -n reinstall-local-keystone-skills.sh
git diff --check
git status --short
```

Run installer staging/parity/rollback only against a temporary `CODEX_HOME`, never the user's installed skills.

- [ ] **Step 6: Check exact scope and scan for retired current authority**

```bash
git diff --name-only "$S06_IMPLEMENTATION_BASE"..HEAD
rg -n 'HMAC|hmac|reviewer key|evidence root|agent_behavior_evidence|run_owned_surface_apply|capture_assignment_snapshot|record_acceptance_event' README.md scripts skills --glob '!**/tests/fixtures/**'
git diff --name-only "$S06_IMPLEMENTATION_BASE"..HEAD | rg '00_docs/works/r011-work-model-evolution'
```

Every remaining HMAC/evidence reference must be explicitly historical structural compatibility. The R011 scope search must be empty.

- [ ] **Step 7: Request independent code review and repair only in-scope findings**

Review for spec compliance first, then implementation quality. Any extra required path outside the S06 Change Set is a stop condition requiring Main approval.

- [ ] **Step 8: Commit only directly caused verification repairs, if any**

Stage every reviewed repair path by its exact filename, confirm `git diff --cached --name-only`, then commit with `fix(r010): close core simplification regressions`.

Skip this commit when verification required no repair.

---

## Completion Handoff

After all seven tasks are green, Coordinator must produce a concise pre-acceptance closure record containing:

```yaml
scope:
  implementation_base: recorded Coordinator Context Pack commit
  changed_paths: exact cumulative path list from Git
  forbidden_paths_changed: []
verification:
  focused: pass
  packages: pass
  shared: pass
  work_state: pass
  repository_graph: pass
  installer_staging: pass
historical_compatibility:
  closure_v1_v3: structural_only
  finalization_v1_v6: structural_only
  graph_v2_application_evidence: structural_only
current_authority:
  keys_required: false
  external_evidence_required: false
  agent_evidence_required: false
decision: accept_candidate | repair | blocked
```

Main retains acceptance. Only after Main accepts may Author synchronize S06 Progress, Work/index/Context Map metadata, then run Work State and repository graph validation. A new finalization manifest is not a current success prerequisite.
