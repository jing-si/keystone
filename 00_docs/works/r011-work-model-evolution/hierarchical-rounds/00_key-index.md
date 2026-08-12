---
doc_type: work
created_at: "2026-08-10"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-11", accepted_by: main}
work_status: complete
key:
  id: key.work.hierarchical-rounds.index
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.work-recovery
    - key.topic.skill-contract
    - key.topic.verification
    - key.claim.r011.round-hierarchy-two-level-limit
    - key.claim.r011.depth-overflow-restructure
    - key.claim.r011.parent-global-round-authority
    - key.claim.r011.child-local-execution-authority
    - key.claim.r011.parent-child-aggregate-gate
work_id: hierarchical-rounds
title: Hierarchical Rounds
owner_lane: main
work_type: [standard, implementation, test, verification]
risk_level: high
global_state:
  active_round: R011
  latest_accepted_round: R010
  active_steps: [R011/S03]
---

# Hierarchical Rounds

## 문서

- 작업서 및 Change Set: `key-work-hierarchical-rounds.md`
- 진행 기록: `key-progress.md`

## 현재 상태

- Step: R011/S02
- Work status: complete
- Approval state: accepted
- Active: false
- Finalization state: complete — `R011/S02/main-acceptance`
- Issue: `KS-HIERARCHICAL-ROUND-001`
- Next action: S02는 accepted history로 보존하고 S03 Project Signal and Contract Triage의
  source-evidence 경계를 따른다.

R011/S02는 `R011/S02/main-acceptance`로 complete + accepted + finalized됐고 active set에서
제외됐다. 현재 유일 active Step은 R011/S03이다.
