---
doc_type: context_map
key:
  id: key.context-map
  refs:
    - key.topic.document-system
    - key.topic.artifact-graph
    - key.doc.source
    - key.topic.work-sequence
    - key.topic.work-round
    - key.topic.skill-contract
    - key.standard.subagent
    - key.topic.bootstrap
    - key.topic.initialization
    - key.topic.runtime-independence
global_state:
  active_round: none
  latest_accepted_round: R009
  active_steps: []
---

# 프로젝트 컨텍스트 맵

활성 Keystone 계획 문서는 `00_docs/` 아래에 둔다. 현재 active work round는 없으며, 최신 accepted round는
`00_docs/works/r009-coordinator-keystone-closure/`이다.

<!-- key: id=key.context-map.project refs=key.doc.source key.topic.skill-contract key.topic.bootstrap -->
## 프로젝트

이 저장소는 `keystone` 스킬 시스템을 정의하고 구현하기 위한 저장소다. 최종 산출물은
사람이 읽을 수 있는 원천 문서(2)를 중심 인터페이스로 삼아 stable owner ID와 ref로 문서, code,
config, schema, test를 직접 탐색하고, 필요한 의미 연결만 선택적 아티팩트 그래프(14)로 해석하며
bounded worker 실행 결과를 worker assignment/report로 연결하는 독립 스킬들의 집합이다.

1. `keystone-init`: 새 프로젝트에 R000과 작업 복구 scaffold를 만들고 프로젝트 기준서 작성
   흐름을 시작한다.
2. `keystone-reader`: 세션 시작에 기준서(3), 작업서(4)를 읽고 docs-first context readiness와
   context brief를 준비하며 repository artifact scope는 필요할 때 lazy하게 요청한다.
3. `keystone-clarify`: 실제 사용자 결정(6)을 한 topic씩 정리하고 호출자에게 반환한다.
4. `keystone-author`: 기준서, 작업서, 진행 기록, 결정 기록, Change Set(17)을 작성하거나
   승인된 범위에서 수정한다.
5. `keystone-linker`: Source-write-free internal role로 owner/ref external index readiness와 선택적
   Artifact Graph 해석, impact/stale/gap 및 validation을 수행하고 multi-surface change에서 exact
   graph mutation을 결정하되 repository source surface를 직접 수정하지 않는다.
6. `keystone-coordinator`: 사용자 허락이 있는 work scope에서 `direct_execution` 또는
   external-skill `orchestration`을 선택하고, bounded Keystone context와 worker report를
   Linker/Author document·metadata·graph·finalization closure supervision으로 회수한다.

설치된 skill package는 고유 runtime 계약을 자체 포함한다. 이 저장소의
`00_docs/standards/skills/**`는 개발·검수 명세이며 소비 프로젝트의 runtime 선행 문서가 아니다.

기존 `work-package-doc-architect`와 `subagent-work-coordinator` 스킬은 참고용 prototype이다.
이들은 최종 runtime dependency가 아니며 현재 Keystone 스킬 source의 이력 참고 자료다.

<!-- key: id=key.context-map.standards refs=key.topic.document-system key.doc.source key.topic.skill-contract key.standard.subagent -->
## 기준서

