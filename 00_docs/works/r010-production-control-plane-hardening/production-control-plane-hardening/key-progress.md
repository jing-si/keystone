---
doc_type: progress
created_at: "2026-08-07"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-08", accepted_by: main}
work_status: complete
step_ref: R010/S01
work_ref: R010/production-control-plane-hardening
finalization: {state: complete, acceptance_ref: R010/S01/main-acceptance}
key:
  id: key.work.production-control-plane-hardening.progress
  refs:
    - key.topic.progress-update
    - key.topic.artifact-graph
    - key.topic.finalization
    - key.role.coordinator
    - key.topic.verification
    - key.acceptance.r010.foundation.lifecycle-wire
    - key.acceptance.r010.foundation.applied-digest-binding
    - key.acceptance.r010.foundation.physical-target-v2
    - key.acceptance.r010.foundation.source-unit-companion-parity
    - key.acceptance.r010.foundation.artifact-dependency-separation
    - key.acceptance.r010.foundation.coordinator-closure-v2
    - key.acceptance.r010.foundation.finalization-v5
    - key.acceptance.r010.foundation.parser-impact-regression
    - key.acceptance.r010.foundation.verification-suite
    - key.acceptance.r010.foundation.release-security
    - key.acceptance.r010.foundation.work-decomposition
    - key.acceptance.r010.foundation.evidence-replay
    - key.acceptance.r010.foundation.main-acceptance-review
---

# Production Control Plane Hardening 진행 기록

## 현재 상태

- Step: R010/S01
- Work status: complete
- Approval state: accepted (2026-08-08, main)
- Active: false
- Finalization state: complete
- Acceptance ref: `R010/S01/main-acceptance`
- Resume point: S01 correctness hardening은 accepted/finalized 상태다. Schema-v5 manifest와
  package-owned Author runner evidence를 보존한 뒤 별도 전이로 R010/S02를 활성화한다.

Active steps: []

## 준비 증거

- Baseline commit: `d36feb79666f53cacd44f01a79dda8f14d672bb6`
- 변경 전 테스트: Linker 219, Author 81, Coordinator 27, cross-skill 19 tests passed.
- 변경 전 repository full graph validation: complete true, diagnostics 0.
- 핵심 residual risk: lifecycle replacement 표현, planned/applied byte binding, Coordinator manifest
  self-report trust, inline/companion interpretation drift.

## 진행 로그

1. 2026-08-07: 사용자 zero-base review를 R010/S01의 source context와 completion criteria로 기록했다.
2. 2026-08-07: project Python convention과 installed Linker/Author/Coordinator runtime contract를
   확인하고 baseline suite를 실행했다.
3. 2026-08-07: lifecycle domain과 relation lifecycle을 분리하고 document `superseded` replacement,
   retired impact seed, parser false-positive 회귀를 shared executable policy로 정합화했다.
4. 2026-08-07: schema-v2 executable patch의 planned/applied digest equality, canonical physical-target
   uniqueness, 기본-v2 planner와 명시적 legacy-v1 compatibility를 구현했다.
5. 2026-08-07: inline/companion SourceUnit을 readiness와 reconstruction이 공유하게 하고 artifact
   flat dependency를 legacy Work gate에서 분리했다.
6. 2026-08-07: Coordinator closure v2가 assignment/context, root/snapshot, changed-file scope·digest,
   Linker transaction, Author schema-v5 finalization과 Step/Work gate를 실제 source에서 검증하게 했다.
7. 2026-08-07: Author finalization v5에 event Round, active-Step prefix, typed four-source role/status와
   canonical path, duplicate/mixed frontmatter fail-closed 검증을 추가했다.
8. 2026-08-07: 독립 adversarial 재감사에서 physical path alias, companion lifecycle, v1 wire
   downgrade, source-role alias와 mixed mapping 우회를 모두 재현 후 차단했다.
9. 2026-08-07: Linker 247, Author 92, Coordinator 53, Reader 2, cross-skill/self-host 48 tests가
   통과했다. Docs readiness는 153/153, repository readiness와 full graph validation은 255/255,
   skipped/omitted/declared-only source 0이었다.
10. 2026-08-07: 현재 Author package로 baseline archive의 R008/R009 finalization을 재실행해
    historical compatibility가 통과함을 확인했다.
11. 2026-08-07: 12개 agent behavior scenario와 RC/production release gate를 추가했다. 외부
    evidence가 없거나 worktree가 dirty하면 각각 fail-closed하고, RC/production 계획은 current
    finalization 포함 여부를 분리한다.
12. 2026-08-07: release/eval 독립 감사에서 inherited PATH/PYTHONPATH, rc-only success, truncated
    production plan, caller-selected weak key, symlink ancestor, stale outcome와 duplicate JSON key
    우회를 추가 발견해 security hardening과 회귀 검증을 시작했다.
