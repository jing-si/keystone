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
  id: key.work.dependency-work-gate-standard.order
  refs:
    - key.doc.work
    - key.topic.artifact-graph
    - key.topic.work-sequence
    - key.topic.work-recovery
    - key.topic.change-set
---

# Dependency and Work Gate Standard 작업서 및 Change Set

<!-- key: id=key.work.dependency-work-gate-standard.order.goal refs=key.section.goal key.topic.artifact-graph -->
## Goal

Keystone의 의미 관계와 작업 실행 조건을 분리하고, 기존 `depends_on` 사용을 보존하면서 단계별
dependency를 기계적으로 복구·해석·검증할 수 있는 권위 있는 기준을 확정한다.

<!-- key: id=key.work.dependency-work-gate-standard.order.findings refs=key.topic.findings key.topic.artifact-graph -->
## 현재 발견사항

- Bootstrap 기준은 `depends_on`을 typed relation 예로 들지만 Artifact Graph와 Linker의 공식
  관계 목록에는 포함하지 않는다.
- Repo-local skill source는 `produced_from`을 사용하지만 Linker normalization 목록과 관계
  모델의 분류가 일치하지 않는다.
- Work-level dependency만으로는 일부 step만 target 완료를 기다리는 pipeline을 표현할 수 없다.
- 단순 work node cycle 검사는 실제로 비순환인 단계별 pipeline을 cycle로 오인할 수 있다.
- Dependency target 상태가 planned, in progress, complete, cancelled 또는 superseded일 때의
  판정 계약이 없다.

<!-- key: id=key.work.dependency-work-gate-standard.order.scope refs=key.section.scope key.topic.artifact-graph -->
## Scope

Include:

- `depends_on`의 관계 방향, 좁은 의미와 impact 해석
- Artifact relation과 execution gate의 책임 분리
- `key.relations.depends_on`과 별도 `work_gates` schema
- 기존 `<!-- keystone: depends_on=... -->` 호환 및 우선순위
- target 존재, duplicate, self-reference, step ID와 cycle 검증
- dependency 판정 상태와 work status의 분리
- cancelled, superseded, missing target의 fail-soft 처리
- `produced_from`과 `revised_by`의 관계 어휘 또는 metadata gap 분류
- Project, Artifact Graph, Bootstrap와 관련 skill 개발 기준서
- 공통 결정 기록, index와 Context Map 동기화

Exclude:

- `skills/keystone-*/SKILL.md` 수정
- 실제 validator executable 또는 parser library 구현
- Uptendo R007/R008 원천 문서 수정
- dependency에 따른 자동 work status 변경, worker 할당, 취소 또는 acceptance
- global skill install, plugin packaging, publish와 기존 corpus 일괄 migration

<!-- key: id=key.work.dependency-work-gate-standard.order.target-model refs=key.topic.keystone-metadata key.topic.work-sequence -->
## 목표 metadata 모델

```yaml
key:
  id: key.work.example
  relations:
    depends_on:
      - target: key.work.target

work_gates:
  - dependency: key.work.target
    applies_to:
      steps: [S08, S09, S10, S11]
      work_completion: true
    condition:
      work_status: complete
    optional: false
```

`key.relations.depends_on`은 의미 관계를, `work_gates`는 source 적용 범위와 target 충족 조건을
소유한다. 긴 이유, 취소 시 대응과 예외는 본문이 소유한다.

<!-- key: id=key.work.dependency-work-gate-standard.order.decisions refs=key.doc.decision key.topic.artifact-graph -->
## 확정할 결정

