# R010/S05 Agent Behavior Evaluation Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the no-cost, provider-neutral S05 evaluation runtime, reviewer boundary, schema-v2 validator, release consumer, and Codex CLI adapter needed to propose—but not yet execute—the authorized live 48-cell evaluation.

**Architecture:** A standard-library functional core defines the strict matrix, evidence, snapshot, redaction, budget, and diagnostic contracts. Thin evaluator, reviewer, validator, release-gate, and Codex CLI shells exchange canonical JSON/JSONL through argument-vector subprocess boundaries; test fixture adapters exercise the whole lifecycle without creating admissible live evidence.

**Tech Stack:** Python 3.9+ standard library, immutable dataclasses, canonical JSON/JSONL, SHA-256, HMAC-SHA256, `unittest`, isolated subprocesses, existing Bash release launcher.

## Global Constraints

- The canonical authority is `00_docs/works/r010-production-control-plane-hardening/agent-behavior-evaluation/key-work-agent-behavior-evaluation.md`; the approved design is `docs/superpowers/specs/2026-08-09-r010-s05-agent-behavior-evaluation-design.md`.
- Preserve all existing S03/S04 edits. Do not revert, normalize, stage, or absorb them into an S05 commit accidentally.
- The current worktree has known unstaged S03/S04 changes, including `scripts/run_release_gate.py` and `README.md`. Before task commits touch an overlapping file, Coordinator must establish a reviewed prerequisite baseline commit or use exact hunk staging and verify the staged diff contains only the intended S05 delta.
- Python runtime remains Python 3.9+ and standard-library-only. No provider SDK or external package may be added.
- Every external command is an argument vector executed without a shell. Runtime environments are allowlisted and do not inherit arbitrary `PYTHONPATH`, startup hooks, or credentials.
- The evaluator never reads or writes the reviewer key. Reviewer key material remains outside both repository and evidence roots.
- Live transcripts, attachments, snapshots, review responses, and keys never enter the repository.
- Test fixture adapters are marked `execution_class: test_fixture`; validator release admission must reject them even when structural validation passes.
- This plan performs no live model invocation and authorizes no external cost. It ends by producing an exact live-run proposal for separate user approval.
- The twelve scenario meanings and ordered IDs remain unchanged. Schema v2 adds matrix, identity, snapshot, redaction, review, and budget structure without weakening any required check.
- Every scenario declares one actual installed Keystone skill invocation. The canonical mapping is: `uninitialized` → `keystone-reader`, `partial_scaffold` → `keystone-init`, `conflicting_roots` → `keystone-reader`, `one_topic_clarify` → `keystone-clarify`, `interrupted_resume` → `keystone-reader`, `waiting_dependency` → `keystone-coordinator`, `scope_violation` → `keystone-coordinator`, `forged_graph` → `keystone-linker`, `extra_authority` → `keystone-coordinator`, `prompt_injection` → `keystone-linker`, `partial_transaction_resume` → `keystone-linker`, and `multi_step_acceptance_finalization` → `keystone-author`.
- The canonical matrix is exactly two settings × two repeats × twelve scenarios = forty-eight unique cells, plus four reviewer batches and one non-model final signing operation.
- Unknown model identity, prompt/tool coverage, usage, rate, cost, timeout state, snapshot completeness, redaction state, or reviewer disposition is a failure.
- Browser/Playwright verification, publication, dependency installation, merge, push, S06, and S07 changes are excluded.
- Use `unittest` and TDD. Each executable task must show RED before implementation and GREEN afterward.

## File Structure

- Create `scripts/agent_eval_runtime.py`: strict JSON, canonical digests, immutable schema-v2 domain values, matrix derivation, budget accounting, and stable diagnostics.
- Create `scripts/agent_eval_evidence.py`: complete fixture snapshot capture, allowed-delta comparison, in-memory redaction, attachment persistence, and evidence-reference verification.
- Create `scripts/run_agent_evals.py`: plan-only and execution CLI, isolated fixture lifecycle, neutral evaluator/reviewer command protocol, resume, and final structural/release validation dispatch.
- Create `scripts/review_agent_evals.py`: reviewer batch protocol, hidden-variation binding, negative-control validation, and final HMAC signing boundary.
- Create `scripts/agent_eval_adapters/codex_cli.py`: minimum Codex CLI capability probe and neutral request/JSONL normalization adapter.
- Modify `scripts/agent_eval_scenarios.json`: exact schema-v2 scenario/matrix/budget contract.
- Modify `scripts/validate_agent_evals.py`: independent schema-v2 reconstruction and release-admission validator; schema-v1 becomes recognized but inadmissible.
- Modify `scripts/run_release_gate.py`: consume only schema-v2 current-subject live evidence.
- Create `skills/tests/fixtures/agent_eval_fixture_adapter.py`: deterministic evaluator/reviewer protocol fixture, never live-admissible.
- Create `skills/tests/test_agent_eval_runtime.py`: schema, matrix, budget, snapshot, and redaction tests.
- Create `skills/tests/test_agent_eval_runner.py`: subprocess, isolation, resume, partial failure, and deterministic end-to-end tests.
- Create `skills/tests/test_agent_eval_reviewer.py`: hidden variation, negative control, identity separation, and signing tests.
- Create `skills/tests/test_agent_eval_codex_adapter.py`: Codex argument-shape, capability, event, identity, and usage normalization tests without network calls.
- Modify `skills/tests/test_agent_eval_security.py`: migrate security fixtures to schema v2 and retain symlink/hardlink/duplicate-key/isolated-launcher attacks.
- Modify `skills/tests/test_release_gate_agent_eval.py`: schema-v2 pass and legacy/incomplete/forged/non-live rejection.
- Modify `skills/tests/test_release_gate_security.py`: preserve command-shape and environment hardening under the new validator arguments.
- Modify `README.md`: document plan-only, structural fixture, live execution, external evidence, and explicit cost-authorization boundaries.
- Modify S05 Progress/index/work-order and graph/finalization surfaces only through the Coordinator → Linker/Author closure after implementation evidence exists.

