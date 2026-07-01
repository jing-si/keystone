---
doc_type: work_order
key:
  id: key.work.clarify-standard.order
  refs:
    - key.doc.work
    - key.role.clarify
    - key.topic.decision-collection
    - key.output.edit-plan
    - key.topic.author-handoff
---

# Clarify Standard 작업서(4)

<!-- key: id=key.work.clarify-standard.order.goal refs=key.role.clarify key.topic.decision-collection key.topic.reflection key.output.edit-plan key.topic.author-handoff -->

## Goal

`keystone-clarify`의 topic-scoped decision collection, reflection, edit plan, Author
handoff 계약을 정리한다.

<!-- key: id=key.work.clarify-standard.order.scope refs=key.role.clarify key.section.scope key.mode.plan key.mode.default key.boundary.direct-edit-exception -->

## Scope

Include:

- high-impact topic trigger
- Plan Mode와 Default Mode
- reflection과 edit plan
- decision recording hint
- initial setup question boundary
- 단순 오탈자 직접 수정 예외

Exclude:

- Clarify runtime 책임으로 넓은 문서 수정을 수행하게 만들기
- Clarify runtime 책임으로 기준서(3)나 작업서(4)를 직접 작성하게 만들기
- Clarify runtime 책임으로 implementation code, config, schema, API, test,
  generated/codegen artifact를 수정하게 만들기

Conditionally allowed:

- Author handoff와 관련된 좁은 cross-reference 보정

<!-- key: id=key.work.clarify-standard.order.source-context refs=key.section.source-context key.role.clarify key.doc.standard -->

## Source Context

- `00_docs/standards/01_key-project-standard.md`
- `00_docs/standards/skills/author/key-standard-author.md`
- `00_docs/standards/skills/clarify/00_key-index.md`
- `00_docs/standards/skills/clarify/key-standard-clarify.md`

<!-- key: id=key.work.clarify-standard.order.completion-criteria refs=key.topic.acceptance key.role.clarify key.topic.topic-scope key.output.edit-plan key.topic.author-handoff -->

## Completion Criteria

- [ ] Clarify가 한 번에 하나의 topic을 다룬다는 점이 명확하다.
- [ ] 수락된 decision summary와 edit plan을 Author가 적용한다는 경계가 명확하다.
- [ ] `decision_completeness_check`가 선택/기각 옵션, 영향 문서와 artifact, acceptance 또는
      status 영향, 기록 범위와 사유, Author 적용 가능 여부를 드러낸다.
- [ ] affected artifact 후보 범위가 capability, code, config, schema, API, test를 포함한다.
- [ ] decision recording hint가 global, round, work 범위별 기록 위치 또는 none/unresolved 상태를
      표현하되 기록 권한으로 해석되지 않는다.
- [ ] Author Clarify-Apply 입력이 `decision_recording_hint`를 포함한다.
- [ ] decision recording hint가 Clarify result의 조건부 필수 output으로 연결되어 있다.
- [ ] 불충분한 답변은 `author_edit_ready: false`, unresolved `open_questions`, Author-ready
      `edit_plan` 없음으로 보고된다.
- [ ] `open_questions`가 current-topic unresolved 질문과 out-of-topic 질문을 구분한다.
- [ ] `decision_completeness_check`와 `decision_recording_hint`가 `none`과 `unresolved` 기록
      상태를 표현할 수 있다.
- [ ] `affected_documents`가 update target, inspect-only 후보, excluded 후보를 최소 shape로
      구분한다.
- [ ] 직접 수정 예외가 단순 오탈자로 제한된다.
- [ ] setup question이 common/global instruction file에 쓰도록 유도하지 않는다.
- [ ] Clarify가 `.keystone/config.yaml` 또는 `.keystone/config.local.yaml`을 직접 생성하거나
      수정하지 않는다는 경계가 명확하다.
- [ ] fixture/test step 또는 명시적인 project-local setup 요구 없이 implementation repository에
      `.keystone/config.yaml`이 필요하다고 암시하거나 생성하지 않는다.
- [ ] stop condition이 Clarify topic을 넘는 artifact 수정 또는 실행 결정으로 좁혀져 있다.

