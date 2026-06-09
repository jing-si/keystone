# Keystone 프로젝트 기준서

## 목적

이 기준서는 Keystone 스킬 시스템을 만들기 위한 프로젝트 공통 규칙을 정의한다.
프로젝트 목표는 사람이 읽을 수 있는 문서를 바탕으로 네 개의 독립 스킬을 만드는 데
있다.

1. 기준서(3)와 작업서(4)를 원천 문서(2)로 삼는다.
2. clarification, authoring, reading, main-agent to subagent 작업을 구조화한다.
3. 네 개의 Keystone 스킬이 독립적으로 동작하되 같은 문서 체계를 공유하게 한다.

## 적용 범위

- 설정된 document root(1) 아래의 기준서(3)와 작업 패키지(work package)
- 향후 Keystone 스킬 source file
- Keystone 프로젝트 설정과 프로젝트 로컬 Keystone 설정
- 정책, 범위, 문서, 스킬 계약을 명확히 하는 clarification 동작
- 기준서/작업서 authoring 동작
- 기준서/작업서 reading 및 work-preparation 동작
- main agent와 subagent 사이의 runtime coordination 동작
- 향후 Keystone coordination 스킬과 호환되어야 하는 문서

## 적용하지 않는 범위

- 관련 없는 로컬 IDE 파일
- 참고용 prototype으로 사용하는 경우를 제외한 외부 설치 스킬
- 사용자 명시 호출 또는 수락된 Keystone 문서 규칙 없이 외부 workflow 스킬을
  자동으로 사용하는 동작
- 명시적으로 요청되지 않은 persistent worker handoff 문서

## 표준 용어

표준 용어는 Keystone 문서 전체에서 같은 개념을 같은 이름으로 쓰기 위한 기준이다. 새
문서를 작성하거나 기존 문서를 수정할 때는 먼저 이 section을 확인한다.

첨자 규칙은 다음과 같다.

1. `(1)`, `(2)` 같은 첨자가 붙은 용어는 이 section에 정의된 표준 용어로 판단한다.
2. 표준 용어 정의는 `(n) 선호 언어명(영문명): 짧은 설명` 형식을 따른다.
3. 본문에서는 `설정된 document root(1)`처럼 선호 언어명 바로 뒤에 첨자를 붙이고
   영문명은 반복하지 않는다.
4. 첨자가 붙은 용어를 해석하거나 수정할 때는 이 section의 의미, 권위 규칙, 사용 규칙을
   먼저 확인한다.
5. 새 표준 용어가 필요하면 기존 첨자와 충돌하지 않는 새 번호를 추가한다.
6. 문서나 절에서 처음 등장하거나 혼동 가능성이 있는 위치에 첨자를 붙인다.

(1) 설정된 document root(configured document root): Keystone 원천 문서 root directory

- 의미: `STD-KEYSTONE-015`의 document root resolution 결과로 정해진 Keystone 원천 문서
  root directory
- 기본값: 별도 설정이 없을 때 `00_docs/`
- 권위 규칙: `STD-KEYSTONE-015`
- 사용 규칙: 실제 위치를 직접 쓰지 말고 `설정된 document root(1)`라고 쓴다. 기본값을
  설명하거나 예시 path를 보여줄 때만 `00_docs/`를 언급한다.

(2) 원천 문서(source document): 사람이 읽을 수 있고 권위를 가지는 Keystone 문서

- 의미: 사람이 읽을 수 있고 권위를 가지는 Keystone 문서
- 권위 규칙: `STD-KEYSTONE-001`
- 사용 규칙: agent-facing runtime pack, handoff, reviewer brief와 구분한다.

(3) 기준서(standard): 재사용 가능한 정책, 표준, 도메인 규칙 문서

- 의미: 재사용 가능한 정책, 표준, 도메인 규칙 문서
- 권위 규칙: `STD-KEYSTONE-002`, `STD-KEYSTONE-016`, `STD-KEYSTONE-017`
- 사용 규칙: 장기 정책과 반복 가능한 guidance는 기준서에 둔다.

(4) 작업서(work order): 현재 AI 작업의 목표, 범위, 순서, 검증 경로 문서

- 의미: 현재 AI 작업의 목표, 범위, 순서, 검증 경로 문서
- 권위 규칙: `STD-KEYSTONE-002`, `STD-KEYSTONE-018`
- 사용 규칙: subagent-sized Goal unit과 verification path를 복구할 수 있게 작성한다.

