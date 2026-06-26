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
기준서와 목표를 바탕으로 진행하는 하나의 작업 차수이며, round 안에서 작업 순서는 `S00`부터
다시 시작한다.

<!-- key: id=key.work.index.rounds refs=key.topic.work-round key.doc.work key.topic.work-sequence -->
## Work rounds

| Round | 제목 | 경로 | 상태 | 목적 |
|---|---|---|---|---|
| R001 | Bootstrap Keystone | `r001-bootstrap-keystone/00_key-index.md` | active | Keystone 기준 corpus와 초기 스킬 기준서를 만든다 |

<!-- key: id=key.work.index.common-decisions refs=key.doc.decision key.doc.work key.topic.work-round -->
## 공통 결정

- 여러 round에 영향을 주는 결정 기록(6): `key-decisions.md`

<!-- key: id=key.work.index.reading-rules refs=key.doc.work key.doc.source key.topic.document-system key.topic.work-round -->
## 읽기 규칙

1. 프로젝트 전체 방향은 `00_docs/key-context-map.md`를 먼저 읽는다.
2. 공통 기준과 용어는 `00_docs/standards/01_key-project-standard.md`를 따른다.
3. 현재 active round는 이 파일의 `Work rounds` 표를 권위로 삼는다.
4. Round 내부 실행 순서는 해당 round의 `00_key-index.md`에서 확인한다.
5. 각 work의 세부 목표와 검증은 해당 work node의 `key-work-{slug}.md`에서 확인한다.
6. 각 work의 진행 상태는 해당 work node의 `key-progress.md`에서 확인한다.

<!-- key: id=key.work.index.round-creation-rules refs=key.doc.work key.topic.document-system key.topic.work-round -->
## Work round 생성 규칙

1. Work round folder는 `r{number}-{slug}` 형식을 사용한다.
2. `r`은 round를 뜻하며, 특정 시점의 기준서와 목표를 바탕으로 진행하는 하나의 작업 차수를
   나타낸다.
3. 각 round는 `00_key-index.md`를 가지며, round 안의 실행 순서는 `S00`부터 다시 시작한다.
4. Round 안의 work node는 하나의 reviewable goal을 가져야 한다.
5. 너무 작은 작업은 별도 work node로 만들지 않고 관련 work의 step으로 흡수한다.
