---
doc_type: standard
created_at: "2026-07-20"
document_lifecycle: active
approval:
  state: pending
key:
  id: key.standard.bootstrap
  refs:
    - key.doc.standard
    - key.topic.bootstrap
    - key.topic.initialization
    - key.topic.runtime-independence
    - key.topic.user-decision
    - key.topic.acceptance
    - key.topic.work-recovery
    - key.topic.temporal-metadata
---

# Keystone Bootstrap 및 런타임 독립성 기준서

<!-- key: id=key.standard.bootstrap.purpose refs=key.topic.bootstrap key.topic.runtime-independence key.topic.work-recovery -->
## 목적

Keystone을 한 번도 사용하지 않은 프로젝트에서도 먼저 작업을 복구할 문서 기반을 만들고,
그 기반 위에서 프로젝트 기준서를 자연스럽게 작성할 수 있게 한다. Bootstrap은 Keystone의
영구적인 축소 운영 형태가 아니라, 공통 운영 모델로 진입하기 위한 일시적인 과정이다.

<!-- key: id=key.standard.bootstrap.scope refs=key.topic.bootstrap key.topic.initialization key.topic.acceptance -->
## 적용 범위

1. 설치된 스킬 패키지와 소비 프로젝트 문서의 권위 경계
2. 초기화 상태와 `ready` 판정
3. R000 Project Foundation의 목적과 최소 구조
4. 초기화 전 프로젝트 조사와 Author/Clarify 연결
5. Main 수락과 User Decision의 분리
6. Init handoff, resume, fail-soft 공통 동작
7. Bootstrap 문서 metadata와 상태 의미

<!-- key: id=key.standard.bootstrap.out-of-scope refs=key.topic.skill-source key.topic.implementation -->
## 적용하지 않는 범위

1. 특정 호스트 AI의 내부 실행 mode, UI 또는 질문 API 지정
2. 소비 프로젝트에 Keystone 스킬별 기준서를 복제하는 동작
3. 기존 문서의 자동 이동, 일괄 metadata migration, 대규모 정규화
4. `skills/keystone-*/SKILL.md` 구현과 validator, packaging, publishing
5. Worktree, branch, 병렬 writer 수 같은 실행 환경 전략의 강제

<!-- key: id=key.standard.bootstrap.authority-boundary refs=key.topic.runtime-independence key.topic.skill-contract key.doc.source -->
## 런타임 권위 경계

Keystone의 기준은 다음 세 층으로 나눈다.

1. 설치된 스킬 패키지
   - 역할, trigger/non-trigger, 필수 입력, workflow, 수정 권한, 출력, stop condition,
     fail-soft, 초기화 상태 탐지와 handoff/resume 같은 고유 실행 계약을 소유한다.
   - 핵심 실행 계약은 설치된 `SKILL.md`만으로 완결되어야 한다. 상세 schema, template,
     validator는 같은 패키지의 `references/`, `assets/`, `scripts/`에 둘 수 있다.
   - Acceptance finalization core validator는 새 스킬이 아니라 `keystone-author/scripts/`의
     bundled artifact로 제공하며 설치 시 Author package와 함께 복사한다.
2. 소비 프로젝트의 Keystone 문서
   - 프로젝트 목적, 범위, 용어, architecture, domain policy, document root, 프로젝트 고유
     승인 규칙, 결정, 작업, 진행 상태와 Artifact Graph evidence를 정의한다.
   - Reader, Author, Clarify, Linker, Coordinator, Init의 고유 작동 방식을 다시 정의하지 않는다.
3. Keystone 저장소의 `00_docs/standards/skills/**`
   - Keystone 스킬을 개발하고 검수하기 위한 원천 명세다.
   - 배포된 스킬의 소비 프로젝트 런타임 선행 문서가 아니다.

따라서 소비 프로젝트는 `standards/skills/reader`, `author`, `clarify`, `linker`,
`coordinator`, `init` 문서를 생성하거나 필수 입력으로 요구하지 않는다.

