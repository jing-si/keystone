---
doc_type: work_order
created_at: "2026-08-10"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-11", accepted_by: main}
work_status: complete
finalization: {state: complete, acceptance_ref: R011/S01/main-acceptance}
key:
  id: key.work.parallel-active-state.order
  refs:
    - key.doc.work
    - key.topic.work-sequence
    - key.topic.work-recovery
    - key.topic.change-set
    - key.topic.impact-review
    - key.topic.skill-contract
    - key.topic.verification
---

# Parallel Active State 작업서 및 Change Set

<!-- key: id=key.work.parallel-active-state.order.goal refs=key.section.goal key.topic.work-recovery -->
## Goal

복수의 Work와 Round가 동시에 `in_progress | blocked`일 때 어느 하나를 대표 작업으로 승격하거나
나머지를 숨기지 않고, active Work·Round·Step과 active Step이 불명확한 Work를 source-derived
global state로 복구한다. Reader, Author, Coordinator, Linker, validator와 release consumer가 같은
versioned 의미를 사용하되 기존 단일 `active_round` corpus는 명시적 compatibility로 읽는다.

<!-- key: id=key.work.parallel-active-state.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- `active_works`, `active_rounds`, 동등한 `active_steps`와 unresolved active-Step representation
- Work Index, Progress frontmatter, Round Index, Root Index와 Context Map의 상태 소유·projection 경계
- 단일 `active_round`의 legacy compatibility와 복수 상태 비표현 진단
- 여러 Work가 `in_progress`인데 전역 목록 일부가 누락되는 경우의 fail-soft recovery
- active Work인데 active Step이 없거나 후보만 있는 경우의 명시적 unresolved 상태
- Progress frontmatter, Work/Index와 live recovery text 사이 충돌 진단
- Reader·Author·Coordinator·Linker·validator·release의 canonical runtime parity
- R008 Work active/no formal Step과 R010 active Step 병행 사례를 포함한 fixture

Exclude:

- 특정 소비 프로젝트의 R008·R010 상태값을 자동 수정하거나 한쪽을 대표 작업으로 선택하는 동작
- 복수 active 상태만으로 병렬 writer, 실행 권한 또는 우선순위를 부여하는 정책
- 한 acceptance event가 서로 다른 Round의 Step을 함께 수락하도록 넓히는 변경
- 외부 소비 프로젝트 문서의 직접 수정과 accepted history 소급 rewrite

<!-- key: id=key.work.parallel-active-state.order.direction refs=key.topic.work-recovery key.topic.skill-contract -->
## Working Direction

1. Work aggregate 상태는 Work source, Step 상태는 Progress source가 소유하고 상위 index와 Context
   Map은 파생 projection으로 다룬다.
2. Active Work가 존재하지만 active Progress/Step을 확정할 수 없으면 Work를 숨기지 않고
   `active_step_resolution: unresolved`와 evidence/candidate를 반환한다.
3. `active_rounds`는 active Work/Step evidence에서 파생하고 Round source와 다르면 source conflict를
   반환한다.
4. Legacy `active_round`는 0개 또는 1개 상태의 compatibility projection으로만 사용한다. 복수
   상태에서 임의 Round나 `none`을 권위 값으로 만들지 않는다.
5. Active set은 우선순위가 아니다. 세션 focus가 필요하면 별도 비권위 실행 문맥으로 전달한다.
6. 프로젝트별 상태 표현이 현재 계약에 따라 유효한 경우 상태값 자체를 바꾸지 않고 일반 계약의
   가시성·명명·복구 문제만 개선한다.

<!-- key: id=key.work.parallel-active-state.order.lean-core refs=key.boundary.scope-control key.topic.work-recovery key.topic.verification -->
## Lean Core 경계

1. Canonical Work State Runtime이 active 상태 의미를 한 번 계산하고, 각 consumer는 그 결과를
   재사용한다. Consumer별 독립 상태 판정기를 만들지 않는다.
2. 기존 source frontmatter에서 복구 가능한 범위에서는 새 mandatory document, manifest, receipt,
   key, evidence root 또는 외부 service를 추가하지 않는다.
3. Root Index와 Context Map의 수동 포인터 증식은 compatibility 범위로 제한한다. 장기적인 derived
   projection 정규화는 S04가 소유하며 S01이 별도 projection framework를 만들지 않는다.
4. 기존 `active_round` zero/one wire를 유지하면서 복수 상태에서만 필요한 versioned field와
   diagnostic을 추가한다. Historical source를 일괄 migration하지 않는다.
