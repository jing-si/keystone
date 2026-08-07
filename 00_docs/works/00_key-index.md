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
global_state:
  active_round: R010
  latest_accepted_round: R009
  active_steps: [R010/S01]
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
| R010 | Production Control Plane Hardening | `r010-production-control-plane-hardening/00_key-index.md` | active | cross-runtime correctness와 actual-state production gate를 구현·검증한다 |

<!-- key: id=key.work.index.common-decisions refs=key.doc.decision key.doc.work key.topic.work-round -->
## 공통 결정

- 여러 round에 영향을 주는 결정 기록(6): `key-decisions.md`

<!-- key: id=key.work.index.reading-rules refs=key.doc.work key.doc.source key.topic.document-system key.topic.work-round -->
## 읽기 규칙

1. 프로젝트 전체 방향은 `00_docs/key-context-map.md`를 먼저 읽는다.
2. 공통 기준과 용어는 `00_docs/standards/01_key-project-standard.md`를 따른다.
3. 현재 active round가 있으면 이 파일의 `Work rounds` 표를 권위로 삼는다. 현재 active round는
   R010이며, 최신 accepted round는 R009다.
4. Round 내부 실행 순서는 해당 round의 `00_key-index.md`에서 확인한다.
5. 각 work의 세부 목표와 검증은 해당 work node의 `key-work-{slug}.md`에서 확인한다.
6. 각 work의 진행 상태는 해당 work node의 `key-progress.md`에서 확인한다.

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
