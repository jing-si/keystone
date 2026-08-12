---
doc_type: work_order
created_at: "2026-08-07"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-11", accepted_by: main}
work_status: complete
finalization: {state: complete, acceptance_ref: R010/S07/main-acceptance}
key:
  id: key.work.production-candidate-85-closure.order
  refs:
    - key.doc.work
    - key.topic.work-sequence
    - key.topic.work-recovery
    - key.topic.finalization
    - key.topic.change-set
    - key.topic.integration-verification
    - key.topic.verification
    - key.work.decisions.dec-works-029
  relations:
    depends_on:
      - target: key.work.whole-flow-self-host-e2e.order
work_gates:
  - id: r010-s07-start-core-simplification
    dependency: key.work.whole-flow-self-host-e2e.order
    applies_to: {steps: [S07], work_completion: false}
    condition: {work_status: complete, approval_state: accepted}
    optional: false
  - id: r010-s07-completion-core-simplification
    dependency: key.work.whole-flow-self-host-e2e.order
    applies_to: {steps: [], work_completion: true}
    condition: {work_status: complete, approval_state: accepted}
    optional: false
---

# Product Workflow Verification and R010 Closure 작업서 및 Change Set

이 문서의 경로와 Work owner ID는 기존 R010/S07 계획 참조를 보존한다. `85`는 historical locator일
뿐 현재 completion score가 아니다.

<!-- key: id=key.work.production-candidate-85-closure.order.goal refs=key.section.goal key.topic.integration-verification -->
## Goal

단순화된 Keystone이 실제 기준서 기반 프로젝트 관리 상품으로 작동하는지 검증한다. 기준서 작성과
변경에서 관련 산출물 탐색, bounded implementation, verification, Progress 업데이트, 중단 후 복구와
사용자 수락까지 하나의 설명 가능한 흐름으로 연결하고, 외부 secret·실제 agent evaluation·임의
점수 없이 R010을 종료한다.

<!-- key: id=key.work.production-candidate-85-closure.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- S05 product boundary와 S06 simplified implementation의 current-source verification
- Temporary fixture project에서 standards/work/artifact graph를 사용하는 대표 제품 흐름
- 기준서 또는 criterion→code/config/schema/API/test owner/ref·relation 탐색
- 산출물 변경→영향받는 기준·작업·verification stale candidate 역탐색
- Reader active Work/Step, goal, criteria, evidence, next action recovery
- 중단된 작업의 durable Progress 기반 resume와 scope drift 차단
- Main direct 또는 permitted Coordinator 구현 뒤 Author/Linker document·graph closure
- 기본 package tests, readiness, graph validation, installer parity와 clean source verification
- Historical R001-R010 read compatibility와 current-write meaning
- 사용자용 시작·복구·검증 설명과 residual risk

Exclude:

- Actual model invocation, transcript, reviewer/adjudicator와 external evidence root
- HMAC/private key, 조직 독립성, regulated audit와 remote attestation
- 평균 8.5/8.7 점수, versioned scoring rubric와 mechanical score cap
- 강제 `0.7.0-rc.1` version bump, candidate→terminal cryptographic lineage와 publication
- External pilot, 브라우저/Playwright 검증과 새 product feature
- R011 planned scope와 외부 소비 프로젝트 source 수정

<!-- key: id=key.work.production-candidate-85-closure.order.source-context refs=key.section.source-context key.topic.integration-verification -->
## Source Context

- `DEC-WORKS-029`
- S05 accepted disposition/Change Set
- S06 accepted standards/runtime/test evidence
- Project, Bootstrap, Artifact Graph와 six-skill contracts
- R010 historical Work/Progress/finalization evidence
- `README.md`, installer와 simplified release checks
- `00_docs/convention.md`

<!-- key: id=key.work.production-candidate-85-closure.order.product-scenarios refs=key.topic.integration-verification key.topic.work-recovery -->
## Required Product Scenarios

### PWF-01 Standard to implementation

1. Fixture project의 accepted standard 또는 Work criterion을 변경한다.
2. Linker가 source-owned ID/ref와 필요한 typed relation으로 관련 code/test candidate를 찾는다.
3. Main 또는 permitted Coordinator가 bounded implementation을 수행한다.
4. Verification과 changed source를 기준서/Work criterion에 다시 연결한다.
5. Author가 Progress와 필요한 document metadata를 갱신하고 Main이 결과를 검토한다.

