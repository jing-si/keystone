---
doc_type: work_round_index
key:
  id: key.work.index
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.document-system
    - key.doc.source
---

# 작업서(4) round 색인

이 색인은 Keystone work round를 찾기 위한 최상위 진입점이다. 각 work round는 특정 시점의
기준서와 목표를 바탕으로 진행하는 하나의 작업 차수이며, round 안에서 작업 순서는 `S01`부터
다시 시작한다.

<!-- key: id=key.work.index.rounds refs=key.topic.work-round key.doc.work key.topic.work-sequence -->
## Work rounds

| Round | 제목 | 경로 | 상태 | 목적 |
|---|---|---|---|---|
| R001 | Bootstrap Keystone | `r001-bootstrap-keystone/00_key-index.md` | superseded | S00-S07 accepted 이력을 보존하고 미수락 S08-S09를 R002로 이관했다 |
| R002 | Bootstrap and Runtime Independence | `r002-bootstrap-runtime-independence/00_key-index.md` | accepted | Init, R000과 설치된 skill runtime 독립성을 정의하고 repo source에 구현했다 |
| R003 | Dependency and Work Gate | `r003-dependency-work-gate/00_key-index.md` | accepted | `depends_on`과 단계별 실행 gate를 정의하고 관련 skill runtime 계약에 구현했다 |
| R004 | Acceptance Finalization | `r004-acceptance-finalization/00_key-index.md` | accepted | Main acceptance를 문서 정합성과 executable validator로 종료한다 |
| R005 | Artifact Graph Synchronization | `r005-artifact-graph-synchronization/00_key-index.md` | accepted | 기준서와 실제 산출물을 capability-first graph synchronization lifecycle로 연결했다 |
| R006 | Reference Index and Context Readiness | `r006-reference-index-context-readiness/00_key-index.md` | accepted | source-owned ID/ref 탐색과 Reader·Linker context readiness를 구현·검증했다 |
| R007 | Contract Execution Reconciliation | `r007-contract-execution-reconciliation/00_key-index.md` | accepted | 문서 계약 실행 정합화와 Python convention·점진적 리팩터링을 완료했다 |
| R008 | Skill Graph and Self-Host Runtime Closure | `r008-skill-graph-traceability/00_key-index.md` | accepted | readiness부터 dependency·transaction·finalization까지 self-host workflow를 정합화하고 검증했다 |
| R009 | Coordinator Keystone Closure | `r009-coordinator-keystone-closure/00_key-index.md` | accepted | Coordinator context provisioning, closure gate, local installation parity를 complete and accepted로 기록한다 |
| R010 | Standards-to-Product Alignment | `r010-production-control-plane-hardening/00_key-index.md` | accepted | accepted correctness 이력을 보존하고 기준서↔산출물 trace, work recovery와 단순한 제품 흐름으로 재정렬했다 |
| R011 | Parallel Work State and Hierarchical Rounds | `r011-work-model-evolution/00_key-index.md` | accepted | 병렬 Work·2단계 Round·signal triage와 source-derived projection 경계를 구현·검증하고 terminal acceptance로 닫았다 |
| R012 | Current Work State and Session Focus Simplification | `r012-current-work-state-simplification/00_key-index.md` | accepted | active parent Round 집합 중심 Work State, Round session focus와 실행자 Step 선택을 단순화하고 production gate로 검증했다 |
| R013 | Author Terminal Status Reconciliation | `r013-author-terminal-status-reconciliation/00_key-index.md` | accepted | 상태 전이별 bounded projection 대조와 Clarify 그룹 종료별 문서 적용·Q&A log 경계를 구현·검증했다 |
| R014 | Reader Progressive Context Loading | `r014-reader-progressive-context-loading/00_key-index.md` | accepted | progressive orientation, selected-Work bounded Linker와 contract parity를 구현·검증하고 닫았다 |
| R015 | Keystone Consumer Goal Effectiveness Review | `r015-keystone-consumer-goal-effectiveness-review/00_key-index.md` | active | Uptendo 소비 프로젝트 evidence로 Keystone 목표 달성 효과와 비용을 검토하고 개선 Work Order 최종본을 작성한다 |
| R016 | Worktree Locator and Targeted Work Discovery | `r016-worktree-locator-navigation/00_key-index.md` | accepted | Worktree 선택 시 canonical Work Order에 exact locator를 기록하고 대상 경로만 탐색하는 계약을 구현·검증했다 |
| R017 | Standards-First Round Construction | `r017-standards-first-round-construction/00_key-index.md` | accepted | Round 생성·실행 경계와 standards-first 제약, Excel column 방식 하위 세션 작명을 구현·검증했다 |
| R018 | Keymeta-First Bounded Discovery | `r018-keymeta-bounded-discovery/00_key-index.md` | planned | 키메타 anchor에서 필요한 source만 확장하고 routine Work 준비의 repository-wide reconstruction을 제거한다 |
| R019 | Keystone Session Title Display | `r019-keystone-session-title/00_key-index.md` | accepted | 프로젝트 로컬 Codex terminal title opt-in과 Round 기반 thread rename 제안을 구현·검증했다 |
| R020 | Keystone Session Title Automation | `r020-keystone-session-title-automation/00_key-index.md` | accepted | current Round focus를 Python helper로 현재 Codex thread 이름에 자동 반영한다 |
| R021 | Session Title Permission Hardening | `r021-session-title-permission-hardening/00_key-index.md` | accepted | exact helper executable 권한 승인으로 sandbox 환경의 자동 rename을 보강했다 |
| R022 | Session Title Assignment Gate | `r022-session-title-assignment-gate/00_key-index.md` | accepted | 명시적 기존 라운드 수행에만 native title hint를 적용하고 비종료 라운드 선택 문맥을 구현·검증했다 |
| R023 | Session Title Work Authoring Gate | `r023-session-title-work-authoring-gate/00_key-index.md` | accepted | 작업서 생성·수정 착수도 예정 또는 기존 Round ref로 native title을 준비하도록 구현·검증했다 |

