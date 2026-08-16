---
doc_type: standard
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-12", accepted_by: user}
key:
  id: key.standard.skill.reader
  refs:
    - key.role.reader
    - key.topic.document-navigation
    - key.topic.work-preparation
    - key.topic.work-round
    - key.topic.artifact-graph
    - key.boundary.read-only
    - key.contract.output
---

# keystone-reader 기준서

<!-- key: id=key.standard.skill.reader.purpose refs=key.role.reader key.topic.document-navigation key.topic.work-preparation -->
## 목적

이 기준서는 `keystone-reader`의 상세 계약을 정의한다. `keystone-reader`는 원천 문서(2)를
읽어 프로젝트를 파악하고, 관련 기준서(3), 작업서(4), 진행 기록(5), 결정(6)을 찾아 main이
다음 작업을 준비할 수 있도록 read-only context brief를 만든다. Reader는 artifact graph가
필요한지 판단할 수 있지만, capability, code, config, schema, API, test artifact의 깊은
impact/stale/gap 해석은 `keystone-linker`로 넘긴다.

<!-- key: id=key.standard.skill.reader.scope refs=key.role.reader key.topic.document-navigation key.topic.work-preparation key.topic.artifact-graph key.contract.output -->
## 적용 범위

1. `keystone-reader`의 trigger와 non-trigger condition
2. Orientation, Navigator, Work Prep mode의 workflow와 output
3. 문서 root, standards/works tree, active parent Round 집합과 active Work 탐색 방식
4. Artifact graph 필요 여부 판단과 `keystone-linker` handoff cue
5. Repository snapshot과 document-to-repository mismatch reporting
6. Reader의 read-only boundary, stop condition, verification 기준

<!-- key: id=key.standard.skill.reader.out-of-scope refs=key.role.reader key.boundary.read-only -->
## 적용하지 않는 범위

1. 원천 문서(2), code, config, 진행 기록(5), 결정(6), generated file 수정
2. 기준서(3)나 작업서(4)의 creation/revision
3. high-impact topic 결정(6) 수집 또는 수락
4. subagent assignment, worker handoff 확정, report acceptance
5. persistent `agent/` 문서 생성
6. Skill implementation file 작성

<!-- key: id=key.standard.skill.reader.standard-relations refs=key.role.reader key.doc.standard key.topic.skill-contract key.topic.work-round key.topic.artifact-graph -->
## 기준 관계

1. Parent 기준서: `../../01_key-project-standard.md`
2. 상위 규칙: `STD-KEYSTONE-001`, `STD-KEYSTONE-010`, `STD-KEYSTONE-011`,
   `STD-KEYSTONE-012`, `STD-KEYSTONE-015`, `STD-KEYSTONE-017`,
   `STD-KEYSTONE-018`, `STD-KEYSTONE-020`, `STD-KEYSTONE-023`,
   `STD-KEYSTONE-024`, `STD-KEYSTONE-025`, `STD-KEYSTONE-026`,
   `STD-KEYSTONE-027`, `STD-KEYSTONE-040`, `STD-KEYSTONE-045`, `STD-KEYSTONE-046`
3. 충돌 처리: 이 기준서와 parent 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의
   결정(6)을 받는다. 결정 전까지는 parent 기준서를 임시 우선 기준으로 삼는다.
4. 상세화 범위: 이 기준서는 `STD-KEYSTONE-040`의 Reader 책임을 구현 가능한 수준으로
   상세화한다.

<!-- key: id=key.standard.skill.reader.skill-identity refs=key.role.reader key.topic.skill-contract -->
## Skill identity

1. Skill name: `keystone-reader`
2. Primary role: read-only project orientation, document navigation, context brief preparation
3. Primary user: main agent 또는 Keystone 문서를 탐색하려는 사용자
4. Output authority: Reader output은 source of truth가 아니며, 원천 문서(2)를 대체하지
   않는다.

<!-- key: id=key.standard.skill.reader.runtime-authority refs=key.role.reader key.topic.runtime-independence key.topic.initialization -->
## 런타임 권위와 초기화 경계

이 문서는 Keystone 저장소에서 Reader를 개발·검수하기 위한 원천 명세다. 배포된 Reader의
실행 계약은 설치된 skill package 안에서 완결되어야 하며, 소비 프로젝트의
`standards/skills/reader/**`를 required input으로 요구하지 않는다.

