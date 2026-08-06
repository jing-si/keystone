---
doc_type: work_order
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-06", accepted_by: main}
work_status: complete
key:
  id: key.work.coordinator-keystone-closure.order
  refs:
    - key.doc.work
    - key.role.coordinator
    - key.standard.subagent
    - key.topic.skill-contract
    - key.topic.keystone-metadata
    - key.topic.artifact-graph
    - key.topic.change-set
---

# Coordinator Keystone Closure 작업서 및 Change Set

<!-- key: id=key.work.coordinator-keystone-closure.order.goal refs=key.section.goal key.role.coordinator -->
## Goal

Coordinator가 구현 전에 Main context와 Keystone source를 결합한 bounded Context Pack을 제공하고,
구현 후에는 외부 스킬의 결과를 표준 worker report로 회수해 Linker·Author를 통한 문서,
키메타, 그래프와 finalization closure가 끝날 때까지 감독한다.

<!-- key: id=key.work.coordinator-keystone-closure.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- Coordinator의 `direct_execution | orchestration` mode 분리
- 외부 스킬이 있으면 구현을 위임하고 Coordinator는 implementation surface를 직접 수정하지 않는 경계
- 외부 스킬이 없으면 default bounded-worker contract로 Coordinator가 직접 구현할 수 있는 경계
- Main checkpoint, Reader/Author/Linker evidence, 기준서·작업서·진행 기록을 합친 Context Pack
- 외부 스킬 결과를 canonical worker report와 artifact delta 목록으로 정규화하는 contract
- document sync, metadata sync, graph sync와 verification closure gate
- Linker graph classification과 Author source-document update/finalization routing
- Coordinator package가 독립 실행할 수 있는 standard-library-only closure validator와 test
- Subagent/Coordinator 기준서, installed Coordinator skill과 contract test 정합화

Exclude:

- R008 work source, R008 round status와 Project Standard
- Linker의 canonical graph mutation authority 또는 Author의 source-write authority 이전
- 외부 스킬별 내부 workflow 재구현
- Nested worker를 Coordinator 밖에서 임의 생성하도록 허용하는 권한 확대
- Publication, push, merge와 외부 소비 프로젝트 pilot

<!-- key: id=key.work.coordinator-keystone-closure.order.source-context refs=key.section.source-context key.topic.skill-contract -->
## Source Context

- 사용자 결정: Coordinator는 외부 작업자에게 Keystone context를 제공하고 구현 뒤 Keystone
  closure를 책임진다.
- `DEC-WORKS-008`, `DEC-WORKS-017`, `DEC-WORKS-018`, `DEC-WORKS-021`, `DEC-WORKS-024`,
  `DEC-WORKS-026`
- `00_docs/standards/subagents/key-standard-subagents.md`
- `00_docs/standards/skills/coordinator/key-standard-coordinator.md`
- `00_docs/standards/skills/author/key-standard-author.md`
- `00_docs/standards/skills/linker/key-standard-linker.md`
- `00_docs/convention.md`

<!-- key: id=key.work.coordinator-keystone-closure.order.baseline refs=key.topic.impact-review key.topic.verification -->
## Baseline Findings

1. Coordinator는 Context Pack, artifact delta, metadata sync risk와 acceptance finalization routing을
   이미 문서상 요구한다.
2. 외부 스킬 report의 `document_sync_needed`와 `metadata_sync_needed`는 구조와 closure evidence가
   없어 생략되거나 단순 boolean으로 축소될 수 있다.
3. Coordinator와 외부 스킬을 함께 사용할 때 direct implementation과 orchestration mode가
   구분되지 않는다.
4. Superpowers task/ledger/branch completion을 Keystone worker report, Main acceptance와
   finalization으로 변환하는 gate가 없다.
5. 현재 contract test는 문구 존재를 확인할 뿐 incomplete metadata/graph closure를 fail-closed로
   검증하지 않는다.

<!-- key: id=key.work.coordinator-keystone-closure.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: 외부 스킬 구현과 Keystone closure 사이에 Coordinator-owned 감시·routing gate를 둔다.
- Impact seeds: `key.standard.subagent`, `key.standard.skill.coordinator`,
  `key.skill.coordinator`, `key.role.author`, `key.role.linker`
- Required candidates: Subagent/Coordinator 기준서와 관련 index/README, installed Coordinator skill,
  closure validator, package/contract tests
- Independent active-round namespace: R008은 active로 보존하며 R009의 dependency나 blocker가 아니다
- Excluded: 다른 Keystone skill runtime 의미 변경, Linker/Author Python runtime 변경, R008 source
- Acceptance owner: Main
- Graph handling: Linker는 기존 `key.skill.coordinator governed_by key.standard.skill.coordinator`
  relation이 유효하며 canonical node/relation mutation은 필요 없다고 판정했다. R002
  `produced_from`은 historical provenance이고 R008/S07 code/test anchor는 non-blocking coverage debt다.

