---
doc_type: standard
key:
  id: key.standard.skill.clarify
  refs:
    - key.role.clarify
    - key.doc.decision
    - key.topic.question-flow
    - key.output.edit-plan
    - key.topic.impact-review
    - key.topic.keystone-metadata
    - key.topic.code-anchor
    - key.topic.artifact-graph
---

# keystone-clarify 기준서

<!-- key: id=key.standard.skill.clarify.purpose refs=key.role.clarify key.doc.decision key.output.edit-plan -->
## 목적

이 기준서는 `keystone-clarify`의 상세 계약을 정의한다. `keystone-clarify`는 원천 문서(2)
또는 스킬 계약에 영향을 주는 high-impact topic을 하나씩 명확히 하고, 수락된 결정(6)과
문서 update plan을 `keystone-author`가 안전하게 적용할 수 있게 만든다.

<!-- key: id=key.standard.skill.clarify.scope refs=key.role.clarify key.doc.decision key.topic.question-flow key.output.edit-plan -->
## 적용 범위

1. `keystone-clarify`의 trigger와 non-trigger condition
2. Topic-scoped question collection
3. Plan Mode selection UI 또는 동등한 질문 흐름
4. Reflection, decision summary, edit plan
5. Default Mode author handoff와 명시 승인된 현재 대상 문서의 단순 오탈자 수정 boundary
6. Impact update 대상과 stop condition
7. Initial project setup question contract

<!-- key: id=key.standard.skill.clarify.out-of-scope refs=key.role.clarify key.topic.skill-contract key.topic.external-assist -->
## 적용하지 않는 범위

1. 사소한 typo, wording, formatting 질문을 매번 생성하기. 단, 명시 승인된 현재 대상 문서
   안의 단순 오탈자는 Default Mode 직접 수정 예외로 처리할 수 있다.
2. 사용자 수락 없이 원천 문서(2), code, config, schema, API, test, generated/codegen artifact 수정
3. 스킬 구현 파일 작성
4. 기준서(3)나 작업서(4)를 직접 생성하거나 넓은 범위에서 재작성하기
5. 외부 보조 스킬(12)을 자동 실행 대상으로 만들기
6. project-local setting이 아닌 common/global instruction file에 Keystone setup 결과 쓰기

<!-- key: id=key.standard.skill.clarify.standard-relations refs=key.role.clarify key.doc.standard key.topic.skill-contract -->
## 기준 관계

1. Parent 기준서: `../../01_key-project-standard.md`
2. 상위 규칙: `STD-KEYSTONE-001`, `STD-KEYSTONE-006`, `STD-KEYSTONE-007`,
   `STD-KEYSTONE-014`, `STD-KEYSTONE-015`, `STD-KEYSTONE-016`,
   `STD-KEYSTONE-023`, `STD-KEYSTONE-041`, `STD-KEYSTONE-050`,
   `STD-KEYSTONE-051`, `STD-KEYSTONE-052`
3. 관련 결정(6): `00_docs/works/key-decisions.md`
4. 충돌 처리: 이 기준서와 parent 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의
   결정(6)을 받는다. 결정 전까지는 parent 기준서를 임시 우선 기준으로 삼는다.
5. 상세화 범위: 이 기준서는 `STD-KEYSTONE-041`의 Clarify behavior를 구현 가능한 수준으로
   상세화한다.

<!-- key: id=key.standard.skill.clarify.skill-identity refs=key.role.clarify key.topic.skill-contract -->
## Skill identity

1. Skill name: `keystone-clarify`
2. Primary role: high-impact topic clarification and author-ready document update planning
3. Primary user: main agent 또는 문서 정책 결정을 확정하려는 사용자
4. Output authority: Clarify output은 사용자가 수락하기 전까지 원천 문서(2)를 대체하지
   않는다.

<!-- key: id=key.standard.skill.clarify.required-input refs=key.role.clarify key.topic.question-flow key.output.edit-plan key.topic.impact-review -->
## Required input