(5) 진행 기록(progress record): 현재 step과 workflow 상태를 복구하는 문서

- 의미: 현재 step과 workflow 상태를 복구하는 문서
- 권위 규칙: `STD-KEYSTONE-022`
- 사용 규칙: implementation complete 같은 완료 상태는 main acceptance 이후에만 표시한다.

(6) 결정(decision): 수락된 정책 또는 설계 선택

- 의미: 수락된 정책 또는 설계 선택
- 권위 규칙: `STD-KEYSTONE-021`, `STD-KEYSTONE-025`
- 사용 규칙: 여러 문서에 영향을 주는 결정은 관련 원천 문서와 함께 일관되게 기록한다.

(7) 범위 문서(scope document): 필요할 때만 추가하는 상세 범위 문서

- 의미: 필요할 때만 추가하는 상세 범위 문서
- 권위 규칙: `STD-KEYSTONE-008`
- 사용 규칙: 작업서의 Scope만으로 부족할 때만 추가한다.

(8) 파생 에이전트 문서(derived agent document): 원천 문서에서 파생되는 agent-facing 문서

- 의미: 원천 문서에서 파생되는 agent-facing 문서
- 권위 규칙: `STD-KEYSTONE-020`, `STD-KEYSTONE-021`, `STD-KEYSTONE-027`
- 사용 규칙: 원천 문서가 아니며, 원천 문서와 충돌하면 원천 문서가 우선한다.

## 핵심 규칙

### STD-KEYSTONE-001: 사람이 읽을 수 있는 원천 문서(2)가 권위다

원천 문서(2)는 사람이 읽을 수 있어야 하며 다음 문서를 포함한다.

1. 기준서(3): 프로젝트 정책, 표준, 재사용 가능한 guidance를 담는다.
2. 작업서(4): 현재 AI 작업의 목표, 범위, 순서, 검증 경로를 담는다.
3. 진행 기록(5): 현재 step, 상태, 수락 여부를 담는다.
4. 결정(6)과 결정 기록(decision record): 수락된 정책 결정을 담는다.
5. 범위 문서(7): 필요할 때만 별도로 추가하는 상세 범위를 담는다.

파생 자료는 다음 원칙을 따른다.

1. agent-facing runtime pack, handoff, reviewer brief는 원천 문서에서 파생된다.
2. 파생 자료는 원천 문서를 덮어쓸 수 없다.
3. 원천 문서와 파생 자료가 충돌하면 원천 문서가 우선한다.

### STD-KEYSTONE-002: 기준서(3)와 작업서(4)는 책임이 다르다

책임은 다음처럼 나눈다.

1. 기준서: 프로젝트 정책, 표준, 도메인 규칙, 재사용 가능한 guidance를 정의한다.
2. 작업서: AI 작업의 구체적 목표, 범위, 순서, 완료 기준, 중단/보고 조건, 검증
   경로를 정의한다.

기준서를 새로 만들거나 큰 기준서를 정리할 때는 구조화된 양식을 우선한다.

1. 짧은 목적 문단으로 해당 기준서가 다루는 대상을 먼저 밝힌다.
2. 핵심 개념, 책임, 절차, 조건, 예외는 긴 문단보다 번호 목록으로 나눈다.
3. 용어 정의는 필요한 경우 `(n) 선호 언어명(영문명): 짧은 설명` 형식으로 정리한다.
4. 정의된 용어를 본문에서 참조할 때는 `선호 언어명(n)`처럼 쓴다.
5. 여러 항목을 비교하거나 나열할 때는 항목별로 `이름: 설명` 구조를 사용한다.
6. 표가 가로로 길어져 읽기 어려우면 항목별 subsection 또는 decision block으로 푼다.
7. 기계적으로 참조되는 ID, path, status, field name은 기존 literal 값을 유지한다.
8. 이미 다른 STD에서 명문화한 규칙은 반복 정의하지 말고 해당 STD ID를 참조한다.
9. 새 규칙을 추가하기 전에 기존 STD가 같은 책임을 이미 다루는지 확인한다.
10. 기존 STD를 참조할 때는 참조 대상과 적용 이유를 함께 적는다.

### STD-KEYSTONE-003: 기준서는 parent-child 계층을 가질 수 있다

큰 기준서는 필요할 때 parent/child 구조로 나눌 수 있다.

1. 기본 흐름: Keystone 기준서는 전체 공통 기준서에서 시작해 필요한 경우 스킬별 child
   기준서로 내려간다.
