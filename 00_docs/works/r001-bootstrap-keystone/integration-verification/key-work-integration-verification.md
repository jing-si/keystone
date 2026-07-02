---
doc_type: work_order
key:
  id: key.work.integration-verification.order
  refs:
    - key.doc.work
    - key.topic.integration-verification
    - key.topic.verification
    - key.topic.workflow
    - key.topic.simulation
---

# Integration Verification 작업서(4)

<!-- key: id=key.work.integration-verification.order.goal refs=key.topic.integration-verification key.topic.keystone-workflow key.topic.skill-source key.section.goal -->

## Goal

문서, artifact graph, 다섯 개 skill source가 하나의 Keystone workflow로 이어지는지 검증한다.

<!-- key: id=key.work.integration-verification.order.scope refs=key.section.scope key.role.reader key.role.author key.role.clarify key.role.linker key.role.coordinator key.output.current-step-brief key.contract.output key.boundary.browser-forbidden -->

## Scope

Include:

- Reader가 active work와 관련 기준서를 찾을 수 있는지 확인
- Clarify result를 Author가 적용할 수 있는지 확인
- Author가 Change Set을 만들고 Linker handoff seed를 남길 수 있는지 확인
- Linker가 문서 변경에서 capability와 output artifact 후보를 찾을 수 있는지 확인
- Linker가 code/config/schema/API/test 변경에서 문서 stale 후보를 찾을 수 있는지 확인
- Author가 만든 work step을 Coordinator가 복구할 수 있는지 확인
- Coordinator가 Current Step Brief, Context Pack, worker assignment, review/verification focus를
  도출할 수 있는지 확인
- 명시된 외부 코딩 스킬이 Coordinator를 대체하지 않고 worker assignment의 injected skill로
  들어가는지 확인
- Worker report를 Keystone workflow로 회수할 수 있는지 확인
- Metadata 과다 부여를 방지하는지 확인
- Structured payload와 기본 사용자 응답이 분리되고, optional viewer가 semantic owner가 되지
  않는지 확인
- File-changing work가 수정 전 routing decision을 만들고 surface별 lane/report로 분리되는지 확인
- 기준서(3), 결정(6), 작업서(4)가 만드는 output artifact와 실제 산출물 surface가 연결되는지 확인

Exclude:

- real publishing
- global install
- unrelated repository cleanup
- browser or Playwright verification
- Coordinator 밖의 추가 실행 보조 workflow

Conditionally allowed:

- 문서 기반 simulation
- 외부 코딩 스킬 주입 boundary simulation
- 필요성이 확인된 작은 fixture. 생성 전 위치와 범위를 보고한다.

<!-- key: id=key.work.integration-verification.order.source-context refs=key.section.source-context key.context-map key.work.index key.topic.skill-source -->

## Source Context

- `00_docs/key-context-map.md`
- `00_docs/standards/01_key-project-standard.md`
- `00_docs/standards/artifacts/key-standard-artifact-graph.md`
- `00_docs/standards/skills/00_key-index.md`
- `00_docs/works/00_key-index.md`
- `00_docs/works/r001-bootstrap-keystone/00_key-index.md`
- repo-local `skills/` source

<!-- key: id=key.work.integration-verification.order.completion-criteria refs=key.topic.acceptance key.topic.source-document-model key.topic.input-output key.topic.current-step key.topic.risk-record -->

## Completion Criteria

- [ ] Reader, Author, Clarify, Linker, Coordinator가 같은 source document model을 사용한다.
- [ ] 다섯 skill이 같은 artifact graph model을 사용한다.
- [ ] 각 skill의 output이 다음 skill의 input으로 연결될 수 있다.
- [ ] 문서 변경에서 관련 output artifact 후보가 나온다.
- [ ] code/config/schema/API/test 변경에서 문서 stale 후보가 나온다.
- [ ] Coordinator가 worker assignment와 worker report contract를 만들 수 있다.
- [ ] 외부 코딩 스킬은 Coordinator replacement가 아니라 injected skill로 해석된다.
- [ ] Coordinator가 현재 work step을 복구할 수 있다.
- [ ] Metadata 과다 부여를 방지하는 시나리오가 통과한다.
- [ ] 기본 사용자 응답은 structured payload를 그대로 노출하지 않고 결론, 근거, risk, 다음 행동,
      주요 출처를 요약한다.
