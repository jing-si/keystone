---
doc_type: standard
key:
  id: key.standard.project
  refs:
    - key.doc.source
    - key.topic.document-system
    - key.topic.artifact-graph
    - key.topic.skill-contract
    - key.topic.key-prefix
    - key.topic.bootstrap
---

# Keystone 프로젝트 기준서

<!-- key: id=key.standard.project.purpose refs=key.doc.source key.topic.skill-contract key.topic.bootstrap -->
## 목적

이 기준서는 Keystone을 문서 기반 project control plane으로 정의하기 위한 프로젝트 공통
규칙을 정의한다. Keystone의 목표는 사람이 수락한 의도와 결정(6), 원천 문서(2),
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
4. `keystone-linker`: Artifact Graph를 read-only로 해석해 문서, capability(16), code, config,
   schema, API, test artifact의 연결과 impact/stale/gap 후보를 보고한다.
5. `keystone-coordinator`: Keystone context를 bounded worker assignment로 만들고 worker
   report를 Keystone workflow로 회수한다.

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
- Coordinator 사용 규칙: Keystone 작업 문맥에서 code/config/schema/API/test 수정 요청이 들어오면
  Coordinator가 기본 routing을 맡고, 명시된 외부 코딩 스킬은 Coordinator를 대체하지 않고
  worker assignment(19)의 injected skill contract로 주입한다.

(13) 작업 round(work round): 특정 시점의 기준서와 목표를 바탕으로 진행하는 작업 차수

- 의미: 기준서 개정, 기능 추가, 기능 변경, 검증처럼 하나의 목적을 가진 작업 묶음이다.
- 사용 규칙: folder는 `r{number}-{slug}` 형식을 사용한다. `r`은 round를 뜻한다. 각 round
  안에서는 작업 step을 `S00`부터 다시 번호 매긴다.

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

(17) Change Set(Change Set): 하나의 사람 의도 또는 결정(6)을 문서, code, test 변경 후보와
검증으로 묶는 변경 단위

- 의미: changed nodes, impact seeds, required/optional candidates, excluded scope,
  verification, acceptance 상태를 함께 담는 구조다.
- 사용 규칙: 큰 변경이나 문서-code-test 동시 영향이 있는 변경은 Change Set으로 조율한다.

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

문서, code, test의 권위는 다음처럼 구분한다.

1. 수락된 기준서(3)와 결정(6)은 intended behavior와 policy의 규범적 권위다.
2. Code와 config는 현재 실행 상태의 operative evidence다.
3. Test와 verification result는 behavior 검증 evidence다.
4. 키메타(9)와 코드 앵커(18)는 navigation and relation evidence이며 문서, code, test의 의미를
   대체하지 않는다.
5. 원천 문서(2), code, test가 충돌하면 어느 한쪽을 조용히 덮어쓰지 않는다.
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
   workspace guard, verification, report contract는 Coordinator assignment가 정한다.
8. 수락 이후에는 Keystone 기준서와 작업서가 최종 권위다.

<!-- key: id=key.standard.project.std-keystone-007 refs=key.doc.source -->
### STD-KEYSTONE-007: 원천 문서(2) 변경에는 명시적 승인이 필요하다

1. 기준서, 작업서, scope, acceptance criteria, progress state를 의미 있게 바꾸는 변경은
   명시적 승인이 필요하다.
2. 승인된 작업 step 안의 직접 관련 수정은 허용된다.
3. 승인된 goal, scope, acceptance criteria, status semantics, source authority를 바꾸는
   변경은 다시 승인이 필요하다.
4. 미승인 관련 변경은 조용히 적용하지 않고 보고한다.

<!-- key: id=key.standard.project.std-keystone-008 refs=key.topic.document-system key.doc.source -->
### STD-KEYSTONE-008: 확장보다 최소 구조가 먼저다

1. `STD-KEYSTONE-010`의 document root resolution과 `STD-KEYSTONE-011`의 tree 규칙을 따른다.
2. 범위 문서(7)는 필요할 때만 추가한다.
3. 결정(6) 기록은 수락된 정책이나 설계 선택을 기록해야 할 때만 추가한다.
4. Coordination 문서는 실제 조율 필요가 생길 때만 추가한다.
5. 파생 에이전트 문서(8)는 `STD-KEYSTONE-016` 조건을 만족할 때만 추가한다.

