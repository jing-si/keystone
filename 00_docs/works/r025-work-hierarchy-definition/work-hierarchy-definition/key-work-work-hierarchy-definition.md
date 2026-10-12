---
doc_type: work_order
created_at: "2026-10-12"
document_lifecycle: active
approval: {state: pending}
work_status: planned
key:
  id: key.work.work-hierarchy-definition.order
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.standard.project
    - key.standard.skill.author
    - key.work.unified-state-management.order
---

# 작업 계층 정의 작업서

## Goal

Round·Work·Step·Task를 어떤 목적으로 구분하고 누가 정의·선택·관리하는지 명확히 한다.
개념 계층과 물리적인 파일 분리, 사용자 작업 지정과 AI 내부 실행 계획을 구분하여
불필요한 단위나 관리 절차를 늘리지 않고 일관된 작업 모델을 만든다.

## 사용자 방향과 미정 경계

1. 현행 Round·Work·Step 계층이 존재한다. Work 개념을 제거하기로 결정하지 않았으며,
   그 역할과 필요성을 기존 용례에 근거해 명확히 한다.
2. Step은 반드시 작성한다. 기존 Goal·Scope·완료 조건·검증을 갖춘 실행 단계의 의미는
   크게 바꾸지 않는다. 사용자는 Step까지 작업 대상을 지정할 수 있다.
3. Task는 AI가 Step 수행에 필요할 때만 만든다. 필요 없으면 생략하며 구체적 작업 내용과
   순서는 AI가 정의한다. 사용자에게 Task 관리 책임이나 별도 지정 의무를 부과하지 않는다.
4. 사용자는 Round를 파일 단위로 나눌 수 있는 가장 큰 분류 단위로, Step을 반드시 별도
   파일로 나눌 필요가 없는 단위로 설명했다. Work의 파일 경계와 기존 child Round·Step 및
   개별 Progress 계약과의 관계는 조사 후 확정한다. 이 설명만으로 기존 파일을 합치지 않는다.
5. Task의 저장 여부·식별자·복구 수준·상태 및 Step 완료와의 관계는 미정이다.
   선택적 Task를 필수 문서·수락 절차로 확대하지 않는다.

## Scope

Include:

- 네 단위의 정의·목적·포함 관계·생성 기준과 필수·선택 여부
- 사용자와 AI의 지정·분해·수정 권한 및 상위 Goal·Scope를 보존하는 경계
- Work와 Work Order의 구분, 논리 단위와 파일·폴더·진행 기록의 관계
- 기존 Round 계층·Step 계약·작업 복구와 선택적 Task의 정합성
- 필요한 사용자 결정 후 프로젝트·관련 스킬 개발 기준서와 용어 설명 정합화
- R024가 참조할 정의와 별도 구현이 필요한 영향 후보 정리

Exclude:

- Work 제거, Step 선택 사항 전환 또는 모든 Step의 Task 생성 강제
- R024의 상태 저장 트리·상태 이전·관리 목록 제외 규칙 확정 및 구현
- 미승인 식별자 변경, 기존 Round·Step 재번호화, 이력·수락 의미 변경
- runtime·schema·skill source·test 구현, 설치·배포 및 기존 문서 전체의 일괄 이전

이 Round는 정의·기준 정합화 작업이다. 구현 변경이 필요하면 영향과 후속 범위를 제시하고
별도 실행 범위를 확정한다. R024의 전체 문서 소급 개편은 해당 Round에서 다룬다.

## Source Context

- `00_docs/standards/01_key-project-standard.md`: 용어, STD-KEYSTONE-020~026/030~033/062
- `00_docs/standards/skills/author/key-standard-author.md`: 작업서 구성과 Progress 소유권
- `00_docs/standards/skills/reader/key-standard-reader.md`: Round 선택과 Step 복구
- `00_docs/standards/skills/coordinator/key-standard-coordinator.md`: 실행 단위와 작업 분해
- `00_docs/works/00_key-index.md`: 현행 Round·Work 탐색 구조
- `00_docs/works/r024-unified-state-management/unified-state-management/key-work-unified-state-management.md`

