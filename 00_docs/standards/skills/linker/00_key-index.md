---
doc_type: standard_index
key:
  id: key.standard.skill.linker.index
  refs:
    - key.role.linker
    - key.topic.artifact-graph
    - key.topic.impact-review
    - key.doc.standard
---

# keystone-linker 기준서 색인

이 색인은 `keystone-linker` child 기준서로 이동하기 위한 기준이다.

<!-- key: id=key.standard.skill.linker.index.documents refs=key.role.linker key.topic.artifact-graph key.doc.standard -->
## 문서

1. `key-standard-linker.md`
   - `keystone-linker`의 artifact discovery, impact analysis, stale review, execution context
     seed mode와 output contract를 정의한다.

<!-- key: id=key.standard.skill.linker.index.parent-standard refs=key.role.linker key.doc.standard key.topic.artifact-graph -->
## Parent 기준서

1. `../../01_key-project-standard.md`
   - Keystone 공통 용어, 원천 문서(2) 권위, metadata 상위 원칙, Linker 책임 anchor를 정의한다.
2. `../../artifacts/key-standard-artifact-graph.md`
   - Artifact namespace, typed relation, metadata admission, locator, stale handling,
     impact candidate 기준을 정의한다.

<!-- key: id=key.standard.skill.linker.index.reading-rules refs=key.role.linker key.doc.standard key.topic.impact-review -->
## 읽기 규칙

1. Linker 관련 작업을 준비할 때는 `../../01_key-project-standard.md`의
   `STD-KEYSTONE-015`, `STD-KEYSTONE-017`, `STD-KEYSTONE-018`, `STD-KEYSTONE-027`,
   `STD-KEYSTONE-044`를 먼저 확인한다.
2. Artifact graph 상세 기준이 필요하면 `../../artifacts/key-standard-artifact-graph.md`를 읽는다.
3. Linker 구현 또는 상세 계약 검토가 필요하면 `key-standard-linker.md`를 읽는다.
4. Parent 기준서와 이 child 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의
   결정(6)을 받는다. 결정 전까지는 parent 기준서를 임시 우선 기준으로 삼는다.
