---
doc_type: decisions
key:
  id: key.work.decisions
  refs:
    - key.doc.decision
    - key.doc.work
    - key.topic.document-system
    - key.topic.key-prefix
    - key.topic.work-round
---

# 작업서 결정 기록(6)

이 문서는 `00_docs/works/` tree에 적용되는 공통 결정(6)을 기록한다.

<!-- key: id=key.work.decisions.dec-works-001 refs=key.doc.decision key.doc.work key.topic.document-system -->
## DEC-WORKS-001: Active work tree는 `works/`를 사용한다

- 관련 work: Document Tree Setup
- 상태: accepted
- 결정: 새 Keystone 작업 문서는 `00_docs/works/` 아래에 둔다. 기존 `00_docs/work-packages/`
  문서는 active 작업 문서로 유지하지 않는다.
- 이유: 현재 기준서의 `standards/`와 `works/` tree 정책에 맞추고 legacy 경로와 현재 진행
  상태의 충돌을 제거하기 위해서다.

<!-- key: id=key.work.decisions.dec-works-002 refs=key.doc.decision key.doc.work key.topic.document-system -->
## DEC-WORKS-002: 작업서는 기준서 구조에 종속되지 않는다

- 관련 work: Author Standard
- 상태: accepted
- 결정: 작업서는 기준서별, 기능별, 구현 단계별, 검증 단계별로 만들 수 있다. 관련 기준서를
  참조하되 실행 순서는 기준서 tree가 아니라 work round index 또는 별도 상위 work plan이
  관리한다.
- 이유: 기준서는 장기 규칙이고 작업서는 현재 실행 순서와 범위를 담기 때문에 두 구조가 항상
  같을 필요가 없다.

<!-- key: id=key.work.decisions.dec-works-003 refs=key.doc.decision key.topic.work-sequence key.doc.work key.topic.work-round -->
## DEC-WORKS-003: R001 작업 순서는 S00-S07로 둔다

- 관련 work: Document Tree Setup
- 상태: accepted
- 결정: R001 Bootstrap Keystone round의 작업 순서는 S00 문서 트리 재정비, S01 전체 기준서,
  S02 reader, S03 author, S04 clarify, S05 coordinator, S06 Skill 생성, S07 통합 검증 순서로
  둔다.
- 후속 결정: `DEC-WORKS-006`이 R001 순서를 S00-S09로 확장한다.
- 이유: 문서 구조를 먼저 안정화하고, 공통 기준서와 스킬별 기준서를 분리한 뒤 구현과 통합
  검증으로 넘어가기 위해서다.

<!-- key: id=key.work.decisions.dec-works-004 refs=key.doc.decision key.topic.key-prefix key.topic.document-system -->
## DEC-WORKS-004: Keystone-managed 문서는 key prefix를 사용한다

- 관련 work: Project Standard
- 상태: accepted
- 결정: Keystone-managed Markdown 문서는 파일명에 lower-case `key` prefix를 사용한다. 문서
  순서를 정해야 하는 경우 `{number}_key-{slug}.md`를 사용하고, 그 외에는
  `key-{slug}.md`를 사용한다. 같은 위치에서 첫 순서 문서는 `00_`, 다음 순서 문서는 `01_`,
  그 다음은 `02_`를 사용한다. 파일명 단어 구분은 `-`로 통일한다.
- 이유: Keystone 결과물인지 파일명만으로 식별해 Reader, Author, Clarify, Coordinator
  routing 기준으로 사용할 수 있게 하기 위해서다.

<!-- key: id=key.work.decisions.dec-works-005 refs=key.doc.decision key.topic.work-round key.topic.document-system key.doc.work -->
## DEC-WORKS-005: 작업서는 round 단위로 묶는다

- 관련 work: Project Standard
- 상태: accepted
- 결정: `works/00_key-index.md`는 전체 work round 목록을 관리한다. 각 round는
  `r{number}-{slug}` folder를 가지며, `r`은 round를 뜻한다. 각 round 안에서는 작업 순서를
  `S00`부터 다시 시작한다.
- 이유: 기준서는 프로젝트의 지속 기준이지만 작업서는 특정 시점의 기준서와 목표를 바탕으로 한
  실행 차수이기 때문이다.

