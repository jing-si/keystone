---
doc_type: standard
created_at: "2026-05-31"
document_lifecycle: active
approval:
  state: pending
key:
  id: key.standard.project
  refs:
    - key.doc.source
    - key.topic.document-system
    - key.topic.artifact-graph
    - key.topic.skill-contract
    - key.topic.key-prefix
    - key.topic.bootstrap
    - key.topic.initialization
    - key.topic.runtime-independence
    - key.topic.temporal-metadata
---

# Keystone 프로젝트 기준서

<!-- key: id=key.standard.project.purpose refs=key.doc.source key.topic.skill-contract key.topic.bootstrap -->
## 목적

이 기준서는 Keystone을 문서 기반 project control plane으로 정의하기 위한 프로젝트 공통
규칙을 정의한다. Keystone의 목표는 Main 또는 필요한 User Decision으로 수락한 의도와
결정(6), 원천 문서(2),
capability(16), code, config, schema, API, test artifact, bounded worker 실행 결과를 하나의
추적 가능한 작업 흐름으로 연결하는 것이다.

Keystone에서 문서는 단순 산출물이 아니라 사람, AI, 프로젝트가 공유하는 좌표계다.
기준서(3)와 작업서(4)는 의도와 규칙을 보존하고, 아티팩트 그래프(14)는 문서와 실제
code/config/schema/API/test 사이의 연결과 영향 후보를 드러내며, worker assignment는 bounded
worker가 같은 의도와 경계 안에서 작업하도록 context를 제공한다.

1. `keystone-reader`: 기준서(3), 작업서(4), artifact graph 필요 단서를 읽고 필요한 context
   brief를 만든다.
2. `keystone-clarify`: 사람의 high-impact 의도와 결정(6)을 topic 단위로 정리한다.
3. `keystone-author`: 수락된 결정(6)과 범위 안에서 원천 문서(2)와 Change Set(17)을 작성하거나
   수정한다.
4. `keystone-linker`: Source surface를 read-only로 조사해 Artifact Graph를 해석하고 문서,
   capability(16), code, config, schema, API, test artifact의 canonical graph mutation과
   impact/stale/gap 후보를 결정한다.
5. `keystone-coordinator`: Keystone context를 bounded worker assignment로 만들고 worker
   report를 Keystone workflow로 회수한다.
6. `keystone-init`: 새 프로젝트에 R000과 최소 문서 기반을 만들고 프로젝트 기준서 작성
   흐름을 시작한다.

이 구현 저장소의 현재 기준서(3)와 작업서(4)는 최종 Keystone 스킬이 이미 존재한다고
가정했을 때 만들어졌을 문서 구조와 계약을 사람이 먼저 작성한 부트스트랩 기준 corpus(10)다.
개발 흐름은 이 corpus를 바탕으로 스킬을 구현한 뒤, 구현된 스킬이 같은 구조와 의미의 문서를
재생산하거나 유지할 수 있는지 검증하는 방향을 따른다.

<!-- key: id=key.standard.project.scope refs=key.doc.source key.topic.document-system key.topic.skill-contract -->
## 적용 범위

- 설정된 document root(1) 아래의 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 기록
- 키메타(9)와 코드 앵커(18)로 연결되는 capability, code, config, schema, API, test artifact
- Keystone worker assignment와 worker report contract
- 향후 Keystone skill source file
- Keystone project setting과 target project local setting
- 문서 읽기, 문서 작성, clarification, coordination workflow
- 초기화 상태 탐지, R000 Project Foundation과 Init handoff/resume
- 향후 Keystone coordination 스킬과 호환되어야 하는 작업서 step

<!-- key: id=key.standard.project.out-of-scope refs=key.topic.skill-contract key.topic.external-assist -->
## 적용하지 않는 범위

- 관련 없는 로컬 IDE 파일
- 사용자가 명시적으로 요청하지 않은 package publishing, marketplace registration, global install
- 명시적으로 요청되지 않은 persistent worker handoff 문서
- 사용자 명시 호출이나 수락된 Keystone 문서의 허용 없이 외부 보조 스킬(12)을 자동으로 사용하는
  동작

<!-- key: id=key.standard.project.terms refs=key.doc.source key.topic.document-system key.topic.skill-contract key.topic.key-prefix key.topic.bootstrap key.topic.external-assist -->
## 표준 용어

표준 용어는 Keystone 문서 전체에서 같은 개념을 같은 이름으로 쓰기 위한 기준이다.

첨자 규칙은 다음과 같다.

1. `(1)`, `(2)` 같은 첨자가 붙은 용어는 이 section에 정의된 표준 용어로 판단한다.
2. 표준 용어 정의는 `(n) 선호 언어명(영문명): 짧은 설명` 형식을 따른다.
3. 본문에서는 `설정된 document root(1)`처럼 선호 언어명 바로 뒤에 첨자를 붙인다.
4. 새 표준 용어가 필요하면 기존 첨자와 충돌하지 않는 새 번호를 추가한다.

(1) 설정된 document root(configured document root): Keystone 원천 문서 root directory

- 의미: `STD-KEYSTONE-010`의 document root resolution 결과로 정해진 Keystone 원천 문서
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
- 사용 규칙: 작업 round(13) 안의 work node와 step으로 작성하며, coordinator가 Current Step
  Brief와 Context Pack을 복구할 수 있게 작성한다.

(5) 진행 기록(progress record): 활성 step들과 workflow 상태를 복구하는 문서

- 의미: `active_steps`, step status, main acceptance, `early_work`, 최근 report와 보류 결정을 담는 원천 문서
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

(9) 키스톤 메타데이터(Keystone metadata, 키메타): 원천 문서(2)와 section을 식별하고
연결하기 위한 구조화 메타데이터

- 의미: 문서 frontmatter의 `key.id`, `key.refs` 또는 Markdown comment의 `key: id=... refs=...`
  형태로 문서와 section의 canonical identifier와 관련 문서 후보를 선언한다.
- 권위 규칙: `STD-KEYSTONE-015`
- 사용 규칙: 키메타는 문서 탐색과 영향 분석의 evidence지만 자동 수정 또는 자동 수락 근거가
  아니다.

(10) 부트스트랩 기준 corpus(bootstrap reference corpus): 최종 Keystone 스킬이 재생산해야 할
문서 모델을 사람이 먼저 작성한 원천 문서(2) 집합

- 의미: 이 구현 저장소에서 현재 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 기록은 Keystone
  스킬이 이미 동작했다면 만들어졌을 구조와 의미를 수작업으로 먼저 표현한 reference corpus다.
- 사용 규칙: 원천 문서(2)의 일부이며 파생 에이전트 문서(8)가 아니다. 구현된 스킬이 이
  corpus와 같은 문서 모델을 재생산하거나 유지할 수 있는지 검증하는 기준으로 사용한다.

(11) key prefix(key prefix): Keystone-managed 원천 문서(2)를 파일명으로 식별하기 위한
소문자 prefix

- 의미: 파일명이 `key-`로 시작하거나 정렬용 숫자 뒤에 `_key-`를 가진 Markdown 문서는
  Keystone 스킬로 읽기, 작성, 수정, 실행 routing을 해야 하는 Keystone-managed 원천 문서(2)다.
- 사용 규칙: `key`는 소문자로 쓰고, 그 뒤 이름은 소문자 kebab-case를 사용한다. 문서 순서를
  정해야 할 때만 앞에 두 자리 숫자와 `_`를 붙인다. 같은 위치에서 `00_`을 이미 사용했다면
  다음 순서 문서는 `01_`, 그 다음은 `02_`를 사용한다.
- 예: `00_key-index.md`, `01_key-project-standard.md`, `key-work-project-standard.md`,
  `key-progress.md`

(12) 외부 보조 스킬(external assist skill): Keystone 외부에서 내용 구상, 검토, 비교,
조사, 품질 보조를 제공하는 skill, workflow, tool

- 의미: 문서에 담을 후보 내용이나 판단 재료를 만들 수 있지만 Keystone 문서 형식, 기록 위치,
  상태 의미, metadata 규칙을 대신 정하지 않는다. Code/config/schema/test 수정 절차를 돕는 코딩
  workflow도 외부 보조 스킬에 포함된다.
- 사용 규칙: 사용자가 명시적으로 호출했거나 수락된 Keystone 기준서(3) 또는 작업서(4)가
  허용한 경우에만 보조 input 또는 injected skill로 사용한다.
- Coordinator 사용 규칙: 작은 명확한 code/config/schema/API/test 수정은 Main direct로 처리할
  수 있다. 사용자가 위임을 허락해 Coordinator를 사용할 때 명시된 외부 코딩 스킬은
  Coordinator를 대체하지 않고 worker assignment(19)의 injected skill contract로 주입한다.

(13) 작업 round(work round): 특정 시점의 기준서와 목표를 바탕으로 진행하는 작업 차수

- 의미: 기준서 개정, 기능 추가, 기능 변경, 검증처럼 하나의 목적을 가진 작업 묶음이다.
- 사용 규칙: folder는 `r{number}-{slug}` 형식을 사용한다. `r`은 round를 뜻한다. 각 round
  안에서는 작업 step을 `S01`부터 다시 번호 매긴다. `R000`은 최초 기준서가 아직 없는
  Project Foundation round를 나타내기 위해 예약한다.

(14) 아티팩트 그래프(artifact graph): 사람의 의도, 원천 문서(2), capability, code, config,
schema, API, test, verification evidence를 키메타(9), 코드 앵커(18), repository evidence로 연결한 typed
graph

- 의미: 문서와 프로젝트 구현을 하이퍼링크처럼 탐색하고 영향 분석을 수행하기 위한 관계 구조다.
- 사용 규칙: graph는 변경 후보를 찾는 데 사용하며, 변경 여부와 acceptance는 main 또는
  사용자가 판단한다.

(15) artifact node(artifact node): 아티팩트 그래프(14)에서 `key.id`를 가진 식별 가능한 대상

- 의미: 기준서 section, 결정, 작업 step, capability, API contract, code symbol, test artifact,
  config/schema 같은 추적 가능한 단위다.
- 사용 규칙: artifact node의 ID는 path나 line number가 아니라 의미와 책임을 기준으로 정한다.

(16) capability(capability): 사람이 이해하는 기능적 능력 또는 재사용 가능한 도메인 능력

- 의미: code symbol보다 안정적인 graph 중심 node다. 기준서는 capability를 govern하고, code는
  capability를 provide하거나 use하며, test는 capability를 verify한다.
- 사용 규칙: 새 기능을 만들기 전에는 관련 capability를 먼저 탐색한다.

(17) Change Set(Change Set): 하나의 사람 의도 또는 결정(6)을 문서, code/config/schema/API/test
변경 후보와 검증으로 묶는 변경 단위

