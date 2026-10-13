---
doc_type: work_order
created_at: "2026-10-12"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-10-12", accepted_by: main}
work_status: complete
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
Round·Step을 기본 틀로 유지하고 Work·Task는 필요할 때 추가한다. Round는 사용자가
구획하고, Work는 그 범위 안에서 사용자 또는 AI가 구성하는 선택적 과제로 정의한다.

## 사용자 방향과 적용 경계

1. Round는 사용자가 명확히 인지하고 구획하는 작업 단위다. 부모·하위 Round 모두 생성
   결정권은 사용자에게 있다. AI는 새 Round가 필요하면 이유와 범위를 제시해 생성을
   권유하고 사용자 결정을 기다린다. 작업 분할 필요만으로 Round를 자동 생성하지 않는다.
2. Step은 반드시 작성한다. 기존 Goal·Scope·완료 조건·검증을 갖춘 실행 단계의 의미는
   크게 바꾸지 않는다. 사용자는 Step까지 작업 대상을 지정할 수 있다.
3. Work는 Round 안에서 과제를 구분할 필요가 있을 때만 만든다. 사용자가 의도적으로
   생성·지정할 수 있고, AI도 맡겨진 Round의 Goal·Scope 안에서 판단해 생성한 뒤 통보할 수
   있다. 사용자가 Round만 지정했다고 모든 Round에 Work를 자동으로 만들지는 않는다.
4. AI가 Work를 생성하면 적용한 분할 기준과 이유, 각 Work의 목표·담당 범위 및
   Round·Work·Step 관계를 사용자가 이해할 수 있게 보여준다. 의존성이 있으면 함께 설명한다.
   Work 생성은 상위 범위 확대, 별도 Round 생성 또는 미승인 실행의 허가가 아니다.
5. Round와 Work는 작업 크기만으로 구분하지 않는다. 사용자 결정으로 구획하는 Round와
   그 안에서 AI가 더 자유롭게 구성할 수 있는 Work의 생성 권한 차이를 핵심 경계로 삼는다.
6. Task는 AI가 Step 수행에 필요할 때만 만든다. 필요 없으면 생략하며 구체적 작업 내용과
   순서는 AI가 정의한다. 사용자에게 Task 관리 책임이나 별도 지정 의무를 부과하지 않는다.
   Work와 Task의 필요성은 별개로 판단하며 어느 하나의 생성이 다른 하나를 강제하지 않는다.
7. G01/Q02에서 Work는 기본적으로 Round 작업서 안에 구분하고 내용이 크거나 별도 관리가
   필요할 때만 파일을 분리하기로 확정했다. Step도 별도 파일을 강제하지 않는다. 논리 계층의
   정의 변경만으로 기존 파일을 합치거나 이동하지 않는다.
8. Work는 독립 결과·완료 조건·범위·의존성 구분의 실익이 있을 때 생성한다. Work가 없으면
   Round가 전체 목표·완료 조건과 Step 소속을 직접 보존한다. 새 Step 번호는 기존 Round
   단위 원칙을 유지해 local Round 안에서 중복하지 않으며 기존 ID·이력은 재번호화하지 않는다.
   Work 구성안의 과거 승인 기록을 사용자가 Work 개념 자체를 정의한 근거로 확대하지 않는다.
9. G01/Q01에서 Task는 재개에 필요한 내용만 Step 기록에 남기고 독립 상태·수락 절차를 두지
   않기로 확정했다. 필수 식별자·별도 파일·전수 기록을 추가하지 않으며 Task 완료 표시가
   Step 완료 조건·검증·수락을 대체하지 않는다.

이 방향은 Project STD-KEYSTONE-026과 관련 개발 기준에 반영했다. 기준의 목표 계약과 실제
runtime 지원은 구분하며 기존 저장 계약은 후속 구현·검증·명시적 전환까지 유지한다.

## Scope

Include:

- 네 단위의 정의·목적·포함 관계·생성 기준과 필수·선택 여부
- 사용자와 AI의 지정·분해·수정 권한 및 상위 Goal·Scope를 보존하는 경계
- 사용자 결정에 따른 Round 생성·권유와 AI의 Work 생성 후 이유·관계 안내 계약
- Work 없는 Round·Step 구조와 선택적 Work의 생성 기준·상태 소유·복구 경계
- Work와 Work Order의 구분, 논리 단위와 파일·폴더·진행 기록의 관계
- 기존 Round 계층·Step 계약·작업 복구와 선택적 Task의 정합성
- 필요한 사용자 결정 후 프로젝트·관련 스킬 개발 기준서와 용어 설명 정합화
- R024가 참조할 정의와 별도 구현이 필요한 영향 후보 정리

Exclude:

- Work 개념의 전면 제거, 모든 Round의 Work 생성 강제, Step 선택 사항 전환 또는
  모든 Step의 Task 생성 강제
- 사용자 결정 없는 부모·하위 Round 생성 또는 Work 분할을 통한 상위 범위 확대
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
- `00_docs/standards/key-standard-managed-work-state.md`: R024 저장 계약과 후속 전환 경계

용례 조사 대상은 사용자 지정 프로젝트 `/Users/joung/workspace/uptendo`다. 해당 프로젝트는
읽기 전용 사례 근거이며 R025의 수정·실행 위치를 옮기는 Worktree locator가 아니다.

- `00_docs/works/r004-remaining-standards-enhancement/00_key-index.md`: 복수 Work와 독립 완료 조건
- `00_docs/works/r012-cafe24-integration-state-distinction/00_key-index.md`: Round와 단일 Work의 역할 중첩
- `00_docs/works/r019-board-comment-management/00_key-index.md`: 하위 Round·Work·Step 구성
- `00_docs/works/key-decisions.md`의 `D-R004-01`: 특정 Work 구성안 승인과 개념 정의의 구분

위 네 경로는 Uptendo root 기준이다. 당시 용례와 결정의 근거로 읽으며 현재 기준으로
소급 승인하거나 Uptendo 문서를 이번 Round에서 수정하지 않는다.

## Step 계획

### R025/S01 — 현행 계층과 용례 조사

- **Goal:** 현행 단위의 정의와 실제 사용을 구분하고 모호한 경계를 찾는다.
- **Scope:** Keystone의 현행 기준과 Uptendo의 단일·복수 Work, Step, child Round 사례를
  제한적으로 읽고 위 사용자 방향과의 차이를 비교한다.
- **Source Context:** 위 Project·Author·Reader·Coordinator 기준과 대표 작업서.
- **Completion Criteria:** 단위별 목적·소유자·파일 경계·상태 소유를 비교하고 확정 사항과
  미정 사항을 구분한다. Work의 독립 효용과 Round·하위 Round와의 중첩을 구분하고,
  특정 구성안 승인과 Work 개념 정의를 혼동하지 않는다. Work 생략 시 계약 공백을 식별한다.
- **Stop Conditions:** 근거 없이 Work 제거 또는 상태 관리 구조를 확정해야 하는 경우.
- **Verification:** 각 설명을 원문 및 대표 사례와 대조한다.
- **Expected Output:** 현행 정의 비교와 필요한 결정 목록.

### R025/S02 — 정의 확정과 기준 정합화

- **Goal:** 네 단위의 역할과 사용자·AI 경계를 수락 가능한 계약으로 만든다.
- **Scope:** 실제 미정 결정을 한 번에 하나씩 확인하고 관련 기준의 정의·설명을 정합화한다.
- **Source Context:** S01 근거, 사용자 방향, 영향받는 기준서.
- **Completion Criteria:** Round·Step 기본 틀, 선택적 Work·Task와 사용자·AI 생성 권한이
  명확하다. 부모·하위 Round는 사용자 결정 후 생성하고 AI의 Work 생성에는 사후 이유·범위·관계
  안내가 따른다. Work 생성 판단 기준·생략 시 책임, 파일 분리 및 Task의 생성·변경·생략·복구
  경계가 명확하다. Work·Task가 상위 범위를 임의 확장하지 못한다.
