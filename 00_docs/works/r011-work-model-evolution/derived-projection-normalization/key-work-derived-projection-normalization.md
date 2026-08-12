---
doc_type: work_order
created_at: "2026-08-10"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-12", accepted_by: main}
work_status: complete
finalization: {state: complete, acceptance_ref: R011/S04/main-acceptance}
key:
  id: key.work.derived-projection-normalization.order
  refs:
    - key.doc.work
    - key.topic.document-system
    - key.topic.work-recovery
    - key.topic.artifact-graph
    - key.topic.change-set
    - key.topic.impact-review
    - key.topic.skill-contract
    - key.topic.verification
---

# Derived Projections and Document Normalization 작업서 및 Change Set

<!-- key: id=key.work.derived-projection-normalization.order.goal refs=key.section.goal key.topic.document-system -->
## Goal

Keystone 문서에 같은 현재 의미를 여러 번 수동 기록해 발생하는 drift를 stable `key.id`, typed
relation과 source-derived join으로 줄인다. 다시 계산 가능한 live/effective state는 하나의 source
owner만 갖게 하고 Context Map, Index, recovery와 status table은 검증 가능한 derived projection으로
만든다. 반대로 acceptance event, finalization manifest, historical Progress와 decision rationale처럼
당시 사실을 증명하는 기록은 의도적 역정규화 snapshot으로 보존한다.

<!-- key: id=key.work.derived-projection-normalization.order.classification refs=key.topic.document-system key.topic.impact-review -->
## 분류 원칙

1. 현재 source에서 결정적으로 다시 계산할 수 있는 live/effective 의미는 정규화한다.
2. `key.id`는 stable primary identity, typed relation은 semantic foreign key, path와 Markdown link는
   사람용 locator로 취급한다.
3. Context Map과 Index의 표시 상태는 source authority가 아니라 materialized projection이다.
4. 특정 acceptance/finalization/verification 시점의 상태를 재현하는 immutable event와 evidence는
   의도적 역정규화로 보존한다.
5. 의도적 snapshot은 `source_ref`, acceptance/event ref, source/result digest와 generation 또는
   equivalent binding을 가져 현재 상태와 역사적 상태를 구분한다.
6. 사람이 작성한 rationale, note와 history는 생성하지 않는다. 그 안의 live recovery claim만
   generated 영역과 분리한다.
7. Derived cache와 owner/ref index는 폐기 가능하며 source of truth 또는 acceptance evidence가 아니다.

<!-- key: id=key.work.derived-projection-normalization.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- Standard frontmatter, Standards Index와 Context Map approval projection
- Accepted effective baseline과 pending revision의 분리·join
- Work/Step Progress에서 파생하는 Work/Round/Root/Context Map aggregate 상태
- `active_works`, `active_rounds`, `active_steps`, `latest_accepted_round`와 current recovery projection
- `depends_on` relation과 이를 참조하는 `work_gates`의 중복 target/condition 경계
- Acceptance criterion, verification evidence와 Progress criterion-status view
- Decision/claim `supersedes` chain에서 파생하는 effective-decision view
- Work Order와 Artifact Graph relation에서 파생하는 output/test/impact summary
- Canonical source와 generated skill/runtime copy 사이 generation manifest와 parity projection
- Confirmed human consumer가 있을 때만 사용하는 generated Markdown boundary와 freshness policy,
  stale/missing/ambiguous join diagnostics
- Legacy manually maintained projection의 compatibility와 점진적 migration

Exclude:

- Accepted event, finalization manifest, Progress history와 decision rationale의 제거 또는 재작성
- Context Map, generated index, Artifact Graph cache나 rendered table을 새 source authority로 승격
- 기존 corpus의 일괄 rewrite, accepted history migration과 경로 기반 identity 강제
- Reader, Validator 또는 generator가 approval, acceptance나 work status를 자동 전이하는 동작
- repository source 없이 network database나 always-on service를 필수 조건으로 만드는 설계

<!-- key: id=key.work.derived-projection-normalization.order.candidate-matrix refs=key.topic.impact-review key.topic.work-recovery -->
## 정규화·역정규화 source-owner 기준선

