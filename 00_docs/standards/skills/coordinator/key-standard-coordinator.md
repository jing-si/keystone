---
doc_type: standard
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-06", accepted_by: main}
key:
  id: key.standard.skill.coordinator
  refs:
    - key.role.coordinator
    - key.role.subagent
    - key.standard.subagent
    - key.topic.work-execution
    - key.topic.work-round
    - key.topic.artifact-graph
    - key.topic.external-assist
    - key.topic.verification
    - key.topic.acceptance
---

# keystone-coordinator 기준서

<!-- key: id=key.standard.skill.coordinator.purpose refs=key.role.coordinator key.role.subagent key.topic.work-execution key.topic.formal-workflow -->
## 목적

이 기준서는 `keystone-coordinator`의 상세 계약을 정의한다. `keystone-coordinator`는
main이 supervisor로 남아 있는 상태에서 작업서(4)의 Goal unit, Reader context brief, Linker
report, Author Change Set(17)을 bounded worker assignment(19)로 만들고, worker report(20)를
Keystone workflow로 회수하는 bounded assignment broker다.

Worker assignment와 worker report는 runtime output이며 원천 문서(2)를 대체하지 않는다.
코드 수정은 대표적인 실행 작업이지만, Coordinator의 책임은 코딩 방법론이 아니라 context,
authority, scope, execution environment boundary, stop condition, report contract를 정하는 것이다.

<!-- key: id=key.standard.skill.coordinator.scope refs=key.role.coordinator key.role.subagent key.standard.subagent key.topic.verification key.topic.acceptance key.topic.formal-workflow key.topic.artifact-graph -->
## 적용 범위

1. `keystone-coordinator`의 trigger와 non-trigger condition
2. Current Step Brief, Context Pack, worker assignment 구성
3. Purpose preset, authority, injected skill contract routing
4. Worker handoff boundary와 reviewer focus 도출
5. Worker report handling
6. Review, verification, repair, escalation, acceptance flow
7. Change Set(17), Linker report, reuse discovery, graph validation 조율
8. Execution environment boundary
9. 진행 상태와 report status update boundary
10. 외부 코딩 스킬(12)의 injected skill 선택과 주입
11. 파생 에이전트 문서(8) 생성 조건

<!-- key: id=key.standard.skill.coordinator.out-of-scope refs=key.role.coordinator key.topic.skill-contract key.topic.external-assist -->
## 적용하지 않는 범위

1. 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 기록의 작성 기준과 수정 범위 설계 자체
2. High-impact topic 질문 수집과 결정(6) 확정
3. Read-only project orientation 또는 document navigation만 수행하는 작업
4. Worker가 전체 작업서(4)를 재해석하거나 scope를 확장하게 하기
5. Completion evidence 없이 `work_status: complete`로 표시하거나 Main acceptance 없이
   `approval.state: accepted`로 표시하기
6. 명시적 필요 없이 persistent worker handoff나 reviewer brief 생성
7. Implementation, schema, auth/security, generated/codegen, shared architecture 변경을
   main/user decision 없이 자동 worker task로 보내기
8. 외부 보조 스킬(12)을 Coordinator를 대체하는 automatic 또는 mandatory execution layer로 만들기
9. Artifact relation, impact candidate, stale candidate, metadata gap을 Linker 없이 확정하기
10. Worker가 추가 subagent를 만들게 하기

<!-- key: id=key.standard.skill.coordinator.standard-relations refs=key.role.coordinator key.doc.standard key.topic.skill-contract key.standard.subagent key.topic.work-round key.topic.artifact-graph -->
## 기준 관계

1. Parent 기준서: `../../01_key-project-standard.md`
2. 상위 규칙: `STD-KEYSTONE-001`, `STD-KEYSTONE-006`, `STD-KEYSTONE-007`,
   `STD-KEYSTONE-015`, `STD-KEYSTONE-016`, `STD-KEYSTONE-017`,
   `STD-KEYSTONE-018`, `STD-KEYSTONE-020`, `STD-KEYSTONE-022`,
   `STD-KEYSTONE-023`, `STD-KEYSTONE-024`, `STD-KEYSTONE-025`,
   `STD-KEYSTONE-026`, `STD-KEYSTONE-027`, `STD-KEYSTONE-030`, `STD-KEYSTONE-031`,
   `STD-KEYSTONE-032`, `STD-KEYSTONE-033`, `STD-KEYSTONE-043`, `STD-KEYSTONE-045`
3. 관련 기준서: `../../subagents/key-standard-subagents.md`
4. 관련 결정(6): `00_docs/works/key-decisions.md`
5. 충돌 처리: 이 기준서와 parent 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의
   결정(6)을 받는다. 결정 전까지는 parent 기준서를 임시 우선 기준으로 삼는다.
6. 상세화 범위: 이 기준서는 `STD-KEYSTONE-043`의 Coordinator behavior를 구현 가능한
   수준으로 상세화한다.

<!-- key: id=key.standard.skill.coordinator.skill-identity refs=key.role.coordinator key.topic.skill-contract -->
## Skill identity

1. Skill name: `keystone-coordinator`
2. Primary role: bounded assignment brokering, Goal assignment, worker report handling,
   Change Set coordination, review, verification, acceptance coordination
3. Primary user: main agent
4. Output authority: Coordinator output은 main의 orchestration 판단을 돕는 runtime output이며
   원천 문서(2)를 대체하지 않는다.

<!-- key: id=key.standard.skill.coordinator.runtime-authority refs=key.role.coordinator key.topic.runtime-independence key.topic.user-decision -->
## 런타임 권위와 사용 허락

이 문서는 Keystone 저장소에서 Coordinator를 개발·검수하기 위한 원천 명세다. 배포된
Coordinator의 실행 계약은 설치된 skill package 안에서 완결되어야 하며, 소비 프로젝트의
`standards/skills/coordinator/**`를 required input으로 요구하지 않는다.

