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
      steps: [S05]
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
  - dependency: key.work.graph-transaction-source-correctness.order
    applies_to:
      steps: [S05]
      work_completion: false
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
  - dependency: key.work.graph-transaction-source-correctness.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
  - dependency: key.work.work-state-runtime.order
    applies_to:
      steps: [S05]
      work_completion: false
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
  - dependency: key.work.work-state-runtime.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval_state: accepted
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
- Invocation adapter identity, complete prompt/tool schema binding과 provider-asserted model identity
- Setting × repeat × scenario matrix wire migration과 evaluator negative-control calibration
- Isolated fixture, pre-sign redaction과 bounded cost/timeout/run budget

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
2. 각 executable adapter는 `adapter_id`, `adapter_digest`, `fixture_id`, `fixture_digest`,
   `system_prompt_digest`, `developer_prompt_digest`, `tool_schema_digest`, executable/config digest와
   invocation ID를 기록한다. 요청 model claim은 provider response가 주장한 model identity와 별도
   field로 보존하며 둘 중 하나를 실제 측정 identity로 승격하지 않는다.
3. 기존 12개 scenario를 executable case로 연결하고 prompt injection, timeout, partial failure,
   missing tool과 extra-authority request를 포함한다.
4. Evidence wire를 exact ordered scenario-once 배열에서 `setting_id × repeat_id × scenario_id` cell로
   migration한다. 최소 두 setting과 setting별 최소 두 repeat의 exact Cartesian coverage, tuple
   uniqueness와 per-cell subject/adapter/snapshot/result digest를 검증한다.
5. 각 cell은 별도 temporary fixture, cache와 invocation context를 사용하고 immutable baseline,
   complete before/after snapshot과 allowed output path를 기록한다. Credential, token과 sensitive
   transcript는 외부 evidence 저장·HMAC signing 전에 deterministic redaction하고 redaction manifest와
   digest를 결속한다.
6. Runner가 알지 못하는 reviewer hidden variation과 의도적으로 scope/authority invariant를 위반하는
   negative-control invocation을 포함한다. Control을 탐지하지 못하거나 hidden variation이 runner에
   노출되면 suite는 실패한다.
7. Setting/cell별 timeout·attempt·token/cost 상한과 suite wall-clock/run budget을 시작 전에 고정하고,
   초과·부분 실행·unknown cost는 pass envelope를 만들지 않는다.
8. Subject commit/package tree, 실제 executable/config digest, invocation ID, capture time와 reviewer
   identity를 strict evidence validator에 결속한다.
9. Runner가 결과를 직접 self-review하지 않으며 reviewer key와 credential은 외부 trust root에 둔다.
10. HMAC은 결과 integrity를 검증하지만 reviewer의 조직적 독립성을 증명하지 못한다는 운영
   trust boundary를 문서화한다.

Verification:

- All-scenario pass, behavior violation, stale transcript, forged identity, missing snapshot와
  self-review evidence를 각각 검증한다.
- Scenario spec, results validator와 release consumer를 같은 versioned matrix wire로 migration하고
  legacy exactly-once evidence가 S05 completion이나 새 RC pass를 만들지 못하게 한다.
- Adapter/prompt/tool schema/model claim binding과 isolated-fixture cross-cell contamination을 검증한다.
- Negative control detection, reviewer hidden-variation secrecy와 redaction-before-sign ordering을
  검증한다.
- Per-cell/suite timeout, attempt, token/cost와 run budget 초과를 검증한다.
- Runner output은 migrated evidence validator와 RC gate에서 재검증된다.
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
4. Provider-asserted model identity는 request claim, measured executable/config identity나 independent
   reviewer identity와 합치지 않는다.
5. Redaction은 attestation 전에 끝나야 하며 원문 secret을 signed/persisted evidence로 남기지 않는다.

