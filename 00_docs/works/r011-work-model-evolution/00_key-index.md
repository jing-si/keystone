---
doc_type: work_round
created_at: "2026-08-10"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-12", accepted_by: main}
round_status: accepted
key:
  id: key.work.round.r011-work-model-evolution.index
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.work-recovery
    - key.topic.skill-contract
    - key.topic.verification
    - key.claim.r011.round-hierarchy-two-level-limit
    - key.claim.r011.depth-overflow-restructure
    - key.claim.r011.parent-global-round-authority
    - key.claim.r011.child-local-execution-authority
    - key.claim.r011.parent-child-aggregate-gate
---

# R011 Parallel Work State and Hierarchical Rounds 작업서 색인

R011은 실제 소비 프로젝트에서 확인된 병렬 Work 복구와 작업 규모 확장 문제를 Keystone의 일반
상태·문서 모델로 정리한다. 복수 활성 Work/Round를 대표 작업 하나로 축소하지 않고 복구하며,
`R010-a`, `R010-b` 같은 하위 Round를 parent umbrella Round 아래에 둘 수 있게 하고, 프로젝트 중간
발견사항이 프로젝트 문서 repair인지 Keystone 스킬 계약 개선인지 증거에 따라 분류한다. 같은
현재 의미의 수동 복제는 source-derived projection으로 정규화하고 audit/history snapshot은
provenance를 가진 의도적 역정규화로 보존한다.

R011은 S01-S04를 각각 Main acceptance로 complete + accepted하고 terminal Round acceptance로
닫혔다. S03은 외부 프로젝트를 수정하지 않고 분류·계약·handoff를 완료했고, S04는
projection/snapshot source-owner 정규화와 lean session view를 구현·검증했다.

<!-- key: id=key.work.round.r011.execution-order refs=key.topic.work-sequence key.topic.work-recovery -->
## 실행 순서

Current `active_steps`는 각 Work Progress를 결합한 canonical Work State Runtime에서 복구한다.

| 순서 | Work | 경로 | 상태 | 목적 |
|---|---|---|---|---|
| S01 | Parallel Active State | `parallel-active-state/00_key-index.md` | complete, accepted | 복수 활성 Work/Round, 동등한 active Steps와 unresolved Step을 versioned global state로 복구했다 |
| S02 | Hierarchical Rounds | `hierarchical-rounds/00_key-index.md` | complete, accepted | parent Round가 umbrella 의미를 소유하고 `R010-a` 형식 child Round가 상세 실행을 소유하는 계층을 정의했다 |
| S03 | Project Signal and Contract Triage | `project-signal-triage/00_key-index.md` | complete, accepted | project repair와 skill contract change를 분리하고 4개 lean contract와 외부 repair handoff를 수용했다 |
| S04 | Derived Projections and Document Normalization | `derived-projection-normalization/00_key-index.md` | complete, accepted | live/effective 의미를 source-derived projection으로 정규화하고 immutable event/audit snapshot은 의도적 역정규화로 보존했다 |

현재 active Step은 없다. S01-S04 결과와 R011 acceptance event는 accepted history로 보존한다.

<!-- key: id=key.work.round.r011.issue-map refs=key.topic.work-recovery key.topic.skill-contract -->
## 제안 식별자

| 식별자 | Work | 의미 |
|---|---|---|
| `KS-PARALLEL-ACTIVE-STATE-001` | R011/S01 | 복수 활성 Work/Round가 단일 `active_round`로 축소되거나 숨겨지는 문제 |
| `KS-HIERARCHICAL-ROUND-001` | R011/S02 | 큰 Round를 parent umbrella와 세부 child Round로 나눌 수 없는 문제 |
| `KS-PROJECT-SIGNAL-TRIAGE-001` | R011/S03 | 프로젝트 중간 발견사항을 곧바로 스킬 결함으로 일반화할 위험 |
| `KS-DERIVED-PROJECTION-NORMALIZATION-001` | R011/S04 | 현재 의미의 수동 복제와 보존해야 할 audit snapshot을 구분하지 못하는 문제 |

<!-- key: id=key.work.round.r011.user-direction refs=key.topic.work-round key.topic.work-recovery -->
## 사용자 방향