Clarify는 다음 input을 사용할 수 있어야 한다.

1. 사용자 요청 또는 main의 current clarification topic
2. 현재 topic과 관련된 원천 문서(2), 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 후보
3. Plan Mode 또는 Default Mode를 판단할 수 있는 context
4. 이미 수락된 decision summary와 edit plan이 있는 경우 그 내용
5. 변경 대상 원천 문서(2), section, 승인 범위 후보
6. affected document 후보와 affected artifact 후보
7. Initial setup topic인 경우 document root, tracking policy, output language policy,
   setup storage location 후보
8. 민감 정보, local-only path, common/global instruction file, config write 여부와 관련된
   risk context
9. Modularization topic인 경우 Linker report, reuse candidate, worker report, reviewer
   finding, 또는 사용자가 제시한 유사 capability나 reusable artifact 근거

Input이 부족하면 Clarify는 high-impact decision을 추정하지 않고 incomplete result,
open question, stop condition으로 보고한다.

<!-- key: id=key.standard.skill.clarify.trigger-condition refs=key.role.clarify key.doc.decision key.topic.impact-review -->
## Trigger condition

`keystone-clarify`는 다음 경우에 사용할 수 있다.

1. 정책, 범위, 문서 구조, 스킬 계약, cross-document consistency에 영향을 주는 결정(6)이
   필요하다.
2. 원천 문서(2)를 의미 있게 바꾸기 전에 사용자 의도를 명확히 해야 한다.
3. Keystone initial setup에서 document root, tracking policy, output language policy,
   setup storage location을 결정해야 한다.
4. 문서 변경이 여러 기준서(3), 작업서(4), 진행 기록(5), 결정(6), 파생 에이전트 문서(8)에
   영향을 줄 수 있다.
5. current task의 방향이 기존 원천 문서(2)와 충돌한다.
6. main이 추론으로 진행하면 잘못된 feature, workflow, policy, acceptance criteria를 만들
   위험이 있다.
7. 기존 capability, reusable artifact, 또는 유사 implementation 후보가 evidence와 함께 발견되어
   reuse, extend, extract shared module, create new, investigate first 중 어떤 방향을 택할지
   결정해야 한다.

<!-- key: id=key.standard.skill.clarify.non-trigger-condition refs=key.role.clarify key.topic.skill-contract -->
## Non-trigger condition

`keystone-clarify`는 다음 경우에 사용하지 않는다.

1. 사소한 수정마다 high-impact 질문을 만들기. 단, 명시 승인된 현재 대상 문서 안에서 의미
   변화와 외부 영향이 객관적으로 없는 단순 오탈자는 Default Mode 직접 수정 예외로 처리할 수
   있다.
2. 이미 수락된 결정(6)과 대상 문서가 명확해 Author가 처리해야 하는 단일 문서 update
3. Reader가 수행해야 하는 read-only orientation 또는 document navigation
4. Author가 수행해야 하는 기준서(3) 또는 작업서(4) 작성 자체
5. Coordinator가 수행해야 하는 formal workflow orchestration, report handling,
   acceptance flow
6. 구현 code, config, schema, API, test, generated/codegen artifact 수정이나 테스트 실행 자체
7. 유사 기능 후보가 단순 keyword overlap이거나 local helper 수준이라 high-impact decision이
   아니다.
8. Linker report, worker report, reviewer finding, 사용자 제공 근거 같은 evidence 없이
   Clarify가 repository 유사성을 직접 확정해야 한다.
9. 기존 기준서(3), 작업서(4), 또는 Coordinator assignment scope가 reuse/extend 방향을 이미
   명확히 정했고 worker가 local implementation detail로 안전하게 처리할 수 있다.

<!-- key: id=key.standard.skill.clarify.topic-boundary refs=key.role.clarify key.doc.decision key.topic.question-flow -->
## Topic boundary

Clarify는 한 번에 하나의 topic을 다룬다.

