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
- `00_docs/standards/subagents/key-standard-subagents.md`
- 각 skill별 child 기준서
- Skill creator guidance 또는 현재 platform의 skill format 규칙

<!-- key: id=key.work.skill-creation.order.completion-criteria refs=key.topic.acceptance key.topic.skill-directory key.artifact.skill-md key.boundary.trigger key.topic.prototype-dependency -->

## Completion Criteria

- [ ] 다섯 개 skill directory가 존재한다.
- [ ] 각 `SKILL.md`는 해당 child 기준서와 일치한다.
- [ ] 각 `SKILL.md`는 `name`과 `description` frontmatter를 가진다.
- [ ] Skill description은 trigger/non-trigger 경계를 드러낸다.
- [ ] Skill source output artifact는 원천 문서(2)가 intended behavior와 policy의 권위라는 공통
      경계를 포함한다.
- [ ] `keystone-author`는 repo-local `SKILL.md` 구현 파일 작성자로 설명되지 않는다.
- [ ] 각 `SKILL.md`는 공통 skeleton의 핵심 section을 가진다.
- [ ] 각 `SKILL.md`는 해당 skill의 최소 output example 또는 YAML field shape를 가진다.
- [ ] Reader output example은 `keystone_context_brief`, `recommended_next_action`,
      `final_handoff_ready: false`를 포함한다.
- [ ] Clarify output example은 `decision_completeness_check`, `decision_recording_hint`,
      `affected_documents`, `open_questions`를 포함한다.
- [ ] Linker output example은 `linker_report`, `source_surface_handoffs`,
      `graph_interpretation`, `graph_owner_note`, `candidate_budget`을 포함한다.
- [ ] Coordinator output example은 `worker_assignment`, non-empty `injected_skills`,
      `worker_report`, `worker_report_review`를 포함한다.
- [ ] Linker가 artifact graph, impact candidate, stale candidate 책임을 가진다.
- [ ] Coordinator가 worker assignment와 worker report를 다룬다.
- [ ] Coordinator가 single workspace bounded worker model을 따른다.
- [ ] Coordinator가 외부 코딩 스킬을 runtime dependency가 아니라 injected skill contract로 다룬다.
- [ ] 각 `SKILL.md`는 기본 사용자 응답과 agent-facing structured payload를 구분한다.
- [ ] Full structured payload는 사용자 요청, handoff, audit/debug, verification evidence에
      필요할 때만 노출한다고 설명한다.
- [ ] Optional `keystone-viewer`는 presentation/helper 후보로만 언급하며 다섯 core skill의
      mandatory runtime dependency로 만들지 않는다.
- [ ] 다섯 개 `SKILL.md`는 S08 작업서와 각 skill 기준서가 만드는 `output_artifact`로 해석된다.
- [ ] Linker는 `skill_source`를 특별한 graph 핵심 개념으로 보지 않고 output artifact surface로
      취급한다.
- [ ] File-changing work는 수정 전 `keystone_routing_decision`을 요구한다.
- [ ] `00_docs/**` source document 변경은 Author lane과 `author_patch_report`를 요구한다.
- [ ] `skills/keystone-*/SKILL.md` 변경은 Main direct lane의 `main_direct_change_report` 또는
      Coordinator lane의 worker assignment/report를 요구한다.
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

## Routing Gate

## Default User Response

## Output Contract

## Output Examples

## Boundaries

## Stop Conditions

## Verification