2. 전체 공통 기준서 역할: 프로젝트 목표, 공통 용어, 문서 흐름, 스킬 목록, 공통 정책,
   관련 child 기준서 link를 요약한다.
3. 스킬별 기준서 역할: 개별 스킬의 trigger, non-trigger, input, output, workflow,
   verification, stop condition 같은 상세 계약을 담는다.
4. 분리 기준: 하나의 기준서가 여러 feature나 상세 규칙을 함께 다뤄 읽기 어려워질 때
   나눈다.
5. Parent 기준서 역할: feature 이름, 짧은 설명, reference document를 요약한다.
6. Child 기준서 역할: 현재 작업에 필요한 최종 상세 규칙을 담는다.
7. Navigation 목적: main이 parent 기준서를 읽고 필요한 최종 상세 기준서로 이동할 수
   있어야 한다.
8. 분리 시점: 실제 파일 분리는 관련 contract가 충분히 수락되어 child 기준서의 책임이
   안정됐을 때 진행한다.

### STD-KEYSTONE-004: Coordinator 호환성은 일급 요구사항이다

모든 작업서(4) step은 향후 coordinator가 필요한 runtime 자료를 도출할 수
있을 만큼 충분한 정보를 포함해야 한다.

1. Current Step Brief: 현재 step의 목표와 범위를 요약할 수 있어야 한다.
2. Context Pack: worker나 reviewer가 읽어야 하는 문서와 제한 조건을 추출할 수 있어야 한다.
3. Worker handoff boundary: 위임 가능한 작업과 금지 범위를 구분할 수 있어야 한다.
4. Reviewer focus: reviewer가 확인해야 하는 위험과 완료 기준을 파악할 수 있어야 한다.
5. Stop condition: 중단하거나 main/user에게 보고해야 하는 조건을 알 수 있어야 한다.
6. Verification path: 허용된 검증 방법을 확인할 수 있어야 한다.

### STD-KEYSTONE-005: Main이 orchestration 결정을 담당한다

Main과 subagent의 책임은 다음처럼 나눈다.

1. Main: orchestration 결정을 담당한다.
2. Main: subagent에게 구체적 context를 제공한 뒤에만 작업을 위임한다.
3. Subagent: read-only 조사, bounded implementation, diff review처럼 경계가 명확한 작업만
   수행한다.
4. Subagent 금지: 전체 작업서(4)를 재해석해서는 안 된다.
5. Subagent 금지: 범위를 확장하거나 추가 subagent를 생성해서는 안 된다.

### STD-KEYSTONE-006: 작업은 문서에서 복구 가능해야 한다

사용자가 "run the next step"이라고 말하면 main은 설정된 document root(1)에서 다음
정보를 복구할 수 있어야 한다.

1. 현재 step
2. goal
3. completion criteria
4. applicable standards
5. expected scope
6. risks
7. verification

### STD-KEYSTONE-007: 원천 문서(2) 변경에는 명시적 승인이 필요하다

원천 문서 변경은 다음 승인 규칙을 따른다.

1. 명시적 승인이 필요한 변경: 수락된 기준서, 작업서, scope, acceptance criteria,
   progress state를 의미 있게 바꾸는 변경
2. Step 진행 중 허용되는 변경: 작업 step이 `in_progress`인 동안 승인된 작업 범위 안의
   수정
3. 진행 중에도 다시 승인이 필요한 변경: 승인된 goal, scope, acceptance criteria,
   status semantics, 원천 문서(2) authority를 바꾸는 변경
4. 미승인 관련 변경 처리: 조용히 적용하지 말고 보고한다.

### STD-KEYSTONE-008: 확장보다 최소 구조가 먼저다

문서 구조는 필요한 만큼만 확장한다.

1. 먼저 `STD-KEYSTONE-015`의 document root resolution과 `STD-KEYSTONE-016`의
   standards/works tree 규칙을 따른 최소 구조를 사용한다.
2. Scope는 작업에 필요할 때만 추가한다.
3. 결정(6)은 수락된 정책이나 설계 선택을 기록해야 할 때만 추가한다.
4. Coordination 문서는 실제 조율 필요가 생길 때만 추가한다.
5. Change request는 변경 요청을 따로 추적해야 할 때만 추가한다.
6. 파생 에이전트 문서(8)는 runtime handoff나 review에 필요할 때만
   추가한다.