1. 좋은 topic: document root policy, tracking policy, Reader trigger boundary,
   output language policy, skill-specific non-trigger condition, modularization decision topic
2. 나쁜 topic: "Keystone 전체를 어떻게 할까요"처럼 여러 정책을 한 번에 묶은 질문
3. Topic이 너무 크면 main은 하위 topic으로 나누어 질문한다.
4. 같은 topic 안에서는 충분한 정보가 모일 때까지 필요한 follow-up을 이어갈 수 있다.
5. Topic이 충분히 결정되면 다음 topic으로 넘어가기 전에 reflection과 update plan을
   요약한다.

<!-- key: id=key.standard.skill.clarify.modularization-decision-topic refs=key.role.clarify key.topic.impact-review key.topic.artifact-graph -->
## Modularization decision topic

Modularization decision topic은 기존 capability(16), code/config/schema/API/test artifact,
또는 유사 implementation 후보가 발견되어 reuse, extend, extract shared module, create new,
investigate first 중 어떤 방향으로 갈지 결정해야 하는 high-impact topic이다.

Clarify는 modularization 가능성을 제안할 수 있지만 repository 유사성을 직접 확정하지 않는다.
유사 기능 후보 발견과 evidence 등급화는 Linker report, Coordinator worker report, reviewer
finding, 또는 사용자가 제공한 근거를 input으로 사용한다.

Clarify는 다음 조건을 모두 만족할 때 modularization decision topic을 제안한다.

1. 기존 capability 또는 reusable artifact 후보가 evidence와 함께 발견되었다.
2. 새 구현을 만들면 중복 구현, policy drift, document drift, test drift 중 하나가 생길 수 있다.
3. 선택에 따라 문서, 기준서(3), 작업서(4), API contract, schema, test, acceptance criteria,
   verification, 또는 implementation scope가 달라진다.
4. Reuse, extend, extract shared module, create new, investigate first 중 선택이 필요하다.
5. Linker report, worker report, reviewer finding, 또는 사용자가 제시한 구체 근거가 있다.

Clarify는 다음 경우 modularization decision topic을 제안하지 않는다.

1. 유사성이 단순 keyword overlap뿐이다.
2. 단순 local helper 중복이나 같은 파일 안의 작은 함수 추출 수준이다.
3. 기존 기준서(3), 작업서(4), 결정(6), 또는 Coordinator assignment가 reuse/extend 방향을 이미
   명확히 정했다.
4. Worker가 assignment scope 안에서 local implementation detail로 안전하게 처리할 수 있다.
5. Evidence가 부족해 Linker 또는 investigate worker가 먼저 필요하다. 이 경우 Clarify는
   `investigate_first` 또는 `author_edit_ready: false`로 보고한다.

Modularization 선택지는 다음 vocabulary를 우선 사용한다.

1. `reuse_existing`: 기존 capability/provider를 그대로 사용한다.
2. `extend_existing`: 기존 capability/provider를 승인 범위 안에서 확장한다.
3. `extract_shared_module`: 중복 구현 후보에서 공통 module을 추출하고 기존/신규 구현이 함께
   사용하게 한다.
4. `create_new`: 중복 위험을 인지하고 신규 구현으로 둔다.
5. `investigate_first`: evidence가 부족하므로 Linker 또는 investigate worker를 먼저 수행한다.

`extract_shared_module`은 shared architecture, public interface, API/schema/test scope에 영향을 줄
가능성이 높으므로 high-impact decision으로 취급한다. Clarify는 이 선택을 코드 수정 지시로
바꾸지 않고 Author와 Coordinator handoff에 남긴다.

Clarify 질문은 evidence와 선택지를 분리해 구성한다.

```yaml
modularization_question:
  evidence:
    candidate_capability:
    candidate_artifact:
    source: linker_report | worker_report | reviewer_finding | user_request
    confidence: declared | observed | inferred
    duplication_or_drift_risk:
    affected_documents_or_tests_or_api:
  options:
    - reuse_existing
    - extend_existing
    - extract_shared_module
    - create_new
    - investigate_first
```

