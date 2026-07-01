---
doc_type: standard_index
key:
  id: key.standard.index
  refs:
    - key.topic.document-system
    - key.topic.artifact-graph
    - key.doc.standard
    - key.topic.skill-contract
    - key.doc.source
    - key.standard.subagent
    - key.standard.artifact
    - key.topic.work-round
---

# 기준서(3) 색인

<!-- key: id=key.standard.index.current-standard refs=key.topic.document-system key.doc.standard key.topic.skill-contract key.standard.subagent key.standard.artifact -->
## 현재 기준서

1. 전체 공통 기준서: `01_key-project-standard.md`
   - Keystone의 원천 문서(2), 기준서(3), 작업서(4), 진행 기록(5), 결정(6), 파생
     에이전트 문서(8), 아티팩트 그래프(14), `standards/`와 `works/` tree, 스킬 역할, verification 정책을
     정의한다.
2. Subagent 기준서 색인: `subagents/00_key-index.md`
   - Keystone helper/subagent의 bounded worker model, purpose preset, authority, injected
     skill contract, report status, single workspace guard, 공통 금지와 stop condition을
     정의한다.
3. 스킬별 기준서 색인: `skills/00_key-index.md`
   - Keystone 스킬별 child 기준서로 이동하기 위한 색인이다.
4. Artifact Graph 기준서 색인: `artifacts/00_key-index.md`
   - source document, decision, work, capability, code, config, schema, API, test artifact의 metadata,
     ownership boundary, relation, locator, stale/gap handling, impact candidate 기준으로 이동하기 위한
     색인이다.
5. Reader 기준서: `skills/reader/key-standard-reader.md`
   - `keystone-reader`의 trigger, mode, read-only boundary, output contract,
     mismatch handling을 정의한다.
6. Author 기준서: `skills/author/key-standard-author.md`
   - `keystone-author`의 기준서(3)와 작업서(4) creation/revision, clarify result 적용,
     progress update boundary를 정의한다.
7. Clarify 기준서: `skills/clarify/key-standard-clarify.md`
   - `keystone-clarify`의 topic-scoped decision collection, reflection, edit plan,
     Author handoff를 정의한다.
8. Linker 기준서: `skills/linker/key-standard-linker.md`
   - `keystone-linker`의 operational graph interpretation, artifact discovery, impact analysis,
     stale/gap review, source surface handoff, worker assignment seed output을 정의한다.
9. Coordinator 기준서: `skills/coordinator/key-standard-coordinator.md`
   - `keystone-coordinator`의 worker assignment/report, routing, report, review,
     verification, acceptance flow를 정의한다.

<!-- key: id=key.standard.index.reading-rules refs=key.doc.source key.doc.standard key.topic.document-system key.standard.subagent key.topic.work-round -->
## 읽기 규칙

1. Keystone 원천 문서(2)를 변경하거나 Keystone 작업을 준비하기 전에
   `01_key-project-standard.md`를 먼저 읽는다.
2. Subagent purpose preset, authority, report status, workspace guard가 필요하면
   `subagents/00_key-index.md`를 읽는다.
3. 문서와 code/config/schema/API/test artifact 연결, graph ownership boundary, impact candidate,
   stale/gap 판단이 필요하면 `artifacts/00_key-index.md`를 읽는다.
4. 스킬별 상세 계약이 필요하면 `skills/00_key-index.md`에서 해당 child 기준서로 내려간다.
5. 현재 active work round는 `00_docs/works/00_key-index.md`에서 찾고, round 내부 실행 순서는
   해당 round의 `00_key-index.md`에서 찾는다.
6. 전체 공통 기준서와 child 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의
   결정(6)을 받는다. 결정 전까지는 전체 공통 기준서를 임시 우선 기준으로 삼는다.