### PWF-02 Implementation to stale source

1. 연결된 code/config/schema/API/test artifact를 변경한다.
2. Linker가 관련 기준서·결정·작업·verification의 mechanical stale, semantic stale와 metadata gap을
   구분한다.
3. 후보는 자동 수정이나 acceptance가 아니라 적절한 source owner handoff로 반환된다.

### PWF-03 Interrupt and recover

1. 구현 또는 document/graph closure 중간에 작업을 중단한다.
2. 새 Reader session이 active Work/Step, goal, criteria, 완료 evidence, 미완료 항목과 next action을
   repository documents에서 복구한다.
3. Current source/digest가 checkpoint와 일치하면 안전하게 resume하고, 다르면 새 attempt 또는
   re-plan을 요구한다.

### PWF-04 Default local operation

1. 새 fixture project를 초기화하거나 기존 ready project를 읽는다.
2. External secret, reviewer, model provider와 evidence service 없이 위 세 흐름을 실행한다.
3. 필요한 Git/tree와 scoped SHA 검사는 변경·freshness만 판정하고 신원·독립성을 주장하지 않는다.

<!--
key:
  id: key.work.production-candidate-85-closure.order.product-value
  kind: document_item
  supersedes:
    - key.acceptance.production-score.architecture
    - key.acceptance.production-score.authority
    - key.acceptance.production-score.contract-alignment
    - key.acceptance.production-score.reader-work-state
    - key.acceptance.production-score.dependency
    - key.acceptance.production-score.graph-source
    - key.acceptance.production-score.transaction
    - key.acceptance.production-score.finalization
    - key.acceptance.production-score.coordinator-closure
    - key.acceptance.production-score.agent-behavior
    - key.acceptance.production-score.release-operations
-->
## Product Value Criteria

점수 대신 다음을 pass/fail과 evidence로 판정한다.

| Value | Pass evidence |
|---|---|
| Traceability | 기준서/Work에서 관련 산출물과 verification을 찾고 역방향 stale 후보도 찾는다 |
| Recoverability | 새 session이 현재 상태와 next action을 문서에서 재구성한다 |
| Standards-first | 수락 가능한 문서 의미와 implementation/test가 같은 contract를 구현한다 |
| Scope safety | 권한·scope 밖 변경은 적용하지 않고 사용자 결정이 필요한 지점을 구분한다 |
| Simplicity | 기본 흐름에 external secret·reviewer·agent provider·evidence root가 없다 |
| Compatibility | 필요한 historical read와 installed package 동작이 유지된다 |
| Operability | 실패 진단, resume point, 설치와 기본 검증 명령이 이해 가능하다 |

<!-- key: id=key.work.production-candidate-85-closure.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: 단순화된 R010을 실제 제품관리 workflow와 current source evidence로 종료한다.
- Required candidates: fixture project/work, integration harness, package/readiness/graph/installer tests,
  README operations, R010 Progress/index/finalization documents
- Conditional candidates: 발견된 product-flow blocker에 한정한 focused repair
- Excluded: new feature, external service, score/reviewer infrastructure, version bump와 publication
- Acceptance owner: Main
- Graph handling: fixture와 R010 document/output delta를 Linker가 분류하고 source owner가 필요한
  mutation만 적용한다.

<!-- key: id=key.work.production-candidate-85-closure.order.completion refs=key.topic.acceptance key.topic.integration-verification -->
## Pre-Acceptance Completion Criteria

<!--
key:
  id: key.acceptance.product-workflow.prerequisites
  supersedes:
    - key.acceptance.production-candidate.prerequisites-accepted
-->
- `R010-S07R-CC-01` S05와 S06이 `complete + accepted`이고 required finalization/waiver와 current
  source evidence를 가진다.
<!--
key:
  id: key.acceptance.product-workflow.standard-to-implementation
  supersedes:
    - key.acceptance.production-candidate.subject-binding
-->
- `R010-S07R-CC-02` PWF-01에서 standard/criterion→artifact→implementation→verification→Progress
  관계가 current fixture source에 결속된다.
