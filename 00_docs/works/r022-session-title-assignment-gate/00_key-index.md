---
doc_type: work_round
created_at: "2026-08-28"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-28", accepted_by: main}
round_status: accepted
key:
  id: key.work.round.r022-session-title-assignment-gate.index
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

# R022 Session Title Assignment Gate 작업서 색인

R022는 최초 Reader 진입에서 미완료 라운드를 안내하고, 사용자가 기존 라운드 수행 의도를
명시한 경우에만 Codex native thread title에 Keystone Round 힌트를 제공한다.

## 실행 순서

| 순서 | Step | 상태 | 목적 |
|---|---|---|---|
| S01 | Assignment Gate Contract | accepted | 선택·검토·상태 확인의 의미와 제목 형식을 기준서에 정렬했다 |
| S02 | Hook Runtime Implementation | accepted | 미완료 라운드 안내와 명시적 할당 감지를 구현했다 |
| S03 | Verification and Closure | accepted | 회귀·설치·실제 새 세션 검증 후 Round를 닫았다 |

- Active Step: 없음

## Round 경계

- 제목은 최초 명시적 기존 라운드 수행에만 `RNNN[-SUFFIX]:대표문구`로 힌트한다.
- 검토·조사·확인, 상태 조회와 신규 라운드 준비에는 Keystone 제목 힌트를 넣지 않는다.
- `accepted`, `cancelled`가 아닌 부모·하위 라운드를 부모 번호와 child Excel suffix 오름차순으로
  최대 10개 표시한다.
- 10개 초과는 `외 N개`로 축약하고 상태 이상 가능성을 알린다.
- 사용자 전역 config, Codex DB, App Server, plugin, MCP와 daemon은 범위 밖이다.

## 복구 규칙

1. Goal과 Step 상태는 이 Index에서 확인한다.
2. 세부 의미·수용 기준·검증은 Work Order를 읽는다.
3. 실제 결과와 resume point는 aggregate Progress를 읽는다.
