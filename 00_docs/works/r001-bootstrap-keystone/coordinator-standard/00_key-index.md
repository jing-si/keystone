---
doc_type: work
key:
  id: key.work.coordinator-standard.index
  refs:
    - key.doc.work
    - key.role.coordinator
    - key.role.subagent
    - key.standard.subagent
    - key.topic.orchestration
    - key.topic.acceptance
work_id: coordinator-standard
title: Coordinator Standard
status: in_progress
owner_lane: main-session
work_type:
  - documentation
  - standard
risk_level: medium
---

# Coordinator Standard

<!-- key: id=key.work.coordinator-standard.index.summary refs=key.role.coordinator key.topic.main-supervised key.role.subagent key.topic.workflow key.section.summary -->

## 요약

`keystone-coordinator`의 main-supervised bounded worker workflow 기준서를 정리한다.

<!-- key: id=key.work.coordinator-standard.index.goal refs=key.role.coordinator key.topic.current-step key.output.context-pack key.topic.report-handling key.topic.verification key.topic.acceptance key.standard.subagent -->

## 목표

Coordinator가 current work step을 복구하고 bounded worker workflow를 조율할 수 있도록
Current Step Brief, Context Pack, worker assignment/report, report handling, review,
verification, single workspace guard, acceptance 기준을 명확히 한다.

<!-- key: id=key.work.coordinator-standard.index.source-standards refs=key.role.coordinator key.topic.source-standard key.doc.standard key.standard.subagent -->

## 원천 기준서

- `00_docs/standards/subagents/key-standard-subagents.md`
- `00_docs/standards/skills/coordinator/key-standard-coordinator.md`

<!-- key: id=key.work.coordinator-standard.index.documents refs=key.doc.work key.topic.progress-update key.topic.document-list -->

## 문서

- 작업서(4): `key-work-coordinator-standard.md`
- 진행 기록(5): `key-progress.md`

<!-- key: id=key.work.coordinator-standard.index.current-status refs=key.topic.work-sequence key.topic.status key.step.s05 -->

## 현재 상태

- Status: in_progress
- Current step: S05
