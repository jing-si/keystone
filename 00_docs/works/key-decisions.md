---
doc_type: decisions
created_at: "2026-06-16"
key:
  id: key.work.decisions
  refs:
    - key.doc.decision
    - key.doc.work
    - key.topic.document-system
    - key.topic.key-prefix
    - key.topic.work-round
    - key.topic.bootstrap
    - key.topic.initialization
    - key.topic.runtime-independence
    - key.topic.temporal-metadata
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
- 후속 결정: `DEC-WORKS-014`가 accepted S00-S07을 보존하고 미수락 S08-S09를 R002로
  대체한다.
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
- 후속 결정: `DEC-WORKS-018`이 single workspace와 한 writer 강제를 대체한다. 이 결정은
  R001 당시의 accepted 이력으로 보존한다.

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
- 후속 결정: `DEC-WORKS-018`이 code 변경의 자동 Coordinator routing을 대체한다. 외부 스킬
  주입이 authority를 올리지 않는 경계는 유지한다.

<!-- key: id=key.work.decisions.dec-works-009 refs=key.doc.decision key.topic.artifact-graph key.role.linker key.role.author key.role.coordinator -->
## DEC-WORKS-009: Linker는 Artifact Graph 해석 권위를 가진다

- 관련 work: Artifact Graph Standard, Linker Standard, Author Standard, Coordinator Standard,
  Skill Creation, Integration Verification
- 상태: accepted
- 결정: Artifact Graph의 model language는 Artifact Graph 기준서가 정의한다.
<!-- key: id=key.claim.linker.read-only-interpretation -->
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
- 후속 결정: `DEC-WORKS-018`에 따라 code/config/schema/API/test anchor의 작은 명확한 수정은
  Main direct로도 처리할 수 있고, Coordinator를 사용할 때는 해당 work scope의 허락이 필요하다.

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
  `worker_assignment`, `worker_report`, `worker_report_review`, `keystone_routing_decision`,
  `main_direct_change_report` 같은 structured payload는 agent-facing handoff, audit,
  debugging, verification evidence contract로 유지한다.
- 결정: Full structured payload는 사용자가 요청했거나 다른 Keystone skill 또는 Main이 handoff
  input으로 필요로 할 때만 전체 노출한다.
- 결정: 기본 사용자 응답 전에는 Payload Disclosure Gate를 적용한다. Full payload 요청,
  handoff, audit, debugging, verification evidence 필요성이 없으면 `*_output`, `*_result`,
  `*_report`, `worker_assignment`, `keystone_routing_decision` 원문을 fenced YAML 또는 raw block으로
  노출하지 않는다.
- 결정: 기본 사용자 응답은 structured payload 원문 대신 변경 또는 판단 요약, 대상 파일이나 후보 수,
  검증 결과 요약, 남은 risk, 다음 행동, 주요 출처를 보여준다.
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
- 후속 결정: `DEC-WORKS-018`이 모든 file-changing work의 mandatory routing ceremony를
  대체한다. 이 결정은 R001 당시의 accepted 이력으로 보존한다.

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
- 후속 결정: `DEC-WORKS-018`에 따라 routing은 복수 surface, 권한 경계 또는 audit 필요가 있을
  때만 명시적으로 기록한다.

<!-- key: id=key.work.decisions.dec-works-014 refs=key.doc.decision key.topic.work-round key.topic.bootstrap key.topic.integration-verification -->
## DEC-WORKS-014: R001 이력을 보존하고 R002 corrective round로 전환한다

- 관련 work: R001 Bootstrap Keystone, R002 Bootstrap and Runtime Independence
- 상태: accepted
- 결정: R001의 S00-S07 accepted 이력은 그대로 보존한다.
- 결정: Review 과정에서 빈 프로젝트의 bootstrap 순환 의존이 발견되었으므로 미수락 상태인
  S08 Skill Creation과 S09 Integration Verification은 `superseded`로 전환한다.
- 결정: R002 Bootstrap and Runtime Independence를 유일한 active round로 두고 기준서 개편과
  후속 skill runtime 구현을 분리한다.
- 이유: 기존 accepted 의미를 덮어쓰지 않으면서 실제 사용 과정에서 확인한 문제를 별도 작업으로
  수정하고 이후 작업을 정확히 복구하기 위해서다.

