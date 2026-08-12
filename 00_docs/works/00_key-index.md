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

<!-- key: id=key.work.index.common-decisions refs=key.doc.decision key.doc.work key.topic.work-round -->
## 공통 결정

- 여러 round에 영향을 주는 결정 기록(6): `key-decisions.md`

<!-- key: id=key.work.index.reading-rules refs=key.doc.work key.doc.source key.topic.document-system key.topic.work-round -->
## 읽기 규칙

1. 프로젝트 전체 방향은 `00_docs/key-context-map.md`를 먼저 읽는다.
2. 공통 기준과 용어는 `00_docs/standards/01_key-project-standard.md`를 따른다.
3. `Work rounds` 표는 Round navigation과 사람이 작성한 목적 요약이다. Current active/latest
   상태는 `scripts/work_state_runtime.py --root .`의 source-derived 결과에서 복구하며 이 Index에
   별도 `global_state` pointer를 수동 유지하지 않는다.
4. Round 내부 실행 순서는 해당 round의 `00_key-index.md`에서 확인한다.
5. 각 work의 세부 목표와 검증은 해당 work node의 `key-work-{slug}.md`에서 확인한다.
6. 각 work의 진행 상태는 해당 work node의 `key-progress.md`에서 확인한다.
7. R011의 실행 이력과 다음 범위는 `r011-work-model-evolution/00_key-index.md`, 각 Work Progress와
   canonical Work State 결과를 함께 확인한다.

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
9. `DEC-WORKS-031`에 따라 Root/Context의 전역 Round pointer와 latest-accepted ordering은
   parent ref만 사용한다. Child ref는 parent index의 ordered `child_rounds`, child-local
   Work·Step·Progress와 Work State child 집계에서 복구한다.
