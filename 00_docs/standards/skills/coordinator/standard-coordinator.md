# keystone-coordinator 기준서

## 목적

이 기준서는 `keystone-coordinator`의 상세 계약을 정의한다. `keystone-coordinator`는
main이 supervisor로 남아 있는 상태에서 작업서(4)의 Goal unit을 복구하고, 필요한 context를
준비하며, role 기반 subagent 작업, report, review, verification, acceptance flow를
조율한다.

## 적용 범위

1. `keystone-coordinator`의 trigger와 non-trigger condition
2. Current Step Brief와 Context Pack 구성
3. Role-based subagent routing
4. Worker handoff boundary와 reviewer focus 도출
5. Subagent report handling
6. Review, verification, repair, escalation, acceptance flow
7. 진행 상태와 report status update boundary
8. 파생 에이전트 문서(8) 생성 조건

## 적용하지 않는 범위

1. 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 기록 작성 자체
2. High-impact topic 질문 수집과 결정(6) 확정
3. Read-only project orientation 또는 document navigation만 수행하는 작업
4. Subagent가 전체 작업서(4)를 재해석하거나 scope를 확장하게 하기
5. Main acceptance 없이 진행 상태를 complete 또는 accepted로 표시하기
6. 명시적 필요 없이 persistent worker handoff나 reviewer brief 생성
7. Implementation, schema, auth/security, generated/codegen, shared architecture 변경을
   자동 worker task로 보내기
8. 외부 workflow를 automatic 또는 mandatory로 만들기

## 기준 관계

1. Parent 기준서: `../../00_project-standard.md`
2. 상위 규칙: `STD-KEYSTONE-001`, `STD-KEYSTONE-004`, `STD-KEYSTONE-005`,
   `STD-KEYSTONE-006`, `STD-KEYSTONE-007`, `STD-KEYSTONE-012`,
   `STD-KEYSTONE-013`, `STD-KEYSTONE-018`, `STD-KEYSTONE-020`,
   `STD-KEYSTONE-021`, `STD-KEYSTONE-022`, `STD-KEYSTONE-023`,
   `STD-KEYSTONE-030`
3. 관련 결정(6): `DEC-001`, `DEC-007`, `DEC-009`, `DEC-011`, `DEC-012`,
   `DEC-013`, `DEC-014`, `DEC-022`, `DEC-026`
4. 충돌 처리: 이 기준서와 parent 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의
   결정(6)을 받는다. 결정 전까지는 parent 기준서를 임시 우선 기준으로 삼는다.
5. 상세화 범위: 이 기준서는 `STD-KEYSTONE-030`의 Coordinator behavior를 구현 가능한
   수준으로 상세화한다.

## Skill identity

1. Skill name: `keystone-coordinator`
2. Primary role: Goal assignment, subagent routing, report handling, review, verification,
   acceptance coordination
3. Primary user: main agent
4. Output authority: Coordinator output은 main의 orchestration 판단을 돕는 runtime output이며
   원천 문서(2)를 대체하지 않는다.

## Trigger condition

`keystone-coordinator`는 다음 경우에 사용할 수 있다.

1. 작업서(4)의 current step을 Goal unit으로 실행해야 한다.
2. Main이 worker, explorer, reviewer, verifier 같은 role 기반 subagent에게 bounded Goal을
   배정해야 한다.
3. Current Step Brief, Context Pack, worker handoff boundary, reviewer focus를 구성해야 한다.
4. Subagent report를 받아 accept, repair, review, verify, escalate 중 다음 결정을 내려야
   한다.
5. 진행 상태와 report status를 분리해 기록해야 한다.
6. Verification을 기준서(3)에서 추출해 checklist로 만들고 필요하면 verifier Goal을 배정해야
   한다.
7. Worker 결과가 scope, acceptance criteria, existing user change와 충돌하는지 판단해야
   한다.

## Non-trigger condition

`keystone-coordinator`는 다음 경우에 사용하지 않는다.

1. 원천 문서(2)를 새로 작성하거나 수정하는 것이 주된 작업이다.
2. 사용자가 high-impact policy, scope, 문서 구조, 스킬 계약을 먼저 결정해야 한다.
3. 현재 요청과 관련된 기준서(3)와 작업서(4)를 read-only로 찾기만 하면 된다.
4. Current step, completion criteria, applicable standard를 복구할 수 없다.
5. Work unit이 subagent-sized Goal로 나뉘지 않았다.
6. 작업이 high-risk implementation인데 main/user decision 없이 worker에게 보낼 수 없다.
7. 민감한 정보, local-only path, private data가 포함될 수 있지만 policy가 불명확하다.

## Required input

Coordinator는 다음 input을 사용할 수 있어야 한다.

