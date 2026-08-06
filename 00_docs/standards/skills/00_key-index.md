---
doc_type: standard_index
key:
  id: key.standard.skills.index
  refs:
    - key.topic.skill-contract
    - key.doc.standard
    - key.topic.document-system
    - key.topic.artifact-graph
---

# Keystone 스킬별 기준서 색인

이 색인은 Keystone 저장소에서 스킬을 개발·검수하기 위한 child 기준서로 이동하는 기준이다.
소비 프로젝트의 런타임 선행 문서가 아니다. 전체 공통 규칙은 먼저
`../01_key-project-standard.md`를 읽고, 개별 스킬의 상세 계약이 필요할 때 이 색인에서
해당 스킬 기준서로 내려간다.

<!-- key: id=key.standard.skills.index.current-skill-standards refs=key.topic.skill-contract key.doc.standard key.topic.document-system -->
## 현재 스킬별 기준서

1. `init/00_key-index.md`
   - `keystone-init`의 inspect/initialize/repair와 R000 bootstrap 계약을 정의한다.
2. `clarify/00_key-index.md`
   - `keystone-clarify`의 topic-scoped decision collection과 document update flow를
     정의한다.
3. `author/00_key-index.md`
   - `keystone-author`의 기준서(3)와 작업서(4) creation/revision contract를 정의한다.
4. `reader/00_key-index.md`
   - `keystone-reader`의 session orientation, docs-first context readiness, lazy repository scope,
     recursion guard, read-only boundary와 output contract를 정의한다.
5. `linker/00_key-index.md`
   - `keystone-linker`의 permissionless owner/ref index readiness, optional graph projection,
     artifact discovery, impact/stale/gap review와 source surface handoff를 정의한다.
6. `coordinator/00_key-index.md`
   - `keystone-coordinator`의 Context Pack, direct/orchestration mode, bounded execution routing,
     report, Keystone closure, review, verification과 acceptance flow를 정의한다.

<!-- key: id=key.standard.skills.index.planned-skill-standards refs=key.topic.skill-contract key.doc.standard -->
## 계획된 스킬별 기준서

현재 추가로 계획된 스킬별 기준서는 없다. `keystone-init`의 실제 `SKILL.md` 구현은 R002 후속
work에 남아 있다.

<!-- key: id=key.standard.skills.index.reading-rules refs=key.doc.standard key.topic.document-system key.topic.skill-contract -->
## 읽기 규칙

1. 전체 정책과 공통 용어는 `../01_key-project-standard.md`를 먼저 따른다.
2. Artifact graph 자체의 metadata, relation, stale handling 기준은
   `../artifacts/00_key-index.md`를 따른다.
3. 스킬별 기준서는 전체 공통 기준서를 반복하지 않고 개별 스킬의 상세 계약만 보강한다.
4. 설치된 skill package는 이 개발 명세의 런타임 계약을 자체 포함해야 하며 소비 프로젝트의
   `standards/skills/**`를 요구하지 않는다.
5. 전체 공통 기준서와 스킬별 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의
   결정(6)을 받는다. 결정 전까지는 전체 공통 기준서를 임시 우선 기준으로 삼는다.
