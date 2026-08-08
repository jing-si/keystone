---
doc_type: work_round
created_at: "2026-08-07"
document_lifecycle: active
approval: {state: pending}
round_status: active
key:
  id: key.work.round.r010-production-control-plane-hardening.index
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.artifact-graph
    - key.topic.finalization
    - key.role.coordinator
    - key.topic.verification
global_state:
  active_round: R010
  latest_accepted_round: R009
  active_steps: []
---

# R010 Production Control Plane Hardening 작업서 색인

R010은 zero-base review에서 확인된 cross-runtime 해석 차이와 manifest 자기신고 신뢰를 제거해,
Keystone을 사람이 감독하는 actual-state control plane의 production candidate 수준으로 끌어올린다.
S01의 correctness hardening에 이어 S02-S07은 phase-separated authority chain, graph/source
correctness, shared work state, 실제 agent behavior, whole-flow와 independent release evidence를
서로 다른 acceptance 단위로 결속해 평균 평가 8.5 이상의 종료 근거를 만든다.

<!-- key: id=key.work.round.r010.execution-order refs=key.topic.work-sequence key.topic.work-recovery -->
## 실행 순서

Active steps: []

| 순서 | Work | 경로 | 상태 | 목적 |
|---|---|---|---|---|
| S01 | Production Control Plane Hardening | `production-control-plane-hardening/00_key-index.md` | complete, accepted | lifecycle·transaction·source/finalization·Coordinator actual-state closure와 release evidence를 fail-closed로 정합화했다 |
| S02 | Authority Chain and Snapshot Closure | `authority-chain-snapshot-closure/00_key-index.md` | complete, accepted | complete snapshot과 phase-separated actor attribution을 actual-state evidence로 닫았다 |
| S03 | Graph, Transaction and Source Correctness | `graph-transaction-source-correctness/00_key-index.md` | planned | package-owned classification, mutation-bearing optional 금지, SourceUnit/parser, lifecycle와 canonical mutation을 정합화한다 |
| S04 | Deterministic Work State Runtime | `work-state-runtime/00_key-index.md` | planned | repository-derived global state와 네 consumer의 canonical runtime parity를 구현한다 |
| S05 | Actual Agent Behavior Evaluation | `agent-behavior-evaluation/00_key-index.md` | planned | 실제 skill/model invocation으로 setting×repeat×12 scenario evidence와 negative control을 생성·검증한다 |
| S06 | Whole-Flow Self-Host E2E | `whole-flow-self-host-e2e/00_key-index.md` | planned | 실제 Keystone source의 phase-separated 정상·adversarial·crash/resume workflow를 검증한다 |
| S07 | Production Candidate 8.5 Closure | `production-candidate-85-closure/00_key-index.md` | planned | independent CI, objective scorecard, RC/terminal subject lineage와 R010 finalization을 결속한다 |

### 평균 8.5 개선 목록

| ID | Step | 개선 항목 |
|---|---|---|
| PC85-01 | S02 | Coordinator phase-separated actual-state closure |
| PC85-02 | S02 | Assignment baseline snapshot completeness |
| PC85-03 | S03 | Optional patch fail-closed control |
| PC85-04 | S03 | Package-owned Linker classification |
| PC85-05 | S03 | SourceUnit·source parser 해석 단일화 |
| PC85-06 | S03 | Domain-aware lifecycle inheritance |
| PC85-07 | S03 | Canonical mutation strict schema |
| PC85-08 | S04 | Repository-derived global work state |
| PC85-09 | S04 | Deterministic Work State Runtime |
| PC85-10 | S05 | Actual agent behavior eval runner |
| PC85-11 | S06 | R010 whole-flow self-host E2E |
| PC85-12 | S07 | Independent RC CI와 R010 closure |
| PC85-13 | S02-S07 | Step-start gate와 finalization prerequisite closure |
| PC85-14 | S07 | RC candidate→terminal subject lineage |
| PC85-15 | S07 | Versioned scoring rubric와 independent evaluation |

S02의 Step start와 Work completion은 S01의 `complete + accepted`를 기다린다. S03과 S04는 S02의
accepted complete snapshot/phase contract 뒤 병행할 수 있고, S05의 Step start/completion은
S02-S04의 `complete + accepted`를 기다린다. S06은 S01-S05, S07은 S01-S06의
`complete + accepted`와 아래 finalization prerequisite closure를 모두 소비한다. Dependency 평가는
자동 status transition이나 Main acceptance를 만들지 않는다.

S02는 `R010/S02/main-acceptance`로 complete and accepted됐고 schema-v5 finalization을 완료했다.
S03/S04의 start gate는 satisfied지만 현재 generation에서는 planned/Inactive이며, 활성화는 별도
source transition으로 수행한다.

