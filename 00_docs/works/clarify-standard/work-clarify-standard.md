# Clarify Standard 작업서(4)

## Goal

`keystone-clarify`의 topic-scoped decision collection, reflection, edit plan, Author
handoff 계약을 정리한다.

## Scope

Include:

- high-impact topic trigger
- Plan Mode와 Default Mode
- reflection과 edit plan
- initial setup question boundary
- 단순 오탈자 직접 수정 예외

Exclude:

- 넓은 문서 수정
- 기준서(3)나 작업서(4) 직접 작성
- implementation code

Conditionally allowed:

- Author handoff와 관련된 좁은 cross-reference 보정

## Source Context

- `00_docs/standards/00_project-standard.md`
- `00_docs/standards/skills/clarify/00_index.md`
- `00_docs/standards/skills/clarify/standard-clarify.md`

## Completion Criteria

- [ ] Clarify가 한 번에 하나의 topic을 다룬다는 점이 명확하다.
- [ ] 수락된 decision summary와 edit plan을 Author가 적용한다는 경계가 명확하다.
- [ ] 직접 수정 예외가 단순 오탈자로 제한된다.
- [ ] setup question이 common/global instruction file에 쓰도록 유도하지 않는다.

## Recommended Approach

Clarify는 결정 수집과 적용 계획에 집중한다. 문서 반영은 Author 책임으로 남긴다.

## Context Pack Seed

- `STD-KEYSTONE-025`
- Source authority rule
- Author handoff boundary

## Stop Conditions

- topic이 여러 high-impact 결정을 동시에 포함한다.
- 변경 대상 문서나 승인 범위가 불명확하다.
- Clarify가 Author의 문서 작성 책임을 가져야 할 것처럼 보인다.

## Verification

Allowed:

- `rg -n "Plan Mode|Default Mode|Author handoff" 00_docs/standards/skills/clarify/standard-clarify.md`
- `git diff --check`

## Expected Output

- 현재 문서 체계와 일치하는 Clarify 기준서

## Review Points

- Clarify가 Author 책임을 침범하지 않는지 확인한다.
- 질문 흐름이 한 topic씩 진행되는지 확인한다.

## Progress Record

S04 완료는 main acceptance 후에만 `progress.md`에 기록한다.
