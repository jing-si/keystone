---
doc_type: standard
key:
  id: key.standard.skill.coordinator
  refs:
    - key.role.coordinator
    - key.role.subagent
    - key.standard.subagent
    - key.topic.work-execution
    - key.topic.work-round
    - key.topic.branch-worktree
    - key.topic.merge-gate
    - key.topic.remote-policy
    - key.topic.commit-checkpoint
    - key.topic.merge-authorization
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

<!-- key: id=key.standard.skill.coordinator.scope refs=key.role.coordinator key.role.subagent key.standard.subagent key.topic.verification key.topic.acceptance key.topic.formal-workflow -->
## 적용 범위

1. `keystone-coordinator`의 trigger와 non-trigger condition
2. Current Step Brief와 Context Pack 구성
3. Subagent 기준서의 lane, role, authority 기반 routing
4. Worker handoff boundary와 reviewer focus 도출
5. Subagent report handling
6. Review, verification, repair, escalation, acceptance flow
7. Branch/worktree isolation과 merge gate
8. 진행 상태와 report status update boundary
9. 파생 에이전트 문서(8) 생성 조건

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

<!-- key: id=key.standard.skill.coordinator.standard-relations refs=key.role.coordinator key.doc.standard key.topic.skill-contract key.standard.subagent key.topic.work-round -->
## 기준 관계

1. Parent 기준서: `../../01_key-project-standard.md`
2. 상위 규칙: `STD-KEYSTONE-001`, `STD-KEYSTONE-006`, `STD-KEYSTONE-007`,
   `STD-KEYSTONE-015`, `STD-KEYSTONE-016`, `STD-KEYSTONE-020`,
   `STD-KEYSTONE-022`, `STD-KEYSTONE-023`, `STD-KEYSTONE-024`,
   `STD-KEYSTONE-025`, `STD-KEYSTONE-026`, `STD-KEYSTONE-030`, `STD-KEYSTONE-031`,
   `STD-KEYSTONE-032`, `STD-KEYSTONE-033`, `STD-KEYSTONE-034`,
   `STD-KEYSTONE-043`
3. 관련 기준서: `../../subagents/key-standard-subagents.md`
4. 관련 결정(6): `00_docs/works/key-decisions.md`
5. 충돌 처리: 이 기준서와 parent 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의
   결정(6)을 받는다. 결정 전까지는 parent 기준서를 임시 우선 기준으로 삼는다.
6. 상세화 범위: 이 기준서는 `STD-KEYSTONE-043`의 Coordinator behavior를 구현 가능한
   수준으로 상세화한다.

<!-- key: id=key.standard.skill.coordinator.skill-identity refs=key.role.coordinator key.topic.skill-contract -->
## Skill identity

1. Skill name: `keystone-coordinator`
2. Primary role: Formal execution workflow, Goal assignment, subagent routing,
   report handling, review, verification, acceptance coordination
3. Primary user: main agent
4. Output authority: Coordinator output은 main의 orchestration 판단을 돕는 runtime output이며
   원천 문서(2)를 대체하지 않는다.

<!-- key: id=key.standard.skill.coordinator.trigger-condition refs=key.role.coordinator key.topic.work-execution key.role.subagent key.standard.subagent key.topic.author-edit-contract -->
## Trigger condition

`keystone-coordinator`는 다음 경우에 사용할 수 있다.

1. 작업서(4)의 current step을 Goal unit으로 실행해야 한다.
2. Main이 subagent 기준서에 따른 lane, role, authority가 분명한 bounded Goal을 subagent에게
   배정해야 한다.
3. Current Step Brief, Context Pack, worker handoff boundary, reviewer focus를 구성해야 한다.
4. Subagent report를 받아 accept, repair, review, verify, escalate 중 다음 결정을 내려야
   한다.
5. 진행 상태와 report status를 분리해 기록해야 한다.
6. Verification을 기준서(3)에서 추출해 checklist로 만들고 필요하면 verifier Goal을 배정해야
   한다.
