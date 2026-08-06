---
doc_type: standard
created_at: "2026-07-20"
document_lifecycle: active
approval:
  state: accepted
  accepted_at: "2026-08-06"
  accepted_by: main
key:
  id: key.standard.skill.init
  refs:
    - key.role.init
    - key.role.author
    - key.role.clarify
    - key.topic.bootstrap
    - key.topic.initialization
    - key.topic.work-recovery
    - key.topic.runtime-independence
    - key.topic.temporal-metadata
---

# keystone-init 기준서

<!-- key: id=key.standard.skill.init.purpose refs=key.role.init key.topic.initialization key.topic.work-recovery -->
## 목적

`keystone-init`은 Keystone이 없는 프로젝트에 작업 복구가 가능한 최소 문서 기반과 R000을
만들고, 프로젝트 기준서 작성 흐름을 시작한다. Init의 설치된 skill package는 프로젝트 로컬
Keystone 문서 없이 실행 계약이 완결되어야 한다.

<!-- key: id=key.standard.skill.init.scope refs=key.role.init key.topic.initialization key.topic.bootstrap -->
## 적용 범위

1. `inspect`: 실제 파일과 설정을 읽어 초기화 상태만 판정한다.
2. `initialize`: 미초기화 프로젝트에 고정 scaffold와 R000을 만든다.
3. `repair`: partial scaffold를 보존적으로 보완한다.
4. 초기 설정 질문, Author/Clarify handoff, 검증과 원래 요청 resume context를 준비한다.

<!-- key: id=key.standard.skill.init.out-of-scope refs=key.role.init key.role.author key.topic.implementation -->
## 적용하지 않는 범위

1. 프로젝트 의미를 담은 기준서 내용을 직접 작성하거나 승인하기
2. 기존 문서 이동, 대규모 정규화, metadata 일괄 migration
3. Code, config, schema, API, test 또는 skill source 구현
4. Artifact relation 확정과 worker orchestration
5. 소비 프로젝트의 `standards/skills/**` 생성

<!-- key: id=key.standard.skill.init.runtime-independence refs=key.role.init key.topic.runtime-independence -->
## 런타임 독립성

Init은 프로젝트 기준서, Context Map, Init/Clarify/Author 기준서, 작업서, 진행 기록, Artifact
Graph를 선행 조건으로 요구하지 않는다. 이 저장소의 `key-standard-init.md`는 개발 명세이며,
소비 프로젝트 런타임에서는 설치된 `keystone-init` 패키지가 같은 계약을 자체 제공한다.


<!-- key: id=key.standard.skill.init.required-input refs=key.role.init key.topic.initialization -->
## Required input

1. 사용자 요청 또는 다른 skill에서 보존한 원래 요청
2. repository root와 현재 instruction context
3. 현재 사용자 지시, 존재하는 `.keystone` 설정과 문서 관례
4. 현재 workspace state와 기존 파일 변경 위험
5. mode: `inspect`, `initialize`, `repair`

직접 Init 요청은 초기화 동의를 포함한다. 다른 file-changing skill에서 넘어온 경우에는 같은
대화와 범위에서 한 번 받은 초기화 동의를 보존한다.

<!-- key: id=key.standard.skill.init.state-detection refs=key.role.init key.topic.initialization key.topic.status -->
## 상태 탐지

`../../bootstrap/key-standard-bootstrap.md`의 `uninitialized`, `bootstrapping`, `partial`,
`conflicted`, `ready`를 실제 설정과 파일로 판정한다.

1. Flag 하나만으로 `ready`를 판정하지 않는다.
2. Config가 없어도 기존 문서 관례가 하나로 명확하면 initialize 후보로 채택할 수 있다.
3. 복수 root 후보나 기존 파일 의미 충돌은 `conflicted`다.
4. Artifact Graph metadata가 아직 없다는 사실만으로 `partial`이 되지 않는다.

<!-- key: id=key.standard.skill.init.write-authority refs=key.role.init key.boundary.bounded-edit key.topic.work-round -->
## Bootstrap write authority

Init이 직접 생성할 수 있는 고정 scaffold는 다음뿐이다.

1. `.keystone/config.yaml`
2. `<document_root>/key-context-map.md` bootstrap draft
3. `<document_root>/standards/00_key-index.md`
4. `<document_root>/works/00_key-index.md`
5. `<document_root>/works/key-decisions.md`
6. `<document_root>/works/r000-project-foundation/00_key-index.md`
7. `<document_root>/works/r000-project-foundation/project-foundation/00_key-index.md`
8. `<document_root>/works/r000-project-foundation/project-foundation/key-work-project-foundation.md`
9. `<document_root>/works/r000-project-foundation/project-foundation/key-progress.md`

