---
doc_type: work_order
created_at: "2026-08-12"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-12", accepted_by: main}
work_status: complete
key:
  id: key.work.current-work-state-simplification.order
  refs:
    - key.doc.work
    - key.topic.work-sequence
    - key.topic.work-recovery
    - key.topic.skill-contract
    - key.topic.change-set
    - key.topic.verification
    - key.work.decisions.dec-works-032
    - key.claim.r012.current-round-authority
    - key.claim.r012.round-session-focus
    - key.claim.r012.worker-step-selection
---

# Current Work State and Session Focus Simplification 작업서 및 Change Set

<!-- key: id=key.work.current-work-state-simplification.order.goal refs=key.section.goal key.topic.work-recovery -->
## Goal

Current Work State를 active parent Round와 Work·Step Progress 중심으로 단순화한다. Accepted
ordering을 위한 acceptance-event와 `latest_accepted_round`을 current 필수 계약에서 제거하고,
복수 active parent Round에서는 사용자가 세션 Round만 선택하며 실행자가 진행 중 Step을 알리고
기본 실행 Step을 정하도록 Reader와 consumer 동작을 정합화한다.

<!-- key: id=key.work.current-work-state-simplification.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- 프로젝트 Work State와 Round 기준에서 current authority와 historical compatibility 분리
- `DEC-WORKS-027`, `DEC-WORKS-031`의 부분 대체 의미를 `DEC-WORKS-032`에 따라 반영
- canonical Work State runtime의 acceptance-event optional 처리와 current output versioning
- Reader의 multi-active session focus를 Work가 아닌 parent Round 단위로 변경
- 후보 Round별 현재 진행 중 Step 요약과 정확한 Round 선택 질문
- 선택된 Round에서 실행자가 가장 낮은 번호의 실행 가능 active Step을 기본 선택하는 계약
- Reader·Author·Coordinator generated runtime parity와 직접 관련 consumer/test 정합화
- event가 없는 Uptendo형 corpus, 기존 event chain과 단일·복수·child Round 회귀 검증

Exclude:

- R011과 이전 accepted 문서·결정·Progress의 소급 수정
- 기존 `key-acceptance-events.json` 삭제 또는 새 event·manifest·key·receipt 생성
- 외부 소비 프로젝트 문서 직접 수정
- session focus 또는 Step 선택을 persistent pointer나 priority 상태로 저장
- 실제 작업에 필요하지 않은 범용 scheduler, timestamp 체계 또는 별도 상태 데이터베이스

<!-- key: id=key.work.current-work-state-simplification.order.policy-baseline refs=key.topic.work-recovery key.topic.work-sequence -->
## 수락된 정책 기준선

1. Current 전역 실행 권위는 parent-only `active_rounds`와 Progress에서 파생한 `active_steps`다.
2. `latest_accepted_round`은 current 필수 출력과 권위에서 폐기한다. Accepted history에는 각 Round
   source를 사용하고 별도의 단일 ordering을 만들지 않는다.
3. Acceptance-event는 기존 historical compatibility input일 뿐 부재가 current Work State 실패
   원인이 아니다.
4. Active parent Round가 둘 이상이고 요청에서 대상을 정하지 않았으면 각 Round와 현재 진행 중
   Step을 요약한 뒤 `해당 세션에서 어떤 라운드를 작업할까요?`라고 한 번 묻는다.
5. Round 선택은 session-only다. Step 선택을 위해 묻지 않으며 실행자는 사용자 지정이 없을 때
   dependency/gate를 만족하는 가장 낮은 번호의 active Step을 선택하고 선택 근거를 알린다.

<!-- key: id=key.work.current-work-state-simplification.order.execution-plan refs=key.topic.work-sequence key.topic.verification -->
## 실행 계획

| Step | 상태 | 변경 범위 | 완료 경계 |
|---|---|---|---|
| R012/S01 | complete, accepted | Project/Reader/Author/Coordinator 기준과 active index | DEC-WORKS-032의 current·compatibility·session focus 의미가 충돌 없이 반영됨 |
| R012/S02 | complete, accepted | canonical `scripts/work_state_runtime.py`, generator, generated copies와 runtime tests | no-event initialized repository가 pass하고 latest/event가 current 필수 contract에서 빠짐 |
| R012/S03 | complete, accepted | Reader skill contract와 session-focus tests, 필요한 consumer adapter | Round 후보와 진행 중 Step을 알리고 한 번 질문하며 Step은 실행자가 기본 선택함 |
| R012/S04 | complete, accepted | focused/package/cross-consumer/repository/installer verification | 기존 event compatibility와 새 no-event/multi-Round 경로를 production release gate로 함께 검증했다 |

S02와 S03은 S01의 기준 계약이 complete + accepted된 뒤 시작한다. S04는 S02와 S03의 구현 결과를
함께 검증한다. 미래 Step의 사전 조사는 가능하지만 상태를 자동 전이하지 않는다.

<!-- key: id=key.work.current-work-state-simplification.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

