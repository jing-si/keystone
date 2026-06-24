# Keystone 프로젝트 기준서

## 목적

이 기준서는 Keystone 스킬 시스템을 만들기 위한 프로젝트 공통 규칙을 정의한다. 프로젝트
목표는 사람이 읽을 수 있는 원천 문서(2)를 바탕으로 네 개의 독립 스킬이 같은 문서 체계를
공유하게 하는 것이다.

1. `keystone-reader`: 기준서(3)와 작업서(4)를 읽고 작업 준비 context를 만든다.
2. `keystone-author`: 기준서와 작업서를 작성하거나 승인된 원천 문서 변경을 적용한다.
3. `keystone-clarify`: 정책, 범위, 문서, 스킬 계약에 관한 결정(6)을 topic 단위로 정리한다.
4. `keystone-coordinator`: main-supervised subagent workflow를 조율한다.

이 구현 저장소의 현재 기준서(3)와 작업서(4)는 최종 Keystone 스킬이 이미 존재한다고
가정했을 때 만들어졌을 문서 구조와 계약을 사람이 먼저 작성한 부트스트랩 기준 corpus(10)다.
개발 흐름은 이 corpus를 바탕으로 스킬을 구현한 뒤, 구현된 스킬이 같은 구조와 의미의 문서를
재생산하거나 유지할 수 있는지 검증하는 방향을 따른다.

## 적용 범위

- 설정된 document root(1) 아래의 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 기록
- 향후 Keystone skill source file
- Keystone project setting과 target project local setting
- 문서 읽기, 문서 작성, clarification, coordination workflow
- 향후 Keystone coordination 스킬과 호환되어야 하는 작업서 step

## 적용하지 않는 범위

- 관련 없는 로컬 IDE 파일
- 사용자가 명시적으로 요청하지 않은 package publishing, marketplace registration, global install
- 명시적으로 요청되지 않은 persistent worker handoff 문서
- 사용자 명시 호출 없이 외부 workflow 스킬을 자동으로 사용하는 동작

## 표준 용어

표준 용어는 Keystone 문서 전체에서 같은 개념을 같은 이름으로 쓰기 위한 기준이다.

첨자 규칙은 다음과 같다.

1. `(1)`, `(2)` 같은 첨자가 붙은 용어는 이 section에 정의된 표준 용어로 판단한다.
2. 표준 용어 정의는 `(n) 선호 언어명(영문명): 짧은 설명` 형식을 따른다.
3. 본문에서는 `설정된 document root(1)`처럼 선호 언어명 바로 뒤에 첨자를 붙인다.
4. 새 표준 용어가 필요하면 기존 첨자와 충돌하지 않는 새 번호를 추가한다.

(1) 설정된 document root(configured document root): Keystone 원천 문서 root directory

- 의미: `STD-KEYSTONE-015`의 document root resolution 결과로 정해진 Keystone 원천 문서
  root directory
- 기본값: 별도 설정이 없을 때 `00_docs/`
- 사용 규칙: 기본값이나 예시 path를 보여줄 때만 `00_docs/`를 직접 언급한다.

(2) 원천 문서(source document): 사람이 읽을 수 있고 권위를 가지는 Keystone 문서

- 의미: 기준서, 작업서, 진행 기록, 결정 기록, 필요한 범위 문서처럼 사람이 유지하는 문서
- 사용 규칙: agent-facing runtime pack, handoff, reviewer brief와 구분한다.

(3) 기준서(standard): 재사용 가능한 정책, 표준, 도메인 규칙 문서

- 의미: 장기 정책과 반복 가능한 guidance를 담는 원천 문서
- 사용 규칙: 반복되는 작업서마다 같은 정책을 복사하지 않고 기준서를 참조한다.

(4) 작업서(work order): 현재 AI 작업의 목표, 범위, 순서, 검증 경로 문서

- 의미: AI 작업의 구체적 goal, execution unit, completion criteria, stop condition,
  verification path를 담는 원천 문서
- 사용 규칙: coordinator가 Current Step Brief와 Context Pack을 복구할 수 있게 작성한다.

(5) 진행 기록(progress record): 현재 step과 workflow 상태를 복구하는 문서

