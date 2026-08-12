---
doc_type: work_order
created_at: "2026-08-10"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-11", accepted_by: main}
work_status: complete
finalization: {state: complete, acceptance_ref: R011/S03/main-acceptance}
key:
  id: key.work.project-signal-triage.order
  refs:
    - key.doc.work
    - key.topic.work-sequence
    - key.topic.work-recovery
    - key.topic.change-set
    - key.topic.impact-review
    - key.topic.skill-contract
    - key.topic.finalization
    - key.topic.verification
---

# Project Signal and Contract Triage 작업서 및 Change Set

<!-- key: id=key.work.project-signal-triage.order.goal refs=key.section.goal key.topic.impact-review -->
## Goal

Keystone 사용 중 발견된 상태·문서·복구 불일치를 곧바로 스킬 결함으로 일반화하지 않고 실제
source authority와 반복 가능성을 조사해 `project_document_repair | skill_contract_change | both |
no_change`로 분류한다. 프로젝트 문서 수정과 Keystone 스킬 계약 변경의 owner, evidence,
verification과 재개 지점을 분리한다.

<!-- key: id=key.work.project-signal-triage.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- Context Map과 Standards Index/frontmatter approval drift
- 과거 blocker가 해소됐을 수 있는 `finalization: in_progress` Work의 resumable 후보 탐지
- Aggregate Work Progress와 accepted Step Progress의 상태·파일 ownership 분리
- `depends_on`과 실제 착수/완료 `work_gates` 누락 분류
- live recovery text와 historical explanation 정리 경계
- `active_round`, `active_works`, active-Step Round naming/visibility 영향
- 복수 active Work에서 세션 focus를 정하기 전 Reader의 상세 Work/Progress 탐색 경계
- accepted baseline과 pending revision을 구분하는 Reader readiness 후보
- Project-only repair, recurring contract gap, both와 no-change를 결정하는 증거 기준

Exclude:

- 제공된 외부 소비 프로젝트 경로를 이 저장소에서 직접 수정하는 작업
- validator와 source evidence 없이 Work/finalization을 `complete`로 전이하는 작업
- pending standard를 임의 accepted로 바꾸거나 본문을 frontmatter보다 우선하는 동작
- 단일 프로젝트 사례만으로 모든 Keystone 소비 프로젝트에 새 규칙을 강제하는 동작

<!-- key: id=key.work.project-signal-triage.order.evidence-seeds refs=key.topic.impact-review key.topic.work-recovery -->
## 제공된 소비 프로젝트 evidence seeds

아래 locator는 사용자가 제공한 consuming-project 단서이며 이 저장소의 동일 상대 경로와 혼동하지
않는다. R011/S03 실행 시 해당 프로젝트 source에서 다시 검증하고 line number는 stable identity가
아니라 최초 탐색 위치로만 사용한다.

| 사례 | 제공 locator | 확인할 evidence |
|---|---|---|
| Context Map approval drift | `00_docs/key-context-map.md:124`, `00_docs/standards/00_key-index.md:84` | Backoffice·Workspace standard/index의 실제 approval state |
| API Error finalization resume | `00_docs/works/r010-growth-entry-and-magazine/api-error-boundary-and-oauth-recovery/key-progress.md:285` | 과거 conflict marker, 현재 validator와 finalization blocker 상태 |
| R008 Work/Step Progress 혼합 | `00_docs/works/r008-kotlin-migration/kotlin-migration/key-progress.md:15` | aggregate Work와 S06-G Step의 frontmatter/body status ownership |
| R010-B structured start gate | `00_docs/works/r010-growth-entry-and-magazine/r010-b-cafe24-app-store/cafe24-app-store-integration/key-progress.md:22` | R010-A prerequisite와 Work Order의 `depends_on`/`work_gates` |
| Context Map recovery text | `00_docs/key-context-map.md` current-recovery section | live R008/R010 state와 historical S05 explanation의 혼합 여부 |

Installed Author, Reader, Coordinator와 Linker 계약은 실행 시점의 package source를 authority로 다시
읽고 제공된 과거 line number만으로 contract gap을 확정하지 않는다.

<!-- key: id=key.work.project-signal-triage.order.case-baseline refs=key.topic.impact-review key.topic.skill-contract -->
## 사례별 계획 기준선