7. Worker 결과가 scope, acceptance criteria, existing user change와 충돌하는지 판단해야
   한다.
8. 문서 작업이라도 Author Edit Contract를 바탕으로 doc-impact-writer, reviewer, verifier가
   이어지는 formal workflow가 필요하다.
9. Subagent 작업이 파일 수정으로 이어져 branch context, worktree isolation, merge gate가
   필요하다.
10. 여러 main-session branch를 합치거나, 여러 task branch 사이에 file/key/verification overlap이
    있어 repo-integrator 검토가 필요하다.

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

<!-- key: id=key.standard.skill.coordinator.required-input refs=key.role.coordinator key.topic.work-execution key.topic.branch-worktree key.topic.merge-gate -->
## Required input

Coordinator는 다음 input을 사용할 수 있어야 한다.

1. 사용자 요청 또는 main의 current task
2. 설정된 document root(1)
3. 관련 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 기록
4. Current step 또는 이를 복구하기 위한 active round와 active work state
5. Completion criteria와 verification expectation
6. Included, excluded, conditional work scope
7. Stop conditions와 escalation conditions
8. 현재 repository state와 Git worktree risk
9. 문서 formal workflow인 경우 Author Edit Contract
10. 파일 수정 또는 merge가 필요한 경우 branch context
11. Integration branch가 관련된 경우 `integration_owner_id`

Input이 부족하면 Coordinator는 subagent를 배정하지 않고 Reader, Author, Clarify 중 필요한
다음 작업을 제안하거나 main/user 결정(6)을 요청한다.

<!-- key: id=key.standard.skill.coordinator.common-workflow refs=key.role.coordinator key.topic.work-execution key.topic.verification key.topic.acceptance key.standard.subagent key.topic.branch-worktree key.topic.merge-gate -->
## Common workflow

Coordinator는 다음 순서를 따른다.

1. 설정된 document root(1)와 root works index를 확인한다.
2. Active round index와 active work node index를 따라 `round_id`, `work_id`, `current_step`과
   workflow state를 복구한다.
3. 작업서(4)에서 Goal, Scope, Source Context, Completion Criteria, Stop Conditions,
   Verification, Expected Output을 추출한다.
4. 관련 기준서(3)에서 verification expectation과 forbidden change를 추출한다.
5. Current work나 관련 기준서에 키스톤 메타데이터(9)가 있으면 같은 `key.id`를 참조하는
   문서를 Context Pack 후보로 확인한다.
6. Work unit이 subagent-sized이고 scope가 bounded인지 판단한다.
7. Subagent 기준서에 따라 lane, role, authority를 선택하거나 main override를 반영한다.
8. 파일 수정이 필요하면 branch context와 worktree risk를 확인한다.
   Branch/worktree provisioning이 필요하면 Main 또는 Coordinator가 task branch와 isolated
   worktree를 준비하고, worker는 준비된 worktree 안에서만 작업하게 한다.
9. Current Step Brief와 Context Pack을 만든다.
10. Worker handoff boundary 또는 reviewer focus를 구성한다.
11. Subagent report를 받은 뒤 actual state와 diff 또는 문서 output을 확인한다.
12. 필요하면 review, verification, repo-integrator Goal을 별도로 배정한다.
13. Report 결과를 accept, repair, verify, escalate, block 중 하나로 처리한다.
14. Merge가 포함되면 merge authorization과 final acceptance를 분리한다.
15. Main acceptance 조건이 충족된 경우에만 진행 기록(5)을 갱신한다.

<!-- key: id=key.standard.skill.coordinator.runtime-output-contract refs=key.role.coordinator key.contract.output key.topic.work-execution key.topic.work-round key.standard.subagent key.topic.branch-worktree key.topic.merge-gate key.topic.remote-policy key.topic.commit-checkpoint -->
## Runtime output contract

Coordinator는 상황에 따라 다음 runtime output을 만들 수 있다.