<!-- key: id=key.acceptance.product-workflow.reverse-stale -->
- `R010-S07R-CC-03` PWF-02에서 output change가 관련 source/verification stale와 gap을 구분하고
  자동 수정·acceptance 없이 owner handoff를 반환한다.
<!--
key:
  id: key.acceptance.product-workflow.recovery
  supersedes:
    - key.acceptance.production-candidate.current-agent-evidence
    - key.acceptance.production-candidate.rc-subject-rerun
-->
- `R010-S07R-CC-04` PWF-03에서 새 Reader session이 active work와 next action을 복구하고 current
  source가 checkpoint와 다르면 blind resume하지 않는다.
<!-- key: id=key.acceptance.product-workflow.default-local -->
- `R010-S07R-CC-05` PWF-04 기본 흐름이 external secret, reviewer, model/network와 evidence root 없이
  통과한다.
<!--
key:
  id: key.acceptance.product-workflow.release-baseline
  supersedes:
    - key.acceptance.production-candidate.independent-ci
    - key.acceptance.production-candidate.installer-parity
    - key.acceptance.production-candidate.rc-version
-->
- `R010-S07R-CC-06` Supported local/package CI, readiness, graph validation와 installer parity가
  current source에서 통과하며 version bump는 completion prerequisite가 아니다.
<!--
key:
  id: key.acceptance.product-workflow.value-gate
  supersedes:
    - key.acceptance.production-candidate.unresolved-p0-zero
    - key.acceptance.production-candidate.unresolved-p1-zero
    - key.acceptance.production-candidate.residual-risk-recorded
    - key.acceptance.production-candidate.authority-evidence-bound
    - key.acceptance.production-candidate.normal-flow-pass
    - key.acceptance.production-candidate.adversarial-flow-pass
    - key.acceptance.production-candidate.minimum-area-score
    - key.acceptance.production-candidate.weighted-average-score
    - key.acceptance.production-candidate.rubric-frozen
    - key.acceptance.production-candidate.mechanical-independent-review
    - key.acceptance.production-candidate.score-adjudication
    - key.acceptance.production-candidate.critical-area-floor
    - key.acceptance.production-candidate.internal-average-target
    - key.acceptance.production-candidate.quality-target-pass
    - key.acceptance.production-candidate.acceptance-packet-ready
-->
- `R010-S07R-CC-07` Product Value Criteria가 pass/fail evidence와 residual risk를 가지며 평균 점수,
  reviewer 또는 adjudication을 요구하지 않는다.
<!--
key:
  id: key.acceptance.product-workflow.documentation
  supersedes:
    - key.acceptance.production-candidate.release-documentation-pack
-->
- `R010-S07R-CC-08` README와 recovery documents가 실제 기본 입력, 실행·검증 명령, optional boundary와
  실패 시 next action을 정확히 설명한다.
<!-- key: id=key.acceptance.product-workflow.compatibility -->
- `R010-S07R-CC-09` R001-R010 historical read, current-write contract와 installed package parity가
  통과하고 retired current gate가 success authority를 만들지 않는다.
<!-- key: id=key.acceptance.product-workflow.scope-discipline -->
- `R010-S07R-CC-10` Changed source가 S07 fixture/verification/closure 범위와 발견된 blocker repair에
  한정되고 R011/user changes를 포함하지 않는다.

<!-- key: id=key.work.production-candidate-85-closure.order.post-acceptance refs=key.topic.acceptance key.topic.finalization -->
## Post-Acceptance Finalization Criteria

<!--
key:
  id: key.acceptance.product-workflow.main-acceptance
  supersedes:
    - key.acceptance.production-finalization.main-acceptance
    - key.acceptance.production-finalization.residual-risk-acceptance-binding
-->
- `R010-S07R-PF-01` Main이 product workflow evidence, scope와 residual risk를 검토하고 R010/S07
  acceptance를 명시한다.
<!--
key:
  id: key.acceptance.product-workflow.author-finalization
  supersedes:
    - key.acceptance.production-finalization.author-finalization
    - key.acceptance.production-finalization.terminal-subject-lineage
