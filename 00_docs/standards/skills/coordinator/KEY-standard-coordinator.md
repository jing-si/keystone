---
doc_type: standard
key:
  id: key.standard.skill.coordinator
  refs:
    - key.role.coordinator
    - key.role.subagent
    - key.topic.work-execution
    - key.topic.verification
    - key.topic.acceptance
---

# keystone-coordinator 기준서

<!-- key: id=key.standard.skill.coordinator.purpose refs=key.role.coordinator key.role.subagent key.topic.work-execution key.topic.formal-workflow -->
## 목적

이 기준서는 `keystone-coordinator`의 상세 계약을 정의한다. `keystone-coordinator`는
main이 supervisor로 남아 있는 상태에서 작업서(4)의 Goal unit을 복구하고, 필요한 context를
준비하며, role 기반 subagent 작업, report, review, verification, acceptance가 이어지는
formal execution workflow를 조율한다. 코드 작업은 대표적인 실행 작업이지만, 문서 작업도
formal workflow가 필요하면 Coordinator가 조율할 수 있다.

<!-- key: id=key.standard.skill.coordinator.scope refs=key.role.coordinator key.role.subagent key.topic.verification key.topic.acceptance key.topic.formal-workflow -->
## 적용 범위

1. `keystone-coordinator`의 trigger와 non-trigger condition
2. Current Step Brief와 Context Pack 구성
3. Lane, role, authority 기반 subagent routing
4. Worker handoff boundary와 reviewer focus 도출
5. Subagent report handling
6. Review, verification, repair, escalation, acceptance flow
7. 진행 상태와 report status update boundary
8. 파생 에이전트 문서(8) 생성 조건

<!-- key: id=key.standard.skill.coordinator.out-of-scope refs=key.role.coordinator key.topic.skill-contract key.topic.external-assist -->
## 적용하지 않는 범위

1. 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 기록의 작성 기준과 수정 범위 설계 자체
2. High-impact topic 질문 수집과 결정(6) 확정
3. Read-only project orientation 또는 document navigation만 수행하는 작업
4. Subagent가 전체 작업서(4)를 재해석하거나 scope를 확장하게 하기
5. Main acceptance 없이 진행 상태를 complete 또는 accepted로 표시하기
6. 명시적 필요 없이 persistent worker handoff나 reviewer brief 생성
7. Implementation, schema, auth/security, generated/codegen, shared architecture 변경을
   main/user decision 없이 자동 worker task로 보내기
8. 외부 보조 스킬(12)을 automatic 또는 mandatory로 만들기

<!-- key: id=key.standard.skill.coordinator.standard-relations refs=key.role.coordinator key.doc.standard key.topic.skill-contract -->
## 기준 관계

1. Parent 기준서: `../../00_KEY-project-standard.md`
2. 상위 규칙: `STD-KEYSTONE-001`, `STD-KEYSTONE-006`, `STD-KEYSTONE-007`,
   `STD-KEYSTONE-015`, `STD-KEYSTONE-016`, `STD-KEYSTONE-020`,
   `STD-KEYSTONE-022`, `STD-KEYSTONE-023`, `STD-KEYSTONE-024`,
   `STD-KEYSTONE-025`, `STD-KEYSTONE-030`, `STD-KEYSTONE-031`,
   `STD-KEYSTONE-032`, `STD-KEYSTONE-033`, `STD-KEYSTONE-043`
3. 관련 결정(6): `00_docs/works/KEY-decisions.md`
4. 충돌 처리: 이 기준서와 parent 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의
   결정(6)을 받는다. 결정 전까지는 parent 기준서를 임시 우선 기준으로 삼는다.
5. 상세화 범위: 이 기준서는 `STD-KEYSTONE-043`의 Coordinator behavior를 구현 가능한
   수준으로 상세화한다.

<!-- key: id=key.standard.skill.coordinator.skill-identity refs=key.role.coordinator key.topic.skill-contract -->
## Skill identity

1. Skill name: `keystone-coordinator`
2. Primary role: Formal execution workflow, Goal assignment, subagent routing,
   report handling, review, verification, acceptance coordination
