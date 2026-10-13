---
doc_type: standard
created_at: "2026-06-10"
document_lifecycle: active
approval:
  state: accepted
  accepted_at: "2026-10-13"
  accepted_by: main
key:
  id: key.standard.skill.author
  refs:
    - key.role.author
    - key.role.subagent
    - key.standard.subagent
    - key.topic.document-authoring
    - key.topic.work-creation
    - key.topic.impact-review
    - key.topic.progress-update
    - key.topic.acceptance
    - key.topic.verification
    - key.topic.work-recovery
    - key.topic.question-flow
    - key.topic.artifact-graph
    - key.topic.temporal-metadata
---

# keystone-author 기준서

<!-- key: id=key.standard.skill.author.purpose refs=key.role.author key.topic.document-authoring -->
## 목적

이 기준서는 `keystone-author`의 상세 계약을 정의한다. `keystone-author`는 수락된
요청과 결정(6)을 바탕으로 사람이 읽을 수 있는 기준서(3), 작업서(4), 진행 기록(5),
결정(6) 기록, Change Set(17)을 만들거나 수정한다. Clarify가 여러 수정 그룹을 진행할 때는
대주제별 명확화 로그(21)를 가볍게 유지하고 그룹 질문이 끝난 시점에만 원천 문서를 반영한다.

<!-- key: id=key.standard.skill.author.scope refs=key.role.author key.topic.document-authoring key.topic.work-creation key.topic.impact-review key.topic.artifact-graph -->
## 적용 범위

1. `keystone-author`의 trigger와 non-trigger condition
2. 기준서(3) creation/revision contract
3. 작업서(4) creation/revision contract와 `works/` tree 작성 boundary
4. 수락된 Clarify result를 원천 문서(2)에 적용
5. Parent-child 기준서 구조화와 index update
6. Progress update boundary
7. Change Set(17) 작성 규칙
8. Linker report 또는 Linker handoff seed를 바탕으로 source document metadata 변경,
   Change Set(17), document sync candidate를 반영
9. 새 문서, 현재 의미의 승인과 결정 기록에 temporal metadata를 적용
10. 실제 상태 전이 뒤 bounded terminal status reconciliation
11. Clarify 답변별 명확화 로그(21) append와 그룹별 원천 문서 적용 경계
12. 문서 작성 후 verification과 report contract

<!-- key: id=key.standard.skill.author.out-of-scope refs=key.role.author key.topic.document-authoring key.topic.skill-contract key.topic.formal-workflow key.topic.external-assist -->
## 적용하지 않는 범위

1. High-impact topic을 질문으로 수집하고 결정(6)을 확정하기
2. Read-only project orientation, document navigation, work preparation
3. Formal worker workflow orchestration, worker handoff 확정, report acceptance
4. Implementation code, config, schema, API, test, generated/codegen artifact 수정
5. 승인되지 않은 scope, acceptance criteria, status semantics 변경
6. 명시적 필요 없이 persistent 파생 에이전트 문서(8) 생성
7. 외부 보조 스킬(12)을 자동 실행 대상으로 만들기
8. Artifact relation, impact candidate, stale candidate, metadata gap을 깊게 해석하기

<!-- key: id=key.standard.skill.author.standard-relations refs=key.role.author key.doc.standard key.topic.skill-contract key.standard.subagent -->
## 기준 관계

1. Parent 기준서: `../../01_key-project-standard.md`
2. 상위 규칙: `STD-KEYSTONE-001`, `STD-KEYSTONE-003`, `STD-KEYSTONE-004`,
   `STD-KEYSTONE-006`, `STD-KEYSTONE-007`, `STD-KEYSTONE-008`,
   `STD-KEYSTONE-010`, `STD-KEYSTONE-011`, `STD-KEYSTONE-012`,
   `STD-KEYSTONE-013`, `STD-KEYSTONE-015`, `STD-KEYSTONE-016`,
   `STD-KEYSTONE-017`, `STD-KEYSTONE-018`, `STD-KEYSTONE-019`,
   `STD-KEYSTONE-020`, `STD-KEYSTONE-021`, `STD-KEYSTONE-022`,
   `STD-KEYSTONE-023`, `STD-KEYSTONE-024`, `STD-KEYSTONE-025`,
   `STD-KEYSTONE-027`, `STD-KEYSTONE-030`, `STD-KEYSTONE-032`, `STD-KEYSTONE-042`,
   `STD-KEYSTONE-043`, `STD-KEYSTONE-045`, `STD-KEYSTONE-052`, `STD-KEYSTONE-060`,
   `STD-KEYSTONE-062`
3. 관련 기준서: `../../subagents/key-standard-subagents.md`
4. 관련 결정(6): `00_docs/works/key-decisions.md`
5. 충돌 처리: 이 기준서와 parent 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의
   결정(6)을 받는다. 결정 전까지는 parent 기준서를 임시 우선 기준으로 삼는다.
6. 상세화 범위: 이 기준서는 `STD-KEYSTONE-042`의 Author behavior를 구현 가능한 수준으로
   상세화한다.

<!-- key: id=key.standard.skill.author.skill-identity refs=key.role.author key.topic.skill-contract -->
## Skill identity

1. Skill name: `keystone-author`
2. Primary role: 원천 문서(2) 작성과 승인된 revision
3. Primary user: main agent 또는 Keystone 원천 문서(2)를 작성하려는 사용자
4. Output authority: Author가 수정한 원천 문서(2)는 사용자 또는 main이 수락한 범위 안에서
   권위를 가진다.

<!-- key: id=key.standard.skill.author.runtime-authority refs=key.role.author key.topic.runtime-independence key.topic.initialization -->
## 런타임 권위와 초기화 경계

이 문서는 Keystone 저장소에서 Author를 개발·검수하기 위한 원천 명세다. 배포된 Author의
실행 계약은 설치된 skill package 안에서 완결되어야 하며, 소비 프로젝트의
`standards/skills/author/**`를 required input으로 요구하지 않는다.

Author는 Keystone 문서 작성의 핵심 스킬이다. `uninitialized` 또는 `partial`을 발견하면
사용자에게 초기화 또는 repair 후 계속할지 한 번 확인하고 Init handoff 뒤 원래 작성 요청으로
resume한다. 같은 대화와 범위에서 이미 동의했다면 반복 확인하지 않는다.

<!-- key: id=key.standard.skill.author.trigger-condition refs=key.role.author key.topic.document-authoring key.topic.work-creation key.topic.author-edit-contract key.topic.doc-helper key.standard.subagent -->
## Trigger condition

`keystone-author`는 다음 경우에 사용할 수 있다.

1. 새 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 기록을 작성해야 한다.
2. 기존 기준서(3)나 작업서(4)를 수락된 방향에 맞춰 수정해야 한다.
3. 큰 기준서(3)를 parent-child 구조로 나누거나 child 기준서를 추가해야 한다.
4. 수락된 `keystone-clarify` decision summary와 edit plan을 원천 문서(2)에 반영해야
   한다.
5. 작업서(4) step을 Goal unit으로 정리해 coordinator가 Current Step Brief, Context Pack,
   worker handoff, reviewer focus를 도출할 수 있게 해야 한다.
6. 문서 변경에 따라 index, context map, progress, 결정(6) 기록을 함께 갱신해야 한다.
7. 문서 변경이 capability, code, config, schema, API, test artifact에 미칠 후보 영향을 Change Set(17)이나
   Linker handoff seed로 남겨야 한다.
8. 큰 문서 수정 전에 대상, 범위, 영향 문서, 검증 기준을 Author Edit Contract로 정리해야
   한다.
9. 승인된 문서 수정 범위 안에서 subagent 기준서의 `document_edit` purpose worker를 사용할지
   판단해야 한다.
10. 기존 문서 구조가 너무 크거나 흩어져 있어 수락된 범위 안에서 정리해야 한다.
11. 큰 문서 변경, code 영향이 있는 문서 변경, 여러 artifact에 걸친 변경을 추적 가능한 Change
    Set(17)으로 정리해야 한다.
12. Clarify 답변을 작업서 위치의 대주제별 명확화 로그(21)에 기록하거나, 현재 그룹의 질문이 모두
    끝난 뒤 통합 edit plan을 관련 원천 문서(2)에 한 번 적용해야 한다.

<!-- key: id=key.standard.skill.author.non-trigger-condition refs=key.role.author key.topic.skill-contract -->
## Non-trigger condition

`keystone-author`는 다음 경우에 사용하지 않는다.

1. 질문과 선택지를 통해 high-impact policy나 scope를 먼저 결정해야 한다.
2. 현재 요청과 관련된 문서를 read-only로 찾거나 요약하기만 하면 된다.
3. Report, review, verification, acceptance가 이어지는 formal workflow를 조율해야 한다.
4. 구현 code, config, schema, API, test, build, generated/codegen artifact를 수정해야 한다.
5. 문서 변경 대상과 승인 범위가 불명확하다.
6. 민감한 정보, local-only path, private data를 기록해야 할 수 있지만 정책이 불명확하다.
7. 현재 작업이 다른 문서에 영향이 없는 현재 문서의 단순 오탈자 수정이고 별도 Author Edit
   Contract가 필요하지 않다.

