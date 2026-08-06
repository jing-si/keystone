---
doc_type: work_order
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-06", accepted_by: main}
work_status: complete
key:
  id: key.work.markdown-hierarchy-governance.order
  refs:
    - key.doc.work
    - key.topic.keystone-metadata
    - key.topic.artifact-graph
    - key.topic.change-set
    - key.topic.verification
---

# Markdown Hierarchy and Governance 작업서 및 Change Set

<!-- key: id=key.work.markdown-hierarchy-governance.order.goal refs=key.section.goal key.topic.artifact-graph -->
## Goal

Markdown의 실제 heading 구조를 document→section→item effective metadata 계산에 사용하고,
`governed_by`의 declared metadata, effective provenance와 typed relation이 하나의 승인된 의미를
사용하도록 정합화한다.

<!-- key: id=key.work.markdown-hierarchy-governance.order.scope refs=key.section.scope key.topic.keystone-metadata -->
## Scope

Include:

- Markdown adapter의 모든 heading level/offset 구조 수집
- Heading stack을 사용한 actual enclosing section 계산
- Document/section/item lifecycle, approval, source authority와 governance inheritance
- `governed_by` child 합성 의미와 document-node relation direction 결정
- Declared/effective metadata와 emitted typed relation 정합성
- 공식 Markdown 예시의 parse→validate regression

Exclude:

- 모든 Markdown heading을 독립 graph owner로 승격하는 migration
- 기존 문서 item metadata 일괄 annotation
- Graph wire version 변경과 impact lifecycle grading
- 승인 없이 governance나 source authority 의미를 선택하는 구현

<!-- key: id=key.work.markdown-hierarchy-governance.order.baseline refs=key.topic.impact-review key.topic.verification -->
## Baseline Findings

1. Parser는 `document_node`와 마지막 annotated `current_section_node`만 유지한다.
2. Unannotated heading은 section context를 닫거나 바꾸지 않는다.
3. Child `governed_by`가 parent set 밖의 값을 가지면 runtime은 authority expansion으로 진단하고
   effective value를 parent로 되돌린다.
4. Relation builder는 같은 child declaration으로 relation을 생성해 effective provenance와 graph
   relation이 서로 달라질 수 있다.
5. Relation policy는 `governed_by` source를 output artifact로만 허용해 document item declaration을
   invalid direction으로 판정한다.

<!-- key: id=key.work.markdown-hierarchy-governance.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: source Markdown 구조와 graph hierarchy·governance 의미를 일치시킨다.
- Required candidates: Markdown adapter/parser, hierarchy builder, relation policy와 관련 tests
- Conditional candidates: Artifact Graph/Author/Linker 기준서와 decision record
- Acceptance owner: Main
- Decision gate: `DEC-R008-S02-001`로 child governance의 ordered union, declared-only typed relation,
  approval/source-authority boundary 유지를 확정했다.
- Graph handling: 결정된 semantics가 source metadata에 영향을 주면 Linker가 delta를 분류한다.

<!-- key: id=key.work.markdown-hierarchy-governance.order.approach refs=key.section.recommended-approach key.topic.verification -->
## Recommended Approach

1. Unannotated sibling/nested heading과 table/list item을 RED fixture로 만든다.
2. Metadata node 생성과 별개로 모든 heading의 level/offset stack을 계산한다.
3. 수락된 `DEC-R008-S02-001`의 ordered union을 effective metadata에 적용한다.
4. Declared-only typed relation을 유지해 inherited relation을 child source에 복제하지 않는다.
5. Document item→standard/decision direction 또는 provenance-only 정책을 validator와 함께 고정한다.
6. 공식 문서 예시를 source-only parse→validate로 검증한다.

<!-- key: id=key.work.markdown-hierarchy-governance.order.completion refs=key.topic.acceptance key.topic.integration-verification -->
## Completion Criteria

- [x] Unannotated heading이 이전 annotated section의 item을 잘못 소유하지 않는다.
- [x] Nested heading level에 따라 parent_id가 결정적으로 계산된다.
- [x] `governed_by` child semantics가 승인된 decision과 일치한다.
- [x] Effective governance와 emitted typed relation이 모순되지 않는다.
- [x] Approval/source authority expansion 규칙은 기존 authority boundary를 약화하지 않는다.
- [x] Document/section/item governance 예시가 parse→validate를 통과한다.
- [x] Existing parser, graph validator와 repository regression이 통과한다.

## Acceptance Result

- Main acceptance: 2026-08-06
- Decision: `DEC-R008-S02-001`의 ordered union과 declared-only relation semantics
- Markdown hierarchy: ATX와 Setext heading의 level/offset, unannotated boundary와 nested parent를
  source-only reconstruction에 적용했다.
- Governance: document/section/item/claim/decision/work/output source의 declared
  `governed_by -> standard/decision` 방향을 validator가 허용한다.
- Graph sync: `not_applicable`. 기준서와 Linker runtime contract를 동기화했지만 source metadata의
  canonical node/relation mutation은 없다.

<!-- key: id=key.work.markdown-hierarchy-governance.order.verification refs=key.topic.verification -->
## Verification

- Unannotated sibling/nested heading hierarchy fixtures
- Parent/child governance, approval와 source authority table tests
- Official Markdown examples parse→validate E2E
- Linker full suite와 repository graph validation
- `git diff --check`

<!-- key: id=key.work.markdown-hierarchy-governance.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. Governance set semantics 또는 relation representation에 둘 이상의 유효한 정책 선택이 남는다.
2. 기존 accepted source authority나 approval boundary를 변경해야 한다.
3. Graph wire compatibility 변경 없이는 deterministic result를 만들 수 없다.
4. 전체 corpus metadata migration이 필요해 현재 Work scope를 넘는다.
