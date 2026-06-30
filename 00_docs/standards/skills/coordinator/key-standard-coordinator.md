---
doc_type: standard
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
authority, scope, workspace guard, stop condition, report contract를 정하는 것이다.

<!-- key: id=key.standard.skill.coordinator.scope refs=key.role.coordinator key.role.subagent key.standard.subagent key.topic.verification key.topic.acceptance key.topic.formal-workflow key.topic.artifact-graph -->
## 적용 범위

1. `keystone-coordinator`의 trigger와 non-trigger condition
2. Current Step Brief, Context Pack, worker assignment 구성
3. Purpose preset, authority, injected skill contract routing
4. Worker handoff boundary와 reviewer focus 도출
5. Worker report handling
6. Review, verification, repair, escalation, acceptance flow
7. Change Set(17), Linker report, reuse discovery, graph validation 조율
8. Single workspace guard
9. 진행 상태와 report status update boundary
10. 외부 코딩 스킬(12)의 injected skill 선택과 주입
11. 파생 에이전트 문서(8) 생성 조건

<!-- key: id=key.standard.skill.coordinator.out-of-scope refs=key.role.coordinator key.topic.skill-contract key.topic.external-assist -->
## 적용하지 않는 범위

1. 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 기록의 작성 기준과 수정 범위 설계 자체
2. High-impact topic 질문 수집과 결정(6) 확정
3. Read-only project orientation 또는 document navigation만 수행하는 작업
4. Worker가 전체 작업서(4)를 재해석하거나 scope를 확장하게 하기
5. Main acceptance 없이 진행 상태를 complete 또는 accepted로 표시하기
6. 명시적 필요 없이 persistent worker handoff나 reviewer brief 생성
7. Implementation, schema, auth/security, generated/codegen, shared architecture 변경을
   main/user decision 없이 자동 worker task로 보내기
8. 외부 보조 스킬(12)을 Coordinator를 대체하는 automatic 또는 mandatory execution layer로 만들기
9. Artifact relation, impact candidate, stale candidate를 Linker 없이 확정하기
10. Worker가 추가 subagent를 만들게 하기

<!-- key: id=key.standard.skill.coordinator.standard-relations refs=key.role.coordinator key.doc.standard key.topic.skill-contract key.standard.subagent key.topic.work-round key.topic.artifact-graph -->
## 기준 관계

1. Parent 기준서: `../../01_key-project-standard.md`
2. 상위 규칙: `STD-KEYSTONE-001`, `STD-KEYSTONE-006`, `STD-KEYSTONE-007`,
   `STD-KEYSTONE-015`, `STD-KEYSTONE-016`, `STD-KEYSTONE-017`,
   `STD-KEYSTONE-018`, `STD-KEYSTONE-020`, `STD-KEYSTONE-022`,
   `STD-KEYSTONE-023`, `STD-KEYSTONE-024`, `STD-KEYSTONE-025`,
   `STD-KEYSTONE-026`, `STD-KEYSTONE-027`, `STD-KEYSTONE-030`, `STD-KEYSTONE-031`,
   `STD-KEYSTONE-032`, `STD-KEYSTONE-033`, `STD-KEYSTONE-043`
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

<!-- key: id=key.standard.skill.coordinator.trigger-condition refs=key.role.coordinator key.topic.work-execution key.role.subagent key.standard.subagent key.topic.author-edit-contract -->
## Trigger condition

`keystone-coordinator`는 다음 경우에 사용할 수 있다.

1. 작업서(4)의 current step을 Goal unit으로 실행해야 한다.
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
9. Linker report를 바탕으로 문서, code, API, capability, test artifact 변경 후보를 Change
   Set(17) 단위로 조율해야 한다.
10. Keystone 작업 문맥에서 code/config/test 수정 요청이 들어왔고, bounded implementation
    assignment를 구성해야 한다.
11. 사용자가 `superpowers` 같은 외부 코딩 스킬(12)을 명시해 해당 workflow를 worker
    assignment에 주입해야 한다.

<!-- key: id=key.standard.skill.coordinator.non-trigger-condition refs=key.role.coordinator key.topic.skill-contract -->
## Non-trigger condition

`keystone-coordinator`는 다음 경우에 사용하지 않는다.

1. 원천 문서(2)의 작성 기준, 수정 범위, 영향 문서 판단이 주된 작업이다.
2. 사용자가 high-impact policy, scope, 문서 구조, 스킬 계약을 먼저 결정해야 한다.
3. 현재 요청과 관련된 기준서(3)와 작업서(4)를 read-only로 찾기만 하면 된다.
4. Current step, completion criteria, applicable standard를 복구할 수 없다.
5. Work unit이 bounded worker assignment로 나뉘지 않았다.
6. 작업이 high-risk implementation인데 main/user decision 없이 worker에게 보낼 수 없다.
7. 민감한 정보, local-only path, private data가 포함될 수 있지만 policy가 불명확하다.
8. 문서 작업인데 Author Edit Contract 또는 승인된 문서 수정 범위가 없다.