<!-- key: id=key.standard.bootstrap.operating-model refs=key.topic.bootstrap key.topic.artifact-graph key.role.coordinator -->
## 공통 운영 모델

Keystone은 Lite, Standard, Graph, Orchestrated 같은 도입 profile을 두지 않는다.

1. 기준서와 작업 복구는 모든 Keystone 프로젝트의 중심이다.
2. Artifact Graph와 coordination은 문서와 구현을 유기적으로 연결하는 핵심 능력이다.
3. 관련 artifact relation이 아직 없다는 이유로 초기화 실패나 낮은 profile로 판정하지 않는다.
4. Linker는 read-only이므로 Main이 필요하다고 판단하면 별도 사용자 승인 없이 사용할 수 있다.
5. Coordinator는 영향 범위가 크므로 work scope마다 사용자 허락을 받아야 한다. 사용자가
   직접 Coordinator를 호출한 경우 해당 요청 범위의 허락으로 본다.
6. 명확하고 작은 작업은 Main이 직접 수행할 수 있다. 위임이 유용하면 Main은 사용자에게
   위임 여부를 물을 수 있다.

<!-- key: id=key.standard.bootstrap.state-model refs=key.topic.initialization key.topic.status key.topic.bootstrap -->
## 초기화 상태

상태는 단일 flag가 아니라 실제 설정과 파일을 검사해 판정한다.

1. `uninitialized`
   - Keystone 설정과 권위 있는 document root를 해석할 수 없고 R000 구조도 없다.
2. `bootstrapping`
   - Init scaffold와 R000이 존재하며 프로젝트 기준서를 작성·검증·수락하는 중이다.
3. `partial`
   - 설정, index, Context Map, 결정 기록, R000 필수 문서 중 일부가 누락되었거나 초기화가
     중단되었다.
4. `conflicted`
   - 복수 document root, 기존 문서와 생성 경로, 사용자 지시와 설정처럼 안전하게 자동
     채택할 수 없는 충돌이 있다.
5. `ready`
   - config가 유효하거나 기존 adoption 결정으로 document root가 하나로 해석되고, Context Map,
     standards/works index, 결정 기록, 수락된 프로젝트 기준서가 존재한다.
   - 새 소비 프로젝트는 R000이 Main에 의해 수락되었고 후속 작업을 문서에서 복구할 수 있다.
   - 이미 Keystone corpus와 accepted project standard, active work가 있는 기존 프로젝트는
     별도 adoption 결정으로 현재 document root와 구조를 채택할 수 있으며 config나 R000을
     소급 생성하지 않는다.
   - 열린 필수 User Decision이 없다.

Artifact Graph relation, Linker report, Coordinator 문서나 worker report의 부재만으로
`partial` 또는 `conflicted`가 되지 않는다.

<!-- key: id=key.standard.bootstrap.document-root refs=key.topic.initialization key.topic.document-system -->
## Document root 결정

기본 document root는 `00_docs`다. 다음 우선순위에서 충돌 없이 해석되는 첫 값을 사용한다.

1. 현재 사용자의 명시적 지시
2. `.keystone/config.local.yaml`
3. `.keystone/config.yaml`
4. 프로젝트의 명시적 agent setting
5. 충돌 없는 기존 문서 관례
6. Keystone 기본값 `00_docs`

사용자가 Init을 직접 요청하면 초기화 자체를 다시 승인받지 않는다. 다만 document root처럼
초기 설정에 실제 선택지가 있으면 Init이 직접 자연스럽게 질문할 수 있다. 복수 후보가
충돌하거나 기존 문서의 채택·이동·대체처럼 프로젝트 의미에 영향을 주는 결정은 Clarify가
한 topic씩 다룬다.

<!-- key: id=key.standard.bootstrap.r000 refs=key.topic.work-round key.topic.work-recovery key.role.author -->
## R000 Project Foundation