<!-- key: id=key.work.decisions.dec-works-015 refs=key.doc.decision key.topic.bootstrap key.topic.initialization key.topic.runtime-independence key.role.init -->
## DEC-WORKS-015: Init과 설치된 skill contract로 순환 의존을 제거한다

- 관련 work: Bootstrap Runtime Standard, Skill Runtime Implementation
- 상태: accepted
- 결정: 새 `keystone-init` 계약은 프로젝트 로컬 Keystone 문서 없이 inspect, initialize,
  repair를 수행할 수 있어야 한다.
- 결정: 설치된 skill package가 고유 런타임 계약을 소유하고, 소비 프로젝트 문서는 프로젝트
  내용만 정의한다. 소비 프로젝트의 `standards/skills/**`는 runtime 선행 조건이 아니다.
- 결정: 새 소비 프로젝트는 R000 Project Foundation에서 작업 복구 scaffold를 만들고 Author가
  프로젝트 기준서를 작성한다. 기존 accepted Keystone corpus가 있는 프로젝트는 adoption
  결정으로 현재 document root와 구조를 채택하며 config나 R000을 소급 생성하지 않는다.
- 결정: 초기화 전 code, README, 설정 조사는 Main의 일반 능력에 맡기고 Reader의 선행 책임으로
  규정하지 않는다.
- 이유: 기준서를 만들기 위해 이미 기준서가 필요하다는 순환 의존을 없애면서 Author 중심의
  문서 모델과 작업 복구 능력을 유지하기 위해서다.

<!-- key: id=key.work.decisions.dec-works-016 refs=key.doc.decision key.topic.bootstrap key.topic.artifact-graph key.role.linker key.role.coordinator -->
## DEC-WORKS-016: Keystone은 profile 없이 하나의 운영 모델을 사용한다

- 관련 work: Bootstrap Runtime Standard, Artifact Graph Standard, Linker Standard,
  Coordinator Standard
- 상태: accepted
- 결정: Lite, Standard, Graph, Orchestrated 같은 도입 profile을 두지 않는다.
- 결정: 기준서와 작업 복구가 중심이며 Artifact Graph와 coordination은 문서와 구현을 연결하는
  Keystone의 핵심 능력이다.
- 결정: Graph relation이나 Coordinator 산출물이 아직 없다는 이유만으로 초기화 실패나 낮은
  profile로 판정하지 않는다.
- 결정: Linker는 존재하는 evidence만으로 fail-soft report를 제공한다.
- 이유: 기능을 단계별 제품으로 분리하기보다 하나의 목표를 유지하면서 현재 작업에 필요한
  능력만 자연스럽게 사용하기 위해서다.

<!-- key: id=key.work.decisions.dec-works-017 refs=key.doc.decision key.topic.acceptance key.topic.user-decision key.role.author -->
## DEC-WORKS-017: Main은 위임 범위에서 진행·검증·수락한다

- 관련 work: Project Standard, Bootstrap Runtime Standard, Author Standard, Coordinator Standard
- 상태: accepted
- 결정: 별도의 보편적인 사용자 최종 승인 단계는 두지 않는다. Main은 명시된 요청과 기준
  안에서 작업하고 검증한 뒤 수락한다.
- 결정: Worker `DONE`은 Main 수락이 아니며 Main이 실제 결과, scope, completion criteria,
  verification과 residual risk를 확인한다.
- 결정: 프로젝트 목적·범위, 충돌 대안, 민감 정보, 파괴적 migration, 외부 공개·비용,
  위임 범위 확장처럼 실제 사용자 판단이 필요한 항목만 별도 User Decision step으로 둔다.
- 결정: User Decision이 끝나면 원래 Init, Author 또는 Coordinator 흐름을 자동 resume한다.
- 이유: 이미 검증 가능한 단계까지 반복 승인을 요구하지 않고, 사용자만 결정할 수 있는
  지점에 질문을 집중하기 위해서다.

<!-- key: id=key.work.decisions.dec-works-018 refs=key.doc.decision key.topic.work-execution key.topic.skill-contract key.role.linker key.role.coordinator -->
## DEC-WORKS-018: Routing과 실행 환경은 필요한 경계에서만 명시한다

- 관련 work: Project Standard, Subagent Standard, Author Standard, Linker Standard,
  Coordinator Standard
