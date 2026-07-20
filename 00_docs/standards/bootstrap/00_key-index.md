---
doc_type: standard_index
status: active
approval:
  state: accepted
  accepted_by: main
key:
  id: key.standard.bootstrap.index
  refs:
    - key.topic.bootstrap
    - key.topic.initialization
    - key.topic.runtime-independence
    - key.doc.standard
---

# Bootstrap 기준서 색인

이 색인은 Keystone을 처음 도입하는 프로젝트의 초기화와 정상 운영 전환 기준으로 이동하기
위한 진입점이다.

<!-- key: id=key.standard.bootstrap.index.documents refs=key.topic.bootstrap key.topic.initialization key.doc.standard -->
## 문서

1. `key-standard-bootstrap.md`
   - 런타임 권위 경계, 초기화 상태, R000 Project Foundation, Main 수락과 User Decision,
     handoff/resume, fail-soft 공통 원칙을 정의한다.

<!-- key: id=key.standard.bootstrap.index.related-standards refs=key.doc.standard key.topic.skill-contract -->
## 관련 기준서

1. `../01_key-project-standard.md`
   - Keystone 공통 권위, 문서·작업 모델과 핵심 스킬 역할을 정의한다.
2. `../skills/init/key-standard-init.md`
   - `keystone-init`의 inspect, initialize, repair 계약과 검증 시나리오를 정의한다.

<!-- key: id=key.standard.bootstrap.index.reading-rules refs=key.topic.bootstrap key.topic.runtime-independence key.doc.standard -->
## 읽기 규칙

1. 초기화 상태나 런타임 권위 경계를 판단할 때 `key-standard-bootstrap.md`를 먼저 읽는다.
2. 실제 Init 동작을 개발하거나 검수할 때 `../skills/init/key-standard-init.md`를 함께 읽는다.
3. 이 저장소의 `standards/skills/**`는 스킬 개발 명세이며 소비 프로젝트의 런타임 선행
   문서가 아니다.