| 대상 | 분류 | Authoritative source owner | Projection·보존 및 legacy 규칙 | 구현 상태 |
|---|---|---|---|---|
| Work current status·approval | `normalize` | Aggregate Work Progress `key-progress.md` | Work Index 값은 생략 가능한 호환 projection이며, 값이 있으면 stale 여부만 대조한다 | Slice A 구현 |
| Step current status·approval | `normalize` | compatible combined Progress 또는 `key-progress-{step-slug}.md` | Aggregate와 Step 상태가 갈라질 때만 Step Progress를 만든다 | S03 구현 재사용 |
| Round local status | `manual_authority` | owning parent/child Round Index | Work/Step 집계가 Round를 자동 전이하지 않고 conflict만 진단한다 | S02 구현 재사용 |
| Active Work/Round/Step set | `normalize` | Work·Step Progress와 Round source를 결합한 canonical Work State Runtime | Context Map·Index `global_state`는 생략 가능한 호환 projection이다 | Slice A 구현 |
| Latest accepted Round | `normalize` | canonical acceptance-event chain head와 accepted Round source | Context Map·Index는 source가 아니며 runtime result를 표시할 수만 있다 | 기존 runtime 재사용 |
| Standard policy·현재 approval | `manual_authority` | canonical Standard frontmatter와 accepted source | Standards Index·Context Map approval은 authoritative source가 아니다 | Slice B source binding 확정 |
| Accepted baseline + pending revision effective view | `normalize` | accepted baseline source, pending revision source와 explicit baseline ref | pending 문구나 Index projection으로 accepted baseline을 추정하지 않는다 | Slice B session adapter 구현 |
| Human recovery note·rationale | `manual_authority` | owning Standard·Work Order·Progress·Decision source | generator가 사람이 쓴 설명과 판단을 축약하거나 덮어쓰지 않는다 | 보존 경계 확정 |
| Live current-recovery view | `normalize` | canonical Work State result | 기본은 비영속 runtime output이며, confirmed human consumer가 있을 때만 bounded/fresh generated block을 둔다 | Slice A runtime, renderer 제외 |
| Dependency·gate definition | `manual_authority` | `depends_on` relation과 이를 참조하는 `work_gates` | target을 별도 의미로 중복 소유하지 않고 gate는 적용 범위·condition만 소유한다 | Slice B 구현 |
| Dependency evaluation | `normalize` | dependency/gate sources와 effective Work state resolver를 읽는 canonical evaluator | Progress/Index에는 결과를 수동 권위로 복제하지 않는다 | Slice B owner join 구현 |
| Acceptance criterion definition | `manual_authority` | Work Order의 stable criterion item | criterion 문구는 generated view가 아니다 | 기존 source 유지 |
| Criterion verification status | `normalize` | criterion과 bound `verifies` evidence join | Opt-in session view이며 Progress Criterion Status나 approval을 자동 전이하지 않는다 | Slice C 구현 |
| Decision rationale | `manual_authority` | accepted Decision/claim source | 기계적으로 축약하거나 current projection으로 대체하지 않는다 | 기존 source 유지 |
| Effective Decision 목록 | `normalize` | accepted Decision/claim과 `supersedes` chain | Pending은 별도 overlay, Context/Work summary는 effective chain만 파생한다 | Slice C 구현 |
| Output/test/impact summary | `normalize` | Work Order와 typed Artifact Graph relations | Direct output/test는 session view, transitive impact는 기존 on-demand traversal로 분리한다 | Slice C 구현 |
| Generated skill/runtime parity | `normalize` | canonical source와 generation manifest | package copy 상태는 digest/parity projection으로만 표시한다 | 기존 generator 재사용 |
| Acceptance event | `intentional_denormalization` | immutable event source | 당시 accepted subject·ordering·digest를 보존하며 current pointer로 쓰지 않는다 | 보존 |
| Finalization evidence | `intentional_denormalization` | historical finalization record | 당시 binding을 보존하되 current completion prerequisite로 재생성하지 않는다 | S03 계약 재사용 |
| Historical Progress/log | `intentional_denormalization` | owning historical Progress | live state field와 구분하며 과거 사실을 소급 rewrite하지 않는다 | 보존 |
| Disposable cache·owner/ref index | `excluded` | canonical source 없음 | repository 밖 선택 cache이며 없으면 raw source로 fallback한다 | 기존 Linker 정책 재사용 |

Slice A는 문서 수정 비용이 가장 큰 Work/Step/active/latest projection을 구현했다. Slice B·C는
같은 owner/ref와 GraphSnapshot resolver를 재사용했으며 범용 projection framework나 새 persistent
artifact를 만들지 않았다. Optional Markdown renderer는 확인된 human consumer가 없고 기본
runtime output과 중복되므로 S04에서 제외한다.

<!-- key: id=key.work.derived-projection-normalization.order.architecture refs=key.topic.artifact-graph key.topic.document-system -->
## Working Architecture

```text
Canonical source
  ├─ stable key.id
  ├─ typed relations
  └─ authoritative state/evidence
             |
             v deterministic source join
Derived projections
  ├─ Context Map and indexes
  ├─ current recovery and aggregate status
  ├─ criterion/decision/output summaries
  └─ generated/install parity views

Immutable events and audit snapshots
  └─ source/event refs + digest/generation binding
```

Reader와 validator는 같은 resolver/policy를 사용한다. Artifact Graph와 external owner/ref index는
join을 빠르게 할 수 있지만 cache failure 시 raw source discovery로 fail-soft해야 한다. Generated
Markdown은 명시적 bounded marker, source generation/freshness binding과 stale diagnostic을 가지며
사람이 작성하는 영역을 덮어쓰지 않는다.

<!-- key: id=key.work.derived-projection-normalization.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: current semantic duplication을 source-derived projection으로 바꾸고 audit duplication은
  immutable evidence로 명시해 문서 drift와 과도한 정규화를 함께 방지한다.