5. 실제 필드를 읽는 consumer와 회귀 test만 변경 후보로 인정한다. 문서나 skill 이름이 관련돼
   보인다는 이유만으로 모든 표면을 일괄 수정하지 않는다.

<!-- key: id=key.work.parallel-active-state.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: 병렬 active Work/Round와 unresolved Step을 손실 없이 복구하는 canonical state model을 만든다.
- Required candidates: canonical Work State Runtime, generated Reader/Coordinator/Author copies,
  repository projection 및 focused compatibility tests
- Conditional candidates: Project Standard, individual skill contract, finalization/closure/release와
  Linker readiness는 실제로 새 필드를 판정하거나 직렬화하는 소비가 확인될 때만 수정한다.
- Excluded: consuming-project status rewrite, execution priority, multi-writer policy, cross-Round
  acceptance, HMAC/private key, external evidence root와 새 mandatory closure artifact
- Acceptance owner: Main
- Graph handling: 기존 single-Round claim의 부분 대체와 새 output/test relation은 Linker가
  분류하고 source owner가 필요한 mutation만 적용한다.

<!-- key: id=key.work.parallel-active-state.order.completion refs=key.topic.acceptance key.topic.verification -->
## Completion Criteria

<!-- key: id=key.acceptance.parallel-active-state.parallel-round-recovery -->
- `R011-S01-CC-01` 복수 활성 Round/Work fixture에서 모든 active Work와 Round가 손실 없이 복구된다.
<!-- key: id=key.acceptance.parallel-active-state.no-implicit-priority -->
- `R011-S01-CC-02` 우선순위 근거가 없으면 Reader와 consumer가 대표 Work/Round를 임의 선택하지 않는다.
<!-- key: id=key.acceptance.parallel-active-state.unresolved-step-visibility -->
- `R011-S01-CC-03` active Step이 불명확한 Work도 active Work로 반환되고 unresolved reason과 status
  sources가 보존된다.
<!-- key: id=key.acceptance.parallel-active-state.legacy-compatibility -->
- `R011-S01-CC-04` 기존 단일 `active_round` 문서는 읽을 수 있고, 복수 active evidence와 충돌하면
  조용히 축소하지 않고 명시적 진단을 반환한다.
<!-- key: id=key.acceptance.parallel-active-state.consumer-parity -->
- `R011-S01-CC-05` Reader, Author, Coordinator, Linker, validator와 release consumer가 같은 generation에서
  동일한 active state와 conflict diagnostics를 반환한다.
<!-- key: id=key.acceptance.parallel-active-state.project-state-preservation -->
- `R011-S01-CC-06` R008·R010 사례에서 상태값 수정 필요와 표현/계약 개선 필요를 분리하고, 기존
  project state를 이유 없이 다시 쓰지 않는다.

<!-- key: id=key.work.parallel-active-state.order.verification refs=key.topic.verification -->
## Verification

- R008/R010 two-active-Work and two-active-Round fixtures
- Active Work with zero resolved active Steps and multiple informational candidates
- Progress frontmatter/body/Work Index/Root projection conflict fixtures
- Legacy zero/one active Round compatibility와 multi-active non-representable diagnostics
- Canonical/generated runtime parity와 실제 필드 소비가 확인된 package tests
- Finalization/closure consumer가 active visibility를 acceptance 또는 writer authority로 오인하지
  않는 focused test; 소비하지 않는 표면에는 새 integration layer를 추가하지 않는다

<!-- key: id=key.work.parallel-active-state.order.expected-output refs=key.topic.verification key.topic.work-recovery -->
## Expected Output

- 최소 source-authority 결정과 versioned state wire
- Canonical Work State Runtime 및 required generated consumer copies
- Legacy/multi-active/unresolved/conflict fixture와 실제 consumer에 한정한 parity evidence

<!-- key: id=key.work.parallel-active-state.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. Work, Step, Round와 projection source authority를 구분할 수 없다.
2. 복수 상태 지원이 accepted history rewrite 또는 implicit priority를 요구한다.
3. Multi-Round acceptance event나 병렬 writer 정책까지 범위를 넓혀야 completion이 가능하다.
4. 소비 프로젝트의 실제 상태 수정 없이는 fixture를 정의할 수 없다고 판단된다.
5. Consumer parity를 깨지 않고 legacy compatibility를 제공할 versioned boundary가 없다.
6. 복수 상태 복구가 새 secret, 외부 evidence service, consumer별 판정기 또는 수동 상태 포인터
   증식을 core prerequisite로 요구한다.
