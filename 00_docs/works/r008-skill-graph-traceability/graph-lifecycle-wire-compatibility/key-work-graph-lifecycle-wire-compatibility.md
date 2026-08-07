---
doc_type: work_order
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-07", accepted_by: main}
work_status: complete
key:
  id: key.work.graph-lifecycle-wire-compatibility.order
  refs:
    - key.doc.work
    - key.topic.artifact-graph
    - key.topic.impact-review
    - key.topic.change-set
    - key.topic.verification
---

# Graph Lifecycle and Wire Compatibility 작업서 및 Change Set

<!-- key: id=key.work.graph-lifecycle-wire-compatibility.order.goal refs=key.section.goal key.topic.artifact-graph -->
## Goal

Impact traversal과 relation validation이 evidence/lifecycle을 존중하도록 만들고, 기준서와 runtime이
같은 graph wire version과 lifecycle vocabulary를 사용하도록 명시적 compatibility policy와
migration evidence를 확립한다.

<!-- key: id=key.work.graph-lifecycle-wire-compatibility.order.scope refs=key.section.scope key.topic.impact-review -->
## Scope

Include:

- Declared/observed/inferred evidence의 maximum impact grade
- Active/deprecated/archived/removed relation과 node 처리
- Retired source와 target 양방향 active relation validation
- Document lifecycle과 artifact lifecycle의 wire 의미 분리
- Graph snapshot/transaction v1 compatibility와 v2 canonical candidate
- v1→v2 migration, round-trip와 unknown-field consumer tests

Exclude:

- Release publication, marketplace 또는 external consumer SLA
- Historical relation source를 삭제하는 migration
- Evidence가 없는 inferred relation을 declared로 승격
- Decision 없이 schema version을 유지하거나 올리는 변경

<!-- key: id=key.work.graph-lifecycle-wire-compatibility.order.baseline refs=key.topic.impact-review key.topic.verification -->
## Baseline Findings

1. 기준서의 canonical node/relation lifecycle은 세 값이지만 runtime `Lifecycle`은 draft, active,
   superseded, archived, deprecated와 removed를 모두 가진다.
2. Runtime v1 wire는 기준서의 v1 설명보다 많은 field를 조건부로 출력한다.
3. Impact traversal은 declared active와 inferred archived relation을 같은 grade로 순회할 수 있다.
4. Validator는 retired target exception은 구현했지만 retired source의 active semantic relation은
   통과시킬 수 있다.
5. Exact-field v1 consumer가 conditional metadata field를 거부할 compatibility risk가 있다.

<!-- key: id=key.work.graph-lifecycle-wire-compatibility.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: historical/inferred evidence가 required impact나 active relation으로 오인되지 않게 하고
  wire contract를 versioned meaning과 일치시킨다.
- Required candidates: impact traversal, snapshot validation, model/wire/parser와 compatibility tests
- Conditional candidates: Artifact Graph 기준서, runtime references, VERSION와 decision record
- Acceptance owner: Main
- Decision gate: v1의 permissive extension 유지 또는 canonical v2 도입, lifecycle type 분리와
  compatibility 기간을 확정한다.

<!-- key: id=key.work.graph-lifecycle-wire-compatibility.order.approach refs=key.section.recommended-approach key.topic.verification -->
## Recommended Approach

1. Evidence/lifecycle 조합별 admitted/excluded와 maximum grade table을 source policy로 만든다.
2. Observed evidence는 attestation 여부에 따라 grade cap을 적용하고 inferred는 weak 이하로 제한한다.
3. Deprecated는 informational 이하, archived/removed는 historical/excluded로 분리한다.
4. Active relation의 source와 target lifecycle을 모두 검사하고 canonical supersedes 예외만 유지한다.
5. v1 fixture와 exact-field consumer risk를 검증한 뒤 wire decision을 기록한다.
6. v2가 선택되면 v1 parser compatibility, deterministic migration와 round-trip을 구현한다.

<!-- key: id=key.work.graph-lifecycle-wire-compatibility.order.completion refs=key.topic.acceptance key.topic.integration-verification -->
## Completion Criteria

- [x] Declared/observed/inferred evidence가 승인된 maximum impact grade를 따른다.
- [x] Deprecated/archived/removed relation이 active required candidate로 오인되지 않는다.
- [x] Retired source에서 시작하는 active semantic relation이 진단된다.
- [x] Canonical supersedes exception은 source/target/evidence 조건을 계속 만족한다.
- [x] 기준서와 runtime의 node/relation lifecycle vocabulary가 version별로 일치한다.
- [x] Graph wire decision과 compatibility 기간이 Decision에 기록된다.
- [x] v1 fixture와 선택된 canonical wire의 migration/round-trip tests가 통과한다.

<!-- key: id=key.work.graph-lifecycle-wire-compatibility.order.verification refs=key.topic.verification -->
## Verification

- Evidence/lifecycle impact grade table tests
- Retired source/target and supersedes exception validation matrix
- v1 strict/permissive consumer fixtures
- Selected v1/v2 parser, serializer, transaction round-trip tests
- Linker full suite, repository graph validation과 `git diff --check`

<!-- key: id=key.work.graph-lifecycle-wire-compatibility.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. Wire version, lifecycle type 또는 compatibility 기간에 사용자 결정이 남는다.
2. 기존 verified transaction history를 해석할 migration path가 없다.
3. Impact grade 변경이 accepted policy보다 넓은 automatic edit/acceptance 의미를 만든다.
4. VERSION 또는 release 정책 변경이 publication scope로 확대된다.