- 의미: 현재 step, step status, main acceptance, 최근 report와 보류 결정을 담는 원천 문서
- 사용 규칙: worker `DONE`만으로 accepted 또는 complete로 표시하지 않는다.

(6) 결정(decision): 수락된 정책 또는 설계 선택

- 의미: 이후 문서와 구현에 영향을 주는 수락된 선택
- 사용 규칙: 여러 문서에 영향을 주면 관련 원천 문서와 함께 일관되게 기록한다.

(7) 범위 문서(scope document): 필요할 때만 추가하는 상세 범위 문서

- 의미: 작업서의 Scope만으로 부족한 복잡하거나 change-prone한 범위를 기록하는 원천 문서
- 사용 규칙: 기본 생성하지 않는다.

(8) 파생 에이전트 문서(derived agent document): 원천 문서에서 파생되는 agent-facing 문서

- 의미: agent pack, step context, worker handoff, reviewer brief 같은 runtime 보조 문서
- 사용 규칙: 원천 문서가 아니며 원천 문서와 충돌하면 원천 문서가 우선한다.

(9) 태그(tag): 관련 원천 문서(2)를 찾기 위한 사람이 붙이는 탐색 단서

- 의미: 문서나 section이 다루는 주제 또는 속성을 짧게 표현한 탐색용 단서
- 권위 규칙: `STD-KEYSTONE-031`
- 사용 규칙: 같은 태그를 가진 문서는 함께 검토할 후보가 되지만 자동 수정 대상은 아니다.

(10) 부트스트랩 기준 corpus(bootstrap reference corpus): 최종 Keystone 스킬이 재생산해야 할
문서 모델을 사람이 먼저 작성한 원천 문서(2) 집합

- 의미: 이 구현 저장소에서 현재 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 기록은 Keystone
  스킬이 이미 동작했다면 만들어졌을 구조와 의미를 수작업으로 먼저 표현한 reference corpus다.
- 사용 규칙: 원천 문서(2)의 일부이며 파생 에이전트 문서(8)가 아니다. 구현된 스킬이 이
  corpus와 같은 문서 모델을 재생산하거나 유지할 수 있는지 검증하는 기준으로 사용한다.

(11) KEY prefix(KEY prefix): Keystone-managed 원천 문서(2)를 파일명으로 식별하기 위한
대문자 prefix

- 의미: 파일명이 `KEY-`로 시작하거나 정렬용 숫자 뒤에 `_KEY-`를 가진 Markdown 문서는
  Keystone 스킬로 읽기, 작성, 수정, 실행 routing을 해야 하는 Keystone-managed 원천 문서(2)다.
- 사용 규칙: `KEY`는 대문자로 쓰고, 그 뒤 이름은 소문자 kebab-case를 사용한다. 정렬용 숫자와
  `KEY` 사이에만 `_`를 사용한다.
- 예: `00_KEY-index.md`, `00_KEY-project-standard.md`, `KEY-work-project-standard.md`,
  `KEY-progress.md`

## 핵심 규칙

### STD-KEYSTONE-001: 사람이 읽을 수 있는 원천 문서(2)가 권위다

원천 문서(2)는 사람이 읽을 수 있어야 하며 다음 문서를 포함한다.

1. 기준서(3)
2. 작업서(4)
3. 진행 기록(5)
4. 결정(6) 기록
5. 필요한 경우 범위 문서(7)

파생 에이전트 문서(8)는 원천 문서에서 파생되는 runtime 보조 자료다. 원천 문서와 충돌하면
원천 문서가 우선한다.

### STD-KEYSTONE-002: 기준서(3)와 작업서(4)는 책임이 다르다

1. 기준서: 프로젝트 정책, 표준, 도메인 규칙, 재사용 가능한 guidance를 정의한다.
2. 작업서: AI 작업의 구체적 목표, 범위, 순서, 완료 기준, 중단/보고 조건, 검증 경로를
   정의한다.

새 기준서를 작성하거나 수정할 때는 다음 구조를 우선한다.