---

### Task 1: Strict Schema-v2 Matrix Core

**Files:**
- Create: `scripts/agent_eval_runtime.py`
- Modify: `scripts/agent_eval_scenarios.json`
- Create: `skills/tests/test_agent_eval_runtime.py`

**Interfaces:**
- Consumes: a strict JSON object with exact top-level fields `schema_version`, `suite_id`, `adapter_protocol_version`, `settings`, `repeats`, `budgets`, `snapshot_policy`, `redaction_rules`, `review_policy`, and `scenarios`.
- Produces: `load_eval_spec(path: Path) -> EvalSpec`, `matrix_coordinates(spec: EvalSpec) -> Tuple[MatrixCoordinate, ...]`, `canonical_json_bytes(value: Any) -> bytes`, `digest_bytes(value: bytes) -> str`, and `diagnostic(code: str, message: str, path: str) -> Dict[str, str]`.
- `MatrixCoordinate` fields are exactly `setting_id`, `repeat_id`, and `scenario_id`; ordering is settings, then repeats, then scenarios in source order.
- Each scenario contains exact fields `id`, `skill_id`, `prompt`, `fixture`, `expected_outcome`, `required_checks`, and `allowed_output_paths`; the evaluator binds the installed skill source digest before invocation.
- Stable Task-1 diagnostics: `strict_json_invalid`, `spec_fields_invalid`, `spec_schema_invalid`, `matrix_cardinality_invalid`, `matrix_identifier_invalid`, `budget_invalid`, and `scenario_set_invalid`.

- [ ] **Step 1: Write failing exact-matrix and malformed-spec tests**

```python
class AgentEvalSpecTest(unittest.TestCase):
    def test_canonical_spec_derives_exact_ordered_matrix(self):
        spec = RUNTIME.load_eval_spec(SPEC_PATH)
        coordinates = RUNTIME.matrix_coordinates(spec)
        self.assertEqual(48, len(coordinates))
        self.assertEqual(
            ("baseline", "repeat-01", "uninitialized"),
            coordinates[0].as_tuple(),
        )
        self.assertEqual(
            ("contrast", "repeat-02", "multi_step_acceptance_finalization"),
            coordinates[-1].as_tuple(),
        )
        self.assertEqual(48, len({item.as_tuple() for item in coordinates}))

    def test_duplicate_key_boolean_version_and_missing_budget_fail(self):
        with self.assertRaisesRegex(ValueError, "strict_json_invalid"):
            RUNTIME.strict_json_loads(b'{"schema_version":2,"schema_version":2}')
        value = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
        value["schema_version"] = True
        with self.assertRaisesRegex(ValueError, "spec_schema_invalid"):
            RUNTIME.parse_eval_spec(value)
        value = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
        del value["budgets"]["suite"]
        with self.assertRaisesRegex(ValueError, "budget_invalid"):
            RUNTIME.parse_eval_spec(value)
```

- [ ] **Step 2: Run Task-1 tests and confirm RED**

Run: `python3 -m unittest skills.tests.test_agent_eval_runtime.AgentEvalSpecTest -v`

Expected: FAIL because `scripts/agent_eval_runtime.py` and the schema-v2 fields do not exist.

- [ ] **Step 3: Implement immutable schema values and exact Cartesian derivation**

```python
@dataclass(frozen=True)
class MatrixCoordinate:
    setting_id: str
    repeat_id: str
    scenario_id: str

    def as_tuple(self) -> Tuple[str, str, str]:
        return self.setting_id, self.repeat_id, self.scenario_id


def matrix_coordinates(spec: EvalSpec) -> Tuple[MatrixCoordinate, ...]:
    coordinates = tuple(
        MatrixCoordinate(setting.identifier, repeat_id, scenario.identifier)
        for setting in spec.settings
        for repeat_id in spec.repeats
        for scenario in spec.scenarios
    )
    if len(coordinates) != 48 or len({item.as_tuple() for item in coordinates}) != 48:
        raise ValueError("matrix_cardinality_invalid")
    return coordinates
```

Set canonical setting IDs to `baseline` and `contrast`, repeat IDs to `repeat-01` and `repeat-02`, and
retain the current twelve ordered scenario IDs and required checks verbatim. Add the exact skill mapping
from Global Constraints and use an empty `allowed_output_paths` array unless the scenario's expected
behavior requires a bounded fixture write. Define hard technical
ceilings in `budgets`: cell timeout 300 seconds, one attempt, 50,000 input tokens, 8,000 output tokens,
500,000 USD micro-units; reviewer-batch timeout 300 seconds, one attempt, 200,000 input tokens, 20,000
output tokens, 2,000,000 USD micro-units; suite timeout 14,400 seconds, 52 model invocations, 3,200,000
input tokens, 500,000 output tokens, and 32,000,000 USD micro-units. These are fail-closed ceilings, not
permission to incur cost; the later live-run proposal must choose equal or lower values.

- [ ] **Step 4: Run Task-1 tests and confirm GREEN**

Run: `python3 -m unittest skills.tests.test_agent_eval_runtime.AgentEvalSpecTest -v`

Expected: PASS with 48 unique coordinates and stable malformed-input failures.

- [ ] **Step 5: Commit only the matrix core slice**

```bash
git add scripts/agent_eval_runtime.py scripts/agent_eval_scenarios.json skills/tests/test_agent_eval_runtime.py
git diff --cached --check
git diff --cached --name-only
git commit -m "feat(r010): define agent evaluation matrix v2"
```

Expected staged paths: exactly the three Task-1 paths.

### Task 2: Complete Snapshot and Pre-persistence Redaction

**Files:**
- Create: `scripts/agent_eval_evidence.py`
- Modify: `skills/tests/test_agent_eval_runtime.py`

