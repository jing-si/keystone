---
doc_type: work_round
created_at: "2026-10-13"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-10-13", accepted_by: user}
round_status: accepted
key:
  id: key.work.round.r027-clarify-question-recording.index
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.standard.project
    - key.work.clarify-question-recording.order
---

# R027 질답 기록과 질문 변경 규칙

Clarify의 질문별 즉시 저장, 필요한 경우에만 수행하는 의도 확인, 질문 폐기·추가와
파생 번호, 필요할 때만 기록을 읽는 복구 경계를 정의하고 관련 스킬 계약에 반영한다.

## 계획

| 순서 | Step | 목적 |
|---|---|---|
| S01 | 질답 기록 계약과 기준 정합화 | 합의한 규칙과 남은 세부 경계를 구현 가능한 기준으로 정리한다 |
| S02 | Clarify·Author 계약 반영 | 질문별 저장과 변경·복구 절차를 관련 스킬에 반영한다 |
| S03 | 중단·변경·재개 사례 검증 | 기준과 구현의 일치 및 중복 질문·불필요한 읽기 방지를 검증한다 |

## 문서

- Work 색인: `clarify-question-recording/00_key-index.md`
- 작업서: `clarify-question-recording/key-work-clarify-question-recording.md`
- 진행 기록: `clarify-question-recording/key-progress.md`

2026-10-13 사용자 구현 요청에 따라 S01~S03 구현·검증을 완료했다. Active Step은 없으며
같은 날 사용자가 결과를 수락하고 R027을 클로즈했다. 스킬 교체는 전체 작업 완료 후
별도로 진행하며 이 Round의 미완료 항목이나 종료 조건으로 남기지 않는다.
