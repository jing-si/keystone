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
- Typed relation
- Metadata admission policy
- Locator와 stable ID 분리
- Mechanical stale과 semantic stale
- Impact candidate 등급

Exclude:

- Skill source 생성
- 실제 code/config/schema/test metadata 작성
- 모든 code symbol을 indexing하는 완전한 code index 설계
- R001 다른 work의 accepted 처리

Conditionally allowed:

- Project Standard와 Linker 기준서 사이의 좁은 cross-reference 보정

<!-- key: id=key.work.artifact-graph-standard.order.source-context refs=key.doc.source key.doc.standard key.topic.artifact-graph -->
## Source Context

- `00_docs/standards/01_key-project-standard.md`
- `00_docs/standards/00_key-index.md`
- `00_docs/standards/artifacts/00_key-index.md`
- `00_docs/standards/artifacts/key-standard-artifact-graph.md`
- `00_docs/works/key-decisions.md`

<!-- key: id=key.work.artifact-graph-standard.order.completion-criteria refs=key.topic.verification key.topic.artifact-graph -->
## Completion Criteria

- [ ] Artifact namespace가 문서, decision, work, capability, code, config, schema, API, test를
      구분한다.
- [ ] Typed relation과 `key.refs`의 책임 차이가 명확하다.
- [ ] Metadata admission policy가 metadata 과다 부여를 막는다.
- [ ] Locator와 stable ID가 분리된다.
- [ ] Mechanical stale과 semantic stale이 구분된다.
- [ ] Impact candidate 등급이 자동 수정이나 자동 acceptance로 해석되지 않는다.

<!-- key: id=key.work.artifact-graph-standard.order.recommended-approach refs=key.topic.artifact-graph key.doc.standard -->
## Recommended Approach

Project Standard에는 상위 원칙만 남기고, Artifact Graph의 상세 기준은 child 기준서에 둔다.

<!-- key: id=key.work.artifact-graph-standard.order.context-pack-seed refs=key.topic.artifact-graph key.output.context-pack -->
## Context Pack Seed

- `STD-KEYSTONE-015`
- `STD-KEYSTONE-017`
- `STD-KEYSTONE-018`
- `DEC-WORKS-006`
- Metadata는 semantic anchor에만 붙인다는 원칙

<!-- key: id=key.work.artifact-graph-standard.order.stop-conditions refs=key.section.stop-conditions key.topic.artifact-graph -->
## Stop Conditions

- Artifact Graph 기준이 실제 code behavior를 대체하는 방향으로 바뀐다.
- 모든 code symbol에 metadata를 붙여야만 설명 가능한 구조가 된다.
- Linker 또는 Coordinator 책임을 기준서가 직접 가져와야 한다.

<!-- key: id=key.work.artifact-graph-standard.order.verification refs=key.topic.verification key.topic.artifact-graph -->
## Verification

Allowed:

- `rg -n "Artifact Graph|Metadata admission|Typed relation|stale|Impact candidate" 00_docs/standards/artifacts`
- Artifact Graph 기준서와 Linker 기준서의 link consistency 확인

<!-- key: id=key.work.artifact-graph-standard.order.expected-output refs=key.contract.output key.topic.artifact-graph -->
## Expected Output

- Artifact Graph 기준서와 색인

<!-- key: id=key.work.artifact-graph-standard.order.review-points refs=key.topic.review key.topic.artifact-graph -->
## Review Points

- Artifact Graph가 code index가 아니라 semantic relation 계층으로 정의되는지 확인한다.
- Metadata 후보가 자동 수정 근거로 해석되지 않는지 확인한다.

<!-- key: id=key.work.artifact-graph-standard.order.progress-record refs=key.topic.progress-update key.step.s06 -->
## Progress Record

S06 완료는 main acceptance 후에만 `key-progress.md`에 기록한다.
