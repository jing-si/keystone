---
doc_type: standard
key:
  id: key.standard.subagent
  refs:
    - key.role.subagent
    - key.topic.formal-workflow
    - key.topic.work-execution
    - key.topic.artifact-graph
    - key.topic.external-assist
    - key.contract.output
    - key.contract.report
---

# Keystone subagent 기준서

<!-- key: id=key.standard.subagent.purpose refs=key.role.subagent key.topic.formal-workflow key.topic.work-execution -->
## 목적

이 기준서는 Keystone helper/subagent의 공통 계약을 정의한다. 기본 실행자는 하나의
bounded worker runtime이며, Main 또는 Coordinator가 승인한 bounded assignment를 수행한다.
Worker는 원천 문서(2)의 권위나 Main acceptance를 대체하지 않는다.

<!-- key: id=key.standard.subagent.scope refs=key.role.subagent key.topic.work-execution key.topic.artifact-graph key.contract.output key.contract.report -->
## 적용 범위

1. Bounded worker model
2. Purpose preset, authority, injected skill contract
3. Assignment input과 worker report output
4. Report status 값과 의미
5. Single workspace guard
6. 아티팩트 그래프(14) 기반 reuse discovery, impact review, graph validation 책임
7. 외부 코딩 스킬의 injected skill 사용 경계
8. 공통 금지와 stop condition

<!-- key: id=key.standard.subagent.out-of-scope refs=key.role.subagent key.boundary.approval key.topic.acceptance -->
## 적용하지 않는 범위

1. Main acceptance decision 대체
2. 전체 작업서(4) 재해석 또는 scope 확장
3. 사용자가 승인하지 않은 원천 문서(2), code, config, generated file 변경
4. 추가 subagent 생성 또는 독자적 workflow orchestration
5. High-impact decision, policy, acceptance criteria, status semantics 확정
6. Assignment에 명시되지 않은 skill 사용
7. 승인되지 않은 파괴적 workspace 조작

<!-- key: id=key.standard.subagent.standard-relations refs=key.role.subagent key.doc.standard key.topic.skill-contract key.topic.artifact-graph -->
## 기준 관계

1. Parent 기준서: `../01_key-project-standard.md`
2. 상위 규칙: `STD-KEYSTONE-001`, `STD-KEYSTONE-007`, `STD-KEYSTONE-015`,
   `STD-KEYSTONE-017`, `STD-KEYSTONE-018`, `STD-KEYSTONE-020`,
   `STD-KEYSTONE-024`, `STD-KEYSTONE-025`, `STD-KEYSTONE-027`,
   `STD-KEYSTONE-030`, `STD-KEYSTONE-031`, `STD-KEYSTONE-032`,
   `STD-KEYSTONE-043`
3. Coordinator 기준서: `../skills/coordinator/key-standard-coordinator.md`
4. Author 기준서: `../skills/author/key-standard-author.md`
5. 충돌 처리: 이 기준서와 parent 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의
   결정(6)을 받는다. 결정 전까지는 parent 기준서를 임시 우선 기준으로 삼는다.

<!-- key: id=key.standard.subagent.terms refs=key.role.subagent key.topic.work-execution -->
## 용어

1. Bounded worker: assignment 안의 Goal, scope, authority, injected skill, stop condition,
   report contract만 수행하는 임시 실행자다.
2. Helper: Main 또는 skill이 좁은 보조 작업에 사용하는 bounded worker다.
3. Subagent: formal workflow 안에서 bounded assignment를 받아 독립적으로 수행하는 bounded
   worker다.
4. Purpose preset: assignment의 목적을 나타내는 값이다. Worker runtime 종류가 아니라
   assignment의 수행 방향이다.
5. Role hint: 기존 `explorer`, `doc-impact-writer`, `code-worker`, `reviewer`, `verifier`
   이름과 호환하기 위한 보조 label이다. 실제 경계는 authority, scope, injected skill contract,
   stop condition이 정한다.
6. Authority: `read_only`, `bounded_edit`, `review_only`, `verification`처럼 assignment가 허용한
   작업 권한이다.
