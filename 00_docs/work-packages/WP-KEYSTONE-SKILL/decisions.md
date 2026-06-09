# WP-KEYSTONE-SKILL 결정 기록(decision record)

이 문서는 수락된 Keystone 정책 결정(6)을 기록한다. 이 문서가 기준서(3)
또는 작업서(4)와 충돌하면 파생 에이전트 문서(8)나
implementation plan을 사용하기 전에 원천 문서(2) 간 충돌을 먼저 해결한다.

## 결정 목록

### DEC-001

- 수락 단계: S01
- 영향 단계: S02
- 상태: accepted
- 결정: Keystone 최종 산출물은 `keystone-clarify`, `keystone-author`,
  `keystone-reader`, `keystone-coordinator` 네 개의 독립 스킬이다.
- 이유: clarification, authoring, reading/preparation, coordination 책임을 분리해
  유지한다.

### DEC-002

- 수락 단계: S01
- 영향 단계: S02
- 상태: accepted
- 결정: 문서 경로는 영어를 사용한다. `00_docs/`는 기본 root이지 고정 root가 아니다.
  현재 사용자 지시는 현재 run을 override할 수 있다. 지속되는 project-local setting은
  `.keystone/config.local.yaml`, `.keystone/config.yaml`, project-local agent
  instruction file 안의 명시적 Keystone settings 순서로 해석한다. Common/global
  instruction file은 setup suggestion일 뿐이다.
- 이유: 경로를 portable하게 유지하고 project-local setting을 지속적인 권위로 삼기
  위해서다.

### DEC-003

- 수락 단계: S01
- 영향 단계: S02
- 상태: accepted
- 결정: 향후 기준서는 `standards/`, 향후 작업서는 `works/`를 사용한다. 두 tree는
  깊이 제한 없는 folder tree이며 모든 node에 `00_index.md`를 둔다.
- 이유: 사람과 LLM이 index를 따라 아래로 이동하게 하여 필요한 context를 줄인다.

### DEC-004

- 수락 단계: S01
- 영향 단계: S02
- 상태: accepted
- 결정: 최종 상세 파일은 `standard-{slug}.md`, `work-{slug}.md`, `progress.md`를
  사용한다.
- 이유: filename에 전체 path 의미를 반복하지 않으면서 최종 문서를 식별할 수 있게
  한다.

### DEC-005

- 수락 단계: S01
- 영향 단계: S02
- 상태: accepted
- 결정: 명시적 leaf metadata는 필요 없다. 하위 문서가 없는 node가 final node다.
- 이유: 중복 metadata를 피하고 문서가 자연스럽게 읽히게 한다.

### DEC-006

- 수락 단계: S01
- 영향 단계: S02
- 상태: accepted
- 결정: 상위 기준서와 상위 작업서는 summary, link, scope, common rule을 포함할 수
  있다. 최종 기준서는 상세 rule을 담고, 최종 작업서는 execution step을 담는다.
- 이유: 기준서와 작업서의 서로 다른 목표를 유지하면서 하나의 node model을 공유한다.

### DEC-007

- 수락 단계: S01
- 영향 단계: S02
- 상태: accepted
- 결정: 작업서 step은 subagent assignment를 위한 Goal unit이다.
- 이유: 작업을 자연스럽게 배정하고 검토할 수 있게 만든다.

### DEC-008

- 수락 단계: S01
- 영향 단계: S02
- 상태: accepted
- 결정: `keystone-reader`는 Orientation, Navigator, Work Prep mode를 가진다.
- 이유: 초기 project orientation, targeted document navigation, goal preparation을
  지원하되 reading과 clarification ownership을 섞지 않는다.

### DEC-009

- 수락 단계: S01
- 영향 단계: S02
- 상태: accepted
- 결정: 선택적 파생 에이전트 문서(8)는
  `agent/00_agent-pack.md`, `agent/step-context.md`, `agent/worker-handoff.md`,
  `agent/reviewer-brief.md` 네 type을 유지한다. 필요할 때만 생성한다.
- 이유: LLM-friendly handoff를 지원하되 기본 maintenance cost가 되지 않게 한다.

### DEC-010

- 수락 단계: S01
- 영향 단계: S02
- 상태: accepted
- 결정: 원천 문서(2) 변경은 명확히 영향받는 관련 원천 문서와 파생 에이전트 문서(8)를
  함께 업데이트해야 한다. 영향이 불확실하면 멈추고 묻는다.
- 이유: 불확실한 의미 변경을 추측하지 않으면서 문서 일관성을 보존한다.

### DEC-011

- 수락 단계: S01
- 영향 단계: S02
- 상태: accepted
- 결정: Main은 supervisor다. Implementation 또는 bounded multi-file work의 실제
  수정은 보통 main이 구체적 context를 준비한 뒤 role-based subagent에게 위임한다.
  Main은 승인된 작업 범위 안에 머무르는 low-risk document foundation work, typo fix,
  small local 원천 문서(2) edit, acceptance update를 직접 수행할 수 있다.
