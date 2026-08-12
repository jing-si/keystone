---
doc_type: work_order
created_at: "2026-08-10"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-11", accepted_by: main}
work_status: complete
key:
  id: key.work.hierarchical-rounds.order
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.work-recovery
    - key.topic.change-set
    - key.topic.impact-review
    - key.topic.skill-contract
    - key.topic.verification
    - key.claim.r011.round-hierarchy-two-level-limit
    - key.claim.r011.depth-overflow-restructure
    - key.claim.r011.parent-global-round-authority
    - key.claim.r011.child-local-execution-authority
    - key.claim.r011.parent-child-aggregate-gate
---

# Hierarchical Rounds 작업서 및 Change Set

<!-- key: id=key.work.hierarchical-rounds.order.goal refs=key.section.goal key.topic.work-round -->
## Goal

큰 작업을 하나의 parent Round로 묶고 `R010-a`, `R010-b` 같은 child Round가 세부 Goal과 실행
상태를 소유할 수 있는 계층형 Round 모델을 정의한다. Parent Round는 상위 기준서처럼 전체 목적,
공통 범위·경계와 child navigation을 포괄하고, child Round는 상세 Work Order, Progress,
completion criteria와 verification을 관리한다.

<!-- key: id=key.work.hierarchical-rounds.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- Parent `R010`과 child `R010-a`, `R010-b`를 구분하는 canonical Round ref 문법
- Parent와 그 직접 child의 총 2단계로 제한하는 supported-depth 규칙
- Step suffix family와 일관된 하위 식별자 규칙 및 path/index mapping
- Parent umbrella Goal/Scope/boundary와 child detailed execution authority 분리
- Root Works Index → parent Round Index → child Round Index → Work node navigation
- Child Step ref, 예: `R010-a/S01`, dependency와 `work_gates` target 의미
- 작업 도중 새 child Round를 추가해도 기존 Step/Work/Round ID를 재번호화하지 않는 규칙
- Parent/child aggregate status, active recovery, acceptance와 finalization 경계
- 기존 flat `R001`~`R010` corpus와 installed skill/parser/validator compatibility

Exclude:

- 기존 accepted Round를 계층형 path로 일괄 이동하거나 이름을 바꾸는 migration
- Parent와 child가 동일 상세 상태를 중복 소유하는 모델
- Child 추가만으로 구현 권한, acceptance 또는 dependency satisfaction을 자동 생성하는 동작
- Child 아래 grandchild Round를 만드는 3단계 이상 계층, cross-project Round federation과
  unrelated document hierarchy 변경

<!-- key: id=key.work.hierarchical-rounds.order.direction refs=key.topic.work-round key.topic.document-system -->
## Working Direction

1. Parent Round ref는 기존 `R[0-9]{3,}`를 유지하고 child Round ref는 직접 child를 나타내는
   단일 lower-case ASCII suffix의 `R[0-9]{3,}-[a-z]`를 사용한다. 예시는 `R010-a`,
   `R010-b`며 27개 이상 child가 필요하면 추가 문법을 만들지 않고 작업서를 개편한다.
2. Parent Round Index는 umbrella Goal, 공통 Scope/Boundary, child 순서·링크와 aggregate recovery를
   소유하고 세부 Work 내용을 반복하지 않는다.
3. Child Round Index는 자체 실행 순서, Work nodes, active Steps와 Progress navigation을 소유한다.
4. Root Works Index는 parent Round를 top-level entry로 노출하고 Reader가 parent index에서 관련
   child index를 따라간다.
5. 새 child Round는 planned/pending으로 추가하며 기존 child와 Step ID를 재번호화하지 않는다.
6. Parent folder는 기존 `r{number}-{slug}/`를 유지하고 child folder는 그 안의
   `r{same-number}-{suffix}/`로 고정한다. 예를 들어 `R010-a`는
   `works/r010-parent-slug/r010-a/00_key-index.md`로 mapping하고, child Work node는 그 아래에 둔다.
7. Parent와 child 번호는 같아야 하며 sibling suffix는 중복하거나 재사용하지 않는다.
   `R010-a-a`, sibling root folder `works/r010-a-slug/` 또는 child의 child folder는 거부한다.
8. Supported depth는 `DEC-WORKS-030`에 따라 parent→child 총 2단계로 고정하고, S02 구현 전에
   parent/child status derivation을 versioned Work State schema와 fixture로 확정한다.
9. 3단계 이상이 필요해지면 신규 Round를 만들지 않고 작업 플랜이 과도하게
   복잡해졌다고 보고한 뒤 Goal 축소, sibling child 분리 또는 별도 parent Round를 통한
   작업서 개편을 요청한다.
10. Parent Round Index의 ordered `child_rounds`가 child membership와 navigation authority다.
    Child index는 local `round_status`, Work·Step·Progress를 소유하고, child를 선언한 parent는
    상세 Work를 직접 중복 소유하지 않는다.
11. Work State schema v3은 기존 전역 parent fields를 유지하고 `round_hierarchy`,
    `active_child_rounds`와 child active Work의 `parent_round_ref`를 추가한다. Child Step ref는
    `active_steps`에 보존하되 `active_rounds`/`active_round`은 parent ref를 보존한다.
12. Parent source `round_status`는 child 집계가 자동 변경하지 않는다. 단, parent를 accepted로
    수락하려면 선언한 모든 child가 accepted이고 unresolved child와 active·blocked·planned
    child가 없어야 한다. Child acceptance는 parent gate만 충족하고 전역 ordering을 전이하지 않는다.

