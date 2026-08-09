---
doc_type: work_order
created_at: "2026-08-07"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-09", accepted_by: main}
work_status: complete
key:
  id: key.work.work-state-runtime.order
  refs:
    - key.doc.work
    - key.topic.work-sequence
    - key.topic.work-recovery
    - key.topic.finalization
    - key.topic.change-set
    - key.topic.integration-verification
    - key.role.coordinator
    - key.topic.verification
  relations:
    depends_on:
      - target: key.work.authority-chain-snapshot-closure.order
    supersedes:
      - target: key.work.work-state-agent-evaluation.order
work_gates:
  - dependency: key.work.authority-chain-snapshot-closure.order
    applies_to:
      steps: [S04]
      work_completion: false
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
  - dependency: key.work.authority-chain-snapshot-closure.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
---

# Deterministic Work State Runtime 작업서 및 Change Set

<!-- key: id=key.work.work-state-runtime.order.goal refs=key.section.goal key.topic.work-recovery -->
## Goal

Global work state를 서로 일치하는 manifest 선언이 아니라 repository 전체 authoritative source에서
파생하고, Reader·Coordinator·Author finalization·release gate가 동일 source generation과
deterministic runtime 결과를 사용하게 한다.

<!-- key: id=key.work.work-state-runtime.order.improvements refs=key.topic.work-sequence key.topic.verification -->
## 개선 항목

| ID | 개선 항목 | 구현 순서 | 핵심 근거 |
|---|---|---|---|
| PC85-08 | Repository-derived global work state | 1 | whole-tree active/accepted/latest derivation |
| PC85-09 | Deterministic Work State Runtime | 2 | 네 consumer의 canonical state parity |

<!-- key: id=key.work.work-state-runtime.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- Canonical round/work/progress discovery와 active/accepted/latest derived state
- Acceptance ordering authority와 historical compatibility
- Initialization, active/early work, dependency와 finalization gate를 반환하는 Work State Runtime
- Complete snapshot/source generation/path-set digest와 conflict diagnostics
- Reader, Coordinator, Author finalization과 release gate consumer parity
- Installed package self-containment와 policy parity 검증
- S06/S07이 소비할 repository-derived prerequisite finalization closure

Exclude:

- Coordinator phase chain과 snapshot capture primitives: R010/S02
- Transaction/parser/lifecycle correctness: R010/S03
- Actual model/skill behavior execution: R010/S05
- Whole-flow integration: R010/S06
- Independent CI, live Main acceptance와 terminal finalization: R010/S07

<!-- key: id=key.work.work-state-runtime.order.source-context refs=key.section.source-context key.topic.work-recovery -->
## Source Context

- R010/S01 readiness/finalization/release implementation evidence
- R010/S02 complete snapshot and phase source-generation contract
- `00_docs/standards/01_key-project-standard.md`
- `00_docs/standards/skills/reader/key-standard-reader.md`
- `00_docs/standards/skills/coordinator/key-standard-coordinator.md`
- `00_docs/standards/skills/author/key-standard-author.md`
- `00_docs/convention.md`

<!-- key: id=key.work.work-state-runtime.order.pc85-08 refs=key.topic.work-recovery key.topic.finalization -->
## PC85-08 Repository-derived global work state

Implementation:

1. Canonical round/work/progress source를 발견해 active rounds, accepted rounds, active works,
   active steps와 latest accepted round를 계산한다.
2. Active round는 0개 또는 1개이고 active work/step은 active round 아래에만 있도록 검증한다.
3. Terminal 상태에는 `planned | in_progress | blocked` Work가 없어야 하며 stale active pointer를
   source claim과 derived result 차이로 진단한다.
4. Latest accepted round ordering은 단순 날짜/round 번호가 아니라 accepted event chain
   authority에 결속한다.
5. 장기 기준서의 특정 active-work path claim은 Context Map/root works index 탐색 규칙으로
   대체한다.

Accepted Decision:

- 권장 event record는 `id`, `sequence`, `previous_event_ref`, `round_ref`, `accepted_steps`,
  `acceptance_ref`, `subject_digest`, `accepted_at`, `accepted_by`를 가진다.
- Genesis를 제외한 event는 predecessor보다 `sequence`가 정확히 1 크고, event ID·sequence와
  predecessor는 각각 유일해야 한다. Fork, cycle, missing predecessor와 같은 Step의 상충
  acceptance를 거절하며 canonical chain head가 `latest_accepted_round`의 event여야 한다.
- `DEC-WORKS-027`에 따라 R001-R009는 R009 `sequence: 0` migration genesis의 canonical
  historical-source projection digest로 admission한다. R010/S01-S03 Step acceptance는 local
  evidence로 보존하고, R010 terminal Round acceptance부터 `sequence +1` forward-only chain을
  생성한다.