<!-- key: id=key.standard.skill.coordinator.required-input refs=key.role.coordinator key.topic.work-execution key.topic.artifact-graph -->
## Required input

Coordinator는 다음 input을 사용할 수 있어야 한다.

1. 사용자 요청 또는 main의 current task
2. 설정된 document root(1)
3. 관련 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 기록
4. Current step 또는 이를 복구하기 위한 active round와 active work state
5. Completion criteria와 verification expectation
6. Included, excluded, conditional work scope
7. Stop conditions와 escalation conditions
8. 현재 workspace state와 existing-change risk
9. 문서 formal workflow인 경우 Author Edit Contract
10. 아티팩트 그래프(14)가 관련된 경우 Linker report, impact seeds, artifact candidates, 또는
    Change Set(17)
11. Worker에게 주입할 skill contract 후보
12. 사용자가 명시한 외부 코딩 스킬(12), 또는 선택이 필요한 available coding skill 후보
13. File-writing worker가 필요한 경우 single workspace guard

Input이 부족하면 Coordinator는 worker를 배정하지 않고 Reader, Author, Clarify, Linker 중
필요한 다음 작업을 제안하거나 main/user 결정(6)을 요청한다.

<!-- key: id=key.standard.skill.coordinator.common-workflow refs=key.role.coordinator key.topic.work-execution key.topic.artifact-graph key.topic.verification key.topic.acceptance key.standard.subagent -->
## Common workflow

Coordinator는 다음 순서를 따른다.

1. 설정된 document root(1)와 root works index를 확인한다.
2. Active round index와 active work node index를 따라 `round_id`, `work_id`, `current_step`과
   workflow state를 복구한다.
3. 작업서(4)에서 Goal, Scope, Source Context, Completion Criteria, Stop Conditions,
   Verification, Expected Output을 추출한다.
4. 관련 기준서(3)에서 verification expectation과 forbidden change를 추출한다.
5. Reader context brief와 Author Change Set(17)을 확인한다.
6. 아티팩트 그래프(14) 후보가 있으면 Linker report를 요구하거나 기존 Linker report에서 impact
   seed, required/optional/excluded candidates를 확인한다.
7. Work unit이 bounded worker assignment로 자를 수 있는지 판단한다.
8. Subagent 기준서에 따라 purpose preset, authority, injected skill contract를 선택한다.
9. Code/config/test 수정 요청에서 외부 코딩 스킬(12)이 명시되었으면 Coordinator를 유지한 채
   해당 스킬을 injected skill로 주입한다.
10. Domain-specific 또는 명시된 external coding skill이 없으면 `keystone-default-bounded-worker`
    contract를 선택한다.
11. 여러 coding skill 후보가 있고 선택에 따라 workflow, verification, risk가 달라질 때만
    main/user 선택을 요청한다.
12. File-writing worker가 필요하면 single workspace guard를 설정한다.
13. Current Step Brief, Context Pack, worker assignment를 만든다.
14. Worker handoff boundary 또는 reviewer focus를 구성한다.
15. Worker report(20)를 받은 뒤 actual state와 output을 확인한다.
16. 필요하면 별도 review 또는 verify assignment를 배정한다.
17. Report 결과를 accept candidate, repair, verify, escalate, block 중 하나로 처리한다.
18. Main acceptance 조건이 충족된 경우에만 진행 기록(5)을 갱신한다.

<!-- key: id=key.standard.skill.coordinator.runtime-output-contract refs=key.role.coordinator key.contract.output key.topic.work-execution key.topic.work-round key.topic.artifact-graph key.standard.subagent -->
## Runtime output contract

Coordinator는 상황에 따라 다음 runtime output을 만들 수 있다.

1. Current Step Brief
   - `round_id`, `work_id`, `step_id`, current step, Goal, completion criteria, applicable
     standards, excluded work, expected edit area, verification, known risks,
     `main_context_checkpoint`를 담는다.
2. Context Pack
   - worker나 reviewer가 읽어야 하는 관련 기준서(3), 작업서(4), 결정(6), scope,
     progress 발견사항, 키메타와 코드 앵커 기반 관련 문서와 artifact 후보를 담는다.
3. Change Set brief
   - intent, changed nodes, impact seeds, required candidates, optional candidates, excluded
     scope, verification, acceptance state를 담는다.
4. Worker assignment
   - assignment id, goal, intent summary, purpose, role hint, authority, source documents,
     accepted decisions, applicable standards, context pack, injected skill contract,
     scope, forbidden changes, stop conditions, verification, workspace guard,
     main context checkpoint, return report contract를 담는다.