<!-- key: id=key.work.decisions.dec-works-006 refs=key.doc.decision key.topic.artifact-graph key.topic.skill-contract key.topic.work-sequence -->
## DEC-WORKS-006: Artifact Graph와 Linker를 Keystone 중심 계층으로 승격한다

- 관련 work: Project Standard, Artifact Graph Standard, Linker Standard, Skill Creation,
  Integration Verification
- 상태: accepted
- 결정: Keystone은 단순 문서 CRUD skill 묶음이 아니라, 사람의 의도, 원천 문서(2),
  capability(16), code artifact, API, test artifact, bounded worker 실행 결과를 문서 기반으로 연결하는
  project control plane으로 정의한다.
- 결정: 문서-capability-code-test 연결, impact candidate, stale metadata 후보 탐색은
  `keystone-linker`가 소유한다.
- 결정: 기본 Coordinator 모델은 별도 실행 위임 계층을 정의하지 않는다. 실행이 필요한 작업은
  bounded worker assignment와 worker report로 조율하며, 별도 실행 보조 계층은 실제 필요와
  수락된 기준서가 생긴 뒤 다룬다.
- 결정: 기존 Change Set(17) 개념을 먼저 강화하고, 별도 `key-change-{slug}.md` 문서 타입은
  실제 사용 필요가 확인된 뒤 도입한다.
- 결정: `DEC-WORKS-003`의 R001 순서를 확장해 S06 Artifact Graph Standard, S07 Linker
  Standard를 Skill Creation 전에 추가하고, 기존 Skill Creation과 Integration Verification은 각각
  S08, S09로 이동한다.
- 이유: Reader와 Coordinator에 artifact graph 책임을 나누어 넣으면 책임 경계가 흐려지고,
  기존 계획대로 skill source를 먼저 만든 뒤 재작업할 가능성이 크기 때문이다.

<!-- key: id=key.work.decisions.dec-works-007 refs=key.doc.decision key.topic.work-execution key.standard.subagent key.role.coordinator -->
## DEC-WORKS-007: 기본 Coordinator 실행 모델을 single workspace bounded worker로 복구한다

- 관련 work: Project Standard, Subagent Standard, Coordinator Standard, Author Standard,
  Context Map, README
- 상태: accepted
- 결정: 기본 실행 모델은 single workspace bounded worker orchestration으로 둔다.
- 결정: `STD-KEYSTONE-034`는 삭제한다. 기본 기준서는 별도 작업 격리 계층이나 통합 절차를
  다루지 않는다.
- 결정: role 이름은 worker 종류가 아니라 assignment purpose hint로 낮춘다. 실제 경계는
  purpose preset, authority, injected skill contract, scope, workspace guard, stop condition,
  report contract가 정한다.
- 결정: Worker는 주입된 skill contract 안에서 local planning을 할 수 있지만, 전체 작업서(4)를
  재해석하거나, scope를 넓히거나, 추가 subagent를 만들거나, Main acceptance와 progress
  accepted를 대체하지 않는다.
- 결정: Single workspace에서는 한 번에 하나의 file-writing worker만 허용한다. 기존 사용자
  변경이나 다른 agent 변경을 덮어쓸 위험이 있으면 worker는 멈추고 보고한다.
- 이유: 이전 격리 중심 모델은 기본 Coordinator 기준서에 비해 과하고, 지금 단계에서는 main의
  context 보존, bounded assignment, 명확한 report 회수가 더 중요한 기본 동작이기 때문이다.

<!-- key: id=key.work.decisions.dec-works-008 refs=key.doc.decision key.topic.skill-contract key.topic.external-assist key.role.coordinator key.standard.subagent -->
## DEC-WORKS-008: 외부 코딩 스킬은 Coordinator injected skill로 사용한다

- 관련 work: Project Standard, Subagent Standard, Coordinator Standard, Skill Creation,
  Integration Verification
- 상태: accepted
- 결정: Keystone 작업 문맥이 있고 code/config/schema/API/test 수정 요청이 들어오면 기본 routing은
  `keystone-coordinator`로 한다.
- 결정: 사용자가 `superpowers` 같은 외부 코딩 스킬(12)을 명시하면 해당 스킬은 Coordinator를
  대체하지 않고 worker assignment(19)의 `injected_skills`로 주입한다.