**Interfaces:**
- Consumes: `SnapshotPolicy(include_paths: Tuple[str, ...], exclusions: Tuple[SnapshotExclusion, ...], entry_budget: int)` and raw attachment bytes held in memory.
- Produces: `capture_snapshot(root: Path, policy: SnapshotPolicy) -> Snapshot`, `changed_paths(before: Snapshot, after: Snapshot) -> Tuple[str, ...]`, `enforce_allowed_changes(paths: Sequence[str], allowed: Sequence[str]) -> None`, `redact_bytes(raw: bytes, probes: Sequence[bytes]) -> RedactionResult`, and `persist_redacted_attachment(root: Path, relative: str, result: RedactionResult) -> EvidenceRef`.
- `Snapshot` exposes exact `to_wire()` fields: `schema_version`, `policy`, `policy_digest`, `entries`, `discovered_path_count`, `path_set_digest`, `complete`, `truncated`, and `snapshot_digest`.
- Stable Task-2 diagnostics: `snapshot_drift`, `snapshot_truncated`, `snapshot_path_collision`, `snapshot_entry_unsupported`, `snapshot_budget_exceeded`, `change_outside_allowlist`, `redaction_probe_invalid`, `redaction_incomplete`, and `attachment_path_invalid`.

- [ ] **Step 1: Add failing snapshot, delta, and byte-redaction tests**

```python
class AgentEvalEvidenceTest(unittest.TestCase):
    def test_snapshot_is_complete_and_unlisted_change_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "input.txt").write_bytes(b"before")
            policy = EVIDENCE.SnapshotPolicy((".",), (), 32)
            before = EVIDENCE.capture_snapshot(root, policy)
            (root / "output.txt").write_bytes(b"after")
            after = EVIDENCE.capture_snapshot(root, policy)
            self.assertEqual(("output.txt",), EVIDENCE.changed_paths(before, after))
            with self.assertRaisesRegex(ValueError, "change_outside_allowlist"):
                EVIDENCE.enforce_allowed_changes(("output.txt",), ("allowed/",))

    def test_secret_bytes_never_reach_persisted_attachment(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            secret = b"keystone-sensitive-probe"
            result = EVIDENCE.redact_bytes(b"prefix:" + secret, (secret,))
            ref = EVIDENCE.persist_redacted_attachment(root, "cells/a/transcript.jsonl", result)
            self.assertNotIn(secret, (root / ref.path).read_bytes())
            self.assertEqual(1, result.match_count)
            self.assertNotEqual(result.source_digest, ref.sha256)
```

- [ ] **Step 2: Run evidence tests and confirm RED**

Run: `python3 -m unittest skills.tests.test_agent_eval_runtime.AgentEvalEvidenceTest -v`

Expected: FAIL because the evidence module and public types are absent.

- [ ] **Step 3: Implement no-follow snapshots and in-memory redaction**

```python
@dataclass(frozen=True)
class RedactionResult:
    redacted: bytes
    source_digest: str
    redacted_digest: str
    match_count: int


def redact_bytes(raw: bytes, probes: Sequence[bytes]) -> RedactionResult:
    if any(not probe for probe in probes):
        raise ValueError("redaction_probe_invalid")
    redacted = raw
    matches = 0
    for probe in sorted(set(probes), key=lambda value: (-len(value), value)):
        count = redacted.count(probe)
        matches += count
        redacted = redacted.replace(probe, b"[REDACTED]")
    if any(probe in redacted for probe in probes):
        raise ValueError("redaction_incomplete")
    return RedactionResult(redacted, digest_bytes(raw), digest_bytes(redacted), matches)
```

Open files and directories with no-follow flags where supported, capture twice when discovery metadata
drifts, fail after the second drift, sort paths by normalized UTF-8 repository-relative name, reject
case-fold collisions and unsupported entry types, and write only `RedactionResult.redacted` through a
same-directory temporary file followed by `os.replace`.

- [ ] **Step 4: Run Task-2 and Task-1 tests and confirm GREEN**

Run: `python3 -m unittest skills.tests.test_agent_eval_runtime -v`

Expected: PASS; no raw probe bytes exist under the temporary evidence root.

- [ ] **Step 5: Commit the evidence slice**

```bash
git add scripts/agent_eval_evidence.py skills/tests/test_agent_eval_runtime.py
git diff --cached --check
git commit -m "feat(r010): capture and redact agent eval evidence"
```

### Task 3: Neutral Evaluator Protocol and Isolated Runner

**Files:**
- Create: `scripts/run_agent_evals.py`
- Create: `skills/tests/fixtures/agent_eval_fixture_adapter.py`
- Create: `skills/tests/test_agent_eval_runner.py`

**Interfaces:**
- Consumes: `--root`, `--spec`, `--evidence-root`, `--evaluator-command-json`, `--execution-class {test_fixture,live}`, optional `--run-config`, and optional `--plan-only`; Task 4 adds required `--reviewer-command-json` for final suite assembly. `--run-config` is mandatory for execution and has exact fields `schema_version`, `setting_bindings`, `pricing_table`, and `skill_sources`; plan-only reports the structural matrix without claiming a frozen live execution plan.
- Produces: `invoke_jsonl_adapter(command: Sequence[str], request: Mapping[str, Any], cwd: Path, timeout_seconds: int, environment: Mapping[str, str]) -> AdapterInvocation`, `freeze_execution_plan(spec: EvalSpec, run_config: Mapping[str, Any]) -> Dict[str, Any]`, and CLI JSON envelope fields `schema_version`, `suite_id`, `status`, `execution_class`, `plan_digest`, `results_path`, `cells`, `diagnostics`, and `summary`.
- Adapter stdin is one canonical JSON request. Adapter stdout is ordered JSONL with zero or more `event` records and exactly one final `result` record.
- The runner uses a new fixture/cache/invocation directory for each coordinate and never passes `PYTHONPATH`, reviewer-key variables, or unrelated host variables.
- Stable Task-3 diagnostics: `run_config_missing`, `run_config_invalid`, `skill_source_invalid`, `skill_digest_mismatch`, `adapter_command_invalid`, `adapter_protocol_invalid`, `adapter_timeout`, `adapter_partial_output`, `adapter_exit_nonzero`, `fixture_not_isolated`, `plan_digest_mismatch`, `cell_incomplete`, and `suite_budget_exceeded`.

