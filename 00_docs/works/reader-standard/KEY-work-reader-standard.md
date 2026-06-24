# Reader Standard 작업서(4)

## Goal

`keystone-reader`의 trigger, mode, output, read-only boundary를 구현 가능한 기준으로
정리한다.

## Scope

Include:

- Orientation, Navigator, Work Prep mode
- active work 탐색
- repository snapshot과 mismatch reporting
- output contract
- stop condition과 verification

Exclude:

- 문서 수정
- subagent assignment 확정
- Skill source 생성

Conditionally allowed:

- Parent 기준서와의 좁은 충돌 보정

## Source Context

- `00_docs/standards/00_KEY-project-standard.md`
- `00_docs/standards/skills/reader/00_KEY-index.md`
- `00_docs/standards/skills/reader/KEY-standard-reader.md`
- `00_docs/works/00_KEY-index.md`

## Completion Criteria

- [ ] Reader trigger와 non-trigger가 명확하다.
- [ ] 세 mode의 입력, 읽기 범위, output field가 명확하다.
- [ ] Reader가 원천 문서(2)를 수정하지 않는다는 경계가 명확하다.
- [ ] `works/` tree에서 current work를 찾는 흐름이 명확하다.

## Recommended Approach

기존 Reader 기준서를 현재 works tree 기준으로 검토한다. 구현은 S06에서 진행한다.

## Context Pack Seed

- `STD-KEYSTONE-019`
- Reader child 기준서
- active work index

## Stop Conditions

- Reader가 Author 또는 Coordinator 책임을 가져야만 설명이 가능하다.
- 민감한 local-only 문서를 읽어야 한다.

## Verification

Allowed:

- `rg -n "work-packages|legacy|works" 00_docs/standards/skills/reader`
- `git diff --check`

## Expected Output

- 현재 works tree와 일치하는 Reader 기준서

## Review Points

- Reader output이 원천 문서를 대체하지 않는지 확인한다.
- Work Prep Mode가 final handoff 확정으로 넘어가지 않는지 확인한다.

## Progress Record

S02 완료는 main acceptance 후에만 `KEY-progress.md`에 기록한다.
