---
doc_type: work_round
created_at: "2026-08-24"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-25", accepted_by: main}
round_status: accepted
key:
  id: key.work.round.r014-reader-progressive-context-loading.index
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.context-readiness
    - key.topic.work-recovery
    - key.topic.skill-contract
    - key.topic.verification
    - key.standard.skill.reader
---

# R014 Reader Progressive Context Loading 작업서 색인

R014는 세션 시작 Reader가 프로젝트 상태와 탐색 지도를 먼저 복구하고, 선택된 작업에 필요한
상세 기준과 Artifact Graph 문맥만 점진적으로 읽도록 초기 context readiness 계약을 경량화한다.

이 Round는 S01 기준 계약, S02 Reader skill/focused regression, S03 workflow scenario와 contract
parity 검증을 모두 통과해 `complete + accepted`로 닫혔다.

<!-- key: id=key.work.round.r014.execution-order refs=key.topic.work-sequence key.topic.context-readiness -->
## 실행 순서

| 순서 | Step | 상태 | 목적 |
|---|---|---|---|
| S01 | Progressive Reader Orientation Contract | complete + accepted | 초기 파악, 작업 선택, 작업 준비와 구현 직전의 읽기 깊이 및 상세 기준서 확장 조건을 정의한다 |
| S02 | Reader Skill Contract and Focused Regression | complete + accepted | Reader skill에서 Linker와 상세 기준서 읽기를 조건부로 만들고 focused regression으로 고정한다 |
| S03 | Context Budget and Workflow Verification | complete + accepted | active Round 0개·1개·복수와 명시적 graph 요청 시나리오에서 점진적 context loading을 검증한다 |

현재 active Step은 없다. 세부 Goal, Scope, completion criteria와 검증 결과는 Work Order와
aggregate Progress에서 확인한다.

<!-- key: id=key.work.round.r014.boundaries refs=key.boundary.scope-control key.topic.context-readiness -->
## Round 경계

- Canonical Work State authority, schema와 parent/child Round 의미를 변경하지 않는다.
- Reader의 read-only, accepted/pending authority와 multi-active Round focus gate를 유지한다.
- 상세 기준서와 Linker를 제거하지 않고 선택된 작업의 필요에 따라 늦게 읽도록 한다.
- Repository artifact scope, source views와 deep graph interpretation은 초기 기본 경로에 넣지 않는다.
- 초기 경량화를 이유로 구현·검증 직전의 적용 기준 확인을 생략하지 않는다.

<!-- key: id=key.work.round.r014.reading-rules refs=key.topic.work-recovery key.topic.work-sequence -->
## 복구 규칙

1. R014 목표와 Step 순서는 이 Index를 읽는다.
2. 상세 범위와 completion criteria는 Work Order를 읽는다.
3. 실제 상태, 증거와 resume point는 Progress를 읽는다.
4. S01~S03은 2026-08-25 검증과 Main acceptance로 `complete + accepted`이며, R014에 남은 active
   Step이나 resume point는 없다.