<!-- key: id=key.work.coordinator-keystone-closure.order.approach refs=key.section.recommended-approach key.topic.verification -->
## Recommended Approach

1. Execution mode와 ownership을 먼저 분리한다.
2. Worker에게 전달할 Context Pack의 required evidence를 명시한다.
3. Worker output을 canonical report로 정규화하고 모든 changed surface에 delta를 요구한다.
4. Document/metadata/graph sync disposition과 state를 fail-closed validator로 검사한다.
5. Coordinator는 필요한 Linker와 Author handoff가 끝나기 전 `accept_candidate`를 만들지 않는다.
6. Main acceptance 뒤 Author finalization까지 완료되어야 Keystone closure를 complete로 본다.

<!-- key: id=key.work.coordinator-keystone-closure.order.completion refs=key.topic.acceptance key.topic.integration-verification -->
## Completion Criteria

- [x] Coordinator 단독 사용과 외부 스킬 사용의 execution mode가 구분된다.
- [x] Orchestration mode worker가 Main/Keystone context를 포함한 Context Pack을 받는다.
- [x] 외부 스킬의 구현 결과가 canonical worker report와 artifact delta 목록으로 회수된다.
- [x] Changed surface 누락, 미분류 document/metadata/graph sync와 불완전 verification이
      `accept_candidate`를 fail-closed로 차단한다.
- [x] Linker와 Author의 권한을 유지하면서 Coordinator가 closure routing을 끝까지 책임진다.
- [x] Superpowers completion이 Keystone work completion 또는 acceptance로 직접 승격되지 않는다.
- [x] Closure validator가 정상, no-change, deferred, missing evidence와 invalid mode fixture를 검증한다.
- [x] Coordinator package와 skill contract test가 통과한다.
- [x] Repository graph validator와 `git diff --check`가 통과한다.
- [x] R008 변경을 덮어쓰거나 global active round를 변경하지 않는다.

<!-- key: id=key.work.coordinator-keystone-closure.order.review-points refs=key.section.review-points key.topic.impact-review -->
## Review Points

- Coordinator가 closure를 감독하되 Linker graph authority와 Author document authority를 침범하지 않는가
- External skill `DONE`과 Coordinator `accept_candidate`, Main acceptance가 분리되는가
- Direct execution mode가 외부 스킬이 있는 orchestration mode로 새지 않는가
- Context Pack이 전체 문서 corpus dump가 아니라 bounded source/decision/work evidence인가
- No-change disposition이 구체적인 이유와 evidence 없이 성공으로 처리되지 않는가

<!-- key: id=key.work.coordinator-keystone-closure.order.verification refs=key.topic.verification -->
## Verification

- Coordinator closure validator unit/integration tests
- `python3 -m unittest discover -s skills/tests -p 'test_*.py'`
- Linker, Author와 Reader regression suite
- `python3 -m compileall` with external bytecode cache
- `python3 skills/keystone-linker/scripts/validate_graph.py --root . --scope repository`
- `git diff --check`

<!-- key: id=key.work.coordinator-keystone-closure.order.expected-output refs=key.contract.output key.topic.work-recovery -->
## Expected Output

- Coordinator execution-mode and Keystone-closure runtime contract
- Context Pack과 canonical worker-report closure schema
- Fail-closed Coordinator closure validator와 regression fixture
- Linker/Author handoff와 Main acceptance readiness를 구분한 검증 증거
- Main acceptance, local installation parity와 independent R008 active-round preservation evidence

<!-- key: id=key.work.coordinator-keystone-closure.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. R008과 동일 source를 동시에 수정해야만 구현할 수 있다.
2. Coordinator가 Linker mutation authority 또는 Author source authority를 가져야만 closure가 가능하다.
3. 외부 스킬별 private runtime dependency를 Coordinator package에 추가해야 한다.
4. Python 3.9 standard-library-only 또는 installed-package independence를 깨야 한다.
5. R008 변경을 덮어쓰거나 global active round를 전환해야만 진행할 수 있다.

<!-- key: id=key.work.coordinator-keystone-closure.order.acceptance refs=key.topic.acceptance key.topic.verification -->
## Acceptance

Main은 R009/S01을 2026-08-06에 수락했다. Main의 fresh verification은 Coordinator 25,
skill contracts 18, Linker 175, Author 75, Reader 2 tests passed, external bytecode cache를 쓴
compileall, repository graph diagnostics 0, `bash -n` installer 및 `git diff --check` pass를 포함한다.
Staging/backup/post-swap local install도 성공했고 installed SKILL, validator, reference는 repository와
byte-identical이며 installed Coordinator tests 25 passed했다. 설치 manifest는 `0.6.0-dev`와
`source_dirty: true`를 기록한다. publication, push, merge, external pilot은 범위 밖이다.