- 상태: accepted
- 대체: `DEC-WORKS-007`, `DEC-WORKS-008`의 자동 Coordinator routing,
  `DEC-WORKS-012`의 mandatory routing ceremony
- 결정: 작은 명확한 작업은 Main이 직접 수정한다. 복수 surface나 권한 경계가 있을 때만
  routing context를 명시적으로 기록한다.
<!-- key: id=key.claim.linker.read-only-invocation -->
- 결정: Linker는 read-only이므로 Main이 별도 사용자 허락 없이 사용할 수 있다.
- 결정: Coordinator는 work scope마다 사용자 허락을 받는다. 직접 호출은 해당 범위의
  허락이며 같은 범위의 assignment, review, repair에서는 반복하지 않는다.
- 결정: Keystone은 single workspace, worktree, branch, writer 수와 integration strategy를
  강제하지 않는다. 위임된 skill 또는 host 환경이 자기 계약으로 선택할 수 있다.
- 결정: 위임이 유용하면 Main은 사용자에게 위임 여부를 물을 수 있다. 외부 스킬 주입은
  assignment authority를 올리지 않는다.
- 이유: 과도한 routing ceremony와 실행 환경 강제를 제거하면서 scope, 기존 변경 보존과 Main
  acceptance 경계는 유지하기 위해서다.

<!-- key: id=key.work.decisions.dec-works-019 refs=key.doc.decision key.topic.work-round key.topic.work-sequence key.topic.bootstrap -->
## DEC-WORKS-019: Round step은 S01부터 시작하고 R000은 Foundation에 예약한다

- 관련 work: Project Standard, Bootstrap Runtime Standard, Author Standard, R002
- 상태: accepted
- 결정: 일반 작업 round와 round 내부 step 번호는 각각 `R001`, `S01`부터 시작한다.
- 결정: `R000 Project Foundation`은 최초 기준서가 아직 없는 상태에서 기준서를 세우는
  foundation round임을 나타내기 위해 예약한다. R000 내부 step도 `S01`부터 시작한다.
- 결정: R002의 Bootstrap Runtime Standard와 Skill Runtime Implementation은 각각 S01과 S02로
  기록한다.
- 결정: 이미 수락된 R001의 S00-S09 식별자는 역사 보존을 위해 소급 변경하지 않는다.
- 이유: 0번 round의 의미적 예외와 일반 실행 순서의 1-based numbering을 분리하기 위해서다.

<!-- key: id=key.work.decisions.dec-works-020 refs=key.doc.decision key.topic.keystone-metadata key.topic.temporal-metadata key.topic.acceptance -->
## DEC-WORKS-020: 문서와 결정에 의미 있는 날짜를 기록한다

- 관련 work: Project Standard, Bootstrap Runtime Standard, Author Standard, Init Standard
- 결정일: 2026-07-23
- 상태: accepted
- 결정: 새 원천 문서에는 변경하지 않는 최초 생성일 `created_at`을 기록한다.
- 결정: 현재 문서 의미가 수락되면 `approval.accepted_at`을 기록하고, 의미 변경으로 approval이
  `pending`이 되면 현재 수락일을 제거한 뒤 재수락 시 새 날짜를 기록한다.
- 결정: 새 결정에는 `결정일`을 기록한다. 승인일과 효력일이 다르거나 문서·결정의 대체 시점을
  보존해야 할 때만 선택적 날짜를 추가한다.
- 결정: 일반적인 `updated_at`은 도입하지 않으며, 기존 문서 날짜를 근거 없이 추정하거나
  일괄 migration하지 않는다.
- 결정: 거버넌스 날짜는 `YYYY-MM-DD`를 기본으로 하고, 실행 event의 정확한 순서가 필요한 별도
  기록만 ISO 8601 timestamp와 timezone을 사용한다.
- 이유: 결정·승인·효력의 시간 맥락을 작업 복구와 감사에 사용할 수 있게 하면서 형식 변경과
  Git 이력까지 중복 기록하는 metadata 부담은 피하기 위해서다.

<!-- key: id=key.work.decisions.dec-works-021 refs=key.doc.decision key.topic.acceptance key.topic.finalization key.topic.progress-update key.topic.verification -->
## DEC-WORKS-021: Main acceptance와 원천 문서 finalization 완료를 분리한다

- 관련 work: Project Standard, Author Standard, Coordinator Standard
- 결정일: 2026-08-04
- 상태: accepted
- 결정: Main이 구현·review·verification 결과를 수용하면 해당 work 또는 step은
  `accepted`가 된다.
