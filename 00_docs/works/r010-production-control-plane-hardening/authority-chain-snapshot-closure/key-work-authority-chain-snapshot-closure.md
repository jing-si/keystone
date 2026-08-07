---
doc_type: work_order
created_at: "2026-08-07"
document_lifecycle: active
approval: {state: pending}
work_status: planned
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
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval:
        state: accepted
    optional: false
---

# Authority Chain and Snapshot Closure 작업서 및 Change Set

<!-- key: id=key.work.authority-chain-snapshot-closure.order.goal refs=key.section.goal key.role.coordinator -->
## Goal

Assignment baseline의 전체 path set을 독립 재현 가능한 snapshot policy에 결속하고, worker 이후
Author·repository owner·finalization 변경을 phase별 source generation과 actor authority로 분리한다.
`graph_sync: not_applicable`도 같은 delta와 source generation을 읽은 package-owned Linker 판정으로
닫아 Coordinator actual-state closure를 manifest linter가 아닌 authority-chain verifier로 만든다.

<!-- key: id=key.work.authority-chain-snapshot-closure.order.improvements refs=key.topic.work-sequence key.topic.verification -->
## 개선 항목

| ID | 개선 항목 | 구현 순서 | 핵심 근거 |
|---|---|---|---|
| PC85-02 | Assignment baseline snapshot completeness | 1 | complete path/type/raw-byte digest와 policy binding |
| PC85-01 | Phase-separated actual-state closure | 2 | phase parent digest와 actor별 delta/scope |
| PC85-04 | Package-owned Linker classification | 3 | 동일 delta/source에서 canonical runner 재실행 |

<!-- key: id=key.work.authority-chain-snapshot-closure.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- Normalized include/exclude policy, discovered path set, path type와 raw-byte digest
- `regular_file | directory | symlink | absent`, count/path-set digest와 `complete` evidence
- Assignment, worker, pre-acceptance closure와 post-acceptance phase snapshot chain
- Worker/Author/repository owner delta, scope와 source-write authority 검증
- Package-owned Linker classification runner와 Coordinator evidence binding
- Existing closure compatibility, strict schema와 stable diagnostic tests

Exclude:

- Graph transaction optional patch와 canonical mutation policy: R010/S03
- Derived global work state와 agent execution evidence: R010/S04
- Main acceptance 부여, source write와 terminal finalization: R010/S05
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

Implementation:

1. Assignment digest에 normalized include/exclude policy, 전체 discovered path set, path type와
   raw-byte digest를 결속한다.
2. `discovered_path_count`, `path_set_digest`, `complete`와 truncation/budget 상태를 strict wire로
   고정한다.
3. Symlink target, path normalization과 file↔symlink↔directory replacement를 별도 delta로 다룬다.
4. Baseline과 모든 phase result가 같은 policy를 사용하게 하고 policy 변경은 새 assignment
   digest를 요구한다.
5. Runtime-generated path는 default ignore가 아니라 assignment-owned exclusion reason으로만
   제외한다.

Verification:

- Existing path omission, hidden new path와 deleted file이 actual delta에서 사라지지 않는다.
- Symlink/regular replacement, policy mutation, truncated scan과 path-set count mismatch는 실패한다.
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
   명시한다.

Verification:

- Worker code only, worker+Author sync, worker+post-acceptance finalization은 통과한다.
- Worker document write, Author code write, unattributed change와 parent digest mismatch는 실패한다.
- Acceptance 이전 finalization과 다른 acceptance ref는 실패한다.

Done when: 하나의 final diff가 아니라 actual source bytes로 모든 delta를 정확히 한 phase와 actor에
귀속할 수 있다.

<!-- key: id=key.work.authority-chain-snapshot-closure.order.pc85-04 refs=key.role.linker key.role.coordinator -->
## PC85-04 Package-owned Linker classification

Implementation:

1. Linker package runner가 `required | not_applicable | deferred`, delta-set digest, source-generation
   digest, inspected sources, reason codes와 diagnostics를 strict envelope로 반환한다.