- 의미: changed nodes, impact seeds, required/optional candidates, excluded scope,
  verification, acceptance 상태를 함께 담는 구조다.
- 사용 규칙: 큰 변경이나 문서-code/config/schema/API/test 동시 영향이 있는 변경은 Change Set으로
  조율한다.

(18) 코드 앵커(code anchor): code, test, config artifact 안에서 아티팩트 그래프(14)를 구성하기
위해 남기는 Keystone annotation

- 의미: code/config/schema/API/test artifact의 stable ID, kind, provides, uses, implements,
  governed_by, verifies 같은 typed relation을 선언하는 주석이다.
- 사용 규칙: 모든 코드에 붙이지 않고 public API, reusable core method, domain rule,
  shared service, 중요한 test, schema/config/auth/security boundary 같은 semantic anchor에만
  붙인다.
- 구분: 키메타(9)는 원천 문서(2)와 section을 위한 metadata이고, 코드 앵커는 code/config/schema/API/test
  artifact를 아티팩트 그래프(14)에 연결하기 위한 annotation이다.

(19) Worker assignment(worker assignment): Keystone context를 bounded worker가 수행할 수
있는 작업 입력으로 압축한 runtime output

- 의미: intent summary, source documents, decisions, artifact context, allowed edit scope,
  forbidden changes, verification, document sync requirement를 담는 실행 입력이다.
- 사용 규칙: 원천 문서(2)가 아니며, Keystone 기준서와 작업서에서 복구한 context를 외부
  worker에게 전달하기 위한 파생 runtime output이다.

(20) Worker report(worker report): bounded worker가 수행 결과를 Keystone workflow로 되돌리는
runtime output

- 의미: changed files, changed artifact IDs, tests run, verification result, scope check,
  document sync need, metadata sync need, residual risk를 담는 실행 결과 보고다.
- 사용 규칙: progress status나 Main acceptance를 대체하지 않는다.

<!-- key: id=key.standard.project.core-rules refs=key.doc.source key.topic.document-system key.topic.skill-contract key.topic.key-prefix key.topic.bootstrap -->
## 핵심 규칙

<!-- key: id=key.standard.project.std-keystone-001 refs=key.doc.source -->
### STD-KEYSTONE-001: 사람이 읽을 수 있는 원천 문서(2)가 권위다

원천 문서(2)는 사람이 읽을 수 있어야 하며 intended behavior, policy, accepted decision의
normative truth다. 다음 문서를 포함한다.

1. 기준서(3)
2. 작업서(4)
3. 진행 기록(5)
4. 결정(6) 기록
5. 필요한 경우 범위 문서(7)

파생 에이전트 문서(8)는 원천 문서에서 파생되는 runtime 보조 자료다. 원천 문서와 충돌하면
원천 문서가 우선한다.

문서, code/config/schema/API/test의 권위는 다음처럼 구분한다.

1. 수락된 기준서(3)와 결정(6)은 intended behavior와 policy의 규범적 권위다.
2. Code, config, schema, API contract는 현재 실행 상태 또는 operative contract evidence다.
3. Test와 verification result는 behavior 검증 evidence다.
4. 키메타(9)와 코드 앵커(18)는 navigation and relation evidence이며 문서,
   code/config/schema/API/test의 의미를 대체하지 않는다.
5. 원천 문서(2), code/config/schema/API/test가 충돌하면 어느 한쪽을 조용히 덮어쓰지 않는다.
6. 충돌의 원인과 영향 범위를 분석한 뒤 Main 또는 사용자가 변경 방향을 결정한다.

<!-- key: id=key.standard.project.std-keystone-002 refs=key.topic.bootstrap key.doc.source key.topic.skill-contract -->
### STD-KEYSTONE-002: Keystone은 부트스트랩 기준 corpus(10)로 self-hosting을 검증한다

1. 이 구현 저장소의 현재 기준서(3)와 작업서(4)는 최종 스킬이 만든 파생 에이전트 문서(8)가
   아니다.
2. 이 문서들은 최종 스킬이 존재했다면 만들었을 원천 문서(2)의 구조, 경계, workflow를 사람이
   먼저 작성한 부트스트랩 기준 corpus(10)다.
3. Skill source 생성은 이 corpus를 input contract로 삼아 구현한다.
4. 통합 검증은 구현된 스킬이 같은 문서 모델, role boundary, verification path를 재생산하거나
   유지할 수 있는지 확인한다.
5. 스킬 구현과 corpus가 충돌하면 원천 문서(2)를 임시 권위로 두고, 충돌이 의도 변경인지 구현
   결함인지 main/user 결정(6)을 받는다.

<!-- key: id=key.standard.project.std-keystone-003 refs=key.doc.source key.topic.document-system -->
### STD-KEYSTONE-003: 기준서(3)와 작업서(4)는 책임이 다르다

1. 기준서: 프로젝트 정책, 표준, 도메인 규칙, 재사용 가능한 guidance를 정의한다.
2. 작업서: AI 작업의 구체적 목표, 범위, 순서, 완료 기준, 중단/보고 조건, 검증 경로를
   정의한다.

새 기준서를 작성하거나 수정할 때는 다음 구조를 우선한다.

1. 짧은 목적 문단
2. 적용 범위와 적용하지 않는 범위
3. 번호 목록 중심의 규칙
4. 필요한 경우 표준 용어 첨자
5. 기존 STD와 중복되면 새 규칙을 만들지 않고 기존 STD를 참조

<!-- key: id=key.standard.project.std-keystone-004 refs=key.doc.source key.topic.document-system -->
### STD-KEYSTONE-004: 기준서는 반복 context를 줄인다

1. 기준서는 장기 정책, 아키텍처, convention, 도메인 규칙, 재사용 가능한 결정을 둔다.
2. 작업서는 같은 정책을 반복해서 복사하지 않고 필요한 기준서를 참조한다.
3. 반복되는 날짜별 task document 대신 기준서와 작업서가 primary context source가 된다.

<!-- key: id=key.standard.project.std-keystone-005 refs=key.doc.standard key.topic.document-system key.topic.standard-numbering -->
### STD-KEYSTONE-005: STD 번호는 주제 그룹 단위로 관리한다

STD 번호는 작성 순서가 아니라 기준의 성격과 책임 범위를 기준으로 배정한다. 새 STD는 가장
가까운 주제 그룹의 번호대를 사용한다.

번호대는 다음처럼 예약한다.

1. `001-009`: Core authority
2. `010-019`: Document system
3. `020-029`: Work model
4. `030-039`: Main / execution
5. `040-049`: Skill anchors
6. `050-059`: Project policy

번호 사이의 빈 공간은 향후 같은 그룹의 기준을 추가하기 위해 남겨둘 수 있다. STD 번호를
변경하면 같은 변경 안에서 모든 내부 참조를 함께 갱신해야 한다. 단순 선호나 정렬 목적만으로
기존 번호를 자주 바꾸지 않는다.

<!-- key: id=key.standard.project.std-keystone-006 refs=key.topic.skill-contract key.topic.external-assist key.topic.document-system -->
### STD-KEYSTONE-006: 외부 보조 스킬은 선택적 content-assist layer다

1. Keystone은 문서의 형식, 구조, 기록 위치, metadata, 상태 의미, verification path를
   표준화한다.
2. 문서에 담을 내용을 어떻게 구상하거나 검토할지는 Keystone이 독점적으로 규정하지 않는다.
3. 외부 보조 스킬(12)은 사용자가 명시적으로 호출했거나 수락된 Keystone 문서가 허용한 경우에만
   보조 input 또는 injected skill로 사용할 수 있다.
4. 외부 보조 스킬(12)의 output은 후보 내용이나 판단 재료이며 Keystone 원천 문서(2)를
   대체하지 않는다.
5. Keystone-managed 문서에 반영할 때는 Author가 Keystone 기준에 맞는 문서 구조, 문구,
   metadata, index/progress 반영 범위로 정리한다.
6. Code/config/schema/test 수정 요청에서 외부 코딩 스킬(12)이 명시되면 Coordinator가 해당 스킬을
   worker assignment(19)의 injected skill로 주입할 수 있다.
7. 외부 코딩 스킬(12) 주입은 worker authority를 올리지 않으며, scope, forbidden changes,
   execution environment boundary, verification, report contract는 Coordinator assignment가 정한다.
8. 수락 이후에는 Keystone 기준서와 작업서가 최종 권위다.

<!-- key: id=key.standard.project.std-keystone-007 refs=key.doc.source key.topic.user-decision key.topic.acceptance -->
### STD-KEYSTONE-007: 위임 범위 안의 변경은 Main이 검증하고 수락한다

1. 명시적인 구현·반영 요청은 요청 범위 안의 변경과 Main 수락 권한을 위임한 것으로 본다.
2. Main은 확인 가능한 사실과 수락된 기준을 바탕으로 직접 진행하고 completion criteria,
   scope, verification, residual risk를 확인한 뒤 수락한다.
3. 프로젝트 목적·범위, 충돌하는 유효 대안, 민감 정보, 파괴적 migration, 외부 공개·비용,
   위임 범위 확장처럼 실제 사용자 판단이 필요한 경우만 별도 User Decision으로 요청한다.
4. Worker의 `DONE`이나 스킬 output은 Main 수락을 대체하지 않는다.
5. 승인된 goal, scope, acceptance criteria, status semantics, source authority 밖으로 확장해야
   하면 다시 사용자 결정을 받는다.

<!-- key: id=key.standard.project.std-keystone-008 refs=key.topic.document-system key.doc.source -->
### STD-KEYSTONE-008: 확장보다 최소 구조가 먼저다

1. `STD-KEYSTONE-010`의 document root resolution과 `STD-KEYSTONE-011`의 tree 규칙을 따른다.
2. 범위 문서(7)는 필요할 때만 추가한다.
3. 결정(6) 기록은 수락된 정책이나 설계 선택을 기록해야 할 때만 추가한다.
4. Coordination 문서는 실제 조율 필요가 생길 때만 추가한다.
5. 파생 에이전트 문서(8)는 `STD-KEYSTONE-016` 조건을 만족할 때만 추가한다.

<!-- key: id=key.standard.project.std-keystone-009 refs=key.topic.bootstrap key.topic.runtime-independence key.topic.skill-contract -->
### STD-KEYSTONE-009: 설치된 스킬 계약은 소비 프로젝트 문서와 독립적이다