### STD-KEYSTONE-009: Keystone 스킬은 명시적으로 호출된다

Keystone 스킬 호출은 다음 규칙을 따른다.

1. 사용자가 원하는 Keystone 스킬을 명시적으로 이름 붙여 호출한다고 가정한다.
2. 스킬 시스템은 광범위한 자동 activation에 의존해서는 안 된다.
3. Superpowers 같은 다른 workflow 스킬은 사용자가 호출했거나 수락된 Keystone 기준서
   또는 작업서가 명시적으로 허용한 경우에만 사용한다.

### STD-KEYSTONE-010: 기준서는 반복 context를 줄인다

기준서와 작업서는 반복 context를 줄이기 위해 다음처럼 협력한다.

1. 기준서: 장기적으로 유지되는 프로젝트 정책, 아키텍처, convention, 도메인 규칙,
   재사용 가능한 결정을 둔다.
2. 작업서: 같은 정책을 날짜별 또는 일회성 task 문서마다 반복해서 복사하지 않는다.
3. 작업서: 필요한 정책은 해당 기준서를 참조한다.

### STD-KEYSTONE-011: 작업서는 goal assignment를 위해 작업을 나눈다

작업서는 명확한 goal로 배정할 수 있는 단위로 작업을 나누어야 한다. 각 단위는 다음
정보를 가져야 한다.

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
7. 최종 acceptance decision을 내린다.

### STD-KEYSTONE-013: Subagent는 속도 우선이 아니라 role 기반이다

Subagent 운영은 다음 우선순위를 따른다.

1. Role 기준: explorer, code modifier, reviewer, verifier 같은 role로 선택한다.
2. Explorer 용도: explorer는 code work 전용 role이 아니다.
3. Explorer 배정 조건: 문서 작성, 기준 검토, 기존 규칙 중복 확인, repository 조사,
   prototype 비교처럼 read-only 조사가 필요한 경우 별도 Goal로 배정할 수 있다.
4. Explorer 보고 범위: 결정을 확정하지 않고 finding, source, risk, option을 보고한다.
5. Parallelism 조건: goal과 write scope가 명확히 독립적인 경우에만 허용한다.
6. 우선순위: raw speed보다 correctness, context preservation, report quality를 우선한다.

### STD-KEYSTONE-014: Superpowers는 선택적 quality-assist layer다

Superpowers는 선택적 보조 도구로만 사용한다.

1. 사용 가능 시점: 문서 작성이나 구현 설계 중 보조가 필요할 때 사용할 수 있다.
2. Keystone authoring 역할: infra setup 기준서나 작업서의 위치, 형식, 필수 section을
   정의할 수 있다.
3. Superpowers 역할: 해당 section 안의 실제 infra, server, code-development 내용을
   다듬는 데 사용할 수 있다.
4. 권위: Superpowers output은 보조 input이며, 수락 이후에는 Keystone 기준서와 작업서가
   최종 권위(source of truth)다.

### STD-KEYSTONE-015: Document root resolution은 명시적이고 순서가 있다

설정된 document root(1)는 다음 순서로 해석한다.

1. 현재 사용자 지시가 있으면 현재 run의 document root를 override할 수 있다.
2. `.keystone/config.local.yaml`의 프로젝트 로컬 override를 확인한다.
3. `.keystone/config.yaml`의 공유 프로젝트 설정을 확인한다.
4. 프로젝트 로컬 agent instruction file 안의 명시적 Keystone settings block을 확인한다.
5. 위 설정이 없으면 `00_docs/`를 기본 root로 사용한다.

