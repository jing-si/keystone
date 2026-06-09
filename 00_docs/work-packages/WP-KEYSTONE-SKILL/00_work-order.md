# WP-KEYSTONE-SKILL 작업서(4)

이 작업서(4)는 사람이 읽을 수 있는 실행 계획이다. 또한 향후 Keystone coordination
스킬이 runtime에 Current Step Brief와 Context Pack을 도출할 수 있도록 구조화되어
있다.

## 작업 패키지

- ID: WP-KEYSTONE-SKILL
- 개요: `00_index.md`
- 진행 기록: `progress.md`

## 원천 기준서

주 기준서:

- `00_docs/standards/00_project-standard.md`

보조 참고:

- 참고용 prototype인 `work-package-doc-architect`
- 참고용 prototype인 `subagent-work-coordinator`

## 전체 범위

Include:

- Keystone 스킬 시스템을 위한 `00_docs/` 원천 문서(2)를 생성하고 유지한다.
- 구현 전에 네 개의 의도된 Keystone 스킬 역할을 정의한다.
- 최종 스킬 이름을 정의한다: `keystone-clarify`, `keystone-author`,
  `keystone-reader`, `keystone-coordinator`.
- `keystone-clarify`의 Plan Mode 결정(6) collection과 Default Mode document update
  workflow를 정의한다.
- document root resolution과 영어 path 규칙을 정의한다.
- Keystone을 사용하는 target project의 initial project setup 동작과 Keystone config
  file을 정의한다.
- 기준서(3)와 작업서(4)의 Git policy 선택지를 정의한다.
- Keystone output language policy boundary를 정의한다.
- 향후 `standards/`와 `works/` tree policy를 정의한다.
- 재사용 가능한 기준서와 현재 작업서가 반복 context를 줄이는 방식을 정의한다.
- Superpowers가 Keystone 원천 문서(2)를 대체하지 않는 명시적 supporting
  workflow로 사용될 수 있는 방식을 정의한다.
- main-agent supervisor model과 role-based subagent model을 정의한다.
- reader mode, 파생 에이전트 문서(8) policy, progress/report status,
  standards-led verification을 정의한다.
- 이후 main이 subagent를 안전하게 coordinate할 수 있도록 작업서(4) step을 구성한다.
- 언제 작업을 위임할 수 있고 언제 main 또는 사용자 결정이 필요한지 식별한다.

Exclude:

- 이 문서 단계에서 skill source code 구현
- persistent `agent/` handoff document 기본 생성
- 설치된 외부 스킬 또는 prototype 스킬 수정
- 사용자 명시 지시 또는 수락된 document authorization 없이 Superpowers 자동 호출
- 사용자 승인 없이 기존 `work-packages/` 문서를 `works/`로 이동
- 이후 단계에서 승인되지 않은 broad project setup, build tooling, publishing,
  marketplace integration
- 이후 fixture 또는 test step이 명시적으로 요구하지 않는 한 S01 또는 S02 동안 이
  implementation repository에 `.keystone/config.yaml` 만들기

조건부 허용:

- 승인된 skill-system goal을 바꾸지 않는 작은 문서 refinement
- 다음 수락된 작업에 구체적 필요가 생긴 경우에만 `scope.md` 추가
- 수락된 정책 결정(6)을 `decisions.md`에 기록

## 단계

## Step S01. 문서 기반 수립

### Goal

Main session이 project goal, standards, current step, scope, verification path,
next action을 복구할 수 있도록 Keystone 스킬 시스템 프로젝트의 최소
원천 문서(2) set을 마련한다.

### Scope

Include:

- `00_docs/context-map.md`
- `00_docs/standards/00_index.md`
- `00_docs/standards/00_project-standard.md`
- `00_docs/work-packages/WP-KEYSTONE-SKILL/00_index.md`
- `00_docs/work-packages/WP-KEYSTONE-SKILL/00_work-order.md`
- `00_docs/work-packages/WP-KEYSTONE-SKILL/progress.md`
- `00_docs/work-packages/WP-KEYSTONE-SKILL/decisions.md`

Exclude:

- Skill implementation file
- 구체적 필요가 생기기 전의 optional `agent/` document
- 구체적 필요가 생기기 전의 optional `scope.md`
- `00_docs/` 밖의 변경
- Prototype installed skill 수정
- Superpowers workflow 실행
- 사용자 승인 없는 기존 `work-packages/` 문서의 `works/` migration

조건부 허용:

- 명시된 Keystone skill-system goal을 보존하는 범위 안의 naming 또는 wording refinement

### Source Context

Primary standard:

- `00_docs/standards/00_project-standard.md`

Related rules:

- `STD-KEYSTONE-001`, `STD-KEYSTONE-002`, `STD-KEYSTONE-003`,
  `STD-KEYSTONE-004`, `STD-KEYSTONE-008`, `STD-KEYSTONE-009`,
  `STD-KEYSTONE-010`, `STD-KEYSTONE-011`, `STD-KEYSTONE-012`,
  `STD-KEYSTONE-013`, `STD-KEYSTONE-014`, `STD-KEYSTONE-015`,
  `STD-KEYSTONE-016`, `STD-KEYSTONE-017`, `STD-KEYSTONE-018`,
  `STD-KEYSTONE-019`, `STD-KEYSTONE-020`, `STD-KEYSTONE-021`,
  `STD-KEYSTONE-022`, `STD-KEYSTONE-023`, `STD-KEYSTONE-024`,
  `STD-KEYSTONE-025`, `STD-KEYSTONE-026`, `STD-KEYSTONE-027`,
  `STD-KEYSTONE-028`

Supporting references:

- document structure 참고용 prototype인 `work-package-doc-architect`
- future coordination 참고용 prototype인 `subagent-work-coordinator`

### Completion Criteria

- [ ] `00_docs/context-map.md`가 존재하고 active standards와 work package를 연결한다.
- [ ] `00_docs/standards/00_index.md`가 존재하고 active standards를 색인한다.
- [ ] `00_docs/standards/00_project-standard.md`가 document authority, 네 개의 계획된
  skill role, coordinator compatibility에 관한 project-wide rule을 정의한다.
- [ ] `00_docs/work-packages/WP-KEYSTONE-SKILL/00_index.md`가 package goal, status,
  source standards, current step을 설명한다.
- [ ] `00_docs/work-packages/WP-KEYSTONE-SKILL/00_work-order.md`가 coordinator-compatible
  step을 포함한다.
- [ ] 문서 기반은 Keystone이 반복되는 날짜별 planning document 대신 재사용 가능한
  기준서(3)와 작업서(4)를 primary context source로 사용한다는 점을 기록한다.
- [ ] 문서 기반은 Superpowers가 optional, explicit이며 수락된 Keystone
  원천 문서(2)보다 하위라는 점을 기록한다.
- [ ] 문서 기반은 수락된 document root, tree, file naming policy를 기록한다.
- [ ] 문서 기반은 initial project setup, Keystone config file, 원천 문서(2) Git
  policy, Keystone output language policy를 향후 target-project behavior로 기록하며,
  S01 동안 이 implementation repository에 config file이 필요하지 않음을 기록한다.
- [ ] 문서 기반은 reader mode, 파생 에이전트 문서(8) policy, progress/report
  status, standards-led verification policy를 기록한다.
- [ ] `00_docs/work-packages/WP-KEYSTONE-SKILL/progress.md`가 implementation complete로
  표시하지 않은 상태로 current step을 기록한다.

### 권장 접근

이 step은 document creation이며 main session이 처리해야 한다. `work-package-doc-architect`는
문서 형태를 잡기 위한 참고 자료로만 사용할 수 있다. Main session이 먼저 좁은
documentation Context Pack을 준비하고 review가 필요하다고 판단하지 않는 한 worker를
배정하지 않는다. Prototype skill은 문서 구성을 참고하기 위한 것이며 최종
Keystone dependency가 아니다.

### Context Pack Seed

이후 subagent handoff를 준비할 때 main은 다음을 포함해야 한다:

- `00_index.md`의 Keystone skill-system goal
- `context-map.md`의 네 개 planned skill role
- `00_project-standard.md`의 명시적 Superpowers integration boundary
- `00_project-standard.md`의 main-agent supervisor rule과 role-based subagent rule
- `00_project-standard.md`의 document tree, file naming, 파생 에이전트 문서(8),
  progress/report, verification rule
- `00_project-standard.md`의 initial project setup, Keystone config, Git policy,
  Keystone output language rule. 여기에는 이 implementation repository와 향후 target
  project의 구분이 포함되어야 한다.
- `00_project-standard.md`의 project rule
- `progress.md`의 current step과 status
- 위 include/exclude scope
- 파생 에이전트 문서(8)를 기본 생성하지 않는다는 규칙
- file existence와 structure check를 통한 verification

### Stop Conditions

