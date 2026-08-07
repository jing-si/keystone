---
doc_type: work_order
created_at: "2026-08-07"
document_lifecycle: active
approval: {state: pending}
work_status: planned
key:
  id: key.work.production-candidate-85-closure.order
  refs:
    - key.doc.work
    - key.topic.work-sequence
    - key.topic.work-recovery
    - key.topic.finalization
    - key.topic.acceptance
    - key.topic.change-set
    - key.topic.integration-verification
    - key.topic.verification
  relations:
    depends_on:
      - target: key.work.production-control-plane-hardening.order
      - target: key.work.authority-chain-snapshot-closure.order
      - target: key.work.graph-transaction-source-correctness.order
      - target: key.work.work-state-runtime.order
      - target: key.work.agent-behavior-evaluation.order
      - target: key.work.whole-flow-self-host-e2e.order
work_gates:
  - dependency: key.work.production-control-plane-hardening.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval:
        state: accepted
    optional: false
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
  - dependency: key.work.agent-behavior-evaluation.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval:
        state: accepted
    optional: false
  - dependency: key.work.whole-flow-self-host-e2e.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval:
        state: accepted
    optional: false
---

# Production Candidate 8.5 Closure 작업서 및 Change Set

<!-- key: id=key.work.production-candidate-85-closure.order.goal refs=key.section.goal key.topic.integration-verification -->
## Goal

R010/S01-S06의 accepted correctness, authority, work-state, agent behavior와 whole-flow evidence를
independent clean CI와 release subject에 결속한다. 고정된 Quality Target이 통과한 S07 결과만
Main acceptance 후보로 제출하고, acceptance 이후 별도 Author finalization에서 R010 terminal state를
만든다. S01-S06의 기존 acceptance event/ref는 다시 쓰지 않는다.

<!-- key: id=key.work.production-candidate-85-closure.order.improvements refs=key.topic.work-sequence key.topic.verification -->
## 개선 항목

| ID | 개선 항목 | 구현 순서 | 핵심 근거 |
|---|---|---|---|
| PC85-12 | Independent RC CI와 R010 closure | 1 | clean current commit, RC version, Main acceptance와 schema-v5 finalization |

<!-- key: id=key.work.production-candidate-85-closure.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- Linux/macOS와 supported Python의 independent clean CI
- Package suites, readiness/full graph, S06 whole-flow와 actual agent evidence replay
- Installer staging/parity/forced rollback와 installed tree digest
- Current commit, package tree, installed tree, CI artifact, eval/finalization/release evidence binding
- Fixed Quality Target, finding/risk disposition과 score evidence
- `0.7.0-rc.1`, S07 Main acceptance와 post-acceptance schema-v5 terminal finalization
- New Reader terminal recovery와 production release gate

Exclude:

- Whole-flow harness 구현과 fixture-local acceptance: R010/S06
- 새 기능, relation/skill, external pilot, performance/fuzz/fault-injection program
- Marketplace publication, push/merge와 stable `1.0.0`
- CI가 지원한다고 선언하지 않은 platform을 임의로 required로 만드는 작업
- External reviewer 독립성을 repository code만으로 증명한다는 주장

<!-- key: id=key.work.production-candidate-85-closure.order.source-context refs=key.section.source-context key.topic.integration-verification -->
## Source Context

- R010/S01-S06 Work Order, Progress와 accepted/finalized verification evidence
- S06 actual whole-flow success/adversarial evidence
- Actual agent eval runner, strict evidence validator와 external reviewer operation evidence
- Package-owned Coordinator/Linker/Author runners와 Work State Runtime
- `scripts/run_release_gate.sh`, installer와 current CI configuration
- `00_docs/standards/01_key-project-standard.md`
- `00_docs/standards/skills/author/key-standard-author.md`
- `00_docs/standards/skills/coordinator/key-standard-coordinator.md`
- `00_docs/convention.md`