1. 짧은 목적 문단
2. 적용 범위와 적용하지 않는 범위
3. 번호 목록 중심의 규칙
4. 필요한 경우 표준 용어 첨자
5. 기존 STD와 중복되면 새 규칙을 만들지 않고 기존 STD를 참조

### STD-KEYSTONE-003: 기준서는 parent-child 계층을 가질 수 있다

1. 전체 공통 기준서는 프로젝트 목표, 공통 용어, 문서 흐름, 스킬 목록, 공통 정책을 담는다.
2. 스킬별 child 기준서는 개별 스킬의 trigger, non-trigger, input, output, workflow,
   verification, stop condition을 담는다.
3. Parent 기준서는 상세 규칙을 모두 반복하지 않고 child 기준서로 안내한다.
4. Child 기준서는 현재 작업에 필요한 최종 상세 규칙을 담는다.
5. 전체 공통 기준서와 child 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의 결정(6)을
   받는다. 결정 전까지는 전체 공통 기준서를 임시 우선 기준으로 삼는다.

### STD-KEYSTONE-004: Coordinator 호환성은 일급 요구사항이다

모든 작업서(4) step은 다음 runtime 자료를 도출할 수 있을 만큼 충분한 정보를 포함해야 한다.

1. Current Step Brief
2. Context Pack
3. Worker handoff boundary
4. Reviewer focus
5. Stop condition
6. Verification path

### STD-KEYSTONE-005: Main이 orchestration 결정을 담당한다

1. Main은 orchestration 결정을 담당한다.
2. Main은 subagent에게 구체적 context를 제공한 뒤에만 작업을 위임한다.
3. Subagent는 read-only 조사, bounded implementation, diff review처럼 경계가 명확한 작업만
   수행한다.
4. Subagent는 전체 작업서(4)를 재해석하거나 범위를 확장하거나 추가 subagent를 생성하지
   않는다.

### STD-KEYSTONE-006: 작업은 문서에서 복구 가능해야 한다

사용자가 "run the next step"이라고 말하면 main은 설정된 document root(1)에서 다음 정보를
복구할 수 있어야 한다.

1. 현재 step
2. goal
3. completion criteria
4. applicable standards
5. expected scope
6. risks
7. verification

### STD-KEYSTONE-007: 원천 문서(2) 변경에는 명시적 승인이 필요하다

1. 기준서, 작업서, scope, acceptance criteria, progress state를 의미 있게 바꾸는 변경은
   명시적 승인이 필요하다.
2. 승인된 작업 step 안의 직접 관련 수정은 허용된다.
3. 승인된 goal, scope, acceptance criteria, status semantics, source authority를 바꾸는
   변경은 다시 승인이 필요하다.
4. 미승인 관련 변경은 조용히 적용하지 않고 보고한다.

### STD-KEYSTONE-008: 확장보다 최소 구조가 먼저다

1. `STD-KEYSTONE-015`의 document root resolution과 `STD-KEYSTONE-016`의 tree 규칙을 따른다.
2. 범위 문서(7)는 필요할 때만 추가한다.
3. 결정(6) 기록은 수락된 정책이나 설계 선택을 기록해야 할 때만 추가한다.
4. Coordination 문서는 실제 조율 필요가 생길 때만 추가한다.
5. 파생 에이전트 문서(8)는 `STD-KEYSTONE-020` 조건을 만족할 때만 추가한다.

### STD-KEYSTONE-009: KEY prefix(11) 문서는 Keystone 스킬로 routing한다

1. 최초 Keystone 문서 생성과 bootstrap setup은 사용자 또는 main의 명시 요청으로 시작한다.
2. 파일명이 `KEY-`로 시작하거나 정렬용 숫자 뒤에 `_KEY-`를 가진 원천 문서(2)는
   Keystone-managed 문서로 판단한다.
3. Keystone-managed 문서를 읽거나 작업 준비 context를 만들 때는 `keystone-reader`로
   routing한다.
4. Keystone-managed 원천 문서(2)를 작성하거나 수정할 때는 `keystone-author`로 routing한다.
5. Keystone-managed 정책, 범위, 문서 구조, 스킬 계약에 관한 high-impact 결정(6)이 필요하면
   `keystone-clarify`로 routing한다.
