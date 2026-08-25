---
doc_type: work
created_at: "2026-08-25"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-25", accepted_by: main}
work_status: complete
key:
  id: key.work.worktree-locator-navigation.index
  refs:
    - key.doc.work
    - key.topic.work-recovery
    - key.topic.work-sequence
    - key.topic.work-execution
    - key.topic.keystone-metadata
    - key.topic.skill-contract
    - key.topic.verification
    - key.boundary.scope-control
    - key.work.decisions.dec-works-033
    - key.work.worktree-locator-navigation.order
    - key.work.worktree-locator-navigation.progress
work_id: worktree-locator-navigation
title: Worktree Locator and Targeted Work Discovery
owner_lane: main
work_type: [standard, metadata, skill_runtime, verification]
risk_level: medium
---

# Worktree Locator and Targeted Work Discovery

## 문서

- 작업서 및 Change Set: `key-work-worktree-locator-navigation.md`
- 진행 기록: `key-progress.md`
- S01 진행 기록: `key-progress-s01.md`
- S02 진행 기록: `key-progress-s02.md`
- S03 진행 기록: `key-progress-s03.md`
- 사용자 방향 Q&A log: `clarify/20260825T030754Z-worktree-locator-navigation.md`

## 현재 상태

- Round: `R016`
- Work status: `complete`
- Approval state: `accepted`
- Active Step: 없음
- Accepted Steps: [`R016/S01`, `R016/S02`, `R016/S03`]
- Planned Steps: []
- Next action: 없음. Accepted implementation과 residual risk를 유지한다.

## 복구 순서

1. Progress에서 R016의 active Step과 실제 검증 상태를 확인한다.
2. Work Order의 사용자 방향과 `key.worktree.path` 의미를 읽는다.
3. S01~S03의 scope와 stop condition을 확인한다.
4. 후속 변경은 새 승인 범위에서 별도 Work로 진행한다.
