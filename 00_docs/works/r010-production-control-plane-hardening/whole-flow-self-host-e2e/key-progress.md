---
doc_type: progress
created_at: "2026-08-07"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-11", accepted_by: main}
work_status: complete
step_ref: R010/S06
work_ref: R010/whole-flow-self-host-e2e
finalization: {state: complete, acceptance_ref: R010/S06/main-acceptance}
key:
  id: key.work.whole-flow-self-host-e2e.progress
  refs:
    - key.topic.progress-update
    - key.topic.work-recovery
    - key.topic.artifact-graph
    - key.topic.verification
    - key.acceptance.core-simplification.standards-first
    - key.acceptance.core-simplification.graph-core
    - key.acceptance.core-simplification.work-state-core
    - key.acceptance.core-simplification.default-no-secret
    - key.acceptance.core-simplification.agent-gate-removed
    - key.acceptance.core-simplification.closure-minimum
    - key.acceptance.core-simplification.compatibility
    - key.acceptance.core-simplification.verification
    - key.acceptance.core-simplification.scope-discipline
---

# Standards-to-Product Core Simplification 진행 기록

## 현재 상태

- Step: R010/S06
- Work status: complete
- Approval state: accepted
- Active: false
- Finalization state: complete
- Acceptance ref: `R010/S06/main-acceptance`
- Step-start dependency: satisfied — S05 `complete + accepted` 및 schema-v4 finalization complete
- Activation: 2026-08-10 S05 finalization 후 R010의 유일 active Step으로 전환했다.
- Boundary: 현재 S06을 취소하거나 새 Step으로 대체하지 않는다. Code 구현 전이고 기존 Goal이
  HMAC·external evidence 제거와 core 단순화로 동일하므로, active Work 안에서 Lean Core Contract와
  위험 기반 계층형 검증으로 범위를 좁힌다.
- Accepted planning evidence: S05의 no-secret inventory와 2026-08-11 사용자 결정에 따라 일반 작업은
  관련 문서·scope/diff·targeted test·필요한 Progress만 요구하고 graph/package/installer/historical
  검증은 변경 성격이나 release 요청에 따라 escalation한다.
- Implementation: S06-A~C의 package contract, current closure/graph path, release gate, installer와
  corresponding test 변경을 완료했다.
- Verification: Author 96, Coordinator 34, Linker 367, shared 41 tests가 통과했다. Pre-acceptance
  Work State는 `R010/S06`을 유일 active Step으로 복구했고 repository graph validation은 307/307
  source, error 0, warning 0으로 통과했다. docs/repository readiness, compileall, release plan list와
  installer temporary staging/parity/rollback도 통과했다.
- Acceptance: Main이 current diff, Lean Core 의미와 검증 결과를 검토해 2026-08-11
  `R010/S06/main-acceptance`로 수락했다.
- Finalization: 새 Lean Core 계약에 따라 별도 manifest, HMAC, external evidence 폴더를 만들지 않고
  repository Work/Progress 상태와 local verification evidence로 complete 처리했다.
- Post-acceptance state: Work State가 S06 dependency를 satisfied로 판정하고 `R010/S07`을 유일 active
  Step으로 복구했다.
- Resume point: active R010/S07에서 PWF-01~04 fixture와 product-flow verification을 확정한다.
  명시적 release 요청이 없으므로 clean-tree full release/postflight는 실행하지 않았다.

## Criterion Status

| Criterion ID | State | Evidence ref | 비고 |
|---|---|---|---|
| `key.acceptance.core-simplification.standards-first` | verified | five standards; three package contracts/references; README | source와 package current meaning 정렬 완료 |
| `key.acceptance.core-simplification.graph-core` | verified | Linker 367 tests; repository graph 307/307 | SourceUnit·locator·lifecycle·impact/transaction core 보존 |
| `key.acceptance.core-simplification.work-state-core` | verified | Work State pass; shared recovery/parity tests | `R010/S06` deterministic recovery 확인 |
| `key.acceptance.core-simplification.default-no-secret` | verified | current Coordinator schema v1; graph schema v1/direct transaction | key/evidence-root 없이 current path 통과 |
| `key.acceptance.core-simplification.agent-gate-removed` | verified | canonical 12-step release plan; retired files absent | agent evidence CLI/spec/release step 제거 |
| `key.acceptance.core-simplification.closure-minimum` | verified | current closure tests; owner producer absence tests | scope/diff/verification/Progress 중심으로 축소 |
| `key.acceptance.core-simplification.compatibility` | verified | historical v2/v3 structural-only tests; Author package suite | retired wire는 read/diagnostic 전용으로 유지 |
| `key.acceptance.core-simplification.verification` | verified | 96+34+367+41 tests; readiness/graph/installer checks | release full run만 명시적 요청까지 보류 |
| `key.acceptance.core-simplification.scope-discipline` | verified | fresh consumer search; diff/path review | R011·historical Work·installed skill tree 미수정 |

## 기존 S06 계획 disposition

- 10개 adversarial + 7개 crash/resume matrix, actual agent evidence consumption과 외부 reviewer/key
  isolation은 현재 S06 completion에서 제외한다.
