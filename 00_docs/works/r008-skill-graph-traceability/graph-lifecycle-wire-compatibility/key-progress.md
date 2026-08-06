---
doc_type: progress
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: pending}
work_status: planned
step_ref: R008/S06
work_ref: R008/graph-lifecycle-wire-compatibility
key:
  id: key.work.graph-lifecycle-wire-compatibility.progress
  refs:
    - key.topic.progress-update
    - key.topic.artifact-graph
    - key.topic.impact-review
    - key.topic.verification
---

# Graph Lifecycle and Wire Compatibility 진행 기록

## 현재 상태

- Step: R008/S06
- Work status: planned
- Approval state: pending
- Active: false
- Finalization state: not started
- Resume point: evidence/lifecycle impact matrix와 wire compatibility decision 준비

Active steps: []

## 준비 증거

- Canonical 기준서의 graph node는 여섯 핵심 field와 `active|deprecated|removed` lifecycle을
  정의하지만 runtime schema version 1은 declared/effective metadata, parent와 여섯 lifecycle을
  직렬화한다.
- Impact traversal은 relation evidence와 lifecycle을 보지 않고 policy grade만 적용한다.
- Snapshot validator는 active relation의 retired target은 검사하지만 retired source에서 시작하는
  active relation을 검사하지 않는다.
- Repository version은 `0.6.0-dev`이며 wire compatibility/release policy가 고정되지 않았다.

## 다음 작업

1. Evidence/lifecycle별 maximum impact grade와 exclusion 의미를 기준서로 확정한다.
2. Retired source/target relation validation matrix를 구현한다.
3. v1 permissive compatibility와 v2 canonical wire 선택을 Decision 또는 Clarify로 확정한다.
4. v1→v2 migration/round-trip과 version evidence를 검증한다.