- 결정: 영향 원천 문서 갱신과 교차 문서 정합성 검증은 기존 Progress 또는 Change Set의
  `finalization.state: pending | in_progress | complete | waived` 하위 상태로 기록한다.
  `finalized`를 progress status, work status, lifecycle 또는 approval 값으로 추가하지 않는다.
- 결정: Finalization이 미완료이거나 실패하면 구현 수용은 취소하지 않고
  `finalization.state: pending` 또는 `in_progress`로 남긴다. 이 상태에서는 Keystone workflow를
  완전히 종료하지 않고 다음 구현 step보다 finalization을 먼저 복구한다.
- 결정: Author는 finalization 대상 문서 후보를 계산하고 각 후보의 update, no-change,
  historical, out-of-scope, clarification 또는 integration-gate disposition과 근거를 남긴다.
- 결정: Coordinator는 Main acceptance evidence와 worker·review·verification 결과를 Author
  finalization 입력으로 전달하되, 원천 문서 수정 범위와 기준은 Author가 소유한다.
- 결정: Finalization은 operative artifact, 원천 문서 의미, current step/work/round 상태,
  Change Set, integration gate, residual·deferred item, 또는 namespace 충돌 후보를
  실질적으로 바꾸는 acceptance에 의무로 적용한다.
- 결정: 원천 문서나 workflow 상태 변경이 없는 조사·검토·설명은 finalization 기록을
  강제하지 않는다. Acceptance가 있지만 정합화 대상이 없는 경우에만 `required: false`와 근거를 남긴다.
- 결정: 완료되지 않은 required finalization은 동일 work의 다음 implement assignment,
  `in_progress` 전이, 다음 step Main acceptance와 work 종료를 차단하는 scoped hard gate다.
- 결정: Finalization 복구를 위한 조사·문서 수정·검증·충돌 조사와 다음 step의
  read-only 사전 조사는 허용한다.
- 결정: 다른 work/round는 dependency, 공유 namespace·current step·Change Set 또는
  방향 영향이 없을 때만 병행 진행할 수 있다.
- 결정: 긴급 우회는 자동 예외가 아니며 Main/user가 이유, 허용 범위,
  finalization 부채, 복구 조건과 residual risk를 명시적으로 수용해야 한다.
- 결정: Main acceptance event는 finalization 필요성 판정의 자동 trigger다. Main 또는
  현재 work scope에 허용된 Coordinator는 별도 사용자 요청 없이 대상을 판정하고
  필요하면 Author Acceptance Finalize Mode를 즉시 시작한다.
- 결정: Coordinator 허용이 없는 Main direct workflow에서는 Main이 Author finalization을
  직접 시작하며, finalization을 이유로 Coordinator 권한을 자동 생성하지 않는다.
- 결정: 자동 finalization은 이미 수용된 work의 원천 문서와 검증 범위에
  한하며, 다른 work 수정, 기준 의미·scope·acceptance criteria 변경 또는 high-impact
  결정이 필요하면 pending을 유지하고 필요한 결정·승인을 요청한다.
- 결정: Finalization은 runtime 필수 절차와 executable validator 검증의 두 계층으로
  강제한다. Runtime이 영향 후보·수정·상태 전이를 소유하고 validator가 기계적
  정합성 evidence를 생성한다.
- 결정: Validator는 진단 전용이며 원천 문서 수정, acceptance 또는 `finalization.state: complete`를
  자동 생성하지 않는다. Runtime 판단과 충돌하거나 실패하면 pending을 유지한다.
- 결정: Repository가 pre-commit/CI hook을 지원하면 동일 validator를 재호출하는
  안전망을 연결하되, hook은 runtime finalization을 대체하거나 의미·권한·acceptance를
  추론하지 않는다.
- 결정: Finalization 대상에서 validator가 없거나 호출할 수 없으면
  `validator_unavailable`, process 실행·결과 생성이 실패하면 `validator_execution_failed`로
  분리하고 두 경우 모두 fail-closed로 처리한다.
- 결정: Fail-closed에서 Main `accepted`는 유지하되 `finalization.state: complete`로 전환하지
  않고 pending을 남긴다. 수동 문서 검토로 required validator evidence를 대체하지 않는다.
