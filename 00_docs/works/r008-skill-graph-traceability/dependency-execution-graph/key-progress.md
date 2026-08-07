---
doc_type: progress
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-07", accepted_by: main}
work_status: complete
step_ref: R008/S03
work_ref: R008/dependency-execution-graph
finalization: {state: complete, acceptance_ref: R008/S03/main-acceptance}
key:
  id: key.work.dependency-execution-graph.progress
  refs:
    - key.topic.progress-update
    - key.topic.dependency
    - key.topic.work-sequence
    - key.topic.verification
---

# Dependency Execution Graph 진행 기록

## 현재 상태

- Step: R008/S03
- Work status: complete
- Approval state: accepted
- Active: false
- Finalization state: complete
- Acceptance ref: R008/S03/main-acceptance
- Resume point: R008/S04 binary companion과 repository completeness RED fixture

Active steps: []

## 준비 증거

- `parse_work_gates()`는 `applies_to.steps`가 non-empty string인지 확인하지만 source work에 해당
  Step이 실제 존재하는지 확인하지 않는다.
- Legacy `depends_on`만 있고 explicit gate가 없으면 relation은 생성되지만 work-completion gate
  candidate는 생성되지 않는다.
- Runtime에는 expanded event graph나 SCC/cycle 판정이 없다.
- `ParseResult.work_gates`는 owner/ref `IndexResult`와 readiness CLI response로 전달되지 않는다.

## 다음 작업

1. R008/S04에서 logical source identity와 physical companion patch target을 분리한다.
2. Binary companion transaction과 full/subset completeness envelope를 구현한다.

## 구현 및 검증 결과

- `DependencySource`와 immutable Work/Step registry가 work order state, approval, Step ref,
  structured/legacy dependency와 gate를 같은 discovery generation에서 복구한다.
- Stable gate ID, source, target, Step/work-completion scope, target state, result, blocking, optional,
  origin과 cycle events를 `DependencyEvaluation`으로 보존한다.
- Missing source Work/Step, duplicate/self/undeclared, condition과 structured/legacy conflict는
  서로 다른 diagnostic으로 남고 required invalid gate는 fail-closed다.
- Legacy-only dependency는 Step start를 막지 않는 work-completion candidate로 정규화한다.
- Required gate만 expanded event graph와 deterministic SCC cycle 판정에 참여하며 optional gate는
  상태를 보고하되 blocking 또는 cycle edge가 되지 않는다.
- Readiness CLI는 schema v2로 dependency evaluation을 반환하고 cache schema v5가 전체 payload
  digest에 이를 포함한다.
- Coordinator closure validator는 dependency status와 gate evidence를 요구하고 required
  active-Step blocking gate가 남으면 `accept_candidate`를 거부한다.
- Linker 198, Coordinator 27, Author 75, Reader 2, skill contract 18 tests passed.
- Fresh docs readiness: owners 924, refs 2,889, errors 0, warnings 129.
- Fresh repository readiness: owners 930, refs 2,889, typed edges 20, errors 0, warnings 124.
- Repository graph validator diagnostics 0, compileall과 `git diff --check` passed.
- Graph sync: `not_applicable`; source-owned graph ID/relation/provenance mutation은 없다.