<!-- key: id=key.standard.skill.author.required-input refs=key.role.author key.topic.document-authoring key.standard.subagent -->
## Required input

Author는 다음 input을 사용할 수 있어야 한다.

1. 사용자 요청 또는 main이 수락한 edit instruction
2. 존재하는 설정된 document root(1), 또는 Init handoff에 필요한 초기화 상태
3. 적용할 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 기록
4. 필요한 경우 수락된 `keystone-clarify` decision summary, edit plan,
   decision_completeness_check, decision_recording_hint, modularization_decision
5. 변경할 document section 또는 새 문서의 목적
6. 승인된 scope와 acceptance boundary
7. 현재 workspace state와 existing-change risk
8. 관련 capability, code, config, schema, API, test artifact 후보 또는 impact seed
9. 필요한 경우 `keystone-linker` report 또는 Linker handoff seed
10. 위임이 필요한 경우 사용자 허락과 실행 환경이 제공하는 isolation/concurrency 조건
11. 복수 surface나 권한 경계가 있어 명시적으로 남긴 경우 routing context
12. 명확화 로그(21)를 갱신하는 경우 작업서 위치, 대주제 log path, group/question ref, 실제 질문,
    답변과 답변일시

Input이 부족하고 잘못된 문서 변경으로 이어질 위험이 있으면 Author는 수정하지 않고
main/user에게 결정(6)을 요청하거나 `keystone-clarify`가 다룰 topic으로 보고해야 한다.

<!-- key: id=key.standard.skill.author.common-workflow refs=key.role.author key.topic.document-authoring key.topic.impact-review key.topic.author-edit-contract key.topic.doc-helper key.standard.subagent key.topic.artifact-graph -->
## Common workflow

Author는 작업 mode와 무관하게 다음 순서를 따른다.

1. 초기화 상태와 설정된 document root(1)를 확인한다. `uninitialized` 또는 `partial`이면
   동의를 한 번 확인하고 Init handoff 뒤 이 workflow로 resume한다.
2. 관련 parent 기준서와 child 기준서를 읽어 적용 규칙을 확인한다.
3. 요청이 create, revise, clarify-apply, normalize, progress update 중 무엇인지 정한다.
4. 변경 대상 원천 문서(2)와 section 또는 승인된 명확화 로그(21) entry를 식별한다.
5. 대상이 원천 문서인지 비권위 Work attachment인지 구분한다. 복수 surface나 권한 경계가 있으면
   필요한 routing context를 명시적으로 남긴다.
6. 승인 범위와 impact update 대상이 명확한지 확인한다.
7. High-impact 결정(6)이 부족하면 문서 수정을 멈추고 main/user에게 결정(6)을 요청하거나
   `keystone-clarify`가 다룰 topic으로 보고한다.
8. 변경이 큰 경우 Author Edit Contract로 대상 문서, section, 승인 범위, 영향 문서, 검증
   기준을 정리한다.
9. 현재 대상 문서 안의 단순 오탈자처럼 의미 변화와 외부 영향이 객관적으로 없는 수정은
   직접 처리할 수 있다.
10. 승인된 변경이 현재 문서 또는 영향이 명확한 소수 문서에 국한되면 Author가 직접 수정할
   수 있다.
11. 영향 후보가 여러 원천 문서(2)에 걸치거나 수정 누락 시 문서 간 불일치가 생길 수 있으면
    `investigate` worker로 후보를 조사하거나 `document_edit` worker 사용 여부를 판단한다.
12. `document_edit` worker는 Author Edit Contract 안에서 필요한 관련 문서만 수정한다. 연결된
    문서라는 이유만으로 모두 수정하지 않는다.
13. 위임이 유용하면 사용자에게 위임 여부를 물을 수 있다. 허락되면 실행 isolation,
    worktree와 concurrency는 주입된 skill 또는 host 환경의 계약을 따른다.
14. Reviewer/verifier, 여러 작업자 또는 formal report acceptance가 필요하면 Author Edit
    Contract를 Coordinator에 넘길 수 있으며 Coordinator 허락 범위를 확인한다.
15. Helper를 사용하더라도 subagent 기준서의 공통 경계를 따르며 report acceptance,
    reviewer/verifier orchestration, progress accepted 처리는 소유하지 않는다.
16. 승인된 범위 안에서만 원천 문서(2)를 수정한다.
17. 필요한 index, context map, progress, 결정(6) 기록을 함께 검토한다.
18. 키메타(9)가 있는 경우 같은 `key.id`를 참조하는 문서를 impact candidate로
    검토한다.
19. 코드 앵커(18) typed relation이나 capability(16)가 있는 경우 관련 code/config/schema/API/test
    artifact를 직접 확정하지 않고 Linker handoff seed 또는 Linker report requirement로 남긴다.
20. 큰 변경이나 문서-code-test 동시 영향이 있는 변경은 Change Set(17)을 작성하거나 갱신한다.
21. Code, config, schema, API, test 수정이 필요하면 직접 수정하지 않고 Main direct 또는 사용자
    허락을 받은 Coordinator가 처리할 next action으로 남긴다.
22. 문서 link, 용어, 구조, Markdown 형식을 검증한다.
23. 변경 파일, 적용한 결정(6), 검증 결과, 남은 risk를 보고한다.

Author Edit Contract는 다음 shape을 우선 사용한다.

```yaml
author_edit_contract:
  contract_id:
  accepted_instruction:
  target_documents:
    - path:
      sections:
      allowed_change:
  affected_document_candidates:
    - path:
      reason:
      action: edit | inspect_only | exclude
  forbidden_changes:
    - scope_change
    - acceptance_criteria_change
    - status_semantics_change
    - code_change
  progress_update_policy:
    may_update_progress: true | false
    forbidden_statuses_before_main_acceptance:
      - accepted
      - complete
  verification:
    - check_index_links
    - check_context_map_if_affected
    - check_decision_record_if_affected
```

Author Edit Contract는 다음 원칙을 따른다.

1. `target_documents`는 직접 수정이 승인된 원천 문서(2)만 포함한다.
2. `affected_document_candidates`는 검토 후보이며 자동 수정 권한이 아니다.
3. `action: edit`은 승인 범위와 의미 영향이 명확한 경우에만 사용한다.
4. `action: inspect_only`는 related evidence 확인만 허용한다.
5. `action: exclude`는 현재 범위에서 수정하지 않는 이유를 함께 남긴다.
6. `progress_update_policy`는 Main acceptance 전 `accepted` 또는 `complete` 갱신 금지를
   약화하지 않는다.

<!-- key: id=key.standard.skill.author.mode-contract refs=key.role.author key.topic.document-authoring key.contract.output -->
## Mode contract

<!-- key: id=key.standard.skill.author.create-mode refs=key.role.author key.topic.document-authoring key.topic.work-creation -->
### Create Mode

Create Mode는 새 원천 문서(2)를 만든다.

1. 기준서(3)는 `standards/` tree와 `STD-KEYSTONE-011`, `STD-KEYSTONE-013`을 따른다.
2. 작업서(4)는 `works/` tree와 `STD-KEYSTONE-011`, `STD-KEYSTONE-013`,
   `STD-KEYSTONE-022`, `STD-KEYSTONE-026`을 따른다.
3. 새 작업 문서는 active work round 안에 만든다.
4. 새 work round를 만들면 round folder와 `00_key-index.md`를 함께 만든다.
5. Work는 기본적으로 Round 작업서 안에 구분한다. 별도 폴더로 분리한 경우에만 node
   `00_key-index.md`를 함께 만든다. Work 없는 작업에 빈 Work node를 만들지 않는다.
6. Minimal document set을 먼저 만들고, scope, decisions, coordination 문서는 필요할 때만
   추가한다.
7. 파생 에이전트 문서(8)는 `STD-KEYSTONE-016`의 생성 및 업데이트 조건을 만족할 때만
   추가하거나 업데이트한다.
8. Parent 기준서는 상세 규칙을 반복하지 않고 feature 이름, 짧은 설명, child link를 둔다.
9. Child 기준서는 trigger, non-trigger, input, output, workflow, verification, stop
   condition을 구현 가능한 수준으로 작성한다.
10. 새 원천 문서에는 생성 시점의 `created_at`을 기록하고 이후 revision에서 바꾸지 않는다.
11. 새 결정 기록에는 결정이 확정된 `결정일`을 기록한다.

<!-- key: id=key.standard.skill.author.revise-mode refs=key.role.author key.topic.document-authoring key.topic.impact-review -->
### Revise Mode

Revise Mode는 기존 원천 문서(2)를 수정한다.

1. 수정 대상 문서와 section이 명확해야 한다.
2. 승인된 요청과 관계없는 문장 다듬기, 정리, renaming은 하지 않는다.
3. 이미 다른 STD가 같은 책임을 다루면 새 규칙을 만들지 않고 해당 STD를 참조한다.
4. 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 기록 사이에 영향이 있으면
   `STD-KEYSTONE-023`에 따라 함께 검토한다.