<!-- key: id=key.standard.project.std-keystone-010 refs=key.topic.document-system key.doc.source -->
### STD-KEYSTONE-010: Document root resolution은 명시적이고 순서가 있다

설정된 document root(1)는 다음 순서로 해석한다.

1. 현재 사용자 지시
2. `.keystone/config.local.yaml`
3. `.keystone/config.yaml`
4. 프로젝트 로컬 agent instruction file 안의 명시적 Keystone settings block
5. 위 설정이 없으면 `00_docs/`

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
   verification, acceptance flow는 `keystone-coordinator`로 routing한다.
8. Keystone 작업 문맥에서 code/config/schema/API/test 수정 요청이 들어오면 명시적 `$coordinator` 호출이
   없어도 `keystone-coordinator`를 기본 execution routing으로 사용한다.
9. 같은 요청에서 외부 코딩 스킬(12)이 명시되면 해당 스킬은 `keystone-coordinator`와 함께
   worker assignment(19)의 injected skill로 사용한다.
10. 외부 코딩 스킬(12)이 명시되지 않으면 Coordinator는 subagent 기준서의
   `keystone-default-bounded-worker` contract를 사용한다.
11. 여러 외부 코딩 스킬 후보가 있고 선택에 따라 workflow, verification, risk가 달라질 때만
   main/user 선택을 요청한다.
12. Legacy uppercase `KEY-` 또는 `_KEY-` 파일은 filename migration 전까지 Keystone-managed
   문서로 읽을 수 있지만, 새 파일과 rename 대상 파일은 lower-case key prefix(11)를 사용한다.
13. key prefix(11)가 없는 일반 프로젝트 문서는 자동으로 Keystone-managed 문서로 판단하지
   않는다.
14. 외부 보조 스킬(12)은 사용자가 호출했거나 수락된 Keystone 기준서 또는 작업서가 명시적으로
   허용한 경우에만 사용한다.

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
10. Artifact Graph의 operational interpretation은 Linker가 소유한다. 이 ownership은 graph
    state와 candidate 판단 권위이며, source document 또는 code/config/schema/API/test source edit
    authority를 포함하지 않는다.

Keystone 작업은 문서 탐색, impact review, context brief, worker assignment, review,
verification을 준비할 때 키메타(9), 코드 앵커(18), repository evidence를 함께 사용한다.

아티팩트 해석 순서는 다음 원칙을 따른다.

1. `key-context-map.md`가 있으면 먼저 읽어 active standards와 active work를 찾는다.
2. 기준서(3)는 최상위 기준서에서 시작해 필요한 child 기준서로 내려간다.
3. 작업서(4)는 최상위 work index에서 시작해 active work round와 active work node 또는
   명시된 work node로 내려간다.
4. Current work node 안에서는 node index, 작업서(4), 진행 기록(5)을 함께 읽어 현재 step과
   실행 범위를 복구한다.
5. 결정(6) 기록, 범위 문서(7), 파생 에이전트 문서(8), 키메타와 코드 앵커로 발견한 후보는 위
   순서를 보강하는 추가 evidence로 읽는다.
6. Capability(16)는 문서와 code를 직접 1:1로 묶기보다 기준서가 govern하고 code가 provide/use
   하며 test가 verify하는 중심 node로 우선 검토한다.
7. Capability, code, config, schema, API, test artifact 후보는 코드 앵커 검색과 실제 repository 검색을
   함께 사용한다.
8. 사용자가 특정 step이나 work를 직접 지정하면 해당 work node를 찾을 수 있지만, 실행 판단은
   적용 가능한 기준서(3)를 함께 읽은 뒤에 한다.
9. `key.topic.current-step`으로 표시된 문맥은 `key.topic.next-step` 같은 후속 참고 문맥보다
   우선한다.
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

<!-- key: id=key.standard.project.std-keystone-020 refs=key.doc.source key.topic.document-system -->
### STD-KEYSTONE-020: 작업은 문서에서 복구 가능해야 한다

사용자가 "run the next step"이라고 말하면 main은 설정된 document root(1)에서 다음 정보를
복구할 수 있어야 한다.

