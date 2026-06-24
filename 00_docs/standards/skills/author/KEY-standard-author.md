---
doc_type: standard
key:
  id: key.standard.skill.author
  refs:
    - key.role.author
    - key.topic.document-authoring
    - key.topic.work-creation
    - key.topic.impact-review
    - key.topic.progress-update
---

# keystone-author 기준서

<!-- key: id=key.standard.skill.author.purpose refs=key.role.author key.topic.document-authoring -->
## 목적

이 기준서는 `keystone-author`의 상세 계약을 정의한다. `keystone-author`는 수락된
요청과 결정(6)을 바탕으로 사람이 읽을 수 있는 기준서(3), 작업서(4), 진행 기록(5),
결정(6) 기록을 만들거나 수정한다.

<!-- key: id=key.standard.skill.author.scope refs=key.role.author key.topic.document-authoring key.topic.work-creation key.topic.impact-review -->
## 적용 범위

1. `keystone-author`의 trigger와 non-trigger condition
2. 기준서(3) creation/revision contract
3. 작업서(4) creation/revision contract와 `works/` tree 작성 boundary
4. 수락된 Clarify result를 원천 문서(2)에 적용
5. Parent-child 기준서 구조화와 index update
6. Progress update boundary
7. 문서 작성 후 verification과 report contract

<!-- key: id=key.standard.skill.author.out-of-scope refs=key.role.author key.topic.document-authoring key.topic.skill-contract key.topic.formal-workflow -->
## 적용하지 않는 범위

1. High-impact topic을 질문으로 수집하고 결정(6)을 확정하기
2. Read-only project orientation, document navigation, work preparation
3. Formal subagent workflow orchestration, worker handoff 확정, report acceptance
4. Implementation code, schema, generated file, runtime config 수정
5. 승인되지 않은 scope, acceptance criteria, status semantics 변경
6. 명시적 필요 없이 persistent 파생 에이전트 문서(8) 생성
7. Superpowers나 외부 workflow를 자동 실행 대상으로 만들기

<!-- key: id=key.standard.skill.author.standard-relations refs=key.role.author key.doc.standard key.topic.skill-contract -->
## 기준 관계

1. Parent 기준서: `../../00_KEY-project-standard.md`
2. 상위 규칙: `STD-KEYSTONE-001`, `STD-KEYSTONE-002`, `STD-KEYSTONE-003`,
   `STD-KEYSTONE-005`, `STD-KEYSTONE-006`, `STD-KEYSTONE-007`,
   `STD-KEYSTONE-008`, `STD-KEYSTONE-010`, `STD-KEYSTONE-011`,
   `STD-KEYSTONE-013`, `STD-KEYSTONE-015`, `STD-KEYSTONE-016`,
   `STD-KEYSTONE-017`, `STD-KEYSTONE-018`,
   `STD-KEYSTONE-020`, `STD-KEYSTONE-021`, `STD-KEYSTONE-022`, `STD-KEYSTONE-023`,
   `STD-KEYSTONE-028`, `STD-KEYSTONE-029`, `STD-KEYSTONE-030`, `STD-KEYSTONE-031`
3. 관련 결정(6): `00_docs/works/KEY-decisions.md`
4. 충돌 처리: 이 기준서와 parent 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의
   결정(6)을 받는다. 결정 전까지는 parent 기준서를 임시 우선 기준으로 삼는다.
5. 상세화 범위: 이 기준서는 `STD-KEYSTONE-029`의 Author behavior를 구현 가능한 수준으로
   상세화한다.

<!-- key: id=key.standard.skill.author.skill-identity refs=key.role.author key.topic.skill-contract -->
## Skill identity

1. Skill name: `keystone-author`
2. Primary role: 원천 문서(2) 작성과 승인된 revision
3. Primary user: main agent 또는 Keystone 원천 문서(2)를 작성하려는 사용자
4. Output authority: Author가 수정한 원천 문서(2)는 사용자 또는 main이 수락한 범위 안에서
   권위를 가진다.

<!-- key: id=key.standard.skill.author.trigger-condition refs=key.role.author key.topic.document-authoring key.topic.work-creation key.topic.author-edit-contract key.topic.doc-helper -->
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
7. 큰 문서 수정 전에 대상, 범위, 영향 문서, 검증 기준을 Author Edit Contract로 정리해야
   한다.
8. 승인된 문서 수정 범위 안에서 `doc-explorer` 또는 `doc-writer` helper를 사용할 수 있다.
9. 기존 문서 구조가 너무 크거나 흩어져 있어 수락된 범위 안에서 정리해야 한다.

