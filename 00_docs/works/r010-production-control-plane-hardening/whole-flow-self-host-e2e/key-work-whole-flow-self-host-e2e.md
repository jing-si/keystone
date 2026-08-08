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
  - id: r010-s06-start-production-control-plane-hardening
    dependency: key.work.production-control-plane-hardening.order
    applies_to:
      steps: [S06]
      work_completion: false
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
  - id: r010-s06-completion-production-control-plane-hardening
    dependency: key.work.production-control-plane-hardening.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
  - id: r010-s06-start-authority-chain-snapshot-closure
    dependency: key.work.authority-chain-snapshot-closure.order
    applies_to:
      steps: [S06]
      work_completion: false
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
  - id: r010-s06-completion-authority-chain-snapshot-closure
    dependency: key.work.authority-chain-snapshot-closure.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
  - id: r010-s06-start-graph-transaction-source-correctness
    dependency: key.work.graph-transaction-source-correctness.order
    applies_to:
      steps: [S06]
      work_completion: false
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
  - id: r010-s06-completion-graph-transaction-source-correctness
    dependency: key.work.graph-transaction-source-correctness.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
  - id: r010-s06-start-work-state-runtime
    dependency: key.work.work-state-runtime.order
    applies_to:
      steps: [S06]
      work_completion: false
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
  - id: r010-s06-completion-work-state-runtime
    dependency: key.work.work-state-runtime.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
  - id: r010-s06-start-agent-behavior-evaluation
    dependency: key.work.agent-behavior-evaluation.order
    applies_to:
      steps: [S06]
      work_completion: false
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
  - id: r010-s06-completion-agent-behavior-evaluation
    dependency: key.work.agent-behavior-evaluation.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
---

# Whole-Flow Self-Host E2E 작업서 및 Change Set

<!-- key: id=key.work.whole-flow-self-host-e2e.order.goal refs=key.section.goal key.topic.integration-verification -->
## Goal

R010/S01-S05의 correctness, phase authority, package-owned classification, shared Work State Runtime과
actual agent evidence를 실제 Keystone runtime/source를 변경하는 하나의 isolated whole-flow로
통합한다. Temporary checkout의 별도 fixture document root와 dedicated fixture Round에서 Reader
복구부터 post-acceptance finalization과 새 Reader terminal 재진입까지 정상 흐름과 열거된
adversarial 흐름을 검증하며, live R010 terminal closure는 S07에 남긴다.

<!-- key: id=key.work.whole-flow-self-host-e2e.order.improvements refs=key.topic.work-sequence key.topic.verification -->
## 개선 항목

| ID | 개선 항목 | 구현 순서 | 핵심 근거 |
|---|---|---|---|
| PC85-11 | R010 whole-flow self-host E2E | 1 | actual source의 recovery→implementation→acceptance→terminal 재진입 |

<!-- key: id=key.work.whole-flow-self-host-e2e.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- Temporary clean checkout의 Reader→Coordinator→worker→Linker→Author workflow
- Live R010 works tree와 discovery scope가 분리된 dedicated fixture document root/Round
- Fixture-local Main acceptance event와 post-acceptance finalization
- S02 complete phase snapshot, S03 classification/transaction/source와 S04 work-state integration
- S05 actual agent evidence consumption
- Success flow와 scope/authority/generation/acceptance/evidence adversarial flow
- S01-S05 finalization closure evidence의 actual-source preflight
- 일곱 targeted crash/resume fixture와 idempotent replay/new-attempt 판정
- New Reader terminal recovery와 deterministic result comparison

Exclude:

- Live R010 Main acceptance와 authoritative repository finalization: R010/S07
- Independent platform CI, RC version transition와 production publication: R010/S07
- 새 feature/relation/skill, external pilot와 performance/fuzz/fault-injection program

<!-- key: id=key.work.whole-flow-self-host-e2e.order.source-context refs=key.section.source-context key.topic.integration-verification -->
## Source Context

- R010/S01-S05 Work Order, Progress와 accepted/finalized verification evidence
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