1. 설치된 스킬 패키지는 해당 스킬의 고유 실행 계약을 자체적으로 소유한다.
2. 소비 프로젝트의 문서는 프로젝트 목적, 정책, 결정, 작업과 artifact evidence를 정의한다.
3. 소비 프로젝트의 `standards/skills/**`는 런타임 선행 조건이 아니며 Init이 생성하지 않는다.
4. 이 저장소의 `00_docs/standards/skills/**`는 스킬 개발·검수 원천 명세다.
5. 초기화 상태와 R000, handoff/resume의 상세 기준은
   `standards/bootstrap/key-standard-bootstrap.md`를 따른다.

<!-- key: id=key.standard.project.std-keystone-010 refs=key.topic.document-system key.doc.source -->
### STD-KEYSTONE-010: Document root resolution은 명시적이고 순서가 있다

설정된 document root(1)는 다음 순서로 해석한다.

1. 현재 사용자 지시
2. `.keystone/config.local.yaml`
3. `.keystone/config.yaml`
4. 프로젝트 로컬 agent instruction file 안의 명시적 Keystone settings block
5. 충돌 없는 기존 문서 관례
6. 위 설정이 없으면 `00_docs/`

복수 후보가 충돌하면 임의로 선택하지 않는다. 초기 설정 선택이면 Init이 직접 묻고, 기존
문서의 채택·이동·대체처럼 프로젝트 의미에 영향을 주면 Clarify의 단일 topic으로 넘긴다.

문서 경로는 영어여야 한다. `00_docs/`는 기본 root이지 고정 root가 아니다. 공통 또는 전역
instruction file은 setup suggestion일 수 있지만, project-local setting으로 수락되기 전에는
persistent Keystone setting이 아니다.

<!-- key: id=key.standard.project.std-keystone-011 refs=key.topic.document-system key.topic.key-prefix key.topic.work-round -->
### STD-KEYSTONE-011: Standards와 works는 index 기반 tree를 사용한다

1. 기준서 위치: `standards/`
2. 작업서 위치: `works/`
3. 기준서 tree는 전체 공통 node에서 시작해 필요한 경우 스킬별 child node로 내려간다.
4. 작업서 tree는 최상위 work round 색인에서 시작해 각 작업 round(13)로 내려간다.
5. 각 작업 round(13)는 round 내부 실행 순서를 관리하는 `00_key-index.md`를 가진다.
6. 작업 round(13) 안의 각 work node도 node별 index file을 가진다.
7. Tree 깊이는 필요에 따라 확장할 수 있다.
8. Final node는 하위 node가 없는 node다.
9. Keystone-managed index file은 문서 순서를 정해야 하면 `00_key-index.md`처럼 숫자와
   `key` 사이에 `_`를 사용한다. 같은 위치에서 `00_`을 이미 사용했다면 다음 순서 문서는
   `01_`을 사용한다.

<!-- key: id=key.standard.project.std-keystone-012 refs=key.topic.document-system key.topic.skill-contract -->
### STD-KEYSTONE-012: 기준서는 parent-child 계층을 가질 수 있다

1. 전체 공통 기준서는 프로젝트 목표, 공통 용어, 문서 흐름, 스킬 목록, 공통 정책을 담는다.
2. 스킬별 child 기준서는 개별 스킬의 trigger, non-trigger, input, output, workflow,
   verification, stop condition을 담는다.
3. Parent 기준서는 상세 규칙을 모두 반복하지 않고 child 기준서로 안내한다.
4. Child 기준서는 현재 작업에 필요한 최종 상세 규칙을 담는다.
5. 전체 공통 기준서와 child 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의 결정(6)을
   받는다. 결정 전까지는 전체 공통 기준서를 임시 우선 기준으로 삼는다.

<!-- key: id=key.standard.project.std-keystone-013 refs=key.topic.key-prefix key.topic.document-system key.topic.work-round -->
### STD-KEYSTONE-013: Keystone-managed file은 key prefix(11)와 kebab-case를 사용한다

1. Keystone-managed 원천 문서(2)는 파일명에 key prefix(11)를 사용한다.
2. 정렬용 숫자가 필요하지 않은 파일은 `key-{slug}.md` 형식을 사용한다.
3. 문서 순서를 정해야 하는 파일은 `{number}_key-{slug}.md` 형식을 사용한다.
4. Slug는 소문자 kebab-case를 사용한다.
5. 정렬용 숫자는 같은 folder 안에서 읽기 순서를 명시해야 할 때만 붙인다.
6. 같은 위치에서 첫 순서 문서는 `00_`, 다음 순서 문서는 `01_`, 그 다음은 `02_`를 사용한다.
7. 정렬용 숫자와 `key` 사이를 제외하고 `_`를 사용하지 않는다.
8. 전체 공통 기준서처럼 정렬용 숫자가 필요한 기준서 파일: `00_key-{slug}.md`
9. 스킬별 최종 기준서 파일: `key-standard-{slug}.md`
10. 최종 작업서 파일: `key-work-{slug}.md`
11. Progress file: `key-progress.md`
12. Decisions file: 필요할 때 `key-decisions.md`
13. Work round folder: `r{number}-{slug}`
14. Slug 기준: 해당 folder 안에서 파일을 명확히 구분할 수 있는 가장 짧은 local name
15. 기존 non-key 또는 legacy uppercase `KEY` bootstrap 문서의 rename은 source path와 link를
    바꾸는 migration이므로 별도 승인된 작업에서만 수행한다.

<!-- key: id=key.standard.project.std-keystone-014 refs=key.topic.key-prefix key.topic.skill-contract -->
### STD-KEYSTONE-014: key prefix(11) 문서는 Keystone 스킬로 routing한다

1. 최초 Keystone 문서 생성과 bootstrap setup은 사용자 또는 main의 명시 요청으로 시작한다.
2. 파일명이 `key-`로 시작하거나 정렬용 숫자 뒤에 `_key-`를 가진 원천 문서(2)는
   Keystone-managed 문서로 판단한다.
3. Keystone-managed 문서를 읽거나 작업 준비 context를 만들 때는 `keystone-reader`로
   routing한다.
4. Keystone-managed 원천 문서(2)를 작성하거나 수정할 때는 `keystone-author`로 routing한다.
5. Keystone-managed 정책, 범위, 문서 구조, 스킬 계약에 관한 high-impact 결정(6)이 필요하면
   `keystone-clarify`로 routing한다.
6. 문서, capability(16), code, config, schema, API, test artifact의 연결, impact candidate,
   stale metadata 후보, metadata gap 후보 탐색은 `keystone-linker`로 routing한다.
7. Keystone-managed 작업서(4)의 step 실행, worker assignment/report, report handling, review,
   verification, acceptance flow를 위임해야 하고 사용자가 허락하면 `keystone-coordinator`로
   routing한다.
8. Keystone 작업 문맥의 작은 명확한 code/config/schema/API/test 수정은 Main direct로 처리할 수
   있다. 위임이 유용하면 사용자에게 Coordinator 사용 여부를 묻는다.
9. 사용자가 Coordinator와 외부 코딩 스킬(12)을 함께 허락하면 해당 스킬을 worker
   assignment(19)의 injected skill로 사용한다.
10. 허락된 Coordinator 범위에서 외부 코딩 스킬(12)이 명시되지 않으면 subagent 기준서의
   `keystone-default-bounded-worker` contract를 사용한다.
11. 여러 외부 코딩 스킬 후보가 있고 선택에 따라 workflow, verification, risk가 달라질 때만
   main/user 선택을 요청한다.
12. Legacy uppercase `KEY-` 또는 `_KEY-` 파일은 filename migration 전까지 Keystone-managed
    문서로 읽을 수 있지만, 새 파일과 rename 대상 파일은 lower-case key prefix(11)를 사용한다.
13. key prefix(11)가 없는 일반 프로젝트 문서는 자동으로 Keystone-managed 문서로 판단하지
    않는다.
14. 외부 보조 스킬(12)은 사용자가 호출했거나 수락된 Keystone 기준서 또는 작업서가 명시적으로
    허용한 경우에만 사용한다.
15. File-changing work의 scope와 실행 주체는 판단하되, `STD-KEYSTONE-046`에 따라 복수
    surface, 권한 경계 또는 audit 필요가 있을 때만 routing context를 명시적으로 기록한다.

<!-- key: id=key.standard.project.std-keystone-015 refs=key.topic.document-system key.doc.source key.topic.keystone-metadata key.topic.code-anchor key.topic.artifact-graph key.topic.work-sequence -->
### STD-KEYSTONE-015: Metadata는 원천 문서와 project artifact의 identity/relation을 표현한다

키메타(9)와 코드 앵커(18)는 아티팩트 그래프(14)를 재구성하기 위한 identity와 relation
evidence다. 이 metadata는 탐색, 영향 분석, context packaging을 돕지만 원천 문서(2), code,
test의 의미나 실제 동작을 대체하지 않는다.

상위 원칙은 다음과 같다.

1. `key.id`와 코드 앵커 `id`는 stable identity를 표현하고, path나 line number 같은 locator와
   분리한다.
2. `key.refs`는 넓은 관련성 또는 탐색 후보 edge이며 자동 수정 근거가 아니다.
3. Typed relation은 가능한 한 이미 존재하는 `key.id`, 코드 앵커 `id`, 또는 허용된 controlled
   vocabulary ID를 참조한다.
4. 같은 `key.id`를 참조하거나 typed relation으로 연결된 artifact는 함께 검토한다.
5. Declared relation, observed relation, inferred relation은 구분해 보고한다.
6. 후보 발견은 자동 채택, 자동 수정, 자동 acceptance 근거가 아니다.
7. 실제 수정은 승인 범위, 의미 영향, source authority, artifact authority를 따져 결정한다.
8. Artifact metadata, relation, locator, stale handling, metadata admission policy의 상세
   기준은 `standards/artifacts/key-standard-artifact-graph.md`를 따른다.
9. 문서, capability(16), code, config, schema, API, test artifact의 impact/stale/gap 후보 해석은
   `keystone-linker` 기준서를 따른다.
10. Artifact Graph의 canonical mutation 결정은 Linker만 소유한다. Linker는 graph state와
    candidate를 해석하고 artifact ID, capability node, relation, provenance, locator, lifecycle,
    replacement의 생성·변경·폐기를 canonical mutation으로 결정하지만 source document 또는
    code/config/schema/API/test source를 직접 쓰지 않는다.
11. Author는 `document_delta`와 canonical mutation을 대조해 문서 의미·문서 metadata patch를
    `confirm | reject | needs_revision`으로 attestation하고 승인된 exact patch를 적용한다.
12. Main direct 또는 허락된 Coordinator는 `artifact_delta`와 canonical mutation을 대조해
    repository 의미·anchor patch를 attestation하고 승인된 exact patch를 적용한다. Validator는
    기계적 진단만 하며 mutation, scope, acceptance 또는 source write를 결정하지 않는다.