문서 경로는 영어여야 한다. `00_docs/`는 기본 root이지 고정 root가 아니다.
`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `agent.md` 같은 공통 또는 전역 주입
instruction file은 setup suggestion을 제공할 수 있지만, 프로젝트 로컬 설정으로
수락되기 전에는 persistent Keystone setting이 되지 않는다. 설정된 프로젝트 로컬
root가 있으면 `00_docs/`가 없어도 Keystone은 그 root를 사용한다.

### STD-KEYSTONE-016: Standards와 works는 index 기반 tree를 사용한다

향후 기준서와 작업서는 index 기반 tree를 사용한다.

1. 기준서 위치: `standards/` 아래에 둔다.
2. 작업서 위치: `works/` 아래에 둔다.
3. 기준서 흐름: 기준서 tree는 전체 공통 node에서 시작해 필요한 경우 스킬별 child
   node로 내려간다.
4. 스킬별 node: Keystone 스킬별 상세 기준서는 `skills/` 아래의 스킬별 child node에 둘
   수 있다.
5. Tree 깊이: 두 tree는 깊이 제한 없이 확장될 수 있다.
6. Node index: 모든 node는 `00_index.md`를 가진다.
7. Navigation: child link와 공통 규칙은 reader가 하위 문서로 내려가도록 안내한다.
8. Final node: 하위 문서가 없는 node가 final node다.

### STD-KEYSTONE-017: Final detail file은 local slug를 사용한다

Final detail file은 다음 naming rule을 따른다.

1. 최종 기준서 파일: `standard-{slug}.md`
2. 최종 작업서 파일: `work-{slug}.md`
3. Progress file: `progress.md`
4. Slug 기준: 해당 folder 안에서 파일을 명확히 구분할 수 있는 가장 짧은 local name

### STD-KEYSTONE-018: Work step은 Goal unit이다

작업서 step은 assignable Goal unit으로 작성해야 한다. 각 step은 하나의 role-based
subagent assignment로 맡길 수 있을 만큼 작아야 하고, main이 report를 accept, repair,
verify, escalate 중 무엇으로 처리할지 판단할 수 있을 만큼 명확해야 한다.

필수 필드는 다음과 같다.

1. `Goal`: step이 달성해야 하는 목표
2. `Scope`: 포함/제외 범위
3. `Source Context`: 읽어야 하는 기준서와 관련 문서
4. `Completion Criteria`: 완료 판단 기준
5. `Stop Conditions`: 중단하거나 main/user에게 보고해야 하는 조건
6. `Verification`: 허용된 검증 방법
7. `Expected Output`: step 완료 후 남아야 하는 산출물

`Suggested Role`은 선택 사항이며 delegation 가능성이 클 때 권장한다. Main은 role을
선택하거나 override할 수 있다. 단순하거나 낮은 risk step에서는 각 필드의 내용이
짧아도 된다.

### STD-KEYSTONE-019: Reader는 세 가지 mode를 가진다

`keystone-reader`는 read-only로 원천 문서(2)를 읽어 project orientation, document
navigation, work preparation을 지원한다. 상세 계약은
`skills/reader/standard-reader.md`를 따른다.

1. Orientation Mode
   - Project overview와 shallow repository context를 만든다.
2. Navigator Mode
   - 현재 요청과 관련된 기준서(3)와 작업서(4)를 찾는다.
3. Work Prep Mode
   - Final subagent handoff를 확정하지 않은 채 Goal, context, verification,
     role suggestion을 준비한다.
4. Child 기준서
   - Mode별 input, output field, repository snapshot, mismatch handling, stop condition은
     `skills/reader/standard-reader.md`를 따른다.

### STD-KEYSTONE-020: 파생 에이전트 문서(8)는 선택 사항이지만 지원한다

Keystone은 유용할 때 네 가지 파생 에이전트 문서(8) type을 둘 수
있다.

1. Agent pack: `agent/00_agent-pack.md`
2. Step context: `agent/step-context.md`
3. Worker handoff: `agent/worker-handoff.md`
4. Reviewer brief: `agent/reviewer-brief.md`

생성 및 업데이트 규칙은 다음과 같다.

1. 기본적으로 생성하지 않는다.
2. 원천 문서(2)가 바뀌면 영향받는 파생 에이전트 문서(8)도 함께
   업데이트한다.
3. 충돌이 있으면 원천 문서가 항상 우선한다.

### STD-KEYSTONE-021: Impact update는 문서 일관성을 보존한다

Impact update는 다음 규칙을 따른다.

1. 함께 업데이트할 조건: 원천 문서(2) 변경이 관련 parent, child, work,
   progress, 결정(6), 파생 에이전트 문서(8)에 명확히 영향을
   줄 때
2. 중단할 조건: 영향 범위나 의미 변경이 불확실할 때
3. 중단 후 행동: 불확실한 문서를 수정하기 전에 멈추고 사용자에게 묻는다.

### STD-KEYSTONE-022: 진행 상태(progress status)와 report status는 별개다

진행 상태(progress status)와 subagent report status는 분리한다.

1. Progress status: workflow state를 나타낸다.
2. Subagent report status: 반환된 report 상태를 나타낸다.

Progress status 값은 다음과 같다.

1. `planned`
2. `ready`
3. `in_progress`: main이 승인된 work scope 안에서 적극적으로 작업 중임을 의미한다.
4. `assigned`: subagent 또는 별도 worker가 현재 unit을 담당한다는 뜻이다.
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

### STD-KEYSTONE-023: Verification은 기준서가 이끈다

Verification은 다음 책임 분리를 따른다.

1. 기준서: primary verification expectation을 정의한다.
2. Main: 기준서에서 관련 verification criteria를 추출해 Verification Checklist로
   worker에게 전달한다.
3. Main: 필요하면 verifier subagent에게 별도 verification Goal을 배정한다.
4. 작업서: local verification note를 추가할 수 있다.
5. 금지: 작업서는 기준서 verification을 조용히 약화해서는 안 된다.

### STD-KEYSTONE-024: Skill source는 저장소에 둔다

이 저장소는 네 개 Keystone 스킬의 source of truth다.

1. Clarify skill: `skills/keystone-clarify`
2. Author skill: `skills/keystone-author`
3. Reader skill: `skills/keystone-reader`
4. Coordinator skill: `skills/keystone-coordinator`

초기 배포 형태는 skills repo이며, 이후 plugin metadata를 추가할 여지를 둔다.

### STD-KEYSTONE-025: Clarify는 topic-scoped이고 mode-aware다

`keystone-clarify`는 topic-scoped high-impact 결정(6)에 사용한다.

1. 사용 대상: 정책, 원천 문서(2), work scope, skill contract,
   cross-document consistency에 영향을 주는 결정
2. 비사용 대상: 사소한 수정마다 질문을 만들면 안 된다.
3. Plan Mode: 사용 가능한 경우 `request_user_input` 또는 동등한 selection UI를 사용해
   한 topic에 필요한 질문과 결정을 수집한다.
4. 수락 조건: topic이 충분히 결정되고 사용자 또는 main session이 결정(6)
   summary와 edit plan을 수락한다.
5. Reflection: 수락된 reflection과 document update plan을 요약한다.
6. Default Mode: 수락된 관련 원천 문서(2) update를 함께 적용한다.
7. Impact 대상: standards, works, progress, decisions, 선택적 파생 에이전트
   문서(8)를 포함한다.

### STD-KEYSTONE-026: Initial project setup은 Keystone config에 기록한다

이 규칙은 완성된 Keystone 스킬을 사용하는 target project에서의 Keystone 동작을
설명한다. Keystone 스킬 구현 저장소는 이후 구현 또는 테스트 단계에서 fixture나
example config를 명시적으로 요구하지 않는 한 document foundation 또는 contract
definition 동안 `.keystone/config.yaml` 파일이 필요하지 않다.

Target project에서 Keystone initial setup은 다음 순서로 진행한다.

1. 기존 project setting을 확인한 뒤 setup question을 묻는다.
2. Setting이 없거나 document root 결정이 불명확하면 `keystone-clarify`가 Plan Mode에서
   setup question을 묻는다.
3. 사용 가능한 경우 `request_user_input` 또는 동등한 selection UI를 사용한다.
4. 공통 또는 전역 주입 setting은 추천 선택지로 보여줄 수 있지만 조용히 수락해서는 안 된다.
5. 수락된 shared project setting은 기본적으로 `.keystone/config.yaml`에 기록한다.
6. 개인용, 로컬 전용, 민감한 override는 `.keystone/config.local.yaml`에 둔다.
7. 사용자가 기존 프로젝트 로컬 agent instruction file을 명시적으로 선호하면 그곳에
   Keystone settings block을 기록할 수 있다.
8. Keystone은 공통 또는 전역 주입 instruction file에 절대 쓰지 않는다.

Initial setup은 최소한 다음을 다뤄야 한다:

- document root: 기본 `00_docs/`, 기존 project document folder, 또는 새로 지정한
  folder
- 기준서와 작업서의 원천 문서(2) Git policy
- 파생 에이전트 문서(8) Git policy
- Keystone output language policy
- setup storage location: 기본 `.keystone/config.yaml`, 또는 사용자가 선택한 명시적
  project-local agent instruction file

기본 shared config schema는 다음과 같다:

```yaml
version: 1
document_root: 00_docs
source_docs_git_policy: track_standards_and_works
derived_agent_docs_git_policy: ignore
output_language_policy: dominant_conversation_language
```

### STD-KEYSTONE-027: 원천 문서(2) Git policy는 명시적이다

Keystone은 기준서와 작업서를 원천 문서(2)로 취급하지만, Git publication
policy는 가정이 아니라 project setting이다.

Target project의 initial setup에서 `keystone-clarify`는 tradeoff를 설명하고 다음 선택지를
제공해야 한다.

1. 기준서와 작업서를 모두 track
2. 기준서만 track
3. 둘 다 track하지 않음
4. document change마다 묻기

기본 Git policy는 다음과 같다.

1. 파생 에이전트 문서(8): 명시적으로 승인되지 않는 한 기본적으로
   Git에서 ignore한다.
2. `.keystone/config.yaml`: shared project policy이며 기본적으로 Git에 track한다.
3. `.keystone/config.local.yaml`: local/private override이며 기본적으로 Git에서 ignore한다.

민감한 내용은 쓰기, track, publish, document derivation 전에 사용자 확인이 필요하다.
민감한 내용에는 다음이 포함된다.

1. Secret
2. Credential
3. Private user data
4. Customer data
5. Local-only path
6. Sensitive environment detail
7. Unpublished business information

### STD-KEYSTONE-028: Output language policy는 Keystone artifact에만 적용한다

Output language policy는 project setting으로 선택할 수 있다.

1. Target project: Keystone output language policy를 project setting으로 선택한다.
2. 이 구현 저장소: S01/S02 원천 문서(2) 작성과 검토는 한국어를 기본으로
   한다.
3. Literal 유지: 파일 경로, 설정 key, schema value, status value, skill name, step ID,
   decision ID, standard ID처럼 기계적으로 참조되는 식별자는 영어 또는 기존 literal 값을
   유지한다.

핵심 Keystone 문서 용어는 `## 표준 용어`의 첨자 규칙을 따른다. 선호 언어명은 해당
target project의 Keystone output language policy를 따른다. 이 구현 저장소의 S01/S02
문서에서는 선호 언어가 한국어이므로 한국어 용어를 앞에 둔다. 이후 같은 문서나 절에서는
선호 언어명을 우선 사용한다.

