---
doc_type: work_order
created_at: "2026-07-25"
status: active
approval:
  state: accepted
  accepted_at: "2026-07-25"
  accepted_by: main
work_status: accepted
key:
  id: key.work.dependency-runtime-implementation.order
  refs:
    - key.doc.work
    - key.topic.skill-source
    - key.topic.artifact-graph
    - key.topic.work-recovery
    - key.topic.change-set
---

# Dependency Runtime Implementation 작업서 및 Change Set

<!-- key: id=key.work.dependency-runtime-implementation.order.goal refs=key.section.goal key.topic.skill-source -->
## Goal

S01에서 수락된 관계, gate, 호환성과 판정 계약을 관련 Keystone skill의 self-contained runtime
contract에 구현한다.

<!-- key: id=key.work.dependency-runtime-implementation.order.precondition refs=key.topic.work-sequence key.step.s01 -->
## 선행 조건

- S01 기준서와 공통 결정이 Main에 의해 수락되어야 한다.
- 현재 작업 트리의 기존 변경과 S02 대상 파일의 overlap을 다시 확인해야 한다.

<!-- key: id=key.work.dependency-runtime-implementation.order.scope refs=key.section.scope key.artifact.skill-md -->
## Scope

Include:

- `skills/keystone-author/SKILL.md`
- `skills/keystone-reader/SKILL.md`
- `skills/keystone-linker/SKILL.md`
- `skills/keystone-init/SKILL.md`
- `skills/keystone-coordinator/SKILL.md`
- S01에서 Clarify decision trigger가 실제로 바뀐 경우에만 `skills/keystone-clarify/SKILL.md`
- 각 runtime source의 input, workflow, output, fail-soft, stop condition과 verification 계약

Exclude:

- Project-local 기준서를 runtime prerequisite로 만드는 변경
- executable parser, validator library 또는 scheduler 구현
- dependency 기반 자동 work status 변경, worker 할당, 취소와 acceptance
- global install, plugin packaging, marketplace, publish와 Uptendo 문서 수정

<!-- key: id=key.work.dependency-runtime-implementation.order.behavior refs=key.topic.skill-contract key.topic.work-recovery -->
## 스킬별 동작

1. Author: 관계와 gate 작성 위치, target/step 확인, 본문 동기화와 legacy 신규 작성 금지
2. Reader: 현재 step gate와 전체 dependency 상태 복구, blocker와 unresolved target 보고
3. Linker: `depends_on` normalization, dangling/self/duplicate/stale/cycle 후보와 expanded graph 해석
4. Init: scaffold schema와 최소 dependency consistency 확인, 미래 ID 자동 예약 금지
5. Coordinator: dependency를 실행 순서 제안에 사용하되 자동 상태 변경과 자동 할당 금지
6. Clarify: 자동 전환·취소·dependency 교체처럼 실제 사용자 결정이 필요한 경우에만 처리

<!-- key: id=key.work.dependency-runtime-implementation.order.output-contract refs=key.contract.output key.topic.work-recovery -->
## 공통 판정 계약

Runtime은 dependency 상태를 `satisfied`, `waiting`, `unresolvable`, `invalid`, `unknown`으로
보고한다. 이 판정은 source document의 `work_status`를 직접 수정하지 않는다.

<!-- key: id=key.work.dependency-runtime-implementation.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Source authority: S01에서 수락된 project, artifact graph, bootstrap와 skill 개발 기준
- Required artifacts: Author, Reader, Linker, Init, Coordinator repo-local `SKILL.md`
- Conditional artifact: Clarify `SKILL.md`
- Required behavior: legacy 호환, structured gate 복구, fail-soft 판정, no automatic mutation
- Excluded surfaces: executable code, package/install/publish, consuming-project documents
- Acceptance owner: Main

<!-- key: id=key.work.dependency-runtime-implementation.order.completion refs=key.topic.acceptance key.topic.integration-verification -->
## Completion Criteria

- [x] Author가 `key.relations.depends_on`과 `work_gates`를 수락된 기준대로 작성·검증한다.
- [x] Reader가 현재 step과 전체 작업의 dependency 상태를 복구해 보고한다.
- [x] Linker가 dependency relation과 gate evidence를 구분하고 graph gap을 fail-soft로 보고한다.
- [x] Init이 기본 schema와 최소 consistency를 검사하되 미래 target을 자동 생성하지 않는다.
- [x] Coordinator가 dependency를 순서 제안에 사용하되 자동 mutation을 수행하지 않는다.
- [x] Clarify 변경 여부가 근거와 함께 결정되어 있다.
- [x] 모든 수정 source가 프로젝트 로컬 skill 기준서 없이 자체 완결된다.
- [x] 기존 사용자 변경과 S01 밖의 runtime 의미가 보존되어 있다.
- [x] package/install/publish와 Uptendo 문서는 수정하지 않는다.

<!-- key: id=key.work.dependency-runtime-implementation.order.verification refs=key.topic.verification -->
## Verification

- Repo 기준서와 각 `SKILL.md`의 관계 목록, 상태 이름, 우선순위와 mutation boundary를 비교한다.
- YAML frontmatter, Markdown fence, source 길이와 금지된 legacy 문구를 검사한다.
- `git diff --check`와 변경 파일 scope를 검사한다.
- S03 fixture에서 실행할 대표 runtime input/output 예시를 준비한다.

<!-- key: id=key.work.dependency-runtime-implementation.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. S01 기준 또는 결정이 pending이거나 서로 충돌한다.
2. 실제 parser/scheduler 구현 없이는 runtime 계약을 정직하게 표현할 수 없다.
3. 기존 변경을 보존할 수 없거나 scope 밖 skill source 수정이 필요하다.
4. global installation, packaging 또는 외부 저장소 변경이 필요하다.
