---
doc_type: decision_record
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-06", accepted_by: user}
key:
  id: key.work.markdown-hierarchy-governance.decisions
  refs:
    - key.doc.decision
    - key.topic.keystone-metadata
    - key.topic.artifact-graph
    - key.topic.acceptance
---

# Markdown Hierarchy and Governance 결정 기록

<!-- key: id=key.decision.r008.s02.governed-by-union kind=decision refs=key.topic.keystone-metadata key.topic.artifact-graph -->
## DEC-R008-S02-001: Child governance는 부모와 합집합한다

- 결정일: 2026-08-06
- 상태: accepted
- 결정 주체: user
- 적용 범위: R008/S02와 이후 document → section → item effective metadata 계산

### 결정

1. Child의 effective `governed_by`는 부모 effective set 뒤에 child declared set을 중복 없이
   추가한 ordered union으로 계산한다.
2. Child가 새 governing standard나 decision을 선언하는 것은 authority 확대가 아니라 제약
   추가로 해석한다. `governance_authority_expansion` diagnostic과 parent 값 clamp를 사용하지 않는다.
3. Typed `governed_by` relation은 source에 직접 선언한 target만 emit한다. 부모에서 상속한
   target을 child relation으로 복제하지 않는다.
4. `approval`과 source authority의 child expansion 금지는 그대로 유지한다.
5. Document, section, item, claim, decision, work order와 work step은 standard 또는 decision을
   향해 `governed_by`를 선언할 수 있다. Output artifact의 기존 방향도 유지한다.

### 근거

- 부모 규칙에 자식 규칙을 추가하는 것은 적용 제약을 강화하며 source authority를 넓히지 않는다.
- Effective provenance와 declared typed relation이 서로 다른 target을 보고하던 기존 clamp를
  제거할 수 있다.
- 일반 typed relation은 상속하지 않는 기존 원칙을 유지하므로 graph edge가 불필요하게
  증식하지 않는다.

### 제외

- Approval/source authority의 상속 또는 확대 규칙 변경
- Graph wire version 변경
- 기존 corpus metadata 일괄 migration