적용 범위는 다음으로 제한한다.

1. Clarification prompt
2. 기준서
3. 작업서
4. Keystone summary
5. Handoff
6. Report

적용하지 않는 범위는 다음과 같다.

1. 관련 없는 task
2. Code comment
3. Commit message
4. README file
5. External tool
6. Non-Keystone skill

Initial setup은 다음과 동등한 선택지를 제공해야 한다.

1. 현재 대화의 dominant language
2. 기존 project document language
3. English
4. 매번 묻기

사용자가 특정 task의 언어를 명시적으로 요청하면 그 task-specific instruction이 우선한다.

## 기대 동작

Keystone은 다음 동작을 지원해야 한다.

1. Project orientation
   - Main agent는 설정된 document root(1) 아래의 `context-map.md`를 확인해 활성 기준서와
     작업 패키지를 찾을 수 있다.
   - Main agent는 작업 패키지를 확인하고 `progress.md`에서 현재 step을 식별할 수 있다.
2. Clarification
   - Clarification 스킬은 원천 문서(2)가 변경되기 전에 topic-scoped
     high-impact 결정(6)을 수집할 수 있다.
3. Project setup
   - Keystone은 target project의 `.keystone/config.yaml`에 initial project setting을
     기록하고 이후 run에서 재사용할 수 있다.