Coordinator는 영향 범위가 크므로 work scope마다 사용자 허락을 받는다. 사용자가
`keystone-coordinator`를 직접 호출하면 해당 요청 범위의 허락으로 본다. 같은 범위의 assignment,
review, repair, verification에는 반복 확인하지 않지만 scope나 risk가 커지면 다시 묻는다.

<!-- key: id=key.standard.skill.coordinator.trigger-condition refs=key.role.coordinator key.topic.work-execution key.role.subagent key.standard.subagent key.topic.author-edit-contract -->
## Trigger condition

`keystone-coordinator`는 다음 경우에 사용할 수 있다.

1. 사용자 허락이 있고 작업서(4)의 active 또는 실행 가능 Step을 Goal unit으로 실행해야 한다.
2. Main이 bounded worker assignment(19)를 만들어 worker에게 전달해야 한다.
3. Current Step Brief, Context Pack, worker handoff boundary, reviewer focus를 구성해야 한다.
4. Worker report(20)를 받아 accept candidate, repair, review, verify, escalate 중 다음 결정을
   내려야 한다.
5. 진행 상태와 report status를 분리해 기록해야 한다.
6. Verification을 기준서(3)에서 추출해 checklist로 만들고 필요하면 verifier Goal을 배정해야
   한다.
7. Worker 결과가 scope, acceptance criteria, existing user change와 충돌하는지 판단해야
   한다.
8. 문서 작업이라도 Author Edit Contract를 바탕으로 document_edit, review, verify assignment가
   이어지는 formal workflow가 필요하다.
9. Linker report를 바탕으로 문서, capability, code, config, schema, API, test artifact 변경 후보를 Change
   Set(17) 단위로 조율해야 한다.
10. Keystone 작업 문맥에서 code/config/schema/API/test 수정 요청에 대해 Main direct보다
    위임이 적절하고, 사용자가 bounded implementation assignment를 허락했다.
11. Linker report가 code/config/schema/API/test anchor gap 또는 stale anchor를 보고했고, bounded
    anchor edit assignment를 구성해야 한다.
12. 현재 work scope의 Coordinator 사용이 허락되었고, 사용자가 `superpowers` 같은 외부 코딩
    스킬(12)을 명시해 해당 workflow를 worker assignment에 주입해야 한다.
13. Repo-local `skills/keystone-*/SKILL.md` 변경이 여러 파일, delegation, formal review,
    verification, execution environment 조율 또는 report handling을 요구해 Main direct보다
    허락된 Coordinator가 적합하다.

<!-- key: id=key.standard.skill.coordinator.non-trigger-condition refs=key.role.coordinator key.topic.skill-contract -->
## Non-trigger condition

`keystone-coordinator`는 다음 경우에 사용하지 않는다.

1. 원천 문서(2)의 작성 기준, 수정 범위, 영향 문서 판단이 주된 작업이다.
2. 사용자가 high-impact policy, scope, 문서 구조, 스킬 계약을 먼저 결정해야 한다.
3. 현재 요청과 관련된 기준서(3)와 작업서(4)를 read-only로 찾기만 하면 된다.
4. Active/실행 가능 Step, completion criteria, applicable standard를 복구할 수 없다.
5. Work unit이 bounded worker assignment로 나뉘지 않았다.
6. 작업이 high-risk implementation인데 main/user decision 없이 worker에게 보낼 수 없다.
7. 민감한 정보, local-only path, private data가 포함될 수 있지만 policy가 불명확하다.
8. 문서 작업인데 Author Edit Contract 또는 승인된 문서 수정 범위가 없다.
9. 현재 work scope에 대한 사용자 허락이 없다.

<!-- key: id=key.standard.skill.coordinator.required-input refs=key.role.coordinator key.topic.work-execution key.topic.artifact-graph -->
## Required input

Coordinator는 다음 input을 사용할 수 있어야 한다.

1. 사용자 요청 또는 main의 current task
2. 설정된 document root(1)
3. 관련 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 기록
4. Active steps 또는 이를 복구하기 위한 active round와 active work state
5. Completion criteria와 verification expectation
6. Included, excluded, conditional work scope
7. Stop conditions와 escalation conditions
8. 현재 workspace state와 existing-change risk
9. 문서 formal workflow인 경우 Author Edit Contract
10. 아티팩트 그래프(14)가 관련된 경우 Linker report, impact seeds, artifact candidates, 또는
    Change Set(17)
11. Worker에게 주입할 skill contract 후보
12. 사용자가 명시한 외부 코딩 스킬(12), 또는 선택이 필요한 available coding skill 후보
13. 위임 실행에 필요한 사용자 또는 host의 실행 환경 제약
14. Code/config/schema/API/test anchor 변경이 필요한 경우 Linker report의 recommended anchor
    change, affected artifact ID, relation evidence, verification expectation
15. 복수 surface나 권한 경계가 있어 명시적으로 남긴 경우 routing context

Input이 부족하면 Coordinator는 worker를 배정하지 않고 Reader, Author, Clarify, Linker 중
필요한 다음 작업을 제안하거나 main/user 결정(6)을 요청한다.

<!-- key: id=key.standard.skill.coordinator.common-workflow refs=key.role.coordinator key.topic.work-execution key.topic.artifact-graph key.topic.verification key.topic.acceptance key.standard.subagent -->
## Common workflow

Coordinator는 다음 순서를 따른다.

1. 사용자 허락, 설정된 document root(1)와 root works index를 확인한다.
2. 복수 surface나 권한 경계가 있으면 필요한 routing context를 확인한다.
3. Active round index와 active work node index를 따라 `round_id`, `work_id`, `active_steps`와
   workflow state를 복구한다.
4. 작업서(4)에서 Goal, Scope, Source Context, Completion Criteria, Stop Conditions,
   Verification, Expected Output을 추출한다.