Keystone 문서가 없는 프로젝트의 code, README와 설정 조사는 Main의 일반 능력에 맡긴다.
Reader를 직접 호출한 경우에는 파일을 만들지 않고 현재 초기화 상태, 확인 가능한 partial
orientation, 읽지 못한 Keystone context와 Init 제안을 제공한다.

<!-- key: id=key.standard.skill.reader.trigger-condition refs=key.role.reader key.topic.document-navigation key.topic.work-preparation -->
## Trigger condition

`keystone-reader`는 다음 경우에 사용할 수 있다.

1. 프로젝트의 현재 문서 구조와 활성 작업을 파악해야 한다.
2. 현재 요청과 관련된 기준서(3), 작업서(4), 진행 기록(5)을 찾아야 한다.
3. 사용자가 "run active steps" 또는 "run the next step"처럼 활성·실행 가능 Step 복구가 필요한 요청을 한다.
4. main이 구현이나 문서 수정을 시작하기 전에 관련 source context를 준비해야 한다.
5. document-to-repository mismatch를 read-only로 확인하고 보고해야 한다.
6. Linker, Author, Clarify, Coordinator 중 다음에 호출할 skill을 판단할 context가 필요하다.
7. subagent handoff를 확정하기 전 Goal, context, verification, risk를 준비해야 한다.

<!-- key: id=key.standard.skill.reader.non-trigger-condition refs=key.role.reader key.boundary.read-only -->
## Non-trigger condition

`keystone-reader`는 다음 경우에 사용하지 않는다.

1. 새 기준서(3)나 작업서(4)를 작성하거나 수정해야 한다.
2. high-impact topic 결정(6)을 수집하거나 수락해야 한다.
3. subagent에게 작업을 실제 배정하거나 report를 acceptance해야 한다.
4. code, config, generated file, persistent agent-facing 문서를 수정해야 한다.
5. 사용자가 문서 탐색이 아니라 특정 구현 변경을 명확히 요청했고 source context가 이미
   충분하다.
6. 민감한 문서나 local-only path를 읽어야 하지만 사용자 승인 또는 project policy가
   불명확하다.

<!-- key: id=key.standard.skill.reader.required-input refs=key.role.reader key.topic.work-preparation -->
## Required input

Reader는 다음 input을 사용할 수 있어야 한다.

1. 사용자 요청 또는 main의 current task
2. 현재 repository root
3. 현재 instruction context
4. 존재하는 경우 설정된 document root(1) 또는 이를 해석하기 위한 project-local setting
5. 필요한 경우 target mode: Orientation, Navigator, Work Prep

Input이나 Keystone 문서가 부족하면 Reader는 추측하거나 파일을 만들지 않고
`risks_and_gaps`와 초기화 상태를 포함한 partial result를 보고한다.

<!-- key: id=key.standard.skill.reader.common-workflow refs=key.role.reader key.topic.document-navigation key.topic.work-preparation key.topic.work-round key.topic.artifact-graph -->
## Common workflow

Reader는 mode와 무관하게 다음 순서를 따른다.

1. Bootstrap 기준에 따라 초기화 상태와 document root 후보를 확인한다.
   `uninitialized` 또는 `partial`이면 존재하는 문서만 읽고 partial result와 Init 제안을
   제공한 뒤, 존재하지 않는 index/work 탐색 step은 건너뛴다.
2. `key-context-map.md`가 있으면 먼저 읽어 active standards와 active work를 파악한다.
3. `standards/00_key-index.md` 또는 해당 project의 standards index를 읽는다.
4. `works/00_key-index.md` 또는 해당 project의 root works index를 읽고 Work State에서 active
   parent Round 집합을 찾는다.
5. Active parent Round가 둘 이상이면 Work State 요약의 Round별 진행 중 Step까지만 확인하고
   아래 Round session focus gate를 적용한다.
6. Focus가 선택되거나 gate가 필요 없을 때 선택된 Round의 index와 active Work node index, 작업서(4), 진행
   기록(5)을 읽어 `round_id`, `work_id`, `active_steps`, `early_work`와 실행 가능 Step 후보를 함께
   복구한다. 전체/cross-Round 요청일 때만 필요한 여러 Round와 Work를 읽는다.
