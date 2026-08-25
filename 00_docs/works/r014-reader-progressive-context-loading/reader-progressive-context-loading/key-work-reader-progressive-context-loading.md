---
doc_type: work_order
created_at: "2026-08-24"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-25", accepted_by: main}
work_status: complete
key:
  id: key.work.reader-progressive-context-loading.order
  refs:
    - key.doc.work
    - key.topic.context-readiness
    - key.topic.work-recovery
    - key.topic.work-sequence
    - key.topic.skill-contract
    - key.topic.artifact-graph
    - key.topic.verification
    - key.standard.project
    - key.standard.skill.reader
---

# Reader Progressive Context Loading 작업서 및 Change Set

<!-- key: id=key.work.reader-progressive-context-loading.order.goal refs=key.section.goal key.topic.context-readiness -->
## Goal

최초 Codex 세션의 Reader가 Context Map과 최상위 프로젝트 기준서를 중심으로 프로젝트 목적,
범위, 문서 구조와 권위 관계를 충분히 파악한 뒤 canonical Work State를 결합하도록 한다. 프로젝트
이해에 부족한 부분만 Reader 판단으로 관련 하위 기준서까지 bounded하게 확장해 project brief를
준비하고, Work State 결과로 현재 작업 상태를 결합해 session brief를 완성한다.

구체적인 작업을 선택하거나 계획할 때는 선택된 Work와 상세 기준을 먼저 읽고, Linker를 사용해
문서와 연결된 code/config/schema/API/test 및 필요한 실행 흐름까지 확인한다. 초기 경량화는
agent-facing structured payload를 축약하지 않고 상세 문서와 Linker의 읽기 시점을 늦추는 방식으로
달성한다.

<!-- key: id=key.work.reader-progressive-context-loading.order.problem refs=key.topic.context-readiness key.topic.work-recovery -->
## 문제와 근거

1. 현재 Reader 계약은 초기 Work State 투영 뒤 선택된 docs discovery scope에 대해 Linker
   readiness를 기본 요청한다.
2. 활성 Round가 없고 단순 orientation만 필요한 경우에도 전체 문서 owner/ref index를 만들 수
   있어 초기 목적보다 큰 context payload가 발생한다.
3. 2026-08-24 현재 corpus에서 Work State는 178개 source를 처리했고, Linker docs readiness는
   207개 문서를 다시 처리하면서 133개 비차단 진단과 매우 큰 raw owner/ref payload를 만들었다.
4. 초기 orientation은 모든 상세 문서를 읽는 단계가 아니지만 프로젝트 의미의 권위인 최상위
   프로젝트 기준서는 정독해야 한다. Context Map 요약만으로 프로젝트 의미를 대체할 수 없다.
5. 프로젝트 이해에 하위 기준이 필요한 경우와 구체적인 작업의 기능·화면·구현 상세가 필요한
   경우를 분리하지 않으면 Reader 자율성이 전수 탐색으로 확대되거나 필요한 기준을 놓칠 수 있다.
6. 작업 선택·계획 단계에서는 문서가 의도와 정책을, 코드는 현재 실제 동작을 제공한다. 두 source를
   연결해서 읽어야 Keystone의 문서 중심 작업 계획 목적을 달성할 수 있다.
7. 기준은 정의됐지만 구현이 아직 없는 상태는 정상적인 docs-first 진행 상태일 수 있으므로,
   연결된 코드의 부재를 자동으로 metadata gap이나 오류로 해석하면 안 된다.

<!-- key: id=key.work.reader-progressive-context-loading.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- document root와 최소 initialization evidence를 확인한 뒤 Context Map으로 전체 문서 구조와
  주요 진입점을 파악하는 session orientation 계약
- 프로젝트 목적, 범위, 문서 구조와 권위 관계를 정의하는 accepted 최상위 프로젝트 기준서를
  초기 orientation에서 정독하는 규칙
- 최상위 기준서의 명시적 연결이나 아직 설명되지 않은 프로젝트 핵심 항목을 근거로 하위 기준서를
  확장하고, Reader가 구체적인 미확인 사항을 설명할 수 있을 때 bounded discretion을 허용하는 경계
- 프로젝트 목적, 범위, 주요 문서 구조, 권위 관계와 중요한 미확인 사항을 담는 concise project
  brief를 준비하는 completion condition
- project brief를 만든 뒤 canonical Work State로 현재 Work 상태를 결합해 session brief를
  완성하고, 활성 Round가 없으면 현재 상태와 다음 actor를 보고하며 상세 기능 문서·Linker 호출
  없이 종료하는 흐름
