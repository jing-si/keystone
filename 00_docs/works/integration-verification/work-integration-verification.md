# Integration Verification 작업서(4)

## Goal

문서와 네 개 skill source가 하나의 Keystone workflow로 이어지는지 검증한다.

## Scope

Include:

- Reader가 active work와 관련 기준서를 찾을 수 있는지 확인
- Clarify result를 Author가 적용할 수 있는지 확인
- Author가 만든 work step을 Coordinator가 복구할 수 있는지 확인
- Coordinator가 Current Step Brief, Context Pack, review/verification focus를 도출할 수
  있는지 확인

Exclude:

- real publishing
- global install
- unrelated repository cleanup
- browser or Playwright verification

Conditionally allowed:

- 문서 기반 simulation
- 필요성이 확인된 작은 fixture. 생성 전 위치와 범위를 보고한다.

## Source Context

- `00_docs/context-map.md`
- `00_docs/standards/00_project-standard.md`
- `00_docs/standards/skills/00_index.md`
- `00_docs/works/00_index.md`
- repo-local `skills/` source

## Completion Criteria

- [ ] Reader, Author, Clarify, Coordinator가 같은 source document model을 사용한다.
- [ ] 각 skill의 output이 다음 skill의 input으로 연결될 수 있다.
- [ ] Coordinator가 현재 work step을 복구할 수 있다.
- [ ] 검증 결과와 남은 risk가 기록된다.

## Recommended Approach

처음에는 문서 기반 simulation으로 시작한다. 실제 fixture나 install 검증은 필요성이 확인되고
scope가 승인된 뒤 추가한다.

## Context Pack Seed

- 네 개 skill source
- S01-S05 기준서
- 현재 work order와 progress
- 검증할 workflow sequence

## Stop Conditions

- Skill source가 아직 생성되지 않았다.
- 문서와 skill source가 서로 다른 trigger 또는 output contract를 가진다.
- fixture나 install 검증이 필요하지만 승인되지 않았다.

## Verification

Allowed:

- `rg --files 00_docs skills`
- skill file과 기준서 cross-read
- 문서 기반 workflow simulation

Forbidden until explicitly allowed:

- global install
- package publish
- Playwright/browser verification

## Expected Output

- 통합 검증 결과
- 수정이 필요한 기준서 또는 skill source 목록
- 다음 단계가 필요하면 S08 후보 제안

## Review Points

- 네 skill이 서로 책임을 침범하지 않는지 확인한다.
- 문서에서 current step과 verification path를 복구할 수 있는지 확인한다.

## Progress Record

S07 완료는 main acceptance 후에만 `progress.md`에 기록한다.