5. 관련 기준서(3)에서 verification expectation과 forbidden change를 추출한다.
6. Reader context brief와 Author Change Set(17)을 확인한다.
7. 아티팩트 그래프(14) 후보가 있으면 Linker report를 요구하거나 기존 Linker report에서 impact
   seed, required/optional/excluded candidates를 확인한다.
8. Work unit이 bounded worker assignment로 자를 수 있는지 판단한다.
9. Subagent 기준서에 따라 purpose preset, authority, injected skill contract를 선택한다.
10. Code/config/schema/API/test 수정 요청에서 외부 코딩 스킬(12)이 명시되었으면 Coordinator를 유지한 채
   해당 스킬을 injected skill로 주입한다.
11. Domain-specific 또는 명시된 external coding skill이 없으면 `keystone-default-bounded-worker`
    contract를 선택한다.
12. 여러 coding skill 후보가 있고 선택에 따라 workflow, verification, risk가 달라질 때만
    main/user 선택을 요청한다.
13. 위임 실행의 isolation, worktree, branch, concurrency는 사용자 지시, 주입된 skill과 host
    환경의 계약을 따른다.
14. 선택한 Step의 Step Brief, Context Pack, worker assignment를 만든다.
15. Worker handoff boundary 또는 reviewer focus를 구성한다.
16. Worker report(20)를 받은 뒤 actual state와 output을 확인한다.
17. 필요하면 별도 review 또는 verify assignment를 배정한다.
18. Report 결과를 accept candidate, repair, verify, escalate, block 중 하나로 처리한다.
19. Main acceptance 조건이 충족된 경우에만 진행 기록(5)을 갱신한다.

<!-- key: id=key.standard.skill.coordinator.runtime-output-contract refs=key.role.coordinator key.contract.output key.topic.work-execution key.topic.work-round key.topic.artifact-graph key.standard.subagent -->
## Runtime output contract

Coordinator는 상황에 따라 다음 runtime output을 만들 수 있다.

1. Step Brief
   - `round_id`, `work_id`, `step_id`, active step set, Goal, completion criteria, applicable
     standards, excluded work, expected edit area, verification, known risks,
     `main_context_checkpoint`를 담는다.
2. Context Pack
   - worker나 reviewer가 읽어야 하는 관련 기준서(3), 작업서(4), 결정(6), scope,
     progress 발견사항, 키메타와 코드 앵커 기반 관련 문서와 artifact 후보를 담는다.
3. Change Set brief
   - intent, changed nodes, impact seeds, required candidates, optional candidates, excluded
     scope, verification, acceptance state를 담는다.
4. Worker assignment
   - assignment id, goal, completion criteria, intent summary, purpose, role hint, authority,
     source documents, accepted decisions, applicable standards, context pack, injected skill
     contract, scope, forbidden changes, stop conditions, verification, execution environment,
     main context checkpoint, return report contract를 담는다.
5. Worker report review
   - status, changed files, changed artifact IDs, verification result, scope check,
     document sync need, metadata sync need, stale candidates, source conflicts,
     main context preservation, residual risk를 확인한다.
6. Worker handoff
   - subagent 기준서 기준의 purpose, role hint, authority, primary scope, read scope,
     direct edit scope, conditional edit scope, escalation zone, forbidden changes,
     execution environment constraints를 담는다.
7. Reviewer brief
   - worker goal, completion criteria, changed files 또는 문서 output, known risks,
     verification result, 같은 `key.id`를 참조하는 문서와의 충돌 여부, reviewer focus를
     담는다.
8. Verification checklist
   - 기준서-led verification expectation, graph validation, local verification note를 합쳐 만든다.

Main context checkpoint는 다음 shape을 우선 사용한다.

```yaml
main_context_checkpoint:
  global_intent_summary:
  accepted_decisions_in_effect:
  current_work_identity:
    round_id:
    work_id:
    step_id:
  current_user_instruction:
  progress_state:
  session_state:
  source_conflicts:
    - document:
      conflict:
      resolved_by:
  source_conflict_check:
  stale_work_order_check:
  accepted_decision_propagation_check:
  preserved_boundaries:
    - main_acceptance_only
    - no_scope_expansion
    - no_child_subagents
    - single_workspace_one_writer
  acceptance_owner: main
```

이 runtime output은 기본적으로 persistent 문서가 아니다. 명시적 필요가 있을 때만 파생
에이전트 문서(8)로 저장할 수 있다.

<!-- key: id=key.standard.skill.coordinator.user-response refs=key.role.coordinator key.contract.output key.topic.skill-contract -->
## 기본 사용자 응답

Coordinator는 worker assignment, worker report, worker report review를 agent-facing runtime
payload로 유지한다. 기본 사용자 응답은 다음 항목만 짧게 보여준다.

1. 현재 workflow 판단: assign, review, verify, repair, escalate, accept candidate, block
2. assignment 또는 report의 목표와 scope 요약
3. verification 결과와 Main acceptance 가능 여부
4. residual risk와 source/document sync 필요 여부
5. 다음 권장 행동과 주요 source refs

Full worker assignment/report payload는 사용자가 요청하거나 worker handoff, audit/debug,
verification evidence에 필요할 때만 노출한다. Optional `keystone-viewer`는 Coordinator runtime
payload를 사용자-facing view로 표현할 수 있지만 scope, authority, verification, report status,
Main acceptance readiness를 바꾸지 않는다.

사용자-facing 응답을 보내기 전에는 `STD-KEYSTONE-045`의 Payload Disclosure Gate를 적용한다.
Full payload 요청, worker handoff, audit/debug, verification evidence 필요성이 없으면
`*_output`, `*_result`, `*_report`, `worker_assignment`, `keystone_routing_decision` 원문 block을
기본 응답에 노출하지 않는다. 기본 응답은 payload 의미를 workflow 판단, scope 요약, 검증 요약,
Main acceptance readiness, 남은 risk, 다음 행동, 주요 출처로 압축한다.

