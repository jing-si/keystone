---
doc_type: standard_index
key:
  id: key.standard.artifact.index
  refs:
    - key.topic.artifact-graph
    - key.topic.keystone-metadata
    - key.topic.code-anchor
    - key.doc.standard
---

# Artifact Graph 기준서 색인

이 색인은 Keystone artifact graph 기준서로 이동하기 위한 기준이다.

<!-- key: id=key.standard.artifact.index.current-standard refs=key.topic.artifact-graph key.doc.standard -->
## 현재 기준서

1. `key-standard-artifact-graph.md`
   - 문서, decision, work, capability, code/config/schema/API/test artifact의 metadata,
     ownership boundary, relation direction, locator, lifecycle, stale/gap handling,
     impact candidate 기준을 정의한다.

<!-- key: id=key.standard.artifact.index.parent-standard refs=key.doc.standard key.topic.document-system -->
## Parent 기준서

1. `../01_key-project-standard.md`
   - Keystone 원천 문서(2) 권위, metadata 상위 원칙, artifact graph, Change Set(17),
     Reader/Linker/Coordinator 역할 anchor를 정의한다.

<!-- key: id=key.standard.artifact.index.reading-rules refs=key.doc.standard key.topic.artifact-graph key.topic.impact-review -->
## 읽기 규칙

1. 문서와 code/config/schema/API/test artifact 연결, relation propagation, impact candidate,
   stale/gap 판단이 필요하면 `key-standard-artifact-graph.md`를 읽는다.
2. Artifact graph 기준은 원천 문서(2) 권위와 Main acceptance 규칙을 대체하지 않는다.
3. Artifact graph 후보를 실제 변경으로 연결해야 하면 `../skills/linker/00_key-index.md`,
   `../skills/author/00_key-index.md`, `../skills/coordinator/00_key-index.md`를 함께 확인한다.
4. Parent 기준서와 이 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의 결정(6)을
   받는다. 결정 전까지는 parent 기준서를 임시 우선 기준으로 삼는다.
