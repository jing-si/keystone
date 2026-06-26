---
doc_type: standard
key:
  id: key.standard.subagent
  refs:
    - key.role.subagent
    - key.topic.formal-workflow
    - key.topic.work-execution
    - key.topic.branch-worktree
    - key.topic.merge-gate
    - key.topic.remote-policy
    - key.topic.commit-checkpoint
    - key.topic.verification
    - key.topic.git-capability
    - key.topic.artifact-graph
    - key.contract.output
    - key.contract.report
---

# Keystone subagent 기준서

<!-- key: id=key.standard.subagent.purpose refs=key.role.subagent key.topic.formal-workflow key.topic.work-execution -->
## 목적

이 기준서는 Keystone helper/subagent의 공통 계약을 정의한다. Subagent는 Main이나 Keystone
스킬이 승인한 bounded Goal을 수행하는 실행자이며, 원천 문서(2)의 권위나 Main acceptance를
대체하지 않는다.

<!-- key: id=key.standard.subagent.scope refs=key.role.subagent key.topic.work-execution key.topic.git-capability key.topic.artifact-graph key.contract.output key.contract.report -->
## 적용 범위

1. Helper와 subagent의 공통 책임 경계
2. Lane, role, authority 기준
3. Subagent role catalog
4. Role별 input과 output contract
5. Report status 값과 의미
6. Authority별 Git/file capability matrix
7. 아티팩트 그래프(14) 기반 reuse discovery, impact review, graph validation 책임
8. Branch, worktree, merge 관련 공통 권한 경계
9. 공통 report envelope
10. 공통 금지와 stop condition

<!-- key: id=key.standard.subagent.out-of-scope refs=key.role.subagent key.boundary.approval key.topic.acceptance -->
## 적용하지 않는 범위

1. Main acceptance decision 대체
2. 전체 작업서(4) 재해석 또는 scope 확장
3. 사용자가 승인하지 않은 원천 문서(2), code, config, generated file 변경
4. 추가 subagent 생성 또는 독자적 workflow orchestration
5. High-impact decision, policy, acceptance criteria, status semantics 확정
6. Base branch, integration branch, user-facing stable branch 직접 merge
7. 사용자 명시 승인 없는 remote push, remote branch 생성, PR 생성, remote merge

<!-- key: id=key.standard.subagent.standard-relations refs=key.role.subagent key.doc.standard key.topic.skill-contract key.topic.artifact-graph -->
## 기준 관계

1. Parent 기준서: `../01_key-project-standard.md`
2. 상위 규칙: `STD-KEYSTONE-001`, `STD-KEYSTONE-007`, `STD-KEYSTONE-015`,
   `STD-KEYSTONE-017`, `STD-KEYSTONE-018`, `STD-KEYSTONE-020`,
   `STD-KEYSTONE-024`, `STD-KEYSTONE-025`, `STD-KEYSTONE-027`,
   `STD-KEYSTONE-030`, `STD-KEYSTONE-031`, `STD-KEYSTONE-032`, `STD-KEYSTONE-034`,
   `STD-KEYSTONE-043`
3. Coordinator 기준서: `../skills/coordinator/key-standard-coordinator.md`
4. Author 기준서: `../skills/author/key-standard-author.md`
5. 충돌 처리: 이 기준서와 parent 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의
   결정(6)을 받는다. 결정 전까지는 parent 기준서를 임시 우선 기준으로 삼는다.

<!-- key: id=key.standard.subagent.terms refs=key.role.subagent key.topic.work-execution -->
## 용어

1. Helper: Main 또는 skill이 좁은 보조 작업에 사용하는 bounded 실행자다.
2. Subagent: formal workflow 안에서 Goal, Context Pack, stop condition, report contract를
   받아 독립적으로 수행하는 bounded 실행자다.
3. Helper와 subagent 모두 이 기준서의 lane, role, authority, stop condition을 따른다.
4. `doc-explorer`는 `lane=docs`, `role=explorer`, `authority=read_only`의 별칭이다.
5. `doc-impact-writer`는 `lane=docs`, `role=doc-impact-writer`,
   `authority=bounded_edit`의 별칭이다.