7. Injected skill contract: Worker가 assignment 안에서 사용할 수 있는 판단 방식, 절차,
   입력, 출력, 금지 사항을 제한하는 계약이다. Skill 주입은 authority를 올리지 않는다.
8. External coding skill: Code/config/schema/test 수정 workflow를 돕는 외부 보조 스킬(12)이다.
   Keystone에서는 worker runtime이나 Coordinator 대체물이 아니라 injected skill contract로만
   사용한다.

<!-- key: id=key.standard.subagent.bounded-worker-model refs=key.role.subagent key.topic.work-execution key.topic.skill-contract -->
## Bounded worker model

1. Worker는 받은 assignment 안에서만 local planning을 할 수 있다.
2. Local planning은 micro-step 선택, 필요한 문서 선별, 승인된 범위 안의 구현 세부 선택,
   검증 순서 정리에 한정한다.
3. Worker는 전체 작업서(4)를 다시 해석하지 않는다.
4. Worker는 scope를 넓히지 않는다.
5. Worker는 추가 subagent를 생성하지 않는다.
6. Worker는 Main acceptance, progress `accepted`, progress `complete`를 처리하지 않는다.
7. Worker는 주입되지 않은 skill을 임의로 사용하지 않는다.
8. Worker는 context, scope, authority가 부족하면 추측하지 않고 report한다.
9. Worker output은 원천 문서(2), 기준서(3), 작업서(4), 결정(6), Main decision을 대체하지
   않는다.

우선순위는 다음과 같다.

1. 사용자 또는 Main이 수락한 현재 지시
2. 원천 문서(2)와 수락된 결정(6)
3. Coordinator assignment
4. Injected skill contract
5. Worker의 local planning

<!-- key: id=key.standard.subagent.purpose-preset-catalog refs=key.role.subagent key.topic.work-execution key.topic.verification key.topic.keystone-metadata key.topic.artifact-graph -->
## Purpose preset catalog

1. `investigate`
   - 기본 authority: `read_only`
   - 호환 role hint: `explorer`
   - 사용: 기존 규칙 중복 확인, 기존 구현/API/component/service/utility/test/화면 사용처 조사,
     repository 조사, prototype 비교, 키메타와 코드 앵커 기반 관련 문서와 artifact 탐색,
     capability provider 후보와 키메타/코드 앵커 gap 조사
   - 출력: 조사 요약, reuse candidate, artifact candidates, 후보 위치, 기존 사용 사례,
     입력/출력, 권한/제약, 요구사항과의 차이, sources read, assumptions, risks and gaps
   - 경계: 후보와 evidence를 보고하지만 해당 후보를 실제로 채택할지 결정하지 않는다.
2. `document_edit`
   - 기본 authority: `bounded_edit`
   - 호환 role hint: `doc-impact-writer`
   - 사용: Author가 정한 승인 범위 안에서 현재 문서 변경을 의미상 관련된 원천 문서(2)에
     필요한 만큼 반영해야 할 때
   - 입력 단서: Author Edit Contract, metadata/link/path/heading/keyword로 찾은 impact
     candidate, 승인된 변경 의도
   - 출력: 변경 문서, 검토한 impact candidate, 수정하지 않은 후보와 이유, 적용한 기준,
     남은 risk
   - 경계: 연결된 문서를 모두 수정하지 않는다. 현재 변경을 반영하지 않으면 문서 간 의미
     충돌이나 구조 불일치가 생기는 경우에만 승인 범위 안에서 수정한다.
3. `implement`
   - 기본 authority: `bounded_edit`
   - 호환 role hint: `code-worker`
   - 사용: Coordinator가 정한 승인 범위 안의 bounded implementation
   - 출력: 변경 파일, changed artifact IDs, reuse decision, 코드 앵커 변경, verification result,
     남은 risk
   - 경계: 명시 승인 없이 API contract, DB schema/migration, auth/security, generated/codegen,
     shared architecture, public interface, dependency 또는 build system을 변경하지 않는다.
   - 재사용: 새 기능이나 method를 만들기 전에 capability, `provides`, `uses`, `implements`,
     실제 code reference, 기존 test를 함께 검색하고 `reuse_existing`, `extend_existing`,
     `create_new` 중 하나로 reuse decision을 보고한다.
   - 코드 앵커: reusable core method, public API, domain rule, shared service, 중요한 test에는
     필요한 경우 코드 앵커를 추가한다. Local helper, trivial wrapper, generated code에는 기본적으로
     추가하지 않는다.
