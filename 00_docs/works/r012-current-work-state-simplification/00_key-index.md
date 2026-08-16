---
doc_type: work_round
created_at: "2026-08-12"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-12", accepted_by: main}
round_status: accepted
key:
  id: key.work.round.r012-current-work-state-simplification.index
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.work-recovery
    - key.topic.skill-contract
    - key.topic.verification
    - key.work.decisions.dec-works-032
    - key.claim.r012.current-round-authority
    - key.claim.r012.round-session-focus
    - key.claim.r012.worker-step-selection
---

# R012 Current Work State and Session Focus Simplification 작업서 색인

R012는 current 작업 복구에 필요하지 않은 acceptance-event와 latest-accepted ordering 의존을
제거하고, 병렬 active parent Round를 세션 범위 선택으로 다루는 단순한 실행 계약을 구현한다.
사용자는 여러 active Round 중 이번 세션 대상을 고르며, 실행자는 선택된 Round의 진행 중 Step을
알리고 dependency와 gate를 만족하는 가장 낮은 번호의 Step을 기본 실행 대상으로 선택한다.

R012는 S01-S04의 기준 정합화, runtime·Reader 구현과 production release gate를 모두 통과하고
terminal accepted 상태로 닫혔다. 새 acceptance-event나 finalization 산출물은 만들지 않았다.

<!-- key: id=key.work.round.r012.execution-order refs=key.topic.work-sequence key.topic.work-recovery -->
## 실행 순서

| 순서 | Step | 상태 | 목적 |
|---|---|---|---|
| S01 | Current State Authority and Decision Alignment | complete, accepted | DEC-WORKS-032를 current 기준서와 Work State contract에 반영했다 |
| S02 | Work State Runtime Simplification | complete, accepted | acceptance-event 부재를 정상 입력으로 처리하고 latest-accepted current 계약을 제거했다 |
| S03 | Round Session Focus and Step Selection | complete, accepted | Round 후보·진행 중 Step 안내, session-only 질문과 실행자 Step 선택을 구현했다 |
| S04 | Integration Verification and Rollout Readiness | complete, accepted | no-event·multi-Round·legacy compatibility와 배포 사본 정합성을 검증했다 |

현재 active Step은 없다. Step 결과와 terminal resume point는
`current-work-state-simplification/key-progress.md`에서 확인한다.

<!-- key: id=key.work.round.r012.boundaries refs=key.boundary.scope-control key.topic.verification -->
## Round 경계

- R011과 이전 accepted Round·Step·Decision·Progress를 소급 수정하지 않는다.
- 기존 `key-acceptance-events.json`은 역사 기록으로 보존하고 새 event를 만들지 않는다.
- 외부 소비 프로젝트 문서는 수정하지 않으며 Uptendo는 no-event 회귀 fixture와 후속 rollout
  검증 대상으로만 사용한다.
- Session focus는 parent Round 단위이며 child Round, Work 또는 Step 선택을 영속 pointer로 만들지
  않는다.
- 하나의 parent Round와 하나의 Work로 충분하므로 child Round를 만들지 않는다.

<!-- key: id=key.work.round.r012.completion refs=key.topic.acceptance key.topic.verification -->
## Round 완료 조건

1. S01-S04의 completion criteria와 직접 관련 검증이 충족된다.
2. Current Work State가 acceptance-event 없이 active parent Round, child, Work와 Step을 복구한다.
3. `latest_accepted_round`과 acceptance-event가 current 성공 authority 또는 필수 출력이 아니다.
4. 복수 active parent Round에서 후보별 진행 중 Step을 알린 뒤 Round focus를 한 번 질문하고,
   선택된 Round의 Step은 실행자가 기본 규칙으로 선택한다.
5. 기존 event chain, 단일 Round corpus와 generated runtime consumer는 명시된 compatibility
   경계에서 동작한다.

<!-- key: id=key.work.round.r012.reading-rules refs=key.topic.work-recovery key.topic.work-sequence -->
## 복구 규칙

1. R012 목표와 Step 순서는 이 Index를 읽는다.
2. 세부 범위, criterion과 변경 surface는 Work Order를 읽는다.
3. 실제 진행 상태, 진행 중 Step 목록과 resume point는 Progress를 읽는다.
4. 복수 active parent Round이면 Reader는 상세 Work 문서를 모두 열기 전에 Round session focus를
   질문한다.
