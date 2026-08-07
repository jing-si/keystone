---
doc_type: work_order
created_at: "2026-08-07"
document_lifecycle: active
approval: {state: pending}
work_status: planned
key:
  id: key.work.agent-behavior-evaluation.order
  refs:
    - key.doc.work
    - key.topic.work-sequence
    - key.topic.work-recovery
    - key.topic.change-set
    - key.topic.integration-verification
    - key.role.coordinator
    - key.topic.verification
  relations:
    depends_on:
      - target: key.work.authority-chain-snapshot-closure.order
      - target: key.work.graph-transaction-source-correctness.order
      - target: key.work.work-state-runtime.order
    supersedes:
      - target: key.work.work-state-agent-evaluation.order
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
  - dependency: key.work.graph-transaction-source-correctness.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval:
        state: accepted
    optional: false
  - dependency: key.work.work-state-runtime.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval:
        state: accepted
    optional: false
---

# Actual Agent Behavior Evaluation 작업서 및 Change Set

<!-- key: id=key.work.agent-behavior-evaluation.order.goal refs=key.section.goal key.topic.integration-verification -->
## Goal

기존 12개 agent scenario를 실제 skill/model invocation, tool call과 transcript, before/after
repository snapshot, expected check와 independent reviewer evidence를 생성하는 표준 runner로
실행한다. 형식·서명 validator와 actual behavior 실행기를 분리하면서도 동일 current subject에
결속한다.

<!-- key: id=key.work.agent-behavior-evaluation.order.improvements refs=key.topic.work-sequence key.topic.verification -->
## 개선 항목

| ID | 개선 항목 | 구현 순서 | 핵심 근거 |
|---|---|---|---|
| PC85-10 | Actual agent behavior eval runner | 1 | 실제 invocation·transcript·snapshot·review evidence |

<!-- key: id=key.work.agent-behavior-evaluation.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- Fixture 생성부터 signed result까지 이어지는 `scripts/run_agent_evals.py` lifecycle
- 현재 12개 scenario의 executable invocation/check adapter
- Actual transcript/tool call과 complete before/after snapshot capture
- 기본 model과 다른 model/reasoning setting, 최소 두 번 반복과 allowed variance
- Prompt injection, missing tool, timeout, partial failure와 extra-authority request
- Current commit/package tree, measured executable/config identity와 reviewer attestation binding

Exclude:

- Repository-derived work state와 consumer runtime: R010/S04
- Whole-flow product workflow: R010/S06
- Independent release CI, live Main acceptance와 terminal finalization: R010/S07
- Provider-specific runtime dependency, stored credential/key와 비대칭 attestation 도입

<!-- key: id=key.work.agent-behavior-evaluation.order.source-context refs=key.section.source-context key.topic.integration-verification -->
## Source Context

- R010/S01 evidence validator와 release/eval security implementation
- R010/S02-S04 accepted snapshot, correctness와 Work State Runtime evidence
- `scripts/agent_eval_scenarios.json`
- `scripts/validate_agent_evals.py`
- `scripts/run_release_gate.sh`
- Installed six-skill runtime contracts와 `00_docs/standards/skills/**`
- `00_docs/convention.md`

<!-- key: id=key.work.agent-behavior-evaluation.order.pc85-10 refs=key.topic.integration-verification key.topic.verification -->
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
5. Runner가 결과를 직접 self-review하지 않으며 reviewer key와 credential은 외부 trust root에 둔다.
6. HMAC은 결과 integrity를 검증하지만 reviewer의 조직적 독립성을 증명하지 못한다는 운영
   trust boundary를 문서화한다.

Verification:

- All-scenario pass, behavior violation, stale transcript, forged identity, missing snapshot와
  self-review evidence를 각각 검증한다.
- Runner output은 기존 evidence validator와 RC gate에서 재검증된다.
- Repository prompt injection이 tool/authority 경계를 바꾸지 못한다.
- Missing tool, timeout과 partial execution은 pass envelope를 만들지 않는다.

Done when: 외부 evidence를 손으로 조립하지 않고 actual invocation에서 재현 가능하게 생성하며,
위조·stale·불완전 결과는 validator가 거절한다.

<!-- key: id=key.work.agent-behavior-evaluation.order.operation-gates refs=key.boundary.stop-condition key.topic.verification -->
## Operation Gates