1. active work round
2. 현재 step
3. goal
4. completion criteria
5. applicable standards
6. expected scope
7. risks
8. verification

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
4. 영향 범위나 의미 변경이 불확실하면 수정 전에 멈추고 사용자에게 묻는다.
5. 진행 기록(5)은 main acceptance 없이 accepted 또는 complete로 바꾸지 않는다.

<!-- key: id=key.standard.project.std-keystone-024 refs=key.topic.document-system key.topic.skill-contract key.role.subagent -->
### STD-KEYSTONE-024: 진행 상태(progress status)와 report status는 별개다

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
4. 각 작업 round(13)는 자기 `00_key-index.md`를 가지고, round 안의 실행 순서를 `S00`부터
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

1. Change Set(17)은 큰 변경이나 문서-code-test 동시 영향이 있는 변경에 사용한다.
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
11. Candidate 발견은 수정 허가가 아니다. Coordinator가 scope, authority, workspace guard,
    verification을 기준으로 후속 workflow를 조율한다.
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
5. Report, review, verification, acceptance가 이어지는 formal workflow는 Coordinator가
   조율한다.
6. 작업 결과의 최종 수락은 Main 또는 사용자가 한다.

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
### STD-KEYSTONE-032: 실행자는 bounded worker assignment로 제한한다

Helper 또는 subagent 운영은 속도보다 책임 경계가 우선이다. 실행자는 bounded worker
assignment(19) 안에서만 동작한다. Purpose preset, authority, injected skill contract, report
status, 공통 금지는 `standards/subagents/key-standard-subagents.md`를 따른다.

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

<!-- key: id=key.standard.project.std-keystone-041 refs=key.topic.skill-contract key.doc.source -->
### STD-KEYSTONE-041: Clarify는 topic-scoped이고 mode-aware다

`keystone-clarify`는 topic-scoped high-impact 결정(6)을 수집하고, 수락된 decision summary와
edit plan을 바탕으로 `keystone-author`가 관련 원천 문서(2)를 업데이트할 수 있게 준비한다.
상세 계약은 `skills/clarify/key-standard-clarify.md`를 따른다.

1. Plan Mode: 한 topic에 필요한 질문과 결정(6)을 수집한다.
2. Default Mode: 수락된 decision summary와 edit plan을 Author가 적용할 수 있게 정리한다.
3. 직접 수정 예외: 다른 문서에 영향이 없는 현재 대상 문서의 단순 오탈자만 직접 수정할 수
   있다.

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
   받을 수 있으며, purpose preset과 authority는 subagent 기준서를 따른다. File-writing helper를
   직접 사용할 때는 single workspace guard가 먼저 준비되어야 한다.
6. Change Set: 큰 문서 변경, code/config/schema/API/test 영향이 있는 문서 변경, 여러 artifact에 걸친 변경은
   추적 가능한 Change Set(17)으로 정리한다.
7. Impact candidates: 문서 변경이 capability(16), code, config, schema, API, test artifact에 영향을 줄 수
   있으면 Linker report나 impact seed로 남기고, 실제 code 수정은 Coordinator workflow로
   넘긴다.
8. Progress update: main acceptance 전에는 accepted 또는 complete로 표시하지 않는다.

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
6. Workspace guard: single workspace에서 한 번에 하나의 file-writing worker만 배정한다.
7. Acceptance: main acceptance 조건을 만족한 뒤에만 진행 기록(5)을 accepted로 바꿀 수 있다.

<!-- key: id=key.standard.project.std-keystone-044 refs=key.topic.skill-contract key.topic.artifact-graph key.role.linker -->
### STD-KEYSTONE-044: Linker는 artifact relation과 impact/stale/gap 후보를 해석한다

`keystone-linker`는 Artifact Graph의 operational interpretation owner다. Linker는 read-only로
원천 문서(2), 키메타(9), 코드 앵커(18), repository evidence를 함께 사용해 문서,
capability(16), code, config, schema, API, test artifact의 연결과 영향 후보를 탐색한다.
Linker는 artifact graph의 해석과 후보 보고를 소유하지만 원천 문서(2), code, config, schema,
API, test를 직접 수정하지 않는다.

