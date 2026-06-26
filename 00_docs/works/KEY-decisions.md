---
doc_type: decisions
key:
  id: key.work.decisions
  refs:
    - key.doc.decision
    - key.doc.work
    - key.topic.document-system
    - key.topic.key-prefix
    - key.topic.work-round
---

# 작업서 결정 기록(6)

이 문서는 `00_docs/works/` tree에 적용되는 공통 결정(6)을 기록한다.

<!-- key: id=key.work.decisions.dec-works-001 refs=key.doc.decision key.doc.work key.topic.document-system -->
## DEC-WORKS-001: Active work tree는 `works/`를 사용한다

- 관련 work: Document Tree Setup
- 상태: accepted
- 결정: 새 Keystone 작업 문서는 `00_docs/works/` 아래에 둔다. 기존 `00_docs/work-packages/`
  문서는 active 작업 문서로 유지하지 않는다.
- 이유: 현재 기준서의 `standards/`와 `works/` tree 정책에 맞추고 legacy 경로와 현재 진행
  상태의 충돌을 제거하기 위해서다.

<!-- key: id=key.work.decisions.dec-works-002 refs=key.doc.decision key.doc.work key.topic.document-system -->
## DEC-WORKS-002: 작업서는 기준서 구조에 종속되지 않는다

- 관련 work: Author Standard
- 상태: accepted
- 결정: 작업서는 기준서별, 기능별, 구현 단계별, 검증 단계별로 만들 수 있다. 관련 기준서를
  참조하되 실행 순서는 기준서 tree가 아니라 work round index 또는 별도 상위 work plan이
  관리한다.
- 이유: 기준서는 장기 규칙이고 작업서는 현재 실행 순서와 범위를 담기 때문에 두 구조가 항상
  같을 필요가 없다.

<!-- key: id=key.work.decisions.dec-works-003 refs=key.doc.decision key.topic.work-sequence key.doc.work key.topic.work-round -->
## DEC-WORKS-003: R001 작업 순서는 S00-S07로 둔다

- 관련 work: Document Tree Setup
- 상태: accepted
- 결정: R001 Bootstrap Keystone round의 작업 순서는 S00 문서 트리 재정비, S01 전체 기준서,
  S02 reader, S03 author, S04 clarify, S05 coordinator, S06 Skill 생성, S07 통합 검증 순서로
  둔다.
- 이유: 문서 구조를 먼저 안정화하고, 공통 기준서와 스킬별 기준서를 분리한 뒤 구현과 통합
  검증으로 넘어가기 위해서다.

<!-- key: id=key.work.decisions.dec-works-004 refs=key.doc.decision key.topic.key-prefix key.topic.document-system -->
## DEC-WORKS-004: Keystone-managed 문서는 key prefix를 사용한다

- 관련 work: Project Standard
- 상태: accepted
- 결정: Keystone-managed Markdown 문서는 파일명에 lower-case `key` prefix를 사용한다. 문서
  순서를 정해야 하는 경우 `{number}_key-{slug}.md`를 사용하고, 그 외에는
  `key-{slug}.md`를 사용한다. 같은 위치에서 첫 순서 문서는 `00_`, 다음 순서 문서는 `01_`,
  그 다음은 `02_`를 사용한다. 파일명 단어 구분은 `-`로 통일한다.
- 이유: Keystone 결과물인지 파일명만으로 식별해 Reader, Author, Clarify, Coordinator
  routing 기준으로 사용할 수 있게 하기 위해서다.

<!-- key: id=key.work.decisions.dec-works-005 refs=key.doc.decision key.topic.work-round key.topic.document-system key.doc.work -->
## DEC-WORKS-005: 작업서는 round 단위로 묶는다

- 관련 work: Project Standard
- 상태: accepted
- 결정: `works/00_key-index.md`는 전체 work round 목록을 관리한다. 각 round는
  `r{number}-{slug}` folder를 가지며, `r`은 round를 뜻한다. 각 round 안에서는 작업 순서를
  `S00`부터 다시 시작한다.
- 이유: 기준서는 프로젝트의 지속 기준이지만 작업서는 특정 시점의 기준서와 목표를 바탕으로 한
  실행 차수이기 때문이다.