<!-- key: id=key.standard.skill.clarify.plan-mode-contract refs=key.role.clarify key.topic.question-flow key.doc.decision -->
## Plan Mode contract

Plan Mode는 질문과 결정을 수집하는 mode다.

1. 사용 가능한 경우 `request_user_input` 또는 동등한 selection UI를 사용한다.
2. 한 번에 하나의 focused question을 묻는다.
3. 질문은 선택지의 tradeoff를 짧게 설명해야 한다.
4. 사용자가 답하면 해당 답이 topic을 결정하기에 충분한지 판단한다.
5. 충분하지 않으면 같은 topic에 대해 targeted follow-up을 묻는다.
6. 사용자의 답이 "알아서 해주세요"처럼 편의상 위임에 그치고 project standard의 명시적
   default가 없으면 high-impact decision으로 추정하지 않는다.
7. 답이 충분하지 않은 상태에서 report해야 하면 `author_edit_ready: false`, unresolved
   `open_questions`, Author-ready `edit_plan` 없음으로 incomplete result를 반환한다.
8. 충분하면 decision summary, working assumptions, `decision_completeness_check`,
   `decision_recording_hint`, Author handoff용 edit plan을 만든다.
9. Plan Mode는 원천 문서(2)를 직접 수정하지 않는다.

<!-- key: id=key.standard.skill.clarify.default-mode-contract refs=key.role.clarify key.output.edit-plan key.topic.document-authoring -->
## Default Mode contract

Default Mode는 수락된 clarify result를 바탕으로 Author가 문서 update를 적용할 수 있게
정리한다. Clarify가 직접 수정할 수 있는 경우는 명시 승인된 현재 대상 문서 안에서 의미 변화와
다른 문서 영향이 객관적으로 없는 단순 오탈자로 제한한다.

1. 적용 전 조건:
   - topic이 충분히 결정되어 있다.
   - 사용자 또는 main session이 decision summary와 edit plan을 수락했다.
   - 변경 대상 원천 문서(2)와 section이 식별되어 있다.
2. Author handoff 대상:
   - Handoff는 자동 실행이 아니며, main 또는 사용자가 `keystone-author` 호출 여부와 적용
     범위를 결정한다.
   - 관련 기준서(3)
   - 관련 작업서(4)
   - 진행 기록(5)
   - 결정(6) 기록
   - `STD-KEYSTONE-016`의 조건을 만족하는 파생 에이전트 문서(8)
3. Clarify 직접 수정 허용:
   - 명시 승인된 현재 대상 문서 안의 단순 오탈자
   - 다른 문서, 기준서(3), 작업서(4), scope, acceptance criteria, status semantics에 영향이
     없는 단순 오탈자 수정
4. 금지:
   - 수락되지 않은 topic을 근거로 문서 수정
   - 다른 문서와 함께 맞춰야 하는 원천 문서(2) 수정
   - 기준, 정책, scope, acceptance criteria, status semantics처럼 다른 문서와 함께 맞춰야
     하는 변경 직접 수정
   - implementation code, config, schema, API, test, generated/codegen artifact 수정
   - 승인되지 않은 scope 또는 acceptance criteria 변경
   - common/global instruction file에 setup result 기록

<!-- key: id=key.standard.skill.clarify.reflection-edit-plan refs=key.role.clarify key.output.edit-plan key.doc.decision -->
## Reflection and edit plan

Clarify result는 다음을 포함해야 한다.

1. `topic`: 결정한 주제
2. `decision_summary`: 사용자가 수락한 결정(6). Incomplete result에서는 null 또는 unresolved로
   표시한다.
3. `rationale`: 주요 이유와 tradeoff
4. `working_assumptions`: 이후 작업에서 사용할 가정
5. `affected_documents`: Author가 검토해야 하는 원천 문서(2). 반드시 수정해야 하는 update
   target, inspect-only 후보, excluded 후보를 구분한다.