<!-- key: id=key.work.production-candidate-85-closure.order.pc85-12 refs=key.topic.acceptance key.topic.finalization key.topic.verification -->
## PC85-12 Independent RC CI와 R010 closure

Implementation:

1. Clean checkout에서 Linux/macOS, supported Python, package suites, readiness/full graph validation,
   S06 whole-flow, agent evidence, installer parity/rollback와 RC gate를 실행한다.
2. Windows를 공식 support matrix에 포함할 경우에만 required job으로 추가한다.
3. CI result, release plan, package/installed tree와 external evidence subject를 current commit SHA에
   결속하고 artifact/test result를 보존한다.
4. RC profile은 active R010에서 실행 가능하지만 production profile은 terminal finalization,
   clean tree, non-dev version과 fresh external evidence를 요구한다.
5. Pre-acceptance technical/Quality Target gate 뒤 version을 `0.7.0-rc.1`로 전이하고 결과를 다시
   검증해 S07 acceptance packet을 만든다.
6. Main이 S07만 새 acceptance event로 수락한 뒤 Author schema-v5 finalization이 accepted Step
   `R010/S07`과 그 acceptance ref를 기록한다.
7. Finalization은 S01-S06의 기존 accepted/finalized evidence/ref를 보존하고 모든 Work의 terminal
   상태에서 R010 Round를 닫는다.

Verification:

- CI checkout/evidence/artifact SHA mismatch가 실패한다.
- Dirty tree, `-dev` version, stale evidence, missing required job와 incomplete finalization이
  production profile을 차단한다.
- Installed tree parity, forced rollback과 repeated release plan determinism을 확인한다.
- New Reader session과 production gate가 동일 terminal work state를 반환한다.

Done when: current accepted commit의 clean independent run만 RC/production success를 만들고 모든
R010 global-state source가 terminal state를 재현한다.

<!-- key: id=key.work.production-candidate-85-closure.order.quality-target refs=key.topic.acceptance key.topic.verification -->
## Quality Target

평가 영역은 아래 11개로 고정하고 각 영역 weight는 1.0으로 동일하다. 각 점수는 0.0~10.0
범위이며 `weighted_average = sum(score × weight) / sum(weight)`로 계산한다. `Planning target`은
개선 방향을 나타내는 non-gating guide이고, normative pass threshold는 오직 `R010-QT-07`의 영역별
8.0과 `R010-QT-08`의 평균 8.5다. 점수, evaluator identity, evidence ref와 평가 subject commit은
S07 Progress가 소유하고 평가 전에 area ID·weight·threshold를 변경하지 않는다.

| 평가 영역 | Planning target (non-gating) | Weight |
|---|---:|---:|
| <!-- key: id=key.acceptance.production-score.architecture --> 아키텍처 | 9.0 | 1.0 |
| <!-- key: id=key.acceptance.production-score.authority --> 역할·권한 | 9.0 | 1.0 |
| <!-- key: id=key.acceptance.production-score.contract-alignment --> 기준서·스킬 정합성 | 8.8 | 1.0 |
| <!-- key: id=key.acceptance.production-score.reader-work-state --> Reader·Work State | 8.7 | 1.0 |
| <!-- key: id=key.acceptance.production-score.dependency --> Dependency | 8.7 | 1.0 |
| <!-- key: id=key.acceptance.production-score.graph-source --> Graph·Source | 8.7 | 1.0 |
| <!-- key: id=key.acceptance.production-score.transaction --> Transaction | 8.8 | 1.0 |
| <!-- key: id=key.acceptance.production-score.finalization --> Finalization | 8.8 | 1.0 |
| <!-- key: id=key.acceptance.production-score.coordinator-closure --> Coordinator closure | 8.7 | 1.0 |
| <!-- key: id=key.acceptance.production-score.agent-behavior --> Agent behavior | 8.5 | 1.0 |
| <!-- key: id=key.acceptance.production-score.release-operations --> Release·운영 | 8.5 | 1.0 |