-->
- `R010-S07R-PF-02` Author finalization이 accepted S07 Progress와 current global work state를
  결속하고 불필요한 candidate→terminal cryptographic lineage를 요구하지 않는다.
<!--
key:
  id: key.acceptance.product-workflow.terminal-recovery
  supersedes:
    - key.acceptance.production-finalization.terminal-global-state
    - key.acceptance.production-finalization.reader-production-parity
-->
- `R010-S07R-PF-03` 새 Reader session이 terminal R010 state, latest accepted Round와 다음 planned
  work를 repository documents에서 일관되게 복구한다.

<!-- key: id=key.work.production-candidate-85-closure.order.verification refs=key.topic.verification key.topic.integration-verification -->
## Verification

- PWF-01~04 success and bounded failure fixtures
- Source owner/ref, typed relation, stale/gap와 reverse impact assertions
- Reader fresh-session recovery and drift-safe resume
- Default no-secret/no-agent/no-reviewer operation
- Package suites, readiness, repository graph validation와 installer parity
- Historical read/current-write compatibility and installed package parity
- Markdown/frontmatter/link/ID checks, external-cache compile와 `git diff --check`

<!-- key: id=key.work.production-candidate-85-closure.order.expected-output refs=key.topic.verification key.topic.work-recovery -->
## Expected Output

- Four representative product workflow evidence sets
- Product Value Criteria pass/fail and residual-risk record
- Basic package/release/installer verification without external trust infrastructure
- Accurate README/operator/recovery documents
- S07 acceptance packet, R010 finalization과 terminal Reader recovery

<!-- key: id=key.work.production-candidate-85-closure.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. S05/S06 current evidence가 complete/accepted가 아니거나 S06 simplification이 source와 다르다.
2. 기본 product flow에 external key, reviewer, model/network 또는 evidence service가 필요하다.
3. 기준서↔artifact trace나 work recovery 실패를 점수 또는 서명으로 대체해야 한다.
4. Historical source를 재작성하거나 R011/user changes를 덮어야 한다.
5. Version bump, publication, external pilot 또는 새 feature가 completion 필수가 된다.
6. Main acceptance 없이 terminal/finalization state를 전이해야 한다.

## Superseded Historical Claims

다음 ID는 최초 S07 RC/점수/암호학적 계보 계획의 역사적 locator다. 현재 completion criterion이 아니며
`Product Value Criteria`와 `key.acceptance.product-workflow.*` claim이 대체한다.

### Legacy score-area claims

<!-- key: id=key.acceptance.production-score.architecture -->
- Architecture score — superseded.
<!-- key: id=key.acceptance.production-score.authority -->
- Authority score — superseded.
<!-- key: id=key.acceptance.production-score.contract-alignment -->
- Contract-alignment score — superseded.
<!-- key: id=key.acceptance.production-score.reader-work-state -->
- Reader/Work State score — superseded.
<!-- key: id=key.acceptance.production-score.dependency -->
- Dependency score — superseded.
<!-- key: id=key.acceptance.production-score.graph-source -->
- Graph/Source score — superseded.
<!-- key: id=key.acceptance.production-score.transaction -->
- Transaction score — superseded.
<!-- key: id=key.acceptance.production-score.finalization -->
- Finalization score — superseded.
<!-- key: id=key.acceptance.production-score.coordinator-closure -->
- Coordinator-closure score — superseded.
<!-- key: id=key.acceptance.production-score.agent-behavior -->
- Agent-behavior score — superseded.
<!-- key: id=key.acceptance.production-score.release-operations -->
- Release/operations score — superseded.

### Legacy quality-target claims

