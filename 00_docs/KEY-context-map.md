# 프로젝트 컨텍스트 맵

활성 Keystone 계획 문서는 `00_docs/` 아래에 둔다. 현재 active work tree는
`00_docs/works/`다.

## 프로젝트

이 저장소는 `keystone` 스킬 시스템을 정의하고 구현하기 위한 저장소다. 최종 산출물은
사람이 읽을 수 있는 원천 문서(2)를 바탕으로 함께 동작하는 독립 스킬들의 집합이다.

1. `keystone-reader`: 기준서(3)와 작업서(4)를 읽고 작업 준비 context를 만든다.
2. `keystone-author`: 기준서와 작업서를 작성하거나 승인된 범위에서 수정한다.
3. `keystone-clarify`: 정책, 범위, 문서, 스킬 계약에 관한 결정(6)을 topic 단위로 정리한다.
4. `keystone-coordinator`: main-supervised subagent workflow를 조율한다.

기존 `work-package-doc-architect`와 `subagent-work-coordinator` 스킬은 참고용 prototype이다.
이들은 최종 runtime dependency가 아니며 새 Keystone 스킬로 대체될 예정이다.

## 기준서

| 영역 | 경로 | 읽는 시점 |
|---|---|---|
| 색인 | `00_docs/standards/00_KEY-index.md` | 사용 가능한 기준서를 탐색할 때 먼저 읽는다 |
| 프로젝트 | `00_docs/standards/00_KEY-project-standard.md` | 프로젝트 공통 규칙, 원천 문서(2) 정책, 스킬군 역할, coordinator 호환성을 확인할 때 읽는다 |
| 스킬별 | `00_docs/standards/skills/00_KEY-index.md` | 개별 Keystone 스킬의 상세 기준서를 찾을 때 읽는다 |
| Reader | `00_docs/standards/skills/reader/KEY-standard-reader.md` | `keystone-reader`의 trigger, mode, output, read-only boundary를 확인할 때 읽는다 |
| Author | `00_docs/standards/skills/author/KEY-standard-author.md` | `keystone-author`의 기준서(3), 작업서(4), progress update boundary를 확인할 때 읽는다 |
| Clarify | `00_docs/standards/skills/clarify/KEY-standard-clarify.md` | `keystone-clarify`의 decision collection, reflection, Author handoff를 확인할 때 읽는다 |
| Coordinator | `00_docs/standards/skills/coordinator/KEY-standard-coordinator.md` | `keystone-coordinator`의 Goal assignment, routing, report, review, verification, acceptance flow를 확인할 때 읽는다 |

## 작업서

| 작업 | 경로 | 상태 | 담당 영역 |
|---|---|---|---|
| 작업서 색인 | `00_docs/works/00_KEY-index.md` | active | 실행 순서와 active work 탐색 |
| Document Tree Setup | `00_docs/works/document-tree-setup/00_KEY-index.md` | accepted | `works/` tree 재정비 |
| Project Standard | `00_docs/works/project-standard/00_KEY-index.md` | ready | 전체 공통 기준서 |
| Reader Standard | `00_docs/works/reader-standard/00_KEY-index.md` | planned | `keystone-reader` 기준서 |
| Author Standard | `00_docs/works/author-standard/00_KEY-index.md` | planned | `keystone-author` 기준서와 작업서 생성 표준 |
| Clarify Standard | `00_docs/works/clarify-standard/00_KEY-index.md` | planned | `keystone-clarify` 기준서 |
| Coordinator Standard | `00_docs/works/coordinator-standard/00_KEY-index.md` | planned | `keystone-coordinator` 기준서 |
| Skill Creation | `00_docs/works/skill-creation/00_KEY-index.md` | planned | Keystone skill source 생성 |
| Integration Verification | `00_docs/works/integration-verification/00_KEY-index.md` | planned | 통합 검증 |

## 문서 트리 정책

Keystone 문서는 영어 경로와 설정된 document root(1)를 사용한다. 현재 사용자 지시나
프로젝트 로컬 Keystone 설정이 이를 덮어쓰지 않으면 기본 root는 `00_docs/`다.

```text
00_docs/
  KEY-context-map.md
  standards/
    00_KEY-index.md
    00_KEY-project-standard.md
    skills/
      00_KEY-index.md
      reader/
        00_KEY-index.md
        KEY-standard-reader.md
      author/
        00_KEY-index.md
        KEY-standard-author.md
      clarify/
        00_KEY-index.md
        KEY-standard-clarify.md
      coordinator/
        00_KEY-index.md
        KEY-standard-coordinator.md
  works/
    00_KEY-index.md
    KEY-decisions.md
    document-tree-setup/
      00_KEY-index.md
      KEY-work-document-tree-setup.md
      KEY-progress.md
    project-standard/
      00_KEY-index.md
      KEY-work-project-standard.md
      KEY-progress.md
    ...
```

기준서는 전체 공통 기준서에서 시작해 필요한 경우 스킬별 child 기준서로 내려간다. 작업서는
기준서 구조에 종속되지 않고 reviewable goal 단위로 만든다. 실행 순서는
`00_docs/works/00_KEY-index.md`가 관리하며, 최종 작업서는 `KEY-work-{slug}.md` 형식을 사용한다.

## 현재 작업 단계

현재 active work는 S01이다. S00 문서 트리 재정비는 accepted 상태다.

| Step | 제목 | 목적 |
|---|---|---|
| S00 | 문서 트리 재정비 | `works/` 기준으로 active work 문서와 진행 상태를 초기화한다 |
| S01 | 전체 기준서 | 프로젝트 공통 기준과 용어를 정리한다 |
| S02 | reader | `keystone-reader` 기준서를 정리한다 |
| S03 | author | `keystone-author` 기준서를 정리한다 |
| S04 | clarify | `keystone-clarify` 기준서를 정리한다 |
| S05 | coordinator | `keystone-coordinator` 기준서를 정리한다 |
| S06 | Skill 생성 | 네 개 Keystone skill source를 만든다 |
| S07 | 통합 검증 | 문서와 skill source의 end-to-end 흐름을 검증한다 |

## 계획된 Keystone 스킬

| 스킬 | 상태 | 목적 |
|---|---|---|
| `keystone-reader` | planned | 프로젝트를 파악하고 관련 기준서/작업서를 탐색하며 작업 준비 context를 만든다 |
| `keystone-author` | planned | 기준서와 작업서를 생성하고 승인된 원천 문서(2) 변경을 적용한다 |
| `keystone-clarify` | planned | 영향도 높은 결정(6)을 topic 단위로 수집하고 Author가 적용할 edit plan을 만든다 |
| `keystone-coordinator` | planned | role 기반 Goal assignment, report, review, verification, acceptance flow를 조율한다 |

## 선택적 워크플로 참고

| 참고 | 사용 경계 |
|---|---|
| Superpowers | 사용자가 명시적으로 호출하거나 수락된 Keystone 문서가 허용한 경우에만 quality-assist 참고로 사용한다 |

## Prototype 스킬 참고

| 스킬 | 이 프로젝트에서의 목적 |
|---|---|
| `work-package-doc-architect` | 향후 authoring 스킬을 위한 참고용 prototype |
| `subagent-work-coordinator` | 향후 coordination 스킬을 위한 참고용 prototype |