<!-- key: id=key.work.clarify-standard.order.recommended-approach refs=key.section.recommended-approach key.role.clarify key.topic.decision-collection key.topic.author-handoff -->

## Recommended Approach

Clarify는 결정 수집과 적용 계획에 집중한다. 문서 반영은 Author 책임으로 남긴다.

<!-- key: id=key.work.clarify-standard.order.context-pack-seed refs=key.output.context-pack key.standard.project.std-keystone-041 key.topic.source-authority key.topic.author-handoff -->

## Context Pack Seed

- `STD-KEYSTONE-041`
- Source authority rule
- Author handoff boundary
- decision completeness check
- decision recording hint

<!-- key: id=key.work.clarify-standard.order.stop-conditions refs=key.section.stop-conditions key.topic.topic-scope key.boundary.approval key.topic.author-handoff -->

## Stop Conditions

- topic이 여러 high-impact 결정을 동시에 포함한다.
- 변경 대상 문서나 승인 범위가 불명확하다.
- 결정 기록 위치가 불명확한데 Clarify가 직접 기록해야 할 것처럼 보인다.
- Clarify가 Author의 문서 작성 책임을 가져야 할 것처럼 보인다.

<!-- key: id=key.work.clarify-standard.order.verification refs=key.topic.verification key.role.clarify key.topic.standard-verification -->

## Verification

Allowed:

- `rg -n "Plan Mode|Default Mode|Author handoff" 00_docs/standards/skills/clarify/key-standard-clarify.md`
- `rg -n "decision_completeness_check|author_edit_ready|acceptance_or_status_impact" 00_docs/standards/skills/clarify/key-standard-clarify.md`
- `rg -n "capability, code, config, schema, API, test|config, schema" 00_docs/standards/skills/clarify/key-standard-clarify.md`
- `rg -n "decision_recording_hint|recommended_path|requires_author_update" 00_docs/standards/skills/clarify/key-standard-clarify.md`
- `rg -n "decision_recording_hint|decision_completeness_check|Clarify-Apply" 00_docs/standards/skills/author/key-standard-author.md`
- `rg -n "author_edit_ready: false|open_questions|Author-ready" 00_docs/standards/skills/clarify/key-standard-clarify.md`
- `rg -n "unresolved_current_topic|out_of_topic" 00_docs/standards/skills/clarify/key-standard-clarify.md`
- `rg -n "recording_scope: global|recording_reason|scope: global|none|unresolved" 00_docs/standards/skills/clarify/key-standard-clarify.md`
- `rg -n "update_targets|inspect_only_candidates|excluded|required_change" 00_docs/standards/skills/clarify/key-standard-clarify.md`
- `rg -n "\\.keystone/config.yaml|\\.keystone/config.local.yaml|필요하다고 암시하거나 해당 파일을 생성하기|직접 생성하거나 수정하지 않는다" 00_docs/standards/skills/clarify/key-standard-clarify.md`
- `rg -n "Clarify topic을 넘는|artifact 수정|publishing 실행 결정" 00_docs/standards/skills/clarify/key-standard-clarify.md`
- Clarify 기준서와 Project Standard, Author 기준서의 trigger/non-trigger, handoff consistency 확인

<!-- key: id=key.work.clarify-standard.order.expected-output refs=key.contract.output key.role.clarify key.doc.standard -->

## Expected Output

- 현재 문서 체계와 일치하는 Clarify 기준서

<!-- key: id=key.work.clarify-standard.order.review-points refs=key.section.review-points key.role.clarify key.topic.responsibility-boundary key.topic.question-flow -->

## Review Points

- Clarify가 Author 책임을 침범하지 않는지 확인한다.
- 질문 흐름이 한 topic씩 진행되는지 확인한다.
- decision recording hint가 Author handoff 후보로만 남는지 확인한다.

<!-- key: id=key.work.clarify-standard.order.progress-record refs=key.topic.progress-update key.topic.main-acceptance key.step.s04 -->

## Progress Record

S04 완료는 main acceptance 후에만 `key-progress.md`에 기록한다.