| 사례 | Project document | Skill contract | R011 disposition |
|---|---|---|---|
| Context Map의 Backoffice·Workspace approval drift | pending source와 맞게 Context Map 정렬 | 반복 가능한 projection drift는 R011/S04에 전달 | project repair 우선 + normalization candidate |
| API Error Work의 과거 conflict blocker | validator/conflict 재실행 후 finalization resume | 해소된 blocker의 resumable candidate 탐지 | both candidate |
| R008 aggregate Work Progress에 accepted Step 상태 혼합 | Work Progress와 Step Progress 분리 | Author의 Work/Step Progress ownership 명문화 | both candidate |
| R010-B의 `depends_on`만 있고 start gate 없음 | Work Order에 필요한 `work_gates` 반영 | 기존 dependency/gate 계약은 유지하고 탐지 coverage 검토 | project repair 우선 |
| Context Map의 오래된 R008 recovery text | live recovery와 history 분리 | Author coverage와 R011/S04 generated recovery를 검토 | project repair 우선 + normalization candidate |
| 구버전 `global_state.active_round`가 복수 active Work를 표현하지 못함 | consuming project를 현재 단계에서 rewrite하지 않고 새 버전 적용 시 compatibility/migration으로 해소 | 복수 상태 의미와 진단은 R011/S01에서 완료 | project state no-change; version rollout |
| 복수 active Work의 Reader 상세 탐색 | project 상태·우선순위를 변경하지 않음 | 요청이 Work를 지목하지 않으면 요약 목록 뒤 이번 세션 focus를 한 번 질문하고 선택된 Work만 상세 탐색 | skill contract change |
| Accepted baseline 위 pending standard revision | 승인/재검증은 project authority 유지 | readiness 의미는 S03, baseline/revision join은 R011/S04에서 검토 | skill contract candidate |
| R008·R010 병렬 진행 상태 자체 | 자동 상태 변경 없음 | representation/recovery gap만 별도 검토 | no-change for project state |

<!-- key: id=key.work.project-signal-triage.order.method refs=key.topic.impact-review key.topic.work-recovery -->
## 분류 방법

1. Project source의 frontmatter, Index, live recovery text, validator evidence와 accepted decision을
   먼저 읽고 status owner를 구분한다.
2. 기존 skill contract가 이미 요구하는 동작인데 project source만 누락했다면 project repair로
   분류한다.
3. 기존 contract가 owner/status/recovery 의미를 모호하게 하거나 다른 프로젝트에서도 재현 가능한
   gap이면 skill-contract candidate로 분류한다.
4. Project repair와 contract 재발 방지가 모두 필요하면 `both`로 분리하고 각각 다른 owner와
   verification을 둔다.
5. 현재 상태가 계약상 유효하고 명명/가시성만 오해를 부르면 project state는 바꾸지 않고 contract
   또는 presentation candidate만 남긴다.
6. 복수 active Work이고 사용자 요청이 특정 Work를 지목하지 않으면 Work State의 ID·Round·상태·
   active-Step resolution만 요약하고 이번 세션의 focus Work를 한 번 질문한다. 선택 전에는 각 Work의
   Work Order와 Progress 본문을 모두 상세 탐색하지 않으며, 선택은 priority나 project state가 아니다.
7. Linker는 impact/stale/gap 후보를 분류하고, Author는 project documents, Main 또는 permitted
   Coordinator는 skill/code/test surfaces를 소유한다.
8. 같은 live/effective 의미의 반복이나 audit/history snapshot이 확인되면 source owner를 먼저
   결정하고 normalization 또는 intentional denormalization 후보로 R011/S04에 전달한다.

<!-- key: id=key.work.project-signal-triage.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: 프로젝트 사건에서 실제 skill contract 개선만 추출하고 project-only repair와 분리한다.
- Required candidates: Author/Reader/Linker/Coordinator contracts, finalization/readiness/dependency
  validators, scenario corpus와 project-document repair handoff template
- Conditional candidates: Skill source/runtime/test 변경은 재현 가능한 contract gap으로 분류된
  항목에만 포함한다.
- Excluded: external project source edits, acceptance transition, unrelated state migration
- Acceptance owner: Main
- Graph handling: project/skill surface 후보와 partial contract supersession은 Linker evidence로
  분류하고 각 source owner에게 분리한다.

