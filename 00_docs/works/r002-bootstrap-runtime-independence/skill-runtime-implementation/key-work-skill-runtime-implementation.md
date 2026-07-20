---
doc_type: work_order
status: active
approval:
  state: accepted
  accepted_by: main
work_status: accepted
key:
  id: key.work.skill-runtime-implementation.order
  refs:
    - key.doc.work
    - key.topic.skill-source
    - key.topic.runtime-independence
    - key.topic.initialization
    - key.topic.change-set
---

# Skill Runtime Implementation 작업서 및 Change Set

<!-- key: id=key.work.skill-runtime-implementation.order.goal refs=key.section.goal key.topic.skill-source -->
## Goal

설치된 package만으로 완결되는 `keystone-init`을 추가하고 기존 다섯 Keystone skill source를
R002 runtime independence 계약과 일치시킨다.

<!-- key: id=key.work.skill-runtime-implementation.order.scope refs=key.section.scope key.artifact.skill-md -->
## Scope

Include:

- `skills/keystone-init/SKILL.md`와 필요한 package-local reference/template
- `skills/keystone-reader/SKILL.md`
- `skills/keystone-author/SKILL.md`
- `skills/keystone-clarify/SKILL.md`
- `skills/keystone-linker/SKILL.md`
- `skills/keystone-coordinator/SKILL.md`
- 빈/부분/충돌/ready 및 handoff/resume 검증 fixture나 script가 필요하면 별도 승인 범위로 추가

Exclude:

- plugin packaging, marketplace registration, global install, publish
- 소비 프로젝트 `standards/skills/**` template
- 전체 기존 문서 metadata migration
- Linker/Coordinator 기능 확장

<!-- key: id=key.work.skill-runtime-implementation.order.sequence refs=key.topic.work-sequence key.topic.initialization -->
## 구현 순서

1. `keystone-init`의 inspect/state detection과 no-write report
2. Idempotent initialize/repair, fixed scaffold와 R000 template
3. Author의 Init handoff/resume와 runtime local-standard 의존 제거
4. Reader pre-init fail-soft와 일반 repository 조사 비소유 경계
5. Clarify의 실제 User Decision 및 호출자 resume
6. Linker read-only automatic use와 graph gap fail-soft
7. Coordinator의 per-scope permission과 execution environment 비강제
8. 아홉 통합 시나리오와 기존 프로젝트 legacy adoption 검증

<!-- key: id=key.work.skill-runtime-implementation.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Source standards: `00_docs/standards/bootstrap/key-standard-bootstrap.md`,
  `00_docs/standards/skills/init/key-standard-init.md`, 기존 다섯 skill 개발 기준서
- Required artifacts: 여섯 `SKILL.md` runtime contract
- Required behavior: 상태 탐지, handoff/resume, self-contained package, fail-soft, 질문/허락 경계
- Excluded behavior: profile, project-local skill standards, Plan mode claim, mandatory routing,
  Keystone-owned workspace/worktree strategy
- Verification: package lint/check, scenario fixtures, source-standard cross-read, no unrelated changes
- Acceptance: Main verification 후 수락; 사용자 판단이 필요한 새 scope가 생기면 별도 User Decision

<!-- key: id=key.work.skill-runtime-implementation.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. 수락된 R002 기준과 구현이 충돌한다.
2. 기존 사용자 변경을 덮어써야 한다.
3. 공개·설치·패키징 또는 repository-wide migration이 필요하다.
4. Coordinator 위임이 필요하지만 해당 work scope의 사용자 허락이 없다.

<!-- key: id=key.work.skill-runtime-implementation.order.completion refs=key.topic.acceptance key.topic.integration-verification -->
## Completion Criteria

- [x] `keystone-init` package source가 추가되고 inspect/initialize/repair 계약이 자체 완결된다.
- [x] 기존 다섯 Keystone skill source가 프로젝트 로컬 skill 기준서 없이 동작한다.
- [x] Init handoff와 원래 요청 resume, 실제 User Decision의 Clarify 경계가 반영됐다.
- [x] Reader pre-init, sparse graph와 Coordinator 비활성 상황이 fail-soft로 처리된다.
- [x] Coordinator는 사용자 허락 범위 안에서만 위임하고 실행 환경을 강제하지 않는다.
- [x] 구조 검사와 빈·부분·충돌·ready 흐름의 forward test를 통과했다.
- [x] plugin packaging, global install과 publish는 변경하지 않았다.