<!-- key: id=key.standard.skill.coordinator.worker-assignment-contract refs=key.role.coordinator key.contract.output key.contract.report -->
## Worker assignment and report contract

Worker assignment는 다음 shape을 우선 사용한다.

`routing_context_ref`는 복수 surface, 권한 경계 또는 audit 요구 때문에 routing context를
명시적으로 남긴 경우에만 포함한다.

```yaml
worker_assignment:
  assignment_id:
  routing_context_ref:
  goal:
  completion_criteria:
  intent_summary:
  purpose: investigate | document_edit | implement | review | verify
  role_hint:
  authority: read_only | bounded_edit | review_only | verification
  source_documents:
  accepted_decisions:
  applicable_standards:
  context_pack:
    required_sources:
    optional_sources:
    artifact_context:
    anchor_change_context:
      allowed_anchor_changes:
        - artifact_id:
          surface: code_anchor | config_anchor | schema_anchor | api_anchor | test_anchor
          relation:
          reason:
          linker_report_ref:
      forbidden_anchor_changes:
      verification_required:
    reuse_candidates:
    test_candidates:
    document_sync_candidates:
    metadata_sync_risks:
  main_context_checkpoint:
  injected_skills:
    - skill_id:
      mode:
      authority_ceiling:
      allowed_use:
      required_output:
      forbidden_use:
      stop_conditions:
  scope:
    read_scope:
    allowed_edit_scope:
    excluded_scope:
    conditional_scope:
  forbidden_changes:
  stop_conditions:
  verification:
  execution_environment:
  return_report_contract:
```

Worker assignment는 `injected_skills`를 비워 두지 않는다. Domain-specific skill이 없으면
`keystone-default-bounded-worker` contract를 포함해 worker가 적용할 기본 절차와 report 기준을
명시한다.

Assignment의 goal, purpose, authority, scope, forbidden changes, execution environment boundary, verification,
return report contract는 모든 worker에게 적용되는 Keystone 기본 경계다. 외부 코딩 스킬(12)이
명시된 경우 해당 스킬은 `injected_skills`로 들어가지만 이 기본 경계를 대체하지 않는다.

<!-- key: id=key.standard.skill.coordinator.injected-skill-selection refs=key.role.coordinator key.topic.external-assist key.topic.skill-contract key.standard.subagent -->
### Injected skill selection contract

Coordinator는 사용자가 현재 work scope의 위임을 허락한 경우에만 execution routing을 맡는다.
작고 명확한 code/config/schema/API/test 수정은 Main direct로 처리할 수 있다.

외부 코딩 스킬(12)은 다음 규칙으로 선택한다.

1. 사용자가 `$coordinator`만 명시하면 Coordinator는 `keystone-default-bounded-worker` contract를
   사용한다.
2. 사용자가 `$superpowers`처럼 외부 코딩 스킬만 명시한 것은 Coordinator 허락으로 보지 않는다.
   위임이 필요하면 Main이 Coordinator 사용 여부를 별도로 묻는다.
3. 사용자가 `$coordinator`와 외부 코딩 스킬을 함께 명시하면 Coordinator와 해당 injected skill을
   함께 사용한다.
4. 사용자가 외부 코딩 스킬을 명시하지 않으면 Coordinator는 선택지를 매번 표시하지 않고
   `keystone-default-bounded-worker` contract를 사용한다.
5. 외부 코딩 스킬이 명시된 경우 `keystone-default-bounded-worker` contract를 중복 주입하지
   않아도 된다. 이 경우에도 assignment의 기본 경계와 return report contract는 유지된다.
6. 외부 코딩 스킬 mode는 subagent 기준서의 external coding skill mode policy를 따른다.
   Mode가 명시되지 않으면 `coding_guidance`를 사용한다.
7. 여러 외부 코딩 스킬 후보가 있고 선택에 따라 workflow, verification, risk, required output이
   달라질 때만 main/user에게 선택지를 제시한다.
8. 사용자가 Coordinator를 허락하지 않으면 Main direct로 안전하게 처리 가능한지 판단하고,
   위임 없이는 범위를 안전하게 수행할 수 없을 때만 중단해 설명한다.

외부 코딩 스킬 주입은 다음 경계를 따른다.

1. Injected skill은 worker authority를 올리지 않는다.
2. Injected skill은 Coordinator assignment의 goal, scope, forbidden changes, execution environment boundary,
   verification, return report contract를 바꾸지 않는다.
3. Injected skill이 assignment scope 밖의 절차, 추가 authority, 추가 subagent, external state,
   publishing, dependency/build system 변경을 요구하면 worker는 `NEEDS_SCOPE_CHANGE` 또는
   `NEEDS_CONTEXT`로 보고한다.
4. `NEEDS_SCOPE_CHANGE`의 `kind`는 subagent 기준서의 catalog를 우선 사용한다.
5. 외부 코딩 스킬 사용은 worker의 local workflow를 바꿀 수 있지만 Keystone acceptance
   criteria를 바꾸지 않는다.
6. Worker report는 `skill_usage`에 사용한 external coding skill, mode, outputs used,
   limits hit를 남긴다.
7. Review와 verification은 external coding skill output보다 Coordinator assignment와 Keystone
   기준서를 우선한다.

Worker report는 다음 shape을 우선 사용한다.

```yaml
worker_report:
  assignment_id:
  status: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | NEEDS_SCOPE_CHANGE | BLOCKED
  status_reason:
  reason_code:
  purpose:
  authority:
  goal:
  scope_summary:
  sources_read:
  skill_usage:
    - skill_id:
      mode:
      outputs_used:
      candidates_found:
      limits_hit:
  changed_files:
  changed_key_ids:
  changed_capabilities:
  local_decisions:
    - decision:
      reason:
      evidence:
  scope_check:
  forbidden_change_check:
  verification:
  document_sync_needed:
  metadata_sync_needed:
  source_conflicts:
  main_context_checkpoint_check:
  workspace_conflicts:
  residual_risk:
  recommended_next_action:
```