<!-- key: id=key.acceptance.production-candidate.unresolved-p0-zero -->
- `R010-QT-01` Current subject의 unresolved P0 correctness 또는 authority-chain finding은 0개다.
<!-- key: id=key.acceptance.production-candidate.unresolved-p1-zero -->
- `R010-QT-02` Current subject의 미처리 P1 finding은 0개다.
<!-- key: id=key.acceptance.production-candidate.residual-risk-recorded -->
- `R010-QT-03` Current subject의 complete finding inventory가 evidence로 결속되고, 모든 residual
  risk candidate는 severity, owner, follow-up Round/proposed disposition과 근거를 가진다. Empty
  register는 explicit zero-residual-risk audit evidence가 있을 때만 통과한다.
<!-- key: id=key.acceptance.production-candidate.authority-evidence-bound -->
- `R010-QT-04` 모든 authority-bearing success는 actual state 또는 package-owned runner evidence에
  결속된다.
<!-- key: id=key.acceptance.production-candidate.normal-flow-pass -->
- `R010-QT-05` S06 actual-source normal whole-flow E2E가 current subject에서 통과한다.
<!-- key: id=key.acceptance.production-candidate.adversarial-flow-pass -->
- `R010-QT-06` S06 adversarial whole-flow가 열거된 위반을 모두 fail-closed로 차단한다.
<!-- key: id=key.acceptance.production-candidate.minimum-area-score -->
- `R010-QT-07` 고정된 11개 평가 영역 중 8.0 미만인 영역이 없다.
<!-- key: id=key.acceptance.production-candidate.weighted-average-score -->
- `R010-QT-08` 동일 weight로 계산한 11개 평가 영역 평균이 8.5 이상이다.

<!-- key: id=key.work.production-candidate-85-closure.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: Accepted subsystem evidence를 independent release subject와 evidence-based quality gate에
  결속하고 acceptance/finalization phase를 분리한다.
- Required candidates: Release gate, CI, installer, version source, finding/risk/score evidence,
  R010 finalization/global-state documents와 cross-skill tests
- Conditional candidates: Windows job은 accepted support matrix가 요구할 때만 required다.
- Excluded: S06 harness implementation, new product feature, external pilot, stable release와 publication
- Acceptance owner: Main
- Graph handling: release/finalization document delta를 package-owned Linker가 분류하고 required
  mutation만 owner-attested transaction으로 처리한다.

<!-- key: id=key.work.production-candidate-85-closure.order.completion refs=key.topic.acceptance key.topic.integration-verification -->
## Pre-Acceptance Completion Criteria

Work Order는 criterion statement만 소유하고 current state/evidence는 S07 Progress가 관리한다.

<!-- key: id=key.acceptance.production-candidate.prerequisites-accepted -->
- `R010-S07-CC-01` S01-S06이 각각 `work_status: complete`, `approval.state: accepted`이며 각
  acceptance/finalization evidence를 보존한다.
<!-- key: id=key.acceptance.production-candidate.current-agent-evidence -->
- `R010-S07-CC-02` Actual agent eval 12개 scenario의 repeated external evidence가 current commit에
  결속된다.
<!-- key: id=key.acceptance.production-candidate.independent-ci -->
- `R010-S07-CC-03` Linux/macOS와 supported Python의 independent clean CI가 통과한다.
<!-- key: id=key.acceptance.production-candidate.installer-parity -->
- `R010-S07-CC-04` Installer staging/parity/forced rollback과 installed tree digest가 통과한다.
<!-- key: id=key.acceptance.production-candidate.rc-version -->
- `R010-S07-CC-05` Version은 `0.7.0-rc.1`이며 working tree와 release subject가 clean/current다.
<!-- key: id=key.acceptance.production-candidate.quality-target-pass -->
- `R010-S07-CC-06` `R010-QT-01`부터 `R010-QT-08`까지 current subject evidence로 모두 통과한다.
<!-- key: id=key.acceptance.production-candidate.subject-binding -->
- `R010-S07-CC-07` CI, package, installed tree, agent/whole-flow와 release-plan subject digest가 같은
  current commit에 결속된다.
