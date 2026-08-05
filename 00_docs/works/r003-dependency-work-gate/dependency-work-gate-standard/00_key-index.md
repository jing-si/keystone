---
doc_type: work
created_at: "2026-07-25"
status: active
approval:
  state: accepted
  accepted_at: "2026-07-25"
  accepted_by: main
work_status: accepted
key:
  id: key.work.dependency-work-gate-standard.index
  refs:
    - key.doc.work
    - key.topic.artifact-graph
    - key.topic.work-sequence
    - key.topic.work-recovery
work_id: dependency-work-gate-standard
title: Dependency and Work Gate Standard
owner_lane: keystone-author
work_type:
  - documentation
  - standard
risk_level: high
---

# Dependency and Work Gate Standard

<!-- key: id=key.work.dependency-work-gate-standard.index.summary refs=key.section.summary key.topic.artifact-graph -->
## 요약

`depends_on`을 공식 의미 관계로 정의하고 실행 gate와 분리한다. 단계별 dependency, legacy
HTML syntax, dangling target, self-reference, cycle과 상태 판정 계약을 기준서에 확정한다.

<!-- key: id=key.work.dependency-work-gate-standard.index.documents refs=key.doc.work key.topic.progress-update -->
## 문서

- 작업서: `key-work-dependency-work-gate-standard.md`
- 진행 기록: `key-progress.md`

<!-- key: id=key.work.dependency-work-gate-standard.index.current-status refs=key.topic.status key.step.s01 -->
## 현재 상태

- Status: accepted
- Current step: S01