5. 의미 변경이 불확실하면 수정하지 않고 보고한다.
6. 의미가 바뀌면 approval을 `pending`으로 돌리고 현재 `approval.accepted_at`을 제거한다.
   Main이 변경 결과를 다시 수락하면 새 `accepted_at`을 기록한다.
7. 의미 없는 형식 변경은 근거를 기록하고 기존 approval과 `accepted_at`을 유지할 수 있다.
8. 일반적인 `updated_at`은 추가하거나 갱신하지 않는다.

<!-- key: id=key.standard.skill.author.clarify-apply-mode refs=key.role.author key.role.clarify key.topic.document-authoring -->
### Clarify-Apply Mode

Clarify-Apply Mode는 수락된 Clarify result를 문서에 반영한다.

1. 그룹 범위의 원천 문서를 적용하려면 decision summary, rationale, working assumptions, affected documents,
   affected_artifact_candidates, decision_completeness_check, decision_recording_hint, edit plan이
   충분해야 한다.
2. Author는 Clarify result를 새 decision으로 확정하지 않는다.
3. `decision_completeness_check.author_edit_ready`가 `false`이면 Author는 원천 문서를 적용하지
   않고 Clarify 또는 main/user 결정(6) 보강을 요청한다. 이미 받은 답변의 lightweight log append는
   source application과 분리해 수행할 수 있다.
4. Edit plan 밖의 scope나 acceptance criteria는 바꾸지 않는다.
5. 적용 중 충돌이 발견되면 중단하고 main/user 결정(6)을 요청한다.
6. 적용 후 필요한 경우 결정(6) 기록과 진행 기록(5)을 갱신한다.
   새 결정을 기록한다면 수락된 결정의 `결정일`을 함께 기록한다.
7. 다른 문서와 함께 맞춰야 하는 원천 문서(2) 수정은 Clarify가 아니라 Author가 담당한다.
8. Clarify는 원천 문서를 직접 수정하지 않는다. 단순 오탈자는 Main 또는 Author가 현재 위임
   범위 안에서 처리한다.
9. 수락된 modularization decision이 있으면 Author는 승인 범위 안에서 관련 기준서(3),
   작업서(4), 결정(6) 기록, Change Set(17), affected capability seed, Linker report reference,
   excluded reuse candidate를 반영한다.
10. Modularization decision이 `investigate_first` 또는 `needs_linker_report`이면 Author는
    code/config/schema/API/test 수정 지시를 만들지 않고 필요한 Linker 또는 Coordinator
    investigation을 next action으로 남긴다.

<!-- key: id=key.standard.skill.author.clarification-log-application kind=claim refs=key.role.author key.role.clarify key.topic.question-flow key.topic.document-authoring key.topic.work-recovery -->
## Clarification log와 그룹 적용

Author는 답변별 log append와 그룹 종료별 원천 문서 적용을 서로 다른 write boundary로 처리한다.

1. 기록 대상 질답의 최초 시작 시 첫 질문을 제시하기 전에 로그와 질문 entry를 만든다.
   Round 또는 Work 작업서가 존재하거나 승인 범위에서 함께 만들어지는 경우,
   `<작업서 위치>/clarify/{YYYYMMDDTHHmmssZ}-{topic-slug}.md`를 만든다. Timestamp는 UTC를 사용하고
   같은 대주제의 이후 그룹은 같은 파일에 추가한다. 질문 하나라도 중요한 결정·후속 근거이면
   기록하며 낮은 중요성의 일반 질답에는 로그를 강제하지 않는다. 작업서나 별도로 승인된
   기록 위치가 없으면 위치·권한 미해결을 반환하고 임의 경로나 Work를 만들지 않는다.
2. 명확화 로그(21)는 원천 문서가 아닌 추적되는 작업 attachment다. Key prefix, lifecycle,
   approval, work status, decision 또는 completion metadata를 요구하지 않는다.
3. 기본 구조는 대주제 `#`, 수정 범위 `## G01 - {제목}`, 질문 `### Q01 - {요약}`과 `질문`,
   `답변`, `답변일시`다. 빈 답변은 미응답을 뜻한다. 확인이 필요한 해석은 답변에 `[확인 대기]`,
   폐기 질문은 `[폐기]`와 원인 질문·이유를 표시한다. 이 표시는 작업 상태·평가가 아니다.
4. 질문 답변을 받을 때마다 현재 파일 bytes와 group/question locator를 확인하고 해당 entry만
   저장한다. 예·아니요나 명확한 선택은 재확인하지 않는다. 해석이 필요하면 caller가 제시할
   해석을 확인 대기로 저장한 뒤 확인 질문을 하고, 확인·명확한 교정은 같은 entry를 확정한다.
   같은 답변을 중복 기록하거나 별도 remaining-question 목록을 만들지 않는다.
5. 실제 원천 문서에 영향을 준 질문에만 heading 바로 앞의 선택적 키메타(9)를 둘 수 있다.
   키메타는 탐색 후보이며 source authority, edit permission, 평가 또는 acceptance evidence가 아니다.
6. `Group Decision`, `Author Application`, 질문 충분성, 평가, 점수, 그룹 완료와 작업 상태 field를
   추가하지 않는다. 작업서에는 Q&A가 scope·criterion·결정에 실질적으로 영향을 준 경우에만
   log link를 추가한다.
7. Lightweight log append는 대상 path와 해당 question entry를 다시 읽는 것으로 검증한다.
   Caller는 저장 성공을 받은 뒤 다음 질문으로 진행한다. 실패·충돌 시 받은 답변과 locator를
   보존하고 다음 질문·의존 원문 적용을 멈추며 같은 entry의 저장을 재개한다. 재시도 시 이미
   반영된 entry면 중복 append하지 않고 성공을 반환한다. 이것만 수행했을 때 Progress,
   Work State, graph reconstruction, package/repository test 또는 원천 문서 application을 실행하지 않는다.
8. 현재 그룹의 material question이 모두 끝나고 통합 `author_edit_ready: true` handoff가 오면
   그 그룹의 affected source document 범위만 한 번 적용한다. 다른 그룹의 질문이나 미래 edit
   plan을 함께 반영하지 않는다.
9. Group source application은 일반 Clarify-Apply 검증과 impact review를 따른다. 적용 결과를
   caller에 반환하면 caller가 다음 그룹 또는 모든 그룹 뒤의 원래 작업을 resume한다.
10. Clarify는 log나 원천 문서를 직접 수정하지 않는다. Caller가 Author를 호출하며 사용자에게
    매 답변이나 그룹마다 스킬 재호출을 요구하지 않는다.
11. 기본 질문 ID는 파일 내 유일하게 증가한다. 파생에는 `Q01-A`, `Q01-B`, … `Q01-AA`의
    대문자 Excel-column suffix를 쓰며 재파생도 Q01의 다음 suffix와 직접 원인 링크로 표현한다.
    기존 ID 재번호화·재사용은 하지 않는다. 같은 그룹이면 관련 질문 옆에, 다른 그룹이면
    실제 적용 그룹에 배치하고 원인 링크를 보존한다.
12. 질문 구조 변경은 폐기와 추가만 허용한다. 미응답·확인 대기 질문을 폐기하면 기존 질문과
    필요한 대기 해석을 보존하고 답변에 폐기 이유·원인 질문을 기록한다. 대체 질문에는 대체
    대상도 연결한다. 단순 파생 추가는 원 질문을 폐기하지 않는다. 확정 답변은 덮어쓰지 않고
    새 질문·답변에서 변경 의도를 연결하며 이미 적용된 원문의 영향은 caller가 재검토한다.
13. 답변일시는 실제 사용자 답변 시각, 해석 확인 후에는 확인 시각이다. 정확한 과거 시각이
    없으면 `미상`으로 둔다. AI의 폐기 설명은 사용자 답변이 아니며 이전 답변 없는 폐기 항목의
    답변일시는 비워 둔다. 기록 시각을 과거 답변 시각으로 꾸미지 않는다.
14. 편집 전후 대상 entry 확인은 필수지만 세션 재개·상태 조회마다 전체 로그를 읽지 않는다.
    의미 복구가 필요할 때만 관련 부분을 읽고, 확정 답변 반복 질문·폐기 질문의 미응답 복구를
    피한다. 로그 자체를 결정·진행 상태의 권위로 사용하지 않는다.

<!-- key: id=key.standard.skill.author.normalize-mode refs=key.role.author key.topic.document-system -->
### Normalize Mode

Normalize Mode는 수락된 범위 안에서 문서 구조를 정리한다.

1. 큰 기준서(3)는 의미 있는 parent/child 구조로 나눌 수 있다.
2. Parent 기준서는 navigation과 공통 규칙에 집중한다.
3. Child 기준서는 최종 상세 규칙을 담는다.
4. 항상 함께 읽어야 하는 문서는 억지로 나누지 않는다.
5. 많은 작은 파일을 만들어 main이 context pack을 구성하기 어렵게 하지 않는다.
6. 기존 path 변경, migration, rename은 별도 승인이 있을 때만 수행한다.