4. `review`
   - 기본 authority: `review_only`
   - 호환 role hint: `reviewer`
   - 사용: worker output이 completion criteria, scope, risk, regression 가능성 측면에서 검토가
     필요할 때
   - 출력: findings, risks, required repair, review conclusion
   - 경계: 판단과 보고를 수행한다. 파일 수정, repair, acceptance 처리는 하지 않는다.
   - Graph review: 기존 capability 재사용 여부, 중복 implementation 생성 여부, semantic stale,
     코드 앵커 admission 적절성을 검토한다.
5. `verify`
   - 기본 authority: `verification`
   - 호환 role hint: `verifier`
   - 사용: 기준서-led verification을 별도 Goal로 실행하거나 failure 원인을 분리해야 할 때
   - 출력: verification command/result, pass/fail, failure cause, graph validation result,
     residual risk
   - 경계: 승인된 검증 명령 또는 문서 기반 검증을 실행하고 원인을 분리한다. 명시 승인 없이
     tracked file 수정이나 repair를 하지 않는다.
   - Graph validation: duplicate ID, unresolved relation, stale locator, missing symbol, missing
     test reference 같은 mechanical stale을 확인한다.

<!-- key: id=key.standard.subagent.injected-skill-contract refs=key.role.subagent key.topic.skill-contract key.topic.artifact-graph -->
## Injected skill contract

Injected skill은 authority를 올리지 않는다. Injected skill은 worker가 assignment 안에서 사용할
방법, 판단 기준, 필수 report 항목을 제한한다.

Injected skill contract는 다음 shape을 우선 사용한다.

```yaml
injected_skill:
  skill_id:
  mode:
  authority_ceiling:
  allowed_inputs:
  allowed_outputs:
  allowed_use:
  required_output:
  forbidden_use:
  stop_conditions:
```

Default bounded worker contract는 다음 shape을 우선 사용한다.

```yaml
injected_skill:
  skill_id: keystone-default-bounded-worker
  mode: default
  authority_ceiling: assignment_authority
  allowed_use:
    - assignment 안의 local planning
    - 제공된 source context와 read scope 사용
    - missing context, missing scope, missing verification 보고
  required_output:
    - scope_check
    - forbidden_change_check
    - verification
    - residual_risk
  forbidden_use:
    - child subagent creation
    - scope expansion
    - Main acceptance
    - progress accepted 또는 complete update
  stop_conditions:
    - source context 부족
    - scope 또는 authority 불명확
    - verification path 부재
```

External coding skill contract는 다음 shape을 우선 사용한다. `superpowers` 같은 구체 스킬은
이 shape에 맞춰 주입하며, Keystone 기준서는 특정 외부 코딩 스킬을 runtime dependency로
취급하지 않는다.

```yaml
injected_skill:
  skill_id:
  mode:
  authority_ceiling: assignment_authority
  allowed_inputs:
    - worker_assignment
    - context_pack
    - source_documents
    - allowed_edit_scope
    - verification
  allowed_outputs:
    - implementation_plan
    - changed_files
    - tests_run
    - verification_result
    - residual_risk
  allowed_use:
    - assignment 안의 코딩 workflow guidance
    - 승인된 scope 안의 local planning
    - 승인된 verification path 실행 또는 보고
  required_output:
    - skill_usage
    - scope_check
    - forbidden_change_check
    - verification
    - residual_risk
  forbidden_use:
    - Coordinator replacement
    - authority escalation
    - scope expansion
    - child subagent creation
    - Main acceptance
    - progress accepted 또는 complete update
  stop_conditions:
    - injected skill 절차가 assignment scope를 넘음
    - injected skill이 추가 authority나 외부 상태를 요구함
    - verification path가 skill 요구와 충돌함
```