<!-- key: id=key.standard.subagent.lane-role-authority refs=key.role.subagent key.topic.work-execution key.topic.formal-workflow key.topic.merge-gate -->
## Lane, role, authority

실행 역할은 다음 세 축으로 제한한다.

1. Lane: `docs`, `code`, `repo`처럼 작업 영역을 구분한다.
2. Role: `explorer`, `doc-impact-writer`, `code-worker`, `reviewer`, `verifier`처럼 수행할
   일을 구분한다. 복잡한 병합 전용 역할은 `repo-integrator`를 사용한다.
3. Authority: `read_only`, `bounded_edit`, `review_only`, `verification`, `staging_merge`처럼
   허용 권한을 구분한다.
4. `staging_merge`는 staging branch에서 dry-run 또는 실험 병합만 수행할 수 있는 권한이다.
   Base branch, integration branch, user-facing stable branch merge 권한을 포함하지 않는다.

새 role이 필요하면 Coordinator나 Author 기준서에서 ad hoc으로 만들지 않고 이 기준서를 먼저
수정하거나 main/user 결정(6)을 받는다.

<!-- key: id=key.standard.subagent.role-catalog refs=key.role.subagent key.topic.work-execution key.topic.verification key.topic.keystone-metadata key.topic.artifact-graph key.topic.branch-worktree key.topic.merge-gate -->
## Role catalog

1. Explorer
   - 기본 authority: `read_only`
   - 사용: 기존 규칙 중복 확인, 기존 구현/API/component/service/utility/test/화면 사용처 조사,
     repository 조사, prototype 비교, 키메타와 코드 앵커 기반 관련 문서와 artifact 탐색,
     capability provider 후보와 키메타/코드 앵커 gap 조사
   - 출력: 조사 요약, reuse candidate, artifact candidates, 후보 위치, 기존 사용 사례, 입력/출력,
     권한/제약, 요구사항과의 차이, 키메타/코드 앵커 gaps, sources read, assumptions, risks and
     gaps
   - 경계: Explorer는 후보와 evidence를 보고하지만 해당 후보를 실제로 채택할지 결정하지
     않는다.
2. Doc-impact-writer
   - 기본 lane: `docs`
   - 기본 authority: `bounded_edit`
   - 사용: Author가 정한 승인 범위 안에서 현재 문서 변경을 의미상 관련된 원천 문서(2)에
     필요한 만큼 반영해야 할 때
   - 입력 단서: Author Edit Contract, metadata/link/path/heading/keyword로 찾은 impact
     candidate, 승인된 변경 의도
   - 출력: 변경 문서, 검토한 impact candidate, 수정하지 않은 후보와 이유, 적용한 기준,
     남은 risk
   - 경계: 연결된 문서를 모두 수정하지 않는다. 현재 변경을 반영하지 않으면 문서 간 의미
     충돌이나 구조 불일치가 생기는 경우에만 승인 범위 안에서 수정한다.
3. Code-worker
   - 기본 lane: `code`
   - 기본 authority: `bounded_edit`
   - 사용: Coordinator가 정한 승인 범위 안의 bounded implementation
   - 출력: 변경 파일, reuse decision, 코드 앵커 변경, verification result, 남은 risk
   - 경계: 명시 승인 없이 API contract, DB schema/migration, auth/security, generated/codegen,
     shared architecture, public interface, dependency 또는 build system을 변경하지 않는다.
   - 재사용: 새 기능이나 method를 만들기 전에 capability, `provides`, `uses`, `implements`,
     실제 code reference, 기존 test를 함께 검색하고 `reuse_existing`, `extend_existing`,
     `create_new` 중 하나로 reuse decision을 보고한다.
   - 코드 앵커: reusable core method, public API, domain rule, shared service, 중요한 test에는 필요한
     경우 코드 앵커를 추가한다. Local helper, trivial wrapper, generated code에는 기본적으로
     추가하지 않는다.