1. Legacy work-level `depends_on`은 source 시작을 막지 않고 완료 gate 후보로 해석한다.
2. 구조화 metadata와 legacy HTML이 함께 있으면 구조화 metadata를 우선하고 충돌을 보고한다.
3. 없는 target은 정식 dependency가 아니라 unresolved 또는 planned candidate로 보고한다.
4. Dependency 판정은 `satisfied`, `waiting`, `unresolvable`, `invalid`, `unknown`을 사용한다.
5. Dependency 판정만으로 `work_status: blocked`를 자동 기록하지 않는다.
6. Step gate가 있으면 work node가 아닌 expanded event graph에서 cycle을 판정한다.
7. `verifies`, `provides`, `uses`는 work order 사이의 단축 관계보다 명시적 output/test artifact
   node를 우선한다.
8. `produced_from`은 output artifact의 provenance/authority field로 유지하고 Linker가
   선언된 target에서 역방향 `produces` edge를 generated/inferred evidence로 파생한다.
9. `revised_by`는 revision-history evidence로 유지하고 공식 typed relation에 추가하지
   않으며, 정확한 의미가 필요하면 기존 relation·decision·Change Set으로 명시한다.

<!-- key: id=key.work.dependency-work-gate-standard.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: 문서에 존재하지만 runtime이 해석하지 못하는 dependency를 명시적이고 검증 가능한
  계약으로 만든다.
- Required documents: project, artifact graph, bootstrap, Author, Reader, Linker, Init,
  Coordinator 기준서와 공통 결정 기록
- Strong candidate: Clarify 기준서와 runtime source는 사용자 결정 trigger가 달라지는 경우만 검토
- Deferred artifacts: 관련 repo-local `SKILL.md`는 S02에서 반영
- Excluded artifacts: Uptendo source, global install, plugin/package surface, executable validator
- Acceptance owner: Main

<!-- key: id=key.work.dependency-work-gate-standard.order.completion refs=key.topic.acceptance key.topic.verification -->
## Completion Criteria

- [x] `depends_on`의 source, target, 방향과 좁은 의미가 정의되어 있다.
- [x] Artifact relation과 execution gate의 책임 및 저장 위치가 구분되어 있다.
- [x] `work_gates` field와 허용 값, 필수 조합이 정의되어 있다.
- [x] Legacy HTML syntax의 해석과 구조화 metadata 우선순위가 정의되어 있다.
- [x] missing target, duplicate, self-reference, invalid step과 cycle 판정이 정의되어 있다.
- [x] expanded event graph가 work-level false cycle을 피하도록 정의되어 있다.
- [x] dependency 판정과 문서 lifecycle, approval, work status가 분리되어 있다.
- [x] cancelled와 superseded target의 판정 및 사용자/Main 결정 경계가 정의되어 있다.
- [x] `produced_from`의 provenance field·inverse `produces`·missing target 처리가 기록되어 있다.
- [x] `revised_by`의 revision-history evidence·non-relation·ambiguity 처리가 기록되어 있다.
- [x] 관련 기준서, 결정 기록, index와 Context Map이 일관된다.
- [x] 이번 step에서는 `skills/**`를 수정하지 않는다.

<!-- key: id=key.work.dependency-work-gate-standard.order.verification refs=key.topic.verification -->
## Verification

- 관계 목록과 방향을 Project, Bootstrap, Artifact Graph, Linker 기준서 사이에서 비교한다.
- YAML 예시가 field contract와 일치하는지 검사한다.
- 신규 `key.id` duplicate, 문서 path, index link와 step 상태를 검사한다.
- `git diff --check`와 Markdown fence 균형을 검사한다.
- 작업 시작 전후 `skills/**` diff를 비교해 S01 제외 범위를 확인한다.

<!-- key: id=key.work.dependency-work-gate-standard.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. Artifact relation과 execution gate를 분리할 수 없는 새로운 권위 충돌이 발견된다.
2. 사용자만 결정할 수 있는 자동 상태 전환 또는 scheduling 정책이 필요하다.
3. 기존 미완료 변경을 덮어쓰거나 의미를 추정해야 한다.
4. S01 완료를 위해 `skills/**` 또는 실제 validator 구현이 필요하다.