7. 현재 요청과 관련된 child index만 따라 내려가며 관련 없는 하위 기준서를 읽지 않는다.
8. 요청 또는 current work에 관련 키메타(9)가 있으면 같은 `key.id`를 참조하는
   문서를 탐색 후보로 확인한다.
9. 요청 또는 current work에 capability, code, config, schema, API, test 단서가 있으면 artifact graph가 필요한지
   판단하고, 깊은 후보 탐색이 필요하면 `keystone-linker`를 recommended next action으로 남긴다.
10. Reader가 확인한 키메타(9), link, path, heading, keyword는 Linker handoff seed로만 사용하고
    artifact relation을 확정하지 않는다.
11. 필요한 경우 shallow repository snapshot을 만든다.
12. File-changing work가 필요하다고 판단하면 Reader가 직접 수정하지 않고 Init, Author,
    Coordinator 또는 Main direct 중 적절한 next action을 남긴다.
13. output에는 항상 `sources_read`, `assumptions`, `risks_and_gaps`,
   `recommended_next_action`을 포함한다.

<!-- key: id=key.standard.skill.reader.revision-readiness kind=claim refs=key.role.reader key.topic.work-recovery key.topic.acceptance key.topic.verification -->
## Pending revision readiness

1. 기준서의 pending revision은 그 자체로 구조적 초기화 상태를 자동으로 `partial`로 낮추지 않는다.
   초기화 상태와 해당 정책 범위의 구현 권위 readiness를 분리한다.
2. 현재 source frontmatter의 `approval.state`가 `pending`이면 본문은 proposal과 탐색 evidence로
   읽되 accepted authority로 사용하지 않는다.
3. 현재 accepted source, decision, claim 또는 보존된 accepted version이 명시적으로 식별되고
   복구될 때만 `pending_with_baseline`이다. Context Map이나 Index의 `accepted` projection은
   pending source frontmatter를 덮지 않는다.
4. 기존 승인 이력을 주장하지만 그 의미 source를 복구할 수 없으면
   `pending_without_baseline`이다. Pending 본문이나 Git history를 암묵적인 baseline으로 만들지 않는다.
5. `pending_with_baseline`은 accepted baseline 범위만 권위로 사용하고 pending delta를 비권위 검토
   문맥으로 분리한다. `pending_without_baseline`은 영향을 받는 구현·수용만 멈추고 무관한 accepted
   Work는 계속할 수 있다.
6. `pending_without_baseline`은 Init repair가 아니라 Author 또는 Main에 baseline 복구, revision
   검토나 acceptance action으로 전달한다.
7. 복구 가능한 accepted 의미가 둘 이상 충돌하고 요청에 영향을 주면 `conflicted`로 보고한다.
   실제 사용자 의미 결정이 남을 때만 Clarify로 넘긴다.
8. View는 stable `key.id`, path, 현재 `approval.state`와 raw-byte digest에 결속된 source entry를
   stable ID와 path 순서로 정렬·중복 제거해 deterministic하게 만든다. Accepted entry만 effective
   authority를 구성하고 pending entry는 이를 대체하지 않는 review overlay다.
9. 이 readiness는 session output이다. 별도 source, compatibility manifest, project status로
   저장하지 않는다.

<!-- key: id=key.standard.skill.reader.session-focus kind=claim refs=key.role.reader key.topic.work-recovery key.topic.work-preparation -->
R011에서 수락한 Work-level session focus는 기존 문서와 test relation을 위한 historical
compatibility claim으로 보존한다. Current session selection에는 아래
`key.standard.skill.reader.round-session-focus`를 사용하며 이 claim으로 새 Work 선택 질문을 만들지
않는다.

<!--
key:
  id: key.standard.skill.reader.round-session-focus
  kind: claim
  refs:
    - key.role.reader
    - key.topic.work-recovery
    - key.topic.work-preparation
    - key.topic.work-round
  supersedes:
    - key.standard.skill.reader.session-focus
-->
## Multi-active Round session focus

1. Passing Work State에 active parent Round가 둘 이상이고 요청이 특정 Round를 지목하지 않으면
   Reader는 각 parent Round ref, status, 현재 진행 중인 Step 또는 unresolved reason만 후보 목록으로
   보여준 뒤 사용자에게 정확히 한 번 `해당 세션에서 어떤 라운드를 작업할까요?`라고 묻는다.
