---
doc_type: work_order
created_at: "2026-08-07"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-08", accepted_by: main}
work_status: complete
key:
  id: key.work.authority-chain-snapshot-closure.order
  refs:
    - key.doc.work
    - key.topic.work-sequence
    - key.topic.work-recovery
    - key.topic.artifact-graph
    - key.topic.change-set
    - key.role.coordinator
    - key.role.linker
    - key.topic.verification
  relations:
    depends_on:
      - target: key.work.production-control-plane-hardening.order
work_gates:
  - dependency: key.work.production-control-plane-hardening.order
    applies_to:
      steps: [S02]
      work_completion: false
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
  - dependency: key.work.production-control-plane-hardening.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
---

# Authority Chain and Snapshot Closure 작업서 및 Change Set

<!-- key: id=key.work.authority-chain-snapshot-closure.order.goal refs=key.section.goal key.role.coordinator -->
## Goal

Assignment baseline의 전체 path set을 독립 재현 가능한 snapshot policy에 결속하고, worker 이후
Author·repository owner·finalization 변경을 phase별 source generation과 actor authority로 분리해
Coordinator actual-state closure를 manifest linter가 아닌 authority-chain verifier로 만든다.

<!-- key: id=key.work.authority-chain-snapshot-closure.order.improvements refs=key.topic.work-sequence key.topic.verification -->
## 개선 항목

| ID | 개선 항목 | 구현 순서 | 핵심 근거 |
|---|---|---|---|
| PC85-02 | Assignment baseline snapshot completeness | 1 | complete path/type/raw-byte digest와 policy binding |
| PC85-01 | Phase-separated actual-state closure | 2 | phase parent digest와 actor별 delta/scope |

<!-- key: id=key.work.authority-chain-snapshot-closure.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- Package-owned T0 capture entrypoint, normalized include/exclude policy, discovered existing path set,
  path type와 raw-byte digest
- Existing `regular_file | directory | symlink` entries와 별도 assignment-owned
  `expected_absences`, count/path-set digest와 `complete` evidence
- Assignment, worker, pre-acceptance closure와 post-acceptance phase snapshot chain
- Worker/Author/repository owner delta, scope와 source-write authority 검증
- Configured document root와 Author document-surface authority의 independent binding
- Assignment/worker/pre/post package-owned phase-capture evidence와 replay 방지 binding
- External pinned Coordinator/Main keys, HMAC host receipts와 pre-capture -> acceptance-event ->
  post-capture evidence chain
- Existing closure compatibility, strict schema와 stable diagnostic tests

Exclude:

- Package-owned Linker classification, graph transaction과 canonical mutation policy: R010/S03
- Derived global work state와 shared runtime: R010/S04
- Actual agent execution evidence: R010/S05
- Whole-flow integration: R010/S06
- Main acceptance 부여와 terminal finalization: R010/S07
- 암묵적인 generated/cache/IDE ignore list와 repository-wide cleanup

<!-- key: id=key.work.authority-chain-snapshot-closure.order.source-context refs=key.section.source-context key.topic.artifact-graph -->
## Source Context

- R010/S01 Work Order, Progress와 Coordinator closure v2 implementation evidence
- `00_docs/standards/skills/coordinator/key-standard-coordinator.md`
- `00_docs/standards/skills/linker/key-standard-linker.md`
- `00_docs/standards/artifacts/key-standard-artifact-graph.md`
- `00_docs/standards/subagents/key-standard-subagents.md`
- `00_docs/convention.md`

<!-- key: id=key.work.authority-chain-snapshot-closure.order.pc85-02 refs=key.role.coordinator key.topic.verification -->
## PC85-02 Assignment baseline snapshot completeness

Gate boundary:

- S01 start gate 충족 전에는 read-only analysis와 이 문서 안의 RED case matrix/fixture design만
  허용한다.
- Runtime/test/code/config/schema source write, Work/Step의 `in_progress` 전이와 canonical schema
  commitment는 금지한다.
- 이 계획은 gate 전 implementation 또는 `early_work`가 발생했다는 근거가 아니다.

Implementation:

1. Package-owned `scripts/capture_assignment_snapshot.py`가 worker write 전 T0 source generation을
   capture하고 diagnostic envelope schema v1 안에 canonical snapshot schema v3를 반환한다.
   Package-owned invocation은 operational T0 authority boundary다. Immutable assignment bytes가
   exact captured snapshot을 embed하고 assignment raw-byte digest가 그 bytes를 결속한다.
2. Snapshot의 existing entries는 `regular_file | directory | symlink`만 허용하고, 존재하지
   않아야 할 assignment-owned 경로는 별도 `expected_absences` 집합으로 기록한다.
3. `discovered_path_count`, `expected_absence_count`, 각 집합의 canonical path digest,
   `complete`와 truncation/budget 상태를 policy에 결속한다.
