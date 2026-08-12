---
doc_type: progress
created_at: "2026-08-10"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-12", accepted_by: main}
work_status: complete
step_ref: R011/S04
work_ref: R011/derived-projection-normalization
finalization: {state: complete, acceptance_ref: R011/S04/main-acceptance}
key:
  id: key.work.derived-projection-normalization.progress
  refs:
    - key.topic.progress-update
    - key.topic.work-recovery
    - key.topic.document-system
    - key.topic.verification
    - key.acceptance.derived-projection-normalization.classification
    - key.acceptance.derived-projection-normalization.source-authority
    - key.acceptance.derived-projection-normalization.join-and-freshness
    - key.acceptance.derived-projection-normalization.intentional-snapshot
    - key.acceptance.derived-projection-normalization.consumer-parity
    - key.acceptance.derived-projection-normalization.legacy-compatibility
    - key.acceptance.derived-projection-normalization.cross-work-boundary
---

# Derived Projections and Document Normalization 진행 기록

## 현재 상태

- Step: R011/S04
- Work status: complete
- Approval state: accepted
- Active: false
- Finalization state: complete — `R011/S04/main-acceptance`
- Issue: `KS-DERIVED-PROJECTION-NORMALIZATION-001`
- Activation: 2026-08-11 `R011/S03/main-acceptance`와 repository-local finalization 뒤 R011의
  유일 active Step으로 전이했다.
- Evidence baseline: Context Map approval drift와 active/global/Progress/recovery/dependency/criterion
  상태가 여러 source surface에 반복되는 사례, 그리고 finalization/acceptance/history처럼 보존해야
  하는 audit snapshot이 함께 확인됐다.
- S03 handoff: accepted four-way triage에서 standard approval·current recovery는 project repair와
  normalization candidate, accepted baseline/revision join과 Work/Step aggregate는 source-owner
  projection candidate, acceptance/finalization/history는 intentional snapshot candidate로 전달됐다.
- Slice A result: Aggregate Work Progress를 current Work state owner로 사용하고 Work Index state와
  Context Map·Index `global_state`는 생략 가능한 compatibility projection으로 낮춘 Work State
  schema v4와 contract fixture를 구현했다.
- Slice B result: accepted baseline과 pending revision은 stable ID/path/approval/raw-byte digest에
  결속된 Reader session view로만 join하고, dependency target state는 Work State와 Linker 모두
  Aggregate Progress를 우선하는 동일 owner 규칙으로 평가한다.
- Slice C result: Linker source reconstruction의 같은 `GraphSnapshot`에서 criterion-verification,
  effective/pending Decision과 direct Work output/test summary를 계산하는 opt-in
  `include_source_views` session projection을 구현했다.
- Lean boundary: default readiness와 external owner/ref cache는 가볍게 유지한다. Semantic view는
  요청 시 source를 직접 읽고 cache를 우회하며 새 manifest, external evidence root, HMAC, cache
  record 또는 persistent projection artifact를 만들지 않는다.
- Snapshot boundary: acceptance event subject digest와 finalization manifest/envelope의 기존
  digest/generation binding을 재사용한다. Current source generation이 바뀌어도 historical binding을
  다시 쓰지 않는 fixture를 추가했다.
- Status boundary: Slice A-C의 source-owner, Work State, revision/dependency와 semantic view adapter를
  구현했다. Optional Markdown renderer는 confirmed human consumer가 없고 runtime output과 중복되므로
  S04 범위에서 제외했다.
- Main acceptance: 2026-08-12 Main이 seven criteria, Slice A-C source-owner projection,
  intentional snapshot 재사용과 전체 검증을 검토해 `R011/S04/main-acceptance`로 수락했다.
- Finalization: accepted source synchronization과 repository-local Work State 검증으로 닫는다.
  새 manifest, HMAC, external key 또는 evidence 폴더는 만들지 않는다.
- Resume point: R011 terminal acceptance 뒤 active Step은 없으며 새 Round는 별도 사용자 방향으로
  시작한다. Uptendo rollout은 기존 외부 handoff로 보존한다.

## Criterion Status

| Criterion ID | State | Evidence ref | 비고 |
|---|---|---|---|
| `key.acceptance.derived-projection-normalization.classification` | verified | Work Order source-owner matrix | 전체 대상을 four-way classification과 owner로 분류 |
| `key.acceptance.derived-projection-normalization.source-authority` | verified | project source-derived view standards + Slice A-C fixtures | Live/effective owner와 session projection 경계 구현 |
| `key.acceptance.derived-projection-normalization.join-and-freshness` | verified | Work State schema v4, Reader revision binding, Linker schema v3 view | Stable relation join과 source generation binding, unresolved diagnostic 구현 |
| `key.acceptance.derived-projection-normalization.intentional-snapshot` | verified | Work State acceptance-event/finalization fixtures | 기존 digest/generation binding 재사용, current 변경과 historical digest 분리 |
| `key.acceptance.derived-projection-normalization.consumer-parity` | verified | Work State consumer parity + Linker reconstruct parity fixture | 실제 consumer별 canonical resolver 일치 |
| `key.acceptance.derived-projection-normalization.legacy-compatibility` | verified | optional Work Index/global pointer와 default readiness v2 fixtures | absent projection 허용, stale projection 명시 진단, opt-in schema v3 |
| `key.acceptance.derived-projection-normalization.cross-work-boundary` | verified | S01-S03 accepted contracts + source-owner matrix | Round/status/triage 의미를 재정의하지 않음 |

