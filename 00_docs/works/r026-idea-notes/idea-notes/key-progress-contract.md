---
doc_type: progress
created_at: "2026-10-12"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-10-12", accepted_by: main}
work_status: complete
work_ref: R026/idea-notes
step_ref: R026/S01
key:
  id: key.work.idea-notes.progress.contract
  refs: [key.work.idea-notes.order, key.standard.skill.ideas]
---

# R026/S01 기록·탐색 계약과 기준 정합화

사용자가 합의한 CRUD·표·기록일·300자 권장·실제 삭제·현재 최대 번호+1을
Project STD-KEYSTONE-064와 Ideas 기준에 반영했다. Author 직접 쓰기의 제한적 예외와
Reader의 선택 작업 read-only 탐색을 정합화한 뒤 Main이 이 범위를 수락했다.

기술 선택: 별도 frontmatter/키메타 없는 노트, 단일 파일과 선택적 flat 주제 파일,
읽기 전용 helper와 직접 좁은 편집, 원자적 다중 writer 보장 없음, 삭제 후 ID 재사용에
대비한 제목·날짜·맥락 참조. 새 사용자 정책 결정은 발생하지 않았다.

기준 정합화를 production skill/helper 작성 전에 수행했다. 검증 기대값은 S03에 기록한다.
