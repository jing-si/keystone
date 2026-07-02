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
---

# 프로젝트 컨텍스트 맵

활성 Keystone 계획 문서는 `00_docs/` 아래에 둔다. 현재 active work round는
`00_docs/works/r001-bootstrap-keystone/`다.

<!-- key: id=key.context-map.project refs=key.doc.source key.topic.skill-contract key.topic.bootstrap -->
## 프로젝트

이 저장소는 `keystone` 스킬 시스템을 정의하고 구현하기 위한 저장소다. 최종 산출물은
사람이 읽을 수 있는 원천 문서(2)를 중심 인터페이스로 삼아 사람의 의도, 문서, code, test,
bounded worker 실행 결과를 아티팩트 그래프(14)와 worker assignment/report로 연결하는 독립 스킬들의
집합이다.

1. `keystone-reader`: 기준서(3), 작업서(4), artifact graph 필요 단서를 읽고 context brief를
   만든다.
2. `keystone-clarify`: 정책, 범위, 문서, 스킬 계약에 관한 결정(6)을 topic 단위로 정리한다.
3. `keystone-author`: 기준서, 작업서, 진행 기록, 결정 기록, Change Set(17)을 작성하거나
   승인된 범위에서 수정한다.
4. `keystone-linker`: Artifact Graph의 operational interpretation owner로서 문서, capability,
   code, config, schema, API, test artifact의 연결과 impact/stale/gap 후보를 탐색한다.
5. `keystone-coordinator`: Keystone context를 worker assignment로 만들고 worker report를
   Keystone workflow로 회수한다.

기존 `work-package-doc-architect`와 `subagent-work-coordinator` 스킬은 참고용 prototype이다.
이들은 최종 runtime dependency가 아니며 새 Keystone 스킬로 대체될 예정이다.

<!-- key: id=key.context-map.standards refs=key.topic.document-system key.doc.source key.topic.skill-contract key.standard.subagent -->
## 기준서

| 영역 | 경로 | 읽는 시점 |
|---|---|---|
| 색인 | `00_docs/standards/00_key-index.md` | 사용 가능한 기준서를 탐색할 때 먼저 읽는다 |
| 프로젝트 | `00_docs/standards/01_key-project-standard.md` | 프로젝트 공통 규칙, 원천 문서(2) 정책, 아티팩트 그래프(14), 스킬군 역할, coordinator 호환성을 확인할 때 읽는다 |
| Subagent | `00_docs/standards/subagents/key-standard-subagents.md` | helper/subagent의 bounded worker model, purpose preset, authority, injected skill contract, report status, workspace guard를 확인할 때 읽는다 |
| Artifact Graph | `00_docs/standards/artifacts/key-standard-artifact-graph.md` | graph model, ownership boundary, typed relation, locator, stale/gap handling, impact candidate 기준을 확인할 때 읽는다 |
| 스킬별 | `00_docs/standards/skills/00_key-index.md` | 개별 Keystone 스킬의 상세 기준서를 찾을 때 읽는다 |
| Reader | `00_docs/standards/skills/reader/key-standard-reader.md` | `keystone-reader`의 trigger, mode, output, read-only boundary를 확인할 때 읽는다 |
| Author | `00_docs/standards/skills/author/key-standard-author.md` | `keystone-author`의 기준서(3), 작업서(4), progress update boundary를 확인할 때 읽는다 |
| Clarify | `00_docs/standards/skills/clarify/key-standard-clarify.md` | `keystone-clarify`의 decision collection, reflection, Author handoff를 확인할 때 읽는다 |
| Linker | `00_docs/standards/skills/linker/key-standard-linker.md` | `keystone-linker`의 operational graph interpretation, impact analysis, stale/gap review, source surface handoff, worker assignment seed를 확인할 때 읽는다 |
| Coordinator | `00_docs/standards/skills/coordinator/key-standard-coordinator.md` | `keystone-coordinator`의 worker assignment/report, bounded worker routing, report, review, verification, acceptance flow를 확인할 때 읽는다 |

<!-- key: id=key.context-map.work-order refs=key.topic.document-system key.doc.source key.topic.work-sequence key.topic.work-round -->
## 작업서