<!-- key: id=key.work.project-signal-triage.order.completion refs=key.topic.acceptance key.topic.verification -->
## Completion Criteria

<!-- key: id=key.acceptance.project-signal-triage.classification -->
- `R011-S03-CC-01` 각 사례가 project repair, skill-contract change, both 또는 no-change로 evidence와
  함께 분류된다.
<!-- key: id=key.acceptance.project-signal-triage.project-document-repair -->
- `R011-S03-CC-02` Project repair는 status owner, 대상 문서, 검증과 안전한 resume point를 가지며
  스킬 변경을 자동 요구하지 않는다.
<!-- key: id=key.acceptance.project-signal-triage.skill-contract-threshold -->
- `R011-S03-CC-03` Skill-contract change는 현재 계약의 ambiguity/gap과 cross-project 재현 가능성을
  증명하고 output/test impact를 가진다.
<!-- key: id=key.acceptance.project-signal-triage.work-step-progress-separation requires_verification_of=key.standard.skill.author.progress-ownership -->
- `R011-S03-CC-04` Aggregate Work Progress와 accepted Step Progress의 status/approval/finalization
  ownership이 명시되고 혼합 fixture가 실패한다.
<!-- key: id=key.acceptance.project-signal-triage.readiness-revision requires_verification_of=key.standard.skill.reader.revision-readiness -->
- `R011-S03-CC-05` Reader가 accepted baseline과 pending revision을 어떻게 복구할지 결정하고
  strict partial semantics와 compatibility를 검증한다.
<!-- key: id=key.acceptance.project-signal-triage.resumable-finalization requires_verification_of=key.standard.skill.author.resumable-finalization -->
- `R011-S03-CC-06` 기록된 finalization blocker가 현재 해소됐으면 자동 완료하지 않고 resumable
  finalization 후보와 Author resume action을 반환한다.
<!-- key: id=key.acceptance.project-signal-triage.no-unnecessary-state-rewrite -->
- `R011-S03-CC-07` R008·R010 병렬 진행처럼 현재 계약상 유효한 project state를 skill 개선의
  부수 효과로 다시 쓰지 않는다.
<!-- key: id=key.acceptance.project-signal-triage.multi-active-session-focus requires_verification_of=key.standard.skill.reader.session-focus -->
- `R011-S03-CC-08` 복수 active Work에서 요청이 특정 Work를 지목하지 않으면 Reader가 상세 탐색 전
  비권위 session focus를 한 번 질문하고, 선택되지 않은 Work를 inactive·후순위로 해석하지 않는다.

<!-- key: id=key.work.project-signal-triage.order.verification refs=key.topic.verification -->
## Verification

- Approval drift, stale recovery text, missing `work_gates`와 Progress ownership fixtures
- Blocker present/resolved/still-unknown finalization-resume triad
- Accepted baseline + pending revision readiness fixtures
- Same project symptom with project-only, contract-only, both와 no-change evidence variants
- Linker impact classification and Author/Main source-surface ownership checks
- R008/R010 state-preservation regression and no automatic acceptance/status mutation
- zero/one/multi active Work와 explicit user target별 Reader session-focus 질문/비질문 fixture

<!-- key: id=key.work.project-signal-triage.order.expected-output refs=key.topic.verification key.topic.work-recovery -->
## Expected Output

- Project finding triage rubric와 case classification record
- Project-document repair handoff candidates with validation/resume points
- Accepted skill-contract change candidates and explicit no-change/excluded cases
- Author Work/Step Progress, Reader revision readiness와 resumable finalization contract/test updates
- 복수 active Work의 summary-first session-focus Reader contract/test update
- R011/S04 normalization/intentional-denormalization handoff candidates with source owners

<!-- key: id=key.work.project-signal-triage.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. 외부 프로젝트 source/evidence 없이 실제 상태 변경이나 finalization completion을 판단해야 한다.
2. Project source authority와 skill runtime authority를 구분할 수 없다.
3. Pending standard를 accepted baseline으로 간주하거나 acceptance를 자동 생성해야 한다.
4. 한 프로젝트 사례만으로 public contract를 변경해야 하고 cross-project 재현 근거가 없다.
5. Project repair와 skill implementation을 같은 owner/scope로 섞지 않고는 진행할 수 없다.
