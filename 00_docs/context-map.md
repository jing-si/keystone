# 프로젝트 컨텍스트 맵

활성 프로젝트 계획 문서는 모두 `00_docs/` 아래에 둔다.

## 프로젝트

이 저장소는 `keystone` 스킬 시스템을 정의하고 구현하기 위한 저장소다. 최종 산출물은
공유 원천 문서(2)를 바탕으로 함께 동작하는 독립 스킬들의 집합이다.

1. Clarification 스킬: 정책, 범위, 문서 결정사항을 명확히 한다.
2. Authoring 스킬: 기준서(3)와 작업서(4)를 작성한다.
3. Reading/work-preparation 스킬: 기준서와 작업서를 읽고 작업을 준비한다.
4. Subagent coordination 스킬: role 기반 goal을 subagent에게 배정하고 보고를 수신한다.

기존 `work-package-doc-architect`와 `subagent-work-coordinator` 스킬은 이
프로젝트의 참고용 prototype이다. 이들은 최종 의존성이 아니며 새 Keystone 스킬로
대체될 예정이다.

## 기준서

| 영역 | 경로 | 읽는 시점 |
|---|---|---|
| 색인 | `00_docs/standards/00_index.md` | 사용 가능한 기준서를 탐색할 때 먼저 읽는다 |
| 프로젝트 | `00_docs/standards/00_project-standard.md` | 프로젝트 공통 규칙, 원천 문서(2) 정책, 스킬군 역할, coordinator 호환성을 확인할 때 항상 읽는다 |
| 스킬별 | `00_docs/standards/skills/00_index.md` | 개별 Keystone 스킬의 상세 기준서를 찾을 때 읽는다 |
| Clarify | `00_docs/standards/skills/clarify/standard-clarify.md` | `keystone-clarify`의 trigger, 질문 수집, reflection, Author handoff, 단순 오탈자 직접 수정 boundary를 확인할 때 읽는다 |
| Author | `00_docs/standards/skills/author/standard-author.md` | `keystone-author`의 기준서(3), 작업서(4), progress update boundary를 확인할 때 읽는다 |
| Reader | `00_docs/standards/skills/reader/standard-reader.md` | `keystone-reader`의 trigger, mode, output, read-only boundary를 확인할 때 읽는다 |
| Coordinator | `00_docs/standards/skills/coordinator/standard-coordinator.md` | `keystone-coordinator`의 Goal assignment, subagent routing, report, review, verification, acceptance flow를 확인할 때 읽는다 |

## 향후 문서 트리 정책

이 정책은 수락 이후 새 Keystone 기준서와 작업서에 적용한다. 현재 S01 작업
패키지는 migration이 명시적으로 승인될 때까지 `work-packages/` 아래에 둔다.

향후 Keystone 문서는 영어 경로와 설정된 문서 루트를 사용한다. 현재 사용자
지시나 프로젝트 로컬 Keystone 설정이 이를 덮어쓰지 않으면 기본 루트는
`00_docs/`다.

```text
00_docs/
  standards/
    00_index.md
    00_project-standard.md
    skills/
      00_index.md
      clarify/
        00_index.md
        standard-clarify.md
      author/
        00_index.md
        standard-author.md
      reader/
        00_index.md
        standard-reader.md
      coordinator/
        00_index.md
        standard-coordinator.md
  works/
    00_index.md
    ...
```

기준서는 전체 공통 기준서에서 시작해 필요한 경우 스킬별 child 기준서로 내려간다.
모든 standards 또는 works 노드는 탐색용 `00_index.md`를 가진다. 최종 노드는
하위 노드가 없으며 `standard-{slug}.md`, `work-{slug}.md`, `progress.md` 같은
상세 파일을 포함할 수 있다.

Keystone 프로젝트 설정값은 초기 설정 대화 이후 `.keystone/config.yaml`에 기록한다.

1. 문서 루트
2. 원천 문서(2) Git 정책
3. 파생 에이전트 문서(8) Git 정책
4. Keystone 출력 언어 정책

개인용, 로컬 전용, 민감한 override는 `.keystone/config.local.yaml`에 둔다.

이 저장소는 Keystone 스킬 자체를 정의하고 구현한다. 따라서 S01 또는 S02 동안 이
저장소에는 `.keystone/config.yaml`이 필요하지 않다. config 파일은 향후 target
project에서 Keystone을 사용할 때의 runtime 동작에 속한다. 단, 이후 구현 또는
테스트 단계에서 fixture나 예시 config를 이 저장소에 만들도록 명시적으로 요구한
경우에는 예외로 한다.

이 저장소의 Keystone 원천 문서(2) 기본 언어는 한국어다. 파일 경로, 설정 key,
schema value, status value, skill name, step ID, decision ID, standard ID처럼
기계적으로 참조되는 literal 값은 영어 또는 기존 값을 유지한다.

## 작업 패키지

| 작업 패키지 | 경로 | 상태 | 담당 영역 |
|---|---|---|---|
| WP-KEYSTONE-SKILL | `00_docs/work-packages/WP-KEYSTONE-SKILL/00_index.md` | active | Keystone 스킬 시스템 설계와 구현 |

## 계획된 Keystone 스킬

| 스킬 역할 | 상태 | 목적 |
|---|---|---|
| `keystone-clarify` | planned | 원천 문서(2)를 변경하기 전에 정책, 범위, 문서, 스킬 계약에 관한 영향도 높은 결정(6)을 주제별로 수집한다 |
| `keystone-author` | planned | subagent 크기의 작업 단위를 만들기 쉬운 구조로 재사용 가능한 기준서와 작업서를 생성하고 수정한다 |
| `keystone-reader` | planned | 프로젝트를 파악하고 관련 기준서/작업서를 탐색하며, main context를 보존한 채 main-agent 작업을 준비한다 |
| `keystone-coordinator` | planned | role 기반 goal을 subagent에게 배정하고 보고를 수신하며, main agent가 감독 역할을 유지하게 한다 |

## 현재 구조 메모

기존 `WP-KEYSTONE-SKILL` 패키지는 사용자가 migration 여부를 명시적으로 선택할
때까지 `work-packages/` 아래에 둔다. 새 Keystone 문서는 위의 `standards/`와
`works/` 트리 정책을 따른다.

## 선택적 워크플로 참고

| 참고 | 사용 경계 |
|---|---|
| Superpowers | 사용자가 명시적으로 호출하거나 수락된 Keystone 문서가 허용한 경우에만 brainstorming, planning, TDD, debugging, review, skill testing을 보조하는 선택적 quality-assist 참고 자료 |

## Prototype 스킬 참고

| 스킬 | 이 프로젝트에서의 목적 |
|---|---|
| `work-package-doc-architect` | 향후 기준서/작업서 authoring 스킬을 위한 참고용 prototype |
| `subagent-work-coordinator` | 향후 subagent coordination 스킬을 위한 참고용 prototype |

## Legacy 참고

현재 연결된 legacy 계획 문서는 없다.