<!-- key: id=key.standard.skill.author.progress-update-mode refs=key.role.author key.topic.progress-update -->
### Progress Update Mode

Progress Update Mode는 문서 작업의 진행 기록(5)을 갱신한다.

1. 기록 대상:
   - 기준서(3), 작업서(4), 결정(6) 기록, child 기준서 초안처럼 작업 복구에 의미 있는 문서
     단위 변화
   - 새 문서 초안 작성, 검토 필요, 반영 완료, 수락 완료처럼 workflow state를 복구하는 변화
   - 수락된 Clarify result를 원천 문서(2)에 적용한 결과
2. 기록하지 않는 대상:
   - 현재 문서 안의 단순 오탈자
   - 문장 하나의 미세한 표현 수정
   - 의미 변화 없는 formatting
3. Completion evidence가 있으면 `work_status: complete`로 표시할 수 있지만 Main acceptance 없이
   `approval.state: accepted`로 표시하지 않는다.
4. Worker `DONE`만으로 진행 상태를 완료로 바꾸지 않는다.
5. Acceptance state, status semantics, `active_steps`가 바뀌면 명시적으로 보고한다.
6. Progress update가 작업서(4)의 scope나 completion criteria를 바꾸면 중단한다.

<!-- key: id=key.standard.skill.author.progress-ownership kind=claim refs=key.role.author key.topic.progress-update key.topic.work-recovery key.topic.acceptance -->
## Work/Step Progress ownership

아래 규칙은 기존 Work node 기반 저장의 호환 계약이다. 선택적 Work의 논리적 소유는
Project STD-KEYSTONE-026을 따른다. Work가 없으면 Round가 전체 목표·완료 조건을 직접
소유하고 Step은 Round에 직접 속한다. 이 정의만으로 기존 Progress를 삭제·이전하거나
R024 저장 wire를 바꾸지 않는다. 구현·전환 전까지 기존 source 복구를 유지한다.

1. Aggregate Work Progress인 `key-progress.md`는 Work 전체의 현재 `work_status`,
   `approval.state`, 선택적 `finalization.state`, 실제 증거와 resume point를 소유하는
   `aggregate Progress authority`다.
2. Step Progress인 `key-progress-{step-slug}.md`는 하나의 `step_ref`와 그 Step의
   `work_status`, `approval.state`, 선택적 `finalization.state`, 실행·검증 증거와 resume point를
   소유한다.
3. Work와 현재 Step의 상태 tuple이 같고 독립 보존할 수용 Step이 없으면 `key-progress.md` 하나가
   `step_ref`를 함께 가진 compatible combined record일 수 있다. 두 상태가 갈라질 때만 Aggregate
   Work Progress와 Step Progress를 분리하며 모든 Step마다 파일을 미리 만들지 않는다.
4. Step이 `complete/accepted`가 됐지만 Work가 계속 `in_progress/pending`이면 Step 결과를
   `key-progress-{step-slug}.md`에 기록하고 Aggregate Work Progress를 Step 상태로 덮어쓰지 않는다.
5. Step Progress가 하나라도 존재하면 Aggregate Work Progress는 `step_ref`를 갖지 않는다.
   과거 완료 기록을 이 규칙 때문에 일괄 rewrite하지 않는다.
6. Work Index의 `work_status`·`approval`과 Context Map·Index의 `global_state`는
   `optional compatibility projection`이며 생략할 수 있다. 존재하는 값이 aggregate Progress나
   canonical Work State와 다르면 stale projection으로 진단하고 source authority를 덮어쓰지 않는다.
7. Work State는 Work identity를 Work Index에서, current Work state를 Aggregate Progress에서,
   active Step을 compatible combined record 또는 Step Progress에서 복구한다. Aggregate Progress가
   없는 legacy Work에만 Work Index state fallback을 허용한다.
8. 기본 문서 수정과 recovery를 위해 새 persistent projection artifact를 만들지 않는다. 별도
   rendered view가 실제로 필요할 때만 bounded marker와 freshness binding을 가진 선택적 generated
   block을 사용하고 사람이 작성한 history·rationale 영역을 덮어쓰지 않는다.

<!-- key: id=key.standard.skill.author.section refs=key.role.author key.doc.standard key.topic.document-authoring -->
## 기준서 작성 규칙

기준서(3)를 작성하거나 수정할 때는 다음 규칙을 따른다.

1. 짧은 목적 문단으로 문서가 다루는 대상을 먼저 밝힌다.
2. 적용 범위와 적용하지 않는 범위를 분리한다.
3. Parent 기준서에는 공통 규칙과 child link만 남긴다.
4. Child 기준서에는 skill-specific 상세 계약을 둔다.
5. 용어는 `## 표준 용어`의 첨자 규칙을 따른다.
6. 긴 문단보다 번호 목록과 `이름: 설명` 구조를 우선한다.
7. 기계적으로 참조되는 ID, path, status, field name은 기존 literal 값을 유지한다.
8. 관련 active work가 있으면 기준서 끝이나 index에서 link한다.

<!-- key: id=key.standard.skill.author.work-order-writing-rules refs=key.role.author key.topic.work-creation key.topic.document-authoring -->
## 작업서 작성 규칙

작업서(4)를 작성하거나 수정할 때는 다음 규칙을 따른다.

1. 작업서는 TODO list가 아니라 실행 계획이어야 한다.
2. 각 step은 Goal unit으로 작성한다.
3. 필수 field는 `STD-KEYSTONE-022`을 따른다.
4. Completion criteria는 사람이 검토할 수 있을 만큼 구체적이어야 한다.
5. Stop Conditions는 scope change, missing context, verification gap, high-risk change를
   드러내야 한다.
6. Verification은 기준서가 요구하는 검증을 약화하지 않는다.
7. Context Pack Seed는 main이 필요한 문서만 추출할 수 있게 작성한다.
8. Review points는 reviewer focus로 변환할 수 있어야 한다.

### 선택적 Work·Task 작성

1. 부모·하위 Round 생성은 사용자 결정이 필요하다. AI가 필요성을 발견하면 이유·범위를
   설명해 권유하고 기다린다. 기존 실행 승인을 새 Round 생성 승인으로 확대하지 않는다.
2. Work는 사용자 지정 또는 AI의 범위 내 판단으로 구성한다. AI 생성 후 기준·이유·범위와
   Round·Work·Step 관계 및 실제 의존성을 안내한다. 독립 결과·완료 조건을 구분할 실익이
   없으면 Work를 생략한다. 생성은 미승인 실행·범위 확장의 허가가 아니다.
3. Work는 Round 작업서 안의 section이 기본이다. 내용 크기·독립 편집·참조 필요로 분리할 때만
   별도 작업서를 만들며 동일 계약을 양쪽에 복제하지 않는다. Round에서 분리 문서로 안내한다.
   Step·Task 때문에 별도 파일을 강제하지 않는다.
4. Work 없는 경우 Round 작업서에 전체 목표·범위·완료 조건과 Step 소속을 기록한다.
   Work가 있으면 각 과제의 목표·범위·완료 조건·소속 Step을 명시한다. 새 Step 번호는 local
   Round 안에서 중복하지 않으며 기존 식별자·이력은 이동·재번호화하지 않는다.
5. Task는 AI가 Step 안에서 필요할 때 생성·수정·생략한다. 재개에 필요한 내용만 Step 기록에
   남기고 독립 상태·수락·필수 ID·파일·전수 이력을 요구하지 않는다. Task 완료가 Step의
   완료 조건·검증·수락을 대체하지 않는다.
6. 이 절의 실제 생성·복구 적용은 Project STD-KEYSTONE-026의 R025 구현 적용 경계를 따른다.
   저장·runtime 지원 전에는 기존 source를 유지하고 필요한 후속 구현 범위를 보고한다.

<!-- key: id=key.standard.skill.author.round-creation-execution-boundary kind=claim refs=key.role.author key.topic.work-creation key.topic.work-round key.topic.work-sequence key.topic.verification key.boundary.scope-control key.work.decisions.dec-works-034 key.work.decisions.dec-works-036 -->
## Round 생성과 실행 경계

1. 사용자-facing 설명은 `Round 생성`과 `Step 구성`을 우선한다. Work Order는 그 실행 계약을
   보존하는 원천 문서를 가리킬 때만 사용한다.
2. Round 생성 요청만 있으면 Round Index, Work Order, Progress와 필요한 navigation source를
   `planned / pending`, Active Step 없음으로 작성하고 결과를 보고한 뒤 중단한다.
3. 계획 승인, Round 내용 수용, 단순한 긍정, 생성 결과 확인과 생성 뒤 추가 문서 수정은 실행
   승인이 아니다. 추가 문서 수정 요청은 승인된 문서 범위만 수정한다.