1. Current Step Brief
   - `round_id`, `work_id`, `step_id`, current step, Goal, completion criteria, applicable standards, excluded work,
     expected edit area, verification, known risks를 담는다.
2. Context Pack
   - worker나 reviewer가 읽어야 하는 관련 기준서(3), 작업서(4), 결정(6), scope,
     progress 발견사항, metadata 기반 관련 문서 후보를 담는다.
3. Branch context
   - `round_id`, `work_id`, `step_id`, `session_id`, `integration_owner_id`, `task_id`,
     base branch, integration branch, session branch, task branch 또는 staging branch,
     worktree path, merge target, forbidden merge targets, base commit,
     `session_head_at_assignment`, `merge_target_head_at_review`, `merge_base`, dirty
     worktree 허용 여부, remote policy, push 허용 여부, commit requirement, 필요한 경우 task
     commit range를 담는다.
4. Worker handoff
   - subagent 기준서 기준의 lane, role, authority, primary scope, read scope,
     direct edit scope, conditional edit scope, escalation zone, forbidden changes,
     branch, worktree path, merge target, forbidden merge targets, remote policy,
     commit checkpoint requirement, 임의 branch/worktree 생성 또는 전환 금지를 담는다.
5. Reviewer brief
   - worker goal, completion criteria, changed files 또는 문서 output, known risks,
     verification result, 같은 `key.id`를 참조하는 문서와의 충돌 여부, reviewer focus를
     담는다.
6. Verification checklist
   - 기준서-led verification expectation과 local verification note를 합쳐 만든다.

이 runtime output은 기본적으로 persistent 문서가 아니다. 명시적 필요가 있을 때만 파생
에이전트 문서(8)로 저장할 수 있다.

<!-- key: id=key.standard.skill.coordinator.role-routing-contract refs=key.role.coordinator key.role.subagent key.standard.subagent key.topic.work-execution key.topic.keystone-metadata key.topic.merge-gate -->
## Role routing contract

Role catalog와 기본 authority는 `../../subagents/key-standard-subagents.md`를 따른다.
Coordinator는 그 catalog 안에서 다음 기준으로 실행 역할을 선택한다.

1. Explorer
   - read-only 조사, 기존 규칙 중복 확인, 기존 구현/API/component/service/utility/test/화면
     사용처 조사, repository 조사, prototype 비교가 필요할 때 사용한다. Metadata 기반 관련
     문서 탐색이나 reuse candidate 확인이 필요할 때도 사용할 수 있다.
2. Doc-impact-writer
   - Author Edit Contract와 승인된 문서 수정 범위가 있고, 승인된 변경을 의미상 관련된 원천
     문서(2)에 필요한 만큼 반영해야 하는 경우에만 사용한다.
3. Code-worker
   - edit scope가 명확하고 bounded implementation이 가능한 경우에만 사용한다.
4. Reviewer
   - worker output이 completion criteria, scope, risk, regression 가능성 측면에서 검토가
     필요할 때 사용한다.
5. Verifier
   - 기준서-led verification을 별도 Goal로 실행하거나 failure 원인을 분리해야 할 때
     사용한다.
6. Repo-integrator
   - 여러 main-session branch의 변경을 합치기 전, 또는 여러 task branch 사이에 file/key/merge
     order/verification overlap이 있어 branch diff, text conflict, semantic conflict, merge
     order, verification 범위를 검토해야 할 때 사용한다. Repo-integrator는 staging branch
     밖으로 merge하지 않는다.
7. Main 직접 처리
   - 작은 local 문서 수정, acceptance 판단, scope 변경 판단, high-risk decision이 필요한
     경우 사용한다.

Subagent 공통 금지와 stop condition은 subagent 기준서를 따른다.

<!-- key: id=key.standard.skill.coordinator.branch-worktree-isolation refs=key.role.coordinator key.topic.branch-worktree key.topic.merge-gate key.role.subagent key.topic.remote-policy key.topic.commit-checkpoint -->
## Branch and worktree isolation policy