- [ ] Optional `keystone-viewer`는 presentation/helper로만 해석되고 core runtime dependency나
      mandatory filter chain이 되지 않는다.
- [ ] Mixed surface 변경은 `keystone_routing_decision`으로 `source_document`, `skill_source`,
      `repository_source` lane을 분리한다.
- [ ] Source document 변경은 `author_patch_report`, Main direct skill source 변경은
      `main_direct_change_report`, delegated 변경은 Coordinator worker report를 남긴다.
- [ ] Linker는 `source_document | decision | work_order -> output_artifact` relation을 중심으로
      산출물 후보를 찾고, skill source/code/config/schema/API/test는 surface로 해석한다.
- [ ] 검증 결과와 남은 risk가 기록된다.

<!-- key: id=key.work.integration-verification.order.recommended-approach refs=key.section.recommended-approach key.topic.simulation key.topic.fixture key.boundary.approval -->

## Recommended Approach

처음에는 문서 기반 simulation으로 시작한다. 실제 fixture나 install 검증은 필요성이 확인되고
scope가 승인된 뒤 추가한다.

작은 fixture가 필요하다고 판단되면 다음 최소 구조를 후보로 삼는다. 이 구조는 생성 승인 전
계획 후보이며, 승인 없이 파일을 만들지 않는다.

```text
fixtures/simple-keystone-project/
  00_docs/
    key-context-map.md
    standards/
      00_key-index.md
      01_key-project-standard.md
    works/
      00_key-index.md
      r001-demo/
        00_key-index.md
        demo-change/
          00_key-index.md
          key-work-demo-change.md
          key-progress.md
  src/
    demo_service.ts
  tests/
    demo_service.test.ts
```

<!-- key: id=key.work.integration-verification.order.scenarios refs=key.topic.simulation key.topic.artifact-graph key.contract.output -->
## Verification Scenarios

Scenario A: 문서 변경에서 artifact 영향 후보를 찾는다.

1. 사람이 기준서 변경 의도를 말한다.
2. Clarify가 decision summary와 edit plan을 만든다.
3. Author가 기준서와 Change Set을 수정한다.
4. Linker가 source document, decision, work order가 만드는 output artifact 후보를 찾는다.
5. Linker가 필요하면 output artifact surface를 skill source/code/config/schema/API/test로 분류한다.
6. Coordinator가 worker assignment를 만든다.

통과 기준: 산출물을 직접 수정하지 않아도 관련 output artifact 후보와 surface별 handoff owner가 나온다.

Scenario B: code/config/schema/API/test 변경에서 문서 stale 후보를 찾는다.

1. Worker report에 changed files가 들어온다.
2. Linker가 관련 기준서, decision, capability, test metadata stale 후보를 찾는다.
3. Author가 문서 sync 필요 여부를 보고한다.

통과 기준: code/config/schema/API/test 변경 후 문서 stale 가능성이 report된다.

Scenario C: API contract 변경을 provider 승격 없이 impact 후보로 연결한다.

1. API contract가 변경된 상황을 가정한다.
2. Linker는 API artifact를 capability provider로 직접 확정하지 않는다.
3. Linker는 `implements` relation 또는 repository evidence로 implementing code/config/schema
   후보를 찾는다.
4. Linker는 implementing artifact가 제공하는 capability와 verifying test를 impact candidate로
   보고한다.
5. 문서와 decision stale 후보가 있으면 Author handoff로 분리한다.

통과 기준: API 변경이 문서 stale 후보로 연결되고, API가 기본 capability provider로 승격되지
않으며, 구현체와 test 후보가 Linker report에 나온다.