3. Primary user: main agent
4. Output authority: Coordinator output은 main의 orchestration 판단을 돕는 runtime output이며
   원천 문서(2)를 대체하지 않는다.

<!-- key: id=key.standard.skill.coordinator.trigger-condition refs=key.role.coordinator key.topic.work-execution key.role.subagent key.topic.author-edit-contract -->
## Trigger condition

`keystone-coordinator`는 다음 경우에 사용할 수 있다.

1. 작업서(4)의 current step을 Goal unit으로 실행해야 한다.
2. Main이 lane, role, authority가 분명한 bounded Goal을 subagent에게 배정해야 한다.
3. Current Step Brief, Context Pack, worker handoff boundary, reviewer focus를 구성해야 한다.
4. Subagent report를 받아 accept, repair, review, verify, escalate 중 다음 결정을 내려야
   한다.
5. 진행 상태와 report status를 분리해 기록해야 한다.
6. Verification을 기준서(3)에서 추출해 checklist로 만들고 필요하면 verifier Goal을 배정해야
   한다.
7. Worker 결과가 scope, acceptance criteria, existing user change와 충돌하는지 판단해야
   한다.
8. 문서 작업이라도 Author Edit Contract를 바탕으로 doc-writer, reviewer, verifier가 이어지는
   formal workflow가 필요하다.

<!-- key: id=key.standard.skill.coordinator.non-trigger-condition refs=key.role.coordinator key.topic.skill-contract -->
## Non-trigger condition

`keystone-coordinator`는 다음 경우에 사용하지 않는다.

1. 원천 문서(2)의 작성 기준, 수정 범위, 영향 문서 판단이 주된 작업이다.
2. 사용자가 high-impact policy, scope, 문서 구조, 스킬 계약을 먼저 결정해야 한다.
3. 현재 요청과 관련된 기준서(3)와 작업서(4)를 read-only로 찾기만 하면 된다.
4. Current step, completion criteria, applicable standard를 복구할 수 없다.
5. Work unit이 subagent-sized Goal로 나뉘지 않았다.
6. 작업이 high-risk implementation인데 main/user decision 없이 worker에게 보낼 수 없다.
7. 민감한 정보, local-only path, private data가 포함될 수 있지만 policy가 불명확하다.
8. 문서 작업인데 Author Edit Contract 또는 승인된 문서 수정 범위가 없다.

<!-- key: id=key.standard.skill.coordinator.required-input refs=key.role.coordinator key.topic.work-execution -->
## Required input

Coordinator는 다음 input을 사용할 수 있어야 한다.

1. 사용자 요청 또는 main의 current task
2. 설정된 document root(1)
3. 관련 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 기록
4. Current step 또는 이를 복구하기 위한 active work state
5. Completion criteria와 verification expectation
6. Included, excluded, conditional work scope
7. Stop conditions와 escalation conditions
8. 현재 repository state와 Git worktree risk
9. 문서 formal workflow인 경우 Author Edit Contract

Input이 부족하면 Coordinator는 subagent를 배정하지 않고 Reader, Author, Clarify 중 필요한
다음 작업을 제안하거나 main/user 결정(6)을 요청한다.

<!-- key: id=key.standard.skill.coordinator.common-workflow refs=key.role.coordinator key.topic.work-execution key.topic.verification key.topic.acceptance -->
## Common workflow

Coordinator는 다음 순서를 따른다.

1. 설정된 document root(1)와 current active work 문서를 확인한다.
2. 진행 기록(5)에서 current step과 workflow state를 복구한다.
3. 작업서(4)에서 Goal, Scope, Source Context, Completion Criteria, Stop Conditions,
   Verification, Expected Output을 추출한다.
4. 관련 기준서(3)에서 verification expectation과 forbidden change를 추출한다.
5. Current work나 관련 기준서에 키스톤 메타데이터(9)가 있으면 같은 `key.id`를 참조하는
   문서를 Context Pack 후보로 확인한다.