13. Main/User만 work scope와 acceptance를 결정한다. Graph-relevant 변경 trigger는
    synchronization lifecycle을 자동 시작하지만 scope를 넓히거나 Coordinator 허락을 만들지 않는다.

Keystone 작업은 문서 탐색, impact review, context brief, worker assignment, review,
verification을 준비할 때 키메타(9), 코드 앵커(18), repository evidence를 함께 사용한다.

아티팩트 해석 순서는 다음 원칙을 따른다.

1. `key-context-map.md`가 있으면 먼저 읽어 active standards와 active work를 찾는다.
2. 기준서(3)는 최상위 기준서에서 시작해 필요한 child 기준서로 내려간다.
3. 작업서(4)는 최상위 work index에서 시작해 active work round와 active work node 또는
   명시된 work node로 내려간다.
4. Active work node 안에서는 node index, 작업서(4), 진행 기록(5)을 함께 읽어 0개 이상의
   `active_steps`와 실행 범위를 복구한다.
5. 결정(6) 기록, 범위 문서(7), 파생 에이전트 문서(8), 키메타와 코드 앵커로 발견한 후보는 위
   순서를 보강하는 추가 evidence로 읽는다.
6. Capability(16)는 문서와 code를 직접 1:1로 묶기보다 기준서가 govern하고 code가 provide/use
   하며 test가 verify하는 중심 node로 우선 검토한다.
7. Capability, code, config, schema, API, test artifact 후보는 코드 앵커 검색과 실제 repository 검색을
   함께 사용한다.
8. 사용자가 특정 step이나 work를 직접 지정하면 해당 work node를 찾을 수 있지만, 실행 판단은
   적용 가능한 기준서(3)를 함께 읽은 뒤에 한다.
9. Legacy `key.topic.current-step`은 단일 권위 포인터로 사용하지 않고 실제 step status와
   `active_steps`를 대조할 compatibility evidence로만 읽는다.
10. 문서 frontmatter의 `key.refs`는 section-level `key.refs`보다 넓은 관련성을 나타낸다.

이 저장소에서 사용하는 controlled vocabulary namespace는 다음을 우선 허용한다.

1. `key.doc.*`: 문서 종류
2. `key.role.*`: Keystone 역할 또는 agent 역할
3. `key.topic.*`: 주제, workflow, 상태, 검토 영역
4. `key.boundary.*`: 승인, 금지, 중단, 예외 경계
5. `key.output.*`와 `key.contract.*`: 산출물과 output contract
6. `key.section.*`: 반복 section 역할
7. `key.step.*`: 작업 단계
8. `key.artifact.*`, `key.mode.*`, `key.verification.*`: artifact, mode, verification 단서
9. `key.capability.*`: 사람이 이해하는 기능적 능력 또는 reusable domain capability
10. `key.api.*`: 외부 또는 내부 API, service boundary, command/query, message schema,
    plugin interface 같은 contract
11. `key.code.*`: 구현 artifact 또는 stable code symbol
12. `key.config.*`: runtime config, feature flag, policy config 같은 설정 artifact
13. `key.schema.*`: DB schema, message schema, validation schema 같은 구조화 contract
14. `key.test.*`: behavior, contract, regression을 검증하는 test artifact

표기 위치는 다음을 따른다.

1. 문서 전체에 적용되는 키메타는 YAML frontmatter의 `key`에 둔다.

   ```yaml
   ---
   doc_type: standard
   key:
     id: key.standard.project
     refs:
       - key.doc.source
       - key.topic.document-system
   ---
   ```

2. 특정 section에만 적용되는 키메타는 heading 바로 위 Markdown comment로 한 줄에 둔다.

   ```markdown
   <!-- key: id=<document-id>.<section-id> refs=<ref-id> <ref-id> -->
   ## Metadata example
   ```

3. 코드 앵커는 다른 작업자가 새로 만들기 전에 발견해야 하는 semantic anchor에만 language
   comment로 둔다. Public API, reusable core method, domain rule, shared service, 위험도가
   높은 schema/config/auth/security boundary, 핵심 test가 우선 대상이다.

   ```text
   keystone: id=key.code.auth.lockout-service.apply-policy kind=code_symbol
   keystone: provides=key.capability.auth.account-lockout
   keystone: governed_by=key.standard.security.account-lockout
   ```

4. Local helper, trivial wrapper, generated code, prototype, 구현 세부사항에 불과한 private
   symbol에는 기본적으로 코드 앵커를 붙이지 않는다.
5. Section-level 키메타는 바로 뒤 heading의 section에 적용된다.
6. Section `key.id`는 가능하면 문서 `key.id`를 prefix로 사용한다.
7. 코드 앵커 ID는 path나 line number를 직접 포함하지 않는다.
8. `key.refs`는 느슨한 keyword가 아니라 탐색 후보 edge로 취급하고, impact propagation은 가능한
   한 코드 앵커 typed relation을 우선 사용한다.

<!-- key: id=key.standard.project.std-keystone-016 refs=key.doc.source key.topic.document-system -->
### STD-KEYSTONE-016: 파생 에이전트 문서(8)는 선택 사항이지만 지원한다

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

<!-- key: id=key.standard.project.std-keystone-017 refs=key.topic.document-system key.topic.keystone-metadata key.topic.artifact-graph -->
### STD-KEYSTONE-017: Artifact ID는 stable identity와 locator를 분리한다

Artifact node(15)의 ID는 artifact가 의미하는 책임과 capability(16)를 식별한다. 문서는 키메타(9)의
`key.id`로, code/config/schema/API/test artifact는 코드 앵커(18)의 `id`로 식별한다. 파일 경로, line number,
일시적 symbol name은 locator evidence이며 ID 자체가 아니다.

1. 좋은 ID는 `key.code.billing.refund-service.issue-refund`처럼 domain, component, responsibility를
   나타낸다.
2. 나쁜 ID는 `key.code.src.services.refund_py.line_142`처럼 path나 line number에 종속된다.
3. 파일 이동, 함수명 변경, 내부 구현 교체가 있어도 의미와 responsibility가 같으면 기존 ID를
   유지한다.
4. 의미가 바뀌면 새 ID를 고려하고, source surface의 canonical replacement relation은
   `supersedes`를 우선 사용한다. `replaced_by`는 generated reverse index에서 파생할 수 있고,
   `aliases`는 typed relation이 아니라 locator 또는 name migration 보조 metadata로 다룬다.
5. Locator는 path, symbol, test name, config key, schema name 같은 현재 위치 evidence로
   report나 generated index에 기록한다.
6. Artifact lifecycle status는 필요할 때 `active`, `deprecated`, `removed`로 표현한다.
7. Removed artifact의 ID를 새 의미에 재사용하지 않는다.
8. Reverse relation은 source에 중복 기록하지 않고 generated index에서 만들 수 있다.

<!-- key: id=key.standard.project.std-keystone-018 refs=key.topic.document-system key.topic.keystone-metadata key.topic.artifact-graph key.topic.verification -->
### STD-KEYSTONE-018: 아티팩트 그래프는 검증 가능해야 한다

아티팩트 그래프(14)는 키메타(9), 코드 앵커(18), repository evidence에서 재구성할 수 있어야 한다.
Generated reverse index나 cache는 source of truth가 아니라 탐색 최적화를 위한 파생 artifact다.

1. Mechanical stale은 verifier 또는 graph validation이 담당한다.
2. Mechanical stale 예시는 duplicate ID, unresolved relation, missing locator, missing symbol,
   deleted test reference, 잘못된 namespace, relation format 오류다.
3. Semantic stale은 reviewer가 담당한다.
4. Semantic stale 예시는 symbol은 존재하지만 더 이상 해당 capability(16)를 제공하지 않음,
   test는 통과하지만 기준서 의도를 검증하지 않음, `uses` relation이 구현 세부사항으로 바뀜,
   중복 core method가 새로 생김이다.
5. Observed relation은 import, call, reference처럼 도구가 발견한 구조적 evidence다.
6. Inferred relation은 AI가 의미적으로 관련 가능성이 있다고 본 후보이며 자동 수정 근거가 아니다.
7. Impact candidate는 `required`, `strong_candidate`, `weak_candidate`, `informational`,
   `excluded`로 등급화한다.
8. `key.refs` topic overlap은 기본적으로 `informational` 또는 `weak_candidate`이며 자동 수정
   대상이 아니다.

<!-- key: id=key.standard.project.std-keystone-019 refs=key.topic.keystone-metadata key.topic.temporal-metadata key.topic.status key.topic.acceptance -->
### STD-KEYSTONE-019: 문서 lifecycle, approval, 시간 metadata와 작업 상태를 분리한다

1. 문서 lifecycle은 `document_lifecycle: draft | active | superseded | archived`를 사용한다.
2. 문서 approval은 `approval.state: pending | accepted | rejected`를 사용한다.
3. `accepted`는 lifecycle이 아니며, 작업 진행 상태·Main 결과 수락·산출물 lifecycle과도
   별도 namespace다.
4. 의미 변경은 approval을 `pending`으로 돌린다. 의미 없는 형식 변경은 비의미 변경임을
   기록하고 기존 approval을 유지할 수 있다.
5. 새 원천 문서는 YAML frontmatter에 최초 생성일 `created_at`을 기록하고, 현재 의미가
   수락되면 `approval.accepted_at`을 기록한다.
6. `created_at`은 변경 이력이 아니라 문서가 처음 생성된 날짜이며 이후 수정하지 않는다.
   `approval.accepted_at`은 현재 의미의 수락일이며 lifecycle 또는 작업 상태를 대체하지 않는다.
7. 결정 기록의 새 결정에는 결정이 확정된 `결정일`을 기록한다. 날짜가 최신이라는 사실만으로
   더 높은 권위를 갖지 않으며, 권위와 대체 관계는 상태와 typed relation으로 판단한다.
8. 새 문서는 YAML frontmatter로 상태와 시간 metadata를 표현한다. 기존 corpus의
   frontmatter를 의미 변경과 함께 자동 migration하지 않으며, 상태·승인 metadata migration은
   별도 승인 작업으로 다룬다.
9. 세부 날짜 형식, 선택적 효력·대체 날짜와 기존 문서 호환 규칙은
   `standards/bootstrap/key-standard-bootstrap.md`를 따른다.

<!-- key: id=key.standard.project.std-keystone-020 refs=key.doc.source key.topic.document-system -->
### STD-KEYSTONE-020: 작업은 문서에서 복구 가능해야 한다

사용자가 "run the next step"이라고 말하면 main은 설정된 document root(1)에서 다음 정보를
복구할 수 있어야 한다.

1. active work round
2. 0개 이상의 활성 step과 각 status source
3. goal
4. completion criteria
5. applicable standards
6. expected scope
7. risks
8. verification

