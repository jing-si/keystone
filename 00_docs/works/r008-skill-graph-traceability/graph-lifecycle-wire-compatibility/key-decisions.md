---
doc_type: decision_record
created_at: "2026-08-07"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-07", accepted_by: main}
key:
  id: key.work.graph-lifecycle-wire-compatibility.decisions
  refs:
    - key.doc.decision
    - key.topic.artifact-graph
    - key.topic.impact-review
    - key.topic.verification
---

# Graph Lifecycle and Wire Compatibility 결정 기록

<!-- key: id=key.decision.r008.s06.graph-wire-v2 kind=decision refs=key.topic.artifact-graph key.topic.verification -->
## DEC-R008-S06-001: Canonical graph wire는 v2로 분리한다

- 결정일: 2026-08-07
- 상태: accepted
- 결정 주체: main
- 적용 범위: R008/S06 이후 GraphSnapshot과 graph transaction entity wire

### 결정

1. GraphSnapshot v1 serializer는 exact-field consumer가 읽을 수 있는 여섯 node field와 여섯
   relation field만 출력한다.
2. v1 parser는 기존 conditional `declared_metadata`, `effective_metadata`, `parent_id`를 계속
   읽는 permissive compatibility path로 유지한다.
3. Canonical v2는 node/relation에 `lifecycle_domain`을 추가하고 v1 conditional metadata를
   정식 field로 수용한다.
4. Document domain은 `draft | active | superseded | archived`, artifact domain은
   `active | deprecated | removed`, relation domain은 `active | deprecated | archived | removed`를
   사용한다.
5. v1→v2 migration은 node kind로 lifecycle domain을 결정하고 허용되지 않는 lifecycle 조합은
   자동 변환하지 않고 실패한다.
6. v1 read compatibility는 0.x 전체와 첫 stable 1.0까지 유지한다. 제거는 별도 accepted migration
   decision과 external-consumer evidence 없이는 허용하지 않는다.

### 근거

- 기존 v1의 conditional field는 strict consumer와 runtime의 의미를 동시에 만족시키지 못한다.
- Domain을 명시하면 document lifecycle과 artifact retirement를 같은 enum 문자열만으로
  오해하지 않고 relation history도 별도로 판정할 수 있다.
- Fail-closed migration은 archived document를 removed artifact로 추측 변환하는 의미 손실을 막는다.

### 제외

- VERSION의 stable release 전환 또는 publication
- Historical v1 transaction과 accepted evidence의 일괄 rewrite
- Inferred relation의 canonical mutation 승격
