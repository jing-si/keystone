---
doc_type: progress
created_at: "2026-10-12"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-10-12", accepted_by: main}
work_status: complete
work_ref: R025/work-hierarchy-definition
key:
  id: key.work.work-hierarchy-definition.progress
  refs:
    - key.topic.progress-update
    - key.topic.work-recovery
    - key.work.work-hierarchy-definition.order
---

# 작업 계층 정의 진행 기록

## 현재 상태

- active_steps: []
- Planned Steps: []
- Accepted Steps: [`R025/S01`, `R025/S02`, `R025/S03`]
- Execution location: current worktree
- Resume point: R025의 정의·기준 정합화는 완료했다. runtime·skill source·저장 wire 및
  기존 corpus 적용이 필요하면 S03의 후속 범위를 바탕으로 사용자 실행 범위를 확정한다.

Step별 상태·근거:

- [S01 조사 결과](key-progress-research.md): complete / accepted
- [S02 정의 정합화](key-progress-definition.md): complete / accepted
- [S03 일관성 검증](key-progress-verification.md): complete / accepted

## 생성 근거와 경계

- 2026-10-12: R024 질답 중 사용자는 Round·Work·Step·Task 정의를 명확히 하는 R025
  작업서 생성을 요청했다. Step은 필수, Task는 AI가 필요할 때만 만드는 방향을 보존한다.
- Work 제거는 결정하지 않았다. 개념별 정의와 파일 경계, Task 기록·복구 방식은 후속 과제다.
- 이번에는 계획 문서만 생성한다. R025 실행·기준 개정·구현·수락은 수행하지 않았다.
- 생성 후 원래 R024 상태 통합 관리 질답으로 돌아간다.

## 2026-10-12 작업서 방향 개정

- 사용자가 지정한 Uptendo의 R004·R012·R019 사례를 읽기 전용으로 예비 검토했다.
  복수 독립 과제를 묶는 Work와 단일 Round·하위 Round의 목표가 겹치는 Work 용례를 확인했다.
  `D-R004-01`의 특정 구성안 승인 기록을 Work 개념 자체의 사용자 정의로 간주하지 않는다.
- 사용자는 Round·Step 기본 틀과 선택적 Work·Task 방향을 정하고 작업서 수정을 요청했다.
- 부모·하위 Round 생성은 항상 사용자 결정이다. AI는 필요 시 권유하고 결정을 기다린다.
- Work는 사용자가 지정하거나 AI가 기존 Round 범위 안에서 판단해 생성한 뒤 통보할 수 있다.
  AI는 생성 기준·이유·담당 범위와 Round·Work·Step 관계를 보여준다.
- Work 생성 판단의 상세 기준, Work 생략 시 상태·복구 책임, 파일·식별자 및 Task 기록·복구
  계약은 후속 정합화 대상으로 유지한다.
- 작업서의 Goal·Scope·Step 완료 조건·검증 사례와 Round 색인을 정합화했다.
  이번 개정은 Step 완료·수락, 공통 기준 변경 또는 구현 적용이 아니며
  `planned / pending`, Active Step 없음과 Accepted Steps 빈 목록을 유지한다.

## 2026-10-12 실행 착수와 S01 수락

- 사용자가 구현 시작을 명시하고 추가 결정이 필요하면 멈추고 의견을 묻도록 요청했다.
  실행 범위는 현재 작업서의 정의·기준 정합화이며 runtime·skill source 구현은 제외한다.
- S01은 Uptendo 예비 검토와 현행 계약을 대조하고 단위별 책임·상태·파일 경계, Work 효용과
  중첩 및 미정 정책을 정리해 Main이 수락했다. 개별 Step 기록에 근거를 보존한다.
- S02를 활성화하고 Task의 기록·복구 수준을 사용자 결정 항목으로 분리했다.
  관련 기준 적용은 답변 전까지 보류한다. S03과 R025 전체 수락은 미완료다.

## 2026-10-12 정의·기준 정합화 완료

- G01/Q01에서 Task의 Step 내 최소 기록, G01/Q02에서 Work의 기본 inline 구성과 필요 시
  파일 분리를 사용자가 선택했다. `DEC-WORKS-035`와 관련 기준에 반영했다.
- Project·Author·Reader 및 Coordinator 개발 명세의 생성·분해·복구 경계를 정합화하고
  R024 저장 계약에는 정의와 실제 구현 전환을 구분했다. Coordinator 전체 pending은 유지한다.
- S03의 10개 사례 대조와 형식·Work State 검증으로 완료 조건을 확인해 Main이 S01~S03 및
  R025의 정의·기준 정합화 범위를 수락한다. R015와 다른 Round의 상태·범위는 변경하지 않는다.
- runtime·schema·skill source 구현, 설치·배포, Uptendo 수정과 기존 corpus 일괄 이전은
  수행하지 않았다. 새 문서 형식의 자동 생성·복구는 후속 구현·검증이 필요한 잔여 적용 범위다.
