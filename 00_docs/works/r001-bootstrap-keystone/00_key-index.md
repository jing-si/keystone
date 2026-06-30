---
doc_type: work_round
key:
  id: key.work.round.r001-bootstrap-keystone.index
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.document-system
    - key.doc.source
---

# R001 Bootstrap Keystone 작업서(4) 색인

이 round는 Keystone 기준 corpus와 초기 스킬 기준서를 만들기 위한 첫 작업 차수다. 작업서
구조는 기준서 tree에 종속되지 않는다. 각 work node는 하나의 reviewable goal을 가지며,
round 안의 실행 순서는 이 색인에서 `S00`부터 관리한다.

<!-- key: id=key.work.round.r001-bootstrap-keystone.execution-order refs=key.topic.work-sequence key.doc.work key.topic.document-system key.topic.work-round -->
## 실행 순서

| 순서 | Work | 경로 | 상태 | 목적 |
|---|---|---|---|---|
| S00 | Document Tree Setup | `document-tree-setup/00_key-index.md` | accepted | `work-packages/`를 폐기하고 `works/` 기준 작업 트리를 만든다 |
| S01 | Project Standard | `project-standard/00_key-index.md` | ready | 전체 공통 기준서를 정리한다 |
| S02 | Reader Standard | `reader-standard/00_key-index.md` | planned | `keystone-reader` 기준서를 정리한다 |
| S03 | Author Standard | `author-standard/00_key-index.md` | planned | `keystone-author` 기준서와 작업서 생성 표준을 정리한다 |
| S04 | Clarify Standard | `clarify-standard/00_key-index.md` | planned | `keystone-clarify` 기준서를 정리한다 |
| S05 | Coordinator Standard | `coordinator-standard/00_key-index.md` | planned | `keystone-coordinator` 기준서를 정리한다 |
| S06 | Artifact Graph Standard | `artifact-graph-standard/00_key-index.md` | planned | Artifact Graph 기준서를 정리한다 |
| S07 | Linker Standard | `linker-standard/00_key-index.md` | planned | `keystone-linker` 기준서를 정리한다 |
| S08 | Skill Creation | `skill-creation/00_key-index.md` | planned | 다섯 개 Keystone skill source를 만든다 |
| S09 | Integration Verification | `integration-verification/00_key-index.md` | planned | 문서, artifact graph, skill source의 end-to-end 흐름을 검증한다 |

<!-- key: id=key.work.round.r001-bootstrap-keystone.common-decisions refs=key.doc.decision key.doc.work key.topic.work-round -->
## 공통 결정

- Round 공통 결정 기록(6): 필요한 경우 `key-decisions.md`
- 여러 round에 영향을 주는 결정 기록(6): `../key-decisions.md`

<!-- key: id=key.work.round.r001-bootstrap-keystone.reading-rules refs=key.doc.work key.doc.source key.topic.document-system key.topic.work-round -->
## 읽기 규칙

1. 프로젝트 전체 방향은 `00_docs/key-context-map.md`를 먼저 읽는다.
2. 공통 기준과 용어는 `00_docs/standards/01_key-project-standard.md`를 따른다.
3. 전체 active round는 `00_docs/works/00_key-index.md`에서 확인한다.
4. 이 round 안의 실행 순서는 이 파일의 `실행 순서` 표를 권위로 삼는다.
5. 각 work의 세부 목표와 검증은 해당 work node의 `key-work-{slug}.md`에서 확인한다.
6. 각 work의 진행 상태는 해당 work node의 `key-progress.md`에서 확인한다.

<!-- key: id=key.work.round.r001-bootstrap-keystone.work-creation-rules refs=key.doc.work key.topic.document-system key.topic.work-round -->
## 작업서 생성 규칙

1. 작업서는 기준서 파일 구조에 종속되지 않는다.
2. 기준서별, 기능별, 구현 단계별, 검증 단계별로 독립 work를 만들 수 있다.
3. 작업서는 관련 기준서를 참조하지만, 기준서 안에 실행 순서를 박지 않는다.
4. 실행 순서는 이 round 색인이나 별도 상위 work plan에서 관리한다.
5. 너무 작은 작업은 별도 work로 만들지 않고 관련 work의 step으로 흡수한다.