`active_steps`는 Step 상태를 복제하지 않는 참조 목록이며 우선순위나 대표 Step을 강제하지 않는다.
정식 상태 전이 없이 미래 Step 일부가 먼저 처리되면 대상 Step에 `early_work`로 원인, 처리 범위,
남은 범위와 `status_effect: none`을 기록한다.

<!-- key: id=key.standard.project.std-keystone-021 refs=key.topic.document-system key.topic.skill-contract -->
### STD-KEYSTONE-021: 작업서는 goal assignment를 위해 작업을 나눈다

작업서(4)는 명확한 goal로 배정할 수 있는 단위로 작업을 나누어야 한다. 각 단위는 다음
정보를 가진다.

1. 목적
2. 범위
3. 완료 기준
4. 중단/보고 조건
5. 검증 방법
6. 전체 프로젝트를 다시 읽지 않고도 작업할 수 있게 하는 기준서 reference

<!-- key: id=key.standard.project.std-keystone-022 refs=key.topic.document-system key.topic.skill-contract -->
### STD-KEYSTONE-022: Work step은 Goal unit이다

작업서 step은 assignable Goal unit으로 작성해야 한다. 필수 필드는 다음과 같다.

1. `Goal`
2. `Scope`
3. `Source Context`
4. `Completion Criteria`
5. `Stop Conditions`
6. `Verification`
7. `Expected Output`

`Suggested Role`은 선택 사항이며 delegation 가능성이 클 때 권장한다.

<!-- key: id=key.standard.project.std-keystone-023 refs=key.doc.source key.topic.document-system -->
### STD-KEYSTONE-023: Impact update는 문서 일관성을 보존한다

1. 원천 문서(2) 변경이 관련 parent, child, work, progress, 결정(6), 파생 에이전트
   문서(8)에 명확히 영향을 주면 함께 검토한다.
2. 원천 문서(2) 변경이 capability(16), code, config, schema, API, test artifact에 영향을 줄 수
   있으면 code/config/schema/API/test impact candidate로 보고한다.
3. Code 또는 test 변경이 기준서(3), 작업서(4), 결정(6)에 영향을 줄 수 있으면 document impact
   candidate로 보고한다.
4. 영향 범위나 의미 변경이 불확실하면 수정 전에 멈추고 추가 조사를 한다. 실제 User
   Decision이 필요한 경우에만 사용자에게 묻는다.
5. 진행 기록(5)은 completion evidence 없이 `work_status: complete`로 바꾸지 않고 Main acceptance
   없이 `approval.state: accepted`로 바꾸지 않는다.

<!-- key: id=key.standard.project.std-keystone-024 refs=key.topic.document-system key.topic.skill-contract key.role.subagent -->
### STD-KEYSTONE-024: 진행 상태(progress status)와 report status는 별개다

Work execution status는 workflow state이고, subagent report status는 report outcome이다.

`work_status` 값은 다음과 같다.

1. `planned`
2. `in_progress`
3. `blocked`
4. `complete`
5. `cancelled`
6. `superseded`

`ready`, `assigned`, `reported`, `reviewing`, `verifying`처럼 세부 실행 phase가 필요하면 별도
workflow substate로 기록하며 `work_status` vocabulary에 섞지 않는다. `accepted`는 오직
`approval.state`에 사용한다.

Subagent report status 값과 의미는 `standards/subagents/key-standard-subagents.md`를 따른다.

문서 작성/수정도 작업 복구에 의미 있는 문서 단위 변화라면 진행 기록(5)에 남긴다. 단순
오탈자, 미세 표현 수정, 의미 변화 없는 formatting은 남기지 않는다.

<!-- key: id=key.standard.project.std-keystone-025 refs=key.topic.skill-contract key.topic.document-system -->
### STD-KEYSTONE-025: Verification은 기준서가 이끈다

1. 기준서가 primary verification expectation을 정의한다.
2. Main은 기준서에서 관련 verification criteria를 추출해 checklist로 만든다.
3. 작업서는 local verification note를 추가할 수 있지만 기준서 verification을 약화하지
   않는다.
4. 아티팩트 그래프(14)가 관련되면 duplicate ID, unresolved relation, stale locator 같은 graph
   validation을 verification 후보로 포함한다.
5. 필요하면 verifier subagent에게 별도 verification Goal을 배정한다.

<!-- key: id=key.standard.project.std-keystone-026 refs=key.topic.document-system key.doc.work key.topic.work-round -->
### STD-KEYSTONE-026: 작업서는 round 단위로 묶는다

작업서(4)는 기준서(3)와 달리 하나의 영구 통합 문서가 아니라 특정 시점의 기준서와 목표를
바탕으로 실행되는 작업 round(13)에 속한다.

1. `works/00_key-index.md`는 전체 작업 round(13) 목록과 active round를 관리한다.
2. 각 작업 round(13)는 `works/r{number}-{slug}/` 아래에 둔다.
3. `r`은 round를 뜻하며, version이나 revision 번호가 아니라 작업 차수 번호다.
4. 각 작업 round(13)는 자기 `00_key-index.md`를 가지고, round 안의 실행 순서를 `S01`부터
   다시 시작한다.
5. Work node는 작업 round(13) 안에 두며, 기본적으로 `00_key-index.md`,
   `key-work-{slug}.md`, `key-progress.md`를 가진다.
6. 여러 round에 영향을 주는 결정(6)은 `works/key-decisions.md`에 둔다.
7. 특정 round 안에서만 유효한 결정(6)은 해당 round의 `key-decisions.md` 또는 관련 work node의
   `key-decisions.md`에 둔다.
8. 기준서 tree와 작업 round tree는 1:1로 맞추지 않는다. 기준서는 반복 기준이고, 작업 round는
   특정 시점의 실행 기록이다.
9. Round 안의 step 순서는 기본 실행 순서이며 자동 acceptance gate가 아니다.
10. 특정 step이 이전 step의 accepted 상태 이후에만 시작되어야 하면 해당 작업서(4)의
    Sequencing / Dependency, Stop Conditions, 또는 Completion Criteria에 명시한다.
11. 의존성이 명시되지 않은 step은 main/user 판단에 따라 병행 검토하거나 선반영할 수 있다.
12. Author는 step dependency나 acceptance gate를 임의로 만들지 않고, main/user 또는 Clarify가
    수락한 의존성 결정을 작업서에 반영한다.

<!-- key: id=key.standard.project.std-keystone-027 refs=key.doc.work key.topic.work-round key.topic.artifact-graph key.topic.impact-review key.topic.verification key.topic.acceptance -->
### STD-KEYSTONE-027: Change Set은 artifact 변경과 impact propagation을 묶는다

Change Set(17)은 하나의 사람 의도, 결정(6), 또는 work step이 문서, capability(16), code,
config, schema, API, test artifact에 미치는 영향을 한 변경 단위로 묶는다.

1. Change Set(17)은 큰 변경이나 문서-code/config/schema/API/test 동시 영향이 있는 변경에 사용한다.
2. Change Set(17)은 `intent`, `changed_nodes`, `impact_seeds`, `required_candidates`,
   `optional_candidates`, `excluded`, `verification`, `acceptance`를 포함할 수 있다.
3. `changed_nodes`는 실제로 바뀐 artifact node(15)다.
4. `impact_seeds`는 traversal을 시작할 capability(16), API, standard, decision, code, test
   artifact다.
5. `required_candidates`는 직접 typed relation이나 강한 evidence로 반드시 검토할 대상이다.
6. `optional_candidates`는 scope와 risk에 따라 검토할 대상이다.
7. `excluded`는 현재 scope에서 수정하지 않을 artifact나 topic이다.
8. 문서에서 시작한 변경은 capability(16), API, code, test를 후보로 찾는다.
9. Code에서 시작한 변경은 capability(16), API, test, 기준서(3), 결정(6)을 후보로 찾는다.
10. Test에서 시작한 변경은 capability(16), API, code, acceptance criteria를 후보로 찾는다.
11. Candidate 발견은 수정 허가가 아니다. Main이 scope, authority, verification을 기준으로
    직접 처리하거나, 사용자 허락이 있으면 Coordinator가 후속 workflow를 조율한다.
12. Final acceptance 전에는 Change Set(17)의 acceptance 상태를 accepted로 보지 않는다.

<!-- key: id=key.standard.project.std-keystone-030 refs=key.topic.skill-contract key.topic.formal-workflow key.topic.acceptance -->
### STD-KEYSTONE-030: Main은 최종 조율과 수락 책임을 가진다

Main은 Keystone 작업의 최종 판단 지점이다. 스킬의 책임과 실제 실행자 역할은 분리한다.

1. Main은 원천 문서(2)를 읽고, 작업 방향을 판단하고, 사용자와 필요한 결정(6)을 정리한다.
2. Reader, Clarify, Author, Coordinator의 output은 Main의 판단을 돕는 입력이며 원천 문서(2)를
   대체하지 않는다.
3. Main은 작업을 스킬이나 bounded helper/subagent에게 맡길 수 있지만, 맡기기 전에 goal,
   context, 범위, 중단 조건을 분명히 해야 한다.
4. 맡겨진 역할은 받은 범위 밖으로 작업을 넓히거나 전체 작업서(4)를 재해석하지 않는다.
5. Report, review, verification, acceptance가 이어지는 formal workflow를 위임하고 사용자가
   허락하면 Coordinator가 조율한다.
6. 작업 결과의 최종 수락은 Main이 한다. `STD-KEYSTONE-007`의 User Decision이 필요한
   경우에만 사용자 판단을 먼저 받는다.

<!-- key: id=key.standard.project.std-keystone-031 refs=key.topic.skill-contract -->
### STD-KEYSTONE-031: Main agent는 supervisor다

Main agent는 context를 보존하고 supervisor로 동작해야 한다.

1. Goal을 복구한다.
2. 필요한 문서만 읽는다.
3. Assignment를 준비한다.
4. 필요한 경우 Coordinator를 통해 bounded worker에게 작업을 routing한다.
5. Report나 작업 결과를 받는다.
6. Repair를 결정한다.
7. Final acceptance decision을 내린다.

<!-- key: id=key.standard.project.std-keystone-032 refs=key.topic.skill-contract key.topic.formal-workflow key.role.subagent key.standard.subagent -->
### STD-KEYSTONE-032: 위임된 실행자는 bounded worker assignment로 제한한다

Main은 작고 명확한 작업을 직접 수행할 수 있다. Helper 또는 subagent에게 위임할 때는
bounded worker assignment(19)를 사용한다. Purpose preset, authority, injected skill contract,
report status, 공통 금지는 `standards/subagents/key-standard-subagents.md`를 따른다.

