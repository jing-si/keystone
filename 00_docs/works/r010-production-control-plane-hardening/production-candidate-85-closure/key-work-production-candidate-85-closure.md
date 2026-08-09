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
  - id: r010-s07-start-production-control-plane-hardening
    dependency: key.work.production-control-plane-hardening.order
    applies_to:
      steps: [S07]
      work_completion: false
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
  - id: r010-s07-completion-production-control-plane-hardening
    dependency: key.work.production-control-plane-hardening.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
  - id: r010-s07-start-authority-chain-snapshot-closure
    dependency: key.work.authority-chain-snapshot-closure.order
    applies_to:
      steps: [S07]
      work_completion: false
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
  - id: r010-s07-completion-authority-chain-snapshot-closure
    dependency: key.work.authority-chain-snapshot-closure.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
  - id: r010-s07-start-graph-transaction-source-correctness
    dependency: key.work.graph-transaction-source-correctness.order
    applies_to:
      steps: [S07]
      work_completion: false
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
  - id: r010-s07-completion-graph-transaction-source-correctness
    dependency: key.work.graph-transaction-source-correctness.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
  - id: r010-s07-start-work-state-runtime
    dependency: key.work.work-state-runtime.order
    applies_to:
      steps: [S07]
      work_completion: false
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
  - id: r010-s07-completion-work-state-runtime
    dependency: key.work.work-state-runtime.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
  - id: r010-s07-start-agent-behavior-evaluation
    dependency: key.work.agent-behavior-evaluation.order
    applies_to:
      steps: [S07]
      work_completion: false
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
  - id: r010-s07-completion-agent-behavior-evaluation
    dependency: key.work.agent-behavior-evaluation.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
  - id: r010-s07-start-whole-flow-self-host-e2e
    dependency: key.work.whole-flow-self-host-e2e.order
    applies_to:
      steps: [S07]
      work_completion: false
    condition:
      work_status: complete
      approval_state: accepted
    optional: false
  - id: r010-s07-completion-whole-flow-self-host-e2e
    dependency: key.work.whole-flow-self-host-e2e.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval_state: accepted
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
| PC85-12 | Independent RC CI와 R010 closure | 1 | clean current commit, RC version, Main acceptance와 Work State-bound schema-v6 finalization |

<!-- key: id=key.work.production-candidate-85-closure.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- Linux/macOS와 supported Python의 independent clean CI
- Package suites, readiness/full graph, S06 whole-flow와 actual agent evidence replay
- Installer staging/parity/forced rollback와 installed tree digest
- Current commit, package tree, installed tree, CI artifact, eval/finalization/release evidence binding
- Fixed Quality Target, finding/risk disposition과 score evidence
- RC support matrix, threat model, compatibility matrix, evidence retention policy, operator recovery
  guide와 diagnostic code reference
- `0.7.0-rc.1`, S07 Main acceptance와 post-acceptance Work State-bound schema-v6 terminal finalization
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

1. 평가 전에 supported OS/Python matrix를 accepted evidence로 동결하고, clean checkout에서 그
   Linux/macOS·Python 조합, package suites, readiness/full graph validation, S06 whole-flow, agent
   evidence, installer parity/rollback와 RC gate를 실행한다.
2. Windows를 공식 support matrix에 포함할 경우에만 required job으로 추가한다.
3. CI result, release plan, package/installed tree와 external evidence subject를 current commit SHA에
   결속하고 artifact/test result를 보존한다.
4. RC profile은 active R010에서 실행 가능하지만 production profile은 terminal finalization,
   clean tree, non-dev version과 fresh external evidence를 요구한다.
5. Preliminary release-plan 검사를 마친 뒤 version을 `0.7.0-rc.1`로 전이한다. Version bump가
   포함된 exact candidate에서 S05 actual agent eval, S06 whole-flow E2E와 required
   CI/package/installer gate를 모두 다시 실행하고 그 결과로 final Quality Target을 평가해 S07
   acceptance packet을 만든다.
6. Main이 S07만 새 acceptance event로 수락한 뒤 Author schema-v6 finalization이 accepted Step과
   complete Work State Runtime binding을 결속하고
   `R010/S07`과 그 acceptance ref를 기록한다.
7. Finalization은 S01-S06의 기존 accepted/finalized evidence/ref를 보존하고 모든 Work의 terminal
   상태에서 R010 Round를 닫는다.

Pre-gate policy:

- Required Step-start gate가 waiting인 동안 read-only orientation, evidence inspection과 source write
  없는 RED release-plan 설계만 허용한다.
- Repository source write, `work_status: in_progress` 전이, version/schema/authority commitment와
  acceptance 주장은 금지한다. 이 정책은 실행된 `early_work`를 주장하거나 S07을 활성화하지 않는다.