| 영역 | 경로 | 읽는 시점 |
|---|---|---|
| 색인 | `00_docs/standards/00_key-index.md` | 사용 가능한 기준서를 탐색할 때 먼저 읽는다 |
| 프로젝트 | `00_docs/standards/01_key-project-standard.md` | 프로젝트 공통 규칙, 원천 문서(2) 정책, 아티팩트 그래프(14), 스킬군 역할, coordinator 호환성을 확인할 때 읽는다 |
| Python 컨벤션 | `00_docs/convention.md` | Python runtime을 추가·수정하거나 점진적으로 리팩터링할 때 읽는다 |
| Bootstrap | `00_docs/standards/bootstrap/key-standard-bootstrap.md` | 초기화 상태, R000, runtime authority, Main/User Decision, handoff/resume를 확인할 때 읽는다 |
| Subagent | `00_docs/standards/subagents/key-standard-subagents.md` | helper/subagent의 bounded worker model, purpose preset, authority, injected skill contract, report status, 실행 환경 경계를 확인할 때 읽는다 |
| Artifact Graph | `00_docs/standards/artifacts/key-standard-artifact-graph.md` | owner/ref index, optional graph model, declared/effective metadata, validation scope, direct refresh/transaction과 impact 기준을 확인할 때 읽는다 |
| 스킬별 | `00_docs/standards/skills/00_key-index.md` | 개별 Keystone 스킬의 상세 기준서를 찾을 때 읽는다 |
| Init | `00_docs/standards/skills/init/key-standard-init.md` | `keystone-init` 개발 계약, scaffold write authority와 통합 시나리오를 확인할 때 읽는다 |
| Reader | `00_docs/standards/skills/reader/key-standard-reader.md` | session orientation, docs-first context readiness, lazy repository scope와 read-only boundary를 확인할 때 읽는다 |
| Author | `00_docs/standards/skills/author/key-standard-author.md` | `keystone-author`의 기준서(3), 작업서(4), progress update boundary를 확인할 때 읽는다 |
| Clarify | `00_docs/standards/skills/clarify/key-standard-clarify.md` | `keystone-clarify`의 decision collection, reflection, Author handoff를 확인할 때 읽는다 |
| Linker | `00_docs/standards/skills/linker/key-standard-linker.md` | permissionless owner/ref index readiness, optional graph interpretation, validation과 source surface handoff를 확인할 때 읽는다 |
| Coordinator | `00_docs/standards/skills/coordinator/key-standard-coordinator.md` | `keystone-coordinator`의 worker assignment/report, bounded worker routing, report, review, verification, acceptance flow를 확인할 때 읽는다 |

<!-- key: id=key.context-map.work-order refs=key.topic.document-system key.doc.source key.topic.work-sequence key.topic.work-round -->
## 작업서

| 작업 | 경로 | 상태 | 담당 영역 |
|---|---|---|---|
| Round 색인 | `00_docs/works/00_key-index.md` | current | 최신 round와 active work round 탐색 |
| R001 Bootstrap Keystone | `00_docs/works/r001-bootstrap-keystone/00_key-index.md` | superseded | S00-S07 accepted 이력과 S08-S09 대체 기록 |
| R002 Bootstrap and Runtime Independence | `00_docs/works/r002-bootstrap-runtime-independence/00_key-index.md` | accepted | Init, R000과 skill runtime independence |
| R003 Dependency and Work Gate | `00_docs/works/r003-dependency-work-gate/00_key-index.md` | accepted | `depends_on`, 단계별 work gate, runtime 계약과 통합 검증 완료 |
| R004 Acceptance Finalization | `00_docs/works/r004-acceptance-finalization/00_key-index.md` | accepted | acceptance finalization, runtime·validator·hook 통합 검증 |
| R005 Artifact Graph Synchronization | `00_docs/works/r005-artifact-graph-synchronization/00_key-index.md` | accepted | 기준서와 code/config/schema/API/test를 연결하는 graph synchronization 계약·runtime·검증 |
| R006 Reference Index and Context Readiness | `00_docs/works/r006-reference-index-context-readiness/00_key-index.md` | accepted | source-owned ID/ref 탐색, Reader context readiness와 선택적 graph/transaction 정합화 |
| R007 Contract Execution Reconciliation | `00_docs/works/r007-contract-execution-reconciliation/00_key-index.md` | accepted | 문서 계약 실행 정합화와 Python convention·점진적 리팩터링 완료 |
| R008 Skill Graph and Self-Host Runtime Closure | `00_docs/works/r008-skill-graph-traceability/00_key-index.md` | accepted | readiness부터 dependency·transaction·finalization까지 self-host workflow 정합화·검증 완료 |
| R009 Coordinator Keystone Closure | `00_docs/works/r009-coordinator-keystone-closure/00_key-index.md` | accepted | Coordinator context provisioning, closure gate와 local installation parity를 complete and accepted로 기록 |
| Document Tree Setup | `00_docs/works/r001-bootstrap-keystone/document-tree-setup/00_key-index.md` | accepted | `works/` tree 재정비 |
| Project Standard | `00_docs/works/r001-bootstrap-keystone/project-standard/00_key-index.md` | accepted | 전체 공통 기준서 |
| Reader Standard | `00_docs/works/r001-bootstrap-keystone/reader-standard/00_key-index.md` | accepted | `keystone-reader` 기준서 |
| Author Standard | `00_docs/works/r001-bootstrap-keystone/author-standard/00_key-index.md` | accepted | `keystone-author` 기준서와 작업서 생성 표준 |
| Clarify Standard | `00_docs/works/r001-bootstrap-keystone/clarify-standard/00_key-index.md` | accepted | `keystone-clarify` 기준서 |
| Coordinator Standard | `00_docs/works/r001-bootstrap-keystone/coordinator-standard/00_key-index.md` | accepted | `keystone-coordinator` 기준서 |
| Artifact Graph Standard | `00_docs/works/r001-bootstrap-keystone/artifact-graph-standard/00_key-index.md` | accepted | Artifact Graph 기준서 |
| Linker Standard | `00_docs/works/r001-bootstrap-keystone/linker-standard/00_key-index.md` | accepted | `keystone-linker` 기준서 |
| Skill Creation | `00_docs/works/r001-bootstrap-keystone/skill-creation/00_key-index.md` | superseded | 초기 skill source 이력, R002 S02로 대체 |
| Integration Verification | `00_docs/works/r001-bootstrap-keystone/integration-verification/00_key-index.md` | superseded | 미실행 R001 검증, R002 시나리오로 대체 |
| Bootstrap Runtime Standard | `00_docs/works/r002-bootstrap-runtime-independence/bootstrap-runtime-standard/00_key-index.md` | accepted | 기준서 개편과 문서 시나리오 검증 |
| Skill Runtime Implementation | `00_docs/works/r002-bootstrap-runtime-independence/skill-runtime-implementation/00_key-index.md` | accepted | 여섯 skill runtime contract 구현과 forward test |