13. 2026-08-07: authoritative release entry를 `scripts/run_release_gate.sh`로 고정하고 isolated
    Python, 최소 환경, trusted tool path, exact RC/production plan, strict success envelope와
    preflight/postflight generation equality를 강제했다. Agent evidence는 외부 root, anchored
    reviewer key, stable single-link bytes, measured identity attachment, freshness와 bounded duration에
    결속했다.
14. 2026-08-07: Author·Coordinator·Linker의 authoritative JSON 경계에서 recursive duplicate key,
    boolean/float schema와 unknown success field를 fail-closed로 통일했다. 최종 suite는 Linker 257,
    Author 100, Coordinator 60, Reader 2, cross-skill/self-host 54개가 통과했다. Docs readiness는
    153/153, repository readiness와 full graph validation은 256/256이며 skipped/omitted/
    declared-only source는 0이다. Historical R008/R009 finalization과 external-cache compileall도
    통과했다.
15. 2026-08-07: 사용자의 평균 8.5 목표에 따라 S01의 잔여 agent/release/terminal 책임을
    R010/S02-S05로 분리했다. S01은 완료된 correctness hardening과 그 verification review만
    소유하며, 이 이관은 Main acceptance나 terminal finalization을 주장하지 않는다.
16. 2026-08-07: 후속 검토에 따라 combined S04/S05를 S04 Work State, S05 Agent Behavior,
    S06 Whole-Flow, S07 RC/terminal closure로 다시 분리하고 PC85-04 classification을 S03으로
    이동했다. S01 active/status/history는 변경하지 않았다.
17. 2026-08-07: Work Order의 criterion statement와 Progress의 state/evidence를 분리하고 S01의
    기술 검증 criterion에 stable ID를 부여했다.
18. 2026-08-07: 기존 test count는 이력으로 보존하되 exact result digest가 Progress에 없으므로
    technical criterion을 `needs_replay`로 명시하고 current candidate replay를 completion criterion으로
    추가했다. Main acceptance는 post-completion gate로 분리했다.
19. 2026-08-08: 8.5 execution plan과 S02-S07 start/completion gate, evidence subject lineage,
    scoring rubric을 commit `9d8b194b6fc2cbd4855416189da256ef29b851fa`에 고정했다.
20. 2026-08-08: S01 replay 중 Coordinator v2가 string locator를 Linker canonical locator object로
    투영할 수 없는 CC06 blocker를 발견했다. Schema-v2 artifact delta를 object-only wire로 수렴하고
    mock 없는 Coordinator CLI→package-owned Linker runner integration을 추가했으며, v1 string은
    diagnostic compatibility로 보존했다. Draft relation, document supersession과 canonical v2 wire의
    결합 회귀도 추가해 candidate `c535ea7038c5c695b7c469724a505ecf902a96df`에 고정했다.
21. 2026-08-08: clean candidate에서 Author 100, Coordinator 61, Linker 258, Reader 2,
    cross-skill 55개, 총 476개 test가 통과했다. Docs readiness 174/174, repository readiness와
    full graph 278/278, historical R008/R009, external-cache compileall, installer staging/parity/
    forced rollback과 postflight가 통과했다. RC gate는 16개 중 S01 소유 phase 15개가 통과했고,
    S05가 아직 소유한 외부 `agent_behavior_evidence` 부재만 error로 fail-closed했다.
22. 2026-08-08: Main이 candidate `c535ea7038c5c695b7c469724a505ecf902a96df`의 S01
    correctness hardening, technical replay evidence와 명시된 S05-S07 residual boundary를 검토해
    `R010/S01/main-acceptance`로 수락했다.
23. 2026-08-08: Author가 S01 Progress, Work Order, work/round/root index, Context Map과 S02 gate
    recovery를 정합화했다. S02 상태를 바꾸지 않은 `active_steps: []` generation에서 schema-v5
    finalization을 완료하고 package-owned runner post-edit verification을 실행해 통과했다.

## Criterion Status