새 소비 프로젝트의 첫 작업 round는 `R000 Project Foundation`이다.

1. R000의 목표는 프로젝트 기준서를 만들고 이후 작업을 문서에서 복구할 수 있게 하는 것이다.
2. 기본 S01 이름은 `Establish Project Standards`다. `R000`의 `000`은 기준서가 아직 없는
   foundation round를 뜻하며 step 번호는 다른 round와 같이 `S01`부터 시작한다.
3. Init은 고정된 R000 scaffold와 작업서 template까지만 만든다.
4. 프로젝트 의미를 담은 `standards/01_key-project-standard.md`는 Author가 만든다.
5. 이미 내용이 있는 프로젝트에서는 Main이 보통의 repository 조사 능력으로 code, README,
   설정과 구조를 읽고 확인한 사실을 Author input으로 제공한다.
6. 비어 있는 프로젝트에서는 목적, 범위, 핵심 정책처럼 실제 사용자 결정이 필요한 topic을
   Clarify가 하나씩 다룬다.
7. 조사 결과와 추론은 evidence이며, Author가 문서로 만들고 Main이 수락하기 전까지 프로젝트
   규범적 권위가 아니다.

이 규칙은 새 소비 프로젝트에 적용한다. 이 Keystone 구현 저장소처럼 이미 accepted corpus와
복구 가능한 active work가 있는 프로젝트는 기존 이력을 보존하고 adoption/correction round로
전환한다. 이 저장소에서는 R000을 소급 생성하지 않고 R002가 그 역할의 보완을 기록한다.

초기화 전 일반 repository 조사를 Reader의 책임이나 Keystone 전용 조사 절차로 강제하지
않는다. Keystone 문서가 생긴 뒤에는 Reader가 Context Map, 기준서, 작업서와 진행 기록을
탐색하고 Linker가 graph와 구현 관계를 분석한다.

<!-- key: id=key.standard.bootstrap.handoff-resume refs=key.topic.initialization key.topic.handoff key.topic.work-recovery -->
## Detect, handoff, resume

스킬 간 전환은 함수 호출처럼 표현하지 않고 `detect`, `handoff`, `resume`으로 설명한다.

1. File-changing skill이 `uninitialized` 또는 `partial`을 발견하면 사용자에게 초기화 또는
   repair 후 계속할지 한 번 확인한다.
2. 같은 대화와 같은 범위에서 이미 동의했다면 다시 묻지 않는다.
3. 사용자가 동의하면 Init으로 handoff하고 검증 뒤 원래 skill과 요청으로 자동 resume한다.
4. Reader는 미초기화 상태에서 파일을 만들지 않고, 현재 확인 가능한 orientation과 제한,
   Init 제안을 제공한다.
5. 사용자가 초기화를 거부하면 파일을 만들지 않고 가능한 partial 결과와 후속 Init 방법만
   안내한다.
6. Handoff는 원래 요청, 최초 skill, 초기화 이유, resume 지점, 이미 정해진 결정, 기존 파일
   위험을 보존한다.

<!-- key: id=key.standard.bootstrap.user-decision refs=key.topic.user-decision key.topic.acceptance key.role.clarify -->
## Main 수락과 User Decision

AI가 확인하고 검증할 수 있는 단계는 Main이 위임 범위 안에서 직접 진행하고 수락한다.
별도의 보편적인 사용자 최종 승인 단계는 두지 않는다.

1. Worker의 `DONE`은 Main 수락이 아니다. Main은 실제 결과, scope, completion criteria,
   verification과 residual risk를 확인한다.
2. 프로젝트 목적·범위, 충돌하는 유효 대안, 민감 정보 저장, 파괴적 migration, 외부 공개·비용,
   위임 범위 확장처럼 사용자 판단이 필요한 경우에만 별도 `User Decision` step을 둔다.
