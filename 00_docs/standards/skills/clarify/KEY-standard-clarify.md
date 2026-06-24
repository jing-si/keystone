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
4. Reflection과 decision summary
5. Default Mode author handoff와 명시 승인된 현재 대상 문서의 단순 오탈자 수정 boundary
6. Impact update 대상과 stop condition
7. Initial project setup question contract

<!-- key: id=key.standard.skill.clarify.out-of-scope refs=key.role.clarify key.topic.skill-contract key.topic.external-assist -->
## 적용하지 않는 범위

1. 사소한 typo, wording, formatting 질문을 매번 생성하기. 단, 명시 승인된 현재 대상 문서
   안의 단순 오탈자는 Default Mode 직접 수정 예외로 처리할 수 있다.
2. 사용자 수락 없이 원천 문서(2), code, config, generated file 수정
3. 스킬 구현 파일 작성
4. 기준서(3)나 작업서(4)를 직접 생성하거나 넓은 범위에서 재작성하기
5. 외부 보조 스킬(12)을 자동 실행 대상으로 만들기
6. project-local setting이 아닌 common/global instruction file에 Keystone setup 결과 쓰기

<!-- key: id=key.standard.skill.clarify.standard-relations refs=key.role.clarify key.doc.standard key.topic.skill-contract -->
## 기준 관계

1. Parent 기준서: `../../00_KEY-project-standard.md`
2. 상위 규칙: `STD-KEYSTONE-001`, `STD-KEYSTONE-007`, `STD-KEYSTONE-009`,
   `STD-KEYSTONE-014`, `STD-KEYSTONE-020`, `STD-KEYSTONE-021`, `STD-KEYSTONE-025`,
   `STD-KEYSTONE-026`, `STD-KEYSTONE-027`, `STD-KEYSTONE-028`, `STD-KEYSTONE-031`
3. 관련 결정(6): `00_docs/works/KEY-decisions.md`
4. 충돌 처리: 이 기준서와 parent 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의
   결정(6)을 받는다. 결정 전까지는 parent 기준서를 임시 우선 기준으로 삼는다.
5. 상세화 범위: 이 기준서는 `STD-KEYSTONE-025`의 Clarify behavior를 구현 가능한 수준으로
   상세화한다.

<!-- key: id=key.standard.skill.clarify.skill-identity refs=key.role.clarify key.topic.skill-contract -->
## Skill identity

1. Skill name: `keystone-clarify`
2. Primary role: high-impact topic clarification and author-ready document update planning
3. Primary user: main agent 또는 문서 정책 결정을 확정하려는 사용자
4. Output authority: Clarify output은 사용자가 수락하기 전까지 원천 문서(2)를 대체하지
   않는다.

<!-- key: id=key.standard.skill.clarify.trigger-condition refs=key.role.clarify key.doc.decision key.topic.impact-review -->
## Trigger condition

`keystone-clarify`는 다음 경우에 사용할 수 있다.

1. 정책, 범위, 문서 구조, 스킬 계약, cross-document consistency에 영향을 주는 결정(6)이
   필요하다.
2. 원천 문서(2)를 의미 있게 바꾸기 전에 사용자 의도를 명확히 해야 한다.
3. Keystone initial setup에서 document root, Git policy, output language policy,
   setup storage location을 결정해야 한다.
4. 문서 변경이 여러 기준서(3), 작업서(4), 진행 기록(5), 결정(6), 파생 에이전트 문서(8)에
   영향을 줄 수 있다.
5. current task의 방향이 기존 원천 문서(2)와 충돌한다.
6. main이 추론으로 진행하면 잘못된 feature, workflow, policy, acceptance criteria를 만들
   위험이 있다.

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
6. 구현 코드 수정이나 테스트 실행 자체

<!-- key: id=key.standard.skill.clarify.topic-boundary refs=key.role.clarify key.doc.decision key.topic.question-flow -->
## Topic boundary

Clarify는 한 번에 하나의 topic을 다룬다.

1. 좋은 topic: document root policy, Git policy, Reader trigger boundary,
   output language policy, skill-specific non-trigger condition
2. 나쁜 topic: "Keystone 전체를 어떻게 할까요"처럼 여러 정책을 한 번에 묶은 질문
3. Topic이 너무 크면 main은 하위 topic으로 나누어 질문한다.
4. 같은 topic 안에서는 충분한 정보가 모일 때까지 필요한 follow-up을 이어갈 수 있다.
5. Topic이 충분히 결정되면 다음 topic으로 넘어가기 전에 reflection과 update plan을
   요약한다.

<!-- key: id=key.standard.skill.clarify.plan-mode-contract refs=key.role.clarify key.topic.question-flow key.doc.decision -->
## Plan Mode contract

Plan Mode는 질문과 결정을 수집하는 mode다.

1. 사용 가능한 경우 `request_user_input` 또는 동등한 selection UI를 사용한다.
2. 한 번에 하나의 focused question을 묻는다.
3. 질문은 선택지의 tradeoff를 짧게 설명해야 한다.
4. 사용자가 답하면 해당 답이 topic을 결정하기에 충분한지 판단한다.
5. 충분하지 않으면 같은 topic에 대해 targeted follow-up을 묻는다.
6. 충분하면 decision summary와 working assumptions를 만든다.
7. Plan Mode는 원천 문서(2)를 직접 수정하지 않는다.

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
   - `STD-KEYSTONE-020`의 조건을 만족하는 파생 에이전트 문서(8)