<!-- key: id=key.standard.skill.author.non-trigger-condition refs=key.role.author key.topic.skill-contract -->
## Non-trigger condition

`keystone-author`는 다음 경우에 사용하지 않는다.

1. 질문과 선택지를 통해 high-impact policy나 scope를 먼저 결정해야 한다.
2. 현재 요청과 관련된 문서를 read-only로 찾거나 요약하기만 하면 된다.
3. Report, review, verification, acceptance가 이어지는 formal workflow를 조율해야 한다.
4. 구현 코드, 테스트, build, runtime config, generated output을 수정해야 한다.
5. 문서 변경 대상과 승인 범위가 불명확하다.
6. 민감한 정보, local-only path, private data를 기록해야 할 수 있지만 정책이 불명확하다.
7. 현재 작업이 다른 문서에 영향이 없는 현재 문서의 단순 오탈자 수정이고 별도 Author Edit
   Contract가 필요하지 않다.

<!-- key: id=key.standard.skill.author.required-input refs=key.role.author key.topic.document-authoring -->
## Required input

Author는 다음 input을 사용할 수 있어야 한다.

1. 사용자 요청 또는 main이 수락한 edit instruction
2. 설정된 document root(1) 또는 이를 해석하기 위한 project-local setting
3. 적용할 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 기록
4. 필요한 경우 수락된 `keystone-clarify` decision summary와 edit plan
5. 변경할 document section 또는 새 문서의 목적
6. 승인된 scope와 acceptance boundary
7. 현재 repository state와 Git worktree risk

Input이 부족하고 잘못된 문서 변경으로 이어질 위험이 있으면 Author는 수정하지 않고
main/user에게 결정(6)을 요청하거나 `keystone-clarify`가 다룰 topic으로 보고해야 한다.

<!-- key: id=key.standard.skill.author.common-workflow refs=key.role.author key.topic.document-authoring key.topic.impact-review key.topic.author-edit-contract key.topic.doc-helper -->
## Common workflow

Author는 작업 mode와 무관하게 다음 순서를 따른다.

1. `STD-KEYSTONE-015`에 따라 설정된 document root(1)를 해석한다.
2. 관련 parent 기준서와 child 기준서를 읽어 적용 규칙을 확인한다.
3. 요청이 create, revise, clarify-apply, normalize, progress update 중 무엇인지 정한다.
4. 변경 대상 원천 문서(2)와 section을 식별한다.
5. 승인 범위와 impact update 대상이 명확한지 확인한다.
6. High-impact 결정(6)이 부족하면 문서 수정을 멈추고 main/user에게 결정(6)을 요청하거나
   `keystone-clarify`가 다룰 topic으로 보고한다.
7. 변경이 큰 경우 Author Edit Contract로 대상 문서, section, 승인 범위, 영향 문서, 검증
   기준을 정리한다.
8. 현재 대상 문서 안의 단순 오탈자처럼 의미 변화와 외부 영향이 객관적으로 없는 수정은
   직접 처리할 수 있다.
9. 승인된 범위가 크지만 문서 수정으로 bounded되어 있으면 `doc-explorer` 또는 `doc-writer`
   helper를 사용할 수 있다.
10. Helper를 사용하더라도 report acceptance, reviewer/verifier orchestration, progress
    accepted 처리는 소유하지 않는다.
11. 승인된 범위 안에서만 원천 문서(2)를 수정한다.
12. 필요한 index, context map, progress, 결정(6) 기록을 함께 검토한다.
13. 키스톤 메타데이터(9)가 있는 경우 같은 `key.id`를 참조하는 문서를 impact candidate로
    검토한다.
14. 문서 link, 용어, 구조, Markdown 형식을 검증한다.
15. 변경 파일, 적용한 결정(6), 검증 결과, 남은 risk를 보고한다.

<!-- key: id=key.standard.skill.author.mode-contract refs=key.role.author key.topic.document-authoring key.contract.output -->
## Mode contract

<!-- key: id=key.standard.skill.author.create-mode refs=key.role.author key.topic.document-authoring key.topic.work-creation -->
### Create Mode

Create Mode는 새 원천 문서(2)를 만든다.

1. 기준서(3)는 `standards/` tree와 `STD-KEYSTONE-016`, `STD-KEYSTONE-017`을 따른다.
2. 작업서(4)는 `works/` tree와 `STD-KEYSTONE-016`, `STD-KEYSTONE-017`,
   `STD-KEYSTONE-018`을 따른다.