<!-- key: id=key.work.hierarchical-rounds.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: 큰 Work Round를 안정적 parent umbrella와 추가 가능한 detailed child Rounds로 나눈다.
- Required candidates: Project Standard/round creation rules, Context Map/Works Index navigation,
  canonical Work State와 Reader·Author·Coordinator generated copies, current skill contracts와 focused tests
- Conditional candidates: Linker dependency/gate parser는 child Step ref fixture가 현재 문법을 거부하는 경우에만
  수정한다. Historical finalization/closure adapter는 기존 flat corpus read compatibility만 검증한다.
- Excluded: existing round relocation, history rewrite, external consuming-project migration, 새 acceptance-event
  producer·finalization manifest·Coordinator v2/v3 closure wire 확장
- Acceptance owner: Main
- Graph handling: parent/child navigation과 semantic relation, output/test impact를 Linker가 분류하고
  필요한 source owner mutation만 적용한다.

<!-- key: id=key.work.hierarchical-rounds.order.completion refs=key.topic.acceptance key.topic.verification -->
## Completion Criteria

<!-- key: id=key.acceptance.hierarchical-rounds.reference-grammar -->
- `R011-S02-CC-01` `R[0-9]{3,}-[a-z]` child Round ref, child Step ref, parent→child 2단계
  상한과 nested `r{number}-{suffix}/` folder/index mapping이 모호하지 않은 versioned
  grammar로 정의된다.
<!-- key: id=key.acceptance.hierarchical-rounds.parent-child-authority -->
- `R011-S02-CC-02` Parent umbrella와 child detail의 source authority가 분리되고 같은 status나
  completion criterion을 충돌하게 중복 소유하지 않는다. Parent만 전역 Round 상태·수락
  식별자고 child는 local execution authority다.
<!-- key: id=key.acceptance.hierarchical-rounds.dynamic-child-addition -->
- `R011-S02-CC-03` 진행 중 새 child Round를 planned/pending으로 추가해도 기존 ID, acceptance와
  Progress history가 유지된다.
<!-- key: id=key.acceptance.hierarchical-rounds.recovery -->
- `R011-S02-CC-04` Reader와 canonical Work State Runtime이 parent와 모든 active/planned child를
  탐색하고 unresolved child 상태를 숨기지 않으며, sibling child가 복수여도 전역
  `active_rounds`는 parent ref를 유지한다.
<!-- key: id=key.acceptance.hierarchical-rounds.dependency-gate -->
- `R011-S02-CC-05` Parent/child/sibling dependency와 `work_gates`가 의미 관계와 실행 차단을 구분해
  canonical target으로 평가된다.
<!-- key: id=key.acceptance.hierarchical-rounds.legacy-compatibility -->
- `R011-S02-CC-06` 기존 flat Round corpus와 accepted history는 이동·재번호화 없이 읽고 검증할 수 있다.

<!-- key: id=key.work.hierarchical-rounds.order.verification refs=key.topic.verification -->
## Verification

- Flat `R010` and `r010-parent/r010-a/` nested child `R010-a`/`R010-b` parser fixtures
- `R010-a-a` 형식 3단계 시도 거부와 `work_order_restructure` report fixture
- Parent umbrella/child detail duplicate-authority and stale-link diagnostics
- Parent-only global `active_rounds`/`latest_accepted_round`, child-local status와 multi-sibling active fixture
- Parent accepted + non-accepted/unresolved child rejection and child acceptance no-global-transition fixture
- Dynamic child addition without existing ID renumbering
- Child `R010-a/S01` Progress, dependency, gate, active-state와 current source-sync completion fixtures
- Reader navigation, Author creation/progress sync, Linker readiness, Work State generated-copy parity와
  Coordinator Context Pack
- Current source/Progress/Work State 완료 흐름이 새 finalization manifest, acceptance event,
  external evidence 또는 historical closure wire를 요구하지 않는 것을 검증
- Existing R001-R010 corpus full compatibility and no-migration verification

<!-- key: id=key.work.hierarchical-rounds.order.expected-output refs=key.topic.verification key.topic.work-recovery -->
## Expected Output

- Hierarchical Round standard/decision과 canonical reference/path grammar
- 2단계 상한, depth overflow stop/report와 Work Order 개편 routing 계약
- Parent/child source-authority and aggregation contract
- Updated canonical Work State, generated copies와 current Reader·Author·Coordinator contracts
- Flat/hierarchical/dynamic-addition/dependency/current-completion cross-skill fixture suite

<!-- key: id=key.work.hierarchical-rounds.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. Parent와 child의 상태·approval·acceptance authority가 중복돼 충돌을 피할 수 없다.
2. 기존 accepted Round path/ID migration 없이는 compatibility를 만들 수 없다.
3. Child Round와 Work node 또는 Step의 의미 경계가 구분되지 않는다.
4. Dynamic child addition이 기존 acceptance나 dependency graph를 소급 변경해야 한다.
5. Parent-only global authority를 유지하려면 기존 flat Round pointer 또는 accepted history를
   소급 변경해야 한다.
6. Goal을 완수하기 위해 3단계 이상 Round 계층이 필요하다. 이 경우 계층을 늘리지 않고
   `work_order_restructure`로 보고해 작업서 개편을 먼저 요청한다.
