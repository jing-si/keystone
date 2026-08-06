# Reference Index and Context Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Recenter Keystone on source-owned stable IDs and refs, add docs-first Reader context readiness with permissionless Linker indexing, and reserve typed graph traversal and transactions for the cases that need them.

**Architecture:** Human-readable standards and inline/companion metadata remain authoritative. Linker derives an external, disposable owner/ref index and materializes typed subgraphs lazily; Reader is the session context-readiness entry point but never owns the cache or graph meaning. Multi-surface changes use graph transactions, while direct single-surface work uses owner apply plus index refresh and scoped validation.

**Tech Stack:** Markdown Keystone source documents, Python 3 standard library (`argparse`, `dataclasses`, `hashlib`, `json`, `sqlite3`), `unittest`, Bash installer smoke tests.

## Global Constraints

- Preserve R003-R005 accepted work records as historical evidence; express compatibility and supersession only in R006 sources.
- No user-facing global CLI, PATH modification, external database, global install, publication, or external consumer repository change.
- Reader remains repository-source read-only; Linker may write only an external disposable cache and remains source-write-free.
- Permissionless Linker subagents may scan, index, interpret, and validate but cannot edit source, expand scope, create workers, decide project meaning, or accept work.
- `id` has one owner; other artifacts use `refs`. Typed relations are optional and limited to multi-hop traversal, role semantics, dependency, verification evidence, or reuse analysis.
- Graph transactions are required only for multi-surface changes. Transaction validation gates current work; repository validation reports coverage debt and blocks only current-transaction omissions.
- Keep initialization, context readiness, work execution, approval, dependency, graph transaction, finalization, and verification states in separate namespaces.
- Work execution completion is `work_status: complete`; Main acceptance is `approval.state: accepted`. Default dependencies require both.
- `requires_verification_of` expresses a requirement; `verifies` expresses completed test or verification-result evidence.
- Declared metadata is source-authored; effective metadata is derived through document → section → item inheritance without inheriting `id`, `supersedes`, legacy terms, or general typed relations.
- Context freshness includes the discovery-scope path set and raw-byte source digests; Git HEAD or mtime alone is insufficient.
- Reader→Linker index-readiness calls and Linker→Reader context-recovery calls carry a serialized recursion guard and cannot call back into the initiating lane.
- Use TDD for executable runtime changes and keep existing Author, Linker, and runtime-contract suites green.

---

### Task 1: R006 Work Foundation and Accepted Decision Record

**Files:**
- Create: `00_docs/works/r006-reference-index-context-readiness/00_key-index.md`
- Create: `00_docs/works/r006-reference-index-context-readiness/reference-index-contract-standard/{00_key-index.md,key-work-reference-index-contract-standard.md,key-progress.md}`
- Create: `00_docs/works/r006-reference-index-context-readiness/skill-context-contract-integration/{00_key-index.md,key-work-skill-context-contract-integration.md,key-progress.md}`
- Create: `00_docs/works/r006-reference-index-context-readiness/index-runtime-implementation/{00_key-index.md,key-work-index-runtime-implementation.md,key-progress.md}`
- Create: `00_docs/works/r006-reference-index-context-readiness/integration-verification/{00_key-index.md,key-work-integration-verification.md,key-progress.md}`
- Modify: `00_docs/works/key-decisions.md`
- Modify: `00_docs/works/00_key-index.md`
- Modify: `00_docs/key-context-map.md`

**Interfaces:**
- Consumes: user-accepted decisions captured in this conversation and R005 accepted contracts.
- Produces: R006 S01-S04 authoritative scope, `DEC-WORKS-025`, active-step recovery, and the standards Change Set used by Task 2.

- [ ] **Step 1: Create the R006 round and four work nodes**

Record S01 `in_progress`; S02-S04 `planned`. S01 owns the complete standards contract, S02 the installed skill contracts, S03 the executable index runtime, and S04 integration verification/finalization.

- [ ] **Step 2: Record DEC-WORKS-025 as additive claim-level policy**