6. `affected_artifact_candidates`: capability, code, config, schema, API, test 영향 후보
7. `edit_plan`: 문서별 변경 요약. Incomplete result에서는 Author-ready `edit_plan`을 만들지
   않고 누락 사유를 보고한다.
8. `stop_conditions`: 적용 중 중단해야 하는 조건
9. `open_questions`: 아직 남은 질문. 현재 topic을 완료하기 위해 필요한
   `unresolved_current_topic`과 이번 topic 밖의 `out_of_topic` 질문을 구분한다.
10. `decision_completeness_check`: decision이 Author handoff 가능한 수준인지 확인한 결과
11. `decision_recording_hint`: 수락된 결정(6)을 어디에 기록해야 하는지에 대한 권장 위치와
    이유. Hint는 기록 권한이 아니며, 실제 기록은 Author 또는 Main이 승인 범위 안에서
    처리한다.
12. `modularization_decision`: modularization topic인 경우 reuse, extend, extract shared module,
    create new, investigate first 중 어떤 방향을 선택했는지와 그 근거. Modularization topic이
    아니면 생략한다.

High-impact topic, Plan Mode result, 또는 Author handoff가 있는 non-trivial Clarify result는
`decision_completeness_check`를 포함해야 한다. 현재 case가 단순 오탈자 직접 수정 예외라면
Clarify는 이 check가 적용되지 않는 이유를 보고한다.

결정(6)을 만들거나 바꾸는 non-trivial Clarify result는 `decision_recording_hint`를 포함해야
한다. 영구 결정 기록이 필요하지 않으면 Clarify는 기록이 필요하지 않은 이유를 보고한다.

Affected documents는 다음 shape을 우선 사용한다.

```yaml
affected_documents:
  update_targets:
    - path:
      sections:
      reason:
      required_change:
  inspect_only_candidates:
    - path:
      reason:
      evidence:
  excluded:
    - path:
      reason:
```

`decision_completeness_check.affected_source_documents`는 `affected_documents`의 요약 또는
mirror field다. 두 필드가 다르게 해석될 수 있으면 structured `affected_documents`를 우선한다.

Open questions는 다음 shape을 우선 사용한다.

```yaml
open_questions:
  unresolved_current_topic:
    - question:
      reason:
  out_of_topic:
    - question:
      reason:
```

Decision completeness check는 다음 shape을 우선 사용한다.

```yaml
decision_completeness_check:
  selected_option:
  rejected_options:
  rationale:
  affected_source_documents:
  affected_work_orders:
  affected_artifact_candidates:
  acceptance_or_status_impact:
  recording_scope: global | round | work | none | unresolved
  recording_reason:
  author_edit_ready: true | false
```

Decision recording hint는 다음 shape을 우선 사용한다.

```yaml
decision_recording_hint:
  scope: global | round | work | none | unresolved
  recommended_path:
  reason:
  requires_author_update: true | false
```

Modularization decision은 다음 shape을 우선 사용한다.

```yaml
modularization_decision:
  status: proposed | accepted | rejected | needs_linker_report | out_of_scope
  trigger_evidence:
    source: linker_report | worker_report | reviewer_finding | user_request
    summary:
  similar_artifacts:
    - key_id:
      kind: capability | code | config | schema | api | test
      locator:
      evidence: declared | observed | inferred
      risk:
  options:
    - reuse_existing
    - extend_existing
    - extract_shared_module
    - create_new
    - investigate_first
  selected_option:
  rationale:
  impact:
    affected_documents:
    affected_capabilities:
    affected_code_config_schema_api_test:
    verification_needed:
  handoff:
    author:
    linker:
    coordinator:
```

판단 기준은 다음을 따른다.

