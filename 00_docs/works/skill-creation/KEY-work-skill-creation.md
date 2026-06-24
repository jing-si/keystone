---
doc_type: work_order
tags:
  - 작업서
  - skill-source
  - 스킬계약
  - 구현
  - repo-local
---

# Skill Creation 작업서(4)

<!-- tags: skill-source, repo-local, SKILL.md, 목표 -->

## Goal

수락된 기준서에 맞춰 네 개 Keystone skill source를 repo-local `skills/` 아래에 생성한다.

<!-- tags: skill-source, 범위, SKILL.md, repo-local, publish-forbidden, install-forbidden -->

## Scope

Include:

- `skills/keystone-reader/SKILL.md`
- `skills/keystone-author/SKILL.md`
- `skills/keystone-clarify/SKILL.md`
- `skills/keystone-coordinator/SKILL.md`
- 필요한 경우 작은 reference file

Exclude:

- package publishing
- marketplace registration
- global install
- prototype skill rewrite
- broad code generation

Conditionally allowed:

- skill file이 기준서로 돌아갈 수 있게 하는 link 또는 reference

<!-- tags: source-context, accepted-standard, child-standard, 스킬기준서 -->

## Source Context

- S01-S05에서 수락된 기준서
- `00_docs/standards/00_KEY-project-standard.md`
- 각 skill별 child 기준서

<!-- tags: acceptance, skill-directory, SKILL.md, trigger-boundary, prototype-dependency -->

## Completion Criteria

- [ ] 네 개 skill directory가 존재한다.
- [ ] 각 `SKILL.md`는 해당 child 기준서와 일치한다.
- [ ] Skill description은 trigger/non-trigger 경계를 드러낸다.
- [ ] Prototype skill을 runtime dependency로 삼지 않는다.

<!-- tags: 접근방식, accepted-standard, context-pack, bounded-worker -->

## Recommended Approach

S01-S05가 accepted된 뒤 진행한다. Main이 직접 작은 skill files를 만들거나, 명확한
Context Pack을 준비한 뒤 bounded worker에게 위임할 수 있다.

<!-- tags: context-pack, accepted-standard, target-path, external-skill-forbidden, read-check -->

## Context Pack Seed

- 수락된 S01-S05 기준서
- target file path
- external installed skill 수정 금지
- verification file read check

<!-- tags: stop-condition, accepted-standard, skill-source-location, publish-forbidden, install-forbidden -->

## Stop Conditions

- S01-S05 기준서가 accepted되지 않았다.
- skill source 위치가 불명확하다.
- publish/install 요구가 생긴다.

<!-- tags: verification, skill-source, read-check, install-forbidden, publish-forbidden -->

## Verification

Allowed:

- `rg --files skills`
- 생성된 `SKILL.md` 읽기

Forbidden until explicitly allowed:

- global skill install
- marketplace publish

<!-- tags: output-contract, skill-source, repo-local, SKILL.md -->

## Expected Output

- repo-local `skills/` 아래 네 개 Keystone skill source

<!-- tags: review-point, 책임경계, reader, author, clarify, coordinator -->

## Review Points

- 각 skill이 자신의 기준서 책임만 포함하는지 확인한다.
- Reader, Author, Clarify, Coordinator 사이 책임이 섞이지 않는지 확인한다.

<!-- tags: progress-update, main-acceptance, S06 -->

## Progress Record

S06 완료는 main acceptance 후에만 `KEY-progress.md`에 기록한다.