| Surface | Owner | Required change | Verification |
|---|---|---|---|
| Shared Decision / Project Standard | Author | current active authority, retired latest ordering과 historical event 경계 | metadata·Markdown·effective Decision validation |
| Reader Standard / Skill | Author / Main | Round session focus, Step 목록 안내와 실행자 선택 | zero/one/multi/explicit/cross-Round scenarios |
| Author / Coordinator contracts | Author / Main | current closure와 Work State consumer가 retired field를 요구하지 않음 | focused contract tests |
| Work State Runtime | Main | no-event pass, current output schema와 compatibility adapter | canonical runtime unit/adversarial tests |
| Generated copies / manifests | Main | canonical source에서 재생성하고 exact parity 유지 | generator `--check`, installed isolation |
| Uptendo-shaped fixture | Main | accepted R011과 active R008/R010, child R010-a, event 없음 | active Round/Step recovery와 diagnostics 0 |

<!-- key: id=key.work.current-work-state-simplification.order.completion refs=key.topic.acceptance key.topic.verification -->
## Completion Criteria

<!-- key: id=key.acceptance.current-work-state.authority -->
- `R012-CC-01` Current state authority가 parent-only `active_rounds`, Work·Step Progress와
  `active_steps`로 한정되고 singular/latest projection이 실행 대상을 정하지 않는다.
<!-- key: id=key.acceptance.current-work-state.no-event -->
- `R012-CC-02` 초기화된 repository에 acceptance-event 파일이 없어도 Work State가 유효한 active
  Round·Work·Step과 source generation을 반환하고 missing-event 오류를 만들지 않는다.
<!-- key: id=key.acceptance.current-work-state.retired-latest -->
- `R012-CC-03` `latest_accepted_round`이 current 필수 output, pointer freshness와 Reader 성공
  조건에서 제거되고 기존 값은 호환 자료로만 분류된다.
<!-- key: id=key.acceptance.current-work-state.historical-compatibility -->
- `R012-CC-04` 기존 acceptance-event chain은 삭제·재생성 없이 historical compatibility 범위에서
  읽히며 current completion이나 session focus를 authorize하지 않는다.
<!-- key: id=key.acceptance.current-work-state.round-session-focus -->
- `R012-CC-05` 복수 active parent Round에서 후보별 진행 중 Step을 보여주고 정확한 질문을 한 번
  하며, 명시된 Round와 전체/cross-Round 요청에서는 질문하지 않는다.
<!-- key: id=key.acceptance.current-work-state.worker-step-selection -->
- `R012-CC-06` 선택된 Round의 진행 중 Step을 사용자에게 알리되 Step 선택 질문은 하지 않고,
  실행자는 lowest executable Step과 dependency/gate 우회를 설명한다.
<!-- key: id=key.acceptance.current-work-state.consumer-parity -->
- `R012-CC-07` canonical runtime, Reader·Author·Coordinator generated copies, release consumer와
  package tests가 같은 current/compatibility 의미를 사용한다.
<!-- key: id=key.claim.current-work-state.uptendo-no-event-recovery kind=claim -->
- event 없는 Uptendo형 병렬 parent/child source는 acceptance event와 무관하게 현재 Round와 Step을
  복구하며 compatibility diagnostic을 만들지 않는다.
<!-- key: id=key.acceptance.current-work-state.uptendo-regression requires_verification_of=key.claim.current-work-state.uptendo-no-event-recovery -->
- `R012-CC-08` event 없는 Uptendo형 병렬 parent/child fixture가 diagnostics 0으로 active R008,
  R010과 R010-a의 진행 중 Step을 복구한다.

<!-- key: id=key.work.current-work-state-simplification.order.verification refs=key.topic.verification key.topic.integration-verification -->
## Verification

1. Work State focused tests: uninitialized, initialized/no-event, legacy event valid/invalid, stale legacy
   pointer, single/multiple active parent와 child Round.
2. Reader focused tests: zero/one/multiple active parent, explicit Round, cross-Round 요청, Round별 active
   Step summary, blocked-lowest와 next-executable 선택.
3. Canonical/generated byte·manifest·public API·result parity와 package isolation.
4. Author·Coordinator consumer와 release Work State 단계의 retired-field 의존 검색 및 focused test.
5. 문서 readiness, affected graph validation, Python compile, diff check.
6. 전체 package·repository·installer release gate는 R012/S04에서만 실행한다.

<!-- key: id=key.work.current-work-state-simplification.order.stop refs=key.boundary.stop-condition key.topic.work-sequence -->
## Stop Conditions

1. `latest_accepted_round` 제거가 current 실행과 무관한 외부 public consumer 계약을 깨뜨려 별도
   migration 결정이 필요하다.
2. Historical event 파일의 손상을 current Work State 실패로 볼지 단순 compatibility diagnostic으로
   볼지 수락된 정책만으로 결정할 수 없다.
3. Step 번호와 dependency/gate가 서로 충돌해 lowest executable Step을 결정할 수 없다.
4. 구현을 위해 child 아래 추가 Round나 별도 persistent scheduler가 필요해진다.
5. 외부 소비 프로젝트 source를 직접 수정해야만 검증할 수 있다.

<!-- key: id=key.work.current-work-state-simplification.order.expected-output refs=key.topic.work-recovery key.topic.verification -->
## Expected Output

- DEC-WORKS-032와 정합한 current Work State·Round·Reader 기준
- 단순화된 canonical Work State runtime과 generated consumer copies
- Round session-focus와 실행자 Step-selection 계약·테스트
- no-event Uptendo형 회귀 fixture와 historical compatibility 검증
- 실제 결과, residual risk와 rollout resume point를 기록한 Progress