4. Document reading
   - Document-reading 스킬은 현재 요청 작업에 필요한 관련 기준서와 작업서만 찾을 수 있다.
   - Document-reading 스킬은 사용자 요청에 따라 Orientation, Navigator, Work Prep Mode를
     실행할 수 있다.
   - 사람과 LLM은 관련 없는 branch를 불러오지 않고 `00_index.md`를 따라 standards와
     works tree를 아래로 탐색할 수 있다.
5. Work execution
   - 재사용 가능한 기준서는 반복 task document에서 공통 정책을 제거한다.
   - 작업서(4) step은 subagent가 전체 프로젝트를 다시 파악하지 않아도 되는
     bounded subagent task로 변환될 수 있다.
   - Main agent는 role-based goal을 subagent에게 배정하고 report를 바탕으로 최종 결정을
     내릴 수 있다.
6. Supporting workflow
   - Superpowers는 Keystone 원천 문서(2)를 대체하지 않는 명시적 supporting
     workflow로 사용할 수 있다.
7. Document policy
   - 파생 에이전트 문서(8)는 유용할 때 생성할 수 있지만 원천 문서가
     되지는 않는다.
   - 기준서와 작업서 Git policy는 파생 에이전트 문서를 기본 track하지 않으면서 project별로
     선택할 수 있다.
   - Shared Keystone config는 track할 수 있고 local/private override는 기본적으로 ignore
     상태를 유지한다.
   - Keystone artifact language는 관련 없는 task language를 바꾸지 않으면서 설정할 수 있다.