- 결정: 외부 코딩 스킬이 명시되지 않으면 Coordinator는 `keystone-default-bounded-worker`
  contract를 사용한다.
- 결정: 여러 외부 코딩 스킬 후보가 있고 선택에 따라 workflow, verification, risk가 달라질 때만
  사용자에게 선택지를 제시한다. 매번 선택지를 표시하지 않는다.
- 결정: 외부 코딩 스킬 주입은 authority를 올리지 않는다. Scope, forbidden changes,
  workspace guard, verification, report contract는 Coordinator assignment가 정한다.
- 이유: Keystone은 문서와 bounded assignment를 control plane으로 유지해야 하고, 코딩 방법론은
  교체 가능한 execution guidance로 주입되어야 하기 때문이다.

<!-- key: id=key.work.decisions.dec-works-009 refs=key.doc.decision key.topic.artifact-graph key.role.linker key.role.author key.role.coordinator -->
## DEC-WORKS-009: Linker는 Artifact Graph 해석 권위를 가진다

- 관련 work: Artifact Graph Standard, Linker Standard, Author Standard, Coordinator Standard,
  Skill Creation, Integration Verification
- 상태: accepted
- 결정: Artifact Graph의 model language는 Artifact Graph 기준서가 정의한다.
- 결정: Linker는 Artifact Graph의 operational interpretation owner다. Linker는 source
  document, 키메타(9), 코드 앵커(18), repository evidence를 read-only로 해석해 graph state,
  relation evidence, impact candidate, stale candidate, metadata gap, reuse candidate, test
  candidate를 판단하고 보고한다.
- 결정: Linker의 graph ownership은 source edit authority를 포함하지 않는다.
- 결정: Markdown frontmatter `key.id`, `key.refs`, section-level key comment 같은 source
  document metadata 변경은 Author가 반영한다.
- 결정: code/config/schema/API/test file 안의 anchor 변경과 implementation 변경은 Coordinator가
  bounded worker assignment로 조율한다.
- 결정: Linker report는 evidence와 handoff input이며 자동 수정, 자동 acceptance, Main
  acceptance를 대체하지 않는다.
- 이유: graph 판단 권위와 source edit 권한을 분리해야 candidate 발견이 자동 수정 근거로
  해석되지 않고, Author와 Coordinator의 기존 authority boundary를 유지할 수 있기 때문이다.

<!-- key: id=key.work.decisions.dec-works-010 refs=key.doc.decision key.topic.artifact-graph key.topic.api key.role.linker key.role.coordinator -->
## DEC-WORKS-010: API artifact는 기본적으로 contract artifact로 해석한다

- 관련 work: Artifact Graph Standard, Linker Standard, Integration Verification
- 상태: accepted
- 결정: `key.api.*`는 first-class artifact지만 기본 capability provider가 아니라 API, route,
  RPC, command/query, message contract, plugin interface 같은 contract artifact로 해석한다.
- 결정: Capability는 기본적으로 code/config/schema artifact가 `provides`한다.
- 결정: Code/config/schema artifact는 API 또는 결정된 contract를 `implements`한다.
- 결정: API 변경은 implementing artifact, verifying test, source document, related capability의
  impact/stale 후보를 만들 수 있다.
- 결정: accepted decision 또는 명시된 예외 relation policy가 없으면
  `key.api.* -> provides -> key.capability.*`를 기본 typed relation으로 확정하지 않는다.
- 이유: API를 기본 provider로 승격하면 contract, implementation, capability boundary가 흐려져
  over-linking과 잘못된 impact 후보가 늘 수 있기 때문이다.

<!-- key: id=key.work.decisions.dec-works-011 refs=key.doc.decision key.topic.skill-contract key.contract.output key.topic.external-assist -->
## DEC-WORKS-011: Keystone 출력은 사용자 응답과 structured payload를 분리한다

- 관련 work: Project Standard, Skill Creation, Integration Verification
- 상태: accepted
- 결정: Keystone skill은 기본 사용자 응답으로 결론, 핵심 근거, 주요 risk, 다음 행동, 주요
  출처를 짧게 보여준다.
- 결정: `reader_output`, `clarify_result`, `author_patch_report`, `linker_report`,
  `worker_assignment`, `worker_report`, `worker_report_review` 같은 structured payload는
  agent-facing handoff, audit, debugging, verification evidence contract로 유지한다.