4. Reviewer
   - 기본 authority: `review_only`
   - 사용: worker output이 completion criteria, scope, risk, regression 가능성 측면에서 검토가
     필요할 때
   - 출력: findings, risks, required repair, review conclusion
   - 경계: Reviewer는 판단과 보고를 수행한다. 파일 수정, commit, merge는 하지 않는다.
   - Graph review: 기존 capability 재사용 여부, 중복 implementation 생성 여부, semantic stale,
     코드 앵커 admission 적절성을 검토한다.
5. Verifier
   - 기본 authority: `verification`
   - 사용: 기준서-led verification을 별도 Goal로 실행하거나 failure 원인을 분리해야 할 때
   - 출력: verification command/result, pass/fail, failure cause, graph validation result,
     residual risk
   - 경계: Verifier는 승인된 검증 명령을 실행하고 원인을 분리한다. 명시 승인 없이 tracked file
     수정, repair commit, merge를 하지 않는다.
   - Graph validation: duplicate ID, unresolved relation, stale locator, missing symbol, missing
     test reference 같은 mechanical stale을 확인한다.
6. Repo-integrator
   - 기본 lane: `repo`
   - 기본 authority: `staging_merge`
   - 사용: 여러 branch의 변경을 합치기 전에 branch diff, text conflict, semantic conflict,
     merge order, verification 범위를 검토해야 할 때
   - 출력: branch별 diff 요약, scope 비교, conflict candidate, merge order, staging merge
     result, verification plan, residual risk
   - 경계: staging branch에서만 dry-run 또는 실험 병합을 수행할 수 있다. Base branch,
     integration branch, user-facing stable branch 직접 merge, remote write, final acceptance,
     progress `accepted` 처리는 하지 않는다. 의미 선택이 필요한 conflict는 직접 해결하지 않고
     `needs_review` 또는 `BLOCKED`로 보고한다.

<!-- key: id=key.standard.subagent.input-contract refs=key.role.subagent key.contract.output key.topic.work-execution key.topic.keystone-metadata key.topic.artifact-graph key.topic.branch-worktree key.topic.merge-gate -->
## Input contract

Subagent에게 작업을 맡길 때는 최소한 다음을 제공해야 한다.

1. Goal
2. Lane, role, authority
3. Primary scope와 read scope
4. Direct edit scope와 forbidden changes
5. Source Context 또는 Context Pack
6. 관련 `key.id`, `key.refs`, 코드 앵커 typed relation, 키메타/코드 앵커 기반 후보 문서와 artifact
7. Completion Criteria
8. Stop Conditions
9. Verification path
10. 필요한 경우 impact seeds 또는 Change Set(17)
11. 필요한 경우 branch context
12. Report status contract

Input이 부족하면 subagent는 추측해서 범위를 넓히지 않고 `NEEDS_CONTEXT` 또는 `BLOCKED`로
보고한다.

<!-- key: id=key.standard.subagent.report-status refs=key.role.subagent key.topic.report key.contract.output -->
## Report status

Subagent report status 값은 다음과 같다.

1. `DONE`
   - 요청 범위가 완료되었다고 보고한다.
2. `DONE_WITH_CONCERNS`
   - 완료되었지만 risk나 불확실성이 있다.
3. `NEEDS_CONTEXT`
   - 필요한 문서, 기준, 파일, 결정(6)이 부족하다.
4. `NEEDS_SCOPE_CHANGE`
   - 승인된 scope를 넘어야 한다.
5. `BLOCKED`
   - 외부 상태, missing dependency, 권한, 충돌 때문에 진행할 수 없다.

Subagent report status는 progress status가 아니다. Main 또는 Coordinator가 실제 상태와
verification을 확인하기 전까지 `DONE`을 accepted로 해석하지 않는다.

<!-- key: id=key.standard.subagent.git-file-capability-matrix refs=key.role.subagent key.topic.git-capability key.topic.branch-worktree key.topic.remote-policy key.topic.commit-checkpoint -->
## Git/file capability matrix

Authority별 Git과 file 행위는 다음 표를 따른다.