6. Keystone-managed 작업서(4)의 step 실행, report handling, review, verification,
   acceptance flow는 `keystone-coordinator`로 routing한다.
7. KEY prefix(11)가 없는 일반 프로젝트 문서는 자동으로 Keystone-managed 문서로 판단하지
   않는다.
8. Superpowers 같은 외부 workflow 스킬은 사용자가 호출했거나 수락된 Keystone 기준서 또는
   작업서가 명시적으로 허용한 경우에만 사용한다.

### STD-KEYSTONE-010: 기준서는 반복 context를 줄인다

1. 기준서는 장기 정책, 아키텍처, convention, 도메인 규칙, 재사용 가능한 결정을 둔다.
2. 작업서는 같은 정책을 반복해서 복사하지 않고 필요한 기준서를 참조한다.
3. 반복되는 날짜별 task document 대신 기준서와 작업서가 primary context source가 된다.

### STD-KEYSTONE-011: 작업서는 goal assignment를 위해 작업을 나눈다

작업서(4)는 명확한 goal로 배정할 수 있는 단위로 작업을 나누어야 한다. 각 단위는 다음
정보를 가진다.

1. 목적
2. 범위
3. 완료 기준
4. 중단/보고 조건
5. 검증 방법
6. 전체 프로젝트를 다시 읽지 않고도 작업할 수 있게 하는 기준서 reference

### STD-KEYSTONE-012: Main agent는 supervisor다

Main agent는 context를 보존하고 supervisor로 동작해야 한다.

1. Goal을 복구한다.
2. 필요한 문서만 읽는다.
3. Assignment를 준비한다.
4. Role-based subagent에게 작업을 routing한다.
5. Report를 받는다.
6. Repair를 결정한다.
7. Final acceptance decision을 내린다.

### STD-KEYSTONE-013: Subagent는 속도 우선이 아니라 role 기반이다

Subagent 운영은 다음 우선순위를 따른다.

1. Explorer: read-only 조사, 기존 규칙 중복 확인, repository 조사, prototype 비교
2. Worker/code modifier: 명확한 edit scope 안의 bounded implementation 또는 문서 수정
3. Reviewer: completion criteria, scope, risk, regression 가능성 검토
4. Verifier: 기준서-led verification 실행 또는 failure 원인 분리
5. 우선순위: raw speed보다 correctness, context preservation, report quality

### STD-KEYSTONE-014: Superpowers는 선택적 quality-assist layer다

1. Superpowers는 사용자가 명시적으로 호출했거나 수락된 Keystone 문서가 허용한 경우에만
   보조 input으로 사용할 수 있다.
2. Superpowers output은 Keystone 원천 문서(2)를 대체하지 않는다.
3. 수락 이후에는 Keystone 기준서와 작업서가 최종 권위다.

### STD-KEYSTONE-015: Document root resolution은 명시적이고 순서가 있다

설정된 document root(1)는 다음 순서로 해석한다.

1. 현재 사용자 지시
2. `.keystone/config.local.yaml`
3. `.keystone/config.yaml`
4. 프로젝트 로컬 agent instruction file 안의 명시적 Keystone settings block
5. 위 설정이 없으면 `00_docs/`

문서 경로는 영어여야 한다. `00_docs/`는 기본 root이지 고정 root가 아니다. 공통 또는 전역
instruction file은 setup suggestion일 수 있지만, project-local setting으로 수락되기 전에는
persistent Keystone setting이 아니다.

### STD-KEYSTONE-016: Standards와 works는 index 기반 tree를 사용한다

1. 기준서 위치: `standards/`
2. 작업서 위치: `works/`
3. 기준서 tree는 전체 공통 node에서 시작해 필요한 경우 스킬별 child node로 내려간다.
4. 작업서 tree도 node별 index file을 가진다.
5. Tree 깊이는 필요에 따라 확장할 수 있다.
6. Final node는 하위 node가 없는 node다.
7. Keystone-managed index file은 정렬용 숫자가 필요하면 `00_KEY-index.md`처럼 숫자와 `KEY`
   사이에 `_`를 사용한다.

### STD-KEYSTONE-017: Keystone-managed file은 KEY prefix(11)와 kebab-case를 사용한다