1. Main, Author, Coordinator는 ad hoc runtime role을 만들지 않는다.
2. Role은 worker 종류가 아니라 assignment의 purpose hint다.
3. 실제 경계는 authority, scope, forbidden changes, injected skill contract, stop condition,
   report contract가 정한다.
4. 필요한 purpose preset이나 authority가 기준서에 없으면 subagent 기준서를 먼저 수정하거나
   main/user 결정(6)을 받는다.
5. 모든 helper/subagent/worker는 받은 Goal 밖으로 scope를 넓히거나 추가 subagent를 생성하지
   않는다.
6. Worker output은 원천 문서(2), 기준서(3), 작업서(4), Main acceptance를 대체하지 않는다.

<!-- key: id=key.standard.project.std-keystone-033 refs=key.topic.document-system key.topic.skill-contract -->
### STD-KEYSTONE-033: 작업서는 Coordinator가 바로 실행 계획을 세울 수 있게 쓴다

작업서(4)의 각 step은 Coordinator가 바로 실행 계획으로 바꿀 수 있을 만큼 분명해야 한다.
즉 작업서를 읽으면 다음 질문에 답할 수 있어야 한다.

1. 지금 해야 하는 일은 무엇인가?
2. 그 일을 하려면 어떤 기준서와 작업서를 읽어야 하는가?
3. 작업자에게 맡긴다면 어디까지 맡길 수 있고, 어디부터는 맡기면 안 되는가?
4. 검토자는 무엇을 중점적으로 확인해야 하는가?
5. 어떤 상황이 오면 작업을 멈추고 main이나 사용자에게 물어야 하는가?
6. 완료 후 무엇으로 제대로 끝났는지 확인할 수 있는가?

<!-- key: id=key.standard.project.std-keystone-040 refs=key.topic.skill-contract key.doc.source key.role.reader key.boundary.read-only -->
### STD-KEYSTONE-040: Reader는 read-only context brief preparation을 담당한다

`keystone-reader`는 read-only로 원천 문서(2)를 읽어 project orientation, document navigation,
work preparation, context brief 생성을 지원한다. Reader는 아티팩트 그래프(14)가 필요한지를
판단할 수 있지만, 깊은 artifact impact/stale/gap 해석은 `keystone-linker`로 넘긴다. Reader는
원천 문서(2), code, config, 진행 기록(5), 결정(6)을 수정하지 않는다.

Reader의 mode, workflow, output field, stop condition의 상세 계약은
`skills/reader/key-standard-reader.md`를 따른다.

초기화 전에는 Main이 일반 repository 조사 능력으로 code, README와 설정을 읽는다. 이 조사를
Reader의 선행 책임이나 Keystone 전용 절차로 강제하지 않는다. Keystone 문서가 존재할 때
Reader가 그 문서를 바탕으로 더 나은 navigation과 work recovery를 제공한다.

<!-- key: id=key.standard.project.std-keystone-041 refs=key.topic.skill-contract key.doc.source key.topic.user-decision -->
### STD-KEYSTONE-041: Clarify는 실제 User Decision을 한 topic씩 다룬다

`keystone-clarify`는 topic-scoped high-impact 결정(6)을 수집하고, 수락된 decision summary와
edit plan을 바탕으로 `keystone-author`가 관련 원천 문서(2)를 업데이트할 수 있게 준비한다.
상세 계약은 `skills/clarify/key-standard-clarify.md`를 따른다.

1. 안전한 기본값, 명시된 우선순위, repository evidence로 정할 수 있는 사항은 질문하지 않는다.
2. 질문이 필요하면 한 번에 하나의 실제 결정 topic만 다룬다.
3. 결정이 충분하면 호출자에게 결과를 반환하고 중단한 Init 또는 Author 흐름을 resume한다.
4. 특정 호스트의 내부 실행 mode나 질문 UI를 Clarify 계약으로 만들지 않는다.

<!-- key: id=key.standard.project.std-keystone-042 refs=key.topic.skill-contract key.doc.source -->
### STD-KEYSTONE-042: Author는 승인된 원천 문서(2) 작성을 담당한다

`keystone-author`는 수락된 요청과 결정(6)을 바탕으로 기준서(3), 작업서(4), 진행 기록(5),
결정(6) 기록, Change Set(17)을 만들거나 수정한다. 문서 수정 기준, 승인 범위, 영향 문서,
키메타/index/progress 반영 범위는 Author가 소유한다. code/config/schema/API/test impact candidate의
깊은 탐색은 `keystone-linker` report를 입력으로 사용한다. 상세 계약은
`skills/author/key-standard-author.md`를 따른다.

1. Creation: 새 기준서, 작업서, 진행 기록, 결정 기록, index를 만든다.
2. Revision: 승인된 범위 안에서 기존 원천 문서(2)를 수정한다.
3. Clarify result 적용: 수락된 decision summary와 edit plan을 관련 원천 문서에 반영한다.
4. Author Edit Contract: 큰 문서 수정은 대상, 범위, 영향 문서, 검증 기준을 먼저 정리한다.
5. Bounded doc helper: 승인 범위가 명확하면 `investigate` 또는 `document_edit` worker 도움을
   받을 수 있으며, purpose preset과 authority는 subagent 기준서를 따른다. 실행 isolation과
   concurrency 전략은 사용자 지시, 주입된 skill, host 환경에 맡긴다.
6. Change Set: 큰 문서 변경, code/config/schema/API/test 영향이 있는 문서 변경, 여러 artifact에 걸친 변경은
   추적 가능한 Change Set(17)으로 정리한다.
7. Impact candidates: 문서 변경이 capability(16), code, config, schema, API, test artifact에 영향을 줄 수
   있으면 Linker report나 impact seed로 남긴다. 실제 code 수정은 Main direct로 처리하거나
   위임 허락이 있으면 Coordinator로 넘긴다.
8. Progress update: main acceptance 전에는 accepted 또는 complete로 표시하지 않는다.
9. Initialization: `uninitialized` 또는 `partial`이면 Init handoff 후 원래 Author 요청으로
   resume한다.

<!-- key: id=key.standard.project.std-keystone-043 refs=key.topic.skill-contract key.contract.output key.contract.report key.role.coordinator -->
### STD-KEYSTONE-043: Coordinator는 bounded worker assignment broker다

`keystone-coordinator`는 작업서(4)의 Goal unit, Reader context brief, Linker report,
Author가 작성한 Change Set(17)을 바탕으로 worker assignment(19)를 만들고, worker report(20)를
Keystone workflow로 회수하는 bounded assignment broker다. 코드 작업은 대표적인 실행 작업이지만,
Coordinator는 코딩 방법론 자체를 독점하지 않는다. 외부 코딩 스킬(12)은 Coordinator를
대체하지 않고 injected skill contract로 주입한다. 상세 계약은
`skills/coordinator/key-standard-coordinator.md`를 따른다.

1. Assignment: Current Step Brief, Context Pack, handoff boundary, reviewer focus를 준비한다.
2. Worker assignment: bounded worker가 수행할 goal, intent, artifact context, allowed scope,
   forbidden changes, injected skill contract, verification, return report contract를 만든다.
3. Purpose routing: 목적에 맞는 purpose preset, authority, injected skill contract를 고른다.
4. Worker report handling: report status를 progress status와 분리해 처리한다.
5. Review/verification: Linker report, worker report, 기준서-led verification을 기준으로
   review와 verification을 조율한다.
6. Permission: work scope마다 사용자 허락을 받는다. 직접 Coordinator 호출은 해당 요청 범위의
   허락이며, 같은 범위의 assignment/review/repair에서 반복하지 않는다.
7. Execution strategy: worktree, branch, workspace, concurrency는 Keystone이 강제하지 않는다.
   주입된 skill이나 host가 자기 계약으로 선택할 수 있다.
8. Acceptance: main acceptance 조건을 만족한 뒤에만 진행 기록(5)을 accepted로 바꿀 수 있다.

<!-- key: id=key.standard.project.std-keystone-044 refs=key.topic.skill-contract key.topic.artifact-graph key.role.linker -->
### STD-KEYSTONE-044: Linker는 artifact relation과 impact/stale/gap 후보를 해석한다

`keystone-linker`는 Artifact Graph의 canonical mutation decision owner다. Linker는 source를 read-only로
원천 문서(2), 결정(6), 작업서(4), 키메타(9), 코드 앵커(18), repository evidence를 함께 사용해
문서가 만들거나 통제하는 output artifact와 그 영향 후보를 탐색한다. Output artifact는
skill source, code, config, schema, API, test, generated file, 문서 산출물 같은 surface를 가질
수 있지만, Linker의 1차 관심사는 `문서/결정/작업서 -> 산출물` 관계다. Linker는 artifact
graph의 해석·후보 보고와 exact canonical mutation 결정을 소유하지만 원천 문서(2)나 산출물을
직접 수정하지 않는다. Surface owner attestation과 baseline 검증 없이는 mutation을 적용하거나
`verified`로 판정하지 않는다.

1. Artifact discovery: 현재 요청과 관련된 capability와 output artifact 후보를 찾는다.
2. Impact analysis: 문서, 결정(6), 작업서(4), output artifact diff가 다른 artifact에 줄 영향
   후보를 등급화한다.
3. Stale/gap review: locator, relation, metadata gap, semantic mismatch 후보를 보고한다.
4. Worker assignment seed: Coordinator가 worker assignment(19)를 만들 수 있게 artifact context와
   reuse/test/stale/gap 후보를 정리한다.
5. Handoff: 문서 metadata 수정은 Author에게, output artifact 수정은 Main direct 또는 사용자
   허락을 받은 Coordinator로 넘긴다.
6. Invocation: Linker는 source-write authority가 없으므로 Main이 필요하다고 판단하면 별도 사용자 승인 없이
   사용할 수 있다. Graph evidence가 적으면 확인 가능한 범위와 gap을 fail-soft로 보고한다.

<!-- key: id=key.standard.project.std-keystone-045 refs=key.topic.skill-contract key.contract.output key.topic.external-assist -->
### STD-KEYSTONE-045: 사용자 응답과 structured payload는 분리한다

Keystone skill output은 사람이 읽는 기본 응답과 agent-facing structured payload를 구분한다.

1. 기본 사용자 응답은 결론, 핵심 근거, 주요 risk, 다음 행동, 주요 출처를 짧게 보여준다.
2. `reader_output`, `clarify_result`, `author_patch_report`, `linker_report`,
   `worker_assignment`, `worker_report`, `worker_report_review`, `keystone_routing_decision`,
   `main_direct_change_report` 같은 structured payload는 handoff, audit, debugging,
   verification evidence를 위한 agent-facing contract다.
3. Structured payload는 사용자가 요청했거나, 다른 Keystone skill 또는 Main이 handoff input으로
   필요로 하거나, audit/debug 목적으로 필요할 때만 전체를 노출한다.