- 결정: Full structured payload는 사용자가 요청했거나 다른 Keystone skill 또는 Main이 handoff
  input으로 필요로 할 때만 전체 노출한다.
- 결정: Optional `keystone-viewer`는 presentation/helper skill 후보로 둘 수 있지만, 다섯 core
  Keystone skill의 mandatory runtime dependency나 모든 output의 필수 filter chain으로 만들지
  않는다.
- 결정: Viewer 또는 동등한 presentation layer는 의미 판단, acceptance 판단, risk 제거,
  recommended next action 변경, source authority 변경, handoff payload 수정을 하지 않는다.
- 이유: 내부 handoff payload를 사용자에게 그대로 노출하면 응답이 과하고, 사용자-facing view를
  각 skill에 중복 구현하면 drift와 context 증가가 생기기 때문이다. 기본 출력 정책은 core
  standard에 두고, 복잡한 렌더링은 optional presentation layer로 분리한다.

<!-- key: id=key.work.decisions.dec-works-012 refs=key.doc.decision key.topic.skill-contract key.topic.work-execution key.topic.skill-source key.contract.report -->
## DEC-WORKS-012: File-changing work에는 routing decision과 lane별 report가 필요하다

- 관련 work: Project Standard, Skill Creation, Integration Verification
- 상태: accepted
- 결정: Main은 `00_docs/**`, `skills/keystone-*/SKILL.md`, code/config/schema/API/test source를
  수정하기 전에 target surface와 execution lane을 분류하는 `keystone_routing_decision`을 먼저
  남긴다.
- 결정: `00_docs/**` 원천 문서(2) 변경은 `keystone-author` lane으로 처리하고
  `author_patch_report`를 남긴다.
- 결정: `skills/keystone-*/SKILL.md`는 `skill_source` surface다. 작은 S08 scope 안의 단일 writer
  수정은 Main direct lane으로 처리할 수 있지만 `main_direct_change_report`를 남긴다. 위임,
  formal review/verification, workspace conflict, 여러 writer가 필요하면 `keystone-coordinator`
  lane으로 처리한다.
- 결정: `source_document`와 `skill_source` 또는 repository source가 함께 바뀌는 mixed 변경은
  작업서가 combined flow를 명시하지 않는 한 lane별 phase로 분리한다.
- 결정: 특정 skill 기준서를 읽은 것만으로 그 skill lane을 실행한 것으로 보지 않는다. Lane 실행은
  routing decision, scope 준수, lane별 report로 판단한다.
- 이유: `SKILL.md` trigger만으로는 Main이 수정 전에 적절한 lane을 강제 선택하지 못해 Author,
  Coordinator, Main direct 책임 경계가 흐려질 수 있기 때문이다.

<!-- key: id=key.work.decisions.dec-works-013 refs=key.doc.decision key.topic.artifact-graph key.topic.skill-source key.output.artifact -->
## DEC-WORKS-013: Artifact Graph는 문서가 만든 output artifact를 중심으로 해석한다

- 관련 work: Artifact Graph Standard, Linker Standard, Skill Creation, Integration Verification
- 상태: accepted
- 결정: Artifact Graph의 핵심 relation은 `source_document | decision | work_order -> output_artifact`다.
- 결정: Skill source, code, config, schema, API, test, generated file은 output artifact의 surface
  또는 artifact kind이며, graph 대상 여부를 결정하는 1차 기준이 아니다.
- 결정: `skills/keystone-*/SKILL.md`가 Artifact Graph 대상인 이유는 skill source라는 파일 종류
  때문이 아니라, S08 작업서와 각 skill 기준서가 요구하고 통제하는 산출물이기 때문이다.
- 결정: Linker는 output artifact의 stale/gap을 source document, decision, work order와의 relation
  기준으로 보고하고, 수정은 `keystone_routing_decision`의 surface별 lane으로 넘긴다.
- 이유: 산출물 종류별로 graph 정책을 늘리면 skill source, code, generated file마다 예외가 생긴다.
  Keystone에는 문서와 실제 산출물의 연결이 핵심이므로, surface는 edit routing과 locator evidence로
  다루고 graph 의미는 output artifact relation으로 통일한다.