4. 같은 요청에 `작업서 생성 이후 작업을 바로 진행해주세요`, `만들고 바로 진행해 주세요`가
   포함되거나 후속 메시지에서 Round·Step·구현 진행이 명시되면 생성 뒤 첫 실행 가능 Step을
   이어서 진행할 수 있다.
5. 실행 승인 의미가 불명확하면 구현으로 확대하지 않고 Round를 planned 상태로 유지한다.
6. Round에 유지될 production code, config, schema, API, generated/codegen 또는 skill source
   구현이 있으면 첫 production 구현 Step보다 앞에 기준서 정합화 Step을 구성한다.
7. 기준서 정합화는 intended behavior, scope, boundary, verification expectation과 기존 accepted
   기준서의 충분성을 확인한다. 의미가 부족하면 기준서를 수정하고, 이미 충분하면 의미 없는
   수정 대신 `no_change`와 근거를 기록한다.
8. Round 완료 전 accepted 기준서 의미, 실제 구현과 필요한 verification evidence의 정합성을
   확인한다.
9. 위 세 핵심 제약을 만족하면 Step 이름·개수, 구현·검증 분할, 독립 Step 병행과
   production·문서·조사 Round topology는 Goal에 맞게 구성한다. 하나의 고정 pipeline을 강제하지
   않는다.
10. 문서 전용 Round에는 구현 Step을 만들지 않는다. 조사·실험 Round가 production 구현을
    수락하지 않으면 조사와 사용자 판단 대기 구조를 사용할 수 있다.
11. 구현 중 계획의 의미 변경이나 기준 충돌이 발견되면 `STD-KEYSTONE-062`에 따라 관련 기준의
    재검토 결과를 남긴다. 기준서 변경이 필요하면 추가 정합화 Step을 작업서에 구성하고,
    영향을 받는 구현의 보류·재개 조건과 실제 실행 순서를 명시한다. 기존 Step의 번호를 밀어
    재부여하거나 완료 이력을 덮어쓰지 않는다. 관련 구현은 추가 Step의 검증·수락 뒤 재개한다.
12. 추가 Step은 Goal·Scope·완료 조건·검증 등 기존 Step 계약을 따른다. 작업서와 수행 기록에서
    변경 원인·이유, 대상 조항, 변경 전후 의미, 관련 구현 Step과 검증·수락 근거를 복구할 수
    있어야 한다. 현재 상태는 적용 중인 상태 소유 계약에 따르며 별도 상태 체계를 만들지 않는다.
13. 기준서 변경이 필요 없으면 해당 작업 기록에 검토한 기준과 이유를 남긴다. 매 작업서 수정마다
    새 Step을 만들지 않으며, 사용자에게는 추가 Step 또는 변경 불필요 판단과 관련 구현의
    보류·재개 여부를 요약해 알린다. 요약 출력만으로 영속 기록을 대신하지 않는다.

<!-- key: id=key.standard.skill.author.child-session-naming kind=claim refs=key.role.author key.topic.work-creation key.topic.work-round key.topic.work-sequence key.boundary.scope-control key.work.decisions.dec-works-034 -->
## 하위 세션 식별자 생성

1. `-`는 직전 Round 또는 Step의 직접 하위 세션 경계로만 사용한다.
2. 새 child Round는 `R015-A`, 새 child Step은 `R015/S01-A` 형식으로 만든다. Child Round의
   Step `R015-A/S01`에 직접 child Step이 필요하면 `R015-A/S01-A`로 표기한다.
3. Suffix는 Excel column과 같은 bijective base-26 대문자 영문 번호를 사용한다. 증가 순서는
   `A → Z → AA → AZ → BA → … → ZZ → AAA`다.
4. 새 suffix에 숫자, 영문·숫자 혼합 또는 의미 문자열을 사용하지 않는다. 의미는 title과
   Goal에 기록한다.
5. 같은 직전 parent 안에서 suffix를 중복·재사용하지 않고 기존 ID를 재번호화하지 않는다.
6. 새 child Round directory는 ref suffix의 대소문자를 보존해 parent folder 아래 `r015-AA/`로
   만든다. Parent Index의 `child_rounds`에 membership를 기록한다.
7. 기존 `R010-a`와 단일 소문자 directory는 historical compatibility로만 읽으며 rename하거나
   대문자로 migration하지 않는다. 새 식별자 생성에는 사용하지 않는다.
8. Parent→direct child의 2단계 Round 제한과 parent/child 상태·수락 권위는 변경하지 않는다.

<!-- key: id=key.standard.skill.author.work-order-creation-standard refs=key.role.author key.topic.work-creation key.topic.document-system -->
## 작업서 생성 표준

새 작업서(4)를 만들 때는 다음 표준을 따른다.

1. 작업서는 기준서 tree에 종속되지 않는다.
2. 작업서는 작업 round 단위로 묶는다.
3. Work round folder는 `r{number}-{slug}` 형식을 사용한다. `r`은 round를 뜻한다.
4. 각 round 안의 실행 순서는 `S01`부터 다시 시작한다. `R000`은 최초 기준서가 없는
   Project Foundation round 이름으로만 예약한다.
5. 기준서별, 기능별, 구현 단계별, 검증 단계별로 독립 work를 만들 수 있다.
6. 각 work는 하나의 reviewable goal을 가져야 한다.
7. 작업서는 관련 기준서(3)를 참조하지만, 기준서 안에 실행 순서를 박지 않는다.
8. 실행 순서는 root works index가 아니라 active round의 `00_key-index.md`가 관리한다.
9. 독립 과제 구분의 실익이 없으면 Work를 만들지 않고 Round의 Step 또는 Step 내 Task로 표현한다.
10. Work는 기본적으로 Round 작업서 안에 둔다. 별도 파일·폴더와 index 분리는
    `선택적 Work·Task 작성` 및 Project STD-KEYSTONE-026을 따른다.
11. 결정(6) 기록은 여러 round에 영향을 주면 `works/key-decisions.md`에, 특정 round에만
    영향을 주면 해당 round의 `key-decisions.md`에, 특정 work node에만 영향을 주면 해당 work
    node의 `key-decisions.md`에 둔다.
12. 새 결정에는 `결정일: YYYY-MM-DD`를 기록하며 날짜만으로 결정 우선순위를 판단하지 않는다.
13. 작업서 생성 후 context map, root works index, round index의 link와 status drift를
    확인한다.
14. Round 생성과 실행 승인, production standards-first, closure verification와 topology 자율성은
    `Round 생성과 실행 경계`를 따른다.
15. 하위 Round·Step ref와 directory 생성은 `하위 세션 식별자 생성`을 따른다.

<!-- key: id=key.standard.skill.author.acceptance-finalization refs=key.role.author key.topic.acceptance key.topic.progress-update key.topic.verification -->
## Acceptance finalization

1. Main acceptance 직후 Author는 수락된 Step의 `work_status: complete`,
   `approval.state: accepted`와 acceptance date를 owning Work·Progress·index에 반영한다.
2. Round index, root works index와 Context Map의 `active_steps`를 같은 current source 상태로
   동기화하되, 형제·미래 Step을 자동 승인하지 않는다.
3. 미래 Step의 수행된 부분은 원인, 완료·남은 범위와 `status_effect: none`인
   `early_work`로 구분한다.
4. Progress에는 실제 상태·증거·resume point를 바꾸는 document, decision, standard, recovery,
   gate, residual risk와 namespace disposition만 남긴다. 영향이 없는 category를 열거하지 않는다.
5. Work/Step 상태가 바뀌면 repository-derived Work State를 실행하고 graph-relevant 의미가 바뀌면
   affected-scope graph validation을 실행한다. 진단이 있으면 지속 가능한 resume point를
   Progress에 남긴다.
6. Current success는 원천 문서 동기화, 상태 변경 시 Work State, graph-relevant 변경 시
   disposition/validation과 Main post-edit verification으로 판정한다. 새 finalization manifest,
   external evidence root, owner key 또는 HMAC receipt는 필수 prerequisite가 아니다.
7. 구 finalization schema v1-v6과 package validator는 historical input을 읽고 진단하는
   compatibility adapter로만 유지한다. 이 경로는 새 completion·apply·release authority를 만들지 않는다.
8. 과거 accepted/finalized evidence는 당시 이력으로 보존하고 current contract 변경으로
   성공·실패를 소급 변경하지 않는다.
9. 기준서는 정책 의미, Work Order는 Goal/Scope/criterion, Progress는 실제 상태·증거·resume point,
   index와 Context Map은 active pointer나 집계 상태가 바뀐 경우에만 수정한다.
10. 일반 문서 변경은 관련 문서 탐색, 승인 scope/diff 확인, 문서 구조와 직접 관련된 검증으로
    닫는다. Change Set, finalization manifest, receipt, snapshot 또는 acceptance-event를 기본
    산출물로 만들지 않는다.
11. Metadata/relation, Work State, 여러 surface의 contract가 함께 바뀔 때만 Linker affected-scope
    review, graph synchronization 또는 recovery 검증을 추가한다.