## Related Source Documents
```

`When To Use`와 `When Not To Use`는 body에도 두되, 실제 trigger 품질을 위해 frontmatter
`description`에도 핵심 trigger와 non-trigger 경계를 요약한다.

생성 지침은 다음을 따른다.

1. 각 `description`은 해당 스킬의 trigger와 non-trigger를 함께 요약한다.
2. 모든 `SKILL.md`는 원천 문서(2)와 수락된 결정(6)이 source of truth이며, skill output은
   Main/user acceptance를 대체하지 않는다고 명시한다.
3. 기준서와 skill source가 충돌하면 기준서를 임시 권위로 두고 Main/user decision을 요청하도록
   쓴다.
4. `keystone-author`는 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 기록, Change Set(17)을
   작성하거나 수정하는 스킬로 설명하고, repo-local `skills/*/SKILL.md` 구현 파일 작성은 S08의
   Main 직접 작업 또는 Coordinator bounded worker 작업으로 구분한다.
5. `keystone-linker`는 Artifact Graph의 operational interpretation owner이지만 source edit
   authority가 없다는 점을 반복한다.
6. `keystone-coordinator`는 외부 코딩 스킬(12)을 runtime dependency나 replacement가 아니라
   `injected_skills` entry로만 설명한다.
7. File-changing work로 전환되면 Main이 `keystone_routing_decision`을 먼저 남긴 뒤 target
   surface에 맞는 lane과 report를 사용해야 한다고 설명한다.

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
- Keystone routing decision
- Source document to output artifact relation
- Main direct skill source report boundary
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
- `test -f skills/keystone-reader/SKILL.md`
- `test -f skills/keystone-author/SKILL.md`
- `test -f skills/keystone-clarify/SKILL.md`
- `test -f skills/keystone-linker/SKILL.md`
- `test -f skills/keystone-coordinator/SKILL.md`
- `rg -n "^name:|^description:" skills/*/SKILL.md`
- `rg -n "## Purpose|## Required Source Documents|## When To Use|## When Not To Use|## Required Input|## Workflow|## Routing Gate|## Output Contract|## Output Examples|## Boundaries|## Stop Conditions|## Verification|## Related Source Documents" skills/*/SKILL.md`
- `rg -n "source of truth|source documents|Main acceptance|does not replace" skills/*/SKILL.md`
- `rg -n "work-package-doc-architect|subagent-work-coordinator|marketplace|global install|publish|package publishing" skills || true`
- `rg -n "read-only|does not modify|directly modify|Main acceptance|source documents" skills/*/SKILL.md`
- `rg -n "keystone-default-bounded-worker|injected_skills|single_workspace|worker_assignment|worker_report" skills/keystone-coordinator/SKILL.md`
- `rg -n "linker_report|source_surface_handoffs|graph_interpretation|graph_owner_note|candidate_budget|metadata_gaps|stale_candidates" skills/keystone-linker/SKILL.md`
- `rg -n "output_artifact|produced_from|produces|artifact_kind" 00_docs/standards 00_docs/works skills`
- `rg -n "Default User Response|structured payload|full payload|keystone-viewer" skills/*/SKILL.md`
- `rg -n "keystone_routing_decision|main_direct_change_report|routing decision" 00_docs/standards 00_docs/works skills`
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
- Author skill source가 repo-local skill source implementation을 자기 책임으로 설명하지 않는지
  확인한다.
- Linker skill source가 source edit authority 없이 graph interpretation과 handoff seed만
  제공하는지 확인한다.
- Skill source가 raw structured payload를 기본 사용자 응답으로 취급하지 않는지 확인한다.
- `keystone-viewer`가 언급되더라도 optional presentation/helper로만 설명되는지 확인한다.
- Skill source 변경이 Author lane으로 잘못 설명되지 않고 Main direct 또는 Coordinator lane으로
  설명되는지 확인한다.
- Skill source가 S08 작업서와 skill 기준서의 output artifact로 설명되고, graph 핵심 개념이
  surface 종류에 묶이지 않는지 확인한다.
- Prototype skill이나 외부 installed skill이 Keystone runtime dependency로 굳어지지 않는지
  확인한다.

<!-- key: id=key.work.skill-creation.order.progress-record refs=key.topic.progress-update key.topic.main-acceptance key.step.s08 -->

## Progress Record

S08 완료는 main acceptance 후에만 `key-progress.md`에 기록한다.