Coordinator가 subagent에게 파일 수정이 필요한 bounded Goal을 배정할 때는 다음 branch와
worktree 규칙을 따른다.

1. 각 main session은 자기 session branch를 가진다.
2. Subagent task는 session branch에서 task branch를 만들고, 병렬 실행이면 그 task branch를
   isolated worktree에 checkout해 수행한다.
3. Task branch는 자신을 호출한 main-session branch로만 merge할 수 있다.
4. Branch/worktree provisioning은 Main 또는 Coordinator가 수행한다. Worker는 이미 준비된
   task worktree에서만 작업하며 임의 branch 생성, worktree 생성, branch 전환, worktree 삭제를
   하지 않는다.
5. 여러 main-session branch를 검토할 때 Coordinator 또는 repo-integrator는 staging branch를
   사용한다.
6. Integration branch 반영은 staging 결과가 `safe` 또는 acceptance candidate로 보고된 뒤
   integration owner Main 또는 사용자가 수행한다.
7. 한 integration branch에는 동시에 하나의 `integration_owner_id`만 둔다. Owner 변경은
   main/user decision으로 기록한다.
8. Base branch 또는 user-facing stable branch merge는 integration owner Main 또는 사용자
   acceptance 이후에만 가능하다.
9. 한 working tree를 여러 main session이나 subagent가 공유하지 않는다. 병렬 작업은 git
   worktree 사용을 우선한다.
10. 작업 시작 전 worktree가 dirty 상태라면 명시적으로 허용되지 않은 한 subagent를 배정하지
   않는다.
11. Branch workflow는 기본적으로 local-only다. Branch context에는 `remote_policy:
   local_only`, `push_allowed: false`, `commit_required_before_merge: true`를 포함한다.
12. Coordinator, subagent, repo-integrator는 remote push, remote branch 생성, PR 생성,
    remote merge를 수행하지 않는다. Remote write는 사용자의 명시 요청이 있을 때만 가능하다.
13. 파일 수정 subagent는 task branch 변경을 local commit으로 고정한 뒤 report한다.
    Uncommitted diff는 merge 대상이나 repo-integrator staging input으로 사용하지 않는다.
14. Branch context에는 최소한 `round_id`, `work_id`, `step_id`, `session_id`,
   `integration_owner_id`, `task_id`, base branch, integration branch, session branch, task
   branch 또는 staging branch, worktree path, merge target, forbidden merge targets, base
   commit, `session_head_at_assignment`, `merge_target_head_at_review`, `merge_base`, dirty
   worktree 허용 여부, remote policy, push 허용 여부, commit requirement, 필요한 경우 task
   commit range를 기록한다.
15. Merge 직전에 `merge_target_head_at_review`가 `session_head_at_assignment`와 다르면 새 diff와
   semantic overlap을 다시 검토한다.

<!-- key: id=key.standard.skill.coordinator.merge-gate-policy refs=key.role.coordinator key.topic.merge-gate key.topic.branch-worktree key.topic.keystone-metadata key.topic.acceptance key.topic.commit-checkpoint -->
## Merge gate policy

Main은 단순하고 범위가 명확한 branch를 직접 검토하고 merge할 수 있다. 단순 merge는 다음
조건을 모두 만족해야 한다.

1. 병합 대상이 단일 task branch다.
2. 변경 파일이 적고 direct edit scope 안에만 있다.
3. 공통 권위 문서를 수정하지 않았다.
4. 같은 파일, 같은 `key.id`, 같은 decision topic, 같은 progress state를 다른 branch가
   수정하지 않았다.
5. Task branch 변경이 local commit으로 고정되어 있고 검토할 commit range 또는 branch diff가
   명확하다.
6. Git merge가 clean하다.
7. Verification path가 명확하다.
8. `merge_target_head_at_review`가 `session_head_at_assignment`와 다르면 새 diff와 semantic
   overlap 재검토가 끝났다.