External coding skill mode policy는 다음 값을 우선 사용한다.

```yaml
external_coding_skill_mode_policy:
  default_mode: coding_guidance
  allowed_modes:
    - coding_guidance
    - planning
    - tdd
    - debugging
    - review
    - skill_testing
  mode_selection:
    coding_guidance: 별도 mode가 명시되지 않은 일반 구현 보조
    planning: 구현 전 접근 비교와 계획 수립이 주목적일 때
    tdd: test-first 변경이 승인된 edit scope와 verification path에 포함될 때
    debugging: 실패 재현과 원인 분리가 주목적일 때
    review: 파일 수정 없이 검토가 주목적일 때
    skill_testing: SKILL.md behavior simulation이나 fixture 검증이 주목적일 때
```

규칙은 다음과 같다.

1. Worker의 기본 경계는 assignment의 goal, purpose, authority, scope, forbidden changes,
   workspace guard, verification, return report contract가 정한다.
2. Worker authority는 assignment authority와 injected skill의 `authority_ceiling` 중 더 좁은
   경계를 따른다.
3. `keystone-linker` 같은 read-only skill을 주입받아 발견한 후보는 evidence일 뿐 edit
   permission이 아니다.
4. Discovered candidate는 자동 채택, 자동 수정, 자동 acceptance 근거가 아니다.
5. Injected skill이 요구하는 절차가 assignment scope를 넘으면 worker는 `NEEDS_SCOPE_CHANGE`
   또는 `NEEDS_CONTEXT`로 보고한다.
6. Injected skill output은 worker report에 `skill_usage`로 남긴다.
7. Domain-specific 또는 명시된 external coding skill이 없으면 Coordinator는 worker assignment에
   `keystone-default-bounded-worker` contract를 포함한다.
8. `injected_skills: []`는 worker에게 맡길 절차와 report 기준이 없다는 뜻이므로 기본값으로
   사용하지 않는다.
9. 외부 코딩 스킬이 명시되면 worker는 해당 스킬의 workflow guidance를 사용할 수 있지만,
   Coordinator assignment의 scope, forbidden changes, workspace guard, verification,
   return report contract를 우선한다.
10. 외부 코딩 스킬이 명시된 경우 `keystone-default-bounded-worker` contract를 중복 주입하지
    않아도 된다. 이 경우에도 assignment의 기본 경계와 return report contract는 항상 적용된다.
11. 외부 코딩 스킬이 자체적으로 TDD, debugging, review 같은 workflow를 요구해도 그 절차가
   assignment scope 밖의 파일 변경, 권한 상승, 추가 subagent 생성, Main acceptance를 요구하면
   worker는 진행하지 않고 보고한다.
12. 외부 코딩 스킬 사용은 worker의 local workflow를 바꿀 수 있지만 Keystone acceptance
    criteria를 바꾸지 않는다.
13. 외부 코딩 스킬을 사용한 worker report는 `skill_usage`에 skill id, mode, outputs used,
    limits hit를 남겨야 한다.

<!-- key: id=key.standard.subagent.input-contract refs=key.role.subagent key.contract.output key.topic.work-execution key.topic.keystone-metadata key.topic.artifact-graph -->
## Input contract

Worker에게 작업을 맡길 때는 최소한 다음을 제공해야 한다.

1. `assignment_id`
2. Goal
3. Purpose preset과 optional role hint
4. Authority
5. Primary scope와 read scope
6. Allowed edit scope, excluded scope, conditional scope
7. Source Context 또는 Context Pack
8. 관련 `key.id`, `key.refs`, 코드 앵커 typed relation, 키메타/코드 앵커 기반 후보 문서와 artifact
9. Injected skill contract. Domain-specific skill이 없으면 `keystone-default-bounded-worker`
   contract를 포함한다.
10. Completion Criteria
11. Stop Conditions
12. Verification path
13. 필요한 경우 impact seeds 또는 Change Set(17)
14. Workspace guard
15. Report status contract