- 사용자가 의도한 Keystone skill-system goal을 바꾼다.
- 문서 변경이 승인된 foundation 범위를 넘어 standards, scope, acceptance
  criteria를 바꾼다.
- 문서 변경이 Superpowers를 automatic으로 실행되게 만들거나 수락된 Keystone 원천
  문서(2)보다 더 권위 있게 만든다.
- 문서 변경이 사용자 승인 없이 기존 package path를 migration한다.
- Document acceptance 이전에 implementation file이 필요해진다.
- Optional document가 필요해 보이지만 승인되지 않았다.
- Verification에서 누락되었거나 inconsistent한 document link가 발견된다.

### Verification

허용된 확인:

- `rg --files 00_docs`
- 생성된 Markdown file을 읽어 structure와 link consistency 확인

명시적으로 허용되기 전까지 금지:

- Skill implementation change
- Persistent `agent/` document 생성
- Generated file 생성
- Broad formatting 또는 repository cleanup

### Expected Output

- 승인된 S01 scope 아래의 사람이 읽을 수 있는 원천 문서(2)
- 필수 Goal-unit field를 드러내는 작업서(4)
- Main acceptance 전까지 S01을 active로 유지하는 진행 기록(5)
- Skill implementation, 파생 에이전트 문서(8), package migration,
  broad repository cleanup 없음

### 검토 포인트

Reviewer는 다음을 확인해야 한다:

- 최소 document set이 `00_docs/` 아래에 존재한다.
- 문서는 agent-only config가 아니라 사람이 읽을 수 있는 원천 문서(2)다.
- Keystone의 Superpowers integration은 explicit하고 bounded하다.
- Main-agent supervisor model이 문서에 반영되어 있다.
- 수락된 tree/file/status/verification policy가 문서에 반영되어 있다.
- Work order가 Current Step Brief와 Context Pack을 만들 수 있다.
- Optional document가 필요 없이 생성되지 않았다.
- Progress가 implementation complete로 잘못 표시되어 있지 않다.

### 진행 기록

진행 상태는 `progress.md`에 기록한다. Main session이 document foundation을 수락한 뒤에만
S01을 complete로 표시한다.

## Step S02. Keystone 스킬 시스템 계약 정의

### Goal

Project goal을 네 개 planned Keystone skill의 명시적 contract로 전환한다. Contract에는
trigger condition, non-goal, required input, document creation/reading behavior,
main/subagent role split, runtime output, failure/escalation behavior가 포함된다.

### Scope

Include:

- 네 개 planned Keystone skill의 skill contract content
- 승인된 behavior를 기록하기 위해 필요한 원천 문서(2) update
- `work-package-doc-architect`와 `subagent-work-coordinator`에서 재사용할 behavior를
  참고용 prototype으로 식별
- optional supporting workflow로서 Superpowers integration rule
- Goal assignment와 role-based subagent boundary
- coordinator-compatible 작업서 step을 위한 work step field contract
- topic-scoped 결정(6) collection과 reflection을 위한 clarify mode contract
- Keystone을 사용하는 target project의 `.keystone/config.yaml`과
  `.keystone/config.local.yaml` initial setup contract
- 기준서(3)와 작업서(4) Git publication policy 선택지
- Keystone output language policy boundary
- Reader mode contract
- Orientation Mode output contract와 document-to-repository mismatch policy
- Document tree와 filename contract
- Progress/report status contract
- Derived document와 impact update contract
- Standards-led verification contract

Exclude:

- Contract가 수락되기 전 implementation code
- 설치된 외부 스킬 변경
- 네 개 planned Keystone skill을 하나로 합치기
- Superpowers를 mandatory로 바꾸거나 automatic 실행 대상으로 만들기
- 재사용 가능한 기준서를 반복되는 날짜별 task document로 대체하기
- 명시적 승인 없는 persistent runtime handoff format 생성
- 사용자 결정 없는 현재 `work-packages/` package의 `works/` migration

조건부 허용:

- 수락된 contract 결정(6)이 변경되거나 누적되면 `decisions.md` 업데이트
- `00_project-standard.md`가 너무 넓어지면 dedicated standard document 추가

### Source Context

Primary standard:

- `00_docs/standards/00_project-standard.md`

Related rules:

- `STD-KEYSTONE-001`, `STD-KEYSTONE-002`, `STD-KEYSTONE-003`,
  `STD-KEYSTONE-004`, `STD-KEYSTONE-005`, `STD-KEYSTONE-006`,
  `STD-KEYSTONE-007`, `STD-KEYSTONE-009`, `STD-KEYSTONE-019`,
  `STD-KEYSTONE-021`, `STD-KEYSTONE-025`, `STD-KEYSTONE-026`,
  `STD-KEYSTONE-027`, `STD-KEYSTONE-028`

관련 원천 문서(2):

- `00_docs/context-map.md`
- `00_docs/work-packages/WP-KEYSTONE-SKILL/00_index.md`
- `00_docs/work-packages/WP-KEYSTONE-SKILL/decisions.md`
- `00_docs/work-packages/WP-KEYSTONE-SKILL/progress.md`

Supporting references:

- authoring behavior 참고용 prototype인 `work-package-doc-architect`
- coordination behavior 참고용 prototype인 `subagent-work-coordinator`

### Completion Criteria

- [ ] 네 개 planned Keystone skill role이 원천 문서(2) 또는 승인된 implementation
  note에 설명되어 있다.
- [ ] 최종 skill name은 `keystone-clarify`, `keystone-author`, `keystone-reader`,
  `keystone-coordinator`다.
- [ ] 각 skill의 trigger와 non-trigger condition이 명확하다.
- [ ] `keystone-clarify` trigger boundary, Plan Mode topic collection, Default Mode
  document update behavior가 명확하다.
- [ ] 기준서(3)와 작업서(4)의 책임이 명확하다.
- [ ] Parent-child 기준서 navigation behavior가 명확하다.
- [ ] `standards/`와 `works/` tree rule이 명확하다.
- [ ] `00_index.md`, `standard-{slug}.md`, `work-{slug}.md`, `progress.md` file
  naming rule이 명확하다.
- [ ] Target project를 위한 initial project setup과 Keystone config behavior가
  명확하다.
- [ ] 기준서와 작업서 Git policy 선택지가 명확하다.
- [ ] Keystone output language policy가 Keystone artifact에만 적용되도록 scope가
  명확하다.
- [ ] 재사용 가능한 기준서와 날짜별/반복 task document의 관계가 명확하다.
- [ ] 파생 에이전트 문서(8) type과 creation/update condition이 명확하다.
- [ ] `keystone-reader` Orientation, Navigator, Work Prep mode가 명확하다.
- [ ] Orientation Mode output은 document-led, repository-aware, read-only이며 자동
  수정 없는 mismatch reporting을 포함한다.
- [ ] 명시적 Superpowers integration condition이 명확하다.
- [ ] Main-agent supervisor responsibility가 명확하다.
- [ ] Role-based subagent responsibility가 명확하다.
- [ ] Subagent-sized work unit을 위한 Goal assignment behavior가 명확하다.
- [ ] Work step field가 명확하다. `Goal`, `Scope`, `Source Context`,
  `Completion Criteria`, `Stop Conditions`, `Verification`, `Expected Output`은
  필수이며 `Suggested Role`은 선택 사항이다.
- [ ] Progress status와 subagent report status가 분리되어 있고 정의되어 있다.
- [ ] Standards-led verification과 handoff checklist behavior가 명확하다.
- [ ] Main-agent responsibility와 subagent limit이 명확하다.
- [ ] Required document input과 runtime output이 정의되어 있다.
- [ ] Escalation condition이 향후 coordination skill과 정렬되어 있다.

### 권장 접근

Main은 현재 문서와 사용자 방향을 바탕으로 contract를 draft해야 한다. 모호성이 behavior에
실질적으로 영향을 주면 향후 `keystone-clarify` contract를 사용한다. 즉 Plan Mode에서
한 topic의 질문과 결정(6)을 수집하고, 사용 가능한 경우 `request_user_input` 또는 동등한
selection UI를 사용하며, reflection과 edit plan을 요약한 뒤 Default Mode에서 관련
원천 문서(2) update를 함께 적용한다. 이 step은 기존 skill example 또는 local skill
convention을 조사하기 위해 read-only explorer를 사용할 수 있다. Superpowers는 명시적
호출이 있거나 수락된 Keystone 기준서(3) 또는 작업서(4)가 특정 quality-assist use를 허용한 경우에만
supporting workflow로 사용할 수 있다. 예를 들어 Keystone authoring이 infra setup 기준서
또는 작업서의 document format, location, required section을 정의하고, Superpowers
brainstorming이 그 안의 실제 infra, server, code-development content를 다듬을 수 있다.

### Context Pack Seed

Subagent handoff를 준비할 때 main은 다음을 포함해야 한다:

- 현재 Keystone skill-system goal과 non-goal
- 네 개 planned skill role과 boundary
- `keystone-clarify` topic 결정(6) workflow와 수락된 결정(6)
- Target project를 위한 initial project setup과 Keystone config rule
- 원천 문서(2) Git policy와 Keystone output language policy
- 수락된 document tree와 file naming policy
- Reader mode와 expected output
- Orientation Mode repository snapshot과 read-only mismatch handling
- source of truth가 아닌 optional supporting input으로서 Superpowers
- 재사용 가능한 장기 policy로서 기준서(3), goal-oriented execution document로서
  작업서(4)
- Work step field contract와 optional `Suggested Role` rule
- Main-agent supervisor model과 role-based subagent model
- Progress/report status
- Standards-led verification checklist rule
- `00_project-standard.md`의 관련 rule
- 조사할 정확한 document 또는 skill example
- Installed external skill을 수정하지 않는 boundary
- Finding 또는 proposed contract text를 위한 expected output format

### Stop Conditions

- Contract가 승인된 skill-system goal을 바꾼다.
- Contract가 네 개 planned skill 사이 boundary를 모호하게 만든다.
- Contract가 완료되지 않은 high-impact clarification topic에서 원천 문서(2) edit을
  요구한다.
- Contract가 Superpowers를 mandatory로 바꾸거나 automatic 실행 대상으로 만들거나 수락된
  Keystone 문서보다 권위 있게 만든다.
- Contract가 작업을 role-based goal로 나누지 못하게 만든다.
- Contract가 파생 에이전트 문서(8)를 기본 mandatory로 만든다.
- Contract가 기준서-led verification을 약화한다.
- Contract가 원천 문서(2) Git tracking을 project setting이 아니라 implicit
  setting으로 만든다.
- Contract가 Keystone setup result를 common/global instruction file에 쓰게 만든다.
- Contract가 Keystone setup behavior가 구현되거나 테스트되기 전에 이 implementation
  repository에 `.keystone/config.yaml`이 있어야 한다고 암시한다.
- Contract가 Keystone output language로 관련 없는 task를 override하게 만든다.
- Contract가 Orientation Mode로 document, code, config, progress, 결정(6), generated
  file을 수정하게 허용한다.
- Contract가 document-to-repository mismatch를 사용자 또는 main-agent 결정(6) 없이
  고치게 한다.
- 필요한 behavior가 external skill constraint와 충돌한다.
- 올바른 설계를 확정하는 데 implementation 또는 packaging decision이 먼저 필요하다.
- Step 수행에 승인 없이 `00_docs/` 밖의 변경이 필요하다.

### Verification

허용된 확인:

- 영향받은 원천 문서(2)를 읽어 consistency 확인
- Contract만 보고 skill을 언제 실행해야 하고 언제 실행하지 않아야 하는지 답할 수 있는지 확인

명시적으로 허용되기 전까지 금지:

- Implementation code change
- Skill publish 또는 install
- Broad repository cleanup

### Expected Output

- 네 개 Keystone skill을 구현할 수 있을 만큼 명확한 원천 문서(2) contract
- 수락된 contract 결정(6)이 관련 원천 문서(2)에 일관되게 기록된 상태
- Implementation code, publishing, installation, package migration, unapproved
  persistent runtime handoff format 없음

### 검토 포인트

Reviewer는 다음을 확인해야 한다:

- Contract가 네 개 skill 구현을 안내할 만큼 구체적이다.
- `keystone-clarify` topic 결정(6) behavior가 명시적이다.
- Initial setup, Git policy, Keystone output language behavior가 target-project
  runtime behavior로 명시적으로 정리되어 있다.
- 기준서(3)와 작업서(4) responsibility가 명시적이다.
- Superpowers integration이 explicit하고 bounded하다.
- Work unit이 role-based subagent goal이 될 수 있다.
- Work step field는 simple step에 긴 template를 강제하지 않으면서 recoverability와
  coordinator compatibility에 충분하다.
- Reader mode와 파생 에이전트 문서(8) policy가 명시적이다.
- Orientation Mode는 document-led, repository-aware, read-only이며
  document-to-repository mismatch를 결정(6) 대상으로 보고한다.
- Progress/report status와 verification source가 명시적이다.
- Main/subagent boundary가 명시적이다.
- Stop condition이 정의되어 있다.
- 원천 문서(2)가 사람이 읽을 수 있다.

### 진행 기록