| Role | 허용 | 금지 |
| --- | --- | --- |
| Explorer | `git status`, `git diff`, `git log`, `git show`, `git merge-base` 같은 read-only 조사 | `git add`, `git commit`, `git merge`, `git rebase`, `git reset`, `git stash`, `git clean`, remote write |
| Doc-impact-writer / Code-worker | 준비된 task worktree 안의 scoped file edit, scoped `git add`, local `git commit` | 임의 `git checkout`/`git switch`, branch 삭제, merge, rebase, reset, stash, clean, remote write |
| Reviewer | diff/log/show 기반 검토와 finding 보고 | file edit, commit, merge, repair |
| Verifier | 승인된 verification command 실행과 failure cause 분리 | 명시 승인 없는 tracked file 수정, repair commit, merge |
| Repo-integrator | 승인된 staging worktree의 diff, merge-base, staging merge experiment, verification plan | integration/base/user-facing branch merge, remote write, history rewrite, 의미 선택 conflict 직접 해결 |

모든 role은 명시 승인 없이 다음 명령 또는 동등한 효과를 내는 작업을 수행하지 않는다.

1. `git stash`
2. `git reset --hard`
3. `git clean -fd`
4. `git branch -D`
5. `git worktree remove`
6. `git update-ref`
7. `git rebase`
8. 배정된 branch/worktree 밖으로 이동하는 임의 `git checkout` 또는 `git switch`

<!-- key: id=key.standard.subagent.report-envelope refs=key.role.subagent key.contract.report key.contract.output key.topic.branch-worktree key.topic.verification -->
## Report envelope

Subagent report는 role-specific payload를 추가할 수 있지만, 기본 envelope는 다음 필드를 우선
사용한다.

```yaml
report:
  role:
  lane:
  authority:
  status:
  goal:
  scope_summary:
  branch_context:
  commit_range:
  changed_files:
  keymeta_or_code_anchor_changes:
  reuse_decision:
  findings:
  verification:
  graph_validation:
  scope_check:
  forbidden_change_check:
  keymeta_or_code_anchor_gap_candidates:
  risks:
  residual_risk:
  recommended_next_action:
```

Repo-integrator result는 report status와 다음처럼 연결한다.

1. `safe`는 `DONE`으로 보고한다.
2. `needs_review`는 `DONE_WITH_CONCERNS`로 보고한다.
3. Branch context, commit range, verification input이 부족하면 `NEEDS_CONTEXT`로 보고한다.
4. Scope, acceptance criteria, source authority 변경이 필요하면 `NEEDS_SCOPE_CHANGE`로 보고한다.
5. 해결 불가능 conflict, 금지된 merge target, remote write 요구는 `BLOCKED`로 보고한다.

<!-- key: id=key.standard.subagent.common-boundary refs=key.role.subagent key.boundary.approval key.topic.work-execution key.topic.keystone-metadata key.topic.merge-gate key.topic.remote-policy key.topic.commit-checkpoint -->
## 공통 경계

모든 helper/subagent는 다음을 지켜야 한다.

1. 받은 Goal 밖으로 scope를 넓히지 않는다.
2. 전체 작업서(4)를 재해석하지 않는다.
3. 추가 subagent를 생성하지 않는다.
4. Main acceptance 없이 progress를 `accepted` 또는 `complete`로 바꾸지 않는다.
5. 승인되지 않은 source authority, acceptance criteria, status semantics를 바꾸지 않는다.
6. 민감한 정보, local-only path, private data가 필요하면 멈추고 보고한다.
7. Worker output은 원천 문서(2)나 Main decision을 대체하지 않는다.
8. 키메타/코드 앵커 기반 후보나 reuse candidate는 채택 결정이 아니라 검토 대상 evidence로 보고한다.
9. Impact candidate가 연결되어 있다는 이유만으로 수정하지 않는다. 관련성이 불확실하면
   수정하지 않고 report한다.
10. `staging_merge` authority를 받더라도 base branch, integration branch, user-facing stable
    branch에 직접 merge하지 않는다.
11. Merge 성공을 Main acceptance나 progress `accepted`로 해석하지 않는다.
12. Remote push, remote branch 생성, PR 생성, remote merge를 수행하지 않는다. Remote write는
    사용자가 명시적으로 승인한 경우에만 가능하다.
13. 파일 수정 결과는 merge 전 local commit으로 고정한다. Uncommitted diff는 merge 대상이나
    repo-integrator staging input으로 사용하지 않는다.
