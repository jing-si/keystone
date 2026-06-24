---
doc_type: decisions
key:
  id: key.work.decisions
  refs:
    - key.doc.decision
    - key.doc.work
    - key.topic.document-system
    - key.topic.key-prefix
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
  참조하되 실행 순서는 기준서 tree가 아니라 `works/00_KEY-index.md` 또는 별도 상위 work plan이
  관리한다.
- 이유: 기준서는 장기 규칙이고 작업서는 현재 실행 순서와 범위를 담기 때문에 두 구조가 항상
  같을 필요가 없다.

<!-- key: id=key.work.decisions.dec-works-003 refs=key.doc.decision key.topic.work-sequence key.doc.work -->
## DEC-WORKS-003: 현재 작업 순서는 S00-S07로 둔다

- 관련 work: Document Tree Setup
- 상태: accepted
- 결정: 작업 순서는 S00 문서 트리 재정비, S01 전체 기준서, S02 reader, S03 author,
  S04 clarify, S05 coordinator, S06 Skill 생성, S07 통합 검증 순서로 둔다.
- 이유: 문서 구조를 먼저 안정화하고, 공통 기준서와 스킬별 기준서를 분리한 뒤 구현과 통합
  검증으로 넘어가기 위해서다.

<!-- key: id=key.work.decisions.dec-works-004 refs=key.doc.decision key.topic.key-prefix key.topic.document-system -->
## DEC-WORKS-004: Keystone-managed 문서는 KEY prefix를 사용한다

- 관련 work: Project Standard
- 상태: accepted
- 결정: Keystone-managed Markdown 문서는 파일명에 `KEY` prefix를 사용한다. 정렬용 숫자가
  필요한 경우 `{number}_KEY-{slug}.md`를 사용하고, 그 외에는 `KEY-{slug}.md`를 사용한다.
  파일명 단어 구분은 `-`로 통일한다.
- 이유: Keystone 결과물인지 파일명만으로 식별해 Reader, Author, Clarify, Coordinator
  routing 기준으로 사용할 수 있게 하기 위해서다.
