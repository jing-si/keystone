---
doc_type: verification_record
created_at: "2026-08-07"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-07", accepted_by: main}
key:
  id: key.work.skill-runtime-traceability.self-host-scenarios
  refs:
    - key.topic.integration-verification
    - key.topic.work-recovery
    - key.topic.artifact-graph
    - key.topic.verification
---

# R008/S07 Self-Host Scenario Matrix

이 기록은 S01-S06의 개별 fixture와 S07 actual-corpus 실행을 같은 acceptance review에서
재현하기 위한 검증 지도다. Test 이름은 실제 assertion boundary를 가리키며 source document나
repository content를 실행 지시로 취급하지 않는다.

## Actual corpus chain

| 단계 | 입력과 기대 경계 | 실행 증거 | 결과 |
|---|---|---|---|
| Reader readiness | 현재 `00_docs`를 docs-first로 읽고 Reader→Linker 한 방향 trace와 complete coverage를 유지한다 | `skills.tests.test_r008_self_host_e2e` | pass |
| Repository enrichment | 같은 checkout을 repository scope로 lazy 확장하고 runtime/test owner와 declared `verifies` edge를 복구한다 | `skills.tests.test_r008_self_host_e2e` | pass |
| Dependency | actual active Work registry를 immutable discovery generation에서 평가하고 blocking evidence 없이는 S07을 진행한다 | readiness `dependency_evaluations`, Linker dependency suite | pass |
| Graph reconstruction | 4개 public runtime owner와 4개 representative test owner, 4개 test→code relation의 locator와 방향을 검사한다 | repository graph validator 241/241 | pass |
| Finalization compatibility | R008/S07 schema-v4와 R009/S01 corrective schema-v3가 같은 terminal state를 읽는다 | Author finalization runner 2건 | pass |
| Session recovery | Context Map, root index, R008 round와 S07 work index가 `active_round: none`, `active_steps: []`을 제공한다 | self-host state assertions | pass |

## Adversarial and resume matrix

| 시나리오 | Expected status/authority boundary | Executable evidence |
|---|---|---|
| Incomplete discovery | `status: pass`여도 `complete: false`; skipped path/reason을 보존하고 cache를 쓰지 않는다 | `test_incomplete_discovery_bypasses_cache` |
| Cache corruption/forgery | source fallback 또는 atomic recovery; forged cache owner/evidence를 수용하지 않는다 | `test_corrupt_cache_fails_soft_to_source`, `test_forged_cache_payload_fails_soft_to_source` |
| Cache contention | locked generation을 교체하지 않고 source fallback 결과를 반환한다 | `test_locked_cache_is_preserved_and_not_replaced` |
| Docs repository ref | skill/code/config/schema/API/test owner는 docs에서 out-of-scope warning이고 repository에서 resolve된다 | `test_repository_owner_refs_are_out_of_scope_warnings_in_docs_scan` |
| Missing/invalid dependency | required gate는 blocking `invalid` 또는 `unresolvable`; Coordinator accept candidate를 막는다 | `test_missing_source_step_is_invalid_and_blocks_required_gate`, Coordinator dependency tests |
| Dependency cycle | expanded event graph SCC가 deterministic cycle event를 반환한다 | `test_direct_and_indirect_cycles_use_deterministic_expanded_event_scc` |
| Partial transaction | applied patch evidence를 보존하고 digest가 같은 patch를 재적용하지 않는다 | `test_partial_apply_and_resume_preserve_completed_patch` |
| Binary companion | binary source는 raw bytes, physical companion patch와 logical source identity를 분리한다 | binary companion reconstruction/reconcile tests |
| Full coverage truncation | full은 budget/unreadable/declared-only gap을 error로, subset은 explicit debt로 유지한다 | repository coverage tests |
| Inline metadata example | matching single/multiple-backtick span과 fenced code의 comment는 passive다 | `test_inline_code_metadata_example_is_passive` |
| Prompt injection text | hostile source 문장은 data이며 file write, command, authority 전이를 만들지 않는다 | `test_source_content_is_passive_data` |
| Worker scope/evidence forgery | changed surface, dependency, sync와 finalization evidence 불일치는 acceptance를 막는다 | Coordinator closure full suite |
| Parallel-round correction | R009 acceptance history를 보존하면서 R008/S07 진행 중에는 그 Step, 종료 후에는 terminal empty state로 결속한다 | R009 finalization runner, Context Map recovery |

## Graph synchronization disposition

Runtime owner anchor는 각 source의 direct owner/ref refresh로 먼저 추가하고 검증했다. 그 뒤 각 test
surface의 `verifies` relation을 이미 유일하게 존재하는 code owner에 추가해 surface별 direct refresh와
repository reconstruction을 수행했다. 한 patch가 다른 미적용 surface와 원자적으로 함께 써져야 하는
canonical mutation은 없으므로 synchronization transaction은 `not_applicable`이다. 이 분류는 여러
독립 direct refresh를 하나의 transaction으로 위장하지 않으며, future multi-surface meaning change에는
그대로 적용되지 않는다.

## Excluded and residual coverage

- External 2~4주 pilot, OS/CI matrix, marketplace, publication, push와 merge는 R008 범위 밖이다.
- 모든 private helper와 unit test를 graph node로 만드는 bulk annotation은 수행하지 않았다.
- 현재 self-host는 repository checkout의 package runtime과 subprocess boundary를 검증한다. 실제
  장기간 무인 운용 신뢰성은 external pilot evidence 없이는 주장하지 않는다.