14. File-writing worker는 준비된 task branch와 worktree에서만 작업한다. 임의 branch/worktree
    생성, 전환, 삭제는 하지 않는다.
15. 아티팩트 그래프(14) relation은 자동 수정 또는 자동 acceptance 근거가 아니다.
16. Observed relation과 inferred relation은 declared 키메타나 코드 앵커로 조용히 승격하지 않는다.
17. 기존 reusable capability provider가 발견되면 중복 구현을 만들기 전에 reuse 또는 extension
    가능성을 보고한다.

<!-- key: id=key.standard.subagent.stop-condition refs=key.role.subagent key.boundary.stop-condition key.topic.work-execution key.topic.branch-worktree key.topic.merge-gate key.topic.remote-policy key.topic.commit-checkpoint -->
## Stop condition

Subagent는 다음 상황에서 멈추고 report한다.

1. Goal, scope, authority, stop condition이 불명확하다.
2. Completion Criteria를 만족하려면 승인 범위를 넘어야 한다.
3. 필요한 source context가 빠져 있다.
4. 사용자 변경이나 repository state와 충돌한다.
5. 민감한 정보, local-only path, private data가 필요하다.
6. Verification path가 없거나 실행 결과가 판단 불가능하다.
7. 추가 subagent나 전체 workflow 재조율이 필요하다.
8. 파일 수정 또는 merge가 필요한데 branch context가 없다.
9. Base branch, integration branch, user-facing stable branch 직접 merge가 필요하다.
10. 작업 시작 전 worktree가 dirty 상태인데 허용 여부가 명시되지 않았다.
11. Remote push, remote branch 생성, PR 생성, remote merge가 필요한데 사용자 명시 승인이 없다.
12. 파일 수정 결과를 report하거나 merge해야 하는데 변경이 local commit으로 고정되지 않았다.
13. File-writing task인데 준비된 task branch와 worktree가 없다.
14. 배정된 branch/worktree 밖에서 branch 생성, worktree 생성, branch 전환, worktree 삭제가
    필요하다.
15. 새 reusable artifact를 만들어야 하지만 기존 capability/provider 탐색 결과가 없다.
16. 키메타 또는 코드 앵커 relation이 가리키는 artifact가 없고 fallback 판단이 불가능하다.

<!-- key: id=key.standard.subagent.verification refs=key.role.subagent key.topic.verification key.topic.merge-gate key.topic.remote-policy key.topic.commit-checkpoint -->
## Verification

Subagent 기준은 다음 방법으로 검증한다.

1. 각 role의 lane과 authority를 설명할 수 있어야 한다.
2. Subagent input만 보고 수행 가능 범위와 stop condition을 구분할 수 있어야 한다.
3. Report status와 progress status를 혼동하지 않아야 한다.
4. Coordinator 기준서는 role 정의를 반복하지 않고 이 기준서의 role catalog를 참조해야 한다.
5. Author 기준서는 문서 작업 helper 사용 조건만 정의하고 formal workflow orchestration을
   소유하지 않아야 한다.
6. Doc-impact-writer는 연결된 모든 문서가 아니라 승인된 변경과 의미상 관련된 문서만 수정해야
   한다.
7. Repo-integrator는 staging branch 밖의 merge나 final acceptance를 수행하지 않아야 한다.
8. Subagent는 사용자 명시 승인 없이 remote push, remote branch 생성, PR 생성, remote merge를
   하지 않아야 한다.
9. 파일 수정 subagent의 결과는 merge 전 local commit checkpoint로 고정되어야 한다.
10. Authority별 Git/file capability matrix만 보고 role별 허용 command와 금지 command를 구분할
    수 있어야 한다.
11. 공통 report envelope와 repo-integrator result mapping을 보고 Coordinator가 후속 workflow를
    결정할 수 있어야 한다.
12. Code-worker는 새 구현 전에 reuse discovery 결과를 보고해야 한다.
13. Reviewer는 semantic stale과 중복 구현 risk를 검토할 수 있어야 한다.
14. Verifier는 graph validation의 mechanical stale을 보고할 수 있어야 한다.