`<document_root>/standards/01_key-project-standard.md`의 프로젝트 의미는 Author가 작성한다.
Init template은 목적, scope, source evidence, User Decision 후보, completion criteria,
verification과 resume 지점을 담되 프로젝트 정책을 임의로 채우지 않는다.
Init이 새로 생성하는 scaffold 문서에는 생성 당일의 `created_at: YYYY-MM-DD`를 기록한다.
Draft/pending 문서에는 `approval.accepted_at`을 만들지 않으며, 새 결정이 실제로 기록되면
결정이 확정된 `결정일`을 사용한다.


<!-- key: id=key.standard.skill.init.workflow refs=key.role.init key.role.author key.role.clarify key.topic.initialization -->
## Workflow

1. 상태와 document root 후보를 inspect한다.
2. 현재 지시와 우선순위로 안전하게 결정되는 초기 설정은 질문 없이 적용한다.
3. Document root 등 내장 초기 설정에 실제 선택지가 있으면 Init이 사용자에게 직접 묻는다.
4. 복수의 유효한 문서 채택·이동·대체 선택이나 프로젝트 의미 결정은 Clarify에 한 topic씩
   handoff한다.
5. `uninitialized`이면 고정 scaffold와 R000을 만든다.
6. `partial`이면 기존 파일을 보존하고 누락 scaffold만 repair한다.
7. Main의 일반 repository 조사에서 얻은 사실과 사용자 지시를 R000의 Author input evidence로
   연결한다.
8. Author가 프로젝트 기준서를 draft로 작성하게 handoff한다.
9. 필요한 User Decision이 해결되고 Author 문서가 검증되면 Main이 수락한다.
10. R000과 전체 최소 구조를 검증해 `ready`를 판정한다.
11. Init을 요구한 원래 skill과 요청, 중단 단계로 resume한다.

질문 수집을 특정 호스트의 내부 mode로 규정하지 않는다. 사용할 수 있는 호스트 질문 기능은
자연스럽게 활용하되, skill이 실행 mode를 전환하거나 활성화했다고 주장하지 않는다.

<!-- key: id=key.standard.skill.init.safety refs=key.role.init key.topic.initialization key.boundary.stop-condition -->
## 안전성과 idempotency

1. 반복 실행해도 동일한 유효 scaffold를 중복 생성하지 않는다.
2. 기존 파일을 무조건 덮어쓰지 않는다.
3. 사용자 또는 다른 agent 변경을 보존한다.
4. 충돌 없이 누락된 고정 scaffold만 보완한다.
5. 기존 문서의 이동과 대규모 정규화를 자동 수행하지 않는다.
6. 생성 후 실제 파일과 link를 검증한 뒤에만 다음 상태를 판정한다.
7. 사용자 초기화 거부 시 파일을 생성하지 않는다.
8. Repair 중 기존 문서의 `created_at`을 현재 실행일로 덮어쓰거나 근거 없이 과거 날짜를
   추정하지 않는다.

<!-- key: id=key.standard.skill.init.clarify-boundary refs=key.role.init key.role.clarify key.topic.user-decision -->
## Clarify 경계

Init이 직접 묻는 항목은 document root처럼 초기화를 실행하기 위한 설정이다. Clarify는 다음과
같은 실제 사용자 결정만 다룬다.

1. 복수의 유효한 기준문서 root 중 권위 있는 하나의 선택
2. 기존 문서를 채택·이동·대체할지 결정
3. 프로젝트 목적, 범위, 정책, 용어, 권위 관계
4. 민감 정보 저장 또는 외부 공개처럼 사용자 권한이 필요한 선택

기본 metadata, 기본 파일명/index 구조, skill 역할, `standards/skills/**` 부재, 내부 handoff
payload는 Clarify topic이 아니다.

<!-- key: id=key.standard.skill.init.fail-soft refs=key.role.init key.topic.initialization -->
## Fail-soft

1. `inspect`는 어떤 상태에서도 파일을 수정하지 않는다.
2. `partial`은 단순 오류가 아니라 `repair` 가능한 상태다.
3. `conflicted`에서는 안전한 파일만 보존하고 충돌 대상을 덮어쓰지 않는다.
4. 사용자 결정을 기다리는 동안 원래 요청과 resume context를 잃지 않는다.
5. 검증 불가능 항목은 확정 오류와 구분해 보고한다.

