---
doc_type: work_order
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-06", accepted_by: user}
work_status: complete
key:
  id: key.work.reference-index-contract-standard.order
  refs: [key.doc.work, key.topic.artifact-graph, key.topic.keystone-metadata, key.topic.work-recovery, key.topic.change-set]
---

# Reference Index Contract Standard 작업서 및 Change Set

## Goal

Source-owned ID/ref를 기본 탐색 계약으로 확정하고 Reader의 context readiness, permissionless
Linker index, 선택적 typed graph와 multi-surface transaction을 전체 기준서에서 일관되게 정의한다.

## Prerequisite

- R005 Artifact Graph Synchronization accepted
- DEC-WORKS-025 accepted

## Scope

Include:

- One-owner ID와 ref-first identity, optional typed relation
- Execution과 approval 상태 분리 및 기본 dependency `complete + accepted`
- `requires_verification_of`와 `verifies` 분리
- Declared/effective metadata와 document → section → item 상속
- Transaction/repository validation scope와 conflict-reason retry
- Reader docs-first readiness, Linker external cache, lazy repository scan와 fail-soft fallback
- Permissionless Linker subagent 경계와 Reader↔Linker recursion guard
- Direct single-surface refresh와 multi-surface transaction 분리
- 관련 기준서와 child/root index의 정합화

Exclude:

- `skills/**`와 executable runtime 수정
- R003-R005 accepted 작업 기록 수정
- 외부 DB, user-facing CLI, global install과 외부 소비 repository

## Change Set

- Intent: R005 graph core를 source-owned ID/ref 기본 모델과 필요한 경우의 typed graph로 재정렬한다.
- Changed nodes: Project, Artifact Graph, Subagent, Bootstrap, Init, Reader, Author, Clarify,
  Linker, Coordinator 기준
- Impact seeds: `DEC-WORKS-021`, `DEC-WORKS-024`, dependency gate, finalization, graph transaction
- Required candidates: 관련 기준서, 기준서 색인, R006 work/progress와 Context Map
- Verification: vocabulary 검색, relation 방향, 상태 namespace, index link와 `git diff --check`
- Acceptance: Main이 기준 사이 충돌이 없고 S02-S04의 입력이 완결됐는지 확인한다.

## Completion Criteria

- [x] Owner/ref-first identity와 optional typed graph가 공통 기준에 정의된다.
- [x] Work execution과 approval 및 dependency 조건이 분리된다.
- [x] Verification requirement/evidence와 declared/effective metadata가 분리된다.
- [x] Reader·Linker readiness, freshness, cache authority와 recursion guard가 정의된다.
- [x] Direct refresh와 transaction, transaction/repository validation 범위가 분리된다.
- [x] 모든 관련 skill 기준과 index가 같은 계약을 가리킨다.
- [x] Historical accepted work를 소급 수정하지 않는다.

## Verification

- Accepted vocabulary와 stale vocabulary를 `rg`로 대조한다.
- 모든 relation 예시를 typed relation matrix와 비교한다.
- Reader·Linker·Author·Coordinator 권한과 호출 경계를 교차 검토한다.
- Markdown link, metadata와 `git diff --check`를 검증한다.

## Stop Conditions

1. 기준서 변경에 아직 수락되지 않은 project 의미 결정이 필요하다.
2. S01 완료에 skill 또는 runtime source 수정이 필요하다.
3. Permissionless Linker가 source write나 scope/acceptance 권한을 요구한다.
4. External DB 또는 user-facing command가 기준 계약의 필수 요소가 된다.