2. 사용자가 선택하기 전에는 각 후보 Round의 Work Order와 Progress 본문을 상세 탐색하지 않는다.
   Linker docs readiness를 시작하지 않는다.
3. Active parent Round가 0개 또는 1개이거나, 요청이 특정 Round를 명시하거나, 전체 active Round
   상태 또는 cross-Round 비교를 요구하면 질문을 생략한다.
4. 선택은 비권위 세션 문맥이다. 선택된 Round로 같은 요청을 자동 resume하되 선택되지 않은
   Round·Work·Step의 상태·우선순위를 변경하지 않는다. 선택을 canonical pointer, cache 또는
   project source에 기록하지 않는다.
5. Round 선택 뒤에는 현재 진행 중인 Step 목록을 사용자에게 알리되 Step 선택을 질문하지 않는다.
   별도 사용자 지정이 없으면 dependency와 `work_gates`를 만족하는 active Step 중 번호가 가장
   낮은 Step을 기본 대상으로 삼는다. 가장 낮은 Step이 blocked이면 그 이유와 다음 실행 가능
   Step을 알리며 상태나 priority를 자동 변경하지 않는다.

<!-- key: id=key.standard.skill.reader.mode-contract refs=key.role.reader key.contract.output key.topic.work-preparation -->
## Mode contract

<!-- key: id=key.standard.skill.reader.orientation-mode refs=key.role.reader key.topic.document-navigation key.topic.work-round -->
### Orientation Mode

Orientation Mode는 project-level overview를 만든다.

1. 읽기 범위: instruction, 설정된 document root(1), context map, standards index, root works
   index, active parent Round index, active work, shallow repository snapshot
2. 금지: document, code, config, 진행 기록(5), 결정(6), generated file 수정
3. Repository snapshot 제한:
   - repository root
   - top-level directory
   - key config/build file
   - expected skill/source directory
   - workspace status summary
   - 명백한 document-to-repository mismatch signal
4. Output field:
   - `document_root`
   - `project_summary`
   - `repository_snapshot`
   - `active_document_map`
   - `artifact_graph_summary`
   - `active_rounds`
   - `selected_round`
   - `round_id`
   - `round_index`
   - `work_id`
   - `active_steps`
   - `early_work`
   - `current_work_status`
   - `status_sources`
   - `status_authority_order`
   - `status_conflicts`
   - `recommended_read_order`
   - `operational_boundaries`
   - `risks_and_gaps`
   - `recommended_next_action`
   - `keystone_context_brief`
   - `sources_read`
   - `assumptions`

<!-- key: id=key.standard.skill.reader.navigator-mode refs=key.role.reader key.topic.document-navigation key.contract.output key.topic.work-round key.topic.artifact-graph -->
### Navigator Mode

Navigator Mode는 현재 요청과 관련된 원천 문서(2)를 찾는다.

1. Input: 사용자 요청, current task, known document root
2. 읽기 범위: standards index, root works index, active parent Round index, parent 기준서, 관련 child
   기준서, active work, 관련 아티팩트 그래프(14) 후보
3. Output field:
   - `request_summary`
   - `key_ref_queries`
   - `matched_documents`
   - `artifact_seed_candidates`
   - `key_ref_matched_candidates`
   - `artifact_graph_needed`
   - `mismatches`
   - `active_rounds`
   - `selected_round`
   - `round_id`
   - `round_index`
   - `work_id`
   - `status_sources`
   - `status_conflicts`
   - `recommended_read_order`
   - `why_each_document_matters`
   - `missing_or_ambiguous_documents`
   - `risks_and_gaps`
   - `recommended_next_action`
   - `sources_read`
   - `assumptions`
4. 금지: 관련 없는 문서 tree 전체를 읽거나, 문서 부재를 조용히 새 문서 생성으로 해결하기

<!-- key: id=key.standard.skill.reader.work-prep-mode refs=key.role.reader key.topic.work-preparation key.contract.output key.topic.work-round key.topic.artifact-graph -->
### Work Prep Mode

Work Prep Mode는 main이 다음 작업을 실행하거나 subagent handoff를 준비할 수 있게 한다.
단, final handoff를 확정하지 않는다.

1. Input: current task 또는 active work step
2. 읽기 범위: 관련 기준서(3), root works index, selected parent Round index, work node index,
   작업서(4), 진행 기록(5), completion criteria, verification note, related
   capability/code/config/schema/API/test artifact 후보