1. Keystone-managed 원천 문서(2)는 파일명에 KEY prefix(11)를 사용한다.
2. 정렬용 숫자가 필요하지 않은 파일은 `KEY-{slug}.md` 형식을 사용한다.
3. 정렬용 숫자가 필요한 파일은 `{number}_KEY-{slug}.md` 형식을 사용한다.
4. Slug는 소문자 kebab-case를 사용한다.
5. 정렬용 숫자와 `KEY` 사이를 제외하고 `_`를 사용하지 않는다.
6. 전체 공통 기준서처럼 정렬용 숫자가 필요한 기준서 파일: `00_KEY-{slug}.md`
7. 스킬별 최종 기준서 파일: `KEY-standard-{slug}.md`
8. 최종 작업서 파일: `KEY-work-{slug}.md`
9. Progress file: `KEY-progress.md`
10. Decisions file: 필요할 때 `KEY-decisions.md`
11. Slug 기준: 해당 folder 안에서 파일을 명확히 구분할 수 있는 가장 짧은 local name
12. 기존 non-KEY bootstrap 문서의 rename은 source path와 link를 바꾸는 migration이므로 별도
    승인된 작업에서만 수행한다.

### STD-KEYSTONE-018: Work step은 Goal unit이다

작업서 step은 assignable Goal unit으로 작성해야 한다. 필수 필드는 다음과 같다.

1. `Goal`
2. `Scope`
3. `Source Context`
4. `Completion Criteria`
5. `Stop Conditions`
6. `Verification`
7. `Expected Output`

`Suggested Role`은 선택 사항이며 delegation 가능성이 클 때 권장한다.

### STD-KEYSTONE-019: Reader는 세 가지 mode를 가진다

`keystone-reader`는 read-only로 원천 문서(2)를 읽어 project orientation, document
navigation, work preparation을 지원한다. 상세 계약은
`skills/reader/KEY-standard-reader.md`를 따른다.

1. Orientation Mode: project overview와 shallow repository context를 만든다.
2. Navigator Mode: 현재 요청과 관련된 기준서(3)와 작업서(4)를 찾는다.
3. Work Prep Mode: final handoff를 확정하지 않고 Goal, context, verification, role
   suggestion을 준비한다.

### STD-KEYSTONE-020: 파생 에이전트 문서(8)는 선택 사항이지만 지원한다

Keystone은 유용할 때 네 가지 파생 에이전트 문서(8)를 둘 수 있다.

1. `agent/00_agent-pack.md`
2. `agent/step-context.md`
3. `agent/worker-handoff.md`
4. `agent/reviewer-brief.md`

생성 규칙은 다음과 같다.

1. 기본적으로 생성하지 않는다.
2. 이미 존재하고 명확히 영향받는 파생 에이전트 문서만 함께 업데이트한다.
3. 새로 생성하는 경우는 사용자 명시 요청, 복잡한 handoff 사전 검토, 같은 step rerun,
   audit record 필요로 제한한다.
4. 충돌이 있으면 원천 문서가 우선한다.

### STD-KEYSTONE-021: Impact update는 문서 일관성을 보존한다

1. 원천 문서(2) 변경이 관련 parent, child, work, progress, 결정(6), 파생 에이전트
   문서(8)에 명확히 영향을 주면 함께 검토한다.
2. 영향 범위나 의미 변경이 불확실하면 수정 전에 멈추고 사용자에게 묻는다.
3. 진행 기록(5)은 main acceptance 없이 accepted 또는 complete로 바꾸지 않는다.

### STD-KEYSTONE-022: 진행 상태(progress status)와 report status는 별개다

Progress status는 workflow state이고, subagent report status는 report outcome이다.

Progress status 값은 다음과 같다.

1. `planned`
2. `ready`
3. `in_progress`
4. `assigned`
5. `reported`
6. `reviewing`
7. `verifying`
8. `accepted`
9. `blocked`

Subagent report status 값은 다음과 같다.

1. `DONE`
2. `DONE_WITH_CONCERNS`
3. `NEEDS_CONTEXT`
4. `NEEDS_SCOPE_CHANGE`
5. `BLOCKED`

