---
doc_type: work_order
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: pending}
work_status: in_progress
key:
  id: key.work.dependency-execution-graph.order
  refs:
    - key.doc.work
    - key.topic.dependency
    - key.topic.work-sequence
    - key.topic.change-set
    - key.topic.verification
---

# Dependency Execution Graph 작업서 및 Change Set

<!-- key: id=key.work.dependency-execution-graph.order.goal refs=key.section.goal key.topic.dependency -->
## Goal

Structured dependency와 legacy evidence를 실제 Work/Step registry에 연결하고, source step start와
completion, target condition과 work completion event를 펼친 graph에서 invalid gate와 cycle을
결정적으로 평가해 Reader/Linker readiness에 노출한다.

<!-- key: id=key.work.dependency-execution-graph.order.scope refs=key.section.scope key.topic.work-sequence -->
## Scope

Include:

- Source Work와 실제 Step registry
- Gate ID, source work, dependency target와 applies-to scope 보존
- Missing/invalid Step과 structured/legacy conflict 진단
- Legacy work-level dependency의 non-start-blocking completion candidate
- Expanded event graph와 SCC/cycle diagnostics
- Invalid gate의 evaluation 제외와 optional/blocking 의미
- Readiness CLI의 structured dependency evaluation

Exclude:

- Dependency 결과에 따른 progress 자동 mutation, assignment, cancellation 또는 acceptance
- 일반 build-system package dependency 분석
- Work-node 관계만으로 cycle을 추정하는 단순화
- 현재 Work 밖 문서 상태의 자동 수정

<!-- key: id=key.work.dependency-execution-graph.order.baseline refs=key.topic.impact-review key.topic.verification -->
## Baseline Findings

1. Runtime은 complete+accepted, optional, missing target, cancelled/superseded, self, undeclared와
   duplicate gate의 단순 case를 평가한다.
2. `applies_to.steps: [S99]`는 실제 source Work의 Step 존재 여부와 무관하게 parse될 수 있다.
3. Legacy `depends_on`은 typed relation만 만들고 completion candidate가 없다.
4. 두 Work의 step completion이 서로를 기다리는 cycle을 검출하는 event graph가 없다.
5. Readiness response에는 owners, refs와 optional typed edges만 있고 dependency evaluation이 없다.

<!-- key: id=key.work.dependency-execution-graph.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: 문서 dependency 계약과 실제 session execution evidence를 연결한다.
- Required candidates: dependency parser/evaluator, work/step registry, readiness wire와 tests
- Conditional candidates: Reader/Linker runtime contract와 dependency standard clarification
- Acceptance owner: Main
- Graph handling: `depends_on` typed relation과 `work_gates` execution evidence를 계속 분리한다.

<!-- key: id=key.work.dependency-execution-graph.order.approach refs=key.section.recommended-approach key.topic.verification -->
## Recommended Approach

1. Work ID, Step refs와 status/approval evidence를 immutable registry로 정규화한다.
2. Gate parse와 registry validation을 분리하고 invalid gate는 evaluator에 넣지 않는다.
3. Legacy-only dependency를 `work_completion: true` candidate로 만들되 source start는 막지 않는다.
4. Source step start/completion, target satisfaction와 source work completion event를 생성한다.
5. Event graph에서 SCC를 계산하고 gate ID, source/target, cycle path를 stable diagnostic으로 낸다.
6. Readiness CLI에 evaluation과 completeness를 추가하되 상태 변경 command는 만들지 않는다.

<!-- key: id=key.work.dependency-execution-graph.order.completion refs=key.topic.acceptance key.topic.integration-verification -->
## Completion Criteria

- [ ] Missing source Work/Step과 invalid Step이 `invalid`로 진단된다.
- [ ] Structured/legacy conflict와 duplicate/self/undeclared gate가 구분된다.
- [ ] Legacy-only dependency가 non-start-blocking work-completion candidate로 노출된다.
- [ ] Expanded event graph의 direct/indirect cycle이 deterministic SCC evidence로 검출된다.
- [ ] Optional gate와 invalid gate의 blocking 의미가 구분된다.
- [ ] Readiness CLI가 gate ID, scope, target state, result와 blocking을 반환한다.
- [ ] Evaluation은 progress, assignment나 acceptance를 자동 변경하지 않는다.
- [ ] R003 accepted simple-case regression이 유지된다.

<!-- key: id=key.work.dependency-execution-graph.order.verification refs=key.topic.verification -->
## Verification

- Valid, waiting, optional, missing, invalid-step와 legacy dependency table tests
- Two-work/two-step direct 및 indirect event-cycle fixtures
- Reader→Linker readiness dependency response E2E
- Linker, Reader와 skill contract regression
- Repository graph validation과 `git diff --check`

<!-- key: id=key.work.dependency-execution-graph.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. Source Work/Step authority를 여러 문서에서 충돌하게 해석해야 한다.
2. Gate evaluation이 자동 scheduler나 status mutation으로 확대된다.
3. Legacy normalization이 기존 structured dependency 의미를 덮어쓴다.
4. Readiness public wire compatibility에 별도 user decision이 필요하다.
