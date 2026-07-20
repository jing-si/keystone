---
doc_type: work_order
status: active
approval:
  state: accepted
  accepted_by: main
work_status: accepted
key:
  id: key.work.bootstrap-runtime-standard.order
  refs:
    - key.doc.work
    - key.topic.bootstrap
    - key.topic.initialization
    - key.topic.runtime-independence
    - key.topic.integration-verification
---

# Bootstrap Runtime Standard 작업서

<!-- key: id=key.work.bootstrap-runtime-standard.order.goal refs=key.section.goal key.topic.bootstrap -->
## Goal

Keystone을 처음 도입하는 프로젝트가 R000과 Author를 통해 기준서를 만들고, 설치된 각 skill이
프로젝트 로컬 skill별 기준서 없이 동작하도록 권위 있는 개발 기준을 개편한다.

<!-- key: id=key.work.bootstrap-runtime-standard.order.finding refs=key.topic.findings key.topic.initialization -->
## Integration finding

R001 skill source review를 실제 프로젝트 적용 관점에서 진행한 결과, 프로젝트 기준서, Context
Map, 작업서와 skill별 기준서가 이미 존재해야 Reader, Author, Clarify, Linker, Coordinator가
동작하는 순환 의존을 확인했다. 이 finding은 R001의 실패 판정이 아니라 미수락 S08-S09를 새
계약으로 재구성해야 하는 corrective input이다.

<!-- key: id=key.work.bootstrap-runtime-standard.order.scope refs=key.section.scope key.boundary.skill-source-forbidden -->
## Scope

Include:

- Bootstrap 공통 기준과 `keystone-init` 개발 기준
- Project, Reader, Author, Clarify, Linker, Coordinator, Subagent, Artifact Graph 기준 개편
- 설치된 package와 소비 프로젝트의 권위 경계
- R000, 초기화 상태, handoff/resume, Main acceptance와 User Decision
- R001 S08-S09 supersession, R002 작업 복구 문서
- 기준서/스킬/작업 색인과 Context Map
- 문서 기반 통합 시나리오 검증
- 후속 skill runtime implementation Change Set

Exclude:

- `skills/keystone-*/SKILL.md` 수정
- `skills/keystone-init/` 생성
- validator, automation script, plugin packaging, publish/install
- 기존 문서의 일괄 metadata migration
- README와 code/config/schema/API/test 수정

<!-- key: id=key.work.bootstrap-runtime-standard.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: 기준서 중심성과 작업 복구 능력을 유지하면서 bootstrap 순환 의존을 제거한다.
- Required documents: Bootstrap/Init 기준, project/skill/subagent/artifact 기준, decisions,
  R001/R002 상태, index와 Context Map
- Excluded artifacts: 현재 다섯 `skills/keystone-*/SKILL.md`, 새 Init source, repository code
- Impact seeds: `DEC-WORKS-007`, `DEC-WORKS-008`, `DEC-WORKS-012`,
  `STD-KEYSTONE-007`, `STD-KEYSTONE-041`, `STD-KEYSTONE-046`, R001 S08-S09
- Acceptance owner: Main

<!-- key: id=key.work.bootstrap-runtime-standard.order.completion refs=key.topic.acceptance key.topic.integration-verification -->
## Completion Criteria

- [x] `keystone-init`의 역할, mode와 bounded write authority가 명확하다.
- [x] 초기화 상태와 `ready`, R000, legacy adoption 조건이 정의되어 있다.
- [x] 설치된 skill contract와 소비 프로젝트 문서의 권위 경계가 명확하다.
- [x] 소비 프로젝트의 `standards/skills/**`가 runtime 선행 조건이 아니다.
- [x] Author Init handoff와 원래 요청 resume가 정의되어 있다.
- [x] Reader는 pre-init에서 파일을 만들거나 일반 repository 조사를 독점하지 않는다.
- [x] Clarify는 실제 User Decision만 한 topic씩 처리한다.
- [x] Linker는 자동 사용 가능하고 graph evidence 부재에서 fail-soft로 동작한다.
- [x] Coordinator는 work scope별 사용자 허락을 요구한다.
- [x] Keystone이 특정 worktree/workspace/concurrency 전략을 강제하지 않는다.
- [x] 문서 lifecycle, approval, work status와 Main acceptance가 분리되어 있다.
- [x] Routing payload가 모든 작업의 ceremony나 기본 사용자 출력이 아니다.
- [x] R001 accepted 이력이 보존되고 S08-S09만 superseded다.
- [x] 관련 index, Context Map과 key refs가 일관된다.
- [x] 이번 변경으로 `skills/**`가 추가 수정되지 않는다.

<!-- key: id=key.work.bootstrap-runtime-standard.order.scenarios refs=key.topic.integration-verification key.topic.initialization -->
## 검증 시나리오

1. 빈 저장소에서 Init 직접 실행
2. 빈 저장소에서 Author가 Init handoff 후 자동 resume
3. 빈 저장소에서 Reader가 read-only partial orientation 제공
4. 부분 초기화에서 기존 파일 보존과 누락 scaffold repair
5. 복수 document root에서 Clarify 한 topic 후 Init resume
6. 프로젝트 의미 결정에서 Clarify 한 topic 후 Author resume
7. graph/Coordinator 산출물이 적은 프로젝트의 정상 운영
8. 프로젝트 로컬 skill별 기준서가 없는 소비 프로젝트
9. 사용자 초기화 거부 시 no-write와 제한 안내

<!-- key: id=key.work.bootstrap-runtime-standard.order.verification refs=key.topic.verification -->
## Verification

- `git diff --check`
- active round와 R001/R002 status consistency scan
- `single workspace`, host mode, mandatory routing 잔존 규칙 검토
- 신규 `key.id` duplicate와 문서 path/link 존재 확인
- 작업 시작 전후 `skills/**` diff 비교

<!-- key: id=key.work.bootstrap-runtime-standard.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. 기존 accepted R001 의미를 직접 덮어써야 한다.
2. 사용자와 확정하지 않은 프로젝트 정책 결정이 새로 필요하다.
3. `skills/**` 또는 repository source 수정이 필요하다.
4. 기존 사용자 변경을 보존할 수 없다.
