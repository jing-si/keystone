---
doc_type: progress
created_at: "2026-10-13"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-10-13", accepted_by: main}
work_status: complete
work_ref: R027/clarify-question-recording
step_ref: R027/S01
key:
  id: key.work.clarify-question-recording.progress.contract
  refs: [key.work.clarify-question-recording.order, key.standard.project.std-keystone-060, key.standard.skill.clarify.question-recording, key.standard.skill.author.clarification-log-application]
---

# R027/S01 질답 기록 계약과 기준 정합화

## 원인과 변경 의미

기존 규칙은 질문별 handoff를 요구했지만 실제 저장 완료 전 다음 질문 진행을 명시적으로 막지
않았다. 질문 번호는 출현 순서만 지원했고 모든 상태 표현을 금지해 확인 대기와 폐기 질문의
기록·복구가 불명확했다. 사용자 합의를 아래 조항에 반영하고 Main이 구현 기준으로 수락했다.

- Project STD-KEYSTONE-060: 최초 생성, 매 답변 저장 확인, 최소 기록 표시, 파생 번호와 필요 시 읽기.
- Clarify question-contract/question-recording: 명확한 답변 즉시 확정, 해석만 확인, 폐기·추가·범위 경계.
- Author clarification-log-application: 실제 쓰기·재읽기·실패 재개·중복 방지와 그룹 원문 적용 분리.
- Reader Work Prep: 새 세션·일반 상태 조회의 로그 일괄 읽기 금지, 필요한 의미 복구만 수행.

## 세부 구현 기준

- 답변 안의 `[확인 대기]`, `[폐기]`로 구분하며 별도 workflow 상태 필드를 늘리지 않는다.
- Round 작명과 같은 한 단계 대문자 suffix를 기본으로 적용한다. 재파생은 같은 기본 질문 아래
  다음 suffix와 직접 원인 링크로 표현해 번호 깊이를 늘리지 않는다. 그룹이 다르면 링크로 연결한다.
- 기록이 중요한데 작업서·승인된 위치가 없으면 caller에 위치·권한 미해결을 반환한다.
  임의 경로·Work 자동 생성 또는 중요 질답의 무기록 우회를 도입하지 않는다.
- 기록 없는 대화가 중요해지면 필요한 이전 맥락만 보존한다. 과거 시각을 모르면 미상으로 둔다.
- 확인 대기 저장 후 확인 질문, 실패 시 다음 질문 중단, 같은 entry 재시도로 유실·중복을 줄인다.
  모델 응답 생성 전 갑작스러운 종료나 원자적 다중 writer 잠금까지 보장하는 runtime은 추가하지 않는다.

## 검증과 구현 재개

- 관련 네 기준서의 affected-source graph 검증이 pass했고 `git diff --check`가 통과했다.
- 명확한 답변과 해석 확인, 변경·파생·번복, 기록 생략과 필요 시 읽기의 기준 의미를 대조했다.
- 기존 한 번에 한 질문, source-owner 쓰기, 그룹별 원문 적용과 로그의 비권위성은 유지한다.
- S01 기준을 S02의 Clarify·Author·Reader 스킬 반영과 S03 사례 검증 기준으로 사용한다.