3. Output field:
   - `active_rounds`
   - `selected_round`
   - `round_id`
   - `round_index`
   - `work_id`
   - `goal`
   - `source_context`
   - `applicable_standards`
   - `impact_seeds`
   - `artifact_graph_needed`
   - `artifact_seed_candidates`
   - `key_ref_queries`
   - `key_ref_matched_candidates`
   - `active_steps`
   - `early_work`
   - `current_work_status`
   - `status_sources`
   - `status_authority_order`
   - `status_conflicts`
   - `scope`
   - `completion_criteria`
   - `verification`
   - `suggested_role`
   - `stop_conditions`
   - `risks_and_gaps`
   - `recommended_next_action`
   - `final_handoff_ready`
   - `sources_read`
   - `assumptions`
4. `final_handoff_ready`는 Reader output에서는 기본적으로 `false`다. Final worker assignment는
   Coordinator가 별도로 확정한다.
5. 금지: subagent assignment 확정, progress status 변경, implementation 시작

<!-- key: id=key.standard.skill.reader.mismatch-handling refs=key.role.reader key.topic.document-navigation key.topic.artifact-graph key.boundary.read-only -->
## Mismatch handling

원천 문서(2), 아티팩트 그래프(14), repository state가 충돌하면 Reader는 다음처럼 처리한다.

1. 자동 수정하지 않는다.
2. mismatch의 source와 evidence를 기록한다.
3. 영향을 받는 문서, 작업, capability, code, config, schema, API, test artifact 후보를 식별한다.
4. 사용자 또는 main에게 선택지를 제시한다.
   - 문서 업데이트를 준비한다.
   - code work를 준비한다.
   - 추가 read-only 조사를 진행한다.
   - 현재 작업을 중단한다.
5. mismatch가 current task correctness에 영향을 주면 `recommended_next_action`에
   decision need를 포함한다.

<!-- key: id=key.standard.skill.reader.context-brief refs=key.role.reader key.topic.work-preparation key.contract.output -->
## Context brief

Reader는 필요한 경우 다음 fields를 가진 `keystone_context_brief`를 만든다.

```yaml
keystone_context_brief:
  document_root:
  active_rounds: []
  selected_round:
  current_work:
  session_focus:
    state:
    candidates:
    selected_round:
    authority: non_authoritative
  active_steps:
  early_work:
  current_work_status:
  status_sources:
    context_map:
    root_works_index:
    active_round_indexes:
    work_progress:
  status_authority_order:
    - root_works_index
    - active_round_indexes
    - work_progress
    - context_map
  status_conflicts:
  human_intent_summary:
  applicable_standards:
  accepted_decisions:
  relevant_work_orders:
  artifact_graph_needed:
  artifact_seed_candidates:
  recommended_next_skill:
  risks_and_gaps:
  final_handoff_ready: false
```

`artifact_graph_needed`가 true이면 Reader는 artifact 후보를 확정하지 않고 `keystone-linker`를
recommended next skill로 제안한다.

<!-- key: id=key.standard.skill.reader.user-response refs=key.role.reader key.contract.output key.topic.skill-contract -->
## 기본 사용자 응답

Reader는 `reader_output`과 `keystone_context_brief`를 agent-facing structured payload로 유지한다.
기본 사용자 응답은 다음 항목만 짧게 보여준다.

1. 현재 상태: document root, active parent Rounds, selected Round, current Work, active Steps와
   status sources
2. 핵심 판단: source documents와 repository snapshot에서 확인한 결론
3. 주요 risk 또는 mismatch: status conflict, stale document, missing context
4. 다음 권장 행동: Reader, Clarify, Author, Linker, Coordinator 중 필요한 next action
5. 주요 근거: 핵심 source document 3-5개

Full `reader_output`은 사용자가 요청하거나 Coordinator/Linker handoff, audit/debug,
verification evidence에 필요할 때만 노출한다. Optional `keystone-viewer`가 제공되면 Reader
payload를 사용자-facing view로 렌더링할 수 있지만, Reader의 read-only 판단과 recommended
next action을 바꾸지 않는다.