4. Capture 전후에 같은 policy로 path set을 독립 discovery하고, 각 경로를 no-follow `lstat`로
   식별한다. Regular file은 no-follow `open` 뒤 capture 전후 `fstat`의
   `(size, mtime, ctime, inode)`가 `lstat` identity와 일치해야 하며 drift 시 bounded retry 후
   fail-closed한다.
5. Directory와 symlink도 capture 전후 no-follow identity를 비교하고, symlink target과 regular
   file executable-bit를 digest-bearing entry에 기록한다.
6. Unicode-normalized case-fold key 충돌을 host filesystem의 case sensitivity와 무관하게
   거절하고, path normalization과 file↔symlink↔directory replacement를 별도 delta로 다룬다.
7. Baseline과 모든 phase result가 같은 policy를 사용하게 하고 policy 변경은 새 assignment
   digest를 요구한다.
8. Runtime-generated path는 default ignore가 아니라 assignment-owned exclusion reason으로만
   제외한다.
9. Closure 시점에 host가 제공한 self-consistent path 목록은 package-owned T0 capture completeness를
   대신할 수 없다.

Verification:

- Existing path omission, hidden new path와 deleted file이 actual delta에서 사라지지 않는다.
- Symlink/regular replacement, policy mutation, truncated scan과 path-set count mismatch는 실패한다.
- Expected absence의 생성/누락, capture 전후 path-set drift와 identity drift는 bounded retry가
  소진되면 실패한다.
- Symlink target, executable-bit와 Unicode-normalized case-fold collision 변화는 숨겨지지 않는다.
- 동일 generation을 반복 capture하면 path order와 digest가 동일하다.

Done when: host-provided baseline 목록을 독립 discovery로 재현하지 못하면 authority-bearing
assignment와 closure가 모두 실패한다.

<!-- key: id=key.work.authority-chain-snapshot-closure.order.pc85-01 refs=key.role.coordinator key.topic.verification -->
## PC85-01 Coordinator phase-separated actual-state closure

Implementation:

1. `assignment_phase`, `worker_phase`, `pre_acceptance_closure_phase`, `post_acceptance_phase`를
   explicit closure chain으로 정의한다.
2. 각 phase는 baseline/result snapshot digest, actor, changed paths, artifact deltas와 authority를
   갖고 이전 phase result를 자기 baseline parent로 참조한다.
3. Worker scope, Author document surface, repository owner surface와 Linker source-write-free를
   phase별로 검증한다.
4. 추가·수정·삭제·type replacement가 정확히 한 phase에 귀속되는지 확인하고 inter-phase
   unrecorded generation을 차단한다.
5. Finalization phase의 acceptance ref와 event order를 검증하고 기존 closure wire compatibility를
   명시한다. Coordinator capture와 Main acceptance는 서로 다른 external pinned key를 사용하고,
   acceptance event는 exact assignment/context/policy, pre snapshot, target/ref/Steps에 결속한다.
   Main event runner는 같은 snapshot policy/expected absences로 live repository를 재캡처하고 exact
   pre snapshot과 일치할 때만 event를 발행한다.
   신규 authority-bearing assignment/manifest는 schema v3로 발행하고 schema v1/v2는
   historical diagnostic-only/non-authoritative로 보존한다. Diagnostic envelope schema v1,
   SnapshotPolicy/RepositorySnapshot v3, Linker transaction v2와 Author finalization v5는 독립
   version domain이다.

Verification:

- Worker code only, worker+Author sync, worker+post-acceptance finalization은 통과한다.
- Worker document write, Author code write, unattributed change와 parent digest mismatch는 실패한다.
- Configured document root가 repository root이면 모든 write actor scope를 fail-closed로 거부한다.
- Pre snapshot 이후 Main event 전에 발생한 finalization 또는 다른 write는 live recapture mismatch로
  실패한다.
- Acceptance 이전 finalization과 다른 acceptance ref는 실패한다.
- 임의 producer 문자열, 잘못된 HMAC/key fingerprint, evidence predecessor replay와 같은
  Coordinator/Main key 사용은 실패한다.

Done when: 하나의 final diff가 아니라 actual source bytes로 모든 delta를 정확히 한 phase와 actor에
귀속할 수 있다.

<!-- key: id=key.work.authority-chain-snapshot-closure.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: closure success를 complete snapshot과 actor/phase provenance에 결속한다.
- Required candidates: Coordinator model/parser/validator/contract, package-owned T0 snapshot capture
  entrypoint/filesystem adapter, strict schema-v3 wire와 adversarial fixtures
- Conditional candidates: Author finalization runner binding과 release gate는 phase envelope가 바뀌는
  범위만 검토한다.
- Excluded: S03 package-owned classification/transaction과 S04-S07 owned runtime, unrelated refactor와
  public release