<!-- key: id=key.context-map.document-tree-policy refs=key.topic.document-system key.doc.source key.topic.work-round -->
## 문서 트리 정책

Keystone 문서는 영어 경로와 설정된 document root(1)를 사용한다. 현재 사용자 지시나
프로젝트 로컬 Keystone 설정이 이를 덮어쓰지 않으면 기본 root는 `00_docs/`다.

```text
00_docs/
  key-context-map.md
  standards/
    00_key-index.md
    01_key-project-standard.md
    bootstrap/
      00_key-index.md
      key-standard-bootstrap.md
    subagents/
      00_key-index.md
      key-standard-subagents.md
    artifacts/
      00_key-index.md
      key-standard-artifact-graph.md
    skills/
      00_key-index.md
      init/
        00_key-index.md
        key-standard-init.md
      reader/
        00_key-index.md
        key-standard-reader.md
      author/
        00_key-index.md
        key-standard-author.md
      clarify/
        00_key-index.md
        key-standard-clarify.md
      linker/
        00_key-index.md
        key-standard-linker.md
      coordinator/
        00_key-index.md
        key-standard-coordinator.md
  works/
    00_key-index.md
    key-decisions.md
    r001-bootstrap-keystone/
      00_key-index.md
      document-tree-setup/
        00_key-index.md
        key-work-document-tree-setup.md
        key-progress.md
      project-standard/
        00_key-index.md
        key-work-project-standard.md
        key-progress.md
      artifact-graph-standard/
        00_key-index.md
        key-work-artifact-graph-standard.md
        key-progress.md
      linker-standard/
        00_key-index.md
        key-work-linker-standard.md
        key-progress.md
    r002-bootstrap-runtime-independence/
      00_key-index.md
      bootstrap-runtime-standard/
        00_key-index.md
        key-work-bootstrap-runtime-standard.md
        key-progress.md
      skill-runtime-implementation/
        00_key-index.md
        key-work-skill-runtime-implementation.md
        key-progress.md
    ...
```

기준서는 전체 공통 기준서에서 시작해 필요한 경우 스킬별 child 기준서로 내려간다. 작업서는
기준서 구조에 종속되지 않고 work round 안의 reviewable goal 단위로 만든다. Root works
index는 active round를 관리하고, round 내부 실행 순서는 해당 round의 `00_key-index.md`가
관리한다. 최종 작업서는 `key-work-{slug}.md` 형식을 사용한다.

<!-- key: id=key.context-map.section refs=key.topic.work-sequence key.topic.document-system key.topic.work-round -->
## 현재 작업 단계

