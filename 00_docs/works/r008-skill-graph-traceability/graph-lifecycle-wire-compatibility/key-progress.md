---
doc_type: progress
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-07", accepted_by: main}
work_status: complete
step_ref: R008/S06
work_ref: R008/graph-lifecycle-wire-compatibility
finalization: {state: complete, acceptance_ref: R008/S06/main-acceptance}
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
- Work status: complete
- Approval state: accepted
- Active: false
- Finalization state: complete
- Acceptance ref: R008/S06/main-acceptance
- Resume point: R008/S07 runtime/test traceability와 actual-corpus self-host E2E

Active steps: []

## 준비 증거

- Canonical 기준서의 graph node는 여섯 핵심 field와 `active|deprecated|removed` lifecycle을
  정의하지만 runtime schema version 1은 declared/effective metadata, parent와 여섯 lifecycle을
  직렬화한다.
- Impact traversal은 relation evidence와 lifecycle을 보지 않고 policy grade만 적용한다.
- Snapshot validator는 active relation의 retired target은 검사하지만 retired source에서 시작하는
  active relation을 검사하지 않는다.
- Repository version은 `0.6.0-dev`이며 wire compatibility/release policy가 고정되지 않았다.

## 구현 및 검증 결과

- Active declared relation은 relation policy grade를 유지하고, owner-attested observed는
  `strong_candidate`, unattested observed와 inferred는 `weak_candidate`, deprecated는
  `informational`로 제한한다. Archived, superseded, removed relation/node는 active traversal에서
  제외한다.
- Snapshot validator는 active semantic relation의 retired source와 target을 모두 진단한다.
  Active source가 declared 또는 owner-attested observed evidence로 deprecated/removed target을
  향하는 canonical `supersedes`만 예외로 유지한다.
- DEC-R008-S06-001은 strict-core v1 writer, historical extension을 읽는 permissive v1 reader,
  domain-explicit canonical v2와 0.x 및 최초 stable 1.0까지의 v1 read compatibility를 확정했다.
- Source reconstruction은 canonical graph snapshot v2를 만들고, verified transaction은 baseline과
  result가 transaction wire version과 같은지 검사한다. Deterministic v1→v2 migration은 domain에
  맞지 않는 lifecycle을 추정하지 않고 실패한다.
- v1 strict/permissive fixture, v1→v2 normalized round-trip, v2 transaction reconstruction,
  evidence/lifecycle impact matrix와 retired source/target matrix를 포함한 Linker 219 tests가
  통과했다.
- Repository full graph validation은 239개 source를 모두 발견·parse하고 skipped 0,
  complete true, diagnostics 0을 반환했다.
- Graph sync는 `not_applicable`이다. S06은 source-owned graph ID 또는 typed relation을 변경하지
  않고 runtime의 lifecycle/evidence 해석과 versioned wire contract를 정합화했다. Decision 문서의
  새 owner/ref는 source reconstruction과 repository validation으로 검증했다.
