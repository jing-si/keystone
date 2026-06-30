---
doc_type: standard_index
key:
  id: key.standard.skill.author.index
  refs:
    - key.role.author
    - key.role.subagent
    - key.standard.subagent
    - key.topic.document-authoring
    - key.topic.work-creation
    - key.topic.artifact-graph
    - key.doc.standard
---

# keystone-author 기준서 색인

이 색인은 `keystone-author` child 기준서로 이동하기 위한 기준이다.

<!-- key: id=key.standard.skill.author.index.documents refs=key.role.author key.topic.document-authoring key.topic.work-creation key.doc.standard -->
## 문서

1. `key-standard-author.md`
   - `keystone-author`의 목적, trigger/non-trigger, 기준서(3)와 작업서(4)
     creation/revision, clarify result 적용, Change Set(17) 작성 규칙, progress update
     boundary를 정의한다.

<!-- key: id=key.standard.skill.author.index.parent-standard refs=key.role.author key.doc.standard key.topic.document-system key.standard.subagent -->
## Parent 기준서

1. `../../01_key-project-standard.md`
   - Keystone 공통 용어, 원천 문서(2) 권위, 기준서(3)/작업서(4) 책임, parent-child
     기준서 tree, Change Set(17), work step field, document root, naming rule을 정의한다.
2. `../../subagents/key-standard-subagents.md`
   - Author가 사용할 수 있는 문서 helper의 lane, role, authority, 공통 경계를 정의한다.

<!-- key: id=key.standard.skill.author.index.reading-rules refs=key.role.author key.topic.document-authoring key.doc.standard -->
## 읽기 규칙

1. Author의 공통 문서 작성 정책은 `../../01_key-project-standard.md`의
   `STD-KEYSTONE-003`, `STD-KEYSTONE-007`, `STD-KEYSTONE-010`,
   `STD-KEYSTONE-011`, `STD-KEYSTONE-012`, `STD-KEYSTONE-013`,
   `STD-KEYSTONE-022`, `STD-KEYSTONE-023`, `STD-KEYSTONE-032`,
   `STD-KEYSTONE-042`를 먼저 확인한다.
2. Artifact graph impact/stale 후보 해석이 필요하면 `../linker/00_key-index.md`를 읽는다.
3. Author가 `doc-explorer` 또는 `doc-impact-writer` helper를 사용할 수 있는지 판단해야 하면
   `../../subagents/key-standard-subagents.md`를 읽는다.
4. Author 구현 또는 상세 계약 검토가 필요하면 `key-standard-author.md`를 읽는다.
5. Parent 기준서와 이 child 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의
   결정(6)을 받는다. 결정 전까지는 parent 기준서를 임시 우선 기준으로 삼는다.