1. Temporary clean checkout에서 actual Keystone standards/runtime/source를 사용하는 별도 fixture
   document root와 valid dedicated fixture Round를 만든다. Live R010/S07은 fixture Work State
   discovery scope에 포함하지 않고 원본 bytes가 바뀌지 않았음을 전후 digest로 검증한다.
2. Reader가 fixture active Work를 복구하고 Coordinator가 complete assignment snapshot을 생성한다.
3. Worker가 bounded runtime source를 변경하고 Coordinator가 worker phase actual diff를 검증한다.
4. Package-owned Linker가 graph classification/transaction을 실행하고 Author가 document/metadata를
   pre-acceptance phase에서 동기화한다.
5. Fixture-local Main acceptance event 뒤 Author가 schema-v5 finalization을 수행하고 Coordinator가
   post-acceptance phase를 검증한다.
6. 새 Reader session이 fixture terminal state를 복구하고 Work State Runtime 결과와 비교한다.
7. 모든 phase snapshot/delta, acceptance ref, eval evidence와 derived work state를 current fixture
   generation에 결속한다.

Pre-gate policy:

- Required Step-start gate가 waiting인 동안 read-only orientation, evidence inspection과 source write
  없는 RED scenario 설계만 허용한다.
- Repository source write, `work_status: in_progress` 전이, schema/authority commitment와 acceptance
  주장은 금지한다. 이 정책은 실행된 `early_work`를 주장하거나 S06을 활성화하지 않는다.
- S01-S05 각각의 finalization이 `complete`이거나 Main이 수락한 `waived`이고, 해당 Work acceptance
  ref, finalization manifest/envelope digest와 package-owned Author runner pass가 결속된 뒤에만 S06
  implement assignment를 시작한다. Waiver에는 reason과 follow-up이 모두 필요하다.

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

Targeted crash/resume scenarios:

1. Worker가 source write/report 전에 종료되고 baseline/current digest와 no-delta가 일치하면 같은
   assignment를 resume할 수 있다. Source write 뒤 report 전에 종료됐다면 기존 write를 재적용하지
   않고 actual delta를 보존한 새 closure attempt가 필요하다.
2. Author document/metadata sync 중단은 마지막 owner-attested applied digest와 current bytes가
   일치할 때만 같은 attempt에서 남은 surface를 resume하고, 불일치하면 새 sync attempt를 만든다.
3. Partial graph patch는 transaction이 `partially_applied`이고 applied/resulting digest가 일치할 때
   같은 transaction을 resume한다. `conflicted | failed | stale_baseline`이면 preserved history를 가진
   새 Linker transaction attempt가 필요하다.
4. Main acceptance 뒤 finalization 전에 종료되면 같은 acceptance ref로 finalization을 resume하며
   새 acceptance event를 만들지 않는다.
5. Partial finalization은 source generation과 manifest checkpoint가 일치할 때 같은 acceptance ref로
   resume하고, source drift가 있으면 새 validation attempt를 만들되 acceptance는 보존한다.
6. External evidence timeout/retry는 실패 attempt를 보존하고 fresh invocation/time/identity를 가진
   새 evidence attempt를 요구하며 stale timeout result를 성공 evidence로 재사용하지 않는다.
7. Duplicate Coordinator replay는 assignment/closure/envelope digest가 같으면 mutation 없는
   idempotent result를 반환한다. Digest 또는 parent generation이 다르거나 attempt가 소비됐다면
   replay를 거절하고 새 closure attempt를 요구한다.

Normal resume는 durable checkpoint, 동일 parent generation과 current digest가 모두 일치할 때만
허용한다. 이 중 하나가 없거나 actor attribution이 모호하면 new attempt로 분리하고 이전 attempt
history를 보존한다.

Verification:

- Success flow의 generation parent chain과 acceptance ref가 연속적이다.
- Fixture terminal recovery는 `active_round: none`, empty active Steps와 dedicated fixture Round를
  가리키는 derived latest accepted ref를 반환한다. Live R010은 이 fixture result로 terminal 또는
  accepted가 되지 않는다.