Worker report review는 다음 shape을 우선 사용한다.

```yaml
worker_report_review:
  assignment_id:
  report_status:
  actual_state_confirmed: true | false
  scope_result: within_scope | out_of_scope | unclear
  forbidden_change_result: none | found | unclear
  verification_result: pass | fail | not_run | inconclusive
  source_conflict_result:
  main_context_preserved: true | false
  reason_codes:
  review_required: true | false
  verification_required: true | false
  repair_required: true | false
  escalation_required: true | false
  coordinator_decision: accept_candidate | repair | review | verify | escalate | block
  main_acceptance_allowed: true | false
  residual_risk:
  next_action:
```

`accept_candidate`는 Main acceptance가 아니라 Main이 acceptance 판단을 할 수 있는 후보
상태다.

<!-- key: id=key.standard.skill.coordinator.purpose-routing-contract refs=key.role.coordinator key.role.subagent key.standard.subagent key.topic.work-execution key.topic.keystone-metadata key.topic.artifact-graph -->
## Purpose routing contract

Purpose preset catalog와 기본 authority는 `../../subagents/key-standard-subagents.md`를 따른다.
Coordinator는 다음 기준으로 purpose를 선택한다.

1. `investigate`
   - read-only 조사, 기존 규칙 중복 확인, 기존 구현/API/component/service/utility/test/화면
     사용처 조사, repository 조사, prototype 비교가 필요할 때 사용한다. 키메타와 코드 앵커 기반
     관련 문서와 artifact 탐색, capability provider, reuse candidate, 키메타 또는 코드 앵커 gap
     확인이 필요할 때도 사용할 수 있다.
2. `document_edit`
   - Author Edit Contract와 승인된 문서 수정 범위가 있고, 승인된 변경을 의미상 관련된 원천
     문서(2)에 필요한 만큼 반영해야 하는 경우에만 사용한다.
3. `implement`
   - edit scope가 명확하고 bounded implementation이 가능한 경우에만 사용한다. 새 기능이나
     method를 만들기 전 reuse discovery를 수행하고, 기존 capability provider 재사용/확장/신규
     생성 판단을 report해야 한다.
   - Code/config/schema/API/test anchor 변경도 bounded source edit이므로 Linker report 또는 Main이
     승인한 graph handoff seed가 있을 때만 implement assignment의 좁은 하위 case로 다룬다.
   - Worker는 새 graph relation을 자의적으로 확정하지 않는다. 새 relation 결정이 필요하면
     `NEEDS_CONTEXT` 또는 `NEEDS_SCOPE_CHANGE`로 보고한다.
   - Worker가 기존 유사 기능, duplicate implementation, 또는 module extraction 후보를 발견했고
     선택에 따라 scope, shared architecture, API/schema/test, acceptance criteria, verification이
     달라지면 직접 결정하지 않고 `NEEDS_CONTEXT` 또는 `NEEDS_SCOPE_CHANGE`로 보고한다.
     Coordinator는 필요하면 Linker report 또는 Clarify modularization decision topic으로 넘긴다.
4. `review`
   - worker output이 completion criteria, scope, risk, regression 가능성 측면에서 검토가
     필요할 때 사용한다. 아티팩트 그래프(14)가 관련되면 semantic stale, 중복 구현, 코드 앵커
     admission 적절성도 검토한다.
5. `verify`
   - 기준서-led verification을 별도 Goal로 실행하거나 failure 원인을 분리해야 할 때 사용한다.
     아티팩트 그래프(14)가 관련되면 duplicate ID, unresolved relation, stale locator 같은
     mechanical stale 검증도 수행한다.
6. Main 직접 처리
   - 작은 local 문서 수정, acceptance 판단, scope 변경 판단, high-risk decision이 필요한
     경우 사용한다.

Subagent 공통 금지와 stop condition은 subagent 기준서를 따른다.

<!-- key: id=key.standard.skill.coordinator.execution-environment refs=key.role.coordinator key.role.subagent key.standard.subagent key.topic.work-execution -->
## 실행 환경 경계

Keystone은 single workspace, worktree, branch, 병렬 worker 수나 integration 전략을 고유 규칙으로
강제하지 않는다.

1. 기본은 Main의 직접 수정이며 위임이 필요할 때만 Coordinator를 사용한다.
2. 위임된 skill이 worktree나 별도 workspace를 요구하면 그 skill과 host 환경의 계약을 따른다.
3. Worker는 assignment의 allowed edit scope 밖을 수정하지 않는다.
4. 기존 사용자 또는 다른 agent 변경을 임의로 정리, 되돌림, 덮어쓰지 않는다.
5. 실제 충돌을 발견하면 보고하고, 해결 전략이 사용자 판단을 요구할 때만 질문한다.
6. 파괴적 workspace 조작은 명시적인 사용자 허락 없이 assignment에 포함하지 않는다.
7. Worker report에는 changed files, scope check, forbidden change check와 발견한 conflict를
   포함한다.

Read-only 작업의 병렬 여부와 file-writing 작업의 isolation은 사용자 지시, 주입된 skill,
host capability와 실제 conflict risk를 바탕으로 정한다.

<!-- key: id=key.standard.skill.coordinator.report-handling-contract refs=key.role.coordinator key.topic.report key.role.subagent key.standard.subagent -->
## Report handling contract

Report status 값과 기본 의미는 `../../subagents/key-standard-subagents.md`를 따른다.
Coordinator는 받은 status를 다음 workflow 결정으로 처리한다.

1. `DONE`
   - 실제 상태와 verification을 확인한 뒤 main acceptance 후보로 올린다.
2. `DONE_WITH_CONCERNS`
   - risk나 불확실성을 기준으로 review 또는 verification을 우선 검토한다.
3. `NEEDS_CONTEXT`
   - Reader, Author, Clarify, Linker 또는 main 직접 보강 중 필요한 context 보강 경로를 정한다.