1. Artifact discovery: 현재 요청과 관련된 capability, code, config, schema, API, test artifact 후보를 찾는다.
2. Impact analysis: 문서, 결정(6), code/config/schema/API/test diff가 다른 artifact에 줄 영향 후보를
   등급화한다.
3. Stale/gap review: locator, relation, metadata gap, semantic mismatch 후보를 보고한다.
4. Worker assignment seed: Coordinator가 worker assignment(19)를 만들 수 있게 artifact context와
   reuse/test/stale/gap 후보를 정리한다.
5. Handoff: 문서 metadata 수정은 Author에게, code/config/schema/API/test metadata 수정이나
   implementation은 Coordinator workflow로 넘긴다.

<!-- key: id=key.standard.project.std-keystone-050 refs=key.topic.document-system key.doc.source -->
### STD-KEYSTONE-050: Initial project setup은 Keystone config에 기록한다

이 규칙은 완성된 Keystone 스킬을 사용하는 target project에서의 동작을 설명한다. 이 구현
저장소는 fixture 또는 test step이 명시적으로 요구하지 않는 한 `.keystone/config.yaml`이
필요하지 않다.

Target project에서 initial setup은 다음을 다룬다.

1. document root
2. 기준서(3)와 작업서(4) tracking policy
3. 파생 에이전트 문서(8) tracking policy
4. Keystone output language policy
5. setup storage location

기본 shared config 예시는 다음과 같다.

```yaml
version: 1
document_root: 00_docs
source_docs_tracking_policy: track_standards_and_works
derived_agent_docs_tracking_policy: ignore
output_language_policy: dominant_conversation_language
```

<!-- key: id=key.standard.project.std-keystone-051 refs=key.doc.source key.topic.document-system -->
### STD-KEYSTONE-051: 원천 문서(2) tracking policy는 명시적이다

Target project의 initial setup에서 Keystone은 다음 선택지를 제공해야 한다.

1. 기준서와 작업서를 모두 track
2. 기준서만 track
3. 둘 다 track하지 않음
4. document change마다 묻기

기본 정책은 다음과 같다.

1. 파생 에이전트 문서(8)는 명시 승인 전까지 source tracking 대상에 포함하지 않는다.
2. `.keystone/config.yaml`은 shared project policy이며 기본적으로 source tracking 대상이다.
3. `.keystone/config.local.yaml`은 local/private override이며 기본적으로 source tracking 대상에
   포함하지 않는다.
4. 민감한 내용은 쓰기, track, publish, derive 전에 사용자 확인이 필요하다.

<!-- key: id=key.standard.project.std-keystone-052 refs=key.topic.document-system -->
### STD-KEYSTONE-052: Output language policy는 Keystone artifact에만 적용한다

1. Target project는 Keystone output language policy를 project setting으로 선택한다.
2. 이 구현 저장소의 원천 문서(2) 작성과 검토는 한국어를 기본으로 한다.
3. 파일 경로, 설정 key, schema value, status value, skill name, step ID, decision ID,
   standard ID처럼 기계적으로 참조되는 literal은 영어 또는 기존 값을 유지한다.
4. Output language policy는 관련 없는 task, code comment, change summary, README,
   external tool, non-Keystone skill에는 적용하지 않는다.

<!-- key: id=key.standard.project.std-keystone-053 refs=key.topic.skill-contract -->
### STD-KEYSTONE-053: Skill source는 저장소에 둔다

이 저장소는 다섯 개 Keystone 스킬의 source of truth다.

1. Reader skill: `skills/keystone-reader`
2. Author skill: `skills/keystone-author`
3. Clarify skill: `skills/keystone-clarify`
4. Linker skill: `skills/keystone-linker`
5. Coordinator skill: `skills/keystone-coordinator`

초기 배포 형태는 repo-local skill source이며, publish/install은 별도 승인이 있을 때만 다룬다.

<!-- key: id=key.standard.project.expected-behavior refs=key.doc.source key.topic.document-system key.topic.skill-contract key.topic.bootstrap -->
## 기대 동작

1. Project orientation
   - Main agent는 `key-context-map.md`를 확인해 active standards와 active work를 찾는다.
   - 현재 active work round는 `00_docs/works/00_key-index.md`에서 찾고, round 내부 실행
     순서는 해당 round의 `00_key-index.md`에서 찾는다.