3. User Decision이 해결되면 중단한 Init, Author 또는 Coordinator 흐름을 자동 resume한다.
4. Main, Author, Init은 사용자 결정을 만들어내지 않는다. 확인 가능한 사실과 안전한 기본값으로
   진행하고, 필요한 결정만 사용자에게 묻는다.
5. Coordinator는 사용 허락 자체가 User Decision인 예외다. 한 work scope에 한 번 받고,
   같은 범위의 assignment, review, repair에는 반복하지 않는다.

<!-- key: id=key.standard.bootstrap.metadata-status refs=key.topic.keystone-metadata key.topic.temporal-metadata key.topic.status key.topic.acceptance -->
## 문서 metadata와 상태

Bootstrap과 이후 운영에서 YAML frontmatter는 문서 단위 identity와 상태의 기본 표현이다.

```yaml
---
doc_type: standard
created_at: "2026-07-23"
status: draft
approval:
  state: pending
key:
  id: key.standard.project
  refs: []
  relations: []
---
```

1. 문서 lifecycle: `draft`, `active`, `superseded`, `archived`
2. 문서 approval: `pending`, `accepted`, 필요한 경우 `rejected`
3. 작업 진행 상태, Main의 결과 수락, 산출물 lifecycle은 위 두 상태와 별도 namespace다.
4. `accepted`는 문서 lifecycle이 아니라 approval state다.
5. `active` 문서는 Main 또는 필요한 User Decision에서 나온 추적 가능한 acceptance 근거가
   있어야 한다.
6. 새 원천 문서의 `created_at`은 최초 생성일을 `YYYY-MM-DD`로 기록하고 이후 수정하지 않는다.
7. `approval.state: accepted`에는 현재 의미가 수락된 날짜인 `accepted_at: YYYY-MM-DD`가
   있어야 한다. 의미가 바뀌면 approval을 `pending`으로 돌리고 현재 `accepted_at`을 제거한 뒤,
   다시 수락할 때 새 수락일을 기록한다.
8. 의미 없는 형식 변경은 그 사실을 기록하고 기존 approval과 `accepted_at`을 유지할 수 있다.
9. 승인일과 실제 효력 시작일이 다를 때만 `effective_from: YYYY-MM-DD`를 사용할 수 있다.
   문서가 대체된 날짜를 별도로 추적할 필요가 있을 때만 `superseded_at: YYYY-MM-DD`를 사용한다.
10. 문서 전체의 일반적인 `updated_at`은 사용하지 않는다. 오탈자·서식 변경까지 의미 변경처럼
    보이게 하고 Git 이력과 중복되기 때문이다.
11. 결정 기록의 새 결정에는 `결정일: YYYY-MM-DD`를 둔다. 과거 결정을 나중에 기록한 경우에만
    `기록일`, 대체 시점을 별도로 보존할 필요가 있을 때만 `대체일`을 추가한다.
12. 문서·결정의 거버넌스 날짜는 `YYYY-MM-DD`를 기본으로 한다. 실행 event의 정확한 순서가
    필요한 별도 기록만 ISO 8601 timestamp와 명시적 timezone을 사용한다.
13. 날짜가 최신이라는 이유만으로 문서나 결정의 권위가 올라가지 않는다. lifecycle,
    approval과 `supersedes` 같은 typed relation이 권위와 대체 관계를 결정한다.
14. `key.refs`는 탐색용 일반 참조이며 자동 영향 전파가 아니다. `governed_by`, `depends_on`,
   `supersedes`, `derived_from` 등은 typed relation으로 구분한다.
15. 새 Bootstrap 문서는 이 형식을 적용한다. 기존 corpus의 날짜를 추측하지 않으며, repository
    history 등으로 확인 가능한 날짜만 근거를 검증한 뒤 별도 승인된 migration에서 반영한다.
    검사할 수 없는 날짜는 오류가 아니라 미확인 legacy metadata로 보고한다.