4. `NEEDS_SCOPE_CHANGE`
   - 사용자 또는 관련 기준서(3)/작업서(4) update 결정을 먼저 받아야 한다.
5. `BLOCKED`
   - unblock path를 찾거나 stop report로 main/user에게 보고한다.

Report status는 progress status가 아니다. Coordinator는 worker가 `DONE`을 보고해도 actual
state, scope boundary, verification, residual risk를 확인하기 전에는 accepted로 처리하지 않는다.
Coordinator는 subagent 기준서의 reason code catalog를 우선 사용한다. 특히 source conflict
계열은 `source_conflict`, `stale_work_order`, `stale_progress_record`,
`accepted_decision_not_propagated`를 분리해 review focus와 next action으로 연결한다.

<!-- key: id=key.standard.skill.coordinator.graph-synchronization refs=key.role.coordinator key.role.linker key.topic.artifact-graph key.topic.verification key.topic.change-set -->
## Artifact delta와 graph synchronization

1. Coordinator는 허락된 assignment에서 repository implementation 또는 anchor 의미 변경을
   발견하면 worker report로 `artifact_delta`를 수집한다. Main direct는 같은 contract를 직접
   수행할 수 있다.
2. Delta는 source surface, changed locator, semantic summary와 target source의 UTF-8 raw-byte
   SHA-256 baseline을 가진다. Graph-relevant delta가 복수 source surface patch를 요구할 때만
   Linker synchronization transaction을 시작한다. 단일 surface 변경은 direct refresh로 끝내며
   어느 경로도 current scope, Coordinator permission, worker authority 또는 acceptance를 확대하지 않는다.
3. Linker만 canonical graph mutation과 exact per-surface patch를 결정한다. Coordinator/Main과
   worker는 relation을 독자적으로 확정하거나 Linker proposal을 재해석하지 않는다.
4. Repository surface owner는 자기 implementation 의미와 exact patch를 대조해 patch별
   `confirm | reject | needs_revision`과 evidence를 반환한다. Source document patch는 Author에게
   남기며 Coordinator가 attest하거나 적용하지 않는다.
5. Coordinator는 `confirm`된 scope 안의 patch만 bounded assignment로 적용한다. Apply 직전
   baseline mismatch면 source를 쓰지 않고 `stale_baseline`을 반환한다.
6. Worker report는 patch별 `applied | failed | stale_baseline`, resulting digest와 partial apply
   evidence를 보존한다. 일부 적용된 transaction은 `partially_applied`로 resume하며 이미 적용된
   patch를 blindly 재적용하지 않는다.
7. Linker reconstruction과 mechanical validator가 모두 통과하기 전에는 Coordinator review를
   accept candidate로 만들 수 있어도 transaction `verified`나 finalization `complete`를 선언하지 않는다.
8. Validator는 diagnostic-only이며 patch 생성·적용, scope, attestation, acceptance를 소유하지 않는다.
9. Project coverage debt와 current transaction completeness를 분리해 report에 보존한다. Scope 밖
   legacy gap은 debt로 남기며 bulk metadata migration assignment를 자동 만들지 않는다.

```yaml
artifact_delta:
  source_surface:
  changed_locators: []
  semantic_summary:
  baseline_digest: sha256:<64-lowercase-hex> | absent
graph_attestations:
  - patch_id:
    decision: confirm | reject | needs_revision
    evidence:
graph_apply_results:
  - patch_id:
    result: applied | failed | stale_baseline
    resulting_digest:
```

<!-- key: id=key.standard.skill.coordinator.review-verification-flow refs=key.role.coordinator key.topic.verification key.topic.review key.topic.keystone-metadata key.topic.artifact-graph -->
## Review and verification flow

Review와 verification은 다음 순서를 따른다.

1. Worker output이 scope와 completion criteria 안에 있는지 확인한다.
2. Existing user change 또는 다른 agent change를 덮어쓸 risk가 있는지 확인한다.
3. 같은 `key.id`를 참조하는 문서와의 충돌 여부를 reviewer focus 후보로 확인한다.
4. 아티팩트 그래프(14)가 관련되면 Linker report를 기준으로 capability reuse, typed relation,
   코드 앵커 admission, semantic stale을 reviewer focus 후보로 확인한다.
5. Worker report의 `main_context_checkpoint_check`가 Current Step Brief의 intent, accepted
   decision, current work identity, preserved boundary를 훼손하지 않았는지 확인한다.
6. `source_conflicts`가 있으면 stale work order, stale progress record, accepted decision
   propagation 누락 여부를 분리해 확인한다.
7. 필요하면 별도 `review` assignment를 배정한다.
8. 기준서(3)에서 verification expectation을 추출한다.
9. 아티팩트 그래프(14)가 관련되면 graph validation expectation을 verification 후보로 추가한다.
10. 작업서(4)의 local verification note가 기준서-led verification을 약화하지 않는지 확인한다.
11. 모델 변경 결정이 있으면 old term과 new term consistency scan을 verification 후보로 추가한다.
12. 필요하면 별도 `verify` assignment를 배정한다.
13. Verification failure가 있으면 repair 또는 escalation으로 처리한다.
14. Verification을 실행할 수 없으면 residual risk로 보고하고 acceptance 여부를 main이
    판단한다.

Self-review는 worker report의 일부일 수 있지만 independent review로 보지 않는다. Independent
review가 필요하면 별도 `review` assignment를 만든다.

<!-- key: id=key.standard.skill.coordinator.acceptance-contract refs=key.role.coordinator key.topic.acceptance key.topic.verification -->
## Acceptance contract

Main acceptance는 다음 조건이 충족될 때만 가능하다.

