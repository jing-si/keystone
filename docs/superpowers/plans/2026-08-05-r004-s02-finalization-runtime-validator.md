# R004 S02 Finalization Runtime and Validator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Main acceptance 뒤 Author가 finalization을 자동 시작하고, package-owned 진단 전용 validator의 실행 증거 없이는 완료하지 못하게 한다.

**Architecture:** `keystone-author`가 finalization orchestration과 fail-closed 판정을 소유하고 `scripts/validate_finalization.py`를 subprocess interface로 호출한다. Validator는 JSON manifest와 Keystone Markdown을 표준 라이브러리만으로 검사하고 machine-readable diagnostics와 안정된 exit code를 반환하며, 문서·상태는 절대 수정하지 않는다.

**Tech Stack:** Markdown skill contracts, Python 3.9+ standard library, `unittest`, Bash installer smoke checks.

## Global Constraints

- 기존 lifecycle·approval·work status 체계를 보강하며 새 전역 상태 체계로 대체하지 않는다.
- 직접 상태 전이는 현재 처리하는 Step에만 적용하고, Work·Round·root index·Context Map은 각자의 조건을 평가한다.
- `active_steps`는 0개 이상의 동등한 Step 참조 목록이며 단수 `current_step`을 권위 상태로 사용하지 않는다.
- 미래 Step 선작업은 `early_work`로 기록하고 `status_effect: none`을 유지한다.
- Validator와 hook은 진단 전용이며 source edit, acceptance, finalization 완료 전이를 수행하지 않는다.
- Core validator는 `skills/keystone-author/scripts/`에 포함하고 Python 외부 패키지를 요구하지 않는다.
- 필수 validator가 없거나 실행할 수 없으면 각각 `validator_unavailable`, `validator_execution_failed`로 fail-closed한다.
- S03 상태는 이 계획에서 변경하지 않는다.

---

### Task 1: Activate S02 and lock the runtime interface

**Files:**
- Modify: `00_docs/works/r004-acceptance-finalization/00_key-index.md`
- Modify: `00_docs/works/r004-acceptance-finalization/finalization-runtime-validator/00_key-index.md`
- Modify: `00_docs/works/r004-acceptance-finalization/finalization-runtime-validator/key-work-finalization-runtime-validator.md`
- Modify: `00_docs/works/r004-acceptance-finalization/finalization-runtime-validator/key-progress.md`
- Modify: `00_docs/key-context-map.md`

**Interfaces:**
- Consumes: accepted `DEC-WORKS-021` and R004 S01 contract.
- Produces: `active_steps` entry for R004/S02 and an unchanged planned S03.

- [x] **Step 1:** Change only S02 from `planned` to `in_progress` in its work/index/progress surfaces.
- [x] **Step 2:** Add R004/S02 to `active_steps` in the round index and Context Map.
- [x] **Step 3:** Verify S01 remains accepted and S03 remains planned with `rg`.

### Task 2: Build the diagnostic-only validator with TDD

**Files:**
- Create: `skills/keystone-author/tests/test_validate_finalization.py`
- Create: `skills/keystone-author/scripts/validate_finalization.py`
- Create: `skills/keystone-author/references/finalization-validator.md`

**Interfaces:**
- Consumes: `python3 validate_finalization.py --root ROOT --manifest MANIFEST`.
- Produces: one JSON object on stdout with `status`, `diagnostics`, and `summary`; exit `0` for pass, `1` for validation findings, `2` for invocation/execution errors.

- [x] **Step 1: Write failing CLI tests**

  Cover a valid manifest, missing/invalid manifest, duplicate or unresolved active step, stale singular current-step claim, invalid early-work status effect, missing candidate disposition/reason/path, and duplicate namespace ownership.

- [x] **Step 2: Run RED**

  Run: `python3 -m unittest discover -s skills/keystone-author/tests -p 'test_*.py' -v`

  Expected: failure because `scripts/validate_finalization.py` does not exist.

- [x] **Step 3: Implement the smallest validator**

  Parse JSON without third-party dependencies, resolve all paths under `--root`, validate the declared manifest schema, scan in-scope non-historical Markdown candidates for singular current-step claims, detect namespace/value collisions across owners, and never open files for writing.

- [x] **Step 4: Run GREEN**

  Run: `python3 -m unittest discover -s skills/keystone-author/tests -p 'test_*.py' -v`

  Expected: all tests pass with no warnings.

- [x] **Step 5: Run package smoke tests**

  Invoke the script once with a passing fixture and once with a failing fixture; verify JSON output and exit codes `0` and `1`.

### Task 3: Connect skill runtime and installation verification

**Files:**
- Modify: `skills/keystone-author/SKILL.md`
- Modify: `skills/keystone-coordinator/SKILL.md`
- Modify: `skills/keystone-reader/SKILL.md`
- Modify only if required by the accepted contract: `skills/keystone-linker/SKILL.md`, `skills/keystone-init/SKILL.md`
- Modify: `reinstall-local-keystone-skills.sh`

**Interfaces:**
- Consumes: validator CLI and diagnostic schema from Task 2.
- Produces: automatic acceptance-finalization procedure, scoped gate, resume reasons, and installed artifact verification.

- [x] **Step 1:** Add the Author acceptance trigger, impact-disposition manifest preparation, validator invocation, fail-closed mapping, resume, and completion ownership.
- [x] **Step 2:** Make Reader recover all `active_steps` and `early_work`; make Coordinator preserve equal active steps and block only the same Work's next implementation transition while finalization is incomplete.
- [x] **Step 3:** Add installer preflight and post-copy checks for `keystone-author/scripts/validate_finalization.py` without installing globally.
- [x] **Step 4:** Run unit tests and `bash -n reinstall-local-keystone-skills.sh`.

### Task 4: Verify, review, and finalize S02 documents

**Files:**
- Modify after evidence: R004 S02 work order, progress, work index, round index, and Context Map.

**Interfaces:**
- Consumes: test output, smoke output, independent review findings.
- Produces: S02 `complete`/`accepted` only if Main verification and finalization evidence pass; otherwise leaves S02 active with explicit residuals.

- [x] **Step 1:** Run the full unit suite, package smoke, Bash syntax check, Markdown fence/frontmatter/ID checks, and `git diff --check`.
- [x] **Step 2:** Obtain independent spec and quality review through the user-authorized Coordinator scope and resolve load-bearing findings.
- [x] **Step 3:** Re-read every completion criterion and map it to fresh evidence.
- [x] **Step 4:** Update only S02's direct status; evaluate R004/root/Context Map on their own conditions, preserve S03 planned, and record finalization evidence or fail-closed reason.