6. Work unit이 subagent-sized이고 scope가 bounded인지 판단한다.
7. Lane, role, authority를 선택하거나 main override를 반영한다.
8. Current Step Brief와 Context Pack을 만든다.
9. Worker handoff boundary 또는 reviewer focus를 구성한다.
10. Subagent report를 받은 뒤 actual state와 diff 또는 문서 output을 확인한다.
11. 필요하면 review 또는 verification Goal을 별도로 배정한다.
12. Report 결과를 accept, repair, verify, escalate, block 중 하나로 처리한다.
13. Main acceptance 조건이 충족된 경우에만 진행 기록(5)을 갱신한다.

<!-- key: id=key.standard.skill.coordinator.runtime-output-contract refs=key.role.coordinator key.contract.output key.topic.work-execution -->
## Runtime output contract

Coordinator는 상황에 따라 다음 runtime output을 만들 수 있다.

1. Current Step Brief
   - current step, Goal, completion criteria, applicable standards, excluded work,
     expected edit area, verification, known risks를 담는다.
2. Context Pack
   - worker나 reviewer가 읽어야 하는 관련 기준서(3), 작업서(4), 결정(6), scope,
     progress 발견사항, metadata 기반 관련 문서 후보를 담는다.
3. Worker handoff
   - lane, role, authority, primary scope, read scope, direct edit scope, conditional edit
     scope, escalation zone, forbidden changes를 담는다.
4. Reviewer brief
   - worker goal, completion criteria, changed files 또는 문서 output, known risks,
     verification result, 같은 `key.id`를 참조하는 문서와의 충돌 여부, reviewer focus를
     담는다.
5. Verification checklist
   - 기준서-led verification expectation과 local verification note를 합쳐 만든다.

이 runtime output은 기본적으로 persistent 문서가 아니다. 명시적 필요가 있을 때만 파생
에이전트 문서(8)로 저장할 수 있다.

<!-- key: id=key.standard.skill.coordinator.role-routing-contract refs=key.role.coordinator key.role.subagent key.topic.work-execution -->
## Role routing contract

Coordinator는 role을 다음 기준으로 선택한다.

1. Explorer
   - read-only 조사, 기존 규칙 중복 확인, repository 조사, prototype 비교가 필요할 때
     사용한다. Metadata 기반 관련 문서 탐색이 필요할 때도 사용할 수 있다.
2. Doc-writer
   - Author Edit Contract와 승인된 문서 수정 범위가 있고, bounded 문서 수정이 필요한 경우에만
     사용한다.
3. Code-worker
   - edit scope가 명확하고 bounded implementation이 가능한 경우에만 사용한다.
4. Reviewer
   - worker output이 completion criteria, scope, risk, regression 가능성 측면에서 검토가
     필요할 때 사용한다.
5. Verifier
   - 기준서-led verification을 별도 Goal로 실행하거나 failure 원인을 분리해야 할 때
     사용한다.
6. Main 직접 처리
   - 작은 local 문서 수정, acceptance 판단, scope 변경 판단, high-risk decision이 필요한
     경우 사용한다.

Subagent는 자신에게 배정된 Goal 밖으로 scope를 넓히거나 추가 subagent를 생성하지 않는다.

<!-- key: id=key.standard.skill.coordinator.report-handling-contract refs=key.role.coordinator key.topic.report key.role.subagent -->
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

<!-- key: id=key.standard.skill.coordinator.review-verification-flow refs=key.role.coordinator key.topic.verification key.topic.review -->
## Review and verification flow

Review와 verification은 다음 순서를 따른다.

1. Worker output이 scope와 completion criteria 안에 있는지 확인한다.
2. Existing user change 또는 다른 agent change를 덮어쓸 risk가 있는지 확인한다.
3. 같은 `key.id`를 참조하는 문서와의 충돌 여부를 reviewer focus 후보로 확인한다.
4. 필요하면 reviewer Goal을 배정한다.
5. 기준서(3)에서 verification expectation을 추출한다.
6. 작업서(4)의 local verification note가 기준서-led verification을 약화하지 않는지 확인한다.
7. 필요하면 verifier Goal을 배정한다.
8. Verification failure가 있으면 repair 또는 escalation으로 처리한다.
9. Verification을 실행할 수 없으면 residual risk로 보고하고 acceptance 여부를 main이
   판단한다.