1. Worker 또는 main output을 실제로 확인했다.
2. Completion criteria가 충족되었다.
3. Scope boundary와 forbidden change를 위반하지 않았다.
4. Reviewer review가 완료되었거나 명시적으로 skip되었다.
5. Verification을 실행했거나 실행하지 못한 이유와 residual risk가 보고되었다.
6. Unresolved `NEEDS_SCOPE_CHANGE`가 없다.
7. 진행 상태와 report status를 혼동하지 않았다.
8. 필요한 원천 문서(2) update가 있다면 승인된 범위 안에서 처리되었거나 별도 next action으로
   남겼다.
9. 아티팩트 그래프(14)가 관련된 경우 reuse decision, 키메타 또는 코드 앵커 gap, graph
   validation residual risk를 확인했다.
10. Source conflict가 있으면 resolved, excluded, or next action으로 분리되어 있다.

Completion evidence가 있을 때 `work_status: complete`로 전이하고, Main acceptance 후에만
`approval.state: accepted`로 전이한다. 두 상태는 서로 대체하지 않는다.

<!-- key: id=key.standard.skill.coordinator.progress-update-boundary refs=key.role.coordinator key.topic.progress-update key.topic.acceptance -->
## Progress update boundary

진행 기록(5)은 worker workflow 상태를 복구하기 위해 다음 규칙으로 갱신한다.

1. Assignment를 만들면 optional `workflow_substate: assigned`를 기록할 수 있다.
2. Report를 받으면 optional `workflow_substate: reported`를 기록할 수 있다.
3. Review 중이면 `workflow_substate: reviewing`, verification 중이면
   `workflow_substate: verifying`를 기록할 수 있다. 이 값들은 `work_status`가 아니다.
4. Completion criteria와 verification evidence가 충족되면 `work_status: complete`로 전이한다.
5. Main acceptance 전에는 `approval.state: accepted`로 표시하지 않는다.
6. Worker `DONE`만으로 `work_status: complete` 또는 `approval.state: accepted`로 전이하지 않는다.
7. 문서 작성/수정의 기준과 반영 범위는 `keystone-author`가 담당한다. Formal workflow 상태를
   복구해야 하는 경우에만 Coordinator가 진행 상태 전이를 조율한다.
8. 단순 오탈자, 미세 표현 수정, 의미 변화 없는 formatting은 진행 기록(5)에 남기지 않는다.
9. Status semantics를 바꾸려면 Author 또는 Clarify를 통해 원천 문서(2) update 결정을 먼저
   받는다.

<!-- key: id=key.standard.skill.coordinator.derived-document-policy refs=key.role.coordinator key.doc.source key.topic.document-system -->
## Derived document policy

파생 에이전트 문서(8)는 기본 생성하지 않는다. 이미 존재하고 명확히 영향받는 경우에만
함께 업데이트한다. 새로 생성하는 경우는 다음처럼 명시적 필요가 있을 때로 제한한다.

1. 사용자가 명시적으로 persistent handoff나 reviewer brief를 요청한다.
2. 복잡한 handoff를 사람에게 먼저 검토받아야 한다.
3. 같은 step을 rerun해야 한다.
4. Audit record가 필요하다.

파생 에이전트 문서(8)가 원천 문서(2)와 충돌하면 원천 문서(2)가 우선한다.

<!-- key: id=key.standard.skill.coordinator.stop-condition refs=key.role.coordinator key.topic.skill-contract key.topic.work-execution -->
## Stop condition

Coordinator는 다음 상황에서 중단하거나 main/user 결정(6)을 요청한다.

1. Active/실행 가능 Step, completion criteria, applicable standard를 복구할 수 없다.
2. Work unit이 bounded worker assignment로 자를 수 없다.
3. Scope boundary, direct edit scope, forbidden change가 불명확하다.
4. High-risk implementation이 main/user decision 없이 필요하다.
5. Report가 승인된 scope나 acceptance criteria 변경을 요구한다.
6. Existing user change 또는 다른 agent change를 덮어쓸 risk가 있다.
7. Verification을 실행할 수 없고 failure 원인도 판단할 수 없다.
8. Progress state가 현재 session context와 충돌한다.
9. 민감한 정보, local-only path, private data를 worker context에 넣어야 할 수 있다.
10. 문서 작업인데 Author Edit Contract 없이 무엇을 어떻게 쓸지 결정해야 한다.
11. Worker가 전체 작업서(4)를 재해석하거나 추가 subagent를 생성해야만 진행할 수 있다.
12. 위임에 필요한 사용자 허락이나 host 실행 경계를 확인할 수 없다.
13. 여러 file-writing worker의 변경 충돌을 현재 실행 전략으로 안전하게 관리할 수 없다.
14. Default, domain-specific, explicit external coding skill 중 어떤 injected skill contract도
    assignment에 포함할 수 없다.
15. Accepted decision이 관련 work order나 progress record에 전파되지 않아 current task 방향을
    바꿀 수 있다.
16. 새 reusable code/config/schema/API/test artifact를 만들려 하지만 Linker report 또는 reuse
    discovery 결과가 없다.
17. 아티팩트 그래프(14) mismatch가 current task 방향을 바꿀 수 있지만 Change Set(17) 또는
    Linker report가 없다.
18. 유사 capability, duplicate implementation, 또는 module extraction 후보가 발견되었고 선택에
    따라 scope, shared architecture, API/schema/test, acceptance criteria, verification이 달라지지만
    Clarify decision이나 Main/user 결정(6)이 없다.
19. 외부 코딩 스킬 후보가 여러 개이고 선택에 따라 workflow, verification, risk가 달라지지만
    main/user 선택이 없다.
20. 명시된 외부 코딩 스킬의 필수 절차가 Coordinator assignment의 scope, authority,
    execution environment boundary, verification과 충돌한다.
21. 복수 surface나 권한 경계가 불명확해 assignment scope를 안전하게 만들 수 없다.

<!-- key: id=key.standard.skill.coordinator.verification refs=key.role.coordinator key.topic.verification key.topic.acceptance key.standard.subagent -->
<!-- key: id=key.standard.skill.coordinator.dependency-sequencing refs=key.role.coordinator key.topic.work-sequence key.topic.work-execution -->
## Dependency sequencing