- 실제 제품 workflow E2E는 단순화 implementation 이후 S07이 소유한다.
- 과거 계획 문구와 stable IDs는 새 `key.acceptance.core-simplification.*` claim의 `supersedes`
  관계로 이력을 보존한다.
- 현재 S06은 code 구현 전이고 개편 후에도 Goal과 owner가 동일하므로 취소하지 않는다. 새 Step을
  만들지 않고 active S06을 Lean Core Contract, mandatory audit path 제거, tiered verification의
  세 phase로 개정한다.

## 진행 로그

1. 2026-08-07~08: 기존 whole-flow self-host와 adversarial/crash-resume 계획을 작성했다.
2. 2026-08-10: `DEC-WORKS-029`에 따라 S06을 Standards-to-Product Core Simplification으로 개편하고
   actual-agent/cryptographic-audit dependency를 core에서 분리했다.
3. 2026-08-10: S05가 no-secret current contract, exact source/test/document paths, historical-read
   adapters와 phase별 rollback/deletion gate를 작성했다. S06 status는 planned로 유지한다.
4. 2026-08-10: S05가 complete, accepted, finalized되어 S06 start gate가 열렸고 S06을
   `in_progress`/Active로 활성화했다.
5. 2026-08-10: Artifact Graph, Author, Coordinator, Linker, Subagent 다섯 pending standard에
   current source-owner direct apply, repository source reconstruction, Work State/Progress closure와
   no-secret 기본 경계를 반영했다. 구 HMAC·receipt·snapshot/finalization wire는 historical
   read/diagnostic으로 강등했고 package contract·README와 code/test는 수정하지 않았다.
6. 2026-08-11: 사용자가 Keystone의 기본 검증을 위험 기반 계층형 정책으로 최적화하고 일반 작업에서
   HMAC·외부 evidence·agent 평가와 무조건적인 full validation을 제거하기로 결정했다. 실제 진행도는
   다섯 pending standard 초안뿐이고 code 구현이 없어 S06을 취소하지 않고 in-place 개편했다.
7. 2026-08-11: Artifact Graph, Author, Coordinator, Linker, Subagent pending standard를 Lean Core
   Contract에 맞춰 정렬했다. Default/Escalated/Release 검증, 실제 의미·상태·pointer 변경에 한정한
   문서 갱신, optional delegation과 cache source-scan fallback을 명시하고 구 HMAC·receipt·snapshot
   wire 상세를 adapter-owned historical compatibility로 축약했다. Work State는 경고 없이 pass했고
   docs readiness는 191/191 complete, error 0으로 통과했다. 기존 locator/out-of-scope warning은
   current transaction 밖 coverage debt로 유지한다.
8. 2026-08-11: Author·Coordinator·Linker package contract와 세 reference, README를 current source,
   current diff, owner baseline/result, conditional graph/Work State, durable Progress 중심으로 정렬했다.
   Current completion에서 finalization manifest, external evidence root, owner/reviewer key, HMAC
   receipt, assignment snapshot과 acceptance-event를 요구하지 않게 했다.
9. 2026-08-11: agent-eval spec/validator/release tests, canonical/Author/Coordinator owner-apply
   runtime·runner·generator, Coordinator snapshot/acceptance-event producer와 결합 test를 제거했다.
   Installer는 retained package와 Work State parity만 stage하며 retired producer 부재를 검증한다.
10. 2026-08-11: Coordinator schema v1을 current no-secret closure로 승격하고 v2/v3를
    `historical_structure_only` read path로 격리했다. Linker schema-v2 application evidence는 외부 trust
    material이 없을 때 current source/replay 구조 검증과 warning만 수행하고 current authority를 만들지
    않는다. Author finalization v1-v6 parser는 historical package compatibility로 유지했다.
11. 2026-08-11: release gate를 preflight → package tests → shared tests → compileall → docs/repository
    readiness → Work State → repository graph → installer staging/parity/rollback → postflight의 12단계로
    축소했다. RC/production은 같은 mechanical plan을 사용하고 agent/current-finalization/별도 historical
    phase와 모든 external trust CLI를 제거했다.
12. 2026-08-11: escalated verification으로 Author 96, Coordinator 34, Linker 367, shared 41 tests,
    shell/Python syntax, `git diff --check`, docs/repository readiness, Work State, repository graph
    307/307와 installer temporary staging/parity/rollback을 통과했다. Full release는 clean-tree release
    요청이 아니므로 실행하지 않았다.
13. 2026-08-11: Main이 current diff와 verification evidence를 검토해
    `R010/S06/main-acceptance`로 수락했다. Lean Core 정책에 따라 별도 finalization manifest나 외부
    evidence 산출물 없이 Work/Progress 상태를 complete로 닫고 S07을 활성화했다.

## 다음 작업

1. Active R010/S07에서 PWF-01~04 fixture와 verification command를 확정한다.
2. Product Value Criteria와 residual-risk evidence를 repository-local 결과로 기록한다.
3. Release/publish/install 요청이 별도로 들어오면 clean checkout에서 canonical release plan과
   postflight를 실행한다.