| Criterion ID | State | Evidence ref | Subject | Generation/result digest |
|---|---|---|---|---|
| `key.acceptance.r010.foundation.lifecycle-wire` | verified | Linker `test_document_supersession_and_draft_relation_close_in_v2_wire`, full suite 258 | `c535ea7038c5c695b7c469724a505ecf902a96df` | `sha256:b79027120197183d9cd0b3dbeee0de2a7b9d11a8995e917503bd96f88e8fdab5` |
| `key.acceptance.r010.foundation.applied-digest-binding` | verified | Linker executable patch/reconciler/wire regression, full suite 258 | `c535ea7038c5c695b7c469724a505ecf902a96df` | `sha256:b79027120197183d9cd0b3dbeee0de2a7b9d11a8995e917503bd96f88e8fdab5` |
| `key.acceptance.r010.foundation.physical-target-v2` | verified | Linker planner/evidence/wire regression, full suite 258 | `c535ea7038c5c695b7c469724a505ecf902a96df` | `sha256:b79027120197183d9cd0b3dbeee0de2a7b9d11a8995e917503bd96f88e8fdab5` |
| `key.acceptance.r010.foundation.source-unit-companion-parity` | verified | Linker SourceUnit/scanner/reconstruction regression, full suite 258 | `c535ea7038c5c695b7c469724a505ecf902a96df` | `sha256:b79027120197183d9cd0b3dbeee0de2a7b9d11a8995e917503bd96f88e8fdab5` |
| `key.acceptance.r010.foundation.artifact-dependency-separation` | verified | Linker dependency regression, full suite 258 | `c535ea7038c5c695b7c469724a505ecf902a96df` | `sha256:b79027120197183d9cd0b3dbeee0de2a7b9d11a8995e917503bd96f88e8fdab5` |
| `key.acceptance.r010.foundation.coordinator-closure-v2` | verified | Coordinator 61와 actual `test_coordinator_linker_runner_integration.py` | `c535ea7038c5c695b7c469724a505ecf902a96df` | `sha256:b79027120197183d9cd0b3dbeee0de2a7b9d11a8995e917503bd96f88e8fdab5` |
| `key.acceptance.r010.foundation.finalization-v5` | verified | Author 100, historical R008/R009 current-package replay | `c535ea7038c5c695b7c469724a505ecf902a96df` | `sha256:b79027120197183d9cd0b3dbeee0de2a7b9d11a8995e917503bd96f88e8fdab5` |
| `key.acceptance.r010.foundation.parser-impact-regression` | verified | Linker parser/impact regression, full suite 258 | `c535ea7038c5c695b7c469724a505ecf902a96df` | `sha256:b79027120197183d9cd0b3dbeee0de2a7b9d11a8995e917503bd96f88e8fdab5` |
| `key.acceptance.r010.foundation.verification-suite` | verified | Package/cross-skill 476, readiness/graph/historical/compileall replay | `c535ea7038c5c695b7c469724a505ecf902a96df` | `sha256:b79027120197183d9cd0b3dbeee0de2a7b9d11a8995e917503bd96f88e8fdab5` |
| `key.acceptance.r010.foundation.release-security` | verified | RC gate 15/16 pass와 외부 evidence 부재 fail-closed, release/eval security suite | `c535ea7038c5c695b7c469724a505ecf902a96df` | `sha256:b79027120197183d9cd0b3dbeee0de2a7b9d11a8995e917503bd96f88e8fdab5` |
| `key.acceptance.r010.foundation.work-decomposition` | verified | R010 S02-S07 source와 plan commit `9d8b194b6fc2cbd4855416189da256ef29b851fa` | `c535ea7038c5c695b7c469724a505ecf902a96df` | `sha256:b79027120197183d9cd0b3dbeee0de2a7b9d11a8995e917503bd96f88e8fdab5` |
| `key.acceptance.r010.foundation.evidence-replay` | verified | 아래 S01 Technical Replay Evidence v1 | `c535ea7038c5c695b7c469724a505ecf902a96df` | `sha256:b79027120197183d9cd0b3dbeee0de2a7b9d11a8995e917503bd96f88e8fdab5` |

## S01 Technical Replay Evidence v1

아래 JSON object를 UTF-8로 `json.dumps(sort_keys=True, separators=(",", ":"),
ensure_ascii=False)` 직렬화한 raw bytes의 SHA-256은
`sha256:b79027120197183d9cd0b3dbeee0de2a7b9d11a8995e917503bd96f88e8fdab5`다.

```json
{
  "schema_version": 1,
  "subject": {
    "commit": "c535ea7038c5c695b7c469724a505ecf902a96df",
    "tree": "00f51d1c72e78c85c877403e6e69535b6e7f1f67",
    "release_package_digest": "sha256:e1188b5d99844c48f0c8a5f0684c5ddf53b48e0daeb0bbea2bfe7b6e84e83435"
  },
  "package_suites": {
    "author": 100,
    "coordinator": 61,
    "linker": 258,
    "reader": 2,
    "cross_skill": 55,
    "total": 476
  },
  "docs_readiness": {
    "status": "pass",
    "complete": true,
    "discovered": 174,
    "parsed": 174,
    "skipped": 0,
    "path_digest": "sha256:3af9f885f9118cb4e9da9b6f7bb1104ee2024249519a029f3e280d34ae9119e5"
  },
  "repository_readiness": {
    "status": "pass",
    "complete": true,
    "discovered": 278,
    "parsed": 278,
    "skipped": 0,
    "path_digest": "sha256:3926e5475ca25aef3d32547ee9442eb3c7b41923dc10dbdb9affd50f2f8ee6df"
  },
  "repository_graph": {
    "status": "pass",
    "complete": true,
    "discovered": 278,
    "parsed": 278,
    "omitted": 0,
    "declared_only": 0,
    "skipped": 0,
    "errors": 0,
    "warnings": 0,
    "path_digest": "sha256:3926e5475ca25aef3d32547ee9442eb3c7b41923dc10dbdb9affd50f2f8ee6df"
  },
  "historical_finalization": {
    "R008": "pass",
    "R009": "pass",
    "baseline_commit": "d36feb79666f53cacd44f01a79dda8f14d672bb6"
  },
  "compileall": "pass",
  "installer": {
    "staging": "pass",
    "manifest": "pass",
    "parity": "pass",
    "forced_rollback": "pass"
  },
  "rc_gate": {
    "profile": "rc",
    "passed": 15,
    "failed": 0,
    "errors": 1,
    "total": 16,
    "expected_external_error": "agent_behavior_evidence"
  },
  "worktree": {
    "preflight": "clean",
    "postflight": "clean"
  }
}
```

