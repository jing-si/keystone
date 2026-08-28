---
doc_type: work_order
created_at: "2026-08-28"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-28", accepted_by: main}
work_status: complete
key:
  id: key.work.session-title-work-authoring-gate.order
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.skill-contract
    - key.topic.verification
    - key.boundary.scope-control
    - key.standard.project
    - key.standard.skill.reader
  relations:
    produces:
      - key.skill.reader
      - key.code.reader.keystone-session-title
      - key.test.r020.keystone-session-title-runtime
---

# Session Title Work Authoring Gate 작업서

## Goal

Keystone Reader의 최초 선택 gate에서 기존 Round 수행뿐 아니라 작업서 생성·수정 착수도
작업 할당으로 인식한다. 신규 Round는 현재 Work State에서 예정 ref를 계산해
`RNNN[-SUFFIX]:대표문구` 제목을 생성하고, 같은 ref를 Author가 생성 직전에 재검증하도록
원 요청에 전달한다.

## 수락된 사용자 방향

1. 작업서 생성·수정을 실제로 시작하는 시점에도 세션 제목을 작업 Round로 표시한다.
2. 신규 Round 작업과 parent가 명확하면 작업서가 아직 없어도 예정 local ref를 사용한다.
3. 작업서 작성 전 검토만 요청한 경우에는 authoring 할당으로 처리하지 않는다.
4. 최초 native title이 이미 정해진 이후의 강제 retitle은 보장하지 않는다.
5. 기존 R022의 후보 정렬, 종료 상태 제외, 10개 제한과 자유 검토 흐름을 유지한다.

## Scope

Include:

- Project·Reader work-authoring title 계약 정렬
- 작업서 생성·수정 착수의 보수적 자연어 감지
- 신규 parent 숫자와 신규 child Excel suffix의 deterministic next-ref 계산
- 명시된 기존 Round 작업서 수정의 exact ref 사용
- 예정 ref와 write 직전 충돌 재검증 지시를 same-session Reader 요청에 전달
- focused/shared tests, installer와 실제 새 Codex 세션 검증

Exclude:

- 단순 작업서 검토·확인·조사 요청을 authoring으로 승격
- 예정 ref를 canonical reservation이나 project source로 저장
- 두 세션 사이의 원자적 Round 번호 예약
- 최초 native title 이후 강제 retitle
- Codex SQLite, rollout, App Server와 사용자 전역 config 수정
- plugin, MCP, daemon, watcher와 외부 network service

## 실행 계획

| Step | 상태 | 변경 범위 | 완료 경계 |
|---|---|---|---|
| R023/S01 | accepted | Project·Reader 기준, Work source | 생성·수정·검토와 예정 ref 권한 경계를 일관되게 정의함 |
| R023/S02 | accepted | hook runtime, Reader contract와 tests | 작업서 착수만 title hint로 queue하고 기존 흐름을 보존함 |
| R023/S03 | accepted | focused/shared tests, install, live CLI와 Progress | 신규 child 제목과 회귀를 검증하고 source를 complete/accepted로 정합화함 |

## Completion Criteria

- [x] `R015 하위 신규 라운드 작업서를 만들겠습니다`는 다음 child ref를 계산한다.
- [x] `Z` 다음은 `AA`, `AE` 다음은 `AF`로 계산한다.
- [x] `신규 라운드 작업서를 만들겠습니다`는 다음 top-level Round ref를 계산한다.
- [x] `R015-AF 작업서를 수정해 주세요`는 exact existing ref를 사용한다.
- [x] `R015-AF 작업서 수정안을 검토해 주세요`는 authoring 할당으로 처리하지 않는다.
- [x] 예정 ref는 title hint와 원 요청에 전달되며 source에 예약 상태를 쓰지 않는다.
- [x] 대표문구는 사용자의 주 언어로 작업 내용을 설명하는 5자 이내 문구다.
- [x] R022의 기존 Round 수행·자유 검토·정렬·10개·fail-open 회귀가 유지된다.
- [x] focused/shared tests, skill validation, compileall, installer와 실제 새 세션 검증이 통과한다.

## Verification

1. 순수 함수 테스트로 parent/child next-ref와 Excel suffix 경계를 검증한다.
2. 생성·수정·검토 prompt를 pending/direct Reader 경로에서 검증한다.
3. 기존 assignment, free-form, dependency 확인, queue failure와 opt-out 회귀를 검증한다.
4. Reader/project contract, shared suite, compileall, skill validation과 diff를 검증한다.
5. 설치본을 갱신하고 새 Codex 세션에서 신규 child 예정 ref title을 확인한다.

## Stop Conditions

1. 예정 ref를 canonical reservation으로 저장하지 않으면 안전하게 진행할 수 없다.
2. 단순 검토와 실제 문서 write 착수를 보수적으로 구분할 수 없다.
3. 완료에 최초 native title 이후 강제 retitle 보장이 필요하다.