Input이 부족하면 worker는 추측해서 범위를 넓히지 않고 `NEEDS_CONTEXT` 또는 `BLOCKED`로
보고한다.

<!-- key: id=key.standard.subagent.workspace-guard refs=key.role.subagent key.topic.work-execution key.boundary.approval -->
## Single workspace guard

기본 실행 모델은 single workspace bounded worker orchestration이다.

1. 한 번에 하나의 file-writing worker만 허용한다.
2. Coordinator는 이전 file-writing worker report를 처리하기 전 다음 file-writing worker를
   배정하지 않는다.
3. Worker는 allowed edit scope 밖의 파일을 수정하지 않는다.
4. Worker는 기존 사용자 변경이나 다른 agent 변경을 정리, 되돌림, 덮어쓰기 하지 않는다.
5. 기존 변경과 충돌할 가능성이 있으면 `BLOCKED` 또는 `DONE_WITH_CONCERNS`로 보고한다.
6. 파괴적 workspace 조작은 사용자 또는 Main의 명시 승인 없이는 금지한다.
7. Worker report에는 changed files, scope check, forbidden change check가 포함되어야 한다.

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

<!-- key: id=key.standard.subagent.report-status refs=key.role.subagent key.topic.report key.contract.output -->
## Report status

Worker report status 값은 다음과 같다.

1. `DONE`
   - 요청 범위가 완료되었다고 보고한다.
2. `DONE_WITH_CONCERNS`
   - 완료되었지만 risk나 불확실성이 있다.
3. `NEEDS_CONTEXT`
   - 필요한 문서, 기준, 파일, 결정(6), skill contract가 부족하다.
4. `NEEDS_SCOPE_CHANGE`
   - 승인된 scope를 넘어야 한다.
5. `BLOCKED`
   - 외부 상태, missing dependency, 권한, 충돌 때문에 진행할 수 없다.

Worker report status는 progress status가 아니다. Main 또는 Coordinator가 실제 상태와
verification을 확인하기 전까지 `DONE`을 accepted로 해석하지 않는다.

<!-- key: id=key.standard.subagent.report-envelope refs=key.role.subagent key.contract.report key.contract.output key.topic.verification -->
## Report envelope

Worker report는 purpose-specific payload를 추가할 수 있지만, 기본 envelope는 다음 필드를
우선 사용한다.

```yaml
worker_report:
  assignment_id:
  status: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | NEEDS_SCOPE_CHANGE | BLOCKED
  status_reason:
  reason_code:
  purpose:
  role_hint:
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
  workspace_conflicts:
  keymeta_or_code_anchor_gap_candidates:
  risks:
  residual_risk:
  recommended_next_action:
```

`NEEDS_CONTEXT` report는 가능하면 다음 reason code를 포함한다.

1. `missing_standard`
2. `missing_work_order`
3. `missing_artifact_seed`
4. `missing_skill_contract`
5. `missing_verification_path`
6. `source_conflict`
7. `stale_work_order`
8. `stale_progress_record`
9. `accepted_decision_not_propagated`
10. `default_worker_contract_missing`

`NEEDS_SCOPE_CHANGE` report는 가능하면 다음 shape을 포함한다.

```yaml
requested_scope_change:
  kind:
  reason:
  affected_artifact_candidates:
  verification_impact:
  recommended_next_action:
```

`kind`는 다음 값을 우선 사용한다.

1. `api_contract`
2. `schema`
3. `auth_security`
4. `generated_codegen`
5. `shared_architecture`
6. `public_interface`
7. `dependency`
8. `build_system`
9. `test_scope`
10. `external_skill_scope_conflict`
11. `source_authority_change`
12. `acceptance_criteria_change`
13. `status_semantics_change`

<!-- key: id=key.standard.subagent.common-boundary refs=key.role.subagent key.boundary.approval key.topic.work-execution key.topic.keystone-metadata -->
## 공통 경계

모든 helper/subagent/worker는 다음을 지켜야 한다.