<!-- key: id=key.acceptance.production-candidate.acceptance-packet-ready -->
- `R010-S07-CC-08` S07 acceptance packet이 criterion state/evidence와 residual risk disposition을
  포함해 Main review가 가능한 상태다.

<!-- key: id=key.work.production-candidate-85-closure.order.post-acceptance refs=key.topic.acceptance key.topic.finalization -->
## Post-Acceptance Finalization Criteria

아래 항목은 pre-acceptance completion의 선행 조건이 아니다. Main acceptance event 이후에만
평가하며 상태/evidence는 계속 S07 Progress가 관리한다.

<!-- key: id=key.acceptance.production-finalization.main-acceptance -->
- `R010-S07-PF-01` Main이 pre-acceptance evidence를 검토하고 R010/S07만 새 acceptance event/ref로
  수락한다.
<!-- key: id=key.acceptance.production-finalization.author-finalization -->
- `R010-S07-PF-02` Author schema-v5 finalization이 S07 acceptance ref를 사용하고 S01-S06의 기존
  acceptance/finalization ref를 보존한다.
<!-- key: id=key.acceptance.production-finalization.terminal-global-state -->
- `R010-S07-PF-03` Repository-derived global state가 `active_round: none`, empty active Steps와
  `latest_accepted_round: R010`을 반환하고 residual active Work가 없다.
<!-- key: id=key.acceptance.production-finalization.reader-production-parity -->
- `R010-S07-PF-04` 새 Reader recovery와 production release gate가 동일 terminal state와 current
  accepted commit을 반환한다.
<!-- key: id=key.acceptance.production-finalization.residual-risk-acceptance-binding -->
- `R010-S07-PF-05` Main이 수락한 residual risk disposition은 S07 acceptance ref와 Author
  finalization evidence에 결속되고, zero-risk disposition도 pre-acceptance audit evidence를 보존한다.

<!-- key: id=key.work.production-candidate-85-closure.order.verification refs=key.topic.verification key.topic.integration-verification -->
## Verification

- S01-S06 package/cross-skill evidence replay와 accepted-ref identity
- S06 whole-flow success/adversarial evidence and actual agent repeated evidence
- Full package suites, readiness, repository full graph validation와 historical compatibility
- Linux/macOS supported Python CI, installer parity와 forced rollback
- Quality Target finding/risk/score evidence and current subject binding
- RC/production gate, current commit/package/installed/evidence digest equality
- Post-acceptance Reader recovery, schema-v5 finalization와 `git diff --check`

<!-- key: id=key.work.production-candidate-85-closure.order.expected-output refs=key.topic.verification key.topic.work-recovery -->
## Expected Output

- Independent CI workflows, retained artifacts/evidence와 reproducible RC gate result
- Fixed Quality Target result, finding/risk disposition과 score evidence
- `0.7.0-rc.1` version change and installed-tree parity evidence
- S01-S06 preserved acceptance evidence, S07 acceptance/schema-v5 finalization과 terminal Reader
  recovery record

<!-- key: id=key.work.production-candidate-85-closure.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. S01-S06 required evidence가 complete/accepted가 아니거나 source generation을 재현할 수 없다.
2. External agent/reviewer evidence를 위조하거나 credential/key를 repository에 저장해야 한다.
3. CI subject와 current commit, package/installed tree 또는 evidence subject가 일치하지 않는다.
4. Pre-acceptance criterion이 Main acceptance 또는 post-acceptance finalization을 순환 참조한다.
5. Main acceptance 없이 version/finalization/global state를 accepted/terminal로 바꿔야 한다.
6. Stable release, publication, external pilot 또는 새 feature가 completion 필수가 된다.