12. Package/installer/historical adapter 검증은 해당 surface가 바뀌거나 release 검증이 명시된
    경우에만 실행한다.

<!-- key: id=key.standard.skill.author.terminal-status-reconciliation kind=claim refs=key.role.author key.topic.acceptance key.topic.progress-update key.topic.work-recovery key.topic.verification -->
## Terminal status reconciliation

Author는 실제 상태 전이로 closure 후보가 생긴 경우에만 권위 source와 기존 current/navigation
projection을 bounded하게 대조한다.

1. Trigger는 `work_status`, `approval.state`, `round_status` 또는 `active_steps`의 실제 변경이다.
   상태가 바뀌지 않은 일반 문서 작성·수정에는 이 절차를 실행하지 않는다.
2. 먼저 owning Aggregate/Step Progress와 Round Index에서 전이된 상태와 실행 단위를 확인한다.
   Work Index, root works index와 Context Map은 존재할 때만 current/navigation projection 후보로
   취급하며 권위 source를 덮어쓰지 않는다.
3. 후보 탐색은 owning Round subtree, root works index, Context Map에서 전이된 Round/Step의 exact
   ref가 있는 부분으로 제한한다. Document root 전체를 전수 수정하거나 범용 Markdown table
   parser를 만들지 않는다.
4. Optional projection이 없으면 정상이다. 다만 존재하는 비역사적 current/navigation 요약이
   owning Progress·Round 상태와 다르면 stale conflict로 처리한다.
5. Historical Progress, acceptance evidence, as-of snapshot과 과거 진행 서술은 소급 수정하지
   않는다. 현재 요약과 historical 기록이 구분되지 않으면 자동 수정하지 않고 residual action으로
   남긴다.
6. Step 종료는 해당 Step Progress와 실제로 바뀐 aggregate/current projection만, Work 종료는
   Aggregate Progress와 존재하는 Work/Round projection만 대조한다.
7. Child Round 종료는 child-local Work·Progress·Index를 먼저 닫고 parent의 declared child gate만
   다시 평가한다. Child 종료만으로 root/Context의 parent Round 상태를 전이하지 않는다.
8. Parent Round 종료는 선언된 Step과 child Round가 모두 resolved + accepted인 경우에만 Round,
   root works index와 Context Map의 current/navigation 요약을 동기화한다.
9. 비역사적 projection conflict가 남으면 closure를 complete로 보고하지 않는다. 승인 범위 안에서
   고치거나 충돌 위치와 다음 action을 Progress에 남긴다.
10. 기본 검증은 exact-ref 검색, 변경 상태의 source 대조, 상태가 바뀐 경우의 Work State와 관련
    focused contract test다. 일반 종료에 full graph, package, repository 또는 installer 검증을
    강제하지 않는다.

<!-- key: id=key.standard.skill.author.resumable-finalization kind=claim refs=key.role.author key.role.reader key.topic.finalization key.topic.work-recovery key.topic.verification -->
## Resumable finalization

1. 현재 Progress가 `finalization.state: in_progress`이고 기록된 blocker와 resume point가 있을 때만
   재개 후보로 판정한다. `complete` 또는 `waived`인 finalization은 과거 blocker가 있어도 후보가 아니다.
2. Reader는 기록된 blocker 조건을 현재 source와 accepted contract에 대조해
   `blocked | resumable | unknown`으로 보고하고 source를 수정하지 않는다.
3. `resumable`은 blocker가 `source_change | contract_change`로 해소됐다는 구체 evidence와 Author가
   실행할 최소 current verification·source sync action을 포함한다.
4. Source 변경으로 해소됐으면 current targeted check만 실행한다. 계약 변경으로 예전 요구가 더
   이상 current authority가 아니면 그 사실을 확인하고 과거 실패는 history로 보존한다.
5. 재개만을 위해 과거 HMAC receipt, private key, external evidence root, snapshot이나 legacy
   manifest를 다시 만들지 않는다.
6. Blocker 해소는 acceptance나 completion이 아니다. Author는 current source sync, 적용되는 Work
   State 또는 focused verification과 Main post-edit review 전에는 자동으로 `complete`로 바꾸지 않는다.
7. Blocker가 남았거나 판정할 수 없으면 `in_progress`를 유지하고 실제 evidence나 다음 action이
   달라졌을 때만 Progress resume point를 갱신한다.

<!-- key: id=key.standard.skill.author.graph-synchronization refs=key.role.author key.role.linker key.topic.artifact-graph key.topic.keystone-metadata key.topic.change-set -->
## Document delta와 graph synchronization

승인 범위의 단일 문서 semantic/progress 수정은 Author direct-write lane에 남는다.
Graph synchronization이 `required`이면 Linker가 exact Author-owned transaction-v2 patch를 제공하고
Author가 자기 surface를 직접 적용한다. 어느 경로도 external application evidence, secret,
receipt를 current apply authority로 요구하지 않는다. Author는 transaction을 만들거나 scope를
확대하거나 direct-edit evidence를 Main acceptance로 바꾸지 않는다.

1. Author가 승인 범위에서 문서 의미나 독립 metadata item을 변경하면 path, locator, semantic
   summary와 raw-byte SHA-256 baseline을 가진 `document_delta`를 만든다.
2. Graph-relevant delta가 다른 source surface patch를 요구할 때만 Linker synchronization
   transaction을 시작한다. 단일 document surface 변경은 direct apply 뒤 index refresh로 끝내며,
   어느 경로도 Author scope, Coordinator permission 또는 acceptance를 만들지 않는다.
3. Linker만 canonical node/relation/provenance/locator/lifecycle mutation을 결정한다. Author는
   새 typed relation을 독자적으로 확정하거나 Linker mutation을 재해석하지 않는다.
4. Author는 Linker가 제안한 자기 surface의 exact patch를 문서 의미와 대조하고 patch별로
   `confirm | reject | needs_revision`과 evidence를 반환한다. 다른 surface를 attest하지 않는다.
5. Required patch는 모두 `confirm` 뒤 apply하고, ancillary optional은 선택해 apply할 때 반드시
   `confirm`한다. Apply 직전 source의 UTF-8 raw bytes SHA-256이 `baseline_digest`와 다르면 쓰지
   않고 `stale_baseline`을 반환한다.
6. Apply 결과는 `applied | failed | stale_baseline`과 resulting digest를 기록한다. 일부 성공은
   숨기지 않고 transaction을 `partially_applied`로 복구 가능하게 남긴다.
7. Rename/move에서 의미가 같으면 stable ID를 유지하고 locator만 바꾼다. 의미 변경·removal은
   Linker의 replacement/lifecycle mutation과 history evidence를 따른다.
8. Legacy metadata는 읽기 호환하되 새 metadata와 의미 변경된 metadata만 canonical form으로
   수렴한다. 기존 corpus를 bulk migration하지 않는다.
9. Author write 뒤 Linker가 source를 재구성하고 validator가 기계 검사를 할 때까지 Author는
   transaction을 `verified`나 finalization `complete`로 선언하지 않는다.

### Historical owner-apply compatibility

아래 owner-apply request, receipt, external key와 HMAC 세부는 구 evidence를 읽고 진단하기
위한 historical compatibility다. Current Author는 이 producer를 실행하거나 새 receipt를
success prerequisite로 만들지 않는다.

Historical adapter는 보존된 request/receipt의 구조와 recorded result를 읽을 수 있다. External key,
producer executable 또는 evidence root가 없으면 구조 진단만 반환하고 새 receipt 생성이나 외부
폴더 권한을 요구하지 않는다. 구 wire의 exact schema는 adapter fixture가 소유하며 current Author
apply·completion·release contract가 아니다.

```yaml
document_delta:
  source_surface:
  changed_locators:
    - path: 00_docs/example.md
      heading: Acceptance
  semantic_summary:
  baseline_digest: sha256:<64-lowercase-hex> | absent
graph_attestations:
  - patch_id:
    decision: confirm | reject | needs_revision
    evidence:
graph_apply_results:
  - patch_id:
    result: applied | failed | stale_baseline
    resulting_digest:
```

`changed_locators`의 각 항목은 required `path`와 필요한 locator field만 가진 canonical object다.
Canonical emission은 사용하지 않는 optional field를 생략하고 plain string을 허용하지 않는다.

<!-- key: id=key.standard.skill.author.change-set-writing-rule refs=key.role.author key.topic.artifact-graph key.topic.impact-review -->
## Change Set 작성 규칙

큰 문서 변경, code 영향이 있는 문서 변경, 또는 여러 artifact에 걸친 변경은 Change Set(17)을
가진다. Change Set은 모든 실행을 자동화하는 문서가 아니라, 사람의 의도가 문서, code, test,
검증, 수락을 지나가는 추적 단위다.

Change Set은 다음 fields를 포함할 수 있다.