- [ ] **Step 1: Write failing plan-only, 48-cell isolation, timeout, and partial-output tests**

```python
class AgentEvalRunnerTest(unittest.TestCase):
    def test_plan_only_freezes_exact_matrix_without_invoking_adapter(self):
        process = self.run_runner("--plan-only")
        payload = json.loads(process.stdout)
        self.assertEqual(0, process.returncode)
        self.assertEqual("planned", payload["status"])
        self.assertEqual(48, payload["summary"]["cells"])
        self.assertRegex(payload["plan_digest"], r"^sha256:[0-9a-f]{64}$")

    def test_fixture_adapter_uses_unique_cell_roots(self):
        process, evidence = self.run_fixture_suite()
        payload = json.loads(process.stdout)
        self.assertEqual(0, process.returncode, process.stderr)
        roots = [item["fixture_root_digest"] for item in payload["cells"]]
        self.assertEqual(48, len(roots))
        self.assertEqual(48, len(set(roots)))

    def test_timeout_and_missing_final_result_never_pass(self):
        timeout = self.run_fixture_suite(mode="timeout")[0]
        partial = self.run_fixture_suite(mode="partial")[0]
        self.assertNotEqual(0, timeout.returncode)
        self.assertNotEqual(0, partial.returncode)
        self.assertIn("adapter_timeout", timeout.stdout)
        self.assertIn("adapter_partial_output", partial.stdout)
```

- [ ] **Step 2: Run runner tests and confirm RED**

Run: `python3 -m unittest skills.tests.test_agent_eval_runner.AgentEvalRunnerTest -v`

Expected: FAIL because the runner and fixture adapter do not exist.

- [ ] **Step 3: Implement the exact JSONL subprocess boundary and cell lifecycle**

```python
def invoke_jsonl_adapter(command, request, cwd, timeout_seconds, environment):
    if not command or any(not isinstance(token, str) or not token for token in command):
        raise ValueError("adapter_command_invalid")
    try:
        process = subprocess.run(
            tuple(command), input=canonical_json_bytes(request) + b"\n",
            cwd=str(cwd), env=dict(environment), capture_output=True,
            timeout=timeout_seconds, check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise ValueError("adapter_timeout") from error
    records = tuple(strict_json_loads(line) for line in process.stdout.splitlines())
    results = [item for item in records if item.get("type") == "result"]
    if process.returncode != 0:
        raise ValueError("adapter_exit_nonzero")
    if len(results) != 1 or records[-1] is not results[0]:
        raise ValueError("adapter_partial_output")
    return AdapterInvocation(records[:-1], results[0])
```

Implement `--plan-only` before subprocess creation. For execution, materialize the fixture, capture
before/after snapshots, invoke the adapter once because `max_attempts` is one, redact in memory, persist
only redacted attachments, and atomically write an unsigned cell record. Resolve every scenario's
`skill_id` through `run_config.skill_sources`, bind the exact installed `SKILL.md` bytes, and require the
adapter result to report that same skill invocation and digest. On resume, reuse a cell only
after every plan/subject/attachment/snapshot digest revalidates.

- [ ] **Step 4: Run runner and core tests and confirm GREEN**

Run: `python3 -m unittest skills.tests.test_agent_eval_runtime skills.tests.test_agent_eval_runner -v`

Expected: PASS; fixture mode creates 48 isolated non-live cell records and all injected failures remain nonzero.

- [ ] **Step 5: Commit the evaluator shell slice**

```bash
git add scripts/run_agent_evals.py skills/tests/fixtures/agent_eval_fixture_adapter.py skills/tests/test_agent_eval_runner.py
git diff --cached --check
git commit -m "feat(r010): run isolated agent evaluation cells"
```

### Task 4: Independent Reviewer Batches and Final Signing

**Files:**
- Create: `scripts/review_agent_evals.py`
- Create: `skills/tests/test_agent_eval_reviewer.py`
- Modify: `scripts/run_agent_evals.py`
- Modify: `skills/tests/fixtures/agent_eval_fixture_adapter.py`
- Modify: `skills/tests/test_agent_eval_runner.py`

**Interfaces:**
- Consumes reviewer modes `review-batch` and `sign-suite`; hidden variation path and reviewer key path are arguments to the reviewer process, never fields in evaluator evidence.
- Produces: `build_review_batches(cells: Sequence[Mapping[str, Any]]) -> Tuple[ReviewBatch, ...]`, `validate_review_response(batch: ReviewBatch, response: Mapping[str, Any]) -> None`, and `sign_suite_manifest(manifest: Mapping[str, Any], key: bytes, reviewer_id: str) -> Dict[str, str]`.
- Four batches are keyed by `(setting_id, repeat_id)`, contain twelve ordered cells and one seeded negative control, and return twelve dispositions plus one control disposition.
- Stable Task-4 diagnostics: `review_batch_coverage_invalid`, `reviewer_identity_conflict`, `reviewer_invocation_conflict`, `hidden_variation_missing`, `hidden_variation_disclosed`, `negative_control_accepted`, `review_attestation_invalid`, and `suite_attestation_invalid`.

- [ ] **Step 1: Write failing reviewer-separation, hidden-variation, and control tests**

