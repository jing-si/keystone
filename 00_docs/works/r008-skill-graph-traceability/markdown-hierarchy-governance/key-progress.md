---
doc_type: progress
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-06", accepted_by: main}
work_status: complete
step_ref: R008/S02
work_ref: R008/markdown-hierarchy-governance
finalization: {state: complete, acceptance_ref: R008/S02/main-acceptance}
key:
  id: key.work.markdown-hierarchy-governance.progress
  refs:
    - key.topic.progress-update
    - key.topic.keystone-metadata
    - key.topic.artifact-graph
    - key.topic.verification
---

# Markdown Hierarchy and Governance 진행 기록

## 현재 상태

- Step: R008/S02
- Work status: complete
- Approval state: accepted
- Active: false
- Finalization state: complete
- Acceptance ref: R008/S02/main-acceptance
- Resume point: R008/S03 source Step registry와 expanded-event graph fixture

Active steps: []

## 준비 증거

- Markdown adapter는 metadata-bearing heading만 parser에 전달한다.
- `Security` annotated heading 뒤의 unannotated `Billing` heading 아래 item이 현재
  `Security`의 자식으로 복구되며 diagnostic이 없다.
- Document item의 `governed_by` 선언은 현재 `governance_authority_expansion`과
  `invalid_relation_direction`을 함께 발생시킨다.
- 기준서는 자식 source authority와 approval 확대를 금지하지만 `governed_by`의 child 합성
  규칙은 canonical set operation으로 고정하지 않았다.
- 사용자는 2026-08-06에 child effective governance를 parent와 child declared target의 ordered
  union으로 계산하고 approval/source authority boundary를 유지하는 안을 수락했다.
- Work-local `DEC-R008-S02-001`은 inherited governance를 child relation으로 복제하지 않고
  child가 직접 선언한 `governed_by` relation만 emit하도록 확정한다.

## 다음 작업

1. R008/S03에서 source Work/Step registry와 invalid gate fixture를 고정한다.
2. Legacy completion candidate와 expanded-event SCC/cycle evaluation을 구현한다.

## 구현 및 검증 결과

- RED fixture는 child governance clamp, unannotated sibling의 stale parent, document-item
  relation direction과 Setext heading classification을 각각 재현했다.
- Markdown adapter는 기존 `metadata_blocks()` 3-tuple API를 유지하고 내부 context에 target
  offset, heading level과 nearest annotated ancestor offset을 추가했다.
- ATX와 Setext heading 전체 stack에서 같은 level의 unannotated heading은 이전 annotated
  section을 닫고, nested unannotated heading은 가장 가까운 annotated ancestor를 유지한다.
- Effective governance는 parent-first ordered union이며 중복을 제거한다. Typed relation은
  child declared target만 emit한다.
- Approval과 source authority expansion diagnostic/clamp는 기존대로 통과했다.
- Linker 188, Author 75, Reader 2, skill contract 18 tests passed.
- Fresh docs readiness: owners 924, refs 2,889, errors 0, warnings 129.
- Fresh repository readiness: owners 930, refs 2,889, typed edges 20, errors 0,
  locator warnings 124.
- Repository graph validator, compileall과 `git diff --check` passed.
- Graph sync disposition: `not_applicable`; graph metadata owner/relation 변화 없음.
