---
doc_type: progress
created_at: "2026-10-13"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-10-13", accepted_by: main}
work_status: complete
work_ref: R027/clarify-question-recording
step_ref: R027/S02
key:
  id: key.work.clarify-question-recording.progress.implementation
  refs: [key.work.clarify-question-recording.order, key.standard.skill.clarify, key.standard.skill.author, key.standard.skill.reader]
---

# R027/S02 Clarify·Author 계약 반영

S01 수락 기준을 repository의 Clarify·Author·Reader 스킬에 반영했다. Main이 S02 결과를
검토·수락했으며 실제 사례 검증은 S03에서 수행한다.

## 변경과 검증

- Clarify: 기록 선택·최초 생성, 조건부 해석 확인, 질문별 저장 대기, 폐기·파생·답변 변경,
  필요한 경우만 읽는 복구를 자체 포함 계약으로 작성했다.
- Author: 질문 생성·확인 대기·확정·폐기를 같은 lightweight 기록 모드로 저장하고,
  전후 entry 확인·중복 전달·실패 재개·시각·그룹 원문 적용의 경계를 정리했다.
- Reader: 새 세션·진행 상태 조회마다 질답 로그를 읽지 않는 경계를 추가했다.
- 기존 group-application 검사에서 더 이상 유효하지 않은 기록 필드 문구 기대값 두 곳만 갱신했다.
  새 runtime·저장소·literal-only 회귀 테스트는 추가하지 않았다.
- 관련 계약 검사 26개 통과, 변경 test 파일 Python compile과 diff whitespace 검사 통과.
- 관련 기준·스킬·test 및 기존 provenance target을 포함한 bounded graph 검증 pass, errors 0/warnings 0.
  최초 최소 source 집합에서는 기존 provenance target 미포함으로 8개 missing-target 진단이 있었고
  해당 기존 결정·작업서 두 파일만 검증 입력에 추가해 해결했다. 원문 graph relation은 변경하지 않았다.
- Skill Creator quick_validate는 이 환경의 PyYAML 부재로 실행 불가했다. 새 dependency 설치 대신
  repository frontmatter parser로 세 스킬의 이름·설명·허용 필드·placeholder·fence 기본 형식을
  검증했다. 이는 해당 외부 validator를 실행했다고 주장하는 근거가 아니다.
- 전역 설치본은 변경하지 않았다.