문서 작성/수정도 작업 복구에 의미 있는 문서 단위 변화라면 진행 기록(5)에 남긴다. 단순
오탈자, 미세 표현 수정, 의미 변화 없는 formatting은 남기지 않는다.

### STD-KEYSTONE-023: Verification은 기준서가 이끈다

1. 기준서가 primary verification expectation을 정의한다.
2. Main은 기준서에서 관련 verification criteria를 추출해 checklist로 만든다.
3. 작업서는 local verification note를 추가할 수 있지만 기준서 verification을 약화하지
   않는다.
4. 필요하면 verifier subagent에게 별도 verification Goal을 배정한다.

### STD-KEYSTONE-024: Skill source는 저장소에 둔다

이 저장소는 네 개 Keystone 스킬의 source of truth다.

1. Reader skill: `skills/keystone-reader`
2. Author skill: `skills/keystone-author`
3. Clarify skill: `skills/keystone-clarify`
4. Coordinator skill: `skills/keystone-coordinator`

초기 배포 형태는 repo-local skill source이며, publish/install은 별도 승인이 있을 때만 다룬다.

### STD-KEYSTONE-025: Clarify는 topic-scoped이고 mode-aware다

`keystone-clarify`는 topic-scoped high-impact 결정(6)을 수집하고, 수락된 decision summary와
edit plan을 바탕으로 `keystone-author`가 관련 원천 문서(2)를 업데이트할 수 있게 준비한다.
상세 계약은 `skills/clarify/KEY-standard-clarify.md`를 따른다.

1. Plan Mode: 한 topic에 필요한 질문과 결정(6)을 수집한다.
2. Default Mode: 수락된 decision summary와 edit plan을 Author가 적용할 수 있게 정리한다.
3. 직접 수정 예외: 다른 문서에 영향이 없는 현재 대상 문서의 단순 오탈자만 직접 수정할 수
   있다.

### STD-KEYSTONE-026: Initial project setup은 Keystone config에 기록한다

이 규칙은 완성된 Keystone 스킬을 사용하는 target project에서의 동작을 설명한다. 이 구현
저장소는 fixture 또는 test step이 명시적으로 요구하지 않는 한 `.keystone/config.yaml`이
필요하지 않다.

Target project에서 initial setup은 다음을 다룬다.

1. document root
2. 기준서(3)와 작업서(4) Git policy
3. 파생 에이전트 문서(8) Git policy
4. Keystone output language policy
5. setup storage location

기본 shared config 예시는 다음과 같다.

```yaml
version: 1
document_root: 00_docs
source_docs_git_policy: track_standards_and_works
derived_agent_docs_git_policy: ignore
output_language_policy: dominant_conversation_language
```

### STD-KEYSTONE-027: 원천 문서(2) Git policy는 명시적이다

Target project의 initial setup에서 Keystone은 다음 선택지를 제공해야 한다.

1. 기준서와 작업서를 모두 track
2. 기준서만 track
3. 둘 다 track하지 않음
4. document change마다 묻기

기본 정책은 다음과 같다.

1. 파생 에이전트 문서(8)는 명시 승인 전까지 Git에서 ignore한다.
2. `.keystone/config.yaml`은 shared project policy이며 기본적으로 Git에 track한다.
3. `.keystone/config.local.yaml`은 local/private override이며 기본적으로 Git에서 ignore한다.
4. 민감한 내용은 쓰기, track, publish, derive 전에 사용자 확인이 필요하다.

### STD-KEYSTONE-028: Output language policy는 Keystone artifact에만 적용한다

1. Target project는 Keystone output language policy를 project setting으로 선택한다.
2. 이 구현 저장소의 원천 문서(2) 작성과 검토는 한국어를 기본으로 한다.
3. 파일 경로, 설정 key, schema value, status value, skill name, step ID, decision ID,
   standard ID처럼 기계적으로 참조되는 literal은 영어 또는 기존 값을 유지한다.
4. Output language policy는 관련 없는 task, code comment, commit message, README,
   external tool, non-Keystone skill에는 적용하지 않는다.

### STD-KEYSTONE-029: Author는 승인된 원천 문서(2) 작성을 담당한다

