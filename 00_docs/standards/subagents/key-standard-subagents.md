---
doc_type: standard
key:
  id: key.standard.subagent
  refs:
    - key.role.subagent
    - key.topic.formal-workflow
    - key.topic.work-execution
    - key.topic.verification
    - key.contract.output
---

# Keystone subagent 기준서

<!-- key: id=key.standard.subagent.purpose refs=key.role.subagent key.topic.formal-workflow key.topic.work-execution -->
## 목적

이 기준서는 Keystone helper/subagent의 공통 계약을 정의한다. Subagent는 Main이나 Keystone
스킬이 승인한 bounded Goal을 수행하는 실행자이며, 원천 문서(2)의 권위나 Main acceptance를
대체하지 않는다.

<!-- key: id=key.standard.subagent.scope refs=key.role.subagent key.topic.work-execution key.contract.output -->
## 적용 범위

1. Helper와 subagent의 공통 책임 경계
2. Lane, role, authority 기준
3. Subagent role catalog
4. Role별 input과 output contract
5. Report status 값과 의미
6. 공통 금지와 stop condition

<!-- key: id=key.standard.subagent.out-of-scope refs=key.role.subagent key.boundary.approval key.topic.acceptance -->
## 적용하지 않는 범위

1. Main acceptance decision 대체
2. 전체 작업서(4) 재해석 또는 scope 확장
3. 사용자가 승인하지 않은 원천 문서(2), code, config, generated file 변경
4. 추가 subagent 생성 또는 독자적 workflow orchestration
5. High-impact decision, policy, acceptance criteria, status semantics 확정

<!-- key: id=key.standard.subagent.standard-relations refs=key.role.subagent key.doc.standard key.topic.skill-contract -->
## 기준 관계

1. Parent 기준서: `../01_key-project-standard.md`
2. 상위 규칙: `STD-KEYSTONE-001`, `STD-KEYSTONE-007`, `STD-KEYSTONE-020`,
   `STD-KEYSTONE-024`, `STD-KEYSTONE-025`, `STD-KEYSTONE-030`,
   `STD-KEYSTONE-031`, `STD-KEYSTONE-032`, `STD-KEYSTONE-043`
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

<!-- key: id=key.standard.subagent.lane-role-authority refs=key.role.subagent key.topic.work-execution key.topic.formal-workflow -->
## Lane, role, authority

실행 역할은 다음 세 축으로 제한한다.

1. Lane: `docs`, `code`, `repo`처럼 작업 영역을 구분한다.
2. Role: `explorer`, `doc-impact-writer`, `code-worker`, `reviewer`, `verifier`처럼 수행할
   일을 구분한다.
3. Authority: `read_only`, `bounded_edit`, `review_only`, `verification`처럼 허용 권한을
   구분한다.

새 role이 필요하면 Coordinator나 Author 기준서에서 ad hoc으로 만들지 않고 이 기준서를 먼저
수정하거나 main/user 결정(6)을 받는다.

<!-- key: id=key.standard.subagent.role-catalog refs=key.role.subagent key.topic.work-execution key.topic.verification key.topic.keystone-metadata -->
## Role catalog

1. Explorer
   - 기본 authority: `read_only`
   - 사용: 기존 규칙 중복 확인, 기존 구현/API/component/service/utility/test/화면 사용처 조사,
     repository 조사, prototype 비교, metadata 기반 관련 문서 탐색
   - 출력: 조사 요약, reuse candidate, 후보 위치, 기존 사용 사례, 입력/출력, 권한/제약,
     요구사항과의 차이, sources read, assumptions, risks and gaps
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
   - 출력: 변경 파일, verification result, 남은 risk
4. Reviewer
   - 기본 authority: `review_only`
   - 사용: worker output이 completion criteria, scope, risk, regression 가능성 측면에서 검토가
     필요할 때
   - 출력: findings, risks, required repair, review conclusion
5. Verifier
   - 기본 authority: `verification`
   - 사용: 기준서-led verification을 별도 Goal로 실행하거나 failure 원인을 분리해야 할 때
   - 출력: verification command/result, pass/fail, failure cause, residual risk

<!-- key: id=key.standard.subagent.input-contract refs=key.role.subagent key.contract.output key.topic.work-execution key.topic.keystone-metadata -->
## Input contract

Subagent에게 작업을 맡길 때는 최소한 다음을 제공해야 한다.

1. Goal
2. Lane, role, authority
3. Primary scope와 read scope
4. Direct edit scope와 forbidden changes
5. Source Context 또는 Context Pack
6. 관련 `key.id`, `key.refs`, metadata 기반 후보 문서
7. Completion Criteria
8. Stop Conditions
9. Verification path
10. Report status contract

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

<!-- key: id=key.standard.subagent.common-boundary refs=key.role.subagent key.boundary.approval key.topic.work-execution key.topic.keystone-metadata -->
## 공통 경계

모든 helper/subagent는 다음을 지켜야 한다.

1. 받은 Goal 밖으로 scope를 넓히지 않는다.
2. 전체 작업서(4)를 재해석하지 않는다.
3. 추가 subagent를 생성하지 않는다.
4. Main acceptance 없이 progress를 `accepted` 또는 `complete`로 바꾸지 않는다.
5. 승인되지 않은 source authority, acceptance criteria, status semantics를 바꾸지 않는다.
6. 민감한 정보, local-only path, private data가 필요하면 멈추고 보고한다.
7. Worker output은 원천 문서(2)나 Main decision을 대체하지 않는다.
8. Metadata 기반 후보나 reuse candidate는 채택 결정이 아니라 검토 대상 evidence로 보고한다.
9. Impact candidate가 연결되어 있다는 이유만으로 수정하지 않는다. 관련성이 불확실하면
   수정하지 않고 report한다.

<!-- key: id=key.standard.subagent.stop-condition refs=key.role.subagent key.boundary.stop-condition key.topic.work-execution -->
## Stop condition

Subagent는 다음 상황에서 멈추고 report한다.

1. Goal, scope, authority, stop condition이 불명확하다.
2. Completion Criteria를 만족하려면 승인 범위를 넘어야 한다.
3. 필요한 source context가 빠져 있다.
4. 사용자 변경이나 repository state와 충돌한다.
5. 민감한 정보, local-only path, private data가 필요하다.
6. Verification path가 없거나 실행 결과가 판단 불가능하다.
7. 추가 subagent나 전체 workflow 재조율이 필요하다.

<!-- key: id=key.standard.subagent.verification refs=key.role.subagent key.topic.verification -->
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
