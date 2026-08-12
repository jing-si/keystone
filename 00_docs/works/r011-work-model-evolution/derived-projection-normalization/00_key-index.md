---
doc_type: work
created_at: "2026-08-10"
document_lifecycle: active
key:
  id: key.work.derived-projection-normalization.index
  refs:
    - key.doc.work
    - key.topic.document-system
    - key.topic.work-recovery
    - key.topic.artifact-graph
    - key.topic.skill-contract
    - key.topic.verification
work_id: derived-projection-normalization
title: Derived Projections and Document Normalization
owner_lane: main
work_type: [standard, implementation, test, verification]
risk_level: high
---

# Derived Projections and Document Normalization

## 문서

- 작업서 및 Change Set: `key-work-derived-projection-normalization.md`
- 진행 기록: `key-progress.md`

## 상태 복구

- Work identity와 scope: 이 Index와 Work Order
- Work/Step current state, evidence와 resume point: `key-progress.md`
- Round/active/latest aggregate: canonical Work State Runtime
- Issue: `KS-DERIVED-PROJECTION-NORMALIZATION-001`

이 Index는 `work_status`, `approval` 또는 `global_state`를 별도 권위로 복제하지 않는다. Legacy
Index projection은 읽기 호환하되 current source와 다르면 stale diagnostic 대상이다.