- Acceptance owner: Main
- Graph handling: document/artifact delta를 Linker가 분류하고 multi-surface mutation이 필요할 때만
  owner-attested transaction을 사용한다.

<!-- key: id=key.work.authority-chain-snapshot-closure.order.completion refs=key.topic.acceptance key.topic.integration-verification -->
## Completion Criteria

Work Order는 criterion statement만 소유하고 현재 state/evidence는 S02 Progress가 관리한다.

<!-- key: id=key.acceptance.authority-chain.complete-snapshot -->
- `R010-S02-CC-01` Snapshot policy, 전체 discovered path set, path type와 raw-byte digest가
  package-owned T0 capture와 assignment bytes에 결속되고 count/path-set digest/`complete` evidence가
  일치한다.
<!-- key: id=key.acceptance.authority-chain.hidden-change-detection -->
- `R010-S02-CC-02` Omission, hidden path, deletion, type replacement와 truncated scan이
  fail-closed다.
<!-- key: id=key.acceptance.authority-chain.expected-absences -->
- `R010-S02-CC-03` Existing entries는 `regular_file | directory | symlink`로 한정되고 같은
  canonical RepositorySnapshot v3 안의 assignment-owned `expected_absences`
  array/count/path-set digest/`complete` evidence가 pre/post 부재 검증과 일치한다.
<!-- key: id=key.acceptance.authority-chain.stable-capture -->
- `R010-S02-CC-04` Capture 전후 path set 및 no-follow `lstat/open/fstat` identity
  `(size, mtime, ctime, inode)`가 일치하거나 bounded retry 뒤 fail-closed한다.
<!-- key: id=key.acceptance.authority-chain.portable-path-identity -->
- `R010-S02-CC-05` Symlink target, executable-bit와 Unicode-normalized case-fold collision이
  digest-bearing evidence로 검증된다.
<!-- key: id=key.acceptance.authority-chain.phase-parent-chain -->
- `R010-S02-CC-06` 각 phase baseline digest가 이전 phase result digest와 일치하고, capture receipt가
  preceding evidence raw digest와 non-circular assignment authority-core digest에 결속된다.
<!-- key: id=key.acceptance.authority-chain.actor-delta-scope -->
- `R010-S02-CC-07` Worker, Author, repository owner와 finalization delta가 actor authority 안에 있고,
  Worker/repository-owner edit scope는 independently configured document root와 겹치지 않는다.
<!-- key: id=key.acceptance.authority-chain.unattributed-ordering -->
- `R010-S02-CC-08` Inter-phase unattributed mutation과 acceptance 이전 finalization이 실패한다.
  Main acceptance event는 distinct pinned key, exact pre-acceptance subject와 raw evidence predecessor
  chain에 결속된다.
<!-- key: id=key.acceptance.authority-chain.closure-compatibility -->
- `R010-S02-CC-09` 신규 authority-bearing closure는 Coordinator schema v3만 사용하고 v1/v2는
  historical diagnostic-only/non-authoritative compatibility로 보존한다. Diagnostic envelope v1,
  SnapshotPolicy/RepositorySnapshot v3, Linker transaction v2와 Author finalization v5의 version
  domain 및 strict unknown-field policy가 regression으로 고정된다.
<!-- key: id=key.acceptance.authority-chain.prerequisite-verification -->
- `R010-S02-CC-10` S01 Work가 `complete + accepted`이고 S02 focused/package/cross-skill
  verification이 통과한다.

<!-- key: id=key.work.authority-chain-snapshot-closure.order.verification refs=key.topic.verification -->
## Verification

- Snapshot omission/type/symlink/policy/truncation, expected-absence, TOCTOU와 Unicode
  case-fold collision adversarial matrix
- Phase success·scope violation·unattributed change·digest/timing mismatch matrix
- Coordinator full package suite와 affected cross-skill tests
- Cross-skill actual-source fixture, repository full graph validation와 `git diff --check`

<!-- key: id=key.work.authority-chain-snapshot-closure.order.expected-output refs=key.topic.verification key.topic.work-recovery -->
## Expected Output

- Complete SnapshotPolicy/RepositorySnapshot v3 value object, package-owned T0 capture entrypoint와
  validation envelope
- Phase-separated closure chain, parser/validator와 stable diagnostics
- Contract/reference updates, adversarial unit/integration fixtures와 Progress evidence

<!-- key: id=key.work.authority-chain-snapshot-closure.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. Public closure wire compatibility를 보존할 version/migration 경로가 없다.
2. Complete path set을 host 자기신고가 아닌 filesystem discovery로 검증할 수 없다.
3. Validator가 source write, graph mutation 또는 Main acceptance 권한을 가져야 한다.
4. R010/S01과 같은 path를 다른 baseline에서 수정해 기존 변경을 덮어써야 한다.
5. External dependency, repository-wide ignore migration 또는 unrelated refactor가 필수가 된다.