1. 사용자 요청 또는 main의 current task
2. 설정된 document root(1)
3. 관련 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 기록
4. Current step 또는 이를 복구하기 위한 work package state
5. Completion criteria와 verification expectation
6. Included, excluded, conditional work scope
7. Stop conditions와 escalation conditions
8. 현재 repository state와 Git worktree risk

Input이 부족하면 Coordinator는 subagent를 배정하지 않고 Reader, Author, Clarify 중 필요한
다음 작업을 제안하거나 main/user 결정(6)을 요청한다.

## Common workflow

Coordinator는 다음 순서를 따른다.

1. 설정된 document root(1)와 current work package를 확인한다.
2. 진행 기록(5)에서 current step과 workflow state를 복구한다.
3. 작업서(4)에서 Goal, Scope, Source Context, Completion Criteria, Stop Conditions,
   Verification, Expected Output을 추출한다.
4. 관련 기준서(3)에서 verification expectation과 forbidden change를 추출한다.
5. Work unit이 subagent-sized이고 scope가 bounded인지 판단한다.
6. Role을 선택하거나 main override를 반영한다.
7. Current Step Brief와 Context Pack을 만든다.
8. Worker handoff boundary 또는 reviewer focus를 구성한다.
9. Subagent report를 받은 뒤 actual state와 diff 또는 문서 output을 확인한다.
10. 필요하면 review 또는 verification Goal을 별도로 배정한다.
11. Report 결과를 accept, repair, verify, escalate, block 중 하나로 처리한다.
12. Main acceptance 조건이 충족된 경우에만 진행 기록(5)을 갱신한다.

## Runtime output contract

Coordinator는 상황에 따라 다음 runtime output을 만들 수 있다.

1. Current Step Brief
   - current step, Goal, completion criteria, applicable standards, excluded work,
     expected edit area, verification, known risks를 담는다.
2. Context Pack
   - worker나 reviewer가 읽어야 하는 관련 기준서(3), 작업서(4), 결정(6), scope,
     progress 발견사항을 담는다.
3. Worker handoff
   - primary scope, read scope, direct edit scope, conditional edit scope, escalation
     zone, forbidden changes를 담는다.
4. Reviewer brief
   - worker goal, completion criteria, changed files 또는 문서 output, known risks,
     verification result, reviewer focus를 담는다.
5. Verification checklist
   - 기준서-led verification expectation과 local verification note를 합쳐 만든다.

이 runtime output은 기본적으로 persistent 문서가 아니다. 명시적 필요가 있을 때만 파생
에이전트 문서(8)로 저장할 수 있다.

## Role routing contract

Coordinator는 role을 다음 기준으로 선택한다.

1. Explorer
   - read-only 조사, 기존 규칙 중복 확인, repository 조사, prototype 비교가 필요할 때
     사용한다.
2. Worker 또는 code modifier
   - edit scope가 명확하고 bounded implementation 또는 문서 수정이 가능한 경우에만
     사용한다.
3. Reviewer
   - worker output이 completion criteria, scope, risk, regression 가능성 측면에서 검토가
     필요할 때 사용한다.
4. Verifier
   - 기준서-led verification을 별도 Goal로 실행하거나 failure 원인을 분리해야 할 때
     사용한다.
5. Main 직접 처리
   - 작은 local 문서 수정, acceptance 판단, scope 변경 판단, high-risk decision이 필요한
     경우 사용한다.

Subagent는 자신에게 배정된 Goal 밖으로 scope를 넓히거나 추가 subagent를 생성하지 않는다.

## Report handling contract

Subagent report는 다음 status 중 하나로 해석한다.

1. `DONE`
   - 요청 범위가 완료되었다고 보고한다. Main은 실제 상태와 verification을 확인하기 전까지
     accepted로 처리하지 않는다.
2. `DONE_WITH_CONCERNS`
   - 완료되었지만 risk나 불확실성이 있다. Main은 review 또는 verification을 우선 검토한다.
3. `NEEDS_CONTEXT`
   - 필요한 문서, 기준, 파일, 결정(6)이 부족하다. Main은 Reader, Author, Clarify 또는 직접
     context 보강을 결정한다.
4. `NEEDS_SCOPE_CHANGE`
   - 승인된 scope를 넘어야 한다. Main은 사용자 또는 관련 기준서(3)/작업서(4) update 결정을
     먼저 받아야 한다.
5. `BLOCKED`
   - 외부 상태, missing dependency, 권한, 충돌 때문에 진행할 수 없다. Main은 unblock path나
     stop report를 결정한다.

## Review and verification flow

Review와 verification은 다음 순서를 따른다.

