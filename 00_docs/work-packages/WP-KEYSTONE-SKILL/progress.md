# WP-KEYSTONE-SKILL 진행 기록(5)

## 현재 Step

S01

## 마지막 수락 Step

None

## Step 상태

| Step | Status | Main Acceptance | Notes |
|---|---|---|---|
| S01 | in_progress | pending | 문서 기반을 작성 중이며 main session acceptance가 필요하다 |
| S02 | planned | pending | S01 acceptance 이후 네 개 스킬의 Keystone contract를 정의한다 |
| S03 | planned | pending | S02 acceptance 이후 초기 Keystone skill set을 구현한다 |

## 최근 Worker 결과

- None

## 최근 Reviewer 결과

- None

## 보류 결정

- 현재 `work-packages/WP-KEYSTONE-SKILL` 문서를 향후 `works/` tree로 migration할지
  결정한다.
- S02가 시작된 뒤 optional `scope.md`가 필요한지 결정한다.

## 누적 발견사항

### 초기 상태

- 프로젝트 시작 시점에 이 저장소에는 기존 `00_docs/` directory가 없었다.
- `docs/convention.md` 파일은 발견되지 않았다.
- 초기 local verification은 Git diff/status에 의존할 수 없었다. 이는 historical
  context이며 현재 repository state를 설명하지 않을 수 있다.

### 프로젝트 성격과 산출물

- Keystone은 단일 스킬 프로젝트가 아니라 skill-system 프로젝트다.
- 최종 산출물은 네 개의 독립 스킬이다: policy/scope/document clarification,
  standards/work-order authoring, standards/work-order reading and work
  preparation, subagent coordination.
- `work-package-doc-architect`와 `subagent-work-coordinator`는 참고용 prototype이며
  최종 의존성으로 남기지 않고 대체할 예정이다.
- Keystone은 자동 적용되지 않고 사용자가 명시적으로 호출해야 한다.

### 문서와 설정 정책

- Keystone은 날짜 기반 일회성 plan document에서 context가 반복되지 않도록 재사용 가능한
  policy는 기준서에, 현재 execution은 작업서에 둔다.
- 향후 문서 경로는 영어다. `00_docs/`는 기본 root이지 고정 root가 아니다. 현재
  사용자 지시는 현재 run을 override할 수 있다. 지속되는 project-local setting은
  `.keystone/config.local.yaml`, `.keystone/config.yaml`, project-local agent
  instruction file 안의 명시적 Keystone setting 순서로 해석한다. Common/global
  instruction file은 setup suggestion일 뿐이다.
- Initial shared Keystone project setup은 Keystone을 사용하는 target project에서
  Plan Mode setup question 이후 `.keystone/config.yaml`에 기록해야 한다. 개인용,
  로컬 전용, 민감한 override는 `.keystone/config.local.yaml`에 둔다.
- 이 저장소는 Keystone 스킬 자체를 정의하고 구현한다. 이후 fixture 또는 test step이
  명시적으로 요구하지 않는 한 S01 또는 S02 동안 `.keystone/config.yaml`이 필요하지
  않다.
- 기준서와 작업서 Git policy는 project setting이며 네 가지 선택지가 있다: 둘 다
  track, 기준서만 track, 둘 다 track하지 않음, 매번 묻기. 파생 에이전트 문서(8)는
  기본적으로 ignore한다.
- Keystone을 사용하는 target project에서 `.keystone/config.yaml`은 shared project
  policy로서 기본적으로 Git에 track한다. `.keystone/config.local.yaml`은 local/private
  override로서 기본적으로 Git에서 ignore한다.
- Sensitive setting이나 document는 쓰기, track, publish, 파생 에이전트 문서(8) 생성 전에
  사용자 확인이 필요하다.
- Keystone output language policy는 Keystone artifact에만 적용되며 관련 없는 task
  language, code comment, commit message, README file, external tool, non-Keystone
  skill을 override해서는 안 된다.
- 이 Keystone 스킬 구현 저장소의 원천 문서(2) 기본 언어는 한국어다. 파일 경로,
  설정 key, schema value, status value, skill name, step ID, decision ID, standard
  ID처럼 기계적으로 참조되는 literal은 영어 또는 기존 값을 유지한다.
- 향후 기준서는 `standards/` 아래에, 향후 작업서는 `works/` 아래에 둔다. 두 tree는
  깊이 제한 없는 folder node와 `00_index.md`를 사용한다.
- 최종 기준서 file은 `standard-{slug}.md`, 최종 작업서 file은 `work-{slug}.md`,
  progress file은 `progress.md`를 사용한다.

### 역할과 workflow

