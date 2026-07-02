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
- Linker가 문서 변경에서 capability/code/config/schema/API/test 후보를 찾을 수 있는지 확인
- Linker가 code/config/schema/API/test 변경에서 문서 stale 후보를 찾을 수 있는지 확인
- Author가 만든 work step을 Coordinator가 복구할 수 있는지 확인
- Coordinator가 Current Step Brief, Context Pack, worker assignment, review/verification focus를
  도출할 수 있는지 확인
- 명시된 외부 코딩 스킬이 Coordinator를 대체하지 않고 worker assignment의 injected skill로
  들어가는지 확인
- Worker report를 Keystone workflow로 회수할 수 있는지 확인
- Metadata 과다 부여를 방지하는지 확인

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
- [ ] 문서 변경에서 관련 code/config/schema/API/test 후보가 나온다.
- [ ] code/config/schema/API/test 변경에서 문서 stale 후보가 나온다.
- [ ] Coordinator가 worker assignment와 worker report contract를 만들 수 있다.
- [ ] 외부 코딩 스킬은 Coordinator replacement가 아니라 injected skill로 해석된다.
- [ ] Coordinator가 현재 work step을 복구할 수 있다.
- [ ] Metadata 과다 부여를 방지하는 시나리오가 통과한다.
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

Scenario A: 문서 변경에서 code 영향 후보를 찾는다.

1. 사람이 기준서 변경 의도를 말한다.
2. Clarify가 decision summary와 edit plan을 만든다.
3. Author가 기준서와 Change Set을 수정한다.
4. Linker가 capability/code/config/schema/API/test 후보를 찾는다.
5. Coordinator가 worker assignment를 만든다.

통과 기준: 코드를 직접 수정하지 않아도 관련 code/config/schema/API/test 후보가 나온다.

Scenario B: code 변경에서 문서 stale 후보를 찾는다.

1. Worker report에 changed files가 들어온다.
2. Linker가 관련 기준서, decision, capability, test metadata stale 후보를 찾는다.
3. Author가 문서 sync 필요 여부를 보고한다.

통과 기준: code/config/schema/API/test 변경 후 문서 stale 가능성이 report된다.

Scenario C: bounded worker assignment를 회수한다.

1. Coordinator가 `implement` purpose의 bounded worker assignment를 만든다.
2. 실제 file-writing worker 실행은 하지 않는다.
3. 반환해야 할 worker report contract를 확인한다.

통과 기준: Keystone이 Main context를 보존하면서 bounded worker에게 실행 context를 전달하고
report를 회수할 수 있다.

Scenario D: metadata 과다 부여를 방지한다.

1. 새 local helper function이 생긴 상황을 가정한다.
2. Linker는 semantic anchor가 아닌 artifact에 metadata 부여를 요구하지 않는다.

통과 기준: semantic anchor가 아닌 artifact에 metadata를 강제하지 않는다.

Scenario E: 최소 fixture가 필요한 경우의 검증 범위를 제한한다.

1. Reader는 fixture의 active work를 복구한다.
2. Linker는 fixture의 source/test 후보를 read-only로 보고한다.
3. Coordinator는 실제 file-writing worker 실행 없이 assignment contract만 만든다.

통과 기준: fixture 검증이 repo-local fixture 범위를 넘지 않고, install/publish/browser 검증으로
확장되지 않는다.

Scenario F: 외부 코딩 스킬은 Coordinator injected skill로만 사용한다.

1. 사용자가 Keystone 작업 문맥에서 `$superpowers` 같은 외부 코딩 스킬을 명시했다고 가정한다.
2. Coordinator는 bounded worker assignment를 유지하고 해당 스킬을 `injected_skills`에 넣는다.
3. Assignment의 authority, scope, forbidden changes, workspace guard, verification,
   return report contract는 Keystone 기준서를 따른다.

통과 기준: 외부 코딩 스킬이 Coordinator replacement, runtime dependency, scope expansion 근거로
해석되지 않는다.

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