사용자-facing 응답을 보내기 전에는 `STD-KEYSTONE-045`의 Payload Disclosure Gate를 적용한다.
Full payload 요청, handoff, audit/debug, verification evidence 필요성이 없으면 `*_output`,
`*_result`, `*_report`, `worker_assignment`, `keystone_routing_decision` 원문 block을 기본
응답에 노출하지 않는다. 기본 응답은 payload 의미를 상태/판단 요약, 대표 근거, 검증 요약,
남은 risk, 다음 행동, 주요 출처로 압축한다.

<!-- key: id=key.standard.skill.reader.metadata-handling refs=key.role.reader key.topic.document-navigation key.topic.keystone-metadata key.topic.code-anchor key.topic.artifact-graph -->
## 키메타와 코드 앵커 handling

Reader는 키메타(9)와 코드 앵커(18)를 관련 문서와 Linker handoff seed 탐색 단서로 사용한다.

1. 같은 `key.id`를 참조하는 문서는 관련 문서 후보로 검토한다.
2. 같은 `key.refs`가 있어도 자동으로 관련 문서나 artifact라고 확정하지 않는다.
3. `key.refs`나 typed relation이 없어도 관련 없음으로 단정하지 않는다.
4. Navigator Mode와 Work Prep Mode output에는 사용한 `key.refs`, artifact seed candidate,
   `artifact_graph_needed` 여부를 포함한다.
5. Artifact relation, impact candidate, stale candidate, metadata gap 등급화는
   `keystone-linker`가 담당한다.
6. Reader가 발견한 inferred relation은 Linker seed candidate이며 자동 수정 근거가 아니다.

<!-- key: id=key.standard.skill.reader.stop-condition refs=key.role.reader key.boundary.read-only key.topic.work-preparation -->
## Stop condition

Reader는 다음 상황에서 중단하거나 main/user 결정(6)을 요청한다.

1. 복수 document root가 충돌해 read scope 자체를 안전하게 정할 수 없다.
2. 복구할 active Round나 active Step이 없다는 사실이 아니라, 서로 충돌하는 상태 출처 때문에
   current task 방향을 정할 수 없다.
3. 원천 문서(2)가 현재 사용자 방향과 충돌한다.
4. 문서 변경이 필요한데 Reader mode가 read-only라 처리할 수 없다.
5. 민감한 원천 문서(2)나 local-only path를 읽어야 하지만 권한 또는 policy가 불명확하다.
6. document-to-repository 또는 아티팩트 그래프(14) mismatch가 current task의 방향을 바꿀 수 있다.

관련 기준서(3) 또는 작업서(4)의 단순 부재는 stop condition이 아니다. Reader는 partial
result와 Init 또는 Author 제안을 제공한다.

<!-- key: id=key.standard.skill.reader.verification refs=key.role.reader key.contract.output key.topic.verification -->
<!-- key: id=key.standard.skill.reader.dependency-recovery refs=key.role.reader key.topic.work-recovery key.topic.work-sequence -->
## Dependency recovery

1. Reader는 각 active/실행 가능 Step에 적용되는 gate와 전체 work completion gate를 분리해 복구한다.
2. 각 dependency를 `satisfied`, `waiting`, `unresolvable`, `invalid`, `unknown`으로 보고하고
   target locator, condition evidence, blocking 적용 범위를 함께 보여준다.
3. Structured metadata를 우선하고 legacy conflict, missing/cancelled/superseded target은
   fail-soft risk로 보고한다.
4. Reader는 dependency 판정으로 work status를 바꾸거나 worker를 할당하지 않는다.

## Verification

Reader 기준은 다음 방법으로 검증한다.

1. Reader contract만 보고 trigger와 non-trigger를 구분할 수 있어야 한다.
2. Mode별 output field가 `STD-KEYSTONE-040`의 상위 Reader 책임과 일관되어야 한다.
3. Reader output은 원천 문서(2)를 대체하거나 수정하지 않아야 한다.
4. Work Prep Mode output은 coordinator가 `round_id`, `work_id`, `active_steps`를 가진
   final handoff를 만들기 전 단계로 사용할 수
   있어야 한다.
5. 키메타 또는 코드 앵커를 사용한 경우 output에서 사용한 `key.refs`, artifact seed candidate,
   `artifact_graph_needed` 여부를 확인할 수 있어야 한다.
6. Reader는 아티팩트 그래프(14) 필요성을 보고할 수 있지만 impact/stale/gap 후보를 확정하거나
   code/config/schema/API/test를 수정하지 않아야 한다.