- 결정: Validator가 제공·복구되면 기존 문서 수정과 acceptance evidence를 보존한
  채 동일 finalization을 재개해 validator를 다시 실행한다.
- 결정: Core finalization validator engine과 기본 규칙은 설치된 Keystone package가
  자체 포함하며, 소비 프로젝트에 validator source 복사본을 생성하지 않는다.
- 결정: 프로젝트는 document root, 문서 구조, namespace과 추가 검사를 설정·adapter로
  확장할 수 있지만 core 규칙·fail-closed를 제거·약화하거나 validator의 권한을
  수정·acceptance·finalization 완료 전이로 높일 수 없다.
- 보완 결정일: 2026-08-05
- 결정: 단수 `current_step`을 권위 모델로 사용하지 않는다. 활성 Step은 상태를 복제하지 않는
  `active_steps` 참조 목록으로 표현하며 0개 이상의 동등한 Step을 허용한다.
- 결정: 다른 Step을 처리하는 과정에서 미래 Step 일부를 먼저 수행했지만 해당 Step 상태를
  전이하지 않은 경우, 대상 Step에 `early_work`로 원인·처리 범위·남은 범위·상태 영향 없음
  을 기록한다. 미래 Step은 이 기록만으로 활성화하거나 완료하지 않는다.
- 결정: 현재 Step 수용 시 해당 Step만 직접 상태 전이하고, Work·Round·root index·Context Map처럼
  상태를 집계하거나 노출하는 상위 소유자는 자체 전이 조건 충족 여부를 평가한다. 형제·미래
  Step 상태는 변경하지 않는다.
- 결정: Core validator는 새 사용자 호출 스킬이 아니라 `keystone-author` 설치 패키지의 bundled
  script로 제공한다. Author가 finalization에서 자동 실행하고 hook/CI는 같은 command를 재호출한다.
- 결정: Pre-commit/CI와 project-local wrapper는 package가 제공하는 안정적 command/interface를
  호출하는 surface이며 독립 validator source of truth가 아니다.
- 이유: 구현 수용 사실을 보존하면서 Progress, Work Order, Change Set, index,
  standard, 복구 안내가 서로 다른 시점을 가리키는 상태를 workflow 종료로 오인하지
  않기 위해서다.

<!-- key: id=key.work.decisions.dec-works-022 refs=key.doc.decision key.topic.artifact-graph key.topic.provenance -->
## DEC-WORKS-022: `produced_from`은 provenance field로 유지한다

- 관련 work: R003 Dependency and Work Gate Standard, Artifact Graph Standard, Linker Standard
- 결정일: 2026-08-04
- 상태: accepted
- 결정: `produced_from`은 output artifact가 어느 source document, decision 또는 work order의
  산출물인지 기록하는 provenance/authority field로 유지하고 공식 typed relation에 추가하지 않는다.
- 결정: Linker는 선언된 `produced_from: <source>`에서 `<source> produces <output>`의
  역방향 edge를 generated/inferred evidence로 파생한다.
- 결정: Source surface에 `produced_from`과 `produces`를 양방향으로 중복 기록하지 않는다.
- 결정: Work-order provenance는 artifact-to-artifact 파생을 나타내는 `derived_from`과
  혼용하지 않는다.
- 결정: `produced_from` target이 없거나 유효한 source로 해석되지 않으면
  unresolved provenance 또는 metadata gap으로 보고한다.
- 이유: 이미 사용 중인 output-to-source provenance를 보존하면서 공식 `produces`와의
  양방향 중복·drift를 피하고 `derived_from`의 파생 의미를 유지하기 위해서다.

<!-- key: id=key.work.decisions.dec-works-023 refs=key.doc.decision key.topic.artifact-graph key.topic.revision-history -->
## DEC-WORKS-023: `revised_by`는 revision-history evidence로 유지한다

- 관련 work: R003 Dependency and Work Gate Standard, Artifact Graph Standard, Linker Standard
- 결정일: 2026-08-04
- 상태: accepted
- 결정: `revised_by`는 문서·artifact의 개정 이력을 탐색하기 위한 revision-history
  evidence로 유지하고 공식 typed relation에 추가하지 않는다.
- 결정: `revised_by`만으로 authority, impact propagation, `supersedes`, `produces`,
  `governed_by`를 추론하지 않는다.