- 이유: Main context를 보존하면서 S01 foundation work를 main이 직접 완료할 수 있게
  하기 위해서다.

### DEC-012

- 수락 단계: S01
- 영향 단계: S02
- 상태: accepted
- 결정: 기본 subagent role은 explorer, worker/code-modifier, reviewer, verifier다.
- 이유: Role을 명확하고 보고 가능하게 유지한다.

### DEC-013

- 수락 단계: S01
- 영향 단계: S02
- 상태: accepted
- 결정: Progress status와 report status는 분리한다. Progress는 `planned`, `ready`,
  `in_progress`, `assigned`, `reported`, `reviewing`, `verifying`, `accepted`,
  `blocked`를 사용한다. Report는 `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`,
  `NEEDS_SCOPE_CHANGE`, `BLOCKED`를 사용한다.
- 이유: Workflow state와 subagent report outcome을 분리하기 위해서다.

### DEC-014

- 수락 단계: S01
- 영향 단계: S02
- 상태: accepted
- 결정: Verification은 기준서-led다. Main은 기준서에서 verification criteria를 추출해
  Verification Checklist로 만들고, 필요하면 verifier Goal을 배정한다.
- 이유: Verification을 올바른 policy level에 두고 subagent가 문서를 직접 다시 읽는
  비용을 피한다.

### DEC-015

- 수락 단계: S01
- 영향 단계: S02
- 상태: accepted
- 결정: Superpowers는 사용자가 명시적으로 호출/허용했거나 수락된 Keystone 기준서 또는
  작업서가 특정 supporting use를 허용한 경우에만 사용할 수 있다. Superpowers는
  supporting input이며 Keystone source of truth가 아니다.
- 이유: 명시적 skill invocation을 보존하고 자동 workflow 전환을 피한다.

### DEC-016

- 수락 단계: S01
- 영향 단계: S03
- 상태: accepted
- 결정: 초기 skill source는 repo-local `skills/` 아래에 둔다.
- 이유: Git 저장소를 source of truth로 삼고 향후 plugin packaging 여지를 둔다.

### DEC-017

- 수락 단계: S01
- 영향 단계: S02
- 상태: accepted
- 결정: 기존 `work-packages/WP-KEYSTONE-SKILL` 문서는 자동으로 `works/`로 migration하지
  않는다. Migration 전에 사용자에게 묻는다.
- 이유: 승인되지 않은 path churn을 피하면서 향후 구조 정책을 기록한다.

### DEC-018

- 수락 단계: S01
- 영향 단계: S02
- 상태: accepted
- 결정: `keystone-clarify`는 high-impact topic 결정(6)을 위한 별도 스킬이다.
  Plan Mode에서 topic question을 수집하고, 사용 가능한 경우 `request_user_input` 또는
  동등한 selection UI를 사용하며, 수락된 reflection과 edit plan을 요약한 뒤 Default
  Mode에서 관련 원천 문서(2) update를 지원한다.
- 이유: 모든 사소한 수정을 질문으로 만들지 않으면서 결정이 여러 문서에 영향을 미칠 때
  일관성을 보존한다.

### DEC-019

- 수락 단계: S01
- 영향 단계: S02
- 상태: accepted
- 결정: Keystone initial shared project setting은 Keystone을 사용하는 target project에서
  Plan Mode setup 이후 기본적으로 `.keystone/config.yaml`에 기록한다. 개인용, 로컬 전용,
  민감한 override는 `.keystone/config.local.yaml`에 둔다. 기존 project-local agent
  instruction file은 사용자가 그 저장 위치를 선택한 경우에만 사용할 수 있다. Keystone은
  common/global instruction file에 쓰지 않는다. 이 Keystone implementation repository는
  이후 fixture 또는 test step이 명시적으로 요구하지 않는 한 S01 또는 S02 동안 config
  file이 필요하지 않다.
- 이유: 반복 setup question을 피하면서 project-level choice를 명시적이고 portable하게
  유지하고, 이 implementation repository를 configured target project로 오해하지 않게 한다.

### DEC-020

- 수락 단계: S01
- 영향 단계: S02
- 상태: accepted
- 결정: 기준서와 작업서 Git policy는 네 가지 선택지를 지원한다: 둘 다 track, 기준서만
  track, 둘 다 track하지 않음, 매번 묻기. 파생 에이전트 문서(8)는
  기본적으로 ignore한다.
- 이유: Project가 collaboration/privacy tradeoff를 선택할 수 있게 하고, 원천 문서(2)를
  완전히 local로 둘 수도 있게 한다.

### DEC-021

- 수락 단계: S01
- 영향 단계: S02
- 상태: accepted
- 결정: Keystone output language policy는 Keystone artifact에만 적용하며, 관련 없는
  task language, code comment, commit message, README file, external tool,
  non-Keystone skill을 override해서는 안 된다.
- 이유: Keystone 문서 일관성을 유지하면서 언어 정책이 관련 없는 작업으로 새지 않게 한다.

### DEC-022