5. Worker report review
   - status, changed files, changed artifact IDs, verification result, scope check,
     document sync need, metadata sync need, stale candidates, source conflicts,
     main context preservation, residual risk를 확인한다.
6. Worker handoff
   - subagent 기준서 기준의 purpose, role hint, authority, primary scope, read scope,
     direct edit scope, conditional edit scope, escalation zone, forbidden changes,
     workspace guard를 담는다.
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
  source_conflicts:
    - document:
      conflict:
      resolved_by:
  preserved_boundaries:
    - main_acceptance_only
    - no_scope_expansion
    - no_child_subagents
    - single_workspace_one_writer
```

이 runtime output은 기본적으로 persistent 문서가 아니다. 명시적 필요가 있을 때만 파생
에이전트 문서(8)로 저장할 수 있다.

<!-- key: id=key.standard.skill.coordinator.worker-assignment-contract refs=key.role.coordinator key.contract.output key.contract.report -->
## Worker assignment and report contract

Worker assignment는 다음 shape을 우선 사용한다.

```yaml
worker_assignment:
  assignment_id:
  goal:
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
  workspace_guard:
  return_report_contract:
```

Worker assignment는 `injected_skills`를 비워 두지 않는다. Domain-specific skill이 없으면
`keystone-default-bounded-worker` contract를 포함해 worker가 적용할 기본 절차와 report 기준을
명시한다.

<!-- key: id=key.standard.skill.coordinator.injected-skill-selection refs=key.role.coordinator key.topic.external-assist key.topic.skill-contract key.standard.subagent -->
### Injected skill selection contract

Coordinator는 Keystone 작업 문맥과 code/config/test 수정 요청을 분리하지 않는다. Keystone
작업 문맥이 복구되고 bounded implementation이 가능한 경우, 명시적 `$coordinator` 호출이 없어도
Coordinator를 기본 execution routing으로 사용한다.

외부 코딩 스킬(12)은 다음 규칙으로 선택한다.

1. 사용자가 `$coordinator`만 명시하면 Coordinator는 `keystone-default-bounded-worker` contract를
   사용한다.
2. 사용자가 `$superpowers`처럼 외부 코딩 스킬만 명시하고 Keystone 작업 문맥에서
   code/config/test 수정 요청을 하면 Coordinator를 기본으로 사용하고, 해당 스킬을
   `injected_skills`에 추가한다.
3. 사용자가 `$coordinator`와 외부 코딩 스킬을 함께 명시하면 Coordinator와 해당 injected skill을
   함께 사용한다.
4. 사용자가 외부 코딩 스킬을 명시하지 않으면 Coordinator는 선택지를 매번 표시하지 않고
   `keystone-default-bounded-worker` contract를 사용한다.
5. 여러 외부 코딩 스킬 후보가 있고 선택에 따라 workflow, verification, risk, required output이
   달라질 때만 main/user에게 선택지를 제시한다.
6. 사용자가 Coordinator를 사용하지 말라고 명시하면 Keystone source authority, scope,
   verification, acceptance risk를 검토하고 안전하지 않으면 중단하거나 사용자 결정을 요청한다.

외부 코딩 스킬 주입은 다음 경계를 따른다.

1. Injected skill은 worker authority를 올리지 않는다.
2. Injected skill은 Coordinator assignment의 goal, scope, forbidden changes, workspace guard,
   verification, return report contract를 바꾸지 않는다.
3. Injected skill이 assignment scope 밖의 절차, 추가 authority, 추가 subagent, external state,
   publishing, dependency/build system 변경을 요구하면 worker는 `NEEDS_SCOPE_CHANGE` 또는
   `NEEDS_CONTEXT`로 보고한다.
4. Worker report는 `skill_usage`에 사용한 external coding skill, mode, outputs used,
   limits hit를 남긴다.
5. Review와 verification은 external coding skill output보다 Coordinator assignment와 Keystone
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

<!-- key: id=key.standard.skill.coordinator.workspace-guard-policy refs=key.role.coordinator key.role.subagent key.standard.subagent key.topic.work-execution -->
## Single workspace policy

기본 실행 모델은 single workspace bounded worker orchestration이다.

1. Coordinator는 한 번에 하나의 file-writing worker만 배정한다.
2. 이전 file-writing worker report를 처리하기 전에는 다음 file-writing worker를 배정하지 않는다.
3. Worker는 allowed edit scope 밖의 파일을 수정하지 않는다.
4. 기존 사용자 변경이나 다른 agent 변경을 정리, 되돌림, 덮어쓸 가능성이 있으면 멈추고
   보고하게 한다.
5. 파괴적 workspace 조작은 사용자 또는 Main의 명시 승인 없이는 worker assignment에 포함하지
   않는다.
6. Worker report에는 changed files, scope check, forbidden change check, workspace conflicts가
   포함되어야 한다.

Workspace guard는 다음 shape을 우선 사용한다.

```yaml
workspace_guard:
  model: single_workspace
  active_file_writer_policy: exclusive
  allowed_paths:
  protected_paths:
  existing_changes_policy: do_not_overwrite_unlisted_changes
  destructive_workspace_operation_policy: forbidden
  file_change_report_required: true