1. Coordinator는 각 active/실행 가능 Step gate를 assignment 순서 제안에 사용하고 work completion gate를
   acceptance readiness에서 별도로 확인한다.
2. Required gate가 `waiting`이면 해당 step implement assignment를 만들지 않지만
   `investigate`/`verify`와 optional gate 작업은 scope에 따라 제안할 수 있다.
3. `unresolvable`, `invalid`, `unknown`은 자동 status mutation·assignment·cancellation이 아니라
   Main/user decision, Author repair 또는 Linker evidence의 next action으로 연결한다.
4. Coordinator는 dependency 판정만으로 progress를 `blocked`로 바꾸거나 work를 수용하지 않는다.

## Verification

Coordinator 기준은 다음 방법으로 검증한다.

1. Coordinator contract만 보고 trigger와 non-trigger를 구분할 수 있어야 한다.
2. 작업서(4) step에서 Current Step Brief, Context Pack, worker assignment를 만들 수 있어야 한다.
3. Scope를 worker handoff boundary로 변환할 수 있어야 한다.
4. Review points를 reviewer focus로 변환할 수 있어야 한다.
5. High-risk work가 자동 worker-routable로 취급되지 않아야 한다.
6. Progress update가 main acceptance와 worker report status를 혼동하지 않아야 한다.
7. 문서 formal workflow는 Author Edit Contract 없이 시작되지 않아야 한다.
8. 파생 에이전트 문서(8)는 기본 생성되지 않아야 한다.
9. Linker report를 Context Pack 후보와 reviewer focus 후보로 사용할 수 있어야 한다.
10. 아티팩트 그래프(14) 후보를 Change Set(17), worker assignment, reviewer focus,
    verification 후보로 변환할 수 있어야 한다.
11. Purpose catalog와 report status 정의를 반복하지 않고 subagent 기준서를 참조해야 한다.
12. Keystone이 특정 workspace/worktree/concurrency 전략을 강제하지 않으면서 기존 변경 보존과
    assignment scope를 검증할 수 있어야 한다.
13. Worker assignment와 worker report contract를 구분할 수 있어야 한다.
14. Worker `DONE`과 Keystone acceptance를 구분할 수 있어야 한다.
15. Default worker contract가 assignment에 포함되어야 하는 상황을 판단할 수 있어야 한다.
16. Main context checkpoint로 global intent, accepted decision, current work identity,
    preserved boundary가 보존되는지 확인할 수 있어야 한다.
17. Source conflict, stale work order, stale progress record, accepted decision propagation
    누락을 reason code와 review focus로 분리할 수 있어야 한다.
18. 작은 명확한 code/config/schema/API/test 수정은 Main direct가 가능하고, Coordinator는 사용자
    허락과 위임 필요가 있을 때만 사용되어야 한다.
19. 외부 코딩 스킬이 명시되면 Coordinator를 대체하지 않고 injected skill로 들어가야 한다.
20. 외부 코딩 스킬이 명시되지 않으면 `keystone-default-bounded-worker` contract가 사용되어야
    한다.
21. 여러 외부 코딩 스킬 후보가 있을 때 매번 묻지 않고 선택이 의미 있게 다른 경우에만
    main/user 선택을 요청해야 한다.
22. 기본 사용자 응답은 worker assignment/report payload를 그대로 노출하지 않고 workflow 판단,
    scope, verification, risk, next action을 요약해야 한다.
23. Delegated `skill_source` 변경은 Coordinator lane으로 worker assignment/report를 남겨야 한다.
24. Verification command:
   - `rg --files 00_docs`
   - Coordinator 관련 기준서를 읽어 link와 scope consistency 확인
   - `rg -n "branch|worktree|merge gate|remote push|commit checkpoint|repo-integrator|task branch|session branch" 00_docs/standards 00_docs/works | rg -v 'rg -n "branch\\|worktree'`
   - `rg -n "bounded worker|worker assignment|purpose preset|injected skill contract|execution environment" 00_docs/standards 00_docs/works`
   - `rg -n "external coding skill|외부 코딩 스킬|keystone-default-bounded-worker|injected skill" 00_docs/standards`
25. 프로젝트 로컬 Coordinator 기준서가 없어도 설치된 contract로 사용자 허락과 assignment
    경계를 판단할 수 있어야 한다.

<!-- key: id=key.standard.skill.coordinator.permissionless-linker-boundary refs=key.role.coordinator key.role.linker key.standard.subagent key.boundary.scope-control -->
## Permissionless Linker와 Coordinator 허락 경계

1. Coordinator의 explicit user permission은 file-changing worker delegation과 scope-bearing
   orchestration에 적용한다. Source-write authority가 없는 Linker의 internal scan/index/graph
   interpretation/validation은 이 permission을 요구하지 않는다.
2. Permissionless Linker는 Coordinator worker가 아니며 source patch, scope expansion, worker 생성,
   의미 결정과 acceptance를 수행할 수 없다. 이 예외가 Coordinator 권한을 확대하지 않는다.
3. Coordinator는 assignment 전에 fresh Reader context token을 재사용하고 필요한 artifact context가
   없을 때 permissionless Linker의 lazy repository scope 결과를 Context Pack에 포함할 수 있다.
4. File-changing worker report 뒤 affected discovery scope를 invalidation한다. 후속 review와
   verification은 stale pre-write index가 아니라 refreshed owner/ref/graph context를 사용한다.
5. 단일 repository surface 안의 승인된 작은 anchor refresh는 해당 surface owner의 direct lane으로
   처리할 수 있다. Document와 repository 등 복수 surface 정합화가 필요할 때만 graph transaction을
   요구한다.
6. Transaction retry는 conflict reason별 변경 조건과 새 transaction ID/attempt history를 검증한다.
   Repository coverage debt는 current transaction omission과 분리해 assignment scope를 자동 넓히지 않는다.