7. 기본 사용자 응답은 structured payload를 그대로 노출하지 않고 핵심 상태, risk, next action,
   주요 출처만 요약해야 한다.
8. File-changing next action은 필요한 실행 주체를 제안하되 모든 작은 작업에 별도 routing
   payload를 요구하지 않아야 한다.
9. 프로젝트 로컬 Reader 기준서가 없어도 설치된 contract와 존재하는 문서만으로 동작해야 한다.
10. 복수 active parent Round의 대상 미지정 요청은 진행 중 Step 요약 뒤 상세 탐색 전 정확한
    Round focus 질문을 한 번 하고, explicit/cross-Round 요청은 질문을 생략해야 한다. 선택 뒤
    Step은 질문 없이 lowest executable 기본 규칙으로 정하되 project status나 priority를 변경하지
    않아야 한다.
11. Verification command:
   - `rg --files 00_docs`
   - Reader 관련 기준서를 읽어 link와 scope consistency 확인

<!-- key: id=key.standard.skill.reader.context-readiness refs=key.role.reader key.role.linker key.topic.work-recovery key.boundary.read-only -->
## Session context readiness

사용자가 Codex 세션 시작에 Reader를 명시 호출하면 Reader는 project orientation과 context readiness의
진입점이 된다. Reader는 cache owner가 아니며 repository source read-only를 유지한다.

1. Installed Reader package의 `scripts/work_state_runtime.py --root ROOT`를 먼저 실행한다. Passing
   envelope의 initialization, active parent Round/Works/Steps, dependency/finalization gate,
   diagnostic과 complete source generation을 authoritative current work-state projection으로
   복구한 뒤 root/round/work index와 active Progress를 narrative context로 읽는다. Acceptance-event와
   `latest_accepted_round`은 current passing 조건이나 필수 context field가 아니다. Runtime failure나
   incomplete generation을 서로 같은 pointer claim으로 대체하지 않는다.
2. Passing envelope에 active parent Round가 둘 이상이고 요청이 특정 Round 또는
   전체/cross-Round 범위를 명시하지 않으면 `Multi-active Round session focus`를 먼저 적용한다.
   Focus 선택 전에는 candidate Round별 현재 진행 중 Step만 요약하고 Work Order와 Progress 본문을
   상세 탐색하거나 Linker docs readiness를 시작하지 않는다.
3. Focus가 선택되거나 gate가 필요 없으면 docs discovery scope에 대해 permissionless Linker
   index-readiness를 요청한다.
   Scope token은 worktree identity, sorted path set과 각 file raw-byte digest를 포함한다.
4. Code/config/schema/test scan은 artifact context가 요청되거나 downstream skill input에 실제로
   필요할 때만 lazy repository scope로 확장한다.
5. Fresh external index가 있으면 재사용하고 stale/missing/corrupt이면 Linker refresh 또는 source
   직접 탐색으로 fail-soft fallback한다. Cache 문제 자체를 사용자 decision으로 올리지 않는다.
6. Reader가 만든 context brief는 freshness token, discovery scope, source citations와 unresolved
   gap을 포함한다. 다른 skill은 token이 fresh한 동안 이를 재사용하고 write 후에는 영향을 받은
   scope를 invalidation한다.
7. Reader -> Linker 호출은 `initiator: reader` recursion guard를 전달한다. 해당 Linker execution은
   같은 chain에서 Reader를 다시 호출하지 않는다. Linker가 Reader recovery를 시작한 chain도
   반대 방향으로 동일하게 제한한다.
8. Permissionless Linker의 raw readiness/index payload는 agent-facing handoff다. 기본 사용자 응답은
   project state, relevant risk와 next action만 요약한다.
9. 선택된 context에 criterion verification, effective Decision 또는 Work output/test summary가
   필요할 때만 `include_source_views`를 요청한다. 이 결과는 Linker가 validator와 같은
   reconstructed `GraphSnapshot`에서 계산한 source-bound session-only projection이며
   `source_generation`과 unresolved diagnostic을 함께 보존한다.
10. Output/test target이 필요하면 lazy repository scope를 사용한다. `verified` view를 automatic
    acceptance나 approval로 해석하지 않고, default readiness에는 가벼운 owner/ref 결과만 유지한다.