<!-- key: id=key.standard.bootstrap.fail-soft refs=key.topic.initialization key.topic.artifact-graph key.boundary.read-only -->
## Fail-soft

1. Reader: 존재하는 Keystone 문서만으로 partial 결과를 제공한다.
2. Author: 초기화가 필요하면 Init handoff 후 원래 문서 작업을 resume한다.
3. Init: `partial`이면 기존 파일을 보존하고 누락 scaffold만 repair한다.
4. Clarify: 실제 사용자 결정이 없으면 호출하지 않는다.
5. Linker: graph evidence가 없으면 확인 가능한 범위와 gap을 보고하며 사용자 작업을 막지 않는다.
6. Coordinator: 사용자 허락이 없으면 자동 호출하지 않고 Main direct 또는 허락 요청을 제안한다.
7. 기존 문서 충돌: 덮어쓰지 않고 `conflicted`와 결정 topic을 보고한다.
8. 구현 작업: 기준 부재가 실제 방향이나 안전성에 영향을 줄 때만 중단한다.

<!-- key: id=key.standard.bootstrap.dependency-compatibility refs=key.topic.artifact-graph key.topic.work-sequence key.topic.work-recovery -->
## Dependency compatibility

1. Structured `key.relations.depends_on`/`work_gates`를 우선하고 legacy HTML `depends_on`은
   structured metadata가 없을 때만 compatibility evidence로 읽는다.
2. Legacy work-level dependency는 source 시작을 자동 차단하지 않고 completion gate 후보로
   보고한다.
3. Init은 프로젝트 의미를 추정해 dependency/gate를 생성하지 않고, Reader/Linker는
   없거나 모호한 target을 fail-soft로 보고한다.
4. Dependency evaluation은 initialization state, lifecycle, approval, work status를 대체하지 않는다.

<!-- key: id=key.standard.bootstrap.verification refs=key.topic.verification key.topic.initialization -->
## Verification

1. 설치된 skill contract만으로 초기화 상태 탐지와 Init handoff를 설명할 수 있어야 한다.
2. 소비 프로젝트에 `standards/skills/**`가 없어도 정상 상태로 해석되어야 한다.
3. `ready` 판정은 파일 존재뿐 아니라 R000, 프로젝트 기준서 수락, work recovery 가능성을
   확인해야 한다.
4. 일반 repository 조사는 Reader나 특정 호스트 mode의 선행 조건이 아니어야 한다.
5. 초기화 질문과 실제 프로젝트 의미 결정이 분리되어야 한다.
6. 사용자 초기화 거부, partial, conflict에서 기존 파일을 덮어쓰지 않아야 한다.

<!-- key: id=key.standard.bootstrap.context-readiness refs=key.topic.bootstrap key.topic.work-recovery key.role.reader key.role.linker -->
## 초기화와 session context readiness 분리

Init은 Keystone foundation이 없거나 partial/conflicted인 프로젝트의 inspect/initialize/repair를
소유한다. 이미 usable foundation이 있는 프로젝트에서 사용자가 세션 시작에 Reader를 명시 호출해
project context를 복구하는 것은 Init이 아니라 Reader context readiness다.

1. Reader는 configured document root를 우선 읽고 docs discovery scope의 path set/raw-byte digest를
   Linker external index freshness와 대조한다.
2. Code/config/schema/test repository scan은 초기화나 session orientation의 필수 조건이 아니며
   artifact context가 실제로 필요한 요청에서 lazy하게 수행한다.
3. Cache/index miss, corruption 또는 write failure는 foundation 상태를 `partial`로 바꾸지 않는다.
   Reader/Linker는 source 직접 탐색으로 fail-soft fallback한다.
4. Owner/ref index와 typed graph projection은 source에서 재생성 가능하고 repository 밖에 있으며
   초기화 scaffold나 소비 프로젝트의 권위 문서가 아니다.