- Required candidates: Project/Artifact Graph standards, Reader/Author/Coordinator/Linker contracts,
  Work State/owner-ref resolver, projection generator, validators, generated consumers와 tests
- Conditional candidates: dependency/gate wire, acceptance evidence wire와 Standard revision layout은
  해당 owner 모델이 현재 schema로 표현되지 않을 때만 versioned update한다.
- Excluded: external consuming-project source edits, accepted history rewrite, automatic status/approval
  mutation, mandatory live database
- Acceptance owner: Main
- Graph handling: stable owner/ref/relation과 generated output/test relation 변경은 Linker가 source별
  candidate를 분류하고 각 surface owner가 필요한 mutation만 적용한다.

<!-- key: id=key.work.derived-projection-normalization.order.completion refs=key.topic.acceptance key.topic.verification -->
## Completion Criteria

<!-- key: id=key.acceptance.derived-projection-normalization.classification -->
- `R011-S04-CC-01` 모든 대상이 `normalize | intentional_denormalization | manual_authority |
  excluded` 중 하나와 source owner, 이유를 가진다.
<!-- key: id=key.acceptance.derived-projection-normalization.source-authority requires_verification_of=key.standard.project.derived-work-state-projection -->
- `R011-S04-CC-02` Live/effective field마다 authoritative source가 하나이며 Context Map, Index,
  rendered table과 cache는 권위를 중복 소유하지 않는다.
<!-- key: id=key.acceptance.derived-projection-normalization.join-and-freshness -->
- `R011-S04-CC-03` Stable ID/ref join, generated boundary와 freshness binding이 deterministic하고
  duplicate owner, unresolved ref, stale projection과 source conflict를 명시적으로 진단한다.
<!-- key: id=key.acceptance.derived-projection-normalization.intentional-snapshot -->
- `R011-S04-CC-04` Acceptance/finalization/history snapshot은 current projection과 구분되고 당시
  source/event ref와 digest/generation을 보존한다.
<!-- key: id=key.acceptance.derived-projection-normalization.consumer-parity -->
- `R011-S04-CC-05` Work State를 소비하는 Reader, Author, Coordinator와 release consumer는 같은
  projection을 사용하고, opt-in semantic view를 소비하는 Reader/Linker는 validator와 같은
  GraphSnapshot resolver와 source generation을 사용한다.
<!-- key: id=key.acceptance.derived-projection-normalization.legacy-compatibility -->
- `R011-S04-CC-06` 기존 수동 Context Map/Index/recovery corpus를 읽되 충돌을 조용히 덮지 않고
  점진적 migration 또는 explicit legacy diagnostic을 제공한다.
<!-- key: id=key.acceptance.derived-projection-normalization.cross-work-boundary -->
- `R011-S04-CC-07` S04는 공통 join/projection/snapshot 계약을 소유하고 S01 상태 의미, S02 Round
  hierarchy와 S03 project-vs-contract 판정의 source authority를 대신 결정하지 않는다.

<!-- key: id=key.work.derived-projection-normalization.order.verification refs=key.topic.verification -->
## Verification

- Standard accepted baseline + pending revision + Context Map projection fixtures
- Work/Step/active/latest source mutation 뒤 stale generated projection 진단과 regeneration
- Duplicate owner, unresolved ref, ambiguous typed relation과 changed-source freshness fixtures
- Dependency ref/gate scope, criterion/evidence와 decision supersession join fixtures
- Finalization/acceptance snapshot이 이후 current state 변경 뒤에도 당시 generation을 재현하는 테스트
- Generated block 밖의 human narrative와 historical log가 보존되는 owner-apply 테스트
- Cache unavailable/stale/corrupt 시 raw source fallback과 cross-consumer parity
- Legacy manual projection read compatibility와 no automatic approval/status mutation

<!-- key: id=key.work.derived-projection-normalization.order.expected-output refs=key.topic.verification key.topic.work-recovery -->
## Expected Output

- Source-authority and normalization/intentional-denormalization decision matrix
- Stable owner/ref join과 derived-projection versioned contract
- Generated Markdown boundary, freshness binding과 stale/conflict diagnostic policy
- Standard/status/recovery/dependency/criterion/decision/output projection adapters where accepted
- Immutable snapshot binding and legacy compatibility fixture suite

<!-- key: id=key.work.derived-projection-normalization.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. Live/effective state와 immutable historical snapshot을 구분할 source authority가 없다.
2. Generated projection 또는 cache가 canonical source보다 높은 권위를 가져야 한다.
3. 정규화를 위해 accepted history나 audit evidence를 제거·재작성해야 한다.
4. Join 결과가 source generation에 deterministic하게 결속되지 않거나 consumer마다 달라진다.
5. S01-S03의 상태·Round·triage 의미를 S04가 임의로 다시 결정해야 한다.
6. Legacy 호환을 유지하면서 stale projection을 명시적으로 진단할 수 없다.