Scenario D: bounded worker assignment를 회수한다.

1. Coordinator가 `implement` purpose의 bounded worker assignment를 만든다.
2. 실제 file-writing worker 실행은 하지 않는다.
3. 반환해야 할 worker report contract를 확인한다.

통과 기준: Keystone이 Main context를 보존하면서 bounded worker에게 실행 context를 전달하고
report를 회수할 수 있다.

Scenario E: metadata 과다 부여를 방지한다.

1. 새 local helper function이 생긴 상황을 가정한다.
2. Linker는 semantic anchor가 아닌 artifact에 metadata 부여를 요구하지 않는다.

통과 기준: semantic anchor가 아닌 artifact에 metadata를 강제하지 않는다.

Scenario F: 최소 fixture가 필요한 경우의 검증 범위를 제한한다.

1. Reader는 fixture의 active work를 복구한다.
2. Linker는 fixture의 source/test 후보를 read-only로 보고한다.
3. Coordinator는 실제 file-writing worker 실행 없이 assignment contract만 만든다.

통과 기준: fixture 검증이 repo-local fixture 범위를 넘지 않고, install/publish/browser 검증으로
확장되지 않는다.

Scenario G: 외부 코딩 스킬은 Coordinator injected skill로만 사용한다.

1. 사용자가 Keystone 작업 문맥에서 `$superpowers` 같은 외부 코딩 스킬을 명시했다고 가정한다.
2. Coordinator는 bounded worker assignment를 유지하고 해당 스킬을 `injected_skills`에 넣는다.
3. Assignment의 authority, scope, forbidden changes, workspace guard, verification,
   return report contract는 Keystone 기준서를 따른다.

통과 기준: 외부 코딩 스킬이 Coordinator replacement, runtime dependency, scope expansion 근거로
해석되지 않는다.

Scenario H: 사용자 응답과 structured payload를 분리한다.

1. Reader가 full `reader_output`을 만들 수 있는 상황을 가정한다.
2. 기본 사용자 응답은 결론, 핵심 근거, 주요 risk, 다음 행동, 주요 출처만 보여준다.
3. 사용자가 full payload를 요청하면 원래 structured payload를 보여줄 수 있다.
4. Optional `keystone-viewer`가 있는 경우 payload를 audience-specific view로 렌더링하지만
   status, risk, recommended next action, acceptance 판단을 바꾸지 않는다.
5. Coordinator는 viewer summary가 아니라 원래 structured payload 또는 handoff capsule을 input으로
   사용한다.

통과 기준: 사용자-facing view가 context를 줄이면서도 source authority, risk, handoff payload,
Main acceptance 판단을 바꾸지 않는다.

Scenario I: mixed surface 변경은 routing gate를 통과한다.

1. `00_docs/**`와 `skills/keystone-*/SKILL.md`를 함께 바꾸는 요청을 가정한다.
2. Main은 수정 전에 `keystone_routing_decision`을 만들고 target surface를 `mixed`로 표시한다.
3. Source document 변경은 Author lane으로 보내고 `author_patch_report`를 요구한다.
4. Skill source 변경은 작은 S08 scope면 Main direct lane과 `main_direct_change_report`를
   사용하고, delegation이나 formal verification이 필요하면 Coordinator worker assignment를 사용한다.
5. Linker가 skill source surface의 output artifact stale/gap 후보를 보고할 수 있지만 직접 수정하지 않는다.

통과 기준: 기준서를 읽은 것만으로 lane 실행을 대체하지 않고, surface별 report가 남는다.

Scenario J: source document가 만든 output artifact를 추적한다.

1. S08 작업서가 다섯 개 `skills/keystone-*/SKILL.md`를 산출물로 요구하는 상황을 가정한다.
2. Linker는 S08 작업서와 각 skill 기준서에서 produced output artifact 후보를 찾는다.
3. Linker는 각 `SKILL.md`를 `artifact_kind: skill_source`인 output artifact surface로 분류한다.
4. Linker는 stale/gap을 산출물 relation 기준으로 보고하고, 수정은 routing decision으로 넘긴다.