1. 여러 round에 영향을 주는 결정(6)은 `works/key-decisions.md`를 권장한다.
2. 특정 round 안에서만 유효한 결정(6)은 해당 round의 `key-decisions.md`를 권장한다.
3. 특정 work node 안에서만 유효한 결정(6)은 해당 work node의 `key-decisions.md`를 권장한다.
4. `none`은 영구 결정 기록이 필요하지 않은 경우에 사용한다.
5. `unresolved`는 decision이 아직 충분하지 않아 기록 위치를 정할 수 없는 경우에 사용한다.
6. 결정 기록 위치가 불명확하면 Clarify는 직접 기록하지 않고 Author handoff에
   `decision_recording_hint`를 포함한다.
7. Hint는 기록 권한이 아니며, 실제 원천 문서(2) 반영은 Author 또는 Main이 승인 범위 안에서
   처리한다.
8. `author_edit_ready`가 `false`이면 Clarify result는 Author가 바로 적용할 수 있는 edit
   instruction이 아니다. Main 또는 사용자는 남은 open question을 먼저 결정해야 한다.
9. 사용자의 답이 decision을 확정하기에 부족하면 `author_edit_ready: false`, unresolved
   `open_questions`, Author-ready `edit_plan` 없음으로 보고한다.
10. `acceptance_or_status_impact`가 있으면 progress status, acceptance criteria, status semantics를
    바꾸는지 분리해 보고한다.
11. Modularization decision이 `investigate_first` 또는 `needs_linker_report`이면 Author-ready
    `edit_plan`을 만들지 않고 필요한 Linker 또는 Coordinator investigation을 next action으로
    남긴다.
12. `create_new`를 선택하면 제외한 reuse candidate와 이유를 Author handoff 또는 Change Set
    후보에 남긴다.
13. `extract_shared_module`을 선택하면 shared architecture, public interface, API/schema/test,
    verification impact를 별도로 보고하고 Coordinator workflow로 넘긴다.

<!-- key: id=key.standard.skill.clarify.impact-update refs=key.role.clarify key.topic.impact-review key.output.edit-plan key.topic.keystone-metadata key.topic.code-anchor key.topic.artifact-graph -->
## Impact update

수락된 clarify result가 문서에 반영될 때는 다음 규칙을 따른다.

1. 관련 parent 기준서와 child 기준서가 함께 영향을 받으면 `keystone-author`가 둘 다
   검토할 수 있게 edit plan에 포함한다.
2. 작업서(4)의 scope, completion criteria, status semantics에 영향을 주면 명시적으로
   보고한다.
3. 진행 기록(5)은 main acceptance 없이 완료 상태로 바꾸지 않는다.
4. 결정(6)은 장기 정책이나 여러 문서에 영향을 주는 경우에 기록한다.
5. 파생 에이전트 문서(8)는 이미 존재하고 명확히 영향받을 때만 edit plan에 포함한다. 새로
   생성하는 경우는 `STD-KEYSTONE-016`의 명시적 필요 조건을 따른다.
6. 키메타(9)가 있는 topic이나 문서가 관련되면 같은 `key.id`를 참조하는 문서를
   affected document 후보로 검토한다.
7. 같은 `key.refs`가 있어도 자동으로 edit plan에 포함하지 않는다.
8. `key.refs`가 없어도 관련 없음으로 단정하지 않는다.
9. 결정이 capability, code, config, schema, API, test artifact에 영향을 줄 수 있으면 코드 앵커(18)나
   아티팩트 그래프(14) 기반 affected artifact 후보를 edit plan에 분리해 기록한다.
10. Modularization decision이 수락되면 affected capability, excluded reuse candidate,
    verification 필요성, Linker report reference, Coordinator handoff 필요성을 edit plan 또는
    Author handoff에 분리해 기록한다.
11. 영향 범위가 불확실하면 문서 수정을 멈추고 사용자 또는 main 결정(6)을 요청한다.

<!-- key: id=key.standard.skill.clarify.initial-setup-question-contract refs=key.role.clarify key.topic.question-flow key.topic.document-system -->
## Initial setup question contract

