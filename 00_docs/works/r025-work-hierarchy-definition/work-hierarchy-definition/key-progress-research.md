---
doc_type: progress
created_at: "2026-10-12"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-10-12", accepted_by: main}
work_status: complete
work_ref: R025/work-hierarchy-definition
step_ref: R025/S01
key:
  id: key.work.work-hierarchy-definition.progress.research
  refs: [key.work.work-hierarchy-definition.order, key.standard.project]
---

# R025/S01 현행 계층과 용례 조사

## 범위와 근거

사용자의 R025 실행 요청에 따라 이전 대화의 Uptendo 예비 검토를 재사용하고 현재 source와
대조했다. Keystone 기준과 아래 Uptendo 대표 문서만 조사했으며 전체 corpus·구현 감사는 아니다.
Uptendo 경로는 `/Users/joung/workspace/uptendo` 기준이고 해당 프로젝트에는 쓰지 않았다.

| 근거 | 확인한 사실 | 의미와 한계 |
|---|---|---|
| `00_docs/works/r004-remaining-standards-enhancement/00_key-index.md` | Data·Security·Backoffice·Delivery·교차 검증을 다섯 Work로 분리하고 개별 완료·의존 경계를 둠 | 독립 과제 구분의 효용을 보여준다. R004는 cancelled 이력이며 성공·비용 절감의 증거는 아님 |
| 같은 R004의 `data-standard-enhancement/key-work-data-standard-enhancement.md`, `security-standard-enhancement/key-work-security-standard-enhancement.md` | 각 작업서가 자체 S01~S03을 사용 | 복수 Work의 Step을 Round ref만으로 표시하면 식별이 모호해질 수 있어 새 식별 규칙 검토가 필요함. 기존 ID를 재번호화하지 않음 |
| `00_docs/works/r012-cafe24-integration-state-distinction/00_key-index.md`와 해당 Work Order·Index | Round 하나와 같은 목표의 Work 하나가 S01~S06을 관리 | 독립 과제 구분보다 문서·진행 기록 묶음 역할이 큼 |
| `00_docs/works/r019-board-comment-management/00_key-index.md`, `r019-A/00_key-index.md`와 댓글 수집 Work Order·Progress | 부모 Round→하위 Round→단일 Work→Step 구성, 수집·작성의 독립 범위와 gate | 하위 Round와 Work의 기능 중첩을 보여줌. 생성 권한의 차이는 이번 사용자 방향으로 명확히 함 |
| `00_docs/works/key-decisions.md`, `D-R004-01` | 특정 기준서별 Work 구성안 승인 기록 | Work의 보편 정의를 사용자가 직접 정했다는 증거로 확대하지 않음 |

## 현행 단위 비교

| 단위 | 목적·결정/관리 책임 | 문서·상태 경계 | 이번 방향과의 차이 |
|---|---|---|---|
| Round | 특정 시점 목표의 작업 묶음. Main/User가 범위·수락 판단 | Round Index가 전역 또는 자식 local 상태·구성을 소유 | 부모·하위 Round 생성 결정은 사용자에게만 있음을 명시해야 함 |
| Work | 독립 과제 및 작업서·진행 기록 묶음. AI가 source를 구성·복구 | Work Index의 identity와 Aggregate Progress 상태를 결합 | 선택적 Work, AI 생성 후 안내 및 Work 없는 복구 경로를 공통 계약에 반영해야 함 |
| Step | Goal·Scope·완료 조건·검증이 있는 실행 단위. 사용자 지정 또는 실행자의 선택 | Work 내 계획, combined Progress 또는 개별 Step Progress | 필수 실행 단위 의미를 유지하되 Work 없는 소속과 복수 Work 식별을 명확히 해야 함 |
| Task | 외부 workflow의 세부 분해·실행 항목 용례가 있음 | 공통 관리 계층의 별도 상태·수락 계약은 확인되지 않음 | AI가 필요할 때 만드는 선택적 단위로 정의하되 저장·복구 수준은 사용자 결정이 남음 |

Keystone 근거는 프로젝트 기준의 표준 용어·STD-KEYSTONE-020~026/030~033/062,
Author의 Work/Step Progress ownership, Reader의 Round 선택·Step 복구 계약이다.
Coordinator 개발 기준서는 현재 `approval: pending`이므로 task decomposition과 실행 용례를
검토 자료로만 사용하며 accepted 정책 권위로 승격하지 않는다.

## 확정 방향과 남은 결정

1. 사용자 확정: Round·Step 기본 틀, 선택적 Work·Task, 부모·하위 Round의 사용자 생성 결정,
   AI의 Round 생성 권유, AI의 범위 내 Work 생성과 이유·범위·관계 사후 안내.
2. Work 생략 시 Round가 작업 목표·완료 조건을 직접 담는 방향이 자연스러운 후보이나,
   실제 파일·진행 기록 소유와 조회 계약은 아직 정합화되지 않았다.
3. Work 생성 후보 기준: 독립적인 결과·범위·완료 조건·의존성을 구분할 실익이 있을 때 사용.
   파일 수나 작업량만으로 생성하지 않는 방향을 S02에서 구체화한다.
4. Task의 독립 상태·식별·복구 및 완료가 Step 수락에 미치는 관계는 미정이다. 이를 먼저
   확인한 뒤 한 번의 일관된 기준 개정으로 적용한다.
5. Work·Step 식별, 파일 분리, 변경·종료 책임을 구체화해야 한다. 기존 수락 이력과 ID는
   이번 정의 변경으로 이동·재번호화하지 않는다.

## R024와 후속 구현 경계

수락된 `00_docs/standards/key-standard-managed-work-state.md`는 round/work/step만 관리하고
Task를 제외하며 R025 확정 전까지 기존 Work→Step 관계를 사용한다. 기존 corpus는 명시적
이전 전까지 legacy Progress 복구를 유지한다. 새 저장 mode의 수락을 corpus 이전으로 보지 않는다.

Work 없는 Step 소속·작업서 locator·전체 완료 조건, 복수 Work 식별, Reader/Coordinator의
실행 선택과 Author의 생성·종료 규칙이 후속 정합화 후보이다. 런타임·schema·skill source·test
변경 및 기존 corpus 이전은 현재 R025 범위 밖이며 이 기록은 구현 완료나 graph 영향 확정이 아니다.

## 검증·수락

대표 source의 목적·Step·완료·의존 관계와 비교표를 대조했다. Work의 독립 효용과 중첩,
확정 사용자 방향과 미정 계약, 기존 상태 소유와 새 저장 mode의 경계를 분리했다.
S01 Completion Criteria를 충족하므로 Main은 조사 결과를 수락한다. 이는 S02 정책 결정,
기준 개정 또는 R025 전체 완료·수락을 대신하지 않는다.