## Post-Completion Acceptance Status

| Criterion ID | State | Evidence ref | Subject | Generation/result digest |
|---|---|---|---|---|
| `key.acceptance.r010.foundation.main-acceptance-review` | accepted | `R010/S01/main-acceptance`; schema-v5 Author finalization pass | `c535ea7038c5c695b7c469724a505ecf902a96df` | manifest `sha256:0ef0991c85931e515550b4a1e2f3a7be4d7f4fdbe55ef43315284752766ade34`; runner envelope `sha256:bfc73e865440500635d4f6ed66c1455db12aef5e9ff79a2d5bcc9b893a2bd65c` |

## Acceptance Finalization Evidence

- Acceptance ref: `R010/S01/main-acceptance`
- Accepted implementation subject: `c535ea7038c5c695b7c469724a505ecf902a96df`
- Technical replay result digest:
  `sha256:b79027120197183d9cd0b3dbeee0de2a7b9d11a8995e917503bd96f88e8fdab5`
- Schema-v5 manifest: `../key-finalization-manifest.json`
- Manifest raw-byte digest:
  `sha256:0ef0991c85931e515550b4a1e2f3a7be4d7f4fdbe55ef43315284752766ade34`
- Package-owned Author runner: exit `0`, status `pass`, errors `0`, warnings `0`
- Runner envelope raw-byte digest:
  `sha256:bfc73e865440500635d4f6ed66c1455db12aef5e9ff79a2d5bcc9b893a2bd65c`
- Graph disposition: `not_applicable` — execution, approval, finalization과 recovery projection만
  바뀌며 stable identity, typed relation, lifecycle domain과 locator는 바뀌지 않았다.
- Subject lineage: 이 pre-S02 finalization source generation은 별도 commit으로 고정하고, S02
  activation evidence가 해당 commit을 parent로 기록한다.

## 현재 검증 경계

- S01 technical criteria와 clean-subject evidence replay는 candidate
  `c535ea7038c5c695b7c469724a505ecf902a96df` 및 위 result digest에 결속돼 있다.
- Author 100, Coordinator 61, Linker 258, Reader 2, cross-skill 55개와 actual-corpus graph/
  historical/installer 검증이 통과했다. 이 기록은 Main acceptance가 아니며 finalization을 완료하지
  않는다.
- RC gate의 외부 `agent_behavior_evidence` 오류는 fail-open 성공이 아니라 S05 evidence 부재를
  의도대로 차단한 결과다. S01 technical replay와 분리해 보존한다.
- Context Map은 `active_round: R010`이므로 production profile의 current-finalization 단계는 아직
  통과하면 안 된다.
- Main은 위 candidate와 residual boundary를 `R010/S01/main-acceptance`로 수락했고, schema-v5
  manifest와 package-owned Author runner가 pre-S02 source generation의 finalization을 통과했다.
- 실제 model transcript/evidence 생성 runtime과 독립 reviewer workflow는 R010/S05가 소유하고,
  whole-flow 소비는 R010/S06, RC/production closure는 R010/S07이 소유한다.
- HMAC은 key holder의 attestation을 증명하지만 실제 model 실행과 reviewer 독립성을 스스로
  증명하지는 않는다. 이 운영 trust boundary는 Main acceptance에서 별도로 확인한다.

## 다음 작업

1. 이 finalization source generation을 별도 commit으로 고정한다.
2. 해당 commit을 parent evidence로 삼아 R010/S02를 별도 상태 전이로 활성화한다.
3. S02/S03은 authority-chain과 graph/source correctness 후속 항목을 실행한다.
4. S04는 shared work state, S05는 actual agent eval, S06은 whole-flow E2E를 수행한다.
5. S07은 independent RC evidence, Main acceptance와 terminal finalization을 결속한다.