1. 복수 활성 Work와 Round, 동등한 active Steps를 손실 없이 표현한다.
2. Parent `R010` 아래에 `R010-a`, `R010-b` 같은 child Round를 허용한다.
3. Parent Round는 전체 Goal, 공통 Scope, 경계와 child navigation을 포괄하고, child Round가 상세
   Work Order, Progress, completion criteria와 verification을 소유한다.
4. 작업 도중 새 세부 단위가 필요하면 기존 Step 식별자를 재번호화하지 않고 새 child Round를
   parent index에 추가할 수 있어야 한다.
5. Round 계층은 parent와 직접 child의 총 2단계까지만 허용한다. 3단계 이상이
   필요해지면 생성을 멈추고 과도한 플랜 복잡도로 판정해 작업서 개편을 요청한다.
6. Parent만 전역 Round 상태·수락 식별자를 소유하고 child는 local Round·Work·Step
   상태를 소유한다. Parent 수락은 선언한 모든 child의 accepted 상태를 gate로 한다.
7. 소비 프로젝트의 상태나 문서 불일치는 맥락을 먼저 판정하고, project-document repair와
   Keystone skill-contract change를 분리한다.
8. 다시 계산 가능한 live/effective 의미는 stable ID/ref join과 derived projection으로 정규화하고,
   acceptance event, finalization과 history는 provenance-bound snapshot으로 보존한다.

<!-- key: id=key.work.round.r011.boundaries refs=key.boundary.scope-control key.topic.verification -->
## Round 경계

- R011 등록 자체는 문서 계획 수립이며 runtime, validator, generated copy와 skill source를 수정하지 않는다.
- 외부 소비 프로젝트의 Context Map, Work Order, Progress와 상태값은 이 저장소에서 직접 수정하지 않는다.
- R008·R010 병렬 진행 사실은 evidence/fixture seed이며 그 상태를 오류로 단정하거나 소급 변경하지 않는다.
- 기존 accepted Work Order와 Decision은 역사로 보존하고, 의미 변경이 필요하면 item/claim 단위의
  명시적 후속 결정과 검증으로 처리한다.
- 복수 활성 상태는 병렬 writer 권한이나 작업 우선순위를 자동 부여하지 않는다.
- 하위 Round는 accepted history 재번호화나 기존 flat Round의 일괄 migration을 요구하지 않는다.
- 하위 Round 계층은 parent→child에서 종료하며, child 아래 추가 Round를 만들지 않는다.
- Child local acceptance는 전역 latest-accepted pointer나 별도 acceptance-event/finalization 산출물을
  만들지 않는다.
- Generated projection과 disposable cache는 source authority가 아니며 approval/status를 자동 전이하지 않는다.
- Acceptance/finalization/history snapshot은 중복처럼 보여도 current projection으로 덮거나 제거하지 않는다.

<!-- key: id=key.work.round.r011.completion refs=key.topic.acceptance key.topic.verification -->
## Round 완료 조건

1. S01-S04가 각각 `work_status: complete`, `approval.state: accepted`와 required finalization
   closure를 가진다.
2. 프로젝트 기준서, Reader·Author·Coordinator·Linker 계약, canonical runtime, validator와 release
   consumer가 수락된 상태·Round hierarchy와 projection/snapshot 의미를 동일하게 해석한다.
3. 단일 Round legacy corpus, 복수 활성 Round, active Work without active Step, parent/child Round,
   dynamic child addition, project-vs-skill triage, stale projection과 immutable snapshot fixture가
   통과한다.
4. R010과 이전 accepted history를 소급 재작성하지 않고 compatibility와 supersession 경계를
   evidence로 남긴다.

<!-- key: id=key.work.round.r011.reading-rules refs=key.topic.work-recovery key.topic.work-sequence -->
## 복구 규칙

1. R011 전체 방향과 Work 순서는 이 index를 읽는다.
2. 각 Goal, Scope, completion criteria와 stop condition은 S01-S04 Work Order를 읽는다.
3. 실제 진행 상태와 resume point는 각 Work의 Progress를 읽는다.
4. 현재 active Round/Step은 canonical Work State Runtime에서 복구한다. Root Index와 Context
   Map의 수동 `global_state`를 별도 권위로 요구하지 않는다.
