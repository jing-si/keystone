---
doc_type: work
created_at: "2026-08-07"
document_lifecycle: active
approval: {state: pending}
work_status: planned
key:
  id: key.work.whole-flow-self-host-e2e.index
  refs:
    - key.doc.work
    - key.topic.work-sequence
    - key.topic.work-recovery
    - key.topic.integration-verification
    - key.topic.finalization
    - key.role.coordinator
    - key.topic.verification
work_id: whole-flow-self-host-e2e
title: Whole-Flow Self-Host E2E
owner_lane: main
work_type: [integration, test, verification]
risk_level: high
---

# Whole-Flow Self-Host E2E

## 문서

- 작업서 및 Change Set: `key-work-whole-flow-self-host-e2e.md`
- 진행 기록: `key-progress.md`

## 현재 상태

- Step: R010/S06
- Work status: planned
- Approval state: pending
- Active: false
- Finalization state: pending
- Step-start dependency: waiting — S01-S05 각각의 `complete + accepted`가 `steps: [S06]`에
  적용된다.
- Work-completion dependency: waiting — 같은 S01-S05 조건이 Work completion에도 적용된다.
- Finalization pre-gate: waiting — S01-S05 각각의 finalization `complete` 또는 Main-accepted
  waiver, acceptance ref, finalization manifest/envelope digest와 package-owned Author runner pass가
  필요하다.
- Pre-gate boundary: waiting 중에는 read-only orientation, evidence inspection과 source-write-free
  RED scenario 설계만 허용한다. Repository source write, `in_progress` 전이, schema/authority
  commitment와 acceptance는 금지하며, 실행된 `early_work`는 주장하지 않는다.
- Next action: Step-start gate와 finalization pre-gate가 모두 충족되면 temporary clean checkout의
  isolated fixture document root/fixture Round에서 10개 adversarial 및 7개 crash/resume scenario
  harness를 구현한다. Live R010 terminal closure는 S07만 소유한다.

현재 active Step의 권위 있는 목록은 R010 round index, root works index와 Context Map을 따른다.