- S01-S06 각각의 finalization이 `complete`이거나 Main이 수락한 `waived`이고, Work acceptance ref,
  finalization manifest/envelope digest와 package-owned Author runner pass가 결속된 뒤에만 S07
  implement assignment를 시작한다. Waiver에는 reason과 follow-up이 모두 필요하다.

Release subject lineage:

- `rc_candidate_subject`는 version bump를 포함한 clean candidate commit SHA, repository tree digest,
  package tree digest와 `0.7.0-rc.1`을 exact identity로 가진다. S05, S06와 required CI/package/installer
  rerun evidence는 모두 이 subject에 직접 결속한다.
- `terminal_subject`는 post-acceptance Author finalization을 포함한 exact terminal commit/tree이며
  `parent_candidate`가 `rc_candidate_subject`의 commit/tree digest와 정확히 일치해야 한다.
- Finalization 이후 delta가 declared docs-only finalization path set에만 있고 package tree digest가
  `rc_candidate_subject`와 동일하면 terminal subject에서 docs readiness, repository full graph,
  schema-v6 finalization, Reader recovery와 production gate만 다시 실행하고 RC technical evidence를
  lineage로 재사용할 수 있다.
- Package tree parity가 깨지거나 docs-only path set 밖의 runtime/config/schema/test/eval/CI source가
  바뀌면 새 `rc_candidate_subject`로 분기해 S05, S06, required CI/package/installer를 포함한 full
  terminal rerun을 수행하고 새 acceptance packet과 Main acceptance가 필요하다.

Verification:

- CI checkout/evidence/artifact SHA mismatch가 실패한다.
- Dirty tree, `-dev` version, stale evidence, missing required job와 incomplete finalization이
  production profile을 차단한다.
- Installed tree parity, forced rollback과 repeated release plan determinism을 확인한다.
- Version-bumped `rc_candidate_subject`의 S05/S06/CI rerun과 terminal parent lineage를 확인한다.
- Finalization delta가 docs-only path set과 package parity 조건을 만족하는지 검사하고, 조건 밖
  변경은 full terminal rerun 없이는 차단한다.
- New Reader session과 production gate가 동일 terminal work state를 반환한다.

Done when: current accepted commit의 clean independent run만 RC/production success를 만들고 모든
R010 global-state source가 terminal state를 재현한다.

<!-- key: id=key.work.production-candidate-85-closure.order.quality-target refs=key.topic.acceptance key.topic.verification -->
## Quality Target

평가 영역은 아래 11개로 고정하고 각 영역 weight는 1.0으로 동일하다. 각 final score는 0.0~10.0
범위이며 `weighted_average = sum(final_score × weight) / sum(weight)`로 계산한다. `Planning target`은
개선 방향을 나타내는 non-gating guide다. Hard threshold는 모든 영역 8.0 이상, 전체 평균 8.5
이상이고 아래 critical six 영역은 각각 8.5 이상이다. 내부 평균 8.7은 release-improvement를 위한
non-gating target이며 미달 결과를 숨기지 않고 기록한다. 이 절의 `current subject`는 version bump와
필수 rerun을 포함한 exact `rc_candidate_subject`를 뜻한다.

Rubric version은 `R010-QS-v1`로 고정한다. Package-owned runner는 finding/E2E/CI와 subject digest를
기계적으로 검증해 eligibility와 score cap만 결정하고 점수를 부여하지 않는다. 서로 독립된 두
reviewer가 같은 rubric/subject/evidence를 평가하며, score 차이가 0.5를 초과하거나 cap 적용에
불일치하면 두 reviewer와 다른 adjudicator가 최종 점수를 판정한다. 차이가 0.5 이하이고 cap
불일치가 없으면 두 점수 평균을 사용한다. 어느 경우든 final score는 applicable mechanical cap을
넘을 수 없고, mechanical 결과가 reviewer 점수를 올릴 수 없다. 각 score evidence는 rubric version,
reviewer/adjudicator identity, exact subject commit/tree/package digest와 evidence digest를 attestation한다.

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

Score anchors:

| Score | Evidence anchor |
|---:|---|
| 8.0 | Required contract와 current-subject evidence가 통과하고 known P0/P1이 없으나 운영 깊이 또는 독립 검증이 최소 수준이다. |
| 8.5 | 정상·adversarial 증거와 독립 reviewer 근거가 재현 가능하며 production-candidate 기준을 충족한다. |
| 8.8 | Cross-runtime/authority 경계와 recovery 증거가 일관되고 남은 위험이 낮으며 명시적으로 통제된다. |
| 9.0 | 다양한 지원 환경과 반복 실행에서 강한 독립 증거, deterministic recovery와 운영 문서가 완결된다. |
| 9.5 | 장기간 또는 외부 pilot을 포함한 폭넓은 production evidence가 있고 residual uncertainty가 매우 낮다. |