- 활성 Round가 하나면 해당 Round index와 active Work/Progress만, 복수이면 기존 session focus
  질문 뒤 선택된 Round만 먼저 읽는 규칙
- 작업 선택·계획 단계에서는 선택된 Work Order·Progress와 관련 기준서·기능 문서를 먼저 충분히
  읽고, 그 문서의 stable ID/ref/relation을 anchor로 구현 artifact를 탐색하는 docs-first 규칙
- Linker가 선택된 Work와 관련 문서를 anchor로 code/test/config/schema/API를 찾고 실제 동작과
  변경 영향을 이해하는 데 필요한 호출자·피호출자·데이터 흐름만 bounded하게 확장하는 경계
- 연결된 구현이 없을 때 문서 상태와 bounded repository search를 확인하고, 증거가 없으면 구현
  확인 불가 또는 미구현 가능으로 보고하며 코드 후보와 relation 불일치가 있을 때만 metadata gap
  후보로 분리하는 규칙
- 전체 repository graph는 명시적 audit, release 검증 또는 범위 충돌에만 사용하는 경계
- agent-facing structured payload와 인간 친화적 사용자 응답의 현재 계약을 유지하고 payload shape나
  내부 evidence를 경량화 범위에 포함하지 않는 규칙
- active Round 0개·1개·복수, explicit Round, work-scoped Linker, no-implementation evidence와
  cache unavailable 시나리오의 focused contract regression

Exclude:

- Canonical Work State derivation, schema, Round hierarchy 또는 dependency 의미 변경
- Reader의 read-only 경계, accepted/pending authority와 source conflict stop condition 완화
- Context Map이나 별도 요약 문서를 새로운 policy authority로 승격
- 상세 기준서, Linker, Artifact Graph 또는 repository scope 제거
- Work Order가 참조한 적용 기준을 구현 전에 생략하는 최적화
- agent-facing Work State/Linker payload shape, full structured handoff 또는 사용자 presentation
  contract 변경
- 연결된 구현이 없다는 사실만으로 metadata gap, stale 상태 또는 작업 오류를 확정
- Linker cache, scanner, owner/ref graph runtime 자체의 성능 리팩터링
- Coordinator, Author, Clarify 또는 Init의 실행 계약 변경
- full repository/package/installer release 검증을 기본 completion gate로 추가

<!-- key: id=key.work.reader-progressive-context-loading.order.direction refs=key.topic.context-readiness key.topic.artifact-graph -->
## 사용자 방향

상세 질문과 답변은
`clarify/20260825T015248Z-reader-progressive-context-review.md`에 비권위 memory log로 기록한다.

1. 최초 세션은 document root·최소 initialization 확인, Context Map, 최상위 프로젝트 기준서,
   필요한 하위 기준서, project brief, canonical Work State 순으로 파악한다.
2. 최상위 프로젝트 기준서는 정독한다. 하위 기준서는 프로젝트 이해의 구체적인 미확인 사항이
   있을 때 근거 기반으로 읽되 Reader의 bounded discretion을 허용한다.
3. 기능·화면·개별 구현의 상세 문서는 초기 orientation이 아니라 작업 선택·계획 단계에서 읽는다.
4. 초기 orientation은 목적·범위·문서 구조·권위·미확인 사항을 먼저 설명하고 Work State에서
   현재 Work 상태를 결합한 session brief를 만들 수 있으면 충분하다.
5. 작업 계획 단계에서는 조금 느려도 문서를 먼저 충분히 읽고 연결된 구현 artifact와 실제 코드
   흐름까지 확인한다.
6. Linker는 세션 시작의 필수 단계가 아니라 선택된 Work와 문서의 artifact 문맥이 필요할 때
   호출한다.
7. Linker는 Work/document anchor에서 시작해 필요한 relation과 repository source만 bounded하게
   확장하고 full graph는 audit, release 또는 범위 충돌 때만 사용한다.
8. 연결된 구현이 없으면 bounded search 뒤 미구현 가능 또는 구현 확인 불가로 보고한다. 실제 코드
   후보가 있는데 relation만 없을 때 metadata gap 후보로 분리한다.
9. agent-facing structured payload와 사용자 친화적 요약의 기존 경계는 변경하지 않는다.
10. 경량화는 payload 축약이 아니라 초기 읽기 범위와 Linker 호출 시점으로 달성한다.

<!-- key: id=key.work.reader-progressive-context-loading.order.execution-plan refs=key.topic.work-sequence key.topic.verification -->
## 실행 계획

