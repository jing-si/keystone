---
doc_type: work_order
key:
  id: key.work.artifact-graph-standard.order
  refs:
    - key.doc.work
    - key.topic.artifact-graph
    - key.topic.keystone-metadata
    - key.topic.code-anchor
    - key.topic.impact-review
---

# Artifact Graph Standard 작업서(4)

<!-- key: id=key.work.artifact-graph-standard.order.goal refs=key.topic.artifact-graph key.doc.standard key.section.goal -->
## Goal

`00_docs/standards/artifacts/key-standard-artifact-graph.md`를 Artifact Graph의 공식 child 기준서로
정리한다.

<!-- key: id=key.work.artifact-graph-standard.order.scope refs=key.topic.artifact-graph key.section.scope -->
## Scope

Include:

- Artifact namespace
- Graph ownership boundary
- Graph source surface
- Graph record model
- Typed relation
- Relation direction and propagation
- Metadata admission policy
- Locator와 stable ID 분리
- Mechanical stale, semantic stale, metadata gap
- Capability node 생성 기준
- Artifact lifecycle과 replacement policy
- Impact candidate 등급
- Generated graph index 초기 read-only policy

Exclude:

- Skill source 생성
- 실제 code/config/schema/API/test metadata 작성
- 모든 code symbol을 indexing하는 완전한 code index 설계
- R001 다른 work의 accepted 처리
- Linker가 source document나 code/config/schema/API/test surface를 직접 수정하도록 권한 부여

Conditionally allowed:

- Project Standard와 Linker 기준서 사이의 좁은 cross-reference 보정
- S06 ownership boundary를 보존하기 위한 Author, Coordinator 기준서의 좁은 경계 문구 보정

<!-- key: id=key.work.artifact-graph-standard.order.source-context refs=key.doc.source key.doc.standard key.topic.artifact-graph -->
## Source Context

- `00_docs/standards/01_key-project-standard.md`
- `00_docs/standards/00_key-index.md`
- `00_docs/standards/artifacts/00_key-index.md`
- `00_docs/standards/artifacts/key-standard-artifact-graph.md`
- `00_docs/standards/skills/linker/key-standard-linker.md`
  - S07에서 최종 정리될 기준서이므로 S06에서는 ownership consistency reference로 사용한다.
- `00_docs/standards/skills/author/key-standard-author.md`
- `00_docs/standards/skills/coordinator/key-standard-coordinator.md`
- `00_docs/works/key-decisions.md`

<!-- key: id=key.work.artifact-graph-standard.order.completion-criteria refs=key.topic.verification key.topic.artifact-graph -->
## Completion Criteria

- [ ] Artifact namespace가 문서, decision, work, capability, code, config, schema, API, test를
      구분한다.
- [ ] Linker의 graph interpretation ownership과 source edit authority가 분리된다.
- [ ] Source document metadata 변경은 Author, code/config/schema/API/test anchor 변경은 Coordinator로
      handoff된다는 기준이 명확하다.
- [ ] Graph source surface와 conceptual record model이 Linker report와 worker assignment context에
      같은 의미로 쓰일 수 있다.
- [ ] Typed relation과 `key.refs`의 책임 차이가 명확하다.
- [ ] Relation direction과 propagation 기준만 보고 Linker가 candidate 등급을 일관되게 판단할 수
      있다.
- [ ] Metadata admission policy가 metadata 과다 부여를 막는다.
- [ ] Capability node 생성 기준이 code symbol alias 양산을 막는다.
- [ ] Locator와 stable ID가 분리된다.
- [ ] Mechanical stale, semantic stale, metadata gap이 구분된다.
- [ ] Replacement relation과 alias policy가 source relation 중복을 만들지 않는다.
- [ ] Impact candidate 등급이 자동 수정이나 자동 acceptance로 해석되지 않는다.
- [ ] Generated graph index는 초기 단계에서 source of truth나 Linker write target으로 해석되지
      않는다.

<!-- key: id=key.work.artifact-graph-standard.order.recommended-approach refs=key.topic.artifact-graph key.doc.standard -->
## Recommended Approach

Project Standard에는 상위 원칙만 남기고, Artifact Graph의 상세 기준은 child 기준서에 둔다.

<!-- key: id=key.work.artifact-graph-standard.order.context-pack-seed refs=key.topic.artifact-graph key.output.context-pack -->
## Context Pack Seed

- `STD-KEYSTONE-015`
- `STD-KEYSTONE-017`
- `STD-KEYSTONE-018`
- `DEC-WORKS-006`
- `DEC-WORKS-009`
- Metadata는 semantic anchor에만 붙인다는 원칙
- Linker owns graph interpretation, not graph source mutation
- Source document metadata는 Author, code/config/schema/API/test anchor는 Coordinator가 반영한다는
  surface boundary

<!-- key: id=key.work.artifact-graph-standard.order.stop-conditions refs=key.section.stop-conditions key.topic.artifact-graph -->
## Stop Conditions

- Artifact Graph 기준이 실제 code behavior를 대체하는 방향으로 바뀐다.
- 모든 code symbol에 metadata를 붙여야만 설명 가능한 구조가 된다.
- Linker가 source edit authority를 가져야만 설명 가능한 구조가 된다.
- Coordinator가 Linker 없이 artifact relation, impact candidate, stale candidate, metadata gap을 확정해야 하는
  구조가 된다.

<!-- key: id=key.work.artifact-graph-standard.order.verification refs=key.topic.verification key.topic.artifact-graph -->
## Verification

Allowed:

- `rg -n "Artifact Graph|Metadata admission|Typed relation|stale|Impact candidate" 00_docs/standards/artifacts`
- `rg -n "Artifact Graph ownership boundary|Metadata gap|Relation direction|Generated graph index" 00_docs/standards/artifacts/key-standard-artifact-graph.md`
- `rg -n "source_surface_handoffs|graph_interpretation|operational graph interpretation" 00_docs/standards/skills/linker/key-standard-linker.md`
- Artifact Graph 기준서와 Linker 기준서의 link consistency 확인

<!-- key: id=key.work.artifact-graph-standard.order.expected-output refs=key.contract.output key.topic.artifact-graph -->
## Expected Output

- Artifact Graph 기준서와 색인

<!-- key: id=key.work.artifact-graph-standard.order.review-points refs=key.topic.review key.topic.artifact-graph -->
## Review Points

- Artifact Graph가 code index가 아니라 semantic relation 계층으로 정의되는지 확인한다.
- Metadata 후보가 자동 수정 근거로 해석되지 않는지 확인한다.
- Linker가 graph interpretation owner로 남고 source edit owner가 되지 않는지 확인한다.
- S06이 graph model 기준을 정의하고 S07이 graph 접근, 해석, report, handoff 기준을 다루는지
  확인한다.

<!-- key: id=key.work.artifact-graph-standard.order.progress-record refs=key.topic.progress-update key.step.s06 -->
## Progress Record

S06 완료는 main acceptance 후에만 `key-progress.md`에 기록한다.