2. Canonical input에는 모든 artifact/document delta, changed locator와 baseline digest를 포함한다.
3. Coordinator는 package-owned runner identity를 고정하고 output digest와 current delta/source
   generation을 직접 비교한다.
4. Graph-relevant locator의 exclusion reason과 inspected source evidence가 대응하지 않으면
   `not_applicable`을 거절한다.
5. Classification과 후속 transaction/validation 사이 source generation drift를 차단한다.

Verification:

- Hand-made classification, stale generation, omitted delta와 substituted runner는 실패한다.
- 동일 delta/source에서 canonical runner가 만든 `not_applicable`은 통과한다.
- `required` 결과는 같은 delta set을 사용하는 graph transaction evidence로 이어진다.

Done when: `not_applicable`도 required graph sync와 같은 package authority·delta completeness·source
generation 경계를 가진다.

<!-- key: id=key.work.authority-chain-snapshot-closure.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: closure success를 complete snapshot, actor/phase provenance와 package-owned graph 판정에
  결속한다.
- Required candidates: Coordinator model/parser/validator/contract, Linker classification runner,
  snapshot filesystem adapter, strict wire와 adversarial fixtures
- Conditional candidates: Author finalization runner binding과 release gate는 phase envelope가 바뀌는
  범위만 검토한다.
- Excluded: S03/S04/S05 owned runtime, unrelated refactor와 public release
- Acceptance owner: Main
- Graph handling: document/artifact delta를 Linker가 분류하고 multi-surface mutation이 필요할 때만
  owner-attested transaction을 사용한다.

<!-- key: id=key.work.authority-chain-snapshot-closure.order.completion refs=key.topic.acceptance key.topic.integration-verification -->
## Completion Criteria

- [ ] Snapshot policy, 전체 discovered path set, path type와 raw-byte digest가 assignment에 결속된다.
- [ ] Omission, hidden path, deletion, type replacement와 truncated scan이 fail-closed다.
- [ ] 각 phase baseline digest가 이전 phase result digest와 일치한다.
- [ ] Worker, Author, repository owner와 finalization delta가 actor authority 안에 있다.
- [ ] Inter-phase unattributed mutation과 acceptance 이전 finalization이 실패한다.
- [ ] `not_applicable`도 package-owned Linker가 동일 delta/source에서 재판정한다.
- [ ] Existing closure compatibility와 strict unknown-field policy가 regression으로 보존된다.
- [ ] S01 Work가 `complete + accepted`이고 S02 focused/package/cross-skill verification이 통과한다.

<!-- key: id=key.work.authority-chain-snapshot-closure.order.verification refs=key.topic.verification -->
## Verification

- Snapshot omission/type/symlink/policy/truncation adversarial matrix
- Phase success·scope violation·unattributed change·digest/timing mismatch matrix
- Classification forged/stale/omitted/substituted runner tests
- Coordinator and Linker full package suites
- Cross-skill actual-source fixture, repository full graph validation와 `git diff --check`

<!-- key: id=key.work.authority-chain-snapshot-closure.order.expected-output refs=key.topic.verification key.topic.work-recovery -->
## Expected Output

- Complete snapshot policy/value object, capture adapter와 validation envelope
- Phase-separated closure chain, parser/validator와 stable diagnostics
- Package-owned Linker classification runner와 Coordinator binding
- Contract/reference updates, adversarial unit/integration fixtures와 Progress evidence

<!-- key: id=key.work.authority-chain-snapshot-closure.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. Public closure wire compatibility를 보존할 version/migration 경로가 없다.
2. Complete path set을 host 자기신고가 아닌 filesystem discovery로 검증할 수 없다.
3. Validator가 source write, graph mutation 또는 Main acceptance 권한을 가져야 한다.
4. R010/S01과 같은 path를 다른 baseline에서 수정해 기존 변경을 덮어써야 한다.
5. External dependency, repository-wide ignore migration 또는 unrelated refactor가 필수가 된다.
