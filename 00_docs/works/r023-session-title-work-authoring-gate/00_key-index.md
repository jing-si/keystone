---
doc_type: work_round
created_at: "2026-08-28"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-28", accepted_by: main}
round_status: accepted
key:
  id: key.work.round.r023-session-title-work-authoring-gate.index
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

# R023 Session Title Work Authoring Gate 작업서 색인

R023은 최초 Reader gate에서 작업서 생성·수정 착수가 확정된 요청도 Round 수행 문맥으로
인식해 native thread title에 예정 또는 기존 Round ref를 제공한다.

## 실행 순서

| 순서 | Step | 상태 | 목적 |
|---|---|---|---|
| S01 | Work Authoring Title Contract | accepted | 생성·수정·검토 경계와 예정 Round ref 계산을 기준서에 정렬했다 |
| S02 | Hook Runtime Implementation | accepted | 작업서 착수 감지, next ref 계산과 same-session title hint를 구현했다 |
| S03 | Verification and Closure | accepted | 회귀·설치·실제 새 세션 검증 후 Round를 닫았다 |

- Active Step: 없음

## Round 경계

- 작업서 생성·수정의 실행 의도가 명확한 최초 Reader 문맥에만 제목 힌트를 넣는다.
- 신규 child는 명시된 parent의 선언된 모든 child를 기준으로 다음 Excel suffix를 계산한다.
- 신규 parent는 선언된 모든 parent의 다음 숫자를 비권위 예정 ref로 계산한다.
- 예정 ref는 문서 생성 권한이나 예약이 아니며 Author가 write 직전에 충돌을 다시 확인한다.
- 작업서 검토·확인·조사, 단순 Round 언급과 이미 제목이 정해진 세션의 retitle은 범위 밖이다.

## 복구 규칙

1. Goal과 Step 상태는 이 Index에서 확인한다.
2. 세부 의미·수용 기준·검증은 Work Order를 읽는다.
3. 실제 결과와 resume point는 aggregate Progress를 읽는다.