- **Stop Conditions:** 사용자 결정 미해결, 기존 수락 의미 변경 또는 구현 범위 확대가 필요하다.
- **Verification:** 선택·제외 대안과 근거를 확인하고 관련 기준 간 모순을 대조한다.
- **Expected Output:** 확정된 정의와 정합화된 기준, R024 참조 사항.

### R025/S03 — 정의 일관성 검증

- **Goal:** 정의가 실제 작업 구분과 복구에 적용 가능함을 확인한다.
- **Scope:** Work 없는 Round, 사용자 지정 Work, AI 생성 Work의 사후 안내, 새 Round 권유와
  사용자 결정 대기, Task 없는 Step, 여러 Task를 쓰는 Step 및 파일 분리 사례를 검토한다.
- **Source Context:** S02 정의와 기존 실행·수락·복구 계약.
- **Completion Criteria:** 사용자에게 Task 관리가 요구되지 않고 Step 필수성이 유지된다.
  Work·Task를 불필요하게 강제하지 않고 Round 생성 권한과 Work 생성 안내가 지켜진다.
  기존 계약과의 충돌·후속 구현 필요성 및 R024 연계가 명시된다.
- **Stop Conditions:** 정의만으로 단위를 구분할 수 없거나 필수 관리 부담이 불필요하게 늘어난다.
- **Verification:** 사례별 생성·지정·변경·종료 책임과 문서 간 용어 일치를 검토한다.
- **Expected Output:** 정의 검증 결과와 필요한 후속 적용 범위.

## 순서와 생성·실행 경계

기본 순서는 S01 → S02 → S03이다. 작업서 개정 당시에는 `planned / pending`, Active Step
없음을 유지했다. 이후 2026-10-12 사용자가 실행 시작을 명시하고 추가 결정이 필요하면
멈추고 의견을 묻도록 요청했다. 두 질답을 거쳐 S01~S03의 조사·정의·기준 정합화·사례 검증을
완료했으며 Main이 이 범위를 수락했다. 현재 Work는 `complete / accepted`, active_steps는
`[]`다. 상세 증거와 후속 구현 범위는 Progress에서 복구한다.
실행 승인은 이 작업서의 정의·기준 정합화 범위이며 runtime·schema·skill source·test 구현은
계속 제외한다. 질답은 `clarify/20261012T091957Z-work-hierarchy-definition.md`에 기록한다.
생성 당시에는 R024 질답 복귀를 예정했으며 현재는 R025 방향을 논의해 이 작업서를 개정한다.
두 Round 사이의 자동 실행·완료 gate는 만들지 않는다. R024는 수락된 방향과 남은 미정 경계를
구분해 참조하며 상태 저장·이전 계약과 R025 정의의 적용을 별도 범위로 정합화한다.

## Round Completion Criteria

- [x] 네 단위의 목적·포함 관계·필수성·책임이 정의돼 있다.
- [x] 부모·하위 Round 생성은 사용자 결정이며 AI는 필요 시 권유하고 결정을 기다린다.
- [x] Work는 사용자 또는 AI가 선택적으로 구성하고 AI 생성 시 이유·범위·관계를 안내한다.
- [x] Work 없는 구조와 Work가 있는 구조 모두 목표·완료 조건·상태·복구 책임이 명확하다.
- [x] Step의 기존 의미와 필수 작성, AI의 선택적 Task 사용이 보존된다.
- [x] Work·Work Order와 논리 계층·물리 파일 구조가 구분된다.
- [x] 관련 기준과 대표 사례의 일관성을 검증했다.
- [x] R024 연계, 후속 구현 필요성과 남은 한계를 명시했다.

완료 근거: `key-progress-research.md`, `key-progress-definition.md`, `key-progress-verification.md`.
새 구조의 runtime 지원·기존 문서 전환 완료는 위 문서 계약의 완료 조건에 포함하지 않는다.