Record each Global Constraint as a stable claim. Add IDs to only the historical DEC-WORKS-021/024 bullets that are partially superseded, preserve their text, and point the new claims to those IDs. Do not supersede R005 as a whole.

- [ ] **Step 3: Activate R006 in global navigation**

Update the root works index and both current-state locations in Context Map so they agree on R006/S01. Keep R005 accepted.

- [ ] **Step 4: Verify document structure**

Run:

```bash
rg -n "R006|Active steps|DEC-WORKS-025" 00_docs/works 00_docs/key-context-map.md
git diff --check
```

Expected: exactly one active round, S01 active, no whitespace errors.

- [ ] **Step 5: Commit**

```bash
git add 00_docs/works/r006-reference-index-context-readiness 00_docs/works/key-decisions.md 00_docs/works/00_key-index.md 00_docs/key-context-map.md
git commit -m "docs: define R006 reference index work"
```

### Task 2: Canonical Standards Reconciliation

**Files:**
- Modify: `00_docs/standards/01_key-project-standard.md`
- Modify: `00_docs/standards/artifacts/key-standard-artifact-graph.md`
- Modify: `00_docs/standards/subagents/key-standard-subagents.md`
- Modify: `00_docs/standards/bootstrap/key-standard-bootstrap.md`
- Modify: `00_docs/standards/skills/init/key-standard-init.md`
- Modify: `00_docs/standards/skills/reader/key-standard-reader.md`
- Modify: `00_docs/standards/skills/linker/key-standard-linker.md`
- Modify: `00_docs/standards/skills/author/key-standard-author.md`
- Modify: `00_docs/standards/skills/coordinator/key-standard-coordinator.md`
- Modify: `00_docs/standards/skills/clarify/key-standard-clarify.md`
- Modify: relevant standard child indexes and `00_docs/standards/00_key-index.md`
- Modify: R006 S01 work/progress/index and global Context Map after acceptance

**Interfaces:**
- Consumes: R006 S01 work order and `DEC-WORKS-025`.
- Produces: complete normative contract for Tasks 3-5, including explicit compatibility with historical R003-R005 states.

- [ ] **Step 1: Reconcile core identity, state, verification, and validation rules**

Define owner/ref-first identity, unique owner, optional typed graph, separate execution/approval states, `requires_verification_of`, declared/effective inheritance, dependency `complete + accepted`, and transaction/repository validation scopes.

- [ ] **Step 2: Reconcile Reader and permissionless Linker responsibilities**

Define explicit Reader session orientation, docs-scope readiness, freshness tokens, external Linker cache ownership, lazy repository scan, recursion guard, fail-soft fallback, and hidden internal payload behavior.

- [ ] **Step 3: Reconcile authoring, coordination, bootstrap, initialization, and clarification contracts**

Define direct single-surface refresh versus multi-surface transaction, conflict-reason retry, fresh Reader context reuse, context invalidation after writes, and the narrow permissionless Linker subagent exception without expanding Coordinator authority.

- [ ] **Step 4: Cross-read examples and indexes**

Replace acceptance-item `verifies` requirement examples with `requires_verification_of`; ensure every relation direction example matches the standard matrix. Update index summaries without creating duplicate authority.

- [ ] **Step 5: Run standards verification**

```bash
rg -n "owner/ref|requires_verification_of|declared|effective|permissionless|transaction.*repository|complete.*accepted|recursion" 00_docs/standards
rg -n "verifies=.*key\.claim|work_status: accepted" 00_docs/standards
git diff --check
```

Expected: accepted new vocabulary is present; stale requirement examples and conflated terminal state examples are absent or explicitly marked historical compatibility.

- [ ] **Step 6: Commit**

```bash
git add 00_docs/standards 00_docs/works/r006-reference-index-context-readiness 00_docs/key-context-map.md
git commit -m "docs: align Keystone reference index standards"
```

### Task 3: Installed Skill Contract Synchronization

**Files:**
- Modify: `skills/keystone-reader/SKILL.md`
- Modify: `skills/keystone-linker/SKILL.md`
- Modify: `skills/keystone-author/SKILL.md`
- Modify: `skills/keystone-coordinator/SKILL.md`
- Modify if contract impact is concrete: `skills/keystone-init/SKILL.md`, `skills/keystone-clarify/SKILL.md`
- Create: `skills/tests/test_r006_context_readiness_contracts.py`
- Modify: R006 S02 work/progress/index and Context Map after acceptance

