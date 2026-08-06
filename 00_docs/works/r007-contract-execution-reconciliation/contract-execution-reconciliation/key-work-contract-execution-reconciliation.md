---
doc_type: work_order
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-06", accepted_by: user}
work_status: complete
key:
  id: key.work.contract-execution-reconciliation.order
  refs: [key.doc.work, key.topic.artifact-graph, key.topic.finalization, key.topic.verification, key.topic.change-set]
---

# Contract Execution Reconciliation 작업서 및 Change Set

## Goal

문서 계약을 parser, validator, impact planner, transaction retry, finalization과 repository
readiness가 같은 의미로 실행하도록 연결한다.

## Scope

Include:

- `complete` execution과 `accepted` approval을 분리한 finalization schema v3
- 단일 relation policy와 `requires_verification_of` traversal/planning
- document → section → item effective metadata, structured dependency와 work gate evaluator
- conflict reason별 transaction retry
- transaction/repository validation scope와 strict unknown field
- ambiguous owner, taxonomy ref, kind-aware locator, multi-generation cache, scan budget와 internal wrapper
- 공식 경로와 기존 suite 회귀 검증

Exclude:

- 외부 소비 프로젝트 pilot과 실제 global install/publication
- 기존 accepted work 기록의 소급 migration
- source를 자동 수정하거나 acceptance를 자동 부여하는 기능

## Completion Criteria

- [x] finalization v3가 `complete`와 `approval.state: accepted`를 독립 검증한다.
- [x] 공식 relation이 parse → validate → traverse → plan에서 끊기지 않는다.
- [x] effective metadata와 structured dependency/work gate가 runtime 값으로 복구된다.
- [x] retry가 conflict reason별 변경 조건을 적용한다.
- [x] repository scope가 source를 발견하고 full/subset omission을 구분한다.
- [x] owner/ref index가 ambiguous owner와 taxonomy refs를 구분하고 bounded scan을 수행한다.
- [x] Linker와 Author 전체 회귀 suite가 통과한다.
- [x] Main이 변경 결과를 검토하고 acceptance를 결정한다.

## Stop Conditions

1. Accepted source 의미를 변경하는 새 정책 결정이 필요하다.
2. 외부 repository 또는 global 설치 환경의 mutation이 필요하다.
3. 기존 사용자 변경과 충돌한다.
