---
doc_type: work_round
created_at: "2026-10-12"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-10-12", accepted_by: main}
round_status: accepted
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

2026-10-12 명시적 구현 요청에 따라 S01~S03을 완료·수락했다. Active Step은 없다.
전역 설치·publish는 실행 범위에 포함하지 않는다.
