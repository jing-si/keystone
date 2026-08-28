---
doc_type: work
created_at: "2026-08-26"
document_lifecycle: active
approval: {state: pending}
work_status: planned
key:
  id: key.work.keymeta-bounded-discovery.index
  refs:
    - key.doc.work
    - key.topic.work-recovery
    - key.topic.work-sequence
    - key.topic.context-readiness
    - key.topic.artifact-graph
    - key.topic.keystone-metadata
    - key.topic.skill-contract
    - key.topic.verification
    - key.boundary.scope-control
    - key.standard.project
    - key.standard.artifact.graph
    - key.standard.skill.linker
    - key.work.keymeta-bounded-discovery.order
    - key.work.keymeta-bounded-discovery.progress
work_id: keymeta-bounded-discovery
title: Keymeta-First Bounded Discovery
owner_lane: main
work_type: [standard, skill_runtime, graph_runtime, verification]
risk_level: high
---

# Keymeta-First Bounded Discovery

## 문서

- 작업서 및 Change Set: `key-work-keymeta-bounded-discovery.md`
- 진행 기록: `key-progress.md`

## 현재 상태

- Round: `R018`
- Work status: `planned`
- Approval state: `pending`
- Active Step: 없음
- Accepted Steps: []
- Planned Steps: [`R018/S01`, `R018/S02`, `R018/S03`, `R018/S04`]
- Next action: 사용자가 R018 진행을 명시하면 S01에서 discovery contract와 기준서 정합화를
  시작한다.

## 복구 순서

1. Progress에서 R018의 현재 상태와 resume point를 확인한다.
2. Work Order에서 키메타 anchor, bounded expansion, full-scan 경계와 수용 기준을 읽는다.
3. 사용자의 명시적 진행 요청이 있는 경우에만 S01을 시작한다.
4. S01이 accepted 의미를 확정하기 전에는 production runtime과 skill source를 수정하지 않는다.