1. 받은 Goal 밖으로 scope를 넓히지 않는다.
2. 전체 작업서(4)를 재해석하지 않는다.
3. 추가 subagent를 생성하지 않는다.
4. Main acceptance 없이 progress를 `accepted` 또는 `complete`로 바꾸지 않는다.
5. 승인되지 않은 source authority, acceptance criteria, status semantics를 바꾸지 않는다.
6. 민감한 정보, local-only path, private data가 필요하면 멈추고 보고한다.
7. Worker output은 원천 문서(2)나 Main decision을 대체하지 않는다.
8. 키메타/코드 앵커 기반 후보나 reuse candidate는 채택 결정이 아니라 검토 대상 evidence로
   보고한다.
9. Impact candidate가 연결되어 있다는 이유만으로 수정하지 않는다. 관련성이 불확실하면
   수정하지 않고 report한다.
10. Existing user change 또는 다른 agent change를 덮어쓰지 않는다.
11. Self-review는 worker report의 일부일 수 있지만 independent review로 보지 않는다.
12. Independent review가 필요하면 별도 `review` assignment를 만든다.

<!-- key: id=key.standard.subagent.stop-condition refs=key.role.subagent key.boundary.stop-condition key.topic.work-execution -->
## Stop condition

Worker는 다음 상황에서 멈추고 report한다.

1. Goal, scope, authority, stop condition이 불명확하다.
2. Completion Criteria를 만족하려면 승인 범위를 넘어야 한다.
3. 필요한 source context가 빠져 있다.
4. 필요한 injected skill contract가 빠져 있다.
5. 사용자 변경이나 workspace state와 충돌한다.
6. 민감한 정보, local-only path, private data가 필요하다.
7. Verification path가 없거나 실행 결과가 판단 불가능하다.
8. 추가 subagent나 전체 workflow 재조율이 필요하다.
9. 새 reusable artifact를 만들어야 하지만 기존 capability/provider 탐색 결과가 없다.
10. 키메타 또는 코드 앵커 relation이 가리키는 artifact가 없고 fallback 판단이 불가능하다.
11. Assignment scope 밖의 API contract, schema, auth/security, generated/codegen, shared
    architecture, public interface, dependency, build system 변경이 필요하다.
12. Existing user change 또는 다른 agent change를 덮어써야만 진행할 수 있다.
13. 주입된 외부 코딩 스킬의 필수 절차가 assignment의 authority, scope, verification,
    workspace guard와 충돌한다.

<!-- key: id=key.standard.subagent.verification refs=key.role.subagent key.topic.verification -->
## Verification

Subagent 기준은 다음 방법으로 검증한다.

1. Purpose preset과 authority를 설명할 수 있어야 한다.
2. Worker assignment만 보고 수행 가능 범위와 stop condition을 구분할 수 있어야 한다.
3. Injected skill이 authority를 올리지 않는다는 점을 확인할 수 있어야 한다.
4. Report status와 progress status를 혼동하지 않아야 한다.
5. Coordinator 기준서는 purpose preset 정의를 반복하지 않고 이 기준서의 catalog를 참조해야 한다.
6. Author 기준서는 문서 작업 helper 사용 조건만 정의하고 formal workflow orchestration을
   소유하지 않아야 한다.
7. `document_edit` worker는 연결된 모든 문서가 아니라 승인된 변경과 의미상 관련된 문서만
   수정해야 한다.
8. `implement` worker는 새 구현 전에 reuse discovery 결과를 보고해야 한다.
9. `review` worker는 semantic stale과 중복 구현 risk를 검토할 수 있어야 한다.
10. `verify` worker는 graph validation의 mechanical stale을 보고할 수 있어야 한다.
11. Single workspace guard만 보고 file-writing worker의 배정 가능 여부를 판단할 수 있어야 한다.
12. 외부 코딩 스킬은 Coordinator를 대체하지 않고 injected skill로만 사용되어야 한다.
13. 외부 코딩 스킬이 요구하는 절차가 assignment boundary를 넘으면 worker가 멈추고 보고해야
    한다.