- 수락 단계: S01
- 영향 단계: S02
- 상태: accepted
- 결정: 모든 작업서 step은 `Goal`, `Scope`, `Source Context`, `Completion Criteria`,
  `Stop Conditions`, `Verification`, `Expected Output`을 포함해야 한다. 단순한 step은
  내용이 짧아도 된다. `Suggested Role`은 선택 사항이며 delegation 가능성이 클 때 권장한다.
- 이유: 작은 작업에 긴 template를 강제하지 않으면서 step의 recoverability와 coordinator
  compatibility를 유지한다.

### DEC-023

- 수락 단계: S01
- 영향 단계: S02
- 상태: accepted
- 결정: Keystone을 사용하는 target project에서 `.keystone/config.yaml`은 shared project
  policy로서 기본적으로 Git에 track하고, `.keystone/config.local.yaml`은 local/private
  override로서 기본적으로 Git에서 ignore한다. Sensitive setting이나 document는 쓰기,
  track, publish, 파생 에이전트 문서(8) 생성 전에 사용자 확인이 필요하다.
- 이유: 안정적인 project policy는 공유하고 private/sensitive data는 기본적으로 Git과
  파생 에이전트 문서(8) 밖에 둔다.

### DEC-024

- 수락 단계: S01
- 영향 단계: S02
- 상태: accepted
- 결정: `keystone-reader` Orientation Mode는 document-led, repository-aware, read-only다.
  출력에는 document root, project summary, shallow repository snapshot, active document
  map, current work status, recommended read order, operational boundaries,
  risks/gaps, next action, sources read, assumptions가 포함된다. Document-to-repository
  mismatch는 자동 수정하지 않고 사용자/main 결정(6) 대상으로 보고한다.
- 이유: Stale document와 repo-state drift를 일찍 발견하되 read-only orientation step이
  원천 문서(2)나 code를 조용히 바꾸지 않게 한다.

### DEC-025

- 수락 단계: S01
- 영향 단계: S02
- 상태: accepted
- 결정: 이 Keystone 스킬 구현 저장소의 원천 문서(2) 기본 언어는 한국어다.
  파일 경로, 설정 key, schema value, status value, skill name, step ID, decision ID,
  standard ID처럼 기계적으로 참조되는 literal은 영어 또는 기존 값을 유지한다. Target
  project의 Keystone output language policy는 별도 project setting으로 선택할 수 있다.
- 이유: S01/S02 문서 검토를 한국어로 진행하면서도 경로와 식별자의 안정성을 유지한다.

### DEC-026

- 수락 단계: S01
- 영향 단계: S01, S02
- 상태: accepted
- 결정: Keystone 기준서(3)는 전체 공통 기준서에서 시작해 필요한 경우 스킬별 child
  기준서로 내려가는 계층으로 정리한다. 전체 공통 기준서는 프로젝트 목표, 공통 용어,
  문서 흐름, 스킬 목록, 공통 정책을 요약하고, 스킬별 기준서는 `keystone-clarify`,
  `keystone-author`, `keystone-reader`, `keystone-coordinator`의 상세 계약을 담는다.
  실제 파일 분리는 스킬별 contract가 충분히 안정된 뒤 진행한다.
- 이유: main이 전체 흐름을 먼저 파악한 뒤 현재 작업에 필요한 최종 상세 기준서로 이동하게
  하고, 네 개 스킬의 독립 계약을 문서 구조에서도 분리하기 위해서다.

수락된 결정(6)은 명시적으로 다르게 표시하지 않는 한 S01 foundation policy로 수락된
것이다. `영향 단계`는 해당 결정이 나중 단계의 contract 또는 implementation에
영향을 준다는 뜻이며, 그 단계가 시작되었거나 수락되었다는 뜻은 아니다.

## 결정 메모

- `keystone-clarify`는 원천 문서(2)가 변경되기 전에 high-impact policy,
  scope, document, skill-contract 결정(6) collection을 담당한다.
- `keystone-clarify`는 project setting에 충분한 정보가 없을 때 initial Keystone
  setup question도 담당한다.
- Initial Keystone setup config는 Keystone을 사용하는 target project에 속한다. 이
  implementation repository는 S01 또는 S02 동안 `.keystone/config.yaml`을 요구하지
  않는다.
- `keystone-author`는 기준서와 작업서의 creation/revision을 담당한다.
- `keystone-reader`는 project orientation, document navigation, work preparation을
  담당한다.
- `keystone-coordinator`는 Goal assignment, subagent routing, report, review,
  verification, acceptance flow를 담당한다.
- 기준서는 사람과 LLM을 위한 사람이 읽을 수 있는 문서가 기본이다. 작업서는 사람이
  읽을 수 있지만 주로 LLM work preparation과 subagent execution을 위해 구조화된다.
- 이 저장소의 Keystone 원천 문서(2)는 한국어를 기본으로 작성한다. 경로와 기계적
  식별자는 영어 또는 기존 literal 값을 유지한다.
- 기존 prototype 스킬은 reference일 뿐이다. `work-package-doc-architect`와
  `subagent-work-coordinator`는 최종 runtime dependency가 아니다.