<!-- key: id=key.acceptance.production-candidate.unresolved-p0-zero -->
- `R010-QT-01` unresolved P0 zero 요구 — superseded.
<!-- key: id=key.acceptance.production-candidate.unresolved-p1-zero -->
- `R010-QT-02` unresolved P1 zero 요구 — superseded.
<!-- key: id=key.acceptance.production-candidate.residual-risk-recorded -->
- `R010-QT-03` finding inventory와 residual-risk register 요구 — superseded.
<!-- key: id=key.acceptance.production-candidate.authority-evidence-bound -->
- `R010-QT-04` authority-bearing success evidence 결속 요구 — superseded.
<!-- key: id=key.acceptance.production-candidate.normal-flow-pass -->
- `R010-QT-05` S06 whole-flow normal pass 요구 — superseded.
<!-- key: id=key.acceptance.production-candidate.adversarial-flow-pass -->
- `R010-QT-06` S06 adversarial whole-flow pass 요구 — superseded.
<!-- key: id=key.acceptance.production-candidate.minimum-area-score -->
- `R010-QT-07` 열한 평가 영역 최소 8.0 요구 — superseded.
<!-- key: id=key.acceptance.production-candidate.weighted-average-score -->
- `R010-QT-08` 열한 평가 영역 평균 8.5 요구 — superseded.
<!-- key: id=key.acceptance.production-candidate.rubric-frozen -->
- `R010-QT-09` score rubric/digest 사전 동결 요구 — superseded.
<!-- key: id=key.acceptance.production-candidate.mechanical-independent-review -->
- `R010-QT-10` package evidence와 독립 reviewer 둘 요구 — superseded.
<!-- key: id=key.acceptance.production-candidate.score-adjudication -->
- `R010-QT-11` reviewer 편차 adjudication 요구 — superseded.
<!-- key: id=key.acceptance.production-candidate.critical-area-floor -->
- `R010-QT-12` critical area score floor 8.5 요구 — superseded.
<!-- key: id=key.acceptance.production-candidate.internal-average-target -->
- `R010-QT-13` 내부 평균 8.7 목표 — superseded.

### Legacy candidate and finalization claims

<!-- key: id=key.acceptance.production-candidate.prerequisites-accepted -->
- `R010-S07-CC-01` S01-S06 acceptance/finalization chain 요구 — superseded.
<!-- key: id=key.acceptance.production-candidate.current-agent-evidence -->
- `R010-S07-CC-02` actual agent evidence와 RC subject 결속 요구 — superseded.
<!-- key: id=key.acceptance.production-candidate.independent-ci -->
- `R010-S07-CC-03` 구 independent CI requirement — superseded.
<!-- key: id=key.acceptance.production-candidate.installer-parity -->
- `R010-S07-CC-04` 구 installer parity requirement — superseded.
<!-- key: id=key.acceptance.production-candidate.rc-version -->
- `R010-S07-CC-05` 강제 `0.7.0-rc.1` requirement — superseded.
<!-- key: id=key.acceptance.production-candidate.quality-target-pass -->
- `R010-S07-CC-06` `R010-QT-*` score gate 요구 — superseded.
<!-- key: id=key.acceptance.production-candidate.subject-binding -->
- `R010-S07-CC-07` 모든 evidence의 RC candidate digest 결속 요구 — superseded.
<!-- key: id=key.acceptance.production-candidate.acceptance-packet-ready -->
- `R010-S07-CC-08` score/evidence acceptance packet 요구 — superseded.
<!-- key: id=key.acceptance.production-candidate.rc-subject-rerun -->
- `R010-S07-CC-09` version-bumped RC subject 전체 재실행 요구 — superseded.
<!-- key: id=key.acceptance.production-candidate.release-documentation-pack -->
- `R010-S07-CC-10` RC용 위협/retention/recovery 문서 pack 요구 — superseded.
<!-- key: id=key.acceptance.production-finalization.main-acceptance -->
- `R010-S07-PF-01` 구 Main RC acceptance requirement — superseded.
<!-- key: id=key.acceptance.production-finalization.author-finalization -->
- `R010-S07-PF-02` schema-v6 finalization binding 요구 — superseded.
<!-- key: id=key.acceptance.production-finalization.terminal-global-state -->
- `R010-S07-PF-03` 구 terminal global-state requirement — superseded.
<!-- key: id=key.acceptance.production-finalization.reader-production-parity -->
- `R010-S07-PF-04` Reader/release terminal parity 요구 — superseded.
<!-- key: id=key.acceptance.production-finalization.residual-risk-acceptance-binding -->
- `R010-S07-PF-05` residual-risk acceptance cryptographic binding 요구 — superseded.
<!-- key: id=key.acceptance.production-finalization.terminal-subject-lineage -->
- `R010-S07-PF-06` candidate→terminal subject lineage 요구 — superseded.