9. Main이 diff를 직접 이해하고 scope 위반 여부를 판단할 수 있다.

다음 조건 중 하나라도 있으면 Coordinator는 repo-integrator 또는 reviewer/verifier workflow로
escalation한다.

1. 병합 대상 main-session branch가 둘 이상이다.
2. 병합 대상 task branch가 둘 이상이고 file/key/merge-order/verification overlap이 있다.
3. 같은 파일을 여러 branch가 수정했다.
4. 같은 `key.id`를 여러 branch가 수정했다.
5. `key-context-map.md`, works index, decisions, progress, project standard 같은 공통 권위
   문서가 변경되었다.
6. Scope, acceptance criteria, status semantics, source authority가 변경될 수 있다.
7. Git conflict 또는 semantic conflict 가능성이 있다.
8. Task branch commit range가 불명확하거나 uncommitted diff를 병합해야 한다.
9. 병합 순서나 merge 후 verification 범위가 불명확하다.
10. Assignment 이후 merge target HEAD가 바뀌었지만 새 diff와 semantic overlap 검토가 없다.

같은 `key.refs` overlap은 semantic review candidate로 보고한다. 넓은 topic refs만 겹치는
경우에는 warning으로 보고하고 자동 block으로 처리하지 않는다.

<!-- key: id=key.standard.skill.coordinator.repo-integrator-contract refs=key.role.coordinator key.role.subagent key.topic.merge-gate key.topic.branch-worktree key.topic.verification key.topic.remote-policy key.topic.commit-checkpoint -->
## Repo-integrator contract

Repo-integrator는 Coordinator가 호출하는 복잡 병합 전용 subagent role이다. 새 Keystone 스킬이
아니며, role과 authority는 `../../subagents/key-standard-subagents.md`를 따른다.

1. Lane: `repo`
2. Role: `repo-integrator`
3. Authority: `staging_merge`
4. 허용: branch별 diff 요약, declared scope와 actual diff 비교, text conflict 확인,
   semantic conflict 후보 확인, commit range 확인, merge order 제안, staging branch dry-run
   또는 실험 병합, 사전 승인된 merge plan 안의 기계적으로 명백한 conflict 해결,
   verification plan 작성
5. 금지: base branch 직접 merge, integration branch 직접 merge, user-facing stable branch 직접
   merge, remote push, remote branch 생성, PR 생성, remote merge, final acceptance, progress
   `accepted` 처리, policy 결정, scope 확장, 의미 선택이 필요한 conflict 직접 해결
6. Output: `safe`, `needs_review`, `blocked` 중 하나와 evidence, staging merge result,
   verification plan, residual risk를 보고한다.

<!-- key: id=key.standard.skill.coordinator.report-handling-contract refs=key.role.coordinator key.topic.report key.role.subagent key.standard.subagent -->
## Report handling contract

Report status 값과 기본 의미는 `../../subagents/key-standard-subagents.md`를 따른다.
Coordinator는 받은 status를 다음 workflow 결정으로 처리한다.

1. `DONE`
   - 실제 상태와 verification을 확인한 뒤 main acceptance 후보로 올린다.
2. `DONE_WITH_CONCERNS`
   - risk나 불확실성을 기준으로 review 또는 verification을 우선 검토한다.
3. `NEEDS_CONTEXT`
   - Reader, Author, Clarify 또는 main 직접 보강 중 필요한 context 보강 경로를 정한다.
4. `NEEDS_SCOPE_CHANGE`
   - 사용자 또는 관련 기준서(3)/작업서(4) update 결정을 먼저 받아야 한다.
5. `BLOCKED`
   - unblock path를 찾거나 stop report로 main/user에게 보고한다.

Repo-integrator result는 다음 report status로 해석한다.