- Historical per-Round synthetic backfill, date/Round-number fallback와 legacy/event dual
  ordering authority는 허용하지 않는다.

Verification:

- Multiple active rounds, out-of-round active work/step, nonexistent latest accepted와 terminal
  residual Work가 실패한다.
- 같은 날짜 복수 acceptance와 round-number 역전 fixture에서 accepted ordering이 deterministic하다.
- Duplicate sequence/predecessor, fork, cycle, missing event와 non-head latest fixture가 실패한다.
- 네 global source가 서로 같아도 derived state와 다르면 finalization이 실패한다.

Done when: latest/active 상태를 manifest 선언만으로 위조할 수 없고 repository source에서 같은
결과를 재계산할 수 있다.

<!-- key: id=key.work.work-state-runtime.order.pc85-09 refs=key.topic.work-recovery key.role.coordinator -->
## PC85-09 Deterministic Work State Runtime

Implementation:

1. Repository root/document root를 입력으로 initialization state, active round/works/steps, early
   work, latest accepted, conflicts, dependency evaluations와 finalization gates를 반환한다.
2. Parse/policy는 deterministic functional core, filesystem discovery는 adapter로 분리한다.
3. 하나의 canonical pure source를 build input으로 두고, build/install이 각 독립 skill package에
   generated vendored copy를 만든다. Runtime cross-skill import와 수작업 copy는 허용하지 않는다.
4. Canonical policy digest와 generated copy의 byte/API digest를 manifest에 기록하고 build, install,
   package test에서 exact parity를 검증한다.
5. Output에 complete snapshot/source generation/path-set digest를 포함한다.
6. Reader orientation, Coordinator Context Pack, Author finalization과 release gate가 runtime output을
   직접 소비하고 자체 재해석을 제거한다.
7. 각 prerequisite Work의 finalization을 repository source와 package-owned Author runner에서 파생해
   `result: complete | waived`, `waiver_reason`, `follow_up`, `acceptance_ref`, `manifest_digest`,
   `envelope_digest`, `author_runner_status: pass`를 가진 closure로 반환한다. `waived`는 non-empty
   reason과 follow-up이 필수이고, 누락·digest mismatch·runner non-pass는 fail-closed다.

Accepted Architecture:

- `DEC-WORKS-028`에 따라 `scripts/work_state_runtime.py`를 canonical pure source로 두고
  `scripts/generate_work_state_runtimes.py`가 Reader, Coordinator와 Author package에
  `scripts/work_state_runtime.py` vendored copy를 생성한다. Release gate는 canonical source를
  직접 소비한다.
- Generator `--check`, policy/byte/public-API digest, build/install과 package tests가 exact parity를
  fail-closed로 검증한다.
- Runtime cross-skill import, repository-local sibling import, 수작업 copy와 consumer별 별도 policy는
  수락하지 않는다.

Verification:

- 네 consumer가 동일 fixture/generation에서 canonical state와 diagnostics를 동일하게 반환한다.
- Conflict, incomplete scan, interrupted work, waiting dependency와 terminal state를 공통 fixture로
  검증한다.
- Installed package가 repository-local 다른 skill import 없이 실행된다.
- Generated copies의 policy digest, bytes와 public API가 canonical source와 일치한다.
- Complete/waived prerequisite closure와 missing reason/follow-up, stale manifest/envelope,
  Author runner fail fixture를 S06/S07 consumer까지 검증한다.

Done when: active-state drift를 consumer별 parser 차이로 재현할 수 없고 incomplete coverage는 네
consumer 모두에서 fail-closed다.

<!-- key: id=key.work.work-state-runtime.order.decision-gates refs=key.doc.decision key.boundary.stop-condition key.work.decisions.dec-works-027 key.work.decisions.dec-works-028 -->
## Decision and Architecture Gates

1. Acceptance ordering authority는 `DEC-WORKS-027`의 R009 migration genesis와 forward-only
   terminal Round event chain으로 확정했다.
2. Runtime 배치는 `DEC-WORKS-028`의 canonical pure source와 generated vendored copies로
   확정했다.
3. Runtime/schema implementation과 parity evidence는 두 Decision을 변경하지 않고 S04 Progress에
   별도로 기록한다.

<!-- key: id=key.work.work-state-runtime.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: work recovery와 finalization/release state를 repository-derived canonical result에 결속한다.
- Required candidates: Reader/Coordinator/Author runtime·contracts, release gate consumer,
  work-state parser/policy, generated-copy pipeline, prerequisite finalization closure와 cross-skill
  parity tests
- Conditional candidates: Acceptance/finalization schema는 accepted ordering field가 추가되는 범위만
  versioned update한다.