**Interfaces:**
- Consumes: accepted Task 2 standards.
- Produces: self-contained installed contracts for the runtime implemented in Task 4.

- [ ] **Step 1: Write failing contract tests**

Assert docs-first Reader readiness, permissionless one-hop Linker enrichment, cache/source authority boundary, optional graph/transaction, state separation, freshness invalidation, and recursion guard language across the four skill sources.

- [ ] **Step 2: Run the RED test**

```bash
python3 -m unittest skills.tests.test_r006_context_readiness_contracts -v
```

Expected: failures identify missing R006 contracts.

- [ ] **Step 3: Update skill sources minimally**

Implement only accepted Task 2 semantics. Keep structured readiness/enrichment payloads hidden by default and do not expose a user-facing CLI.

- [ ] **Step 4: Run contract and regression tests**

```bash
python3 -m unittest skills.tests.test_r006_context_readiness_contracts -v
python3 -m unittest skills.tests.test_s03_runtime_contracts -v
```

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add skills/keystone-reader/SKILL.md skills/keystone-linker/SKILL.md skills/keystone-author/SKILL.md skills/keystone-coordinator/SKILL.md skills/keystone-init/SKILL.md skills/keystone-clarify/SKILL.md skills/tests/test_r006_context_readiness_contracts.py 00_docs/works/r006-reference-index-context-readiness 00_docs/key-context-map.md
git commit -m "feat: align Keystone context readiness skills"
```

### Task 4: Internal Owner/Ref Index Runtime

**Files:**
- Create: `skills/keystone-linker/scripts/graph_runtime/index_model.py`
- Create: `skills/keystone-linker/scripts/graph_runtime/scanner.py`
- Create: `skills/keystone-linker/scripts/graph_runtime/index_store.py`
- Create: `skills/keystone-linker/scripts/graph_runtime/query.py`
- Create: `skills/keystone-linker/scripts/graph_runtime/readiness.py`
- Modify: `skills/keystone-linker/scripts/graph_runtime/__init__.py`
- Create: `skills/keystone-linker/references/reference-index-runtime.md`
- Create: `skills/keystone-linker/tests/test_reference_index.py`
- Create: `skills/keystone-linker/tests/test_context_readiness.py`
- Modify only when required by accepted contracts: existing adapters/metadata/validator/reconciler tests and code
- Modify: R006 S03 work/progress/index and Context Map after acceptance

**Interfaces:**
- Consumes: installed Skill contracts from Task 3 and existing adapter/parser output.
- Produces: hidden Python API for docs/repository scan, external SQLite cache, freshness token, owner/ref lookup, optional typed subgraph, and validation scope evidence.

- [ ] **Step 1: Write failing owner/ref and freshness tests**

Cover unique owner, reverse refs, duplicate/dangling diagnostics, docs-only coverage, lazy repository coverage, path-set plus raw-byte digest invalidation, dirty/untracked files, worktree identity, corrupt-cache fail-soft, and source content treated as data.

- [ ] **Step 2: Run RED tests**

```bash
env PYTHONPATH=skills/keystone-linker/scripts python3 -m unittest \
  skills.keystone-linker.tests.test_reference_index \
  skills.keystone-linker.tests.test_context_readiness -v