<!-- key: id=key.standard.skill.coordinator.acceptance-contract refs=key.role.coordinator key.topic.acceptance key.topic.verification -->
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

<!-- key: id=key.standard.skill.coordinator.progress-update-boundary refs=key.role.coordinator key.topic.progress-update key.topic.acceptance -->
## Progress update boundary

진행 기록(5)은 subagent workflow 상태를 복구하기 위해 다음 규칙으로 갱신한다.

1. Assignment를 만들면 필요한 경우 `assigned`를 기록할 수 있다.
2. Report를 받으면 필요한 경우 `reported`를 기록할 수 있다.
3. Review 중이면 `reviewing`, verification 중이면 `verifying`을 기록할 수 있다.
4. Main acceptance 전에는 `accepted`로 표시하지 않는다.
5. Worker `DONE`만으로 progress를 완료 처리하지 않는다.
6. 문서 작성/수정의 기준과 반영 범위는 `keystone-author`가 담당한다. Formal workflow 상태를
   복구해야 하는 경우에만 Coordinator가 진행 상태 전이를 조율한다.
7. 단순 오탈자, 미세 표현 수정, 의미 변화 없는 formatting은 진행 기록(5)에 남기지 않는다.
8. Status semantics를 바꾸려면 Author 또는 Clarify를 통해 원천 문서(2) update 결정을 먼저
   받는다.

<!-- key: id=key.standard.skill.coordinator.derived-document-policy refs=key.role.coordinator key.doc.source key.topic.document-system -->
## Derived document policy

파생 에이전트 문서(8)는 기본 생성하지 않는다. 이미 존재하고 명확히 영향받는 경우에만
함께 업데이트한다. 새로 생성하는 경우는 다음처럼 명시적 필요가 있을 때로 제한한다.

1. 사용자가 명시적으로 persistent handoff나 reviewer brief를 요청한다.
2. 복잡한 handoff를 사람에게 먼저 검토받아야 한다.
3. 같은 step을 rerun해야 한다.
4. Audit record가 필요하다.

파생 에이전트 문서(8)가 원천 문서(2)와 충돌하면 원천 문서(2)가 우선한다.

<!-- key: id=key.standard.skill.coordinator.stop-condition refs=key.role.coordinator key.topic.skill-contract key.topic.work-execution -->
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
10. 문서 작업인데 Author Edit Contract 없이 무엇을 어떻게 쓸지 결정해야 한다.
11. Subagent가 전체 작업서(4)를 재해석하거나 추가 subagent를 생성해야만 진행할 수 있다.

<!-- key: id=key.standard.skill.coordinator.verification refs=key.role.coordinator key.topic.verification key.topic.acceptance -->
## Verification

Coordinator 기준은 다음 방법으로 검증한다.

1. Coordinator contract만 보고 trigger와 non-trigger를 구분할 수 있어야 한다.
2. 작업서(4) step에서 Current Step Brief와 Context Pack을 만들 수 있어야 한다.
3. Scope를 worker handoff boundary로 변환할 수 있어야 한다.
4. Review points를 reviewer focus로 변환할 수 있어야 한다.
5. High-risk work가 자동 worker-routable로 취급되지 않아야 한다.
6. Progress update가 main acceptance와 worker report status를 혼동하지 않아야 한다.
7. 문서 formal workflow는 Author Edit Contract 없이 시작되지 않아야 한다.
8. 파생 에이전트 문서(8)는 기본 생성되지 않아야 한다.
9. Metadata 기반 후보 문서를 Context Pack 후보와 reviewer focus 후보로 사용할 수 있어야
   한다.
10. Verification command:
   - `rg --files 00_docs`
   - Coordinator 관련 기준서를 읽어 link와 scope consistency 확인
   - `git diff --check`