통과 기준: Artifact Graph 대상 여부가 skill source라는 파일 종류가 아니라 source document와 work
order가 요구한 output artifact relation에서 나온다.

<!-- key: id=key.work.integration-verification.order.context-pack-seed refs=key.output.context-pack key.topic.skill-source key.step.s01-s07 key.doc.work-order key.doc.progress key.topic.workflow-sequence -->

## Context Pack Seed

- 다섯 개 skill source
- S01-S07 기준서
- 현재 work order와 progress
- 검증할 workflow sequence
- Artifact Graph 기준서
- Linker report contract
- Worker assignment/report contract
- external coding skill injected skill boundary
- structured payload와 user-facing response separation
- optional `keystone-viewer` presentation/helper boundary
- Keystone routing decision and lane-specific reports
- source document to output artifact relation
- 필요한 경우 승인된 최소 fixture path

<!-- key: id=key.work.integration-verification.order.stop-conditions refs=key.section.stop-conditions key.topic.skill-source-missing key.contract.output key.boundary.fixture-approval -->

## Stop Conditions

- Skill source가 아직 생성되지 않았다.
- 문서와 skill source가 서로 다른 trigger 또는 output contract를 가진다.
- 외부 코딩 스킬 검증이 Coordinator 밖의 별도 실행 계층을 요구한다.
- fixture나 install 검증이 필요하지만 승인되지 않았다.
- 문서 기반 simulation만으로 artifact graph 흐름을 검증할 수 없다.

<!-- key: id=key.work.integration-verification.order.verification refs=key.topic.verification key.topic.cross-read key.topic.simulation key.boundary.install-forbidden key.boundary.publish-forbidden key.boundary.browser-forbidden -->

## Verification

Allowed:

- `rg --files 00_docs skills`
- `rg -n "external coding skill|외부 코딩 스킬|injected skill|keystone-default-bounded-worker" 00_docs/standards skills`
- `rg -n "structured payload|Default User Response|keystone-viewer|사용자 응답" 00_docs/standards 00_docs/works skills`
- `rg -n "keystone_routing_decision|main_direct_change_report|routing decision|skill_source" 00_docs/standards 00_docs/works skills`
- `rg -n "output_artifact|produces|produced_from|artifact_kind" 00_docs/standards 00_docs/works skills`
- skill file과 기준서 cross-read
- 문서 기반 workflow simulation

Forbidden until explicitly allowed:

- global install
- package publish
- Playwright/browser verification
- 실제 file-writing worker 실행

<!-- key: id=key.work.integration-verification.order.expected-output refs=key.contract.output key.topic.integration-verification key.topic.risk-record key.step.s08-candidate -->

## Expected Output

- 통합 검증 결과
- 수정이 필요한 기준서 또는 skill source 목록
- 다음 단계가 필요하면 S10 후보 제안

<!-- key: id=key.work.integration-verification.order.review-points refs=key.section.review-points key.topic.responsibility-boundary key.topic.current-step key.topic.verification-path -->

## Review Points

- 다섯 skill이 서로 책임을 침범하지 않는지 확인한다.
- 문서에서 current step과 verification path를 복구할 수 있는지 확인한다.
- Linker와 Coordinator가 artifact 후보 해석과 bounded assignment brokering을 분리하는지
  확인한다.
- 외부 코딩 스킬이 Coordinator assignment boundary 안의 injected skill로만 쓰이는지 확인한다.
- Worker report가 Main acceptance를 대체하지 않는지 확인한다.

<!-- key: id=key.work.integration-verification.order.progress-record refs=key.topic.progress-update key.topic.main-acceptance key.step.s09 -->

## Progress Record

S09 완료는 main acceptance 후에만 `key-progress.md`에 기록한다.