| 작업 | 경로 | 상태 | 담당 영역 |
|---|---|---|---|
| Round 색인 | `00_docs/works/00_key-index.md` | active | active work round 탐색 |
| R001 Bootstrap Keystone | `00_docs/works/r001-bootstrap-keystone/00_key-index.md` | active | 초기 Keystone 기준 corpus와 스킬 기준서 |
| Document Tree Setup | `00_docs/works/r001-bootstrap-keystone/document-tree-setup/00_key-index.md` | accepted | `works/` tree 재정비 |
| Project Standard | `00_docs/works/r001-bootstrap-keystone/project-standard/00_key-index.md` | accepted | 전체 공통 기준서 |
| Reader Standard | `00_docs/works/r001-bootstrap-keystone/reader-standard/00_key-index.md` | accepted | `keystone-reader` 기준서 |
| Author Standard | `00_docs/works/r001-bootstrap-keystone/author-standard/00_key-index.md` | accepted | `keystone-author` 기준서와 작업서 생성 표준 |
| Clarify Standard | `00_docs/works/r001-bootstrap-keystone/clarify-standard/00_key-index.md` | accepted | `keystone-clarify` 기준서 |
| Coordinator Standard | `00_docs/works/r001-bootstrap-keystone/coordinator-standard/00_key-index.md` | accepted | `keystone-coordinator` 기준서 |
| Artifact Graph Standard | `00_docs/works/r001-bootstrap-keystone/artifact-graph-standard/00_key-index.md` | accepted | Artifact Graph 기준서 |
| Linker Standard | `00_docs/works/r001-bootstrap-keystone/linker-standard/00_key-index.md` | accepted | `keystone-linker` 기준서 |
| Skill Creation | `00_docs/works/r001-bootstrap-keystone/skill-creation/00_key-index.md` | planned | Keystone skill source 생성 |
| Integration Verification | `00_docs/works/r001-bootstrap-keystone/integration-verification/00_key-index.md` | planned | 통합 검증 |

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
    subagents/
      00_key-index.md
      key-standard-subagents.md
    artifacts/
      00_key-index.md
      key-standard-artifact-graph.md
    skills/
      00_key-index.md
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
    ...
```

기준서는 전체 공통 기준서에서 시작해 필요한 경우 스킬별 child 기준서로 내려간다. 작업서는
기준서 구조에 종속되지 않고 work round 안의 reviewable goal 단위로 만든다. Root works
index는 active round를 관리하고, round 내부 실행 순서는 해당 round의 `00_key-index.md`가
관리한다. 최종 작업서는 `key-work-{slug}.md` 형식을 사용한다.

<!-- key: id=key.context-map.section refs=key.topic.work-sequence key.topic.document-system key.topic.work-round -->
## 현재 작업 단계

현재 active round는 R001 Bootstrap Keystone이다. S00 문서 트리 재정비, S01 전체 기준서,
S02 reader 기준서, S03 author 기준서, S04 clarify 기준서, S05 coordinator 기준서,
S06 Artifact Graph 기준서, S07 linker 기준서는 accepted 상태다. 다음 planned work는 S08 Skill
Creation이다.

| Step | 제목 | 목적 |
|---|---|---|
| S00 | 문서 트리 재정비 | `works/` 기준으로 active work 문서와 진행 상태를 초기화한다 |
| S01 | 전체 기준서 | 프로젝트 공통 기준과 용어를 정리한다 |
| S02 | reader | `keystone-reader` 기준서를 정리한다 |
| S03 | author | `keystone-author` 기준서를 정리한다 |
| S04 | clarify | `keystone-clarify` 기준서를 정리한다 |
| S05 | coordinator | `keystone-coordinator` 기준서를 정리한다 |
| S06 | Artifact Graph | Artifact Graph 기준서를 정리한다 |
| S07 | linker | `keystone-linker` 기준서를 정리한다 |
| S08 | Skill 생성 | 다섯 개 Keystone skill source를 만든다 |
| S09 | 통합 검증 | 문서, artifact graph, skill source의 end-to-end 흐름을 검증한다 |

<!-- key: id=key.context-map.planned-keystone-skills refs=key.topic.skill-contract key.topic.bootstrap -->
## 계획된 Keystone 스킬

| 스킬 | 상태 | 목적 |
|---|---|---|
| `keystone-reader` | planned | 프로젝트를 파악하고 관련 기준서/작업서를 탐색하며 작업 준비 context를 만든다 |
| `keystone-author` | planned | 기준서와 작업서를 생성하고 승인된 원천 문서(2) 변경을 적용한다 |
| `keystone-clarify` | planned | 영향도 높은 결정(6)을 topic 단위로 수집하고 Author가 적용할 edit plan을 만든다 |
| `keystone-linker` | planned | Artifact Graph를 read-only로 해석하고 문서, capability, code, config, schema, API, test artifact의 impact/stale/gap 후보와 handoff seed를 보고한다 |
| `keystone-coordinator` | planned | worker assignment/report 기반 Goal assignment, report, review, verification, acceptance flow를 조율한다 |

<!-- key: id=key.context-map.prototype-skill-reference refs=key.topic.bootstrap key.topic.skill-contract -->
## Prototype 스킬 참고

| 스킬 | 이 프로젝트에서의 목적 |
|---|---|
| `work-package-doc-architect` | 향후 authoring 스킬을 위한 참고용 prototype |
| `subagent-work-coordinator` | 향후 coordination 스킬을 위한 참고용 prototype |