1. External model credential과 reviewer key는 repository source나 test fixture에 저장하지 않는다.
2. Reviewer identity/key anchor는 evaluator identity와 분리하고 Main이 운영 독립성을 검토한다.
3. Provider/model별 nondeterminism은 allowed variance로 명시하되 authority·scope invariant는 완화하지
   않는다.

<!-- key: id=key.work.agent-behavior-evaluation.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: agent behavior success를 actual execution, complete repository state와 independent review
  evidence에 결속한다.
- Required candidates: Eval runner/scenario adapters, capture/snapshot layer, validator/release
  integration, installed skill contracts와 adversarial tests
- Conditional candidates: Model/provider adapter는 current execution environment가 요구하는 최소
  boundary만 포함한다.
- Excluded: S04/S06/S07 owned implementation, external credentials와 publication
- Acceptance owner: Main
- Graph handling: runner/contract/test delta를 Linker가 분류하고 required mutation만 source owner가
  적용한다.

<!-- key: id=key.work.agent-behavior-evaluation.order.completion refs=key.topic.acceptance key.topic.integration-verification -->
## Completion Criteria

Work Order는 criterion statement만 소유하고 현재 state/evidence는 S05 Progress가 관리한다.

<!-- key: id=key.acceptance.agent-eval.runner-lifecycle -->
- `R010-S05-CC-01` Actual eval runner가 fixture부터 signed result까지 하나의 fail-closed lifecycle로
  실행한다.
<!-- key: id=key.acceptance.agent-eval.actual-invocation -->
- `R010-S05-CC-02` 12개 scenario가 actual skill/model invocation과 tool/transcript evidence에
  결속된다.
<!-- key: id=key.acceptance.agent-eval.repeated-settings -->
- `R010-S05-CC-03` 두 model/reasoning setting과 각 최소 두 번의 반복이 deterministic invariant와
  allowed variance를 구분해 통과한다.
<!-- key: id=key.acceptance.agent-eval.state-identity-binding -->
- `R010-S05-CC-04` Complete before/after snapshot, subject commit/package tree와 measured
  executable/config identity가 result에 결속된다.
<!-- key: id=key.acceptance.agent-eval.adversarial-boundaries -->
- `R010-S05-CC-05` Prompt injection, missing tool, timeout, partial failure와 extra-authority request가
  fail-closed다.
<!-- key: id=key.acceptance.agent-eval.reviewer-separation -->
- `R010-S05-CC-06` Independent reviewer evidence가 evaluator와 분리되고 HMAC trust boundary가
  명시된다.
<!-- key: id=key.acceptance.agent-eval.evidence-validation -->
- `R010-S05-CC-07` Forged, stale, incomplete 또는 self-reviewed evidence가 validator와 RC gate에서
  실패한다.
<!-- key: id=key.acceptance.agent-eval.prerequisite-verification -->
- `R010-S05-CC-08` S02-S04 Work가 `complete + accepted`이고 S05 focused/package/cross-skill
  verification이 통과한다.

<!-- key: id=key.work.agent-behavior-evaluation.order.verification refs=key.topic.verification -->
## Verification

- 12개 actual agent scenario와 repeated setting matrix
- Transcript/tool-call/snapshot/identity/reviewer evidence integrity tests
- Prompt-injection, missing-tool, timeout, partial-failure와 extra-authority fixtures
- Evidence forgery/staleness/self-review and release-gate consumption tests
- Repository full readiness/graph validation, external-cache compileall과 `git diff --check`

<!-- key: id=key.work.agent-behavior-evaluation.order.expected-output refs=key.topic.verification key.topic.work-recovery -->
## Expected Output

- `scripts/run_agent_evals.py`와 executable scenario adapters
- Transcript/tool evidence, complete snapshot과 signed results layout
- Independent reviewer operation contract와 trust-boundary documentation
- Repeated behavior results, adversarial suite와 Progress evidence

<!-- key: id=key.work.agent-behavior-evaluation.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. External credential, reviewer key 또는 sensitive transcript를 repository에 저장해야 한다.
2. Agent behavior를 실제로 실행하지 않고 synthetic evidence로 대체해야 한다.
3. Evaluator가 자기 결과를 independent review로 서명해야 completion이 가능하다.
4. 새 skill 또는 provider-specific external dependency가 completion 필수가 된다.
