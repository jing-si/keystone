---
doc_type: progress
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-07", accepted_by: main}
work_status: complete
step_ref: R008/S07
work_ref: R008/skill-runtime-traceability
finalization: {state: complete, acceptance_ref: R008/S07/main-acceptance}
key:
  id: key.work.skill-runtime-traceability.progress
  refs:
    - key.topic.progress-update
    - key.topic.skill-source
    - key.topic.code-anchor
    - key.topic.artifact-graph
    - key.topic.verification
---

# Skill Runtime Traceability and Self-Host E2E 진행 기록

## 현재 상태

- Step: R008/S07
- Work status: complete
- Approval state: accepted
- Active: false
- Finalization state: complete
- Acceptance ref: R008/S07/main-acceptance
- Resume point: none — R008 complete and accepted; external pilot은 후속 round 후보

Active steps: []

## 준비 증거

- 여섯 installed skill package와 repository source가 일치한다.
- Repository production owner는 여섯 `SKILL.md`에 존재한다.
- 현재 repository typed graph에는 declared `verifies` relation이 없다.
- R008 최초 baseline에서는 Linker 175, Author 73, Reader 2, skill contract 11 tests가 통과했다.
- 병행 중인 Coordinator 변경이 포함된 재검토 시점에는 package-level skill contract 17 tests 중
  2 tests가 문자열 경계 불일치로 실패했다. R008 결함과 혼합하지 않고 S07 전 별도 baseline으로
  정리해야 한다.
- README의 current-source navigation은 아직 R006 round를 가리키며 S07 navigation closure에서
  최신 active/latest state와 정합화한다.

## 구현 및 검증 결과

- 여섯 `key.skill.*` owner의 production provenance와 project/child/bootstrap governance를 보존했다.
- Public runtime boundary 4개와 실제 contract test 4개만 stable owner로 추가했다. 기준서 연결은
  owner/ref, test evidence는 `test verifies code` typed relation으로 두고 private helper와 나머지
  unit test는 승격하지 않았다.
- Readiness CLI는 `complete`, discovered/parsed/skipped count, path digest와 skipped reason을
  반환한다. Docs scope는 repository-owned skill/code/config/schema/API/test ref를 lazy-resolution
  warning으로 유지한다.
- Matching single/multiple-backtick inline code metadata example을 passive data로 처리한다.
- Schema-v4 global state는 active Step이 없을 때만 `active_round: none`을 허용해 round 종료를
  active 상태로 위장하지 않는다.
- `key-self-host-scenarios.md`가 actual corpus chain과 cache, dependency, transaction resume,
  companion, truncation, prompt injection, Coordinator forgery, parallel-round correction fixture를
  연결한다.
- Actual self-host contract는 docs/repository readiness, 8개 anchor owner, 4개 verification edge,
  repository graph validation과 R008/R009 finalization을 한 실행에서 검증했다.
- Linker 219, Author 81, Coordinator 27, Reader 2, contract/self-host 19 tests가 통과했다.
- Graph sync는 `not_applicable`이다. Code owner를 먼저 독립 direct refresh하고 각 test relation을
  이미 존재하는 owner에 surface별로 추가했으며, 미적용 sibling surface와 원자적으로 결속해야 할
  canonical mutation은 없었다.
- External pilot, OS/CI matrix, global install, marketplace, publication, push와 merge는 범위 밖으로
  유지한다.