1. `safe`는 `DONE`으로 처리한다.
2. `needs_review`는 `DONE_WITH_CONCERNS`로 처리한다.
3. Branch context, commit range, verification input이 부족하면 `NEEDS_CONTEXT`로 처리한다.
4. Scope, acceptance criteria, source authority 변경이 필요하면 `NEEDS_SCOPE_CHANGE`로 처리한다.
5. 해결 불가능 conflict, 금지된 merge target, remote write 요구는 `BLOCKED`로 처리한다.

<!-- key: id=key.standard.skill.coordinator.review-verification-flow refs=key.role.coordinator key.topic.verification key.topic.review key.topic.merge-gate key.topic.keystone-metadata -->
## Review and verification flow

Review와 verification은 다음 순서를 따른다.

1. Worker output이 scope와 completion criteria 안에 있는지 확인한다.
2. Existing user change 또는 다른 agent change를 덮어쓸 risk가 있는지 확인한다.
3. 같은 `key.id`를 참조하는 문서와의 충돌 여부를 reviewer focus 후보로 확인한다.
4. Merge가 포함되면 text conflict와 semantic conflict 후보를 분리해 확인한다.
5. 같은 `key.id`를 여러 branch가 수정하면 repo-integrator 검토 대상으로 본다.
6. 같은 `key.refs` overlap은 semantic review candidate로 보고하며 자동 block으로 처리하지
   않는다.
7. 필요하면 reviewer Goal을 배정한다.
8. 기준서(3)에서 verification expectation을 추출한다.
9. 작업서(4)의 local verification note가 기준서-led verification을 약화하지 않는지 확인한다.
10. Merge 전 verification과 merge 후 verification이 다를 수 있으면 둘을 분리해 기록한다.
11. 필요하면 verifier Goal을 배정한다.
12. Verification failure가 있으면 repair 또는 escalation으로 처리한다.
13. Verification을 실행할 수 없으면 residual risk로 보고하고 acceptance 여부를 main이
   판단한다.

<!-- key: id=key.standard.skill.coordinator.merge-authorization-contract refs=key.role.coordinator key.topic.merge-authorization key.topic.acceptance key.topic.verification key.topic.merge-gate -->
## Merge authorization contract

Merge authorization은 특정 branch를 integration 또는 base branch에 merge해도 된다는 사전 승인이다.
Final acceptance는 merge 후 verification과 residual risk까지 확인한 최종 수락이다.

1. Staging 결과가 `safe` 또는 accepted candidate로 보고된다.
2. Integration owner Main 또는 사용자가 merge authorization을 내린다.
3. Integration owner Main 또는 사용자가 integration branch에 merge한다.
4. Post-merge verification을 실행하거나 실행 불가 사유와 residual risk를 기록한다.
5. Main 또는 사용자가 final acceptance를 내린다.
6. Final acceptance 이후에만 progress를 `accepted`로 표시한다.

<!-- key: id=key.standard.skill.coordinator.acceptance-contract refs=key.role.coordinator key.topic.acceptance key.topic.verification key.topic.merge-gate key.topic.merge-authorization -->
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
9. Merge가 포함된 경우 merge target이 허용 범위 안에 있고 base branch 직접 merge가 아니다.
10. Merge가 포함된 경우 병합 대상 변경이 local commit checkpoint로 고정되어 있다.
11. Remote push, remote branch 생성, PR 생성, remote merge가 필요한 경우 사용자 명시 승인이
    있다.
12. Integration/base branch merge가 포함된 경우 merge authorization과 final acceptance를
    분리했다.
13. Merge 성공을 Keystone acceptance로 해석하지 않았다.

Acceptance 후에만 진행 기록(5)을 `accepted` 또는 해당 project의 완료 상태로 바꿀 수 있다.
Merge 성공은 Git 상태가 합쳐졌다는 뜻일 뿐이며, 진행 기록(5)의 `accepted` 상태는 Main 또는
사용자 acceptance 이후에만 기록한다.

<!-- key: id=key.standard.skill.coordinator.progress-update-boundary refs=key.role.coordinator key.topic.progress-update key.topic.acceptance key.topic.merge-gate -->
## Progress update boundary