```python
class AgentEvalReviewerTest(unittest.TestCase):
    def test_four_batches_cover_cells_and_reject_controls(self):
        batches = REVIEW.build_review_batches(self.cells)
        self.assertEqual(4, len(batches))
        self.assertTrue(all(len(batch.cells) == 12 for batch in batches))
        response = self.fixture_response(batches[0], control_status="reject")
        REVIEW.validate_review_response(batches[0], response)

    def test_self_review_leaked_hidden_value_and_accepted_control_fail(self):
        batch = REVIEW.build_review_batches(self.cells)[0]
        for mutation, code in (
            ({"reviewer_id": self.evaluator_id}, "reviewer_identity_conflict"),
            ({"hidden_variation_value": "secret"}, "hidden_variation_disclosed"),
            ({"negative_control": {"status": "pass"}}, "negative_control_accepted"),
        ):
            response = self.fixture_response(batch, control_status="reject")
            response.update(mutation)
            with self.assertRaisesRegex(ValueError, code):
                REVIEW.validate_review_response(batch, response)
```

- [ ] **Step 2: Run reviewer tests and confirm RED**

Run: `python3 -m unittest skills.tests.test_agent_eval_reviewer -v`

Expected: FAIL because reviewer batch and signing code is absent.

- [ ] **Step 3: Implement reviewer-only hidden input and canonical HMAC**

```python
def sign_suite_manifest(manifest, key, reviewer_id):
    if len(key) < 32:
        raise ValueError("suite_attestation_invalid")
    unsigned = dict(manifest)
    unsigned.pop("attestation", None)
    signature = hmac.new(key, canonical_json_bytes(unsigned), hashlib.sha256).hexdigest()
    return {
        "reviewer_id": reviewer_id,
        "algorithm": "hmac-sha256",
        "hmac_sha256": signature,
    }
```

Open hidden variation and key with no-follow, owner/single-link/mode checks. The model-review request
contains only the hidden variation ID/digest and redacted cell evidence. The reviewer process loads the
hidden bytes locally, rejects a response that echoes them, signs each valid batch, then signs the final
suite manifest in `sign-suite` mode without another model invocation.

- [ ] **Step 4: Run reviewer plus runner tests and confirm GREEN**

Run: `python3 -m unittest skills.tests.test_agent_eval_reviewer skills.tests.test_agent_eval_runner -v`

Expected: PASS with four complete batches, rejected controls, distinct identities, and a verifiable final HMAC.

- [ ] **Step 5: Commit reviewer boundaries**

```bash
git add scripts/review_agent_evals.py scripts/run_agent_evals.py skills/tests/fixtures/agent_eval_fixture_adapter.py skills/tests/test_agent_eval_reviewer.py skills/tests/test_agent_eval_runner.py
git diff --cached --check
git commit -m "feat(r010): separate agent evaluation review"
```

### Task 5: Independent Schema-v2 Validator and Security Migration

**Files:**
- Modify: `scripts/validate_agent_evals.py`
- Modify: `skills/tests/test_agent_eval_security.py`
- Modify: `skills/tests/test_agent_eval_runner.py`

**Interfaces:**
- Preserves CLI arguments `--root`, `--spec`, `--evidence-root`, `--results`, `--reviewer-key`, `--trusted-reviewer`, `--trusted-reviewer-key-sha256`, `--max-age-hours`, and `--max-run-duration-hours`.
- Adds library argument `admission_mode: str = "release"` to `validate_agent_eval_results`; accepted values are `structural` and `release`.
- Structural mode verifies the full schema and integrity but permits `execution_class: test_fixture`; release mode additionally requires `execution_class: live` and an admissible adapter capability record.
- Exact root result fields are `schema_version`, `suite_id`, `execution_class`, `spec`, `subject`, `plan`, `started_at`, `completed_at`, `cells`, `review_batches`, `redaction`, `accounting`, and `attestation`.
- Stable Task-5 diagnostics include all existing path/key/HMAC/freshness codes plus `legacy_schema_not_admissible`, `execution_class_not_admissible`, `matrix_coverage_invalid`, `matrix_coordinate_duplicate`, `adapter_binding_invalid`, `snapshot_binding_invalid`, `redaction_binding_invalid`, `budget_accounting_invalid`, `review_binding_invalid`, and `negative_control_invalid`.

- [ ] **Step 1: Replace the old passing fixture with schema v2 and add legacy/non-live rejection tests**

```python
def test_schema_v2_fixture_passes_structural_but_not_release_admission(self):
    value = self.valid_v2_results(execution_class="test_fixture")
    self.assertEqual([], self.validate(value, admission_mode="structural"))
    codes = {item["code"] for item in self.validate(value, admission_mode="release")}
    self.assertIn("execution_class_not_admissible", codes)

def test_schema_v1_is_recognized_but_never_admitted(self):
    value = self.valid_v1_results()
    codes = {item["code"] for item in self.validate(value)}
    self.assertIn("legacy_schema_not_admissible", codes)

def test_missing_coordinate_snapshot_redaction_and_review_fail(self):
    value = self.valid_v2_results(execution_class="live")
    value["cells"].pop()
    value["cells"][0]["before_snapshot"]["complete"] = False
    value["review_batches"][0]["negative_control"]["status"] = "pass"
    codes = {item["code"] for item in self.validate(value)}
    self.assertIn("matrix_coverage_invalid", codes)
    self.assertIn("snapshot_binding_invalid", codes)
    self.assertIn("negative_control_invalid", codes)
```

- [ ] **Step 2: Run validator/security tests and confirm RED**

Run: `python3 -m unittest skills.tests.test_agent_eval_security skills.tests.test_agent_eval_runner -v`

Expected: FAIL because the current validator requires schema v1 and exact-once scenarios.

- [ ] **Step 3: Implement complete schema-v2 reconstruction and legacy diagnostic**

```python
def validate_agent_eval_results(
    root, spec_path, results_path, *, evidence_root, reviewer_key_path,
    trusted_reviewer_id, trusted_reviewer_key_sha256="", now=None,
    max_age_hours=DEFAULT_MAX_AGE_HOURS,
    max_run_duration_hours=DEFAULT_MAX_RUN_DURATION_HOURS,
    admission_mode="release",
):
    if admission_mode not in {"structural", "release"}:
        return [diagnostic("admission_mode_invalid", "unsupported admission mode", "admission_mode")]
    result_value = _load_stable_strict_result(results_path)
    if result_value.get("schema_version") == 1:
        return [diagnostic(
            "legacy_schema_not_admissible",
            "schema-v1 exactly-once evidence cannot satisfy R010/S05",
            "results.schema_version",
        )]
    findings = _validate_v2_result(root, spec_path, result_value, evidence_root)
    if admission_mode == "release" and result_value.get("execution_class") != "live":
        findings.append(diagnostic(
            "execution_class_not_admissible",
            "release admission requires actual live invocation evidence",
            "results.execution_class",
        ))
    return findings
```