8. Risk handling
   - High-risk work는 구현 전에 main 또는 사용자 결정이 필요하다고 문서화된다.

## 재사용할 기존 패턴

1. `work-package-doc-architect`: 향후 authoring 스킬의 참고용 prototype으로 문서 구조와
   template를 참고한다.
2. `subagent-work-coordinator`: 향후 coordination 스킬의 참고용 prototype으로 orchestration
   loop, Context Pack 규칙, scope model, stop condition, review loop를 참고한다.

## 승인 없이 금지되는 변경

1. Goal 변경: Keystone 스킬 시스템 goal의 의미를 바꾸기
2. Skill boundary 변경: 승인 없이 네 개의 계획된 Keystone 스킬을 하나로 합치기
3. Prototype dependency 변경: prototype 스킬을 최종 의존성으로 취급하기
4. Clarification 미완료 변경: 완료되지 않은 high-impact clarification topic에서 원천
   문서(2) 수정하기
5. Document root 변경: 현재 instruction file과 project-local Keystone setting을 확인하기
   전에 새 document root 만들기
6. Setup storage 위반: Keystone setup result를 공통 또는 전역 주입 instruction file에 쓰기
7. Persistent setting 오인: 공통/전역 instruction setting을 project-local acceptance 없이
   persistent project setting으로 취급하기
8. Sensitive document 처리: 명시적 승인 없이 민감한 원천 문서(2)를 track하거나
   publish하기
9. Language override: Keystone output language가 관련 없는 사용자 요청, code, commit,
   README file, external tool, non-Keystone skill을 override하게 하기
10. External workflow 자동 호출: 사용자 지시 또는 수락된 document authorization 없이
    Superpowers 또는 외부 workflow 스킬을 자동 호출하기
11. Context 반복: 재사용 가능한 기준서를 반복되는 날짜별 task document로 대체하기
12. Work tree 위반: 사용자 승인 없이 future active 작업서를 `works/` 대신
    `work-packages/` 아래에 만들기
13. Leaf metadata 추가: child presence로 final node 여부가 결정되는 곳에 `leaf` metadata
    field 추가하기
14. Source authority 위반: 파생 에이전트 문서(8)를 원천 문서(2)로 취급하기
15. Acceptance 위반: Main acceptance 전에 work를 complete로 표시하기
16. Handoff 기본 생성: persistent agent-facing handoff document를 기본 생성하기
17. Scope 확장: 작업서(4) step과 승인 없이 implementation code, schema,
    generated output, global configuration change로 확장하기

## Escalation 조건

1. Source conflict: 원천 문서(2)가 현재 사용자 방향과 충돌한다.
2. Skill boundary gap: 네 개의 계획된 Keystone 스킬 사이 경계가 불명확하다.
3. Clarification gap: high-impact clarification topic을 확신 있게 해결할 수 없다.
4. Setup uncertainty: initial project setting이 없고 document root, Git policy,
   Keystone output language를 안전하게 추론할 수 없다.
5. Authority risk: 요청된 workflow가 Superpowers output을 수락된 Keystone 기준서나
   작업서보다 더 권위 있게 만들 수 있다.
6. Assignment gap: work unit을 reviewable output이 있는 명확한 goal로 배정할 수 없다.
7. Impact uncertainty: 문서 변경이 관련 standards, works, progress, decisions,
   파생 에이전트 문서(8)에 미치는 영향이 불명확하다.
8. High-risk implementation need: step이 API contract, schema, auth/security,
   generated/codegen, shared architecture change를 필요로 한다.
9. Recovery gap: 현재 step, completion criteria, applicable standard를 확신 있게 복구할 수
   없다.
10. Overwrite risk: subagent result가 사용자 또는 다른 agent의 변경을 덮어쓸 수 있다.
11. Verification gap: verification을 실행할 수 없거나 실패 원인이 불명확하다.

## 관련 작업 패키지

- `00_docs/work-packages/WP-KEYSTONE-SKILL/00_index.md`

## 관련 child 기준서

- `00_docs/standards/skills/reader/standard-reader.md`