`keystone-author`는 수락된 요청과 결정(6)을 바탕으로 기준서(3), 작업서(4), 진행 기록(5),
결정(6) 기록을 만들거나 수정한다. 상세 계약은 `skills/author/KEY-standard-author.md`를 따른다.

1. Creation: 새 기준서, 작업서, 진행 기록, 결정 기록, index를 만든다.
2. Revision: 승인된 범위 안에서 기존 원천 문서(2)를 수정한다.
3. Clarify result 적용: 수락된 decision summary와 edit plan을 관련 원천 문서에 반영한다.
4. Progress update: main acceptance 전에는 accepted 또는 complete로 표시하지 않는다.

### STD-KEYSTONE-030: Coordinator는 main-supervised subagent workflow를 조율한다

`keystone-coordinator`는 작업서(4)의 Goal unit을 복구하고, main이 supervisor로 남아 있는
상태에서 role 기반 subagent 작업, report, review, verification, acceptance flow를 조율한다.
상세 계약은 `skills/coordinator/KEY-standard-coordinator.md`를 따른다.

1. Assignment: Current Step Brief, Context Pack, handoff boundary, reviewer focus를 준비한다.
2. Routing: Explorer, worker/code modifier, reviewer, verifier 같은 role을 선택한다.
3. Report handling: report status를 progress status와 분리해 처리한다.
4. Acceptance: main acceptance 조건을 만족한 뒤에만 진행 기록(5)을 accepted로 바꿀 수 있다.

### STD-KEYSTONE-031: 태그(9)는 관련 문서 탐색 hint다

태그는 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 기록을 수정하거나 읽을 때 관련 문서를
찾기 위한 hint다. 태그는 원천 문서(2)의 의미를 대체하지 않는다.

태그의 권위와 한계는 다음과 같다.

1. 같은 태그가 있으면 함께 검토한다.
2. 같은 태그가 있어도 자동 수정하지 않는다.
3. 태그가 없어도 관련 없음으로 단정하지 않는다.
4. 실제 수정은 승인 범위, 의미 영향, source authority를 따져 결정한다.
5. 태그 검색은 제목, 경로, 링크, 본문 keyword 검색을 대체하지 않고 보완한다.

태그는 두 역할을 가질 수 있다.

1. 주제 태그: 문서나 section이 다루는 핵심 기능, 도메인, flow를 나타낸다.
   - 예: `이메일발송`, `회원가입`, `결제`, `권한`
2. 속성 태그: 주제에 붙는 상태, 조건, 목적, 기술 속성, 영향 영역을 나타낸다.
   - 예: `에러`, `알림`, `인증`, `재시도`, `비동기처리`, `관리자`

태그 부여 기준은 다음과 같다.

1. 이 태그로 검색했을 때 함께 검토할 문서가 나올 가능성이 높을 때 붙인다.
2. 문서나 section을 수정할 때 같은 태그 문서를 impact candidate로 검토해야 할 때 붙인다.
3. 태그는 필수가 아니며 많을 필요도 없다.
4. 너무 일반적인 태그는 피한다.
   - 나쁜 예: `문서`, `수정`, `기능`, `작업`
5. 너무 세부적인 일회성 태그도 피한다.
6. 기존 태그가 같은 의미를 이미 표현하면 새 동의어를 만들지 않고 기존 태그를 재사용한다.
7. 태그는 project output language에 맞는 사람이 읽을 수 있는 짧은 이름을 사용한다.

표기 위치는 다음을 따른다.

1. 문서 전체에 적용되는 태그는 YAML frontmatter의 `tags`에 둘 수 있다.

   ```yaml
   ---
   doc_type: standard
   tags:
     - 이메일발송
     - 에러
   ---
   ```

2. 특정 section에만 적용되는 태그는 heading 바로 위 Markdown comment로 둘 수 있다.

   ```markdown
   <!-- tags: 이메일발송, 에러 -->
   ## 에러 발생 시 이메일 발송
   ```

3. Section-level tag는 바로 뒤 heading의 section에 적용된다.
4. Section-level tag는 문서 전체 tag를 대체하지 않고 더 좁은 탐색 단서로 사용한다.