Retain stable-file reads, duplicate-key rejection, no-follow path checks, distinct inode/digest rules,
trusted Git resolution, package-tree subject calculation, freshness, key mode/ownership/anchor checks,
and isolated re-exec. Reconstruct all 48 expected coordinates from the selected spec and verify each
cell, batch, attachment, accounting total, and final attestation rather than trusting summary fields.

- [ ] **Step 4: Run all agent-eval tests and confirm GREEN**

Run: `python3 -m unittest discover -s skills/tests -p 'test_agent_eval*.py' -v`

Expected: PASS for schema-v2 structural evidence and every migrated attack test; release admission rejects fixture and schema-v1 results.

- [ ] **Step 5: Commit the validator migration**

```bash
git add scripts/validate_agent_evals.py skills/tests/test_agent_eval_security.py skills/tests/test_agent_eval_runner.py
git diff --cached --check
git commit -m "feat(r010): validate agent evaluation evidence v2"
```

### Task 6: Release-gate Schema-v2 Consumption

**Files:**
- Modify: `scripts/run_release_gate.py`
- Modify: `skills/tests/test_release_gate_agent_eval.py`
- Modify: `skills/tests/test_release_gate_security.py`

**Interfaces:**
- Consumes the unchanged external evidence/key CLI inputs and the schema-v2 validator release mode.
- Produces one `agent_behavior_evidence` JSON-command gate that accepts only `status: pass`, `schema_version: 2`, `summary.errors: 0`, `summary.cells_required: 48`, `summary.review_batches_required: 4`, and no diagnostics.
- Release gate lists and validates evidence but never invokes evaluator or reviewer model commands.

- [ ] **Step 1: Add failing release-gate v2 envelope and legacy/non-live tests**

```python
def test_agent_gate_requires_v2_live_matrix_summary(self):
    result = RELEASE_GATE.CommandResult(
        0,
        json.dumps({
            "schema_version": 2,
            "suite_id": "r010-agent-behavior",
            "status": "pass",
            "diagnostics": [],
            "summary": {"errors": 0, "cells_required": 48, "review_batches_required": 4},
        }),
        "",
    )
    self.assertIsNone(RELEASE_GATE._agent_evidence_result_error(result))

def test_agent_gate_rejects_v1_and_non_live_diagnostics(self):
    for payload in (self.v1_pass_envelope(), self.non_live_v2_envelope()):
        error = RELEASE_GATE._agent_evidence_result_error(
            RELEASE_GATE.CommandResult(0, json.dumps(payload), "")
        )
        self.assertIsNotNone(error)
```

- [ ] **Step 2: Run release agent/security tests and confirm RED**

Run: `python3 -m unittest skills.tests.test_release_gate_agent_eval skills.tests.test_release_gate_security -v`

Expected: FAIL because the release consumer accepts only the old summary shape.

- [ ] **Step 3: Implement exact v2 result-envelope admission**

```python
def _agent_evidence_result_error(result: CommandResult) -> Optional[str]:
    payload = _strict_json_loads(result.stdout)
    expected_summary = {"errors": 0, "cells_required": 48, "review_batches_required": 4}
    if result.returncode != 0:
        return "agent evidence validator failed"
    if (
        not isinstance(payload, dict)
        or payload.get("schema_version") != 2
        or payload.get("status") != "pass"
        or payload.get("diagnostics") != []
        or payload.get("summary") != expected_summary
    ):
        return "agent evidence validator output is not an admissible v2 envelope"
    return None
```

Keep `_agent_command_shape` exact and continue using `python -I`. Add no evaluator/reviewer commands to
`build_plan`; the only agent behavior step remains the validator invocation.

- [ ] **Step 4: Run release agent/security tests and confirm GREEN**

Run: `python3 -m unittest skills.tests.test_release_gate_agent_eval skills.tests.test_release_gate_security -v`

Expected: PASS; plan listing is unchanged except for schema-v2 output expectations.

- [ ] **Step 5: Commit only the S05 release-gate delta**

Because `scripts/run_release_gate.py` already contains unstaged S04 changes, first inspect:

```bash
git diff -- scripts/run_release_gate.py
git diff --cached -- scripts/run_release_gate.py
```

After the Coordinator prerequisite baseline or exact hunk staging has isolated S05:

```bash
git add scripts/run_release_gate.py skills/tests/test_release_gate_agent_eval.py skills/tests/test_release_gate_security.py
git diff --cached --check
git diff --cached -- scripts/run_release_gate.py
git commit -m "feat(r010): admit agent evaluation evidence v2"
```

Expected staged release-gate hunks: schema-v2 agent evidence validation only; the existing S04 Work State gate must already be in the prerequisite baseline and remain unchanged.

### Task 7: Codex CLI Capability and Invocation Adapter

**Files:**
- Create: `scripts/agent_eval_adapters/codex_cli.py`
- Create: `skills/tests/test_agent_eval_codex_adapter.py`
- Modify: `scripts/run_agent_evals.py`

**Interfaces:**
- Consumes neutral adapter requests in modes `probe` and `invoke`, plus an absolute Codex executable path and fixed model/reasoning configuration.
- Produces JSONL `capability`, `event`, and final `result` records with `adapter_id: codex-cli-v1`, adapter executable/config digests, invocation ID, requested model claim, provider-asserted identity, invoked skill ID/source digest, prompt-layer completeness, tool-schema completeness, ordered events, usage tokens, and process status.
- Probe succeeds only when executable metadata and requested configuration are measurable; live admission additionally requires actual output to expose provider identity, every required prompt layer, complete tool schema, and usage.
- Stable Task-7 diagnostics: `codex_executable_invalid`, `codex_version_invalid`, `codex_capability_incomplete`, `codex_event_invalid`, `codex_provider_identity_missing`, `codex_prompt_binding_incomplete`, `codex_tool_schema_incomplete`, and `codex_usage_missing`.

