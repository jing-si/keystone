---
doc_type: standard_index
key:
  id: key.standard.skill.reader.index
  refs:
    - key.role.reader
    - key.topic.document-navigation
    - key.topic.work-preparation
    - key.doc.standard
---

# keystone-reader 기준서 색인

이 색인은 `keystone-reader` child 기준서로 이동하기 위한 기준이다.

<!-- key: id=key.standard.skill.reader.index.standards refs=key.role.reader key.topic.document-navigation key.topic.work-preparation key.doc.standard -->
## 기준서

1. `key-standard-reader.md`
   - `keystone-reader`의 목적, trigger/non-trigger, required input, mode별 workflow,
     context brief output contract, Linker handoff cue, stop condition, verification을
     정의한다.

<!-- key: id=key.standard.skill.reader.index.parent-standard refs=key.role.reader key.doc.standard key.topic.document-system -->
## 상위 기준서

1. `../../01_key-project-standard.md`
   - Keystone 공통 정책, 표준 용어, 문서 tree, source authority, context brief preparation
     중심의 Reader 책임을 정의한다.

<!-- key: id=key.standard.skill.reader.index.reading-rules refs=key.role.reader key.topic.document-navigation key.doc.standard -->
## 읽기 규칙

1. Reader 관련 작업을 준비할 때는 `../../01_key-project-standard.md`의 `STD-KEYSTONE-040`을
   먼저 확인한다.
2. Artifact impact/stale/gap 후보 해석이 필요하면 `../linker/00_key-index.md`를 읽는다.
3. Reader 구현 또는 상세 계약 검토가 필요하면 `key-standard-reader.md`를 읽는다.
4. Reader 기준서가 전체 공통 기준서와 충돌하면 충돌을 보고하고 사용자 또는 main의
   결정(6)을 받는다. 결정 전까지는 전체 공통 기준서를 임시 우선 기준으로 삼는다.