- 결정: 정확한 semantic relation이 필요하면 적합한 typed relation, decision, Change Set
  또는 revision record로 명시한다.
- 결정: Target이 없거나 의미가 모호하면 relation error로 단정하지 않고
  informational 또는 unknown revision evidence로 보고한다.
- 이유: `revised_by`는 개정의 원인·권위·대체·산출 중 어느 의미인지 단독으로
  확정할 수 없으므로 기존 semantic relation의 정확성을 해치지 않고 history 탐색 단서로만
  사용하기 위해서다.

<!-- key: id=key.work.decisions.dec-works-024 refs=key.doc.decision key.topic.artifact-graph key.topic.keystone-metadata key.topic.finalization key.role.linker key.role.author key.role.coordinator -->
## DEC-WORKS-024: Graph mutation authority와 source surface ownership을 분리한다

- 관련 work: R005 Artifact Graph Synchronization
- 결정일: 2026-08-05
- 상태: accepted
<!--
key:
  id: key.claim.linker.graph-mutation-authority
  supersedes:
    - key.claim.linker.read-only-interpretation
    - key.claim.linker.read-only-invocation
-->
- 결정: Linker는 Artifact Graph의 canonical mutation authority를 가진다. Artifact ID, capability
  node, relation, locator, lifecycle과 replacement의 생성·변경·폐기 결정을 Linker가 소유한다.
- 결정: Linker의 graph mutation authority는 원천 문서의 자연어 의미나 repository implementation
  logic을 직접 수정하는 authority를 포함하지 않는다.
- 결정: Author는 문서 의미와 문서 키메타의 물리적 반영을 소유한다. Coordinator 또는 Main
  direct는 code/config/schema/API/test 구현과 repository anchor의 물리적 반영을 소유한다.
- 결정: Author와 Coordinator/Main은 typed relation을 독자적으로 확정하지 않고 Linker가 만든
  exact graph mutation을 자기 surface의 의미·구현 evidence로 attestation한 뒤 적용한다.
- 결정: Graph-relevant 문서 또는 repository 의미 변경은 별도 사용자 요청 없이 graph
  synchronization lifecycle을 시작한다. 실제 호출 연결은 Main 또는 host runtime이 수행하며
  이 trigger만으로 Coordinator 권한이나 work scope를 자동 생성하지 않는다.
- 결정: Graph transaction은 delta, canonical mutation, surface attestation, baseline 확인,
  surface owner 적용, Linker reconstruction과 mechanical validator 통과 뒤에만 `verified`가 된다.
- 결정: `inferred` relation은 자동 mutation으로 반영하지 않는다. `observed` relation은 해당
  surface owner의 attestation을 요구한다.
- 결정: 프로젝트 전체 graph coverage와 current transaction completeness를 구분한다. 현재
  transaction 밖의 legacy metadata gap은 debt로 보고할 수 있지만 현재 변경 범위가 완결되면
  transaction을 `verified`로 판정할 수 있다.
- 결정: Capability를 문서와 구현 사이의 안정적인 중심 node로 우선 사용하되 단일 schema 제약,
  특정 정책 구현 등 capability node가 과한 경우 문서 item과 artifact의 직접 연결을 허용한다.
- 결정: 기존 metadata는 읽기 호환하고 신규 또는 의미가 변경된 metadata부터 canonical 형식으로
  수렴한다. 기존 corpus의 일괄 metadata migration은 요구하지 않는다.
- 결정: R004 finalization은 R005에서 graph-relevant change의 graph sync disposition과 verified
  evidence를 요구하도록 후속 확장한다. Graph sync 미완료는 Main acceptance를 취소하지 않지만
  required finalization 완료를 차단한다.
- 결정: R005 검증은 Keystone 저장소 내부의 package-owned 합성 fixture와 CLI로 닫는다. Uptendo
  등 외부 소비 프로젝트 상태는 R005 acceptance 조건이 아니며 실제 사용에서 발견한 문제는
  후속 corrective round로 다룬다.
- 이유: Linker가 graph 의미를 가장 정확히 해석하면서도 권고만 하고 surface owner가 relation을
  다시 해석하는 기존 handoff는 graph 누락과 drift를 폐루프로 방지하지 못했다. Graph 의미 결정과
  source write를 분리한 검증 가능한 transaction으로 기준서와 실제 산출물의 양방향 연결을
  안정적으로 유지하기 위해서다.