진행 상태는 main acceptance 이후에만 `progress.md`에 기록한다.

## Step S03. 초기 Keystone 스킬 세트 구현

### Goal

Document foundation과 skill-system contract가 수락된 뒤 네 개 planned Keystone skill의
첫 구현을 작성한다.

### Scope

Include:

- `skills/keystone-clarify`, `skills/keystone-author`, `skills/keystone-reader`,
  `skills/keystone-coordinator` 아래의 초기 Keystone skill source file
- 수락된 contract가 요구하는 최소 reference
- `00_docs/`로 돌아가는 documentation link

Exclude:

- 승인되지 않은 publishing, marketplace registration, installation change
- `work-package-doc-architect` 또는 `subagent-work-coordinator` rewrite
- `work-package-doc-architect` 또는 `subagent-work-coordinator`를 최종 runtime skill로
  의존하기
- Broad automation, code generation, repository restructuring

조건부 허용:

- 수락된 contract가 요구하는 작은 supporting reference file
- 수락된 implementation decision을 반영하기 위한 작은 `00_docs/` update

### Source Context

Primary standard:

- `00_docs/standards/00_project-standard.md`

Related rules:

- `STD-KEYSTONE-001`, `STD-KEYSTONE-002`, `STD-KEYSTONE-003`,
  `STD-KEYSTONE-005`

필수 입력:

- S01에서 수락된 document foundation
- S02에서 수락된 four-skill contract
- repo-local `skills/` 아래의 정확한 target file과 directory
- 재사용할 existing skill format example

### Completion Criteria

- [ ] 네 개 planned Keystone skill 모두의 skill file이 승인된 위치에 생성되어 있다.
- [ ] Skill source file은 repo-local `skills/` 아래에 있다.
- [ ] 각 skill description과 body가 수락된 contract와 일치한다.
- [ ] Clarification skill은 document edit 전에 topic-scoped high-impact 결정(6)
  collection과 reflection을 지원한다.
- [ ] Authoring skill은 기준서와 작업서 creation/revision을 지원한다.
- [ ] Reading/work-preparation skill은 관련 document selection과 context extraction을
  지원한다.
- [ ] Coordination skill은 coordinator-compatible step recovery와 bounded subagent
  handoff를 지원한다.
- [ ] Implementation은 prototype skill을 복제하거나 조용히 rewrite하지 않는다.
- [ ] Lightweight verification으로 skill file이 존재하고 읽을 수 있음을 확인한다.

### 권장 접근

S02가 수락되기 전에는 이 step을 시작하지 않는다. Main은 구체적 Context Pack을 준비한
뒤 직접 구현할지 bounded worker task로 위임할지 결정해야 한다. 승인된 위치가 이
저장소 밖이면 편집 전에 write permission을 확인한다.

### Context Pack Seed

Subagent handoff를 준비할 때 main은 다음을 포함해야 한다:

- S02에서 수락된 four-skill contract
- repo-local `skills/` 아래의 정확한 target file과 directory
- 재사용할 existing skill format example
- external skill modification 금지 boundary
- verification command 또는 file-read check

### Stop Conditions

- 승인된 skill location이 불명확하다.
- Implementation이 installed external skill 변경을 필요로 한다.
- Implementation이 네 개 planned skill의 독립성을 유지할 수 없다.
- Packaging, publishing, install behavior가 필요하지만 승인되지 않았다.
- Verification이 skill file을 읽을 수 있음을 확인하지 못한다.

### Verification

허용된 확인:

- 승인된 skill directory에서 `rg --files`
- 생성된 skill file을 읽어 structure와 content 확인

명시적으로 허용되기 전까지 금지:

- Publishing 또는 marketplace operation
- Broad global skill registry change
- Destructive file operation

### Expected Output

- 승인된 repo-local `skills/` 위치에 있는 네 개의 읽을 수 있는 Keystone skill source
  directory 또는 file
- 수락된 S02 contract와 일치하는 skill description과 instruction
- Publishing, installation, marketplace, prototype-skill rewrite, broad repository
  restructuring 없음

### 검토 포인트

Reviewer는 다음을 확인해야 한다:

- Implementation이 수락된 four-skill contract와 일치한다.
- Scope가 승인된 skill location 안에 머문다.
- Prototype skill은 design input으로만 참조되며 runtime dependency가 아니다.
- Verification evidence가 충분하다.

### 진행 기록

진행 상태는 main acceptance 이후에만 `progress.md`에 기록한다.