4. Payload Disclosure Gate: 기본 사용자 응답을 만들기 전에 다음 질문을 확인한다.
   - 사용자가 full payload를 명시적으로 요청했는가?
   - handoff, audit, debugging, verification evidence에 원문 payload가 실제로 필요한가?
   - 원문 payload가 필요하다면 그 이유를 사용자 응답 또는 handoff context에 짧게 밝혔는가?
   - 위 조건이 아니면 `*_output`, `*_result`, `*_report`, `worker_assignment`,
     `keystone_routing_decision` 원문을 fenced block이나 YAML block으로 노출하지 않았는가?
5. 기본 사용자 응답은 structured payload의 semantic content에서 파생되어야 하며, 별도 판단으로
   risk, recommended next action, source authority, acceptance status를 바꾸지 않는다.
6. 사용자 응답이 후보나 risk를 줄여 보여줄 때는 required item을 조용히 제거하지 않고 요약
   count, 대표 항목, full payload availability를 남긴다.
7. 기본 사용자 응답은 structured payload 원문 대신 변경 또는 판단 요약, 대상 파일이나 후보 수,
   검증 결과 요약, 남은 risk, 다음 행동, 주요 출처를 보여준다. Full payload는 요청 시 제공할 수
   있음을 필요한 경우 한 문장으로만 남긴다.
8. Optional presentation/helper skill인 `keystone-viewer`는 structured payload를 audience와
   detail level에 맞게 렌더링할 수 있지만 core runtime dependency가 아니며, 의미 판단,
   source authority, handoff payload, acceptance status를 바꾸지 않는다.
9. `keystone-viewer` 또는 동등한 presentation layer는 필요할 때만 사용한다. 모든 Keystone
   output이 반드시 viewer를 통과해야 하는 mandatory filter chain으로 만들지 않는다.

<!-- key: id=key.standard.project.std-keystone-046 refs=key.topic.skill-contract key.topic.work-execution key.topic.skill-source key.contract.report -->
### STD-KEYSTONE-046: Routing은 필요한 경계에서만 명시적으로 기록한다

Main은 요청의 target surface와 적절한 실행 주체를 판단하지만, 모든 작은 변경에 별도 routing
문서나 사용자 질문을 요구하지 않는다.

1. `source_document`: `00_docs/**` 원천 문서는 Author가 담당한다.
2. `skill_source`: `skills/keystone-*/SKILL.md`는 이번 저장소의 구현 산출물이며 작은 변경은
   Main direct로 처리할 수 있다.
3. `repository_source`: code, config, schema, API, test, generated/codegen source는 작은 범위가
   명확하면 Main direct로 처리할 수 있다.
4. `mixed`: 복수 surface나 권한 경계가 있으면 phase를 분리하거나 routing을 명시적으로 기록한다.
5. High-impact 프로젝트 결정이 필요하면 Clarify, graph 해석이 필요하면 Linker를 사용한다.
6. Coordinator는 위임, 여러 작업자, formal review/verification처럼 coordination이 실제로
   필요하고 사용자가 해당 work scope를 허락한 경우에만 사용한다.
7. 명시적인 사용자 요청으로 lane과 scope가 충분히 정해졌으면 routing 자체를 Clarify topic이나
   추가 승인 질문으로 만들지 않는다.
8. `keystone_routing_decision`, `main_direct_change_report`, lane별 report는 handoff, audit,
   debugging, verification에 실제 필요할 때만 내부 structured payload로 남긴다.
9. Structured payload를 남겨도 `STD-KEYSTONE-045`에 따라 기본 사용자 응답에는 원문을 노출하지
   않고 선택한 주체, 범위, 검증과 residual risk만 요약한다.
10. 특정 skill 기준서를 읽은 것만으로 해당 skill을 실행했다고 보지 않는다.

<!-- key: id=key.standard.project.std-keystone-050 refs=key.topic.document-system key.doc.source key.topic.initialization -->
### STD-KEYSTONE-050: Init은 config와 R000으로 프로젝트 기반을 만든다

이 규칙은 완성된 Keystone 스킬을 사용하는 target project에서의 동작을 설명한다. 이 구현
저장소는 fixture 또는 test step이 명시적으로 요구하지 않는 한 `.keystone/config.yaml`이
필요하지 않다.

Target project에서 Init은 다음을 다룬다.

1. document root
2. 기준서(3)와 작업서(4) tracking policy
3. 파생 에이전트 문서(8) tracking policy
4. Keystone output language policy
5. setup storage location
6. R000 Project Foundation과 원래 요청의 resume context

기본 shared config 예시는 다음과 같다.

```yaml
version: 1
document_root: 00_docs
source_docs_tracking_policy: track_standards_and_works
derived_agent_docs_tracking_policy: ignore
output_language_policy: dominant_conversation_language
```

Init은 고정 scaffold와 R000 template까지만 직접 만들고, 프로젝트 의미를 담은 기준서는
Author가 작성한다. 상태 탐지, write authority와 `ready` 판정은
`standards/bootstrap/key-standard-bootstrap.md`와
`standards/skills/init/key-standard-init.md`를 따른다.

<!-- key: id=key.standard.project.std-keystone-051 refs=key.doc.source key.topic.document-system -->
### STD-KEYSTONE-051: 원천 문서(2) tracking policy는 명시적이다

Target project는 기준서, 작업서, Context Map과 결정 기록의 tracking policy를 명시한다.
Keystone의 기본 정책은 작업 복구에 필요한 공유 원천 문서를 함께 추적하는 것이다.

1. 파생 에이전트 문서(8)는 명시 필요 전까지 source tracking 대상에 포함하지 않는다.
2. `.keystone/config.yaml`은 shared project policy이며 기본적으로 source tracking 대상이다.
3. `.keystone/config.local.yaml`은 local/private override이며 기본적으로 source tracking 대상에
   포함하지 않는다.
4. 민감한 내용은 쓰기, track, publish, derive 전에 사용자 확인이 필요하다.
5. 프로젝트 정책이 기본 tracking을 바꾸더라도 기준서와 현재 작업을 복구할 권위 위치는
   명확해야 한다.

<!-- key: id=key.standard.project.std-keystone-052 refs=key.topic.document-system -->
### STD-KEYSTONE-052: Output language policy는 Keystone artifact에만 적용한다

1. Target project는 Keystone output language policy를 project setting으로 선택한다.
2. 이 구현 저장소의 원천 문서(2) 작성과 검토는 한국어를 기본으로 한다.
3. 파일 경로, 설정 key, schema value, status value, skill name, step ID, decision ID,
   standard ID처럼 기계적으로 참조되는 literal은 영어 또는 기존 값을 유지한다.
4. Output language policy는 관련 없는 task, code comment, change summary, README,
   external tool, non-Keystone skill에는 적용하지 않는다.

<!-- key: id=key.standard.project.std-keystone-053 refs=key.topic.skill-contract -->
### STD-KEYSTONE-053: Skill source는 저장소에서 구현한다

이 저장소는 여섯 개 Keystone 스킬 계약의 개발 원천이다.

1. Reader skill: `skills/keystone-reader`
2. Author skill: `skills/keystone-author`
3. Clarify skill: `skills/keystone-clarify`
4. Linker skill: `skills/keystone-linker`
5. Coordinator skill: `skills/keystone-coordinator`
6. Init skill: 후속 R002 구현에서 `skills/keystone-init`으로 추가한다.

현재 다섯 skill source는 R001 산출 이력이며 R002 runtime independence 계약과 일치하도록 후속
구현해야 한다. 이번 기준서 개편에서는 `skills/**`를 수정하지 않는다. 초기 배포 형태는
repo-local skill source이며, publish/install은 별도 요청이 있을 때만 다룬다.

<!-- key: id=key.standard.project.expected-behavior refs=key.doc.source key.topic.document-system key.topic.skill-contract key.topic.bootstrap -->
## 기대 동작

1. Project initialization
   - Init은 새 프로젝트에 R000과 고정 scaffold를 만들고 Author가 프로젝트 기준서를 작성할
     수 있게 한다.
   - 초기화 전 repository 조사는 Main의 일반 능력에 맡기며 Reader를 선행 조건으로 요구하지
     않는다.
2. Project orientation
   - Main agent는 `key-context-map.md`를 확인해 active standards와 active work를 찾는다.
   - 현재 active work round는 `00_docs/works/00_key-index.md`에서 찾고, round 내부 실행
     순서는 해당 round의 `00_key-index.md`에서 찾는다.
3. Document reading
   - Reader는 관련 기준서와 작업서만 읽고, 관련 없는 하위 기준서를 불러오지 않으며, 필요한
     context brief를 만든다.
4. Document authoring
   - Author는 승인된 범위 안에서 원천 문서(2)와 Change Set(17)을 작성하거나 수정한다.
5. Clarification
   - Clarify는 high-impact decision topic을 하나씩 정리하고 Author 적용 계획을 만든다.
6. Artifact linking
   - Linker는 문서, capability(16), code, config, schema, API, test artifact의 영향 후보,
     stale 후보, metadata gap 후보를 read-only로 보고한다.
7. Work execution
   - Coordinator는 작업서 step과 Linker report를 worker assignment(19)로 만들고 worker
     report(20)를 Keystone workflow로 회수한다. Work scope별 사용자 허락이 있을 때만
     Coordinator를 사용한다.
8. Supporting workflow
   - 외부 보조 스킬(12)은 명시적 supporting workflow로만 사용할 수 있다.
   - Optional `keystone-viewer` 같은 presentation/helper skill은 structured payload를
     사용자-facing view로 렌더링할 수 있지만 core skill의 의미 판단이나 handoff contract를
     대체하지 않는다.
9. Bootstrap verification
   - 현재 Keystone 원천 문서(2)는 부트스트랩 기준 corpus(10)로 사용되며, R002 Skill Runtime
     Implementation과 아홉 통합 시나리오에서 구현된 스킬이 같은 문서 모델을 재생산하거나
     유지할 수 있는지 검증한다.

<!-- key: id=key.standard.project.forbidden-without-approval refs=key.doc.source key.topic.document-system key.topic.skill-contract -->
## User Decision 없이 금지되는 변경

1. Keystone 스킬 시스템 goal의 의미 변경
2. 여섯 개 Keystone 스킬 계약을 사용자 결정 없이 합치기
3. Prototype skill을 최종 runtime dependency로 취급하기
4. 완료되지 않은 high-impact clarification topic을 근거로 원천 문서(2) 수정하기
5. 위임 범위 밖에서 document root, active work round, active work tree 변경하기
6. common/global instruction file에 Keystone setup result 쓰기
7. 민감한 원천 문서(2)를 승인 없이 track, publish, derive하기
8. Keystone output language가 관련 없는 작업을 override하게 하기
9. 사용자 허락 없이 Coordinator나 위임용 외부 보조 스킬(12)을 호출하기
10. 파생 에이전트 문서(8)를 원천 문서로 취급하기
11. Main acceptance 전에 work를 accepted 또는 complete로 표시하기
12. 승인 없이 API contract, schema, auth/security, generated/codegen, shared architecture로
    scope 확장하기