Target project에서 Keystone setting이 없거나 불명확하면 Clarify는 initial setup question을
다룰 수 있다.

1. 질문 대상:
   - document root
   - 기준서(3)와 작업서(4) tracking policy
   - 파생 에이전트 문서(8) tracking policy
   - Keystone output language policy
   - setup storage location
2. 기본 storage:
   - shared setting은 `.keystone/config.yaml`
   - personal, local-only, sensitive override는 `.keystone/config.local.yaml`
   - Clarify는 setup storage location을 결정하거나 권장할 수 있지만 `.keystone/config.yaml`
     또는 `.keystone/config.local.yaml`을 직접 생성하거나 수정하지 않는다.
   - 수락된 setup decision의 실제 기록은 Author, Main, 또는 명시 승인된 project-local setup
     step이 처리한다.
3. 금지:
   - common/global instruction file에 조용히 기록하기
   - fixture/test step 또는 명시적인 project-local setup 요구 없이 이 Keystone implementation
     repository에 `.keystone/config.yaml`이 필요하다고 암시하거나 해당 파일을 생성하기
   - 민감한 값을 사용자 확인 없이 쓰기, track, publish, derive하기

<!-- key: id=key.standard.skill.clarify.stop-condition refs=key.role.clarify key.topic.skill-contract key.topic.impact-review -->
## Stop condition

Clarify는 다음 상황에서 중단하거나 main/user 결정(6)을 요청한다.

1. Topic이 여러 high-impact 결정을 동시에 포함해 하나의 질문으로 다룰 수 없다.
2. 사용자의 답이 서로 충돌하거나 기존 원천 문서(2)와 충돌한다.
3. 적용하려는 변경이 승인된 scope 또는 acceptance criteria를 바꾼다.
4. 변경 대상 문서나 section이 불명확하다.
5. 민감한 정보, local-only path, private data를 기록해야 할 수 있다.
6. 외부 보조 스킬(12)을 automatic/must-use로 바꾸는 결과가 된다.
7. Clarify topic을 넘는 implementation, config/schema/API/test artifact 수정, auth/security,
   generated/codegen, publishing 실행 결정이 먼저 필요하다.
8. Modularization topic에서 유사 기능 evidence가 부족해 Clarify가 repository 유사성을 직접
   확정해야만 진행할 수 있다.
9. Modularization 선택이 shared architecture, API/schema/test scope, acceptance criteria를 바꾸지만
   사용자 또는 main decision이 없다.

<!-- key: id=key.standard.skill.clarify.verification refs=key.role.clarify key.topic.verification key.output.edit-plan -->
## Verification

Clarify 기준은 다음 방법으로 검증한다.

1. Clarify contract만 보고 trigger와 non-trigger를 구분할 수 있어야 한다.
2. Plan Mode와 Default Mode의 책임 차이가 명확해야 한다.
3. 수락 전에는 원천 문서(2)를 수정하지 않는다는 경계가 명확해야 한다.
4. Reflection과 edit plan만 보고 Author가 문서 update 범위를 판단할 수 있어야 한다.
5. Initial setup question이 `STD-KEYSTONE-050`, `STD-KEYSTONE-051`,
   `STD-KEYSTONE-052`과 일관되어야 한다.
6. 키메타와 코드 앵커 기반 affected 후보가 있으면 edit plan에서 후보와 실제 반영 여부를
   구분할 수 있어야 한다.
7. Modularization decision topic은 Linker report, worker report, reviewer finding, 또는 사용자
   제공 근거를 input으로 사용하고 Clarify가 repository 유사성을 직접 확정하지 않아야 한다.
8. Modularization 선택지가 reuse, extend, extract shared module, create new, investigate first의
   의미와 handoff boundary를 구분해야 한다.
9. Verification command:
   - `rg --files 00_docs`
   - Clarify 관련 기준서를 읽어 link와 scope consistency 확인