<!-- key: id=key.work.round.r010.pre-gate-policy refs=key.topic.work-sequence key.topic.work-recovery -->
### Pre-gate activity policy

Required Step-start gate가 `waiting`인 동안 허용되는 것은 read-only 분석, interface 비교와 Work
Order/Progress 안의 RED case matrix·fixture design뿐이다. Runtime/test/code/config/schema source write,
`work_status: in_progress` 전이와 canonical wire/schema commitment는 금지한다. 실제 선작업이 발생한
경우에만 해당 Progress에 원인, 완료 범위, 남은 범위와 `status_effect: none`을 `early_work`로
기록하며, 이 기록은 Step 활성화나 implement authority를 만들지 않는다.

<!-- key: id=key.work.round.r010.prerequisite-closure refs=key.topic.finalization key.topic.work-sequence key.topic.verification -->
### Integration prerequisite closure

S06은 S01-S05, S07은 S01-S06 각각에 대해 `work_status: complete`, `approval.state: accepted`뿐 아니라
required finalization이 `complete`이거나 Main이 명시적으로 수락한 `waived`임을 확인한다. Evidence는
waiver reason/follow-up, acceptance ref, finalization manifest/envelope digest와 package-owned Author
runner pass를 포함한다. 이 조건은 현재 WorkGate condition에 임의 field를 추가하지 않고 S04 Work
State Runtime이 파생하고 S02 Coordinator actual-state verifier와 S06/S07 prerequisite criterion이
검증한다.

<!-- key: id=key.work.round.r010.quality-target refs=key.topic.acceptance key.topic.verification -->
## Quality Target

R010의 점수 목표는 구현량이 아니라 S07 Work Order의 stable Quality Target criterion과 실제
evidence로 판정한다. 종료 시 unresolved P0/P1 finding은 0개여야 하고, residual risk candidate는
severity·owner·follow-up Round/disposition·근거를 모두 가져야 한다. 모든
authority-bearing success는 actual
state 또는 package-owned runner evidence에 결속되어야 하며 정상·adversarial whole-flow가 모두
통과해야 한다. Hard minimum은 평가 영역별 8.0 이상과 전체 평균 8.5 이상이다. Internal target은
전체 평균 8.7 이상이며 역할·권한, Graph·Source, Transaction, Finalization, Coordinator closure와
Release·운영의 critical floor는 8.5다. 점수는 평가 전에 고정된 versioned rubric/cap, mechanical
evaluation과 independent reviewer evaluation 및 편차 adjudication evidence로만 확정한다.

Residual risk의 severity·owner·follow-up/disposition·evidence는 pre-acceptance에 완성하고, 실제
acceptance ref 결속은 S07 post-acceptance finalization에서 수행한다.

상세 판정 기준과 상태/evidence 소유자는 각각 S07 Work Order의 `R010-QT-*`와 S07 Progress다.

<!-- key: id=key.work.round.r010.subject-lineage refs=key.topic.acceptance key.topic.finalization key.topic.verification -->
## Release subject lineage

S07은 runtime·test·contract와 `0.7.0-rc.1`이 고정된 `rc_candidate_subject`에서 S05/S06, independent
CI와 RC gate를 다시 실행한다. Main acceptance 뒤 docs-only finalization이 만든 `terminal_subject`는
parent candidate, package-tree parity, global-state/finalization digest를 기록한다. Terminal commit의
agent/whole-flow evidence를 재사용하려면 subject scope와 package parity가 schema로 증명돼야 하며,
그렇지 않으면 terminal subject에서 다시 실행한다.

<!-- key: id=key.work.round.r010.boundaries refs=key.boundary.scope-control key.topic.verification -->
## Round 경계

- Schema v1 read compatibility와 이미 accepted된 finalization history는 보존한다.
- 새 transaction과 closure evidence는 strict canonical wire로 수렴한다.
- Publication, push, merge, 외부 소비 프로젝트 변경과 dependency 추가는 범위 밖이다.
- 성능 최적화와 repository-wide metadata migration은 correctness closure 뒤의 별도 후보로 남긴다.

<!-- key: id=key.work.round.r010.reading-rules refs=key.topic.work-recovery -->
## 복구 규칙

1. R010의 현재 correctness hardening 목표·범위·완료 기준은 S01 Work Order를 읽는다.
2. 평균 8.5 개선 목록과 Step 배치는 이 round index를 읽는다.
3. 각 개선 항목의 구현·검증·완료 기준은 S02-S07 Work Order를 읽는다.
4. 실제 실행 상태와 resume point는 각 Work의 Progress에서 복구한다.
5. Graph 의미는 Linker가 분류하고, source document는 Author, repository source는 Main 또는
   permitted Coordinator의 authority를 유지한다.