<!-- key: id=key.standard.project.escalation-conditions refs=key.doc.source key.topic.document-system key.topic.skill-contract -->
## Escalation 조건

1. 원천 문서(2)가 현재 사용자 방향과 충돌한다.
2. 여섯 스킬 사이 경계가 불명확하다.
3. high-impact clarification topic을 확신 있게 해결할 수 없다.
4. document root, tracking policy, output language policy를 안전하게 추론할 수 없다.
5. work unit을 reviewable output이 있는 명확한 goal로 배정할 수 없다.
6. 문서 변경의 impact 범위가 불명확하다.
7. high-risk implementation이 필요하다.
8. active/실행 가능 Step, completion criteria, applicable standard를 복구할 수 없다.
9. 기존 사용자 또는 다른 agent 변경을 덮어쓸 risk가 있다.
10. verification을 실행할 수 없거나 실패 원인이 불명확하다.

<!-- key: id=key.standard.project.std-keystone-054 refs=key.topic.artifact-graph key.topic.work-sequence key.topic.work-recovery key.topic.verification -->
### STD-KEYSTONE-054: Dependency 의미 관계와 work gate를 분리한다

1. `key.relations.depends_on`은 source artifact/work가 target artifact/work에 의미적으로 의존함을
   나타내는 source -> target typed relation이며 자동 status mutation이나 scheduling 명령이 아니다.
2. `work_gates`는 dependency target의 조건이 source의 어느 step 또는 work completion에
   적용되는지 표현하는 execution contract다.
3. Project가 별도 accepted exception을 정의하지 않으면 required gate는 target의
   `work_status: complete`와 `approval.state: accepted`를 모두 요구한다.
4. Legacy work-level `depends_on`에 명시적 gate가 없으면 source 시작을 차단하지 않고
   work completion gate 후보로 해석한다.
5. Dependency 판정은 `satisfied`, `waiting`, `unresolvable`, `invalid`, `unknown`을 사용하고
   lifecycle, approval, work status와 분리한다.
6. Structured metadata과 legacy HTML이 함께 있으면 structured metadata를 우선하고 충돌을 보고한다.
7. Missing target, duplicate, self-reference, invalid step은 `invalid` 또는 `unresolvable`로 분리하고
   dependency만으로 work status를 바꾸거나 worker를 자동 할당·취소하지 않는다.
8. Step gate cycle은 work node만이 아니라 source/target step과 completion event를 펼친
   expanded event graph에서 판정해 false cycle을 피한다.
9. 상세 schema, cancelled/superseded target과 compatibility 판정은 Artifact Graph 기준서를 따른다.

<!-- key: id=key.standard.project.std-keystone-055 refs=key.topic.acceptance key.topic.progress-update key.topic.verification key.topic.work-recovery -->
### STD-KEYSTONE-055: Acceptance finalization은 기존 상태 체계를 보강한다

1. 실행 완료는 `work_status: complete`, Main acceptance는 `approval.state: accepted`로 서로
   독립적으로 기록한다. `accepted`를 work execution status로 사용하지 않는다.
2. Finalization은 새 progress/work/lifecycle/approval 상태가 아니라 기존 Progress 또는 Change Set의
   `finalization.state: pending | in_progress | complete | waived` 하위 상태다.
3. 현재 Step 수용 후 해당 Step과 상태를 집계·노출하는 Work, Round, root index, Context Map을
   평가한다. 상위 소유자는 자체 완료 조건을 충족할 때만 상태를 전이한다.
4. 형제·미래 Step은 선작업이 있어도 상태를 바꾸지 않고 `early_work`만 기록한다.
5. `active_steps`는 0개 이상의 동등한 Step 참조를 허용하며 상태를 복제하지 않는다.
6. Author는 기존 Impact, Change Set과 Linker evidence로 영향 후보를 계산하고 각 후보에
   `updated`, `no_change`, `historical`, `out_of_scope`, `clarification_required`,
   `integration_gate` disposition과 근거를 남긴다.
7. Required finalization이 complete가 아니면 동일 work의 다음 implement 상태 전이를 차단하지만
   다른 work와 read-only 조사에는 자동 확장하지 않는다.
8. Validator는 Author package의 bundled diagnostic script이며 기계적 정합성만 검사한다.
   문서 수정, 의미 판단, acceptance와 finalization 완료 전이를 수행하지 않는다.

<!-- key: id=key.standard.project.std-keystone-056 refs=key.topic.artifact-graph key.topic.finalization key.topic.verification key.role.linker key.role.author key.role.coordinator -->
### STD-KEYSTONE-056: Graph synchronization은 acceptance finalization을 additive하게 확장한다

1. 단일 source surface 안에서 끝나는 ID/ref 또는 metadata 변경은 해당 surface owner가 직접
   갱신하고 Linker가 파생 index를 refresh한다. 둘 이상의 source surface를 함께 정합화해야
   할 때만 현재 Progress 또는 Change Set에 `graph_sync.required: true`와 disposition을 기록하고
   synchronization transaction을 시작한다.
2. Disposition은 최소 `required | not_applicable | deferred`를 사용한다. `not_applicable`과
   `deferred`에는 근거가 필요하며 required transaction은 `verified` evidence가 있어야
   finalization을 `complete`로 만들 수 있다.
3. Verified evidence는 transaction ID, attestation 결과, baseline digest 확인, 모든 required
   surface apply 결과, Linker reconstruction 결과와 mechanical validator 결과를 가리킨다.
4. Required graph sync가 미완료여도 이미 이루어진 Main acceptance를 취소하거나 기존 work
   status를 되돌리지 않는다. 다만 동일 acceptance의 finalization `complete` 전이는 차단한다.
5. 이 확장은 R004의 accepted 문서·진행 기록을 소급 수정하지 않고 이후 finalization runtime에
   additive하게 적용한다.

<!-- key: id=key.standard.project.std-keystone-057 refs=key.topic.artifact-graph key.topic.keystone-metadata key.topic.work-recovery -->
### STD-KEYSTONE-057: Source-owned owner/ref index를 기본 탐색 계약으로 사용한다

1. 독립적으로 참조하거나 변경할 의미가 있는 standard, code, config, schema, test artifact는
   stable `key.id`를 정확히 한 source owner에 선언한다. 다른 source는 같은 ID를 소유하지 않고
   `key.refs` 또는 안전한 language anchor의 `refs`로 참조한다.
2. Owner/ref index는 source path와 locator를 모은 재생성 가능한 외부 파생물이며 source of truth,
   acceptance evidence 또는 별도 중앙 registry가 아니다.
3. Typed relation은 multi-hop 탐색, semantic role, dependency, verification evidence 또는 reuse
   분석이 필요한 경우에만 선언한다. 단순 직접 탐색은 owner/ref index로 충족한다.
4. Declared metadata는 source가 소유하고 effective metadata는 document -> section -> item
   순서로 파생한다. `document_lifecycle`, `governed_by`, source authority와 approval은 상속할 수
   있지만 `id`, `supersedes`와 일반 typed relation은 상속하지 않는다. 자식은 부모 authority나
   approval을 확대할 수 없다.

<!-- key: id=key.standard.project.std-keystone-058 refs=key.topic.progress-update key.topic.acceptance key.topic.work-sequence -->
### STD-KEYSTONE-058: 실행, 승인과 dependency 상태 namespace를 분리한다

1. 문서 상태는 `document_lifecycle`, 작업 실행 상태는 `work_status`, 승인은 `approval.state`로
   기록하고 initialization, context readiness, transaction, finalization, verification 상태와
   혼용하지 않는다.
2. 기본 required dependency gate는 target의 `work_status: complete`와
   `approval.state: accepted`를 모두 요구한다. 두 조건 중 하나만 충족하면 `waiting`이다.
3. `cancelled`와 `superseded`는 execution terminal state일 수 있지만 dependency 충족으로
   간주하지 않는다. 별도 accepted exception이 있을 때만 optional/alternative gate로 처리한다.

<!-- key: id=key.standard.project.std-keystone-059 refs=key.role.reader key.role.linker key.topic.work-recovery key.boundary.read-only -->
### STD-KEYSTONE-059: Reader context readiness와 permissionless Linker를 내부 관리 경계로 둔다

1. 사용자가 세션 시작에 Reader를 명시 호출하면 Reader는 document root와 active work를 읽고
   docs discovery scope의 index readiness를 확인한다.
2. Reader는 source read-only다. Source-write authority가 없는 Linker subagent는 별도 사용자나
   Coordinator 허락 없이 scan, external index/cache refresh, graph interpretation과 validation을
   수행할 수 있다. Source 수정, scope 확장, worker 생성, 의미 결정과 acceptance는 금지한다.
3. Repository source scan은 code/artifact context가 실제로 필요한 때 lazy하게 수행한다.
   Cache 실패나 miss는 source 직접 탐색으로 fail-soft fallback하며 사용자 작업을 막지 않는다.
4. Freshness token은 worktree identity, discovery scope의 path set과 각 source raw-byte digest를
   포함한다. Git HEAD, mtime 또는 cache timestamp만으로 fresh를 선언하지 않는다.
5. Reader -> Linker와 Linker -> Reader handoff는 serialized recursion guard를 전달한다. 호출된
   lane은 initiating lane을 다시 호출하지 않는다.

<!-- key: id=key.standard.project.active-work refs=key.topic.document-system key.topic.work-round -->
## 관련 active work

- `00_docs/works/00_key-index.md`
- `00_docs/works/r006-reference-index-context-readiness/00_key-index.md`

<!-- key: id=key.standard.project.child-standards refs=key.topic.skill-contract key.topic.document-system -->
## 관련 child 기준서

- `00_docs/standards/subagents/key-standard-subagents.md`
- `00_docs/standards/bootstrap/key-standard-bootstrap.md`
- `00_docs/standards/skills/reader/key-standard-reader.md`
- `00_docs/standards/skills/author/key-standard-author.md`
- `00_docs/standards/skills/clarify/key-standard-clarify.md`
- `00_docs/standards/skills/linker/key-standard-linker.md`
- `00_docs/standards/skills/coordinator/key-standard-coordinator.md`
- `00_docs/standards/skills/init/key-standard-init.md`
- `00_docs/standards/artifacts/key-standard-artifact-graph.md`