진행 기록(5)은 subagent workflow 상태를 복구하기 위해 다음 규칙으로 갱신한다.

1. Assignment를 만들면 필요한 경우 `assigned`를 기록할 수 있다.
2. Report를 받으면 필요한 경우 `reported`를 기록할 수 있다.
3. Review 중이면 `reviewing`, verification 중이면 `verifying`을 기록할 수 있다.
4. Main acceptance 전에는 `accepted`로 표시하지 않는다.
5. Worker `DONE`만으로 progress를 완료 처리하지 않는다.
6. Merge 성공만으로 progress를 완료 처리하지 않는다.
7. 문서 작성/수정의 기준과 반영 범위는 `keystone-author`가 담당한다. Formal workflow 상태를
   복구해야 하는 경우에만 Coordinator가 진행 상태 전이를 조율한다.
8. 단순 오탈자, 미세 표현 수정, 의미 변화 없는 formatting은 진행 기록(5)에 남기지 않는다.
9. Status semantics를 바꾸려면 Author 또는 Clarify를 통해 원천 문서(2) update 결정을 먼저
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

<!-- key: id=key.standard.skill.coordinator.stop-condition refs=key.role.coordinator key.topic.skill-contract key.topic.work-execution key.topic.branch-worktree key.topic.merge-gate key.topic.remote-policy key.topic.commit-checkpoint -->
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
12. 파일 수정 또는 merge가 필요한데 branch context가 없다.
13. 작업 시작 전 worktree가 dirty 상태이고 허용 여부가 명시되지 않았다.
14. Task branch가 호출한 main-session branch가 아닌 곳에 merge되려 한다.
15. Base branch, integration branch, user-facing stable branch 직접 merge가 요구된다.
16. 같은 파일 또는 같은 `key.id`를 여러 branch가 수정했지만 repo-integrator 검토가 없다.
17. Merge 후 verification 범위가 불명확하다.
18. Remote push 또는 remote branch 생성, PR 생성, remote merge가 필요한데 사용자 명시 승인이
    없다.
19. Merge 대상 task branch에 local commit으로 고정되지 않은 변경이 있다.
20. Branch/worktree provisioning이 필요한데 Main 또는 Coordinator가 준비하지 않았다.
21. Worker가 준비된 task worktree 밖에서 branch 생성, worktree 생성, branch 전환, worktree
    삭제를 해야만 진행할 수 있다.
22. Integration branch가 관련되어 있지만 `integration_owner_id`가 없거나 둘 이상이다.
23. Assignment 이후 merge target HEAD가 바뀌었지만 새 diff와 semantic overlap 검토가 없다.

<!-- key: id=key.standard.skill.coordinator.verification refs=key.role.coordinator key.topic.verification key.topic.acceptance key.standard.subagent key.topic.branch-worktree key.topic.merge-gate key.topic.remote-policy key.topic.commit-checkpoint -->
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
10. Role catalog와 report status 정의를 반복하지 않고 subagent 기준서를 참조해야 한다.
11. Branch context를 보고 task branch, worktree, merge target, forbidden merge target을
    구분할 수 있어야 한다.
12. Repo-integrator가 staging branch 밖의 merge나 final acceptance를 수행하지 않는다는 점을
    확인할 수 있어야 한다.
13. Remote push, remote branch 생성, PR 생성, remote merge는 사용자 명시 승인 없이는 수행되지
    않아야 한다.
14. Task branch 변경은 merge 전 local commit checkpoint로 고정되어야 한다.
15. Branch context에서 round/work/session/task identity와 assignment/review HEAD drift를
    확인할 수 있어야 한다.
16. Merge authorization과 final acceptance를 구분할 수 있어야 한다.
17. Merge 성공과 Keystone acceptance를 구분할 수 있어야 한다.
18. Verification command:
   - `rg --files 00_docs`
   - Coordinator 관련 기준서를 읽어 link와 scope consistency 확인
   - `git diff --check`