Mechanical caps는 해당 조건의 모든 관련 영역에 적용하며 여러 cap이 겹치면 가장 낮은 값을 쓴다.

| Condition | Mechanical result/cap |
|---|---|
| Unresolved P0 | `R010-QT-01` hard fail, affected area 최대 5.0 |
| Unresolved P1 | `R010-QT-02` hard fail, affected area 최대 7.9 |
| S06 normal/adversarial E2E missing 또는 fail | `R010-QT-05`/`06` hard fail; Graph·Source, Transaction, Finalization, Coordinator closure, Agent behavior 최대 7.9 |
| Required independent CI missing 또는 fail | `R010-S07-CC-03` hard fail; Release·운영 최대 7.9 |
| External pilot 없음 | hard fail 아님; 모든 영역 최대 8.9 |

Critical six는 역할·권한, Graph·Source, Transaction, Finalization, Coordinator closure와
Release·운영이다. 평가 전에 rubric version, anchor, area ID, weight, critical-set 또는 cap을 바꾸면
새 rubric version과 전체 재평가가 필요하다.

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
<!-- key: id=key.acceptance.production-candidate.rubric-frozen -->
- `R010-QT-09` 평가 전에 `R010-QS-v1`, score anchors, mechanical caps, 11개 area ID/weight,
  critical six와 evaluation subject를 동결하고 그 digest를 기록한다.
<!-- key: id=key.acceptance.production-candidate.mechanical-independent-review -->
- `R010-QT-10` Package-owned mechanical eligibility/cap evidence와 서로 독립된 두 reviewer score가
  분리되어 존재하며 rubric/evaluator/subject/evidence attestation이 모든 score에 존재한다.
<!-- key: id=key.acceptance.production-candidate.score-adjudication -->
- `R010-QT-11` Reviewer score 차이가 0.5 이하이면 평균을 사용하고, 0.5 초과 또는 cap 불일치는
  두 reviewer와 다른 adjudicator의 판정 evidence를 요구한다. 편차가 없거나 adjudication이
  불필요한 경우도 그 계산 evidence를 명시한다.
<!-- key: id=key.acceptance.production-candidate.critical-area-floor -->
- `R010-QT-12` 역할·권한, Graph·Source, Transaction, Finalization, Coordinator closure와
  Release·운영 final score가 각각 8.5 이상이다.
<!-- key: id=key.acceptance.production-candidate.internal-average-target -->
- `R010-QT-13` 11개 영역의 내부 평균 8.7 목표 달성 여부와 gap disposition을 기록한다. 이 항목은
  non-gating target이며 8.7 미달만으로 `R010-QT-08` pass를 뒤집지 않는다.

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
- `R010-S07-CC-01` S01-S06이 각각 `work_status: complete`, `approval_state: accepted`이며 각
  finalization은 `complete` 또는 Main-accepted `waived`다. Progress에 waiver reason/follow-up,
  acceptance ref, finalization manifest/envelope digest와 package-owned Author runner pass를 포함한
  exact closure evidence를 보존한다.
<!-- key: id=key.acceptance.production-candidate.current-agent-evidence -->
- `R010-S07-CC-02` Actual agent eval 12개 scenario의 repeated external evidence가 exact
  `rc_candidate_subject`에 결속된다.
<!-- key: id=key.acceptance.production-candidate.independent-ci -->
- `R010-S07-CC-03` Linux/macOS와 supported Python의 independent clean CI가 통과한다.
<!-- key: id=key.acceptance.production-candidate.installer-parity -->
- `R010-S07-CC-04` Installer staging/parity/forced rollback과 installed tree digest가 통과한다.
<!-- key: id=key.acceptance.production-candidate.rc-version -->
- `R010-S07-CC-05` Version은 `0.7.0-rc.1`이며 working tree와 release subject가 clean/current다.
<!-- key: id=key.acceptance.production-candidate.quality-target-pass -->
- `R010-S07-CC-06` Hard gate인 `R010-QT-01`부터 `R010-QT-12`까지 current subject evidence로
  통과하고 non-gating `R010-QT-13` 결과와 gap disposition을 기록한다.
<!-- key: id=key.acceptance.production-candidate.subject-binding -->
- `R010-S07-CC-07` CI, package, installed tree, agent/whole-flow와 release-plan digest가 exact
  `rc_candidate_subject` commit/tree/package identity에 결속된다.
