---
doc_type: work
created_at: "2026-09-14"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-10-13", accepted_by: user}
key:
  id: key.work.unified-state-management.index
  refs:
    - key.doc.work
    - key.topic.work-recovery
    - key.topic.work-sequence
    - key.work.unified-state-management.order
    - key.work.unified-state-management.progress
work_id: unified-state-management
title: 상태 통합 관리
owner_lane: main
work_type: [standard, skill_runtime, python_runtime, verification]
risk_level: high
---

# 상태 통합 관리

## 문서

- 작업서: `key-work-unified-state-management.md`
- 진행 기록: `key-progress.md`

현재 Work 상태와 다음 행동은 Progress에서, 범위·수용 기준과 Step 계획은 Work Order에서
복구한다. 이 색인에는 선택적 Work 상태 복제값을 두지 않는다.