## Step 계획

### R025/S01 — 현행 계층과 용례 조사

- **Goal:** 현행 단위의 정의와 실제 사용을 구분하고 모호한 경계를 찾는다.
- **Scope:** 관련 기준과 단일·복수 Work, Step, child Round 사례를 제한적으로 읽는다.
- **Source Context:** 위 Project·Author·Reader·Coordinator 기준과 대표 작업서.
- **Completion Criteria:** 단위별 목적·소유자·파일 경계·상태 소유를 비교하고 확정 사항과
  미정 사항을 구분한다. 사용자 정의 근거가 없는 기존 개념은 그 사실을 명시한다.
- **Stop Conditions:** 근거 없이 Work 제거 또는 상태 관리 구조를 확정해야 하는 경우.
- **Verification:** 각 설명을 원문 및 대표 사례와 대조한다.
- **Expected Output:** 현행 정의 비교와 필요한 결정 목록.

### R025/S02 — 정의 확정과 기준 정합화

- **Goal:** 네 단위의 역할과 사용자·AI 경계를 수락 가능한 계약으로 만든다.
- **Scope:** 실제 미정 결정을 한 번에 하나씩 확인하고 관련 기준의 정의·설명을 정합화한다.
- **Source Context:** S01 근거, 사용자 방향, 영향받는 기준서.
- **Completion Criteria:** 필수 Step·선택적 Task, Work의 역할, 파일 분리 기준 및 Task의
  생성·변경·생략·복구 경계가 명확하다. Task가 상위 범위를 임의 확장하지 못한다.
- **Stop Conditions:** 사용자 결정 미해결, 기존 수락 의미 변경 또는 구현 범위 확대가 필요하다.
- **Verification:** 선택·제외 대안과 근거를 확인하고 관련 기준 간 모순을 대조한다.
- **Expected Output:** 확정된 정의와 정합화된 기준, R024 참조 사항.

### R025/S03 — 정의 일관성 검증

- **Goal:** 정의가 실제 작업 구분과 복구에 적용 가능함을 확인한다.
- **Scope:** Task 없는 Step, 여러 Task를 쓰는 Step, 복수 Work의 Round 및 파일 분리 사례를 검토한다.
- **Source Context:** S02 정의와 기존 실행·수락·복구 계약.
- **Completion Criteria:** 사용자에게 Task 관리가 요구되지 않고 Step 필수성이 유지된다.
  기존 계약과의 충돌·후속 구현 필요성 및 R024 연계가 명시된다.
- **Stop Conditions:** 정의만으로 단위를 구분할 수 없거나 필수 관리 부담이 불필요하게 늘어난다.
- **Verification:** 사례별 생성·지정·변경·종료 책임과 문서 간 용어 일치를 검토한다.
- **Expected Output:** 정의 검증 결과와 필요한 후속 적용 범위.

## 순서와 생성·실행 경계

기본 순서는 S01 → S02 → S03이다. 현재 요청은 R025 작업서 생성이며 실행 승인이 아니다.
Round와 Work는 `planned / pending`, Active Step은 없음으로 둔다.
R025 생성 후 R024 질답을 재개한다. 두 Round 사이의 자동 실행·완료 gate는 만들지 않는다.
R024 논의 중 단위 정의가 필요한 부분은 R025의 미정 경계를 표시하고 확정된 것으로 가정하지 않는다.

## Round Completion Criteria

- [ ] 네 단위의 목적·포함 관계·필수성·책임이 정의돼 있다.
- [ ] Step의 기존 의미와 필수 작성, AI의 선택적 Task 사용이 보존된다.
- [ ] Work·Work Order와 논리 계층·물리 파일 구조가 구분된다.
- [ ] 관련 기준과 대표 사례의 일관성을 검증했다.
- [ ] R024 연계, 후속 구현 필요성과 남은 한계를 명시했다.
