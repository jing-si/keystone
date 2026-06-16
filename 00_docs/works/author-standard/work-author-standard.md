# Author Standard 작업서(4)

## Goal

`keystone-author`의 문서 작성/수정 계약과 작업서 생성 표준을 정리한다.

## Scope

Include:

- Create, Revise, Clarify-Apply, Normalize, Progress Update mode
- 기준서(3) 작성 규칙
- 작업서(4) 생성 표준
- index와 progress update boundary
- approval boundary와 source edit gate

Exclude:

- high-impact decision collection
- implementation code
- persistent handoff 기본 생성

Conditionally allowed:

- 작업서 생성 표준을 반영하기 위한 `works/00_index.md` link 보정

## Source Context

- `00_docs/standards/00_project-standard.md`
- `00_docs/standards/skills/author/00_index.md`
- `00_docs/standards/skills/author/standard-author.md`
- `00_docs/works/decisions.md`

## Completion Criteria

- [ ] Author가 새 작업서를 `works/` tree에 만든다는 점이 명확하다.
- [ ] 작업서가 기준서 구조에 종속되지 않는다는 표준이 명확하다.
- [ ] 작업 순서는 기준서가 아니라 `works/00_index.md`나 상위 work plan이 관리한다.
- [ ] progress update가 main acceptance와 worker report를 혼동하지 않는다.
- [ ] Clarify와 Author의 책임 경계가 명확하다.

## Recommended Approach

Author 기준서는 문서 작성 책임에 집중한다. Clarify 질문 수집이나 Coordinator runtime flow는
가져오지 않는다.

## Context Pack Seed

- `STD-KEYSTONE-029`
- `DEC-WORKS-002`
- Source edit gate와 approval boundary

## Stop Conditions

- 승인 없이 scope, acceptance criteria, status semantics를 바꿔야 한다.
- Author가 code/schema/generated output을 수정해야 한다.
- 작업서 생성 표준이 기준서 실행 순서를 고정하게 만든다.

## Verification

Allowed:

- `rg -n "작업서 생성|works/00_index|기준서 구조" 00_docs/standards/skills/author/standard-author.md`
- `git diff --check`

## Expected Output

- 작업서 생성 표준이 포함된 Author 기준서

## Review Points

- Author가 approved source document edit만 수행하도록 제한되는지 확인한다.
- 작업서 생성 위치와 순서 관리 위치가 분리되어 있는지 확인한다.

## Progress Record

S03 완료는 main acceptance 후에만 `progress.md`에 기록한다.