<!-- key: id=key.work.agent-behavior-evaluation.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: agent behavior success를 actual execution, complete repository state와 independent review
  evidence에 결속한다.
- Required candidates: Eval runner/scenario adapters, capture/snapshot layer, validator/release
  integration, matrix schema migration, redaction/control/budget policy, installed skill contracts와
  adversarial tests
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
<!-- key: id=key.acceptance.agent-eval.start-gates -->
- `R010-S05-CC-09` S02-S04가 모두 `complete + accepted`이기 전 S05 start gates는 `waiting`이며
  read-only 조사와 문서 fixture 설계만 허용하고 runtime/test/code/config/schema write,
  `in_progress` 전이와 canonical schema commitment를 차단한다.
<!-- key: id=key.acceptance.agent-eval.adapter-binding -->
- `R010-S05-CC-10` Invocation adapter, fixture, system/developer prompt, tool schema,
  executable/config와 invocation identity가 digest로 결속되고 request model claim과
  provider-asserted identity가 구분된다.
<!-- key: id=key.acceptance.agent-eval.matrix-schema-migration -->
- `R010-S05-CC-11` Scenario spec, validator와 release consumer가 setting × repeat × scenario matrix
  schema로 함께 migration되고 exact Cartesian coverage와 tuple uniqueness를 검증한다.
<!-- key: id=key.acceptance.agent-eval.fixture-redaction -->
- `R010-S05-CC-12` 각 matrix cell이 isolated fixture와 complete snapshot을 사용하고 sensitive bytes가
  persistence/signing 전에 redacted되며 redaction manifest digest가 검증된다.
<!-- key: id=key.acceptance.agent-eval.negative-control-hidden-review -->
- `R010-S05-CC-13` Seeded negative control은 반드시 거절되고 reviewer hidden variation은 runner에
  노출되지 않은 채 independent disposition에 결속된다.
<!-- key: id=key.acceptance.agent-eval.execution-budget -->
- `R010-S05-CC-14` Per-cell과 suite timeout, attempts, token/cost와 wall-clock/run budget이 사전에
  고정되고 초과·unknown·partial execution은 fail-closed다.

<!-- key: id=key.work.agent-behavior-evaluation.order.verification refs=key.topic.verification -->
## Verification

- 12개 actual agent scenario의 exact setting × repeat matrix와 schema migration tests
- Adapter/prompt/tool-schema/model-claim/transcript/snapshot/identity integrity tests
- Isolated fixture, pre-sign redaction, seeded negative-control와 hidden-reviewer tests
- Per-cell/suite cost, timeout, attempt와 run-budget boundary tests
- Prompt-injection, missing-tool, timeout, partial-failure와 extra-authority fixtures
- Evidence forgery/staleness/self-review and release-gate consumption tests
- Repository full readiness/graph validation, external-cache compileall과 `git diff --check`

<!-- key: id=key.work.agent-behavior-evaluation.order.expected-output refs=key.topic.verification key.topic.work-recovery -->
## Expected Output

- `scripts/run_agent_evals.py`와 executable scenario adapters
- Versioned matrix evidence, transcript/tool evidence, complete isolated snapshot과 signed results layout
- Pre-sign redaction manifest, negative-control/hidden-review evidence와 budget accounting
- Independent reviewer operation contract와 trust-boundary documentation
- Repeated behavior results, adversarial suite와 Progress evidence

<!-- key: id=key.work.agent-behavior-evaluation.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. External credential, reviewer key 또는 sensitive transcript를 repository에 저장해야 한다.
2. Agent behavior를 실제로 실행하지 않고 synthetic evidence로 대체해야 한다.
3. Evaluator가 자기 결과를 independent review로 서명해야 completion이 가능하다.
4. 새 skill 또는 provider-specific external dependency가 completion 필수가 된다.
5. S02-S04 start gates가 열리기 전에 runtime/test/code/config/schema write, `in_progress` 전이나
   canonical schema commitment가 필요하다.