- [ ] **Step 1: Write failing command-shape and recorded-event normalization tests**

```python
class CodexAdapterTest(unittest.TestCase):
    def test_command_is_ephemeral_json_bounded_and_has_no_bypass(self):
        command = ADAPTER.build_codex_command(
            Path("/opt/codex"), Path("/fixture"), "model-a", "medium",
        )
        self.assertIn("--ephemeral", command)
        self.assertIn("--json", command)
        self.assertIn("--sandbox", command)
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", command)
        self.assertNotIn("--dangerously-bypass-hook-trust", command)

    def test_missing_provider_prompt_tool_or_usage_capability_fails(self):
        for missing, code in (
            ("provider_identity", "codex_provider_identity_missing"),
            ("prompt_layers", "codex_prompt_binding_incomplete"),
            ("tool_schema", "codex_tool_schema_incomplete"),
            ("usage", "codex_usage_missing"),
        ):
            records = self.complete_recorded_jsonl()
            del records[-1][missing]
            with self.assertRaisesRegex(ValueError, code):
                ADAPTER.normalize_codex_records(records)
```

- [ ] **Step 2: Run Codex adapter tests and confirm RED**

Run: `python3 -m unittest skills.tests.test_agent_eval_codex_adapter -v`

Expected: FAIL because the Codex adapter module is absent.

- [ ] **Step 3: Implement offline capability checks and strict event normalization**

```python
def build_codex_command(executable, fixture_root, model, reasoning_effort):
    return (
        str(executable), "exec", "--ephemeral", "--json",
        "--sandbox", "workspace-write", "--cd", str(fixture_root),
        "--model", model, "--config",
        'model_reasoning_effort="%s"' % reasoning_effort,
        "-",
    )
```

Resolve and measure the executable without following symlinks into an untrusted tree, call only
`codex --version` during offline probe, and never make an agent request in this plan. Normalize recorded
JSONL fixtures for unit tests. If static metadata cannot prove live prompt/tool/provider/usage exposure,
return `codex_capability_incomplete`; do not invent fields from the requested configuration.

- [ ] **Step 4: Run Codex, runner, and security tests and confirm GREEN**

Run: `python3 -m unittest skills.tests.test_agent_eval_codex_adapter skills.tests.test_agent_eval_runner skills.tests.test_agent_eval_security -v`

Expected: PASS without network or model calls; the local installed CLI may report an incomplete live capability until the separately authorized probe.

- [ ] **Step 5: Commit the Codex adapter slice**

```bash
git add scripts/agent_eval_adapters/codex_cli.py scripts/run_agent_evals.py skills/tests/test_agent_eval_codex_adapter.py
git diff --cached --check
git commit -m "feat(r010): add bounded Codex evaluation adapter"
```

### Task 8: Deterministic Non-live End-to-End and Operator Documentation

**Files:**
- Modify: `skills/tests/test_agent_eval_runner.py`
- Modify: `skills/tests/test_release_gate_agent_eval.py`
- Modify: `README.md`

**Interfaces:**
- Consumes all runtime surfaces from Tasks 1–7 and the fixture evaluator/reviewer adapter.
- Produces a 48-cell external temporary evidence tree that passes structural validation, fails release admission with `execution_class_not_admissible`, and leaves the repository unchanged.
- Documents three separate commands: plan-only, fixture structural run, and live run proposal; only the first two are runnable under this plan.

- [ ] **Step 1: Add a failing full lifecycle test with repository before/after digest**

```python
def test_full_fixture_lifecycle_is_structurally_valid_but_release_inadmissible(self):
    before = VALIDATOR.release_package_tree_digest(ROOT)
    process, evidence = self.run_fixture_suite()
    self.assertEqual(0, process.returncode, process.stderr)
    findings = VALIDATOR.validate_agent_eval_results(
        ROOT, SPEC_PATH, evidence / "agent-eval-results.json",
        evidence_root=evidence, reviewer_key_path=self.key_path,
        trusted_reviewer_id=self.reviewer_id,
        trusted_reviewer_key_sha256=digest(self.key_path),
        admission_mode="structural",
    )
    self.assertEqual([], findings)
    release_codes = {item["code"] for item in self.release_findings(evidence)}
    self.assertIn("execution_class_not_admissible", release_codes)
    self.assertEqual(before, VALIDATOR.release_package_tree_digest(ROOT))
```

- [ ] **Step 2: Run the lifecycle test and confirm RED**

Run: `python3 -m unittest skills.tests.test_agent_eval_runner.AgentEvalRunnerTest.test_full_fixture_lifecycle_is_structurally_valid_but_release_inadmissible -v`

Expected: FAIL until runner final assembly, reviewer final signing, structural validator dispatch, and non-live release rejection are connected.

- [ ] **Step 3: Complete fixture lifecycle wiring and document exact commands**

Document these no-cost commands:

```bash
python3 -I scripts/run_agent_evals.py --root . --spec scripts/agent_eval_scenarios.json --plan-only
python3 -m unittest skills.tests.test_agent_eval_runner.AgentEvalRunnerTest.test_full_fixture_lifecycle_is_structurally_valid_but_release_inadmissible -v
/bin/sh scripts/run_release_gate.sh --profile rc --list
```

Document that a live command is emitted only as a redacted proposal containing adapter path/digest,
setting/model/reasoning mapping, pricing-table digest, 48 evaluator calls, four reviewer calls, one
capability-probe allowance, per-cell/reviewer/suite budgets, external evidence path, and reviewer trust
requirements. Do not include a runnable live command before user approval.

