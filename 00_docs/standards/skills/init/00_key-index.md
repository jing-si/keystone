---
doc_type: standard_index
status: active
approval:
  state: accepted
  accepted_by: main
key:
  id: key.standard.skill.init.index
  refs:
    - key.role.init
    - key.topic.bootstrap
    - key.topic.initialization
    - key.doc.standard
---

# keystone-init 기준서 색인

<!-- key: id=key.standard.skill.init.index.documents refs=key.role.init key.topic.initialization key.doc.standard -->
## 문서

1. `key-standard-init.md`
   - `keystone-init`의 inspect, initialize, repair, scaffold write authority, 질문 경계,
     Author/Clarify handoff와 초기화 검증을 정의한다.

<!-- key: id=key.standard.skill.init.index.parent-standard refs=key.doc.standard key.topic.bootstrap -->
## 상위 기준서

1. `../../bootstrap/key-standard-bootstrap.md`
   - 런타임 권위 경계, 상태 모델, R000, Main 수락과 User Decision 공통 원칙을 정의한다.
2. `../../01_key-project-standard.md`
   - Keystone 공통 문서와 작업 모델을 정의한다.

<!-- key: id=key.standard.skill.init.index.reading-rules refs=key.role.init key.topic.runtime-independence -->
## 읽기 규칙

이 문서는 Keystone 저장소에서 Init을 개발·검수하기 위한 명세다. 소비 프로젝트의
`keystone-init` 실행 선행 문서가 아니다.