<!-- key: id=key.work.index.common-decisions refs=key.doc.decision key.doc.work key.topic.work-round -->
## 공통 결정

- 여러 round에 영향을 주는 결정 기록(6): `key-decisions.md`

<!-- key: id=key.work.index.reading-rules refs=key.doc.work key.doc.source key.topic.document-system key.topic.work-round -->
## 읽기 규칙

1. 프로젝트 전체 방향은 `00_docs/key-context-map.md`를 먼저 읽는다.
2. 공통 기준과 용어는 `00_docs/standards/01_key-project-standard.md`를 따른다.
3. `Work rounds` 표는 Round navigation과 사람이 작성한 목적 요약이다. Current active 상태는
   `scripts/work_state_runtime.py --root .`의 source-derived `active_rounds`와 `active_steps`에서
   복구하며 이 Index에 별도 `global_state` pointer를 수동 유지하지 않는다.
4. Round 내부 실행 순서는 해당 round의 `00_key-index.md`에서 확인한다.
5. 각 work의 세부 목표와 검증은 해당 work node의 `key-work-{slug}.md`에서 확인한다.
6. 각 work의 진행 상태는 해당 work node의 `key-progress.md`에서 확인한다.
7. R013의 수락된 범위와 실행 이력은 `r013-author-terminal-status-reconciliation/00_key-index.md`,
   Work Order와 Progress에서 확인한다.
8. R014의 수락된 범위와 실행 이력은 `r014-reader-progressive-context-loading/00_key-index.md`,
   Work Order와 Progress에서 확인한다.
9. R015의 작성 중인 개선 Work Order와 review resume point는
   `r015-keystone-consumer-goal-effectiveness-review/00_key-index.md`, Work Order와 Progress에서
   확인한다.
10. R016의 수락된 worktree locator 계약과 검증 이력은
    `r016-worktree-locator-navigation/00_key-index.md`, Work Order와 Progress에서 확인한다.
11. R017의 accepted standards-first Round 생성 계약과 검증 이력은
   `r017-standards-first-round-construction/00_key-index.md`, Work Order와 Progress에서 확인한다.
12. R018의 키메타 우선 bounded discovery 목표와 계획은
    `r018-keymeta-bounded-discovery/00_key-index.md`, Work Order와 Progress에서 확인한다.
13. R019의 프로젝트 로컬 세션 제목 표시 구현과 진행 상태는
    `r019-keystone-session-title/00_key-index.md`, Work Order와 Progress에서 확인한다.
14. R020의 current-thread 자동 rename 구현과 진행 상태는
    `r020-keystone-session-title-automation/00_key-index.md`, Work Order와 Progress에서 확인한다.
15. R021의 session-title helper 권한 보강과 진행 상태는
    `r021-session-title-permission-hardening/00_key-index.md`, Work Order와 Progress에서 확인한다.
16. R022의 session-title assignment gate와 진행 상태는
    `r022-session-title-assignment-gate/00_key-index.md`, Work Order와 Progress에서 확인한다.
17. R023의 work-authoring title gate와 진행 상태는
    `r023-session-title-work-authoring-gate/00_key-index.md`, Work Order와 Progress에서 확인한다.

<!-- key: id=key.work.index.round-creation-rules refs=key.doc.work key.topic.document-system key.topic.work-round -->
## Work round 생성 규칙

1. Work round folder는 `r{number}-{slug}` 형식을 사용한다.
2. `r`은 round를 뜻하며, 특정 시점의 기준서와 목표를 바탕으로 진행하는 하나의 작업 차수를
   나타낸다.
3. 각 round는 `00_key-index.md`를 가지며, round 안의 실행 순서는 `S01`부터 다시 시작한다.
4. `R000`은 최초 기준서가 없는 Project Foundation에만 사용한다. 일반 작업 round는 `R001`,
   일반 step은 `S01`부터 시작한다.
5. Round 안의 work node는 하나의 reviewable goal을 가져야 한다.
6. 너무 작은 작업은 별도 work node로 만들지 않고 관련 work의 step으로 흡수한다.
7. `DEC-WORKS-030`에 따라 계층형 Round의 supported depth는 parent→child 총 2단계로
   제한한다. Exact ref·folder grammar와 상태 파생은 R011/S02에서 검증·수락됐으며 기존 flat
   `R{number}` Round와 함께 Work State schema v3의 실행 권위다.
8. 3단계 이상 Round가 필요해지면 생성을 멈추고 과도한 플랜 복잡도로 보고한 뒤
   Goal 축소, 동급 child 분리 또는 별도 parent Round를 통한 작업서 개편을 요청한다.
9. `DEC-WORKS-031`과 `DEC-WORKS-032`에 따라 `active_rounds`에는 parent ref만 사용한다.
   `latest_accepted_round`은 current 상태 권위가 아닌 기존 호환 projection이며, child ref는
   parent index의 ordered `child_rounds`, child-local Work·Step·Progress와 Work State child
   집계에서 복구한다.