- 기존 10개 adversarial fixture는 의도한 stable diagnostic에서 멈추고 이후 phase를 실행하지 않는다.
- 일곱 crash/resume fixture는 같은 attempt resume와 새 attempt 경계를 위 정책대로 재현한다.
- Temporary fixture가 current repository, external evidence와 reviewer key를 오염시키지 않는다.

Done when: actual Keystone runtime/source를 사용하는 isolated fixture Round가 clean run에서 recovery,
implementation, closure, fixture-local acceptance, finalization과 terminal 재진입을 완주하고 10개
adversarial scenario와 7개 targeted crash/resume scenario를 fail-closed 또는 digest-safe resume로
처리하며 live R010/S07 state는 변경하지 않는다.

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
  Main acceptance→finalization→new Reader flow가 dedicated fixture Round에서 완주하고 live R010
  works tree는 fixture discovery와 mutation scope 밖에 남는다.
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
- `R010-S06-CC-07` Dedicated fixture Round의 terminal Reader recovery와
  Author/Coordinator/release-facing work state가 동일하고, live R010 terminal state를 주장하지
  않는다.
<!-- key: id=key.acceptance.whole-flow.prerequisite-verification -->
- `R010-S06-CC-08` S01-S05 Work가 `complete + accepted`이고 S06 focused/cross-skill verification이
  통과한다.
<!-- key: id=key.acceptance.whole-flow.prerequisite-finalization -->
- `R010-S06-CC-09` S01-S05 각각의 finalization이 `complete` 또는 accepted `waived`이고, waiver
  reason/follow-up, Work acceptance ref, finalization manifest/envelope digest와 package-owned Author
  runner pass가 S06 Progress의 별도 closure evidence에 결속된다.
<!-- key: id=key.acceptance.whole-flow.crash-resume -->
- `R010-S06-CC-10` 일곱 targeted crash/resume fixture가 durable checkpoint, parent generation과
  current digest를 기준으로 same-attempt resume와 new-attempt-required를 정확히 구분한다.

<!-- key: id=key.work.whole-flow-self-host-e2e.order.verification refs=key.topic.verification key.topic.integration-verification -->
## Verification

- Temporary clean checkout whole-flow success corpus
- Phase/actor/generation/acceptance-ref continuity assertions
- Ten required adversarial fixtures, seven targeted crash/resume fixtures와 stable diagnostics
- S01-S05 finalization state/ref/manifest/envelope/Author-runner preflight evidence
- Actual agent evidence consumption and terminal Work State parity
- Installer forced rollback isolation, repository full graph validation와 `git diff --check`

<!-- key: id=key.work.whole-flow-self-host-e2e.order.expected-output refs=key.topic.verification key.topic.work-recovery -->
## Expected Output

- Isolated fixture-Round whole-flow self-host harness와 actual Keystone runtime/source success corpus
- Ten adversarial fixtures, seven targeted crash/resume fixtures, stable diagnostics와 attempt-history
  phase evidence archive
- S01-S05 finalization closure evidence matrix와 package-owned Author runner evidence
- Terminal Reader/work-state parity evidence와 Progress criterion mapping

<!-- key: id=key.work.whole-flow-self-host-e2e.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. S01-S05 required evidence가 complete/accepted가 아니거나 finalization closure evidence와
   generation을 재현할 수 없다.
2. Fixture-local acceptance가 live Main acceptance 또는 authoritative R010 state를 변경한다.
3. External agent/reviewer evidence를 위조하거나 credential/key를 repository에 저장해야 한다.
4. Whole-flow success가 synthetic manifest만으로 actual source phase를 대체한다.
5. Fixture Work State discovery가 live R010/S07을 포함하거나 fixture acceptance/finalization을 live
   R010 terminal evidence로 재사용해야 한다.
6. Stable release, publication, external pilot 또는 새 feature가 completion 필수가 된다.