현재 active round는 없으며 최신 accepted round는 R009 Coordinator Keystone Closure다. R009/S01은
사용자 independent-first direction으로 R008과 독립적으로 먼저 수락됐고, 이후 R008/S01-S07도
complete and accepted로 닫혔다. R001 S00-S07은 accepted 이력으로 보존되고, 미수락
S08 Skill Creation과 S09 Integration Verification은 superseded다. R002의
S01 기준서 개편과 S02 skill source 구현·검증은 모두 수락됐다. R003은 dependency 의미와
단계별 gate 기준과 repo-local runtime 구현·통합 검증을 R003에서 수락했다.
R004 Acceptance Finalization은 accepted round로, Main acceptance 후 영향 문서 자동 정합화,
scoped hard gate, package-owned validator와 hook 안전망을 구현·검증했다.
R005는 기준서가 존재하는 프로젝트에서 capability-first graph, canonical mutation, surface
attestation, source owner 적용과 finalization evidence를 연결하고 runtime·설치 layout·합성 규모
검증까지 accepted했다.
R006은 source-owned stable ID와 ref를 기본 탐색 계약으로 복구하고 Reader의 docs-first context
readiness, Linker의 외부 파생 index, 선택적 typed graph와 multi-surface transaction을 정합화하고
통합 검증까지 accepted했다.
R007은 재검토에서 확인된 상태·dependency·metadata·relation·validation·index 실행 불일치를
정합화하고, Python convention과 1~16차 점진적 모듈 리팩터링 및 최종 검증을 accepted했다.
R008은 compact metadata와 owner/ref readiness부터 Markdown hierarchy, dependency execution,
companion/repository validation, transaction/finalization, graph lifecycle과 wire compatibility를
순서대로 정합화하고, 마지막에 핵심 skill runtime traceability와 self-host E2E로 전체 경로를
검증한다.

Active steps: []

| Step | 제목 | 목적 |
|---|---|---|
| R008/S01 | Metadata Parser and Readiness Repair | complete — compact metadata, owner/ref readiness와 cache completeness를 정합화했다 |
| R008/S02 | Markdown Hierarchy and Governance | complete — 실제 heading hierarchy와 governance relation 의미를 정합화했다 |
| R008/S03 | Dependency Execution Graph | complete — Work/Step registry, legacy gate, expanded-event SCC와 readiness gate를 구현했다 |
| R008/S04 | Companion and Repository Validation | complete — binary companion과 full/subset repository coverage를 fail-closed로 검증한다 |
| R008/S05 | Transaction and Finalization Hardening | complete — executable patch replay, typed retry와 schema-v4 multi-Step/global closure를 구현했다 |
| R008/S06 | Graph Lifecycle and Wire Compatibility | complete — lifecycle/evidence impact, retired relation validation과 graph wire v2 compatibility를 정합화했다 |
| R008/S07 | Skill Runtime Traceability and Self-Host E2E | complete — 최소 runtime·test relation과 actual-corpus self-host workflow를 검증했다 |

<!-- key: id=key.context-map.planned-keystone-skills refs=key.topic.skill-contract key.topic.bootstrap -->
## Keystone 스킬 구현 상태

| 스킬 | 상태 | 목적 |
|---|---|---|
| `keystone-init` | repo source implemented | R000과 최소 scaffold를 만들고 원래 요청 resume를 준비한다 |
| `keystone-reader` | repo source implemented | Keystone 문서를 탐색하고 pre-init에서는 read-only partial 결과를 만든다 |
| `keystone-author` | repo source implemented | 기준서와 작업서를 생성하고 Init handoff 뒤 원래 작업을 resume한다 |
| `keystone-clarify` | repo source implemented | 실제 User Decision을 한 topic씩 수집해 호출자에게 반환한다 |
| `keystone-linker` | repo source implemented | Artifact Graph를 해석하고 canonical mutation을 결정하되 source surface는 read-only로 다룬다 |
| `keystone-coordinator` | repo source implemented | 사용자 허락 범위에서 direct execution 또는 external-skill orchestration, Linker/Author closure supervision을 조율한다 |

<!-- key: id=key.context-map.prototype-skill-reference refs=key.topic.bootstrap key.topic.skill-contract -->
## Prototype 스킬 참고

| 스킬 | 이 프로젝트에서의 목적 |
|---|---|
| `work-package-doc-architect` | authoring 계약의 역사적 참고용 prototype |
| `subagent-work-coordinator` | coordination 계약의 역사적 참고용 prototype |