| Step | 상태 | 변경 범위 | 완료 경계 |
|---|---|---|---|
| R014/S01 | complete + accepted | Project Reader 관련 공통 규칙, Reader 기준서와 index | Context Map→최상위 기준서→bounded child→project brief→Work State orientation과 docs-first 작업 계획 경계를 명확히 한다 |
| R014/S02 | complete + accepted | `skills/keystone-reader/SKILL.md`, `skills/keystone-reader/tests/test_reader_linker_readiness.py`와 필요한 focused test | 설치 가능한 Reader contract가 초기 Linker 호출을 제거하고 선택된 Work에서 문서→artifact를 bounded하게 확장하며 기존 payload/authority 경계를 유지한다 |
| R014/S03 | complete + accepted | focused scenario fixture, contract parity, Work State와 관련 문서 상태 | 0·1·복수 active Round, bounded child read, work-scoped Linker와 미구현 가능 경로가 검증되고 residual risk와 acceptance 후보가 기록된다 |

위 순서는 기본 실행 순서다. 이 작업서의 수락 또는 문서 작성만으로 후속 Step의 상태를 자동
전이하지 않는다.

<!-- key: id=key.work.reader-progressive-context-loading.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

| Surface | Owner | Required change | Verification |
|---|---|---|---|
| Project Standard | Author | Reader의 단계별 읽기 깊이와 초기 최소 authority boundary를 공통 규칙에 정렬 | 관련 rule과 기존 Work State/authority 문안 대조 |
| Reader Standard and Index | Author | 초기 orientation, work-scoped expansion, implementation gate와 조건부 Linker trigger 정의 | scope, trigger, stop condition과 parent standard 정합성 |
| Reader Skill Source | Main | self-contained runtime contract에 같은 progressive loading 순서 반영 | standard/skill phrase and behavior parity |
| Reader Focused Tests | Main | 첫 호출의 무조건 Linker handoff를 조건부 계약으로 바꾸고 단계별 시나리오 추가 | focused unit/contract tests |
| R014 Work Sources | Author | 실제 상태, 검증 결과와 resume point 기록 | Work State와 exact-ref 확인 |

<!-- key: id=key.work.reader-progressive-context-loading.order.completion refs=key.topic.verification key.topic.context-readiness -->
## Completion Criteria

<!-- key: id=key.acceptance.reader-progressive-context.bootstrap-scope -->
- `R014-CC-01` 초기 orientation이 document root·initialization, Context Map, 최상위 프로젝트
  기준서, 필요한 하위 기준서, project brief, canonical Work State 순으로 수행된다.
<!-- key: id=key.acceptance.reader-progressive-context.empty-active-set -->
- `R014-CC-02` 최상위 프로젝트 기준서를 정독하고 목적·범위·문서 구조·권위와 미확인 사항을
  project brief로 설명할 수 있다. 하위 기준은 구체적인 이해 gap이 있을 때만 근거와 Reader의
  bounded discretion으로 확장한다.
<!-- key: id=key.acceptance.reader-progressive-context.selected-work-scope -->
- `R014-CC-03` Work State로 현재 Work 상태를 project brief에 결합한다. Active parent Round가
  없으면 빈 active set과 다음 actor를 보고하고, 한 개 또는 session-selected Round에서는 해당
  Round index와 active Work/Progress만 먼저 읽으며 unselected Round의 상세 source를 열지 않는다.
<!-- key: id=key.acceptance.reader-progressive-context.standard-expansion -->
- `R014-CC-04` 작업 선택·계획 단계에서는 Work Order·Progress와 관련 기준서·기능 문서를 먼저
  충분히 읽고, 문서 ref와 relation을 따라 구현 artifact와 필요한 실제 코드 흐름을 확인한다.
<!-- key: id=key.acceptance.reader-progressive-context.linker-trigger -->
- `R014-CC-05` Linker는 초기 orientation에서 실행하지 않고 선택된 Work의 artifact context,
  stable ID owner/ref, graph-relevant 영향 또는 명시적 audit가 필요할 때 Work/document anchor로
  실행된다.
<!-- key: id=key.acceptance.reader-progressive-context.lazy-repository -->
- `R014-CC-06` 연결된 code/test/config/schema/API를 우선 읽고 필요한 호출·데이터 흐름만 bounded
  확장한다. 연결 구현이 없으면 bounded search 뒤 미구현 가능/확인 불가로 보고하고 코드 후보가
  있을 때만 metadata gap 후보로 분리한다.
<!-- key: id=key.acceptance.reader-progressive-context.authority-preservation -->
- `R014-CC-07` read-only, accepted/pending authority, source conflict stop condition, multi-active
  Round focus와 lowest-executable Step 선택 의미가 유지된다.