1. `change_id`
2. human intent
3. accepted decision
4. changed source documents
5. affected capability seed
6. Linker report reference
7. required artifact candidates
8. worker assignment reference
9. worker report reference
10. document sync status
11. verification result
12. final acceptance status
13. modularization decision과 excluded reuse candidate
14. `graph_sync.required`, disposition과 근거
15. graph transaction ID와 `proposed | awaiting_attestation | ready_to_apply | applying |
    partially_applied | verified | conflicted | failed` state
16. `document_delta`, 관련 `artifact_delta` reference와 source별 baseline digest
17. Linker가 결정한 canonical mutation과 exact surface patch reference
18. surface owner attestation과 apply result
19. reconstruction·mechanical validation evidence와 resume point
20. current transaction completeness와 별도 project coverage debt

Pending graph transaction은 optional Change Set 유무와 관계없이 현재 work의 Progress에서 복구할
수 있어야 한다. Progress에는 최소 `graph_sync.required`, disposition, transaction ID와 state,
input delta와 required patch reference, attestation/apply result reference, reconstruction·mechanical
validation evidence, current transaction completeness, coverage debt, 마지막 성공 event와 resume
point를 기록한다. 전체 mutation이나 patch body는 Linker transaction artifact를 참조할 수 있지만
Progress의 locator만으로 그 artifact와 다음 미완료 action을 찾을 수 있어야 한다.

예:

```yaml
change_set:
  id: key.change.auth.lockout-threshold
  human_intent:
    summary: 로그인 실패 잠금 기준을 5회에서 3회로 변경한다.
  accepted_decisions:
    - DEC-AUTH-001
  changed_documents:
    - 00_docs/standards/security/key-standard-auth.md
  artifact_seeds:
    - key.capability.auth.account-lockout
  linker_report:
    status: required
    path:
  worker_assignment:
    status: pending
  worker_report:
    status: pending
  document_sync:
    status: pending
  final_acceptance:
    status: pending
```

<!-- key: id=key.standard.skill.author.metadata-writing-impact-review refs=key.role.author key.topic.keystone-metadata key.topic.code-anchor key.topic.impact-review key.topic.artifact-graph -->
## 키메타 작성과 Artifact Graph handoff

Author는 source document surface의 키메타(9)를 다음처럼 반영한다. Code/config/schema/API/test
source surface의 코드 앵커(18)는 Author가 직접 수정하지 않는다.

1. 새 기준서(3)나 작업서(4)를 만들 때 문서 전체 `key.id`를 부여한다.
2. 관련 문서 탐색에 실제 도움이 되는 경우에만 `key.refs`를 부여한다.
3. `key.refs`를 붙일 때는 먼저 참조할 기존 `key.id`가 있는지 확인하고, 가능하면 재사용한다.
4. 문서 전체에 적용되는 metadata는 YAML frontmatter의 `key`에 둔다.
5. 문서 identity·상태·시간 metadata인 `doc_type`, `created_at`, `status`, `approval`, 선택적
   `effective_from`과 `superseded_at`은 YAML frontmatter의 top-level에 둔다.
6. 특정 section에만 적용되는 metadata는 heading 바로 위 Markdown comment에 한 줄로 둔다.
7. 문서 metadata 변경이 Artifact Graph 해석을 요구하면 Linker report 또는 Linker handoff seed를
   요구한다.
8. Linker가 보고한 source document metadata gap은 승인 범위 안에서 Author가 반영할 수 있다.
9. Linker가 보고한 code/config/schema/API/test anchor gap은 Author가 직접 수정하지 않고
   Coordinator next action으로 남긴다.
10. 기준서나 작업서를 수정할 때 같은 `key.id`를 참조하는 문서는 impact candidate로 검토한다.
11. 같은 `key.refs`가 있어도 자동 수정하지 않는다.
12. `key.refs`가 없어도 관련 없음으로 단정하지 않고 link, path, heading, keyword도 함께
   확인한다.
13. 코드 앵커(18) typed relation이 있는 code/config/schema/API/test artifact는 Linker handoff
   seed 또는 Linker report requirement로 보고한다.
14. Capability(16)가 바뀌면 provider, consumer, verifier 후보 탐색이 필요한지 보고한다.
15. 실제 문서 수정은 승인 범위와 의미 영향이 명확할 때만 수행한다.
16. Code, config, schema, API, test artifact와 코드 앵커 수정은 Author가 직접 수행하지 않는다.

<!-- key: id=key.standard.skill.author.worktree-locator-writing refs=key.role.author key.role.coordinator key.topic.keystone-metadata key.topic.work-execution key.topic.work-recovery -->
## Worktree locator 작성

1. Coordinator 또는 직접 실행하는 Main이 linked worktree를 생성·선택하고 canonical absolute root와
   같은 Git common directory 확인 결과를 전달한 경우에만 Work Order locator를 기록한다.
2. Author는 substantive repository edit가 시작되기 전에 세션 시작점에서 읽을 수 있는 canonical
   Work Order document의 `key.worktree.path`에 exact root를 기록한다. Target branch에만 존재하는
   사본이나 Progress, Round index에는 locator를 대신 기록하지 않는다.
3. `key.worktree`는 `doc_type: work_order`의 document-level `key` mapping에만 쓰며 `path` 이외의
   child field, relative path, branch와 HEAD를 추가하지 않는다.
4. Worktree를 선택하지 않은 Work에는 field를 만들지 않는다. Existing field의 교체, 삭제 또는
   privacy-sensitive absolute path 기록은 accepted instruction 없이 추측하지 않는다.
5. 적용 뒤 Author는 current source를 다시 읽어 exact path를 확인하고 Coordinator/Main에 반환한다.
   Fresh source confirmation과 target runtime 검증은 Coordinator/Main 책임이며 Author는 구현 edit를
   시작하거나 worktree를 생성하지 않는다.

<!-- key: id=key.standard.skill.author.dependency-writing refs=key.role.author key.topic.artifact-graph key.topic.work-sequence key.topic.verification -->
## Dependency and work gate 작성

1. Author는 수용된 의존성 결정만 `key.relations.depends_on`과 `work_gates`로 작성하고
   step dependency·acceptance gate를 임의로 만들지 않는다.
2. Gate의 `dependency`가 declared target을 가리키는지, `steps` ID가 존재하는지,
   `steps`/`work_completion` 중 하나 이상이 있는지, duplicate/self-reference를 검증한다.
3. 별도 accepted exception이 없으면 required gate condition은 target의
   `work_status: complete`와 `approval.state: accepted`를 모두 작성한다.
4. Structured metadata와 legacy HTML을 함께 쓰지 않고 migration 중 둘 다 있으면
   structured 우선과 충돌을 명시한다.
5. Dependency 판정으로 progress/work status, assignment, cancellation 또는 acceptance를 자동 수정하지 않는다.

<!-- key: id=key.standard.skill.author.output-contract refs=key.role.author key.contract.output -->
## Output contract

Author는 작업 후 다음을 보고해야 한다.

1. 변경한 원천 문서(2)
2. 새로 만든 문서와 연결한 index
3. 적용한 결정(6) 또는 사용한 가정
4. 의도적으로 수정하지 않은 관련 문서
5. Code/config/schema/API/test impact seed 또는 Linker report 요약
6. Change Set 변경 또는 생성 여부
7. Linker report requirement 또는 Linker handoff seed
8. Metadata gap candidates
9. Author Edit Contract 또는 helper 사용 여부
10. 실행한 verification
11. Graph handoff result
12. 남은 risk와 다음 권장 작업
13. 복수 surface나 권한 경계가 있어 기록한 경우 routing context 요약

Author patch report는 다음 shape을 우선 사용한다.

```yaml
author_patch_report:
  contract_id:
  routing_context_ref:
  edits:
    - path:
      section:
      change_type: create | revise | progress_update | decision_record | index_update
      reason:
      source_decision:
  no_edit_candidates:
    - path:
      reason:
  progress_updates:
    - path:
      before:
      after:
      main_acceptance_evidence:
  graph_handoff_result:
    source_document_metadata_applied:
    code_config_schema_api_test_anchor_deferred_to_coordinator:
    linker_report_required:
  verification:
    commands_or_checks:
    result:
  residual_risk:
```

규칙은 다음과 같다.

1. `progress_updates`는 completion evidence 없이 `work_status: complete`로 전이하지 않고 Main
   acceptance 없이 `approval.state: accepted`로 전이하지 않는다.
2. `no_edit_candidates`는 관련 후보를 검토했지만 수정 권한이나 의미 영향이 충분하지 않아
   남긴 문서다.
3. `source_decision`은 수락된 결정(6), 승인된 edit instruction, 또는 명시한 working assumption을
   가리킨다.
4. `routing_context_ref`는 복수 surface나 권한 경계가 있어 Main이 명시적으로 남긴 경우에만
   포함한다.

<!-- key: id=key.standard.skill.author.user-response refs=key.role.author key.contract.output key.topic.skill-contract -->
## 기본 사용자 응답

Author는 `author_patch_report`를 agent-facing structured payload로 유지한다. 기본 사용자 응답은
다음 항목만 짧게 보여준다.