```

Expected: imports or assertions fail because R006 runtime is absent.

- [ ] **Step 3: Implement minimal runtime**

Use SQLite through Python stdlib, a single-writer generation transaction, an external cache path supplied by the caller, and immutable result dataclasses. Do not add a PATH command or repository cache file.

- [ ] **Step 4: Add lazy typed-graph and recursion behavior**

Docs-only readiness returns no typed graph or transaction. Repository enrichment materializes typed edges only when requested. Serialized trace entries reject Reader→Linker→Reader recursion while allowing one bounded enrichment hop.

- [ ] **Step 5: Run Linker suites**

```bash
env PYTHONPATH=skills/keystone-linker/scripts python3 -m unittest discover -s skills/keystone-linker/tests -p 'test_*.py' -v
```

Expected: all existing and new tests pass.

- [ ] **Step 6: Commit**

```bash
git add skills/keystone-linker 00_docs/works/r006-reference-index-context-readiness 00_docs/key-context-map.md
git commit -m "feat: add internal Keystone reference index"
```

### Task 5: Cross-Skill Integration and Installation Verification

**Files:**
- Modify: `reinstall-local-keystone-skills.sh`
- Modify: `skills/keystone-author/tests/test_graph_finalization_package_e2e.py`
- Create: `skills/keystone-linker/tests/test_reference_index_integration.py`
- Create: `skills/keystone-reader/tests/test_reader_linker_readiness.py`
- Create if needed: `skills/keystone-reader/scripts/context_runtime/` narrow wire validator only
- Modify: README contract summary

**Interfaces:**
- Consumes: hidden runtime API and skill contracts.
- Produces: installed-package parity evidence and end-to-end Reader→Linker→Author/Coordinator flows without exposing commands.

- [ ] **Step 1: Write failing integration tests**

Cover first Reader docs scan, cached reuse, stale docs refresh, code request lazy repository scan, no-recursion fallback, Author invalidation, Coordinator fresh-context reuse, multi-agent cache serialization, and installed package layout.

- [ ] **Step 2: Run RED integration tests**

```bash
python3 -m unittest discover -s skills/keystone-reader/tests -p 'test_*.py' -v
env PYTHONPATH=skills/keystone-linker/scripts python3 -m unittest skills.keystone-linker.tests.test_reference_index_integration -v
```

Expected: missing integration surfaces fail.

- [ ] **Step 3: Implement package integration and atomic temp-install smoke**

Keep runtime internal. Verify in a temporary `CODEX_HOME`; do not modify the real installed skills during tests or this task.

- [ ] **Step 4: Run full verification**

```bash
python3 -m unittest skills.tests.test_r006_context_readiness_contracts -q
python3 -m unittest skills.tests.test_s03_runtime_contracts -q
env PYTHONPATH=skills/keystone-linker/scripts python3 -m unittest discover -s skills/keystone-linker/tests -p 'test_*.py' -q
python3 -m unittest discover -s skills/keystone-author/tests -p 'test_*.py' -q
python3 -m unittest discover -s skills/keystone-reader/tests -p 'test_*.py' -q
bash -n reinstall-local-keystone-skills.sh
git diff --check
```

Expected: all suites and syntax checks pass.

- [ ] **Step 5: Commit**

```bash
git add reinstall-local-keystone-skills.sh README.md skills 00_docs/works/r006-reference-index-context-readiness 00_docs/key-context-map.md
git commit -m "test: verify Keystone reference index integration"
```

### Task 6: R006 Acceptance Finalization

**Files:**
- Modify: R006 work orders, progress records, indexes
- Modify: `00_docs/works/00_key-index.md`
- Modify: `00_docs/key-context-map.md`

**Interfaces:**
- Consumes: all task commits, reviews, and final verification evidence.
- Produces: accepted R006 with no active step and explicit residual risks.

- [ ] **Step 1: Perform broad independent review**

Review standards, skill sources, runtime, tests, installer, and historical compatibility. Resolve every Critical/Important finding.

- [ ] **Step 2: Run fresh final verification**

Run the full Task 5 verification command set from a clean worktree and record exact counts.

- [ ] **Step 3: Finalize status sources**

Mark S01-S04 and R006 accepted only after Main acceptance. Ensure Context Map and root/round indexes agree on no active round and latest accepted R006.

- [ ] **Step 4: Verify state invariants**

```bash
rg -n "Active steps: \[S|R006.*active|current active round.*R006|work_status: (planned|in_progress)" 00_docs
git diff --check
git status --short
```

Expected: no stale active R006 state, no whitespace errors, clean status after final commit.

- [ ] **Step 5: Commit**

```bash
git add 00_docs
git commit -m "docs: finalize R006 reference index readiness"
```
