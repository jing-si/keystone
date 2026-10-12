---
doc_type: work_round
created_at: "2026-10-12"
document_lifecycle: active
approval: {state: pending}
round_status: planned
key:
  id: key.work.round.r026-idea-notes.index
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.standard.project
    - key.work.idea-notes.order
---

# R026 아이디어 노트

현재 작업 밖의 아이디어를 필요했던 이유와 함께 가볍게 보관하고, 자연어로 다시 찾아
관리하는 `keystone-ideas` 스킬과 파일 기반 저장 계약을 설계·구현·검증한다.

## 계획

| 순서 | Step | 목적 |
|---|---|---|
| S01 | 기록·탐색 계약과 기준 정합화 | 저장 구조, 최소 기록, CRUD 경계와 검색 절차를 정의한다 |
| S02 | 아이디어 스킬 구현과 연결 | 독립 CRUD 스킬과 필요한 Reader·Author 연결을 구현한다 |
| S03 | 검색 품질·관리 비용 검증 | 표현 변형, 모호성, 분할과 규모별 비용을 확인한다 |

## 문서

- Work 색인: `idea-notes/00_key-index.md`
- 청사진·작업서: `idea-notes/key-work-idea-notes.md`
- 진행 기록: `idea-notes/key-progress.md`

현재는 청사진 생성만 승인된 `planned / pending` 계획이며 Active Step은 없다.
실행·스킬 생성·설치는 별도 명시적 실행 요청 이후에 진행한다.