1. 변경 요약: 생성 또는 수정한 원천 문서(2)와 section
2. 의도적으로 수정하지 않은 후보: scope 밖이거나 inspect-only인 문서
3. 검증: 실행한 command 또는 읽기/consistency check 결과
4. 남은 risk: Main acceptance, Linker/Coordinator handoff, unresolved decision
5. 다음 권장 행동

Full `author_patch_report` 또는 `author_edit_contract`는 사용자가 요청하거나 handoff, audit/debug,
verification evidence에 필요할 때만 노출한다. Optional `keystone-viewer`는 Author report를
표현할 수 있지만 원천 문서 변경 의미, source authority, progress status를 바꾸지 않는다.

사용자-facing 응답을 보내기 전에는 `STD-KEYSTONE-045`의 Payload Disclosure Gate를 적용한다.
Full payload 요청, handoff, audit/debug, verification evidence 필요성이 없으면 `*_output`,
`*_result`, `*_report`, `worker_assignment`, `keystone_routing_decision` 원문 block을 기본
응답에 노출하지 않는다. 기본 응답은 payload 의미를 변경 요약, no-edit 후보, 검증 요약,
남은 risk, 다음 행동, 주요 출처로 압축한다.

<!-- key: id=key.standard.skill.author.stop-condition refs=key.role.author key.topic.skill-contract key.topic.impact-review key.standard.subagent -->
## Stop condition

Author는 다음 상황에서 중단하거나 main/user 결정(6)을 요청한다.

1. 복수 document root가 충돌해 Init 또는 Clarify로도 안전하게 해소할 수 없다.
2. 변경 대상 문서나 section이 불명확하다.
3. 대상 surface가 불명확하거나 원천 문서 밖의 변경이 섞여 있는데 경계를 분리할 수 없다.
4. 승인된 요청과 기존 원천 문서(2)가 충돌한다.
5. High-impact 결정(6)이 필요한데 수락된 Clarify result가 없다.
6. Scope, acceptance criteria, progress status semantics를 바꿔야 할 수 있다.
7. 민감한 정보, local-only path, private data를 기록해야 할 수 있다.
8. Implementation code, config, schema, API, test, auth/security, generated/codegen, shared
   architecture 변경이 필요하다.
9. 기존 사용자 변경을 덮어쓸 위험이 있다.
10. 관련 index, progress, 결정(6) 기록에 미치는 영향이 불확실하다.
11. Reviewer, verifier, formal report acceptance가 필요한 workflow로 커진다.
12. 외부 보조 workflow를 automatic 또는 mandatory로 바꾸는 결과가 된다.
13. 위임 허락이나 실행 환경 경계 없이 helper 작업이 필요하다.
14. Helper 작업에 reviewer/verifier, 여러 writer, workspace conflict, formal report acceptance가
    필요하지만 Coordinator 사용 허락이 없다.
15. 문서 변경이 code/config/schema/API/test artifact 수정을 요구한다.

<!-- key: id=key.standard.skill.author.verification refs=key.role.author key.topic.verification key.topic.document-authoring key.standard.subagent -->
## Verification

Author 기준은 다음 방법으로 검증한다.

1. Author contract만 보고 trigger와 non-trigger를 구분할 수 있어야 한다.
2. Create, Revise, Clarify-Apply, Normalize, Progress Update mode의 책임 차이가
   명확해야 한다.
3. 기준서(3)와 작업서(4)의 책임이 `STD-KEYSTONE-003`와 일관되어야 한다.
4. 작업서(4) step은 `STD-KEYSTONE-022`의 Goal unit field를 복구할 수 있어야 한다.
5. Parent-child 기준서 구조는 `STD-KEYSTONE-012`과 일관되어야 한다.
6. 문서 변경 후 관련 index와 context map link가 현재 상태와 맞아야 한다.
7. 키메타가 있는 문서를 수정할 때 같은 `key.id`를 참조하는 impact candidate를
   검토했는지 확인할 수 있어야 한다.
8. `investigate` 또는 `document_edit` worker를 사용해도 subagent 기준서, 승인 범위,
   Author Edit Contract를 넘지 않아야 한다.
9. 위임 시 사용자 허락과 주입된 skill/host 실행 경계를 보존하고, formal workflow가 필요하면
   허락된 Coordinator 범위로 넘겨야 한다.
10. 문서 변경이 아티팩트 그래프(14)에 미치는 Linker handoff seed 또는 Linker report requirement를
    보고할 수 있어야 한다.
11. 큰 문서-code-test 영향 변경은 Change Set(17)으로 추적할 수 있어야 한다.
12. Author는 code/config/schema/API/test를 직접 수정하지 않아야 한다.
13. Source document 변경은 Author 책임으로 수행하고 결과, 검증과 residual risk를 추적할 수
    있어야 한다. 별도 routing payload는 복수 surface나 audit 필요가 있을 때만 요구한다.
14. 기본 사용자 응답은 structured payload를 그대로 노출하지 않고 변경 요약, 검증, risk,
    next action을 요약해야 한다.
15. Verification command:
   - `rg --files 00_docs`
   - Author 관련 기준서를 읽어 link와 scope consistency 확인
16. 프로젝트 로컬 Author 기준서가 없어도 설치된 contract로 Init handoff와 문서 작성을
    수행할 수 있어야 한다.
17. 새 문서의 `created_at`, accepted 문서의 현재 `approval.accepted_at`, 새 결정의 `결정일`과
    optional temporal field가 Bootstrap 기준과 일치해야 한다.
18. 기존 문서 날짜를 추측하거나 일반 `updated_at`을 추가하지 않아야 한다.
19. Main acceptance 후 Work/Progress/index/Context Map, Work State와 graph disposition을 동기화하되
    새 finalization manifest, external key 또는 HMAC receipt 없이 current closure를 완료할 수 있어야 한다.
20. Finalization schema v1-v6과 owner-apply receipt는 historical read/diagnostic을 유지하지만
    current completion·apply·release authority가 아니어야 한다.
21. 문서 종류별 실제 의미·상태·pointer 변경이 없으면 관련 문서나 index를 갱신하지 않고, 일반
    변경에서 새 Change Set·manifest·receipt·snapshot을 만들지 않아야 한다.
22. Default, escalated, release 검증을 변경 surface로 구분하고 package/installer/historical 검증을
    일반 문서 변경의 기본값으로 실행하지 않아야 한다.
23. Terminal status reconciliation은 실제 상태 전이 때만 bounded exact-ref 후보를 확인하고,
    optional projection 부재와 historical 기록을 정상으로 보존하며 stale current/navigation
    conflict가 남은 closure를 complete로 보고하지 않아야 한다.
24. Clarify 답변별 lightweight log append와 그룹 종료별 원천 문서 application을 분리하고,
    대주제별 log 하나의 최소 `G01`/`Q01` 구조와 비권위·비평가 경계를 유지해야 한다.

<!-- key: id=key.standard.skill.author.reference-index-contract refs=key.role.author key.role.linker key.topic.keystone-metadata key.topic.artifact-graph -->
## Owner/ref authoring과 context invalidation

1. 새로 만들거나 의미를 변경한 독립 standard/document item은 stable owner ID를 검토하고 다른
   owner를 가리킬 때는 duplicate ID가 아니라 `refs`를 쓴다.
2. Acceptance criterion이나 claim의 검증 요구는 `requires_verification_of`로 작성한다. 실제 test
   artifact 또는 verification result가 수행한 evidence만 `verifies`를 선언한다.
3. Declared metadata만 source에 작성한다. Effective `document_lifecycle`, `governed_by`, authority와
   approval은 document -> section -> item 상속으로 계산하며 파생값을 child마다 복제하지 않는다.
   Effective `governed_by`는 부모 effective set과 child declared set의 ordered union으로 계산한다.
4. 승인 범위의 단일 document surface 변경은 Author가 직접 적용하고 Linker에 affected docs scope
   index invalidation/refresh를 알린다. Typed graph가 관련돼도 다른 surface patch가 필요하지 않으면
   transaction을 강제하지 않는다.
5. 둘 이상의 source surface patch가 함께 필요한 경우에만 Linker transaction을 사용한다. Author는
   자기 document surface만 attest/apply하며 cache/index file을 원천 문서처럼 수정하지 않는다.
6. Author write 뒤 downstream skill은 stale Reader context를 재사용하지 않고 affected path-set/digest
   scope를 refresh한다.

## 아이디어 노트 연결 (R026)

아이디어 노트의 직접 CRUD는 `keystone-ideas`가 담당한다. Author는 명시적 작업 구체화
요청에서 필요한 맥락을 작업서에 보존하고 제목·기록일을 함께 남긴다. 삭제 후 재사용 가능한
IDEA 번호를 영구 graph ID로 쓰지 않으며 노트만으로 실행을 승인하지 않는다.

## R015-A 관리 흐름 연결

[관리 흐름·연결 점검](../../key-standard-management-review.md)의 역할·시점·상태 반영 계약을 따른다.
기존 질답 기록·사용자 결정·읽기 전용 경계는 유지한다.