3. 새 작업 문서는 `works/` tree에만 만든다.
4. 새 work node를 만들면 `00_KEY-index.md`를 함께 만든다.
5. Minimal document set을 먼저 만들고, scope, decisions, coordination 문서는 필요할 때만
   추가한다.
6. 파생 에이전트 문서(8)는 `STD-KEYSTONE-020`의 생성 및 업데이트 조건을 만족할 때만
   추가하거나 업데이트한다.
7. Parent 기준서는 상세 규칙을 반복하지 않고 feature 이름, 짧은 설명, child link를 둔다.
8. Child 기준서는 trigger, non-trigger, input, output, workflow, verification, stop
   condition을 구현 가능한 수준으로 작성한다.

<!-- key: id=key.standard.skill.author.revise-mode refs=key.role.author key.topic.document-authoring key.topic.impact-review -->
### Revise Mode

Revise Mode는 기존 원천 문서(2)를 수정한다.

1. 수정 대상 문서와 section이 명확해야 한다.
2. 승인된 요청과 관계없는 문장 다듬기, 정리, renaming은 하지 않는다.
3. 이미 다른 STD가 같은 책임을 다루면 새 규칙을 만들지 않고 해당 STD를 참조한다.
4. 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 기록 사이에 영향이 있으면
   `STD-KEYSTONE-021`에 따라 함께 검토한다.
5. 의미 변경이 불확실하면 수정하지 않고 보고한다.

<!-- key: id=key.standard.skill.author.clarify-apply-mode refs=key.role.author key.role.clarify key.topic.document-authoring -->
### Clarify-Apply Mode

Clarify-Apply Mode는 수락된 Clarify result를 문서에 반영한다.

1. Decision summary, rationale, working assumptions, affected documents, edit plan이
   충분해야 한다.
2. Author는 Clarify result를 새 decision으로 확정하지 않는다.
3. Edit plan 밖의 scope나 acceptance criteria는 바꾸지 않는다.
4. 적용 중 충돌이 발견되면 중단하고 main/user 결정(6)을 요청한다.
5. 적용 후 필요한 경우 결정(6) 기록과 진행 기록(5)을 갱신한다.
6. 다른 문서와 함께 맞춰야 하는 원천 문서(2) 수정은 Clarify가 아니라 Author가 담당한다.
7. `keystone-clarify`가 명시 승인된 현재 대상 문서의 단순 오탈자만 직접 수정할 수 있다는
   예외는 `KEY-standard-clarify.md`의 Default Mode contract를 따른다.

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
3. Main acceptance 없이 작업을 complete 또는 accepted로 표시하지 않는다.
4. Worker `DONE`만으로 진행 상태를 완료로 바꾸지 않는다.
5. Acceptance state, status semantics, current step이 바뀌면 명시적으로 보고한다.
6. Progress update가 작업서(4)의 scope나 completion criteria를 바꾸면 중단한다.

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
3. 필수 field는 `STD-KEYSTONE-018`을 따른다.
4. Completion criteria는 사람이 검토할 수 있을 만큼 구체적이어야 한다.
5. Stop Conditions는 scope change, missing context, verification gap, high-risk change를
   드러내야 한다.
6. Verification은 기준서가 요구하는 검증을 약화하지 않는다.
7. Context Pack Seed는 main이 필요한 문서만 추출할 수 있게 작성한다.
8. Review points는 reviewer focus로 변환할 수 있어야 한다.

<!-- key: id=key.standard.skill.author.work-order-creation-standard refs=key.role.author key.topic.work-creation key.topic.document-system -->
## 작업서 생성 표준

새 작업서(4)를 만들 때는 다음 표준을 따른다.

1. 작업서는 기준서 tree에 종속되지 않는다.
2. 기준서별, 기능별, 구현 단계별, 검증 단계별로 독립 work를 만들 수 있다.
3. 각 work는 하나의 reviewable goal을 가져야 한다.
4. 작업서는 관련 기준서(3)를 참조하지만, 기준서 안에 실행 순서를 박지 않는다.
5. 실행 순서는 `00_docs/works/00_KEY-index.md` 또는 별도 상위 work plan이 관리한다.
6. 너무 작은 작업은 별도 work로 만들지 않고 관련 work의 step으로 흡수한다.
7. Work node는 기본적으로 `00_KEY-index.md`, `KEY-work-{slug}.md`, `KEY-progress.md`를 가진다.
8. 결정(6) 기록은 여러 work에 영향을 주면 `works/KEY-decisions.md`에, 특정 work에만 영향을
   주면 해당 work node의 `KEY-decisions.md`에 둔다.