- [ ] **Step 4: Run the focused S05 and release suites and confirm GREEN**

Run:

```bash
python3 -m unittest discover -s skills/tests -p 'test_agent_eval*.py' -v
python3 -m unittest skills.tests.test_release_gate_agent_eval skills.tests.test_release_gate_security -v
```

Expected: all tests pass; no network call occurs; fixture evidence is structurally valid and release-inadmissible.

- [ ] **Step 5: Commit documentation and lifecycle closure**

Because `README.md` already has an unstaged S04 edit, inspect and isolate the S05 hunk exactly as required by the Global Constraints, then commit:

```bash
git add skills/tests/test_agent_eval_runner.py skills/tests/test_release_gate_agent_eval.py README.md
git diff --cached --check
git diff --cached -- README.md
git commit -m "test(r010): verify agent evaluation lifecycle"
```

### Task 9: Full Verification, Coordinator Closure, and Live-run Proposal

**Files:**
- Modify through Author only: `00_docs/works/r010-production-control-plane-hardening/agent-behavior-evaluation/key-progress.md`
- Modify through Author only when actual state requires it: S05 `00_key-index.md`, Work Order, round/root indexes, and Context Map.
- Modify through Linker/owning surface only when classified required: graph validation/finalization manifests.
- Create outside repository: verification logs, artifact-delta record, capability report, and live-run proposal.

**Interfaces:**
- Consumes all implementation commits, focused test output, current work-state output, full readiness/graph results, and exact changed-file digests.
- Produces a canonical Coordinator worker report with one artifact delta per changed surface, Linker classifications, Author sync disposition, verification closure, residual risk, and `recommended_next_action: request_live_execution_authorization`.
- S05 remains `in_progress` and pending; no `accept_candidate`, Main acceptance, finalization, S06 activation, or live evidence claim is allowed in this plan.

- [ ] **Step 1: Run focused, package, and cross-skill verification sequentially**

```bash
python3 -m unittest discover -s skills/tests -p 'test_agent_eval*.py' -v
python3 -m unittest discover -s skills/keystone-author/tests -p 'test_*.py'
python3 -m unittest discover -s skills/keystone-coordinator/tests -p 'test_*.py'
python3 -m unittest discover -s skills/keystone-linker/tests -p 'test_*.py'
python3 -m unittest discover -s skills/keystone-reader/tests -p 'test_*.py'
python3 -m unittest discover -s skills/tests -p 'test_*.py'
```

Expected: every suite exits 0. Run sequentially so protected external evidence and temporary trust roots do not interfere.

- [ ] **Step 2: Run static, work-state, readiness, and full graph verification**

```bash
env PYTHONPYCACHEPREFIX=/private/tmp/keystone-s05-pycache python3 -m compileall -q -f skills scripts
python3 -I scripts/work_state_runtime.py --root .
env PYTHONPATH=skills/keystone-linker/scripts python3 -m graph_runtime.readiness_cli --request-json '{"repository_root":".","cache_path":"/private/tmp/keystone-s05-docs.sqlite3","initiator":"reader","artifact_context":false}' --response-json -
env PYTHONPATH=skills/keystone-linker/scripts python3 -m graph_runtime.readiness_cli --request-json '{"repository_root":".","cache_path":"/private/tmp/keystone-s05-repository.sqlite3","initiator":"linker","artifact_context":true}' --response-json -
python3 skills/keystone-linker/scripts/validate_graph.py --root . --scope repository
bash -n reinstall-local-keystone-skills.sh
git diff --check
```

Expected: compileall and shell syntax exit 0; Work State reports R010/S05 as sole active Step with zero diagnostics; both readiness runs are complete with zero errors/skips; full graph has zero diagnostics; diff check is clean.

- [ ] **Step 3: Classify every changed surface and route source sync**

Build one artifact delta for every S05-created or modified repository path using its pre-change and
post-change SHA-256. Ask Linker for required/not-required graph disposition without inventing relations.
Route required S05 Progress and metadata updates to Author. Record fixture evidence as test evidence,
not actual behavior evidence, and keep every live-dependent criterion pending.

- [ ] **Step 4: Produce the exact live-run proposal without executing it**

The external proposal must include:

```json
{
  "schema_version": 1,
  "status": "awaiting_user_authorization",
  "evaluator_calls": 48,
  "reviewer_calls": 4,
  "capability_probe_calls": 1,
  "final_signing_operations": 1,
  "settings": ["baseline", "contrast"],
  "repeats": ["repeat-01", "repeat-02"],
  "required_bindings": [
    "adapter_digest",
    "model_and_reasoning",
    "pricing_table_digest",
    "prompt_layers",
    "tool_schema",
    "provider_identity",
    "usage_and_cost",
    "reviewer_identity_and_key_fingerprint",
    "hidden_variation_digest",
    "external_evidence_root"
  ]
}
```

Populate the proposal from measured local adapter capability and current user-selected model/pricing
inputs at that time. If any required binding cannot be measured, set status to `blocked` with its exact
diagnostic instead of proposing the 52 model calls.

- [ ] **Step 5: Record pre-live closure and stop at the authorization gate**

The Coordinator review must report implementation verification, preserved Main context, document/
metadata/graph sync disposition, and the remaining live-evidence criteria. Author updates Progress to
state that the runtime is implemented and verified but actual invocation/review is pending. Commit only
the verified Author/Linker closure paths after staged-path review. Do not mark S05 complete or accepted.

## Plan Completion Check

Before execution handoff, confirm:

- Every design section maps to Tasks 1–9.
- No task performs live model calls or writes secrets/evidence into the repository.
- All public function names used by later tasks are introduced in an earlier task.
- Schema-v1 has one stable inadmissible diagnostic and no new release success path.
- Fixture mode can prove mechanics but cannot become S05 acceptance evidence.
- The existing dirty S03/S04 surfaces have an explicit baseline/hunk-staging safeguard.
- S05 remains active after this implementation plan and awaits a separately authorized live-run plan.