```

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

Acceptance 후에만 진행 기록(5)을 `accepted` 또는 해당 project의 완료 상태로 바꿀 수 있다.

<!-- key: id=key.standard.skill.coordinator.progress-update-boundary refs=key.role.coordinator key.topic.progress-update key.topic.acceptance -->
## Progress update boundary

진행 기록(5)은 worker workflow 상태를 복구하기 위해 다음 규칙으로 갱신한다.

1. Assignment를 만들면 필요한 경우 `assigned`를 기록할 수 있다.
2. Report를 받으면 필요한 경우 `reported`를 기록할 수 있다.
3. Review 중이면 `reviewing`, verification 중이면 `verifying`을 기록할 수 있다.
4. Main acceptance 전에는 `accepted`로 표시하지 않는다.
5. Worker `DONE`만으로 progress를 완료 처리하지 않는다.
6. 문서 작성/수정의 기준과 반영 범위는 `keystone-author`가 담당한다. Formal workflow 상태를
   복구해야 하는 경우에만 Coordinator가 진행 상태 전이를 조율한다.
7. 단순 오탈자, 미세 표현 수정, 의미 변화 없는 formatting은 진행 기록(5)에 남기지 않는다.
8. Status semantics를 바꾸려면 Author 또는 Clarify를 통해 원천 문서(2) update 결정을 먼저
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

1. Current step, completion criteria, applicable standard를 복구할 수 없다.
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
12. File-writing worker가 필요한데 single workspace guard가 없다.
13. 여러 file-writing worker를 동시에 배정해야만 진행할 수 있다.
14. Default worker contract 또는 domain-specific injected skill contract가 없다.
15. Accepted decision이 관련 work order나 progress record에 전파되지 않아 current task 방향을
    바꿀 수 있다.
16. 새 reusable code/API/test artifact를 만들려 하지만 Linker report 또는 reuse discovery 결과가
    없다.
17. 아티팩트 그래프(14) mismatch가 current task 방향을 바꿀 수 있지만 Change Set(17) 또는
    Linker report가 없다.
18. 외부 코딩 스킬 후보가 여러 개이고 선택에 따라 workflow, verification, risk가 달라지지만
    main/user 선택이 없다.
19. 명시된 외부 코딩 스킬의 필수 절차가 Coordinator assignment의 scope, authority,
    workspace guard, verification과 충돌한다.

<!-- key: id=key.standard.skill.coordinator.verification refs=key.role.coordinator key.topic.verification key.topic.acceptance key.standard.subagent -->
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
12. Single workspace guard만 보고 file-writing worker의 배정 가능 여부를 판단할 수 있어야 한다.
13. Worker assignment와 worker report contract를 구분할 수 있어야 한다.
14. Worker `DONE`과 Keystone acceptance를 구분할 수 있어야 한다.
15. Default worker contract가 assignment에 포함되어야 하는 상황을 판단할 수 있어야 한다.
16. Main context checkpoint로 global intent, accepted decision, current work identity,
    preserved boundary가 보존되는지 확인할 수 있어야 한다.
17. Source conflict, stale work order, stale progress record, accepted decision propagation
    누락을 reason code와 review focus로 분리할 수 있어야 한다.
18. Keystone 작업 문맥에서 code/config/test 수정 요청이 들어오면 Coordinator가 기본 routing임을
    확인할 수 있어야 한다.
19. 외부 코딩 스킬이 명시되면 Coordinator를 대체하지 않고 injected skill로 들어가야 한다.
20. 외부 코딩 스킬이 명시되지 않으면 `keystone-default-bounded-worker` contract가 사용되어야
    한다.
21. 여러 외부 코딩 스킬 후보가 있을 때 매번 묻지 않고 선택이 의미 있게 다른 경우에만
    main/user 선택을 요청해야 한다.
22. Verification command:
   - `rg --files 00_docs`
   - Coordinator 관련 기준서를 읽어 link와 scope consistency 확인
   - `rg -n "branch|worktree|merge gate|remote push|commit checkpoint|repo-integrator|task branch|session branch" 00_docs/standards 00_docs/works`
   - `rg -n "single workspace|bounded worker|worker assignment|purpose preset|injected skill contract|workspace guard" 00_docs/standards 00_docs/works`
   - `rg -n "external coding skill|외부 코딩 스킬|keystone-default-bounded-worker|injected skill" 00_docs/standards`
