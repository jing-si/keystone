---
doc_type: work_order
created_at: "2026-08-07"
document_lifecycle: active
approval: {state: pending}
work_status: planned
key:
  id: key.work.production-candidate-85-closure.order
  refs:
    - key.doc.work
    - key.topic.work-sequence
    - key.topic.work-recovery
    - key.topic.finalization
    - key.topic.acceptance
    - key.topic.change-set
    - key.topic.integration-verification
    - key.topic.verification
  relations:
    depends_on:
      - target: key.work.production-control-plane-hardening.order
      - target: key.work.authority-chain-snapshot-closure.order
      - target: key.work.graph-transaction-source-correctness.order
      - target: key.work.work-state-agent-evaluation.order
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
  - dependency: key.work.work-state-agent-evaluation.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval:
        state: accepted
    optional: false
---

# Production Candidate 8.5 Closure 작업서 및 Change Set

<!-- key: id=key.work.production-candidate-85-closure.order.goal refs=key.section.goal key.topic.integration-verification -->
## Goal

R010/S01-S04의 correctness, phase authority, source interpretation, shared work state와 actual agent
evidence를 실제 Keystone source를 변경하는 하나의 clean whole-flow로 통합한다. Independent CI와
release gate를 current commit/package/installed tree/evidence에 결속한다. Version transition을
포함한 S05 결과를 Main이 수락하면 schema-v5 terminal finalization으로 R010을 닫되, S01-S04의
기존 acceptance event와 acceptance ref는 다시 쓰지 않는다.

<!-- key: id=key.work.production-candidate-85-closure.order.improvements refs=key.topic.work-sequence key.topic.verification -->
## 개선 항목

| ID | 개선 항목 | 구현 순서 | 핵심 근거 |
|---|---|---|---|
| PC85-11 | R010 whole-flow self-host E2E | 1 | 실제 source의 recovery→implementation→acceptance→terminal 재진입 |
| PC85-12 | Independent RC CI와 R010 closure | 2 | clean current commit, RC version와 schema-v5 finalization |

<!-- key: id=key.work.production-candidate-85-closure.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- Temporary clean checkout의 Reader→Coordinator→worker→Linker→Author→Main→finalization workflow
- S02 phase/snapshot, S03 transaction/source와 S04 work-state/eval evidence integration
- Success flow와 scope/authority/generation/acceptance/evidence adversarial flow
- Linux/macOS, supported Python, installer parity/rollback와 independent RC CI
- Current commit, package tree, installed tree, eval/finalization/release evidence binding
- `0.7.0-rc.1`, S01-S04 preserved acceptance evidence, S05 acceptance와 schema-v5 terminal
  global state

Exclude:

- 새 기능, relation/skill, external pilot, performance/fuzz/fault-injection program
- Marketplace publication, push/merge와 stable `1.0.0`
- CI가 지원한다고 선언하지 않은 platform을 임의로 required로 만드는 작업
- External reviewer 독립성을 repository code만으로 증명한다는 주장

<!-- key: id=key.work.production-candidate-85-closure.order.source-context refs=key.section.source-context key.topic.integration-verification -->
## Source Context

- R010/S01-S04 Work Order, Progress와 accepted verification evidence
- Package-owned Coordinator/Linker/Author runners와 Work State Runtime
- Actual agent eval runner, strict evidence validator와 external reviewer operation evidence
- `scripts/run_release_gate.sh`, installer와 current CI configuration
- `00_docs/standards/01_key-project-standard.md`
- `00_docs/standards/skills/author/key-standard-author.md`
- `00_docs/standards/skills/coordinator/key-standard-coordinator.md`
- `00_docs/convention.md`

<!-- key: id=key.work.production-candidate-85-closure.order.pc85-11 refs=key.topic.integration-verification key.topic.finalization -->
## PC85-11 R010 whole-flow self-host E2E

Implementation:

