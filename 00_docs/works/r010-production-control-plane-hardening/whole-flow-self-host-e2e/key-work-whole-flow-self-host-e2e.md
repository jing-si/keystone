---
doc_type: work_order
created_at: "2026-08-07"
document_lifecycle: active
approval: {state: pending}
work_status: planned
key:
  id: key.work.whole-flow-self-host-e2e.order
  refs:
    - key.doc.work
    - key.topic.work-sequence
    - key.topic.work-recovery
    - key.topic.finalization
    - key.topic.change-set
    - key.topic.integration-verification
    - key.role.coordinator
    - key.topic.verification
  relations:
    depends_on:
      - target: key.work.production-control-plane-hardening.order
      - target: key.work.authority-chain-snapshot-closure.order
      - target: key.work.graph-transaction-source-correctness.order
      - target: key.work.work-state-runtime.order
      - target: key.work.agent-behavior-evaluation.order
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
  - dependency: key.work.authority-chain-snapshot-closure.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval:
        state: accepted
    optional: false
  - dependency: key.work.graph-transaction-source-correctness.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval:
        state: accepted
    optional: false
  - dependency: key.work.work-state-runtime.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval:
        state: accepted
    optional: false
  - dependency: key.work.agent-behavior-evaluation.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval:
        state: accepted
    optional: false
---

# Whole-Flow Self-Host E2E 작업서 및 Change Set

<!-- key: id=key.work.whole-flow-self-host-e2e.order.goal refs=key.section.goal key.topic.integration-verification -->
## Goal

R010/S01-S05의 correctness, phase authority, package-owned classification, shared Work State Runtime과
actual agent evidence를 실제 Keystone source를 변경하는 하나의 isolated whole-flow로 통합한다.
Reader 복구부터 post-acceptance finalization과 새 Reader terminal 재진입까지 정상 흐름과 열거된
adversarial 흐름을 actual source state에서 검증한다.

<!-- key: id=key.work.whole-flow-self-host-e2e.order.improvements refs=key.topic.work-sequence key.topic.verification -->
## 개선 항목

| ID | 개선 항목 | 구현 순서 | 핵심 근거 |
|---|---|---|---|
| PC85-11 | R010 whole-flow self-host E2E | 1 | actual source의 recovery→implementation→acceptance→terminal 재진입 |

<!-- key: id=key.work.whole-flow-self-host-e2e.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- Temporary clean checkout의 Reader→Coordinator→worker→Linker→Author workflow
- Fixture-local Main acceptance event와 post-acceptance finalization
- S02 complete phase snapshot, S03 classification/transaction/source와 S04 work-state integration
- S05 actual agent evidence consumption
- Success flow와 scope/authority/generation/acceptance/evidence adversarial flow
- New Reader terminal recovery와 deterministic result comparison

Exclude:

- Live R010 Main acceptance와 authoritative repository finalization: R010/S07
- Independent platform CI, RC version transition와 production publication: R010/S07
- 새 feature/relation/skill, external pilot와 performance/fuzz/fault-injection program

<!-- key: id=key.work.whole-flow-self-host-e2e.order.source-context refs=key.section.source-context key.topic.integration-verification -->
## Source Context

- R010/S01-S05 Work Order, Progress와 accepted verification evidence
- Package-owned Coordinator/Linker/Author runners와 Work State Runtime
- Actual agent eval runner와 strict external evidence
- `scripts/run_release_gate.sh`와 installer harness
- `00_docs/standards/01_key-project-standard.md`
- `00_docs/standards/skills/reader/key-standard-reader.md`
- `00_docs/standards/skills/coordinator/key-standard-coordinator.md`
- `00_docs/standards/skills/author/key-standard-author.md`
- `00_docs/convention.md`

<!-- key: id=key.work.whole-flow-self-host-e2e.order.pc85-11 refs=key.topic.integration-verification key.topic.finalization -->
## PC85-11 R010 whole-flow self-host E2E

Implementation:

1. Reader가 active Work를 복구하고 Coordinator가 complete assignment snapshot을 생성한다.
2. Worker가 bounded runtime source를 변경하고 Coordinator가 worker phase actual diff를 검증한다.
3. Package-owned Linker가 graph classification/transaction을 실행하고 Author가 document/metadata를
   pre-acceptance phase에서 동기화한다.
4. Fixture-local Main acceptance event 뒤 Author가 schema-v5 finalization을 수행하고 Coordinator가
   post-acceptance phase를 검증한다.
5. 새 Reader session이 terminal state를 복구하고 Work State Runtime 결과와 비교한다.
6. 모든 phase snapshot/delta, acceptance ref, eval evidence와 derived work state를 current fixture
   generation에 결속한다.

Required failure scenarios:

1. Worker가 scope 밖 파일을 변경한다.
2. Author가 code를 변경한다.
3. Graph classification을 위조하거나 delta를 누락한다.
4. Optional patch를 confirm/baseline 없이 적용한다.
5. Phase 사이에 unattributed file change가 발생한다.
6. Acceptance ref가 phase/finalization 사이에서 다르다.
7. Finalization 뒤 active/planned/blocked Work가 남는다.
8. Source generation이 classification/validation 사이에 바뀐다.
9. Agent evidence가 stale/forged/incomplete다.
10. Installer apply/parity가 실패하고 rollback이 필요하다.

Verification:

- Success flow의 generation parent chain과 acceptance ref가 연속적이다.
- Terminal recovery는 `active_round: none`, empty active Steps와 derived latest accepted R010을
  반환한다.
- 각 failure fixture는 의도한 stable diagnostic에서 멈추고 이후 phase를 실행하지 않는다.
- Temporary fixture가 current repository, external evidence와 reviewer key를 오염시키지 않는다.

Done when: actual Keystone source가 clean run에서 recovery, implementation, closure, fixture-local
acceptance, finalization과 terminal 재진입을 완주하고 모든 failure scenario를 fail-closed로 차단한다.

<!-- key: id=key.work.whole-flow-self-host-e2e.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: 모든 subsystem evidence를 one-generation actual whole-flow에 결속한다.
- Required candidates: Self-host harness, isolated fixture checkout, Coordinator/Linker/Author/Reader
  adapters, agent evidence consumer와 success/adversarial corpus
- Conditional candidates: Installer rollback은 whole-flow source generation을 변경하는 범위만
  포함한다.
- Excluded: S07 live release/finalization, external pilot와 new product feature
- Acceptance owner: Main
- Graph handling: fixture source delta를 package-owned Linker가 분류하고 actual owner authority를
  E2E가 검증한다.

<!-- key: id=key.work.whole-flow-self-host-e2e.order.completion refs=key.topic.acceptance key.topic.integration-verification -->
## Completion Criteria

Work Order는 criterion statement만 소유하고 현재 state/evidence는 S06 Progress가 관리한다.

<!-- key: id=key.acceptance.whole-flow.normal -->
- `R010-S06-CC-01` Clean isolated fixture에서 Reader→Coordinator→worker→Linker→Author→fixture-local
  Main acceptance→finalization→new Reader flow가 완주한다.
<!-- key: id=key.acceptance.whole-flow.actor-attribution -->
- `R010-S06-CC-02` Worker, Author, repository owner와 finalization delta가 각 phase와 actor authority에
  정확히 귀속된다.
<!-- key: id=key.acceptance.whole-flow.phase-continuity -->
- `R010-S06-CC-03` Phase baseline/result digest, source generation과 acceptance ref chain이 연속적이다.
<!-- key: id=key.acceptance.whole-flow.subsystem-binding -->
- `R010-S06-CC-04` Package-owned classification, optional patch와 Work State Runtime evidence가 같은
  fixture subject에 결속된다.
<!-- key: id=key.acceptance.whole-flow.agent-evidence-binding -->
- `R010-S06-CC-05` Actual agent evidence가 whole-flow current commit/package/generation과 일치한다.
<!-- key: id=key.acceptance.whole-flow.adversarial -->
- `R010-S06-CC-06` 열거된 10개 adversarial scenario가 stable diagnostic으로 fail-closed다.
<!-- key: id=key.acceptance.whole-flow.terminal-parity -->
- `R010-S06-CC-07` Terminal Reader recovery와 Author/Coordinator/release-facing work state가 동일하다.
<!-- key: id=key.acceptance.whole-flow.prerequisite-verification -->
- `R010-S06-CC-08` S01-S05 Work가 `complete + accepted`이고 S06 focused/cross-skill verification이
  통과한다.

<!-- key: id=key.work.whole-flow-self-host-e2e.order.verification refs=key.topic.verification key.topic.integration-verification -->
## Verification

- Temporary clean checkout whole-flow success corpus
- Phase/actor/generation/acceptance-ref continuity assertions
- Ten required adversarial fixtures and stable diagnostics
- Actual agent evidence consumption and terminal Work State parity
- Installer forced rollback isolation, repository full graph validation와 `git diff --check`

<!-- key: id=key.work.whole-flow-self-host-e2e.order.expected-output refs=key.topic.verification key.topic.work-recovery -->
## Expected Output

- Isolated R010 whole-flow self-host harness와 actual-source success corpus
- Ten adversarial fixtures, stable diagnostics와 phase evidence archive
- Terminal Reader/work-state parity evidence와 Progress criterion mapping

<!-- key: id=key.work.whole-flow-self-host-e2e.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. S01-S05 required evidence가 complete/accepted가 아니거나 generation을 재현할 수 없다.
2. Fixture-local acceptance가 live Main acceptance 또는 authoritative R010 state를 변경한다.
3. External agent/reviewer evidence를 위조하거나 credential/key를 repository에 저장해야 한다.
4. Whole-flow success가 synthetic manifest만으로 actual source phase를 대체한다.
5. Stable release, publication, external pilot 또는 새 feature가 completion 필수가 된다.