- Excluded: S03/S05-S07 owned implementation, external provider integration와 stored credentials
- Acceptance owner: Main
- Graph handling: runtime/contract/document delta를 Linker가 분류하고 required mutation만
  owner-attested transaction으로 처리한다.

<!-- key: id=key.work.work-state-runtime.order.completion refs=key.topic.acceptance key.topic.integration-verification -->
## Completion Criteria

Work Order는 criterion statement만 소유하고 현재 state/evidence는 S04 Progress가 관리한다.

<!-- key: id=key.acceptance.work-state.whole-tree-derivation -->
- `R010-S04-CC-01` Whole works tree에서 active rounds, accepted rounds, active works, active steps와
  latest accepted round가 파생된다.
<!-- key: id=key.acceptance.work-state.conflict-terminal-detection -->
- `R010-S04-CC-02` Multiple active round, stale pointer, nonexistent latest와 terminal residual Work가
  실패한다.
<!-- key: id=key.acceptance.work-state.acceptance-ordering -->
- `R010-S04-CC-03` Acceptance ordering authority와 historical compatibility가 accepted Decision에
  결속된다.
<!-- key: id=key.acceptance.work-state.consumer-runtime -->
- `R010-S04-CC-04` Reader, Coordinator, Author finalization과 release gate가 같은 Work State Runtime
  결과를 소비한다.
<!-- key: id=key.acceptance.work-state.consumer-parity -->
- `R010-S04-CC-05` 동일 generation의 네 consumer state, diagnostics와 completeness가 canonical
  parity를 만족한다.
<!-- key: id=key.acceptance.work-state.installed-self-containment -->
- `R010-S04-CC-06` Installed package self-containment와 incomplete-coverage fail-closed 경계가
  보존된다.
<!-- key: id=key.acceptance.work-state.prerequisite-verification -->
- `R010-S04-CC-07` S02 Work가 `complete + accepted`이고 S04 focused/package/cross-skill verification이
  통과한다.
<!-- key: id=key.acceptance.work-state.start-gate -->
- `R010-S04-CC-08` S02가 `complete + accepted`이기 전 S04 start gate는 `waiting`이며 read-only 조사와
  문서 fixture 설계만 허용하고 runtime/test/code/config/schema write, `in_progress` 전이와 canonical
  schema commitment를 차단한다.
<!-- key: id=key.acceptance.work-state.acceptance-event-chain -->
- `R010-S04-CC-09` Accepted Decision과 migration policy 아래 event identity, +1 sequence, unique
  predecessor/sequence, no fork/cycle와 chain-head latest invariant가 검증된다.
<!-- key: id=key.acceptance.work-state.generated-runtime-parity -->
- `R010-S04-CC-10` Accepted runtime architecture가 one-policy authority와 installed self-containment를
  보존하고 canonical source와 generated vendored copies의 policy digest·byte/API parity를 증명한다.
<!-- key: id=key.acceptance.work-state.prerequisite-finalization-closure -->
- `R010-S04-CC-11` S06/S07 consumer가 complete 또는 근거 있는 waived prerequisite finalization,
  acceptance ref, manifest/envelope digest와 package-owned Author runner pass를 repository-derived
  output으로 검증한다.

<!-- key: id=key.work.work-state-runtime.order.verification refs=key.topic.verification -->
## Verification

- Whole-tree derived-state 정상/충돌/terminal/ordering fixture
- Reader·Coordinator·Author·release cross-consumer parity suite
- Generated vendored runtime parity, installed self-containment와 incomplete coverage tests
- Prerequisite finalization closure normal/waiver/stale/runner-failure consumer tests
- Repository full readiness/graph validation, external-cache compileall과 `git diff --check`

<!-- key: id=key.work.work-state-runtime.order.expected-output refs=key.topic.verification key.topic.work-recovery -->
## Expected Output

- Derived global-state model and accepted ordering contract
- Deterministic Work State Runtime, canonical CLI/envelope, generated vendored copies와 four-consumer
  adapters
- S06/S07 prerequisite finalization closure projection
- Cross-skill parity/adversarial suites, contract/reference updates와 Progress evidence

<!-- key: id=key.work.work-state-runtime.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. Acceptance ordering authority에 복수 valid 선택이 남고 Main/User decision이 없다.
2. Installed self-containment를 깨지 않고 consumer parity를 만들 architecture가 없다.
3. Incomplete discovery를 authority-bearing success로 취급해야 completion이 가능하다.
4. 새 skill 또는 external dependency가 completion 필수가 된다.
5. S02 start gate가 열리기 전에 runtime/test/code/config/schema write, `in_progress` 전이나 canonical
   schema commitment가 필요하다.
