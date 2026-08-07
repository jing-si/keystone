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
  active_steps: [R010/S01]
---

# R010 Production Control Plane Hardening 작업서 색인

R010은 zero-base review에서 확인된 cross-runtime 해석 차이와 manifest 자기신고 신뢰를 제거해,
Keystone을 사람이 감독하는 actual-state control plane의 production candidate 수준으로 끌어올린다.
S01의 correctness hardening에 이어 S02-S05는 phase-separated authority chain, graph/source
correctness, shared work state, 실제 agent/whole-flow evidence를 순서대로 결속해 평균 평가 8.5
이상의 종료 근거를 만든다.

<!-- key: id=key.work.round.r010.execution-order refs=key.topic.work-sequence key.topic.work-recovery -->
## 실행 순서

Active steps: [R010/S01]

| 순서 | Work | 경로 | 상태 | 목적 |
|---|---|---|---|---|
| S01 | Production Control Plane Hardening | `production-control-plane-hardening/00_key-index.md` | in_progress | lifecycle·transaction·source/finalization·Coordinator actual-state closure와 release evidence를 fail-closed로 정합화한다 |
| S02 | Authority Chain and Snapshot Closure | `authority-chain-snapshot-closure/00_key-index.md` | planned | complete snapshot 위에 phase-separated actor attribution과 package-owned Linker classification을 구현한다 |
| S03 | Graph, Transaction and Source Correctness | `graph-transaction-source-correctness/00_key-index.md` | planned | optional patch, SourceUnit/parser, lifecycle inheritance와 canonical mutation을 fail-closed로 정합화한다 |
| S04 | Work State and Agent Evaluation | `work-state-agent-evaluation/00_key-index.md` | planned | repository-derived state, shared Work State Runtime과 actual agent eval runner를 구현한다 |
| S05 | Production Candidate 8.5 Closure | `production-candidate-85-closure/00_key-index.md` | planned | whole-flow self-host E2E, independent CI, RC version과 R010 terminal finalization을 결속한다 |

### 평균 8.5 개선 목록

| ID | Step | 개선 항목 |
|---|---|---|
| PC85-01 | S02 | Coordinator phase-separated actual-state closure |
| PC85-02 | S02 | Assignment baseline snapshot completeness |
| PC85-03 | S03 | Optional patch fail-closed control |
| PC85-04 | S02 | Package-owned Linker classification |
| PC85-05 | S03 | SourceUnit·source parser 해석 단일화 |
| PC85-06 | S03 | Domain-aware lifecycle inheritance |
| PC85-07 | S03 | Canonical mutation strict schema |
| PC85-08 | S04 | Repository-derived global work state |
| PC85-09 | S04 | Deterministic Work State Runtime |
| PC85-10 | S04 | Actual agent behavior eval runner |
| PC85-11 | S05 | R010 whole-flow self-host E2E |
| PC85-12 | S05 | Independent RC CI와 R010 closure |

S02-S04는 current generation을 각각 캡처해 병행할 수 있다. S02와 S03의 Work completion은 S01의
`complete + accepted`를 기다리고, S05 completion은 S01-S04가 모두 `complete + accepted`인 경우만
허용한다. Dependency 평가는 자동 status transition이나 Main acceptance를 만들지 않는다.

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
3. 각 개선 항목의 구현·검증·완료 기준은 S02-S05 Work Order를 읽는다.
4. 실제 실행 상태와 resume point는 각 Work의 Progress에서 복구한다.
5. Graph 의미는 Linker가 분류하고, source document는 Author, repository source는 Main 또는
   permitted Coordinator의 authority를 유지한다.