9. 작업서 생성 후 `KEY-context-map.md`와 `works/00_KEY-index.md`의 link와 status drift를 확인한다.

<!-- key: id=key.standard.skill.author.metadata-writing-impact-review refs=key.role.author key.topic.keystone-metadata key.topic.impact-review -->
## Keystone metadata 작성과 impact 검토

Author는 키스톤 메타데이터(9)를 다음처럼 다룬다.

1. 새 기준서(3)나 작업서(4)를 만들 때 문서 전체 `key.id`를 부여한다.
2. 관련 문서 탐색에 실제 도움이 되는 경우에만 `key.refs`를 부여한다.
3. `key.refs`를 붙일 때는 먼저 참조할 기존 `key.id`가 있는지 확인하고, 가능하면 재사용한다.
4. 문서 전체에 적용되는 metadata는 YAML frontmatter의 `key`에 둔다.
5. 특정 section에만 적용되는 metadata는 heading 바로 위 Markdown comment에 한 줄로 둔다.
6. 기준서나 작업서를 수정할 때 같은 `key.id`를 참조하는 문서는 impact candidate로 검토한다.
7. 같은 `key.refs`가 있어도 자동 수정하지 않는다.
8. `key.refs`가 없어도 관련 없음으로 단정하지 않고 link, path, heading, keyword도 함께
   확인한다.
9. 실제 수정은 승인 범위와 의미 영향이 명확할 때만 수행한다.

<!-- key: id=key.standard.skill.author.output-contract refs=key.role.author key.contract.output -->
## Output contract

Author는 작업 후 다음을 보고해야 한다.

1. 변경한 원천 문서(2)
2. 새로 만든 문서와 연결한 index
3. 적용한 결정(6) 또는 사용한 가정
4. 의도적으로 수정하지 않은 관련 문서
5. Author Edit Contract 또는 helper 사용 여부
6. 실행한 verification
7. 남은 risk와 다음 권장 작업

<!-- key: id=key.standard.skill.author.stop-condition refs=key.role.author key.topic.skill-contract key.topic.impact-review -->
## Stop condition

Author는 다음 상황에서 중단하거나 main/user 결정(6)을 요청한다.

1. 설정된 document root(1)를 확신 있게 해석할 수 없다.
2. 변경 대상 문서나 section이 불명확하다.
3. 승인된 요청과 기존 원천 문서(2)가 충돌한다.
4. High-impact 결정(6)이 필요한데 수락된 Clarify result가 없다.
5. Scope, acceptance criteria, progress status semantics를 바꿔야 할 수 있다.
6. 민감한 정보, local-only path, private data를 기록해야 할 수 있다.
7. Implementation code, schema, auth/security, generated/codegen, shared architecture
   변경이 필요하다.
8. 기존 사용자 변경을 덮어쓸 위험이 있다.
9. 관련 index, progress, 결정(6) 기록에 미치는 영향이 불확실하다.
10. Reviewer, verifier, formal report acceptance가 필요한 workflow로 커진다.
11. External workflow를 automatic 또는 mandatory로 바꾸는 결과가 된다.

<!-- key: id=key.standard.skill.author.verification refs=key.role.author key.topic.verification key.topic.document-authoring -->
## Verification

Author 기준은 다음 방법으로 검증한다.

1. Author contract만 보고 trigger와 non-trigger를 구분할 수 있어야 한다.
2. Create, Revise, Clarify-Apply, Normalize, Progress Update mode의 책임 차이가
   명확해야 한다.
3. 기준서(3)와 작업서(4)의 책임이 `STD-KEYSTONE-002`와 일관되어야 한다.
4. 작업서(4) step은 `STD-KEYSTONE-018`의 Goal unit field를 복구할 수 있어야 한다.
5. Parent-child 기준서 구조는 `STD-KEYSTONE-003`과 일관되어야 한다.
6. 문서 변경 후 관련 index와 context map link가 현재 상태와 맞아야 한다.
7. 키스톤 메타데이터가 있는 문서를 수정할 때 같은 `key.id`를 참조하는 impact candidate를
   검토했는지 확인할 수 있어야 한다.
8. `doc-explorer` 또는 `doc-writer` helper를 사용해도 승인 범위와 Author Edit Contract를
   넘지 않아야 한다.
9. Verification command:
   - `rg --files 00_docs`
   - Author 관련 기준서를 읽어 link와 scope consistency 확인
   - `git diff --check`