1. Worker output이 scope와 completion criteria 안에 있는지 확인한다.
2. Existing user change 또는 다른 agent change를 덮어쓸 risk가 있는지 확인한다.
3. 필요하면 reviewer Goal을 배정한다.
4. 기준서(3)에서 verification expectation을 추출한다.
5. 작업서(4)의 local verification note가 기준서-led verification을 약화하지 않는지 확인한다.
6. 필요하면 verifier Goal을 배정한다.
7. Verification failure가 있으면 repair 또는 escalation으로 처리한다.
8. Verification을 실행할 수 없으면 residual risk로 보고하고 acceptance 여부를 main이
   판단한다.

## Acceptance contract

Main acceptance는 다음 조건이 충족될 때만 가능하다.

1. Worker 또는 main output을 실제로 확인했다.
2. Completion criteria가 충족되었다.
3. Scope boundary와 forbidden change를 위반하지 않았다.
4. Reviewer review가 완료되었거나 명시적으로 skip되었다.
5. Verification을 실행했거나 실행하지 못한 이유와 residual risk가 보고되었다.
6. Unresolved `NEEDS_SCOPE_CHANGE`가 없다.
7. 진행 상태와 report status를 혼동하지 않았다.
8. 필요한 원천 문서(2) update가 있다면 승인된 범위 안에서 처리되었거나 별도 next action으로
   남겼다.

Acceptance 후에만 진행 기록(5)을 `accepted` 또는 해당 project의 완료 상태로 바꿀 수 있다.

## Progress update boundary

진행 기록(5)은 subagent workflow 상태를 복구하기 위해 다음 규칙으로 갱신한다.

1. Assignment를 만들면 필요한 경우 `assigned`를 기록할 수 있다.
2. Report를 받으면 필요한 경우 `reported`를 기록할 수 있다.
3. Review 중이면 `reviewing`, verification 중이면 `verifying`을 기록할 수 있다.
4. Main acceptance 전에는 `accepted`로 표시하지 않는다.
5. Worker `DONE`만으로 progress를 완료 처리하지 않는다.
6. 문서 작성/수정 작업 자체의 진행 기록(5)은 `keystone-author`의 Progress Update Mode가
   담당한다.
7. 단순 오탈자, 미세 표현 수정, 의미 변화 없는 formatting은 진행 기록(5)에 남기지 않는다.
8. Status semantics를 바꾸려면 Author 또는 Clarify를 통해 원천 문서(2) update 결정을 먼저
   받는다.

## Derived document policy

파생 에이전트 문서(8)는 기본 생성하지 않는다. 이미 존재하고 명확히 영향받는 경우에만
함께 업데이트한다. 새로 생성하는 경우는 다음처럼 명시적 필요가 있을 때로 제한한다.

1. 사용자가 명시적으로 persistent handoff나 reviewer brief를 요청한다.
2. 복잡한 handoff를 사람에게 먼저 검토받아야 한다.
3. 같은 step을 rerun해야 한다.
4. Audit record가 필요하다.

파생 에이전트 문서(8)가 원천 문서(2)와 충돌하면 원천 문서(2)가 우선한다.

## Stop condition

Coordinator는 다음 상황에서 중단하거나 main/user 결정(6)을 요청한다.

1. Current step, completion criteria, applicable standard를 복구할 수 없다.
2. Work unit이 subagent-sized Goal이 아니다.
3. Scope boundary, direct edit scope, forbidden change가 불명확하다.
4. High-risk implementation이 main/user decision 없이 필요하다.
5. Report가 승인된 scope나 acceptance criteria 변경을 요구한다.
6. Existing user change 또는 다른 agent change를 덮어쓸 risk가 있다.
7. Verification을 실행할 수 없고 failure 원인도 판단할 수 없다.
8. Progress state가 현재 session context와 충돌한다.
9. 민감한 정보, local-only path, private data를 worker context에 넣어야 할 수 있다.
10. Subagent가 전체 작업서(4)를 재해석하거나 추가 subagent를 생성해야만 진행할 수 있다.

## Verification

Coordinator 기준은 다음 방법으로 검증한다.

1. Coordinator contract만 보고 trigger와 non-trigger를 구분할 수 있어야 한다.
2. 작업서(4) step에서 Current Step Brief와 Context Pack을 만들 수 있어야 한다.
3. Scope를 worker handoff boundary로 변환할 수 있어야 한다.
4. Review points를 reviewer focus로 변환할 수 있어야 한다.
5. High-risk work가 자동 worker-routable로 취급되지 않아야 한다.
6. Progress update가 main acceptance와 worker report status를 혼동하지 않아야 한다.
7. 파생 에이전트 문서(8)는 기본 생성되지 않아야 한다.
8. Verification command:
   - `rg --files 00_docs`
   - Coordinator 관련 기준서를 읽어 link와 scope consistency 확인
   - `git diff --check`