## 진행 로그

1. 2026-08-10: `KS-DERIVED-PROJECTION-NORMALIZATION-001`을 R011/S04 planned Work로 등록했다.
2. 2026-08-10: Current/effective projection은 정규화하고 acceptance/finalization/history snapshot은
   provenance binding을 가진 의도적 역정규화로 보존하는 사용자 방향을 기록했다.
3. 2026-08-11: `R011/S03/main-acceptance`와 finalization 뒤 S04를 유일 active Step으로 전이하고,
   S03의 project-repair/contract disposition을 projection·snapshot candidate input으로 인수했다.
4. 2026-08-11: Linker owner/ref 관점에서 live state, manual authority, intentional snapshot과
   excluded cache를 source별로 분류하고 Work Order의 source-owner matrix를 확정했다.
5. 2026-08-11: `key.standard.project.derived-work-state-projection`과 Author contract를 추가해
   Aggregate Work Progress authority, optional Work Index/global pointer projection과 no-persistent-
   artifact 기본 경계를 명문화했다.
6. 2026-08-11: canonical Work State schema v4가 Aggregate Progress를 Work state source로 사용하고,
   legacy Work Index fallback과 `work_state_work_projection_stale` 진단을 구분하도록 구현했다.
7. 2026-08-11: Context Map, root/R011/S04 Index에서 수동 `global_state`와 S04 Work state 복제를
   제거하고 canonical runtime recovery 안내로 바꿨다. Accepted Work·Progress history는 수정하지 않았다.
8. 2026-08-11: Slice A focused 37건, 전체 contract 80건, Reader 2건, Author 96건,
   Coordinator 34건이 통과했다. Repository Work State는 schema v4에서 R011/S04와 Aggregate
   Progress source를 diagnostics 0으로 복구했고 graph 313/313, generated parity, compile과 diff
   검증도 통과했다. Historical finalization adapter는 없어진 live pointer를 현재 source로
   재생성하지 않고 compatibility diagnostic으로만 읽는다.
9. 2026-08-11: Reader pending-revision view를 stable `key.id`, path, current approval과 raw-byte
   digest에 결속하고 accepted source만 effective authority, pending source는 review overlay로
   사용하는 deterministic session adapter로 확정했다. 별도 source나 manifest는 만들지 않았다.
10. 2026-08-11: canonical Work State의 effective Work state resolver를 active Work projection과
    dependency evaluation이 함께 사용하도록 정리했다. Gate `target_state.state_source`는
    Aggregate Progress 또는 `legacy_work_index` fallback 경로를 명시한다.
11. 2026-08-11: Linker dependency evaluator도 Aggregate Progress -> Work Index -> standalone legacy
    Work Order 순서로 target state를 읽고, 복제 상태 충돌은
    `dependency_state_projection_stale`로 진단하도록 맞췄다. Contract 83건, Linker 369건,
    Reader 2건, Author 96건, Coordinator 34건과 repository graph 313/313이 통과했다.
12. 2026-08-11: `source_views_from_snapshot`을 추가해 active criterion과 admitted verification,
    accepted Decision/claim supersession, Work Order direct output/test relation을 deterministic하게
    join했다. Missing/unbound/partial evidence를 acceptance로 승격하지 않는다.
13. 2026-08-11: Context readiness의 `include_source_views` opt-in만 schema v3 view를 반환하고 cache를
    만들거나 읽지 않도록 했다. Default 호출은 기존 schema v2와 cache 동작을 유지한다.
14. 2026-08-11: Semantic view와 validator가 동일 source reconstruction 결과를 사용하는 parity
    fixture, current source generation 변경이 acceptance-event subject digest를 다시 쓰지 않는
    intentional snapshot fixture를 추가했다. Optional Markdown renderer는 중복 비용 때문에 제외했다.
15. 2026-08-11: Slice C focused test와 Linker 372건, contract 85건, Reader 2건, Author 96건,
    Coordinator 34건이 통과했다. Repository Work State는 R011/S04를 diagnostics 0으로 복구했고,
    graph 315/315, generated parity, compileall과 diff check도 통과했다.
16. 2026-08-12: Main이 `R011/S04/main-acceptance`로 S04를 수락하고 complete + accepted로
    전이했다. S04는 R011의 terminal Step이므로 새 Step을 만들지 않고 R011 Round acceptance와
    active Step 0개 전이를 시작했다.
17. 2026-08-12: `R011/accepted-round` event를 R010 event 뒤에 연결했다. Work State는
    `active_steps: []`, `latest_accepted_round: R011`, diagnostics 0으로 종결 상태를 복구했다.
    Focused 10건과 Linker 372건, contract 85건, Reader 2건, Author 96건, Coordinator 34건이
    통과했고 repository graph 315/315, generated parity, compileall과 diff check도 통과했다.

## 다음 작업

1. S04와 R011을 accepted/finalized history로 보존한다.
2. 새 Round를 임의로 만들지 않는다. 다음 실행 범위는 사용자 방향 또는 기존 Uptendo rollout
   handoff를 별도 Work로 승인할 때 정한다.