- Superpowers는 brainstorming, planning, TDD, debugging, review, skill testing을
  위한 선택적 supporting workflow로 통합할 수 있지만, 수락된 Keystone 기준서(3)와
  작업서(4)가 계속 권위를 가진다.
- Main agent는 supervisor로 동작해야 한다. Context를 보존하고, role-based goal을
  subagent에게 배정하며, report를 받고, repair를 결정하고, final acceptance
  결정(6)을 내린다.
- Subagent는 explorer, code modifier, reviewer, verifier 같은 role 기반이어야 하며,
  parallel speed보다 correctness와 context preservation을 우선해야 한다.
- 최종 스킬 이름은 `keystone-clarify`, `keystone-author`, `keystone-reader`,
  `keystone-coordinator`다.
- `keystone-clarify`는 high-impact topic 결정(6)을 위한 스킬이다. Plan Mode에서
  관련 질문을 수집하고, 사용 가능한 경우 `request_user_input` 또는 동등한 selection
  UI를 선호하며, reflection과 edit plan을 요약한 뒤 Default Mode에서 관련 원천
  문서(2)를 함께 업데이트해야 한다.
- 작업서 step은 `Goal`, `Scope`, `Source Context`, `Completion Criteria`,
  `Stop Conditions`, `Verification`, `Expected Output`을 요구한다. `Suggested Role`은
  선택 사항이며 delegation 가능성이 클 때 권장한다.

### Reader, 상태, 검증

- `keystone-reader`는 Orientation, Navigator, Work Prep mode를 가진다.
- Orientation Mode는 document-led, repository-aware, read-only다. 출력에는 document
  root, project summary, shallow repository snapshot, active document map, current
  work status, recommended read order, operational boundaries, risks/gaps, next
  action, sources read, assumptions가 포함되어야 한다. Document와 repository state 사이에
  충돌이 있으면 문서나 code를 수정하지 않고 mismatch를 보고하며 사용자/main 결정(6)을
  요청한다.
- 파생 에이전트 문서(8) type은 optional 네 가지로 유지하며 필요할
  때만 생성한다.
- 진행 상태(progress status)와 subagent report status는 별개다. Progress는 `planned`, `ready`,
  `in_progress`, `assigned`, `reported`, `reviewing`, `verifying`, `accepted`,
  `blocked`를 사용한다.
- Verification은 standards-led다. Main은 기준서에서 criteria를 추출해 Verification
  Checklist로 만들고 필요하면 verifier Goal을 배정한다.

### 구현 위치

- Repository-local `skills/`는 초기 Keystone skill implementation의 최종 권위(source of
  truth)다.

### S01 acceptance review

- S01 최소 문서 set은 모두 존재하며, S01은 구조적으로 acceptance review 대상이 될 수 있다.
- 최상위 공통 기준서는 project goal, 공통 용어, 문서 흐름, 스킬 목록, 공통 정책을
  담는 parent 기준서 역할로 거의 정리되어 있다.
- 스킬별 상세 기준서는 아직 별도 child 기준서로 분리되지 않았다. S02의 핵심 작업은
  네 개 스킬의 trigger, non-trigger, input, output, workflow, verification, stop
  condition을 스킬별 기준서로 정의하는 것이다.
- 현재 가장 구체화된 스킬은 `keystone-reader`다. Reader는 Orientation, Navigator,
  Work Prep mode와 Orientation output이 이미 공통 기준서에 정의되어 있으므로 첫 번째
  스킬별 child 기준서 후보로 적합하다.
- `keystone-clarify`는 topic-scoped decision collection과 document update 흐름이 일부
  정의되어 있고, `keystone-author`와 `keystone-coordinator`는 아직 큰 책임 수준의
  설명만 있으므로 S02에서 상세 계약이 필요하다.

### S02 Reader child 기준서 초안

- `keystone-reader` child 기준서 초안을 `00_docs/standards/skills/reader/standard-reader.md`
  에 작성했다.
- 이 초안은 `STD-KEYSTONE-019`를 상세화하며, Reader의 trigger, non-trigger,
  required input, Orientation/Navigator/Work Prep mode, mismatch handling, stop
  condition, verification을 정의한다.
- 이 작업은 skill implementation을 시작하지 않으며, S01 또는 S02 acceptance 상태를
  변경하지 않는다.

## 다음 권장 작업

Step S01 amend와 `keystone-reader` child 기준서 초안을 검토해 accept한 뒤 S02를 이어서
진행한다. 다음 S02 작업은 `keystone-clarify`, `keystone-author`, `keystone-coordinator`의
스킬별 child 기준서 계약을 정의하는 것이다.