3. Clarify 직접 수정 허용:
   - 명시 승인된 현재 대상 문서 안의 단순 오탈자
   - 다른 문서, 기준서(3), 작업서(4), scope, acceptance criteria, status semantics에 영향이
     없는 단순 오탈자 수정
4. 금지:
   - 수락되지 않은 topic을 근거로 문서 수정
   - 다른 문서와 함께 맞춰야 하는 원천 문서(2) 수정
   - 기준, 정책, scope, acceptance criteria, status semantics처럼 다른 문서와 함께 맞춰야
     하는 변경 직접 수정
   - implementation code 수정
   - 승인되지 않은 scope 또는 acceptance criteria 변경
   - common/global instruction file에 setup result 기록

<!-- key: id=key.standard.skill.clarify.reflection-edit-plan refs=key.role.clarify key.output.edit-plan key.doc.decision -->
## Reflection and edit plan

Clarify result는 다음을 포함해야 한다.

1. `topic`: 결정한 주제
2. `decision_summary`: 사용자가 수락한 결정(6)
3. `rationale`: 주요 이유와 tradeoff
4. `working_assumptions`: 이후 작업에서 사용할 가정
5. `affected_documents`: 업데이트가 필요한 원천 문서(2)
6. `edit_plan`: 문서별 변경 요약
7. `stop_conditions`: 적용 중 중단해야 하는 조건
8. `open_questions`: 이번 topic 밖에 남은 질문

<!-- key: id=key.standard.skill.clarify.impact-update refs=key.role.clarify key.topic.impact-review key.output.edit-plan -->
## Impact update

수락된 clarify result가 문서에 반영될 때는 다음 규칙을 따른다.

1. 관련 parent 기준서와 child 기준서가 함께 영향을 받으면 `keystone-author`가 둘 다
   검토할 수 있게 edit plan에 포함한다.
2. 작업서(4)의 scope, completion criteria, status semantics에 영향을 주면 명시적으로
   보고한다.
3. 진행 기록(5)은 main acceptance 없이 완료 상태로 바꾸지 않는다.
4. 결정(6)은 장기 정책이나 여러 문서에 영향을 주는 경우에 기록한다.
5. 파생 에이전트 문서(8)는 이미 존재하고 명확히 영향받을 때만 edit plan에 포함한다. 새로
   생성하는 경우는 `STD-KEYSTONE-020`의 명시적 필요 조건을 따른다.
6. 키스톤 메타데이터(9)가 있는 topic이나 문서가 관련되면 같은 `key.id`를 참조하는 문서를
   affected document 후보로 검토한다.
7. 같은 `key.refs`가 있어도 자동으로 edit plan에 포함하지 않는다.
8. `key.refs`가 없어도 관련 없음으로 단정하지 않는다.
9. 영향 범위가 불확실하면 문서 수정을 멈추고 사용자 또는 main 결정(6)을 요청한다.

<!-- key: id=key.standard.skill.clarify.initial-setup-question-contract refs=key.role.clarify key.topic.question-flow key.topic.document-system -->
## Initial setup question contract

Target project에서 Keystone setting이 없거나 불명확하면 Clarify는 initial setup question을
다룰 수 있다.

1. 질문 대상:
   - document root
   - 기준서(3)와 작업서(4) Git policy
   - 파생 에이전트 문서(8) Git policy
   - Keystone output language policy
   - setup storage location
2. 기본 storage:
   - shared setting은 `.keystone/config.yaml`
   - personal, local-only, sensitive override는 `.keystone/config.local.yaml`
3. 금지:
   - common/global instruction file에 조용히 기록하기
   - 이 Keystone implementation repository에 S01/S02 동안 config가 필요하다고 암시하기
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
7. Implementation, schema, auth/security, generated/codegen, publishing decision이
   먼저 필요하다.

<!-- key: id=key.standard.skill.clarify.verification refs=key.role.clarify key.topic.verification key.output.edit-plan -->
## Verification

Clarify 기준은 다음 방법으로 검증한다.

1. Clarify contract만 보고 trigger와 non-trigger를 구분할 수 있어야 한다.
2. Plan Mode와 Default Mode의 책임 차이가 명확해야 한다.
3. 수락 전에는 원천 문서(2)를 수정하지 않는다는 경계가 명확해야 한다.
4. Reflection과 edit plan만 보고 Author가 문서 update 범위를 판단할 수 있어야 한다.
5. Initial setup question이 `STD-KEYSTONE-026`, `STD-KEYSTONE-027`,
   `STD-KEYSTONE-028`과 일관되어야 한다.
6. Metadata 기반 affected document 후보가 있으면 edit plan에서 후보와 실제 반영 여부를
   구분할 수 있어야 한다.
7. Verification command:
   - `rg --files 00_docs`
   - Clarify 관련 기준서를 읽어 link와 scope consistency 확인
