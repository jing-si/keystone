---
doc_type: work_round
created_at: "2026-08-28"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-28", accepted_by: main}
round_status: accepted
key:
  id: key.work.round.r021-session-title-permission-hardening.index
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.skill-contract
    - key.topic.verification
    - key.boundary.scope-control
    - key.standard.project
    - key.standard.skill.reader
---

# R021 Session Title Permission Hardening 작업서 색인

R021은 R020 자동 세션 제목 helper가 기본 샌드박스에서 Codex 상태 접근에 실패한 결함을
전용 executable의 명시적·최소 권한 승인으로 보강한다.

<!-- key: id=key.work.round.r021.execution-order refs=key.topic.work-sequence key.topic.verification -->
## 실행 순서

| 순서 | Step | 상태 | 목적 |
|---|---|---|---|
| S01 | Permission Contract Alignment | accepted | exact helper executable만 승인하는 권한 경계를 기준서에 반영했다 |
| S02 | Helper and Installer Hardening | accepted | stderr 진단, executable 호출과 installer 검증을 구현했다 |
| S03 | Regression and Closure | accepted | focused·shared·installer·graph·Work State 검증 후 Round를 닫았다 |

- Active Step: 없음

## Round 경계

- generic `python3`, shell 또는 Codex 상태 전체에 대한 broad approval을 만들지 않는다.
- exact session-title helper executable만 승인 대상으로 삼는다.
- 승인 거부 또는 App Server 실패는 exact `/rename` fallback으로 복구한다.
- R015, R018과 완료된 R020의 상태는 변경하지 않는다.
- browser, Playwright, publish와 사용자 전역 config 수정은 포함하지 않는다.

## 복구 규칙

1. R021 목표와 Step 상태는 이 Index에서 확인한다.
2. 권한·설치·검증 경계는 Work Order를 읽는다.
3. 실제 실행 결과와 resume point는 aggregate Progress를 읽는다.
