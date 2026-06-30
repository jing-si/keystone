---
doc_type: work_order
key:
  id: key.work.skill-creation.order
  refs:
    - key.doc.work
    - key.topic.skill-source
    - key.topic.skill-contract
    - key.topic.implementation
    - key.topic.repo-local
---

# Skill Creation 작업서(4)

<!-- key: id=key.work.skill-creation.order.goal refs=key.topic.skill-source key.topic.repo-local key.artifact.skill-md key.section.goal -->

## Goal

수락된 기준서에 맞춰 다섯 개 Keystone skill source를 repo-local `skills/` 아래에 생성한다.

<!-- key: id=key.work.skill-creation.order.scope refs=key.topic.skill-source key.section.scope key.artifact.skill-md key.topic.repo-local key.boundary.publish-forbidden key.boundary.install-forbidden -->

## Scope

Include:

- `skills/keystone-reader/SKILL.md`
- `skills/keystone-author/SKILL.md`
- `skills/keystone-clarify/SKILL.md`
- `skills/keystone-linker/SKILL.md`
- `skills/keystone-coordinator/SKILL.md`
- 필요한 경우 작은 reference file
- 공통 `SKILL.md` skeleton과 skill별 source document link

Exclude:

- package publishing
- marketplace registration
- global install
- prototype skill rewrite
- broad code generation
- S01-S07 acceptance 없이 S08 완료 처리

Conditionally allowed:

- skill file이 기준서로 돌아갈 수 있게 하는 link 또는 reference
- 사용자가 명시적으로 draft를 요청하면 current 기준서 기반 draft skill source를 만들 수 있다. 이
  경우 S08 완료나 accepted 처리로 보지 않고 `DONE_WITH_CONCERNS` 성격의 residual risk를 남긴다.

<!-- key: id=key.work.skill-creation.order.source-context refs=key.section.source-context key.topic.accepted-standard key.topic.child-standard key.topic.skill-standard -->

## Source Context

- S01-S07에서 수락된 기준서
- `00_docs/standards/01_key-project-standard.md`
- `00_docs/standards/artifacts/key-standard-artifact-graph.md`
- 각 skill별 child 기준서
- Skill creator guidance 또는 현재 platform의 skill format 규칙

<!-- key: id=key.work.skill-creation.order.completion-criteria refs=key.topic.acceptance key.topic.skill-directory key.artifact.skill-md key.boundary.trigger key.topic.prototype-dependency -->

## Completion Criteria

- [ ] 다섯 개 skill directory가 존재한다.
- [ ] 각 `SKILL.md`는 해당 child 기준서와 일치한다.
- [ ] 각 `SKILL.md`는 `name`과 `description` frontmatter를 가진다.
- [ ] Skill description은 trigger/non-trigger 경계를 드러낸다.
- [ ] 각 `SKILL.md`는 공통 skeleton의 핵심 section을 가진다.
- [ ] 각 `SKILL.md`는 해당 skill의 최소 output example 또는 YAML field shape를 가진다.
- [ ] Linker가 artifact graph, impact candidate, stale candidate 책임을 가진다.
- [ ] Coordinator가 worker assignment와 worker report를 다룬다.
- [ ] Coordinator가 single workspace bounded worker model을 따른다.
- [ ] Coordinator가 외부 코딩 스킬을 runtime dependency가 아니라 injected skill contract로 다룬다.
- [ ] Prototype skill을 runtime dependency로 삼지 않는다.

공통 `SKILL.md` skeleton은 다음 section을 우선 사용한다.

```markdown
# keystone-{skill-name}

## Purpose

## Required Source Documents

## When To Use

## When Not To Use

## Required Input

## Workflow

## Output Contract

## Output Examples

## Boundaries

## Stop Conditions

## Verification

## Related Source Documents
```

`When To Use`와 `When Not To Use`는 body에도 두되, 실제 trigger 품질을 위해 frontmatter
`description`에도 핵심 trigger와 non-trigger 경계를 요약한다.

<!-- key: id=key.work.skill-creation.order.recommended-approach refs=key.section.recommended-approach key.topic.accepted-standard key.output.context-pack key.topic.bounded-worker -->

## Recommended Approach

S01-S07이 accepted된 뒤 진행한다. Main이 직접 작은 skill files를 만들거나, 명확한
Context Pack을 준비한 뒤 bounded worker에게 위임할 수 있다.

<!-- key: id=key.work.skill-creation.order.context-pack-seed refs=key.output.context-pack key.topic.accepted-standard key.topic.target-path key.boundary.external-skill-forbidden key.topic.read-check -->

## Context Pack Seed

- 수락된 S01-S07 기준서
- target file path
- 공통 `SKILL.md` skeleton
- external installed skill 수정 금지
- external coding skill injected skill boundary
- verification file read check

<!-- key: id=key.work.skill-creation.order.stop-conditions refs=key.section.stop-conditions key.topic.accepted-standard key.topic.skill-source-location key.boundary.publish-forbidden key.boundary.install-forbidden -->

## Stop Conditions

- S01-S07 기준서가 accepted되지 않았다.
- skill source 위치가 불명확하다.
- publish/install 요구가 생긴다.

<!-- key: id=key.work.skill-creation.order.verification refs=key.topic.verification key.topic.skill-source key.topic.read-check key.boundary.install-forbidden key.boundary.publish-forbidden -->

## Verification

Allowed:

- `rg --files skills`
- `rg -n "^name:|^description:" skills/*/SKILL.md`
- `rg -n "## Purpose|## Workflow|## Output Contract|## Output Examples|## Stop Conditions|## Verification" skills/*/SKILL.md`
- 생성된 `SKILL.md` 읽기

Forbidden until explicitly allowed:

- global skill install
- marketplace publish

<!-- key: id=key.work.skill-creation.order.expected-output refs=key.contract.output key.topic.skill-source key.topic.repo-local key.artifact.skill-md -->

## Expected Output

- repo-local `skills/` 아래 다섯 개 Keystone skill source

<!-- key: id=key.work.skill-creation.order.review-points refs=key.section.review-points key.topic.responsibility-boundary key.role.reader key.role.author key.role.clarify key.role.linker key.role.coordinator -->

## Review Points

- 각 skill이 자신의 기준서 책임만 포함하는지 확인한다.
- Reader, Author, Clarify, Linker, Coordinator 사이 책임이 섞이지 않는지 확인한다.
- Coordinator skill source가 외부 코딩 스킬을 Coordinator replacement로 설명하지 않는지 확인한다.
- Prototype skill이나 외부 installed skill이 Keystone runtime dependency로 굳어지지 않는지
  확인한다.

<!-- key: id=key.work.skill-creation.order.progress-record refs=key.topic.progress-update key.topic.main-acceptance key.step.s08 -->

## Progress Record

S08 완료는 main acceptance 후에만 `key-progress.md`에 기록한다.