### STD-KEYSTONE-032: Keystone은 부트스트랩 기준 corpus(10)로 self-hosting을 검증한다

1. 이 구현 저장소의 현재 기준서(3)와 작업서(4)는 최종 스킬이 만든 파생 에이전트 문서(8)가
   아니다.
2. 이 문서들은 최종 스킬이 존재했다면 만들었을 원천 문서(2)의 구조, 경계, workflow를 사람이
   먼저 작성한 부트스트랩 기준 corpus(10)다.
3. Skill source 생성은 이 corpus를 input contract로 삼아 구현한다.
4. 통합 검증은 구현된 스킬이 같은 문서 모델, role boundary, verification path를 재생산하거나
   유지할 수 있는지 확인한다.
5. 스킬 구현과 corpus가 충돌하면 원천 문서(2)를 임시 권위로 두고, 충돌이 의도 변경인지 구현
   결함인지 main/user 결정(6)을 받는다.

## 기대 동작

1. Project orientation
   - Main agent는 `KEY-context-map.md`를 확인해 active standards와 active work를 찾는다.
   - 현재 active work는 `00_docs/works/00_KEY-index.md`에서 찾는다.
2. Document reading
   - Reader는 관련 기준서와 작업서만 읽고, 관련 없는 branch를 불러오지 않는다.
3. Document authoring
   - Author는 승인된 범위 안에서 원천 문서(2)를 작성하거나 수정한다.
4. Clarification
   - Clarify는 high-impact decision topic을 하나씩 정리하고 Author 적용 계획을 만든다.
5. Work execution
   - Coordinator는 작업서 step을 Goal unit으로 복구하고 main-supervised subagent workflow를
     조율한다.
6. Supporting workflow
   - Superpowers는 명시적 supporting workflow로만 사용할 수 있다.
7. Bootstrap verification
   - 현재 Keystone 원천 문서(2)는 부트스트랩 기준 corpus(10)로 사용되며, S06-S07에서 구현된
     스킬이 같은 문서 모델을 재생산하거나 유지할 수 있는지 검증한다.

## 승인 없이 금지되는 변경

1. Keystone 스킬 시스템 goal의 의미 변경
2. 네 개 계획된 Keystone 스킬을 승인 없이 합치기
3. Prototype skill을 최종 runtime dependency로 취급하기
4. 완료되지 않은 high-impact clarification topic을 근거로 원천 문서(2) 수정하기
5. 승인 없이 document root 또는 active work tree 변경하기
6. common/global instruction file에 Keystone setup result 쓰기
7. 민감한 원천 문서(2)를 승인 없이 track, publish, derive하기
8. Keystone output language가 관련 없는 작업을 override하게 하기
9. 외부 workflow 스킬을 자동 호출하기
10. 파생 에이전트 문서(8)를 원천 문서로 취급하기
11. Main acceptance 전에 work를 accepted 또는 complete로 표시하기
12. 승인 없이 API contract, schema, auth/security, generated/codegen, shared architecture로
    scope 확장하기

## Escalation 조건

1. 원천 문서(2)가 현재 사용자 방향과 충돌한다.
2. 네 스킬 사이 경계가 불명확하다.
3. high-impact clarification topic을 확신 있게 해결할 수 없다.
4. document root, Git policy, output language policy를 안전하게 추론할 수 없다.
5. work unit을 reviewable output이 있는 명확한 goal로 배정할 수 없다.
6. 문서 변경의 impact 범위가 불명확하다.
7. high-risk implementation이 필요하다.
8. 현재 step, completion criteria, applicable standard를 복구할 수 없다.
9. 기존 사용자 또는 다른 agent 변경을 덮어쓸 risk가 있다.
10. verification을 실행할 수 없거나 실패 원인이 불명확하다.

## 관련 active work

- `00_docs/works/00_KEY-index.md`

## 관련 child 기준서

- `00_docs/standards/skills/reader/KEY-standard-reader.md`
- `00_docs/standards/skills/author/KEY-standard-author.md`
- `00_docs/standards/skills/clarify/KEY-standard-clarify.md`
- `00_docs/standards/skills/coordinator/KEY-standard-coordinator.md`