<!-- key: id=key.standard.skill.init.scenarios refs=key.role.init key.topic.integration-verification key.topic.initialization -->
## 통합 시나리오

1. 빈 저장소에서 직접 Init
   - 기본 root `00_docs`, 고정 scaffold와 R000 생성, Author project standard draft, Main 검증과
     수락 후 `ready`, `standards/skills/**` 미생성
2. 빈 저장소에서 Author
   - Author가 미초기화를 detect하고 한 번 동의를 받은 뒤 Init handoff, 검증, 원래 Author
     요청 resume
3. 빈 저장소에서 Reader
   - 파일을 만들지 않고 partial orientation, 상태, 읽지 못한 Keystone context와 Init 제안
4. 부분 초기화
   - 기존 파일 보존, 충돌 없는 누락 scaffold만 repair, 불필요한 질문 없음
5. Document root 충돌
   - 임의 선택 없이 Clarify가 권위 있는 root 한 topic을 처리하고 Init resume
6. 프로젝트 내용의 사용자 결정
   - Init 또는 Author가 프로젝트 의미 불확실성을 발견하면 Clarify가 해당 topic 하나를
     처리하고 원래 작성 흐름 resume
7. 작업서나 graph evidence가 아직 적은 프로젝트
   - R000과 프로젝트 기준서로 작업 복구 가능, Linker/Coordinator 산출물 부재는 초기화 오류가
     아님
8. 프로젝트 로컬 스킬 기준서 없음
   - Reader, Author, Clarify, Linker, Coordinator, Init이 설치된 계약으로 정상 동작
9. 사용자 초기화 거부
   - 파일을 생성하지 않고 가능한 partial 결과, 현재 제한, 후속 Init 방법만 안내

<!-- key: id=key.standard.skill.init.stop-condition refs=key.role.init key.topic.initialization key.boundary.stop-condition -->
## Stop condition

1. 복수 document root나 기존 파일 의미 충돌을 안전하게 해소할 수 없다.
2. 기존 문서를 덮어써야만 진행할 수 있다.
3. 사용자 지시와 설정이 충돌한다.
4. 프로젝트 의미에 영향을 주는 필수 User Decision이 해결되지 않았다.
5. Bootstrap write authority 밖의 변경이 필요하다.
6. 민감 정보 저장, 파괴적 이동 또는 외부 공개가 필요하다.

<!-- key: id=key.standard.skill.init.verification refs=key.role.init key.topic.verification key.topic.initialization -->
<!-- key: id=key.standard.skill.init.dependency-boundary refs=key.role.init key.topic.initialization key.topic.work-sequence -->
## Dependency boundary

Init은 fixed R000 scaffold에 project-specific dependency나 `work_gates`를 추정해 생성하지 않는다.
기존 scaffold의 dependency target이 missing/conflicted이면 덮어쓰거나 status를 바꾸지 않고
repair 후 Reader/Author/Main이 복구할 risk로 보고한다.

## Verification

1. `inspect`, `initialize`, `repair`의 쓰기 권한 차이가 명확해야 한다.
2. 같은 상태에서 재실행해도 기존 파일 의미가 보존되어야 한다.
3. 고정 scaffold와 Author project standard 책임이 분리되어야 한다.
4. 아홉 통합 시나리오의 기대 동작을 이 계약만으로 설명할 수 있어야 한다.
5. Init 이후 원래 요청, skill과 resume 단계가 복구되어야 한다.
6. 소비 프로젝트 로컬 Init 기준서를 required input으로 요구하지 않아야 한다.
7. 새 scaffold의 `created_at`, pending approval과 결정일이 Bootstrap temporal metadata 기준과
   일치해야 하며, repair가 기존 날짜를 바꾸지 않아야 한다.

<!-- key: id=key.standard.skill.init.context-readiness-boundary refs=key.role.init key.role.reader key.role.linker key.topic.work-recovery -->
## Context readiness 경계

1. Usable Keystone foundation이 있는 프로젝트의 session orientation과 cache/index readiness는
   Init mode가 아니라 Reader가 수행한다.
2. Init은 external Linker cache를 scaffold, repair 또는 source-of-truth로 만들지 않는다.
3. Initialization inspection 중 graph/index cache가 없거나 stale해도 foundation state를 낮추지
   않는다. Source documents와 recovery invariants만 initialization state를 결정한다.
4. Initialize/repair 뒤 필요한 첫 orientation은 Reader handoff로 남긴다. Repository artifact scan은
   해당 후속 요청에 필요할 때만 lazy하게 수행한다.