1. Reader가 active Work를 복구하고 Coordinator가 complete assignment snapshot을 생성한다.
2. Worker가 bounded runtime source를 변경하고 Coordinator가 worker phase actual diff를 검증한다.
3. Package-owned Linker가 graph classification/transaction을 실행하고 Author가 document/metadata를
   pre-acceptance phase에서 동기화한다.
4. Main acceptance event 뒤 Author가 schema-v5 finalization을 수행하고 Coordinator가
   post-acceptance phase를 검증한다.
5. 새 Reader session이 terminal state를 복구하고 production release gate 직전 상태를 확인한다.
6. 모든 phase snapshot/delta, acceptance ref와 derived work state를 S02/S04 runtime에 결속한다.

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

Done when: 실제 Keystone source가 clean run에서 recovery·implementation·closure·acceptance·
finalization·terminal 재진입을 완주하고 모든 failure scenario를 fail-closed로 차단한다.

<!-- key: id=key.work.production-candidate-85-closure.order.pc85-12 refs=key.topic.acceptance key.topic.finalization key.topic.verification -->
## PC85-12 Independent RC CI와 R010 closure

Implementation:

1. Clean checkout에서 Linux/macOS, supported Python, package suites, readiness/full graph validation,
   whole-flow E2E, agent evidence, installer parity/rollback와 RC gate를 실행한다.
2. Windows를 공식 support matrix에 포함할 경우에만 required job으로 추가한다.
3. CI result, release plan, package/installed tree와 external evidence subject를 current commit SHA에
   결속하고 artifact/test result를 보존한다.
4. RC profile은 active R010에서 실행 가능하지만 production profile은 terminal finalization,
   clean tree, non-dev version과 fresh external evidence를 요구한다.
5. 모든 technical readiness gate 뒤 version을 `0.7.0-rc.1`로 전이하고 그 결과를 다시 검증한
   다음 Main이 S05만 새 acceptance event로 수락한다.
6. Schema-v5 finalization은 accepted Step `R010/S05`와 그 acceptance ref를 기록하고, S01-S04의
   기존 accepted evidence/ref는 보존한 채 모든 Work의 terminal 상태에서 R010 Round를 닫는다.

Verification:

- CI checkout/evidence/artifact SHA mismatch가 실패한다.
- Dirty tree, `-dev` version, stale evidence, missing required job와 incomplete finalization이
  production profile을 차단한다.
- Installed tree parity, forced rollback과 repeated release plan determinism을 확인한다.
- New Reader session과 production gate가 동일 terminal work state를 반환한다.

Done when: current accepted commit의 clean independent run만 RC/production success를 만들고 모든
R010 global-state source가 terminal state를 재현한다.

<!-- key: id=key.work.production-candidate-85-closure.order.acceptance-matrix refs=key.topic.acceptance key.topic.integration-verification -->
## 평균 8.5 Acceptance Matrix

- [ ] Worker, Author, repository owner와 finalization 변경이 phase별로 구분된다.
- [ ] 각 source write가 정확히 한 actor와 authority에 귀속된다.
- [ ] Assignment baseline이 complete path set, path type과 snapshot policy에 결속된다.
- [ ] 실제 applied된 모든 required/optional patch가 owner confirm과 baseline 검사를 통과한다.
- [ ] `not_applicable`도 package-owned Linker가 동일 delta/source에서 판정한다.
- [ ] Scanner, readiness, reconstruction과 validator가 동일 SourceUnit 결과를 사용한다.
- [ ] Non-UTF-8 supported source와 companion이 raw-byte binding으로 처리된다.
- [ ] Cross-domain lifecycle·approval·authority 상속이 발생하지 않는다.
- [ ] Mutation과 authority-bearing object에 unknown/duplicate/policy-bypass field가 허용되지 않는다.
- [ ] Global work state와 latest accepted round가 repository 전체에서 파생된다.
- [ ] Reader·Coordinator·Author·release gate가 동일 Work State Runtime 결과를 사용한다.
- [ ] Actual agent eval runner가 12개 scenario를 반복 실행하고 strict evidence를 생성한다.
- [ ] Actual whole-flow self-host success와 adversarial E2E가 통과한다.
- [ ] Clean independent CI에서 current commit에 결속된 RC release gate가 통과한다.
- [ ] S01-S04의 기존 accepted evidence와 S05의 새 Main acceptance가 각 acceptance ref를 보존한
      채 schema-v5 terminal Round finalization을 통과한다.