2. Document reading
   - Reader는 관련 기준서와 작업서만 읽고, 관련 없는 하위 기준서를 불러오지 않으며, 필요한
     context brief를 만든다.
3. Document authoring
   - Author는 승인된 범위 안에서 원천 문서(2)와 Change Set(17)을 작성하거나 수정한다.
4. Clarification
   - Clarify는 high-impact decision topic을 하나씩 정리하고 Author 적용 계획을 만든다.
5. Artifact linking
   - Linker는 문서, capability(16), code, config, schema, API, test artifact의 영향 후보,
     stale 후보, metadata gap 후보를 read-only로 보고한다.
6. Work execution
   - Coordinator는 작업서 step과 Linker report를 worker assignment(19)로 만들고 worker
     report(20)를 Keystone workflow로 회수한다.
7. Supporting workflow
   - 외부 보조 스킬(12)은 명시적 supporting workflow로만 사용할 수 있다.
8. Bootstrap verification
   - 현재 Keystone 원천 문서(2)는 부트스트랩 기준 corpus(10)로 사용되며, 후속 Skill Creation과
     Integration Verification에서 구현된 스킬이 같은 문서 모델을 재생산하거나 유지할 수 있는지
     검증한다.

<!-- key: id=key.standard.project.forbidden-without-approval refs=key.doc.source key.topic.document-system key.topic.skill-contract -->
## 승인 없이 금지되는 변경

1. Keystone 스킬 시스템 goal의 의미 변경
2. 다섯 개 계획된 Keystone 스킬을 승인 없이 합치기
3. Prototype skill을 최종 runtime dependency로 취급하기
4. 완료되지 않은 high-impact clarification topic을 근거로 원천 문서(2) 수정하기
5. 승인 없이 document root, active work round, active work tree 변경하기
6. common/global instruction file에 Keystone setup result 쓰기
7. 민감한 원천 문서(2)를 승인 없이 track, publish, derive하기
8. Keystone output language가 관련 없는 작업을 override하게 하기
9. 외부 보조 스킬(12)을 자동 호출하기
10. 파생 에이전트 문서(8)를 원천 문서로 취급하기
11. Main acceptance 전에 work를 accepted 또는 complete로 표시하기
12. 승인 없이 API contract, schema, auth/security, generated/codegen, shared architecture로
    scope 확장하기

<!-- key: id=key.standard.project.escalation-conditions refs=key.doc.source key.topic.document-system key.topic.skill-contract -->
## Escalation 조건

1. 원천 문서(2)가 현재 사용자 방향과 충돌한다.
2. 다섯 스킬 사이 경계가 불명확하다.
3. high-impact clarification topic을 확신 있게 해결할 수 없다.
4. document root, tracking policy, output language policy를 안전하게 추론할 수 없다.
5. work unit을 reviewable output이 있는 명확한 goal로 배정할 수 없다.
6. 문서 변경의 impact 범위가 불명확하다.
7. high-risk implementation이 필요하다.
8. 현재 step, completion criteria, applicable standard를 복구할 수 없다.
9. 기존 사용자 또는 다른 agent 변경을 덮어쓸 risk가 있다.
10. verification을 실행할 수 없거나 실패 원인이 불명확하다.

<!-- key: id=key.standard.project.active-work refs=key.topic.document-system key.topic.work-round -->
## 관련 active work

- `00_docs/works/00_key-index.md`
- `00_docs/works/r001-bootstrap-keystone/00_key-index.md`

<!-- key: id=key.standard.project.child-standards refs=key.topic.skill-contract key.topic.document-system -->
## 관련 child 기준서

- `00_docs/standards/subagents/key-standard-subagents.md`
- `00_docs/standards/skills/reader/key-standard-reader.md`
- `00_docs/standards/skills/author/key-standard-author.md`
- `00_docs/standards/skills/clarify/key-standard-clarify.md`
- `00_docs/standards/skills/linker/key-standard-linker.md`
- `00_docs/standards/skills/coordinator/key-standard-coordinator.md`
- `00_docs/standards/artifacts/key-standard-artifact-graph.md`