<!-- key: id=key.acceptance.reader-progressive-context.payload-boundary -->
- `R014-CC-08` agent-facing Work State/Linker structured payload와 사용자 친화적 요약의 기존 경계를
  유지하며, 새로운 tool-level compact payload filtering을 도입하지 않는다.
<!-- key: id=key.acceptance.reader-progressive-context.scenarios -->
- `R014-CC-09` active Round 0개·1개·복수, bounded child standard read, work-scoped Linker,
  missing implementation evidence, explicit full graph와 cache unavailable 시나리오가 focused
  regression으로 검증된다.
<!-- key: id=key.acceptance.reader-progressive-context.contract-parity -->
- `R014-CC-10` Project/Reader 기준과 Reader skill source가 같은 단계별 loading·trigger·stop
  boundary를 가지며 관련 문서 navigation이 현재 상태와 일치한다.

<!-- key: id=key.work.reader-progressive-context-loading.order.verification refs=key.topic.verification -->
## Verification

1. Project/Reader 기준서와 Reader skill의 Context Map→최상위 기준서→bounded child→project brief→
   Work State 순서, 작업 계획의 문서→artifact 흐름과 stop condition을 대조한다.
2. `skills/keystone-reader/tests/test_reader_linker_readiness.py`에서 첫 Reader 호출의 무조건 handoff
   기대를 제거하고 explicit trigger와 recursion guard를 분리 검증한다.
3. 필요한 focused test에 active Round 0개·1개·복수, bounded child read, explicit selection과
   no-Linker startup scenario를 추가하고 실행한다.
4. Work-scoped Linker가 문서 anchor에서 연결 artifact와 필요한 코드 흐름만 확장하고, 코드 증거가
   없는 기준과 relation 누락 후보를 구분하는지 확인한다.
5. Agent-facing structured payload가 기존 계약대로 보존되고 사용자 응답만 인간 친화적으로
   요약되는지 대조한다.
6. Work/Step 상태 변경 뒤 `python3 scripts/work_state_runtime.py --root .`을 실행한다.
7. 새 ID/ref, 관련 link, Markdown metadata와 `git diff --check`를 확인한다.
8. Linker source, graph runtime 또는 repository artifact가 실제로 바뀌지 않으면 full graph,
   package, repository와 installer 검증은 실행하지 않는다.

<!-- key: id=key.work.reader-progressive-context-loading.order.stop refs=key.boundary.stop-condition key.topic.context-readiness -->
## Stop Conditions

1. 경량 orientation을 구현하려면 canonical Work State authority나 schema를 바꿔야 한다.
2. Context Map과 최상위 기준서에서 프로젝트 목적·범위·구조·권위를 복구할 수 없고, 관련 하위
   기준서의 bounded expansion으로도 project brief를 만들 수 없다.
3. 초기 파악 축소가 accepted/pending 구분, source conflict 또는 read-only 경계를 약화한다.
4. 선택된 Work/document anchor에서 bounded graph와 repository 탐색으로 구현 문맥을 정할 수 없고
   full repository graph 없이는 일반 작업 계획을 시작할 수 없다.
5. 기존 Reader session focus 또는 Step 선택 의미를 변경하는 새로운 사용자 결정이 필요하다.
6. Agent-facing structured payload shape를 변경하지 않으면 초기 orientation을 경량화할 수 없다.
7. Reader 이외의 Keystone skill 계약을 함께 변경하지 않으면 일관성을 유지할 수 없다.
8. Focused verification으로 behavior boundary를 검증할 수 없어 별도 runtime 계측이나 repository-wide
   agent evaluation이 필요해진다.

<!-- key: id=key.work.reader-progressive-context-loading.order.expected-output refs=key.topic.context-readiness key.topic.work-recovery -->
## Expected Output

- Context Map, 최상위 프로젝트 기준서, bounded child expansion과 project brief를 사용하는 Reader
  orientation 계약
- 선택된 Work의 문서를 먼저 이해하고 연결된 artifact와 필요한 코드 흐름으로 확장하는 docs-first
  planning 규칙
- 초기에는 실행하지 않고 Work/document anchor가 있을 때 bounded하게 실행되는 Linker trigger
- 구현 증거 부재와 relation metadata gap 후보를 구분하는 보고 경계
- agent-facing structured payload와 사용자 친화적 요약을 분리하는 기존 output contract 보존
- 기존 Work State authority, session focus, read-only와 accepted/pending 경계를 보존하는 Reader skill
- 핵심 시나리오와 contract parity를 고정하는 focused regression 결과
- 실행 상태, 검증, residual risk와 다음 resume point가 기록된 Progress