<!-- key: id=key.acceptance.production-candidate.acceptance-packet-ready -->
- `R010-S07-CC-08` S07 acceptance packet이 criterion state/evidence와 residual risk disposition을
  포함해 Main review가 가능한 상태다.
<!-- key: id=key.acceptance.production-candidate.rc-subject-rerun -->
- `R010-S07-CC-09` Version bump가 포함된 `rc_candidate_subject`에서 S05 actual agent eval, S06
  whole-flow E2E, required CI/package/installer gate가 모두 다시 실행되어 exact subject digest에
  결속된다.
<!-- key: id=key.acceptance.production-candidate.release-documentation-pack -->
- `R010-S07-CC-10` 평가 전에 동결된 RC support matrix, threat model, compatibility matrix, evidence
  retention policy, operator recovery guide와 diagnostic code reference가 current candidate와 release
  evidence를 정확히 설명한다.

<!-- key: id=key.work.production-candidate-85-closure.order.post-acceptance refs=key.topic.acceptance key.topic.finalization -->
## Post-Acceptance Finalization Criteria

아래 항목은 pre-acceptance completion의 선행 조건이 아니다. Main acceptance event 이후에만
평가하며 상태/evidence는 계속 S07 Progress가 관리한다.

<!-- key: id=key.acceptance.production-finalization.main-acceptance -->
- `R010-S07-PF-01` Main이 pre-acceptance evidence를 검토하고 R010/S07만 새 acceptance event/ref로
  수락한다.
<!-- key: id=key.acceptance.production-finalization.author-finalization -->
- `R010-S07-PF-02` Author schema-v6 finalization이 S07 acceptance ref와 complete Work State Runtime
  binding을 사용하고 S01-S06의 기존
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
<!-- key: id=key.acceptance.production-finalization.terminal-subject-lineage -->
- `R010-S07-PF-06` Exact `terminal_subject.parent_candidate`가 accepted `rc_candidate_subject`와
  일치한다. Finalization 뒤 docs-only path set과 package parity를 만족하면 terminal-only 검증이
  통과하고, 그 밖의 변경이면 새 candidate의 S05/S06/CI/package/installer full rerun과 새 Main
  acceptance가 존재한다.

<!-- key: id=key.work.production-candidate-85-closure.order.verification refs=key.topic.verification key.topic.integration-verification -->
## Verification

- S01-S06 package/cross-skill evidence replay와 accepted-ref identity
- S06 whole-flow success/adversarial evidence and actual agent repeated evidence
- Full package suites, readiness, repository full graph validation와 historical compatibility
- Linux/macOS supported Python CI, installer parity와 forced rollback
- Quality Target finding/risk/score evidence and current subject binding
- `R010-QS-v1` mechanical caps, independent dual-review, adjudication과 score attestation
- RC/production gate, current commit/package/installed/evidence digest equality
- `rc_candidate_subject` version-bump rerun과 `terminal_subject.parent_candidate` lineage
- S01-S06 finalization state/ref/manifest/envelope/Author-runner prerequisite evidence
- Post-acceptance Reader recovery, schema-v6 finalization와 `git diff --check`

<!-- key: id=key.work.production-candidate-85-closure.order.expected-output refs=key.topic.verification key.topic.work-recovery -->
## Expected Output

- Independent CI workflows, retained artifacts/evidence와 reproducible RC gate result
- Fixed Quality Target result, finding/risk disposition과 score evidence
- `0.7.0-rc.1` version change and installed-tree parity evidence
- 평가 전에 동결된 RC support matrix, threat model, compatibility matrix, evidence retention policy,
  operator recovery guide와 diagnostic code reference
- Exact `rc_candidate_subject`/`terminal_subject` lineage 및 version-bump/terminal rerun evidence
- S01-S06 preserved acceptance evidence, S07 acceptance/schema-v6 finalization과 terminal Reader
  recovery record

<!-- key: id=key.work.production-candidate-85-closure.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. S01-S06 required evidence가 complete/accepted가 아니거나 exact finalization closure evidence와
   source generation을 재현할 수 없다.
2. External agent/reviewer evidence를 위조하거나 credential/key를 repository에 저장해야 한다.
3. CI subject와 current commit, package/installed tree 또는 evidence subject가 일치하지 않는다.
4. Version-bumped candidate에서 S05/S06/required CI를 다시 실행하지 않았거나 terminal delta가
   docs-only/package-parity 정책을 벗어났는데 full rerun과 새 acceptance가 없다.
5. Pre-acceptance criterion이 Main acceptance 또는 post-acceptance finalization을 순환 참조한다.
6. Main acceptance 없이 version/finalization/global state를 accepted/terminal로 바꿔야 한다.
7. Stable release, publication, external pilot 또는 새 feature가 completion 필수가 된다.