<!-- key: id=key.work.production-candidate-85-closure.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: 모든 subsystem evidence를 actual whole-flow와 independent release subject에 결속한다.
- Required candidates: self-host harness, release gate, CI, installer, agent evidence, version source,
  R010 finalization/global-state documents와 cross-skill tests
- Conditional candidates: Windows job은 accepted support matrix가 요구할 때만 required다.
- Excluded: new product feature, external pilot, stable release와 publication
- Acceptance owner: Main
- Graph handling: actual source delta와 release/finalization document delta를 package-owned Linker가
  분류하고 required mutation만 owner-attested transaction으로 처리한다.

<!-- key: id=key.work.production-candidate-85-closure.order.completion refs=key.topic.acceptance key.topic.integration-verification -->
## Completion Criteria

- [ ] S01-S04가 각각 `work_status: complete`와 `approval.state: accepted`다.
- [ ] Whole-flow success와 10개 required failure scenario가 actual clean checkout에서 통과한다.
- [ ] Agent eval 12개 scenario의 repeated external evidence가 current commit에 결속된다.
- [ ] Linux/macOS와 supported Python의 independent clean CI가 통과한다.
- [ ] Installer staging/parity/forced rollback과 installed tree digest가 통과한다.
- [ ] Version은 `0.7.0-rc.1`이며 working tree와 release subject가 clean/current다.
- [ ] Main이 version/release evidence를 포함한 R010/S05 결과만 새 acceptance event로 수락한다.
- [ ] Schema-v5 S05 finalization이 S01-S04의 기존 acceptance ref를 보존하고, derived work state와
      production release gate가 terminal R010을 재현한다.

<!-- key: id=key.work.production-candidate-85-closure.order.verification refs=key.topic.verification key.topic.integration-verification -->
## Verification

- S01-S04 package/cross-skill evidence replay
- Temporary clean checkout whole-flow success and required failure matrix
- Actual agent eval repeated evidence and strict validator
- Full package suites, readiness, repository full graph validation와 historical compatibility
- Linux/macOS supported Python CI, installer parity와 forced rollback
- RC/production gate, current commit/package/installed/evidence digest equality
- New Reader terminal recovery, schema-v5 finalization와 `git diff --check`

<!-- key: id=key.work.production-candidate-85-closure.order.expected-output refs=key.topic.verification key.topic.work-recovery -->
## Expected Output

- Isolated R010 whole-flow self-host harness, success corpus와 10개 adversarial fixtures
- Independent CI workflows, retained artifacts/evidence와 reproducible RC gate result
- `0.7.0-rc.1` version change and installed-tree parity evidence
- S01-S04 preserved acceptance evidence, S05 acceptance/schema-v5 finalization와 terminal Reader
  recovery record

<!-- key: id=key.work.production-candidate-85-closure.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. S01-S04 required evidence가 complete/accepted가 아니거나 source generation을 재현할 수 없다.
2. External agent/reviewer evidence를 위조하거나 credential/key를 repository에 저장해야 한다.
3. CI subject와 current commit, package/installed tree 또는 evidence subject가 일치하지 않는다.
4. Main acceptance 없이 version/finalization/global state를 accepted/terminal로 바꿔야 한다.
5. Stable release, publication, external pilot 또는 새 feature가 completion 필수가 된다.
