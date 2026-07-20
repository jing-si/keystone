---
doc_type: work_round
status: active
approval:
  state: accepted
  accepted_by: main
round_status: accepted
key:
  id: key.work.round.r002-bootstrap-runtime-independence.index
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.bootstrap
    - key.topic.runtime-independence
    - key.topic.initialization
---

# R002 Bootstrap and Runtime Independence 작업서 색인

이 round는 R001 review에서 확인한 빈 프로젝트 bootstrap 순환 의존을 수정한다. R001의 accepted
S00-S07은 이력으로 보존하고, 미수락 S08-S09를 이 round의 새 기준과 구현 순서로 대체한다.

<!-- key: id=key.work.round.r002-bootstrap-runtime-independence.execution-order refs=key.topic.work-sequence key.doc.work key.topic.bootstrap -->
## 실행 순서

| 순서 | Work | 경로 | 상태 | 목적 |
|---|---|---|---|---|
| S01 | Bootstrap Runtime Standard | `bootstrap-runtime-standard/00_key-index.md` | accepted | Init, R000, runtime authority, Main/User Decision, skill별 fail-soft 기준을 개편한다 |
| S02 | Skill Runtime Implementation | `skill-runtime-implementation/00_key-index.md` | accepted | 수락된 기준을 여섯 `SKILL.md`에 구현하고 forward test로 검증했다 |

<!-- key: id=key.work.round.r002-bootstrap-runtime-independence.decisions refs=key.doc.decision key.topic.work-round -->
## 공통 결정

- 여러 round에 영향을 주는 결정: `../key-decisions.md`의 `DEC-WORKS-014`부터
  `DEC-WORKS-019`

<!-- key: id=key.work.round.r002-bootstrap-runtime-independence.reading-rules refs=key.doc.work key.doc.source key.topic.work-recovery -->
## 읽기 규칙

1. 프로젝트 방향은 `00_docs/key-context-map.md`를 먼저 읽는다.
2. Bootstrap 공통 기준은 `00_docs/standards/bootstrap/00_key-index.md`를 따른다.
3. 현재 상태는 각 work node의 `key-progress.md`에서 확인한다.
4. S01 기준을 S02의 여섯 skill source 구현과 검증에 적용했다.
5. 설치·패키징·배포는 R002 범위에 포함하지 않는다.
