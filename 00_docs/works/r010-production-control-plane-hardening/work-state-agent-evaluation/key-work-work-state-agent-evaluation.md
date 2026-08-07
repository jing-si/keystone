---
doc_type: work_order
created_at: "2026-08-07"
document_lifecycle: active
approval: {state: pending}
work_status: planned
key:
  id: key.work.work-state-agent-evaluation.order
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
work_gates:
  - dependency: key.work.authority-chain-snapshot-closure.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval:
        state: accepted
    optional: false
---

# Work State and Agent Evaluation 작업서 및 Change Set

<!-- key: id=key.work.work-state-agent-evaluation.order.goal refs=key.section.goal key.topic.work-recovery -->
## Goal

Global work state를 manifest의 일치하는 선언이 아니라 repository 전체 authoritative source에서
파생하고, Reader·Coordinator·Author·release gate가 동일 deterministic runtime 결과를 사용하게
한다. 기존 12개 agent scenario를 실제 skill invocation, transcript, before/after snapshot과
independent review evidence를 생성하는 runner로 실행해 행동 검증을 수작업 manifest 단계에서
actual evidence 단계로 올린다.

<!-- key: id=key.work.work-state-agent-evaluation.order.improvements refs=key.topic.work-sequence key.topic.verification -->
## 개선 항목

| ID | 개선 항목 | 구현 순서 | 핵심 근거 |
|---|---|---|---|
| PC85-08 | Repository-derived global work state | 1 | whole-tree active/accepted/latest derivation |
| PC85-09 | Deterministic Work State Runtime | 2 | 네 consumer의 canonical state parity |
| PC85-10 | Actual agent behavior eval runner | 3 | 실제 invocation·transcript·snapshot·review evidence |

<!-- key: id=key.work.work-state-agent-evaluation.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- Canonical round/work/progress discovery와 active/accepted/latest derived state
- Acceptance ordering authority와 historical compatibility
- Initialization, active/early work, dependency와 finalization gate를 반환하는 Work State Runtime
- Reader, Coordinator, Author와 release gate consumer parity
- 12개 agent scenario의 actual invocation, transcript, snapshot, check와 reviewer attestation
- Prompt injection, missing tool, timeout, partial failure와 extra-authority request

Exclude:

- Coordinator phase chain과 snapshot capture primitives: R010/S02
- Transaction/parser/lifecycle correctness: R010/S03
- Whole-flow acceptance/finalization과 CI release orchestration: R010/S05
- 외부 pilot, 비대칭 attestation과 model/provider dependency를 repository runtime에 추가하는 작업

<!-- key: id=key.work.work-state-agent-evaluation.order.source-context refs=key.section.source-context key.topic.work-recovery -->
## Source Context

- R010/S01 readiness/finalization/release/evidence validator implementation
- R010/S02 complete snapshot and phase source-generation contract
- `00_docs/standards/01_key-project-standard.md`
- `00_docs/standards/skills/reader/key-standard-reader.md`
- `00_docs/standards/skills/coordinator/key-standard-coordinator.md`
- `00_docs/standards/skills/author/key-standard-author.md`
- `scripts/agent_eval_scenarios.json`, `scripts/validate_agent_evals.py`와 release gate
- `00_docs/convention.md`

<!-- key: id=key.work.work-state-agent-evaluation.order.pc85-08 refs=key.topic.work-recovery key.topic.finalization -->
## PC85-08 Repository-derived global work state

Implementation:

1. Canonical round/work/progress source를 발견해 active rounds, accepted rounds, active works,
   active steps와 latest accepted round를 계산한다.
2. Active round는 0개 또는 1개이고 active work/step은 active round 아래에만 있도록 검증한다.
3. Terminal 상태에는 `planned | in_progress | blocked` Work가 없어야 하며 stale active pointer를
   source claim과 derived result 차이로 진단한다.
4. Latest accepted round ordering은 단순 날짜/round 번호가 아니라 accepted event ordering
   authority에 결속한다.
5. 장기 기준서의 특정 active-work path claim은 Context Map/root works index 탐색 규칙으로
   대체한다.

Decision gate:

- `acceptance.sequence`를 권장하지만 historical compatibility/migration 규칙과 함께 Main 또는
  Clarify가 수락하기 전 wire를 고정하지 않는다.

Verification:

- Multiple active rounds, out-of-round active work/step, nonexistent latest accepted와 terminal
  residual Work가 실패한다.
- 같은 날짜 복수 acceptance와 round-number 역전 fixture에서 accepted ordering이 deterministic하다.
- 네 global source가 서로 같아도 derived state와 다르면 finalization이 실패한다.

Done when: latest/active 상태를 manifest 선언만으로 위조할 수 없고 repository source에서 같은
결과를 재계산할 수 있다.

<!-- key: id=key.work.work-state-agent-evaluation.order.pc85-09 refs=key.topic.work-recovery key.role.coordinator -->
## PC85-09 Deterministic Work State Runtime

Implementation:

1. Repository root/document root를 입력으로 initialization state, active round/works/steps, early
   work, latest accepted, conflicts, dependency evaluations와 finalization gates를 반환한다.
2. Parse/policy는 deterministic functional core, filesystem discovery는 adapter로 분리한다.
3. Installed skill independence를 깨는 cross-package import를 만들지 않는다.
4. Output에 complete snapshot/source generation/path-set digest를 포함한다.
5. Reader orientation, Coordinator Context Pack, Author finalization과 release gate가 runtime output을
   직접 소비하고 자체 재해석을 제거한다.

Architecture gate:

- Shared generated copy, package-owned runtime 또는 verified parity artifact를 dependency/import
  audit로 비교한다. 단일 policy와 installed self-containment를 동시에 만족하는 방식만 수락한다.

Verification:

- 네 consumer가 동일 fixture/generation에서 canonical state와 diagnostics를 동일하게 반환한다.
- Conflict, incomplete scan, interrupted work, waiting dependency와 terminal state를 공통 fixture로
  검증한다.
- Installed package가 repository-local 다른 skill import 없이 실행된다.

Done when: active-state drift를 consumer별 parser 차이로 재현할 수 없고 incomplete coverage는 네
consumer 모두에서 fail-closed다.

<!-- key: id=key.work.work-state-agent-evaluation.order.pc85-10 refs=key.topic.integration-verification key.topic.verification -->
## PC85-10 Actual agent behavior eval runner

Implementation:

1. Fixture 생성, skill invocation, tool-call/transcript capture, before/after snapshot, expected check,
   reviewer disposition, result manifest와 attestation 생성을 하나의 runner lifecycle로 구현한다.
2. 기존 12개 scenario를 executable case로 연결하고 prompt injection, timeout, partial failure,
   missing tool과 extra-authority request를 포함한다.
3. 현재 기본 model과 다른 model/reasoning setting을 포함해 최소 두 번 반복하고 deterministic
   requirement와 allowed variance를 분리한다.
4. Subject commit/package tree, 실제 executable/config digest, invocation ID, capture time와 reviewer
   identity를 strict evidence validator에 결속한다.
5. HMAC이 reviewer의 조직적 독립성을 증명하지 못한다는 운영 trust boundary를 문서화한다.

Verification:

- All-scenario pass, behavior violation, stale transcript, forged identity, missing snapshot와
  self-review evidence를 각각 검증한다.
- Runner output은 기존 evidence validator와 RC gate에서 재검증된다.
- Repository prompt injection이 tool/authority 경계를 바꾸지 못한다.

Done when: 외부 evidence를 손으로 조립하지 않고 actual invocation에서 재현 가능하게 생성하며,
위조·stale·불완전 결과는 validator가 거절한다.

<!-- key: id=key.work.work-state-agent-evaluation.order.decision-gates refs=key.doc.decision key.boundary.stop-condition -->
## Decision and Operation Gates

1. Acceptance ordering authority는 Main/User가 수락하기 전 schema로 고정하지 않는다.
2. Work State Runtime 배치는 installed self-containment와 consumer parity evidence로 결정한다.
3. External model credential과 reviewer key는 repository source나 test fixture에 저장하지 않는다.
4. Reviewer 독립성은 validator가 기술적으로 증명할 수 없으므로 Main acceptance에서 운영
   evidence로 검토한다.

<!-- key: id=key.work.work-state-agent-evaluation.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: work recovery와 agent behavior success를 repository-derived state와 actual execution
  evidence에 결속한다.
- Required candidates: Reader/Coordinator/Author runtime·contracts, release gate consumer, work-state
  parser/policy, eval runner/scenarios/validator와 cross-skill tests
- Conditional candidates: Acceptance/finalization schema는 accepted ordering field가 추가되는 범위만
  versioned update한다.
- Excluded: S02/S03/S05 owned implementation, external provider integration와 stored credentials
- Acceptance owner: Main
- Graph handling: runtime/contract/document delta를 Linker가 분류하고 required mutation만
  owner-attested transaction으로 처리한다.

<!-- key: id=key.work.work-state-agent-evaluation.order.completion refs=key.topic.acceptance key.topic.integration-verification -->
## Completion Criteria

- [ ] Whole works tree에서 active rounds/works/steps와 latest accepted round가 파생된다.
- [ ] Multiple active round, stale pointer, nonexistent latest와 terminal residual Work가 실패한다.
- [ ] Acceptance ordering authority와 historical compatibility가 accepted Decision에 결속된다.
- [ ] Reader, Coordinator, Author와 release gate가 같은 Work State Runtime 결과를 소비한다.
- [ ] 동일 generation의 네 consumer state/diagnostics가 canonical parity를 만족한다.
- [ ] Actual eval runner가 12개 scenario를 두 setting과 최소 두 번 반복 실행한다.
- [ ] Transcript, snapshots, executable/config identity와 reviewer evidence가 current subject에 결속된다.
- [ ] S02 Work가 `complete + accepted`이고 S04 focused/package/cross-skill verification이 통과한다.

<!-- key: id=key.work.work-state-agent-evaluation.order.verification refs=key.topic.verification -->
## Verification

- Whole-tree derived-state 정상/충돌/terminal/ordering fixture
- Reader·Coordinator·Author·release cross-consumer parity suite
- Installed self-contained runtime and incomplete coverage tests
- Actual agent scenarios, repeated model/reasoning runs와 prompt-injection fixture
- Evidence forgery/staleness/identity/reviewer boundary tests
- Repository full readiness/graph validation, external-cache compileall과 `git diff --check`

<!-- key: id=key.work.work-state-agent-evaluation.order.expected-output refs=key.topic.verification key.topic.work-recovery -->
## Expected Output

- Derived global-state model and accepted ordering contract
- Deterministic Work State Runtime, canonical CLI/envelope와 four-consumer adapters
- `scripts/run_agent_evals.py`, executable fixtures, transcripts/evidence layout와 reviewer workflow
- Cross-skill parity/adversarial suites, contract/reference updates와 Progress evidence

<!-- key: id=key.work.work-state-agent-evaluation.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. Acceptance ordering authority에 복수 valid 선택이 남고 Main/User decision이 없다.
2. Installed self-containment를 깨지 않고 consumer parity를 만들 architecture가 없다.
3. External credential, reviewer key 또는 transcript를 repository에 저장해야 success가 가능하다.
4. Agent behavior를 실제로 실행하지 않고 synthetic evidence로 대체해야 한다.
5. 새 skill, external dependency 또는 provider-specific runtime이 completion 필수가 된다.
