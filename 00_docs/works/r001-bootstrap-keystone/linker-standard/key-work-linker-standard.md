---
doc_type: work_order
key:
  id: key.work.linker-standard.order
  refs:
    - key.doc.work
    - key.role.linker
    - key.topic.artifact-graph
    - key.topic.impact-review
    - key.topic.stale-review
---

# Linker Standard 작업서(4)

<!-- key: id=key.work.linker-standard.order.goal refs=key.role.linker key.topic.artifact-graph key.section.goal -->
## Goal

`keystone-linker`의 read-only artifact discovery, impact analysis, stale/gap review, worker
assignment seed 계약을 정리한다.

<!-- key: id=key.work.linker-standard.order.scope refs=key.role.linker key.section.scope key.topic.impact-review -->
## Scope

Include:

- Linker trigger와 non-trigger
- Operational graph interpretation ownership
- Artifact Discovery, Impact Analysis, Stale/Gap Review, Worker Assignment Seed mode
- `linker_report` output contract
- metadata parsing and normalization rule
- relation direction and propagation 적용
- Author, Reader, Coordinator handoff boundary
- source surface별 handoff owner 분류
- Metadata gap과 stale candidate 보고
- Reuse candidate와 test candidate 보고

Exclude:

- 원천 문서 직접 수정
- code/config/schema/API/test implementation
- code/config/schema/API/test anchor 직접 수정
- worker assignment 실제 배정
- high-impact decision 질문 수집

Conditionally allowed:

- Artifact Graph 기준서와 Coordinator 기준서 사이의 좁은 cross-reference 보정

<!-- key: id=key.work.linker-standard.order.source-context refs=key.doc.source key.doc.standard key.role.linker -->
## Source Context

- `00_docs/standards/01_key-project-standard.md`
- `00_docs/standards/artifacts/00_key-index.md`
- `00_docs/standards/artifacts/key-standard-artifact-graph.md`
- `00_docs/standards/skills/linker/00_key-index.md`
- `00_docs/standards/skills/linker/key-standard-linker.md`
- `00_docs/works/key-decisions.md`

<!-- key: id=key.work.linker-standard.order.completion-criteria refs=key.topic.verification key.role.linker key.contract.output -->
## Completion Criteria

- [ ] Linker trigger와 non-trigger가 명확하다.
- [ ] Linker가 Artifact Graph의 operational interpretation owner이며 source edit authority를
      가지지 않는다는 경계가 명확하다.
- [ ] 네 mode의 목적과 output focus가 구분된다.
- [ ] Linker가 원천 문서(2), code, config, schema, API, test를 직접 수정하지 않는다는 경계가 명확하다.
- [ ] `linker_report`가 Coordinator worker assignment의 artifact context seed로 사용될 수 있다.
- [ ] `linker_report`가 Author, Coordinator, Main/Clarify handoff를 source surface별로 분리한다.
- [ ] Markdown key metadata와 code anchor parsing surface가 명확하다.
- [ ] Metadata gap, mechanical stale, semantic stale 후보가 구분된다.
- [ ] `candidate_budget`이 적용될 때 `required` 후보를 숨기지 않고 `omitted_summary`로 생략
      근거를 남긴다.
- [ ] 후보 발견이 자동 수정이나 자동 acceptance로 해석되지 않는다.

<!-- key: id=key.work.linker-standard.order.recommended-approach refs=key.role.linker key.topic.responsibility-boundary -->
## Recommended Approach

Linker는 artifact graph 해석과 후보 보고에 집중한다. 문서 반영은 Author, worker assignment와
report 회수는 Coordinator 책임으로 남긴다.

<!-- key: id=key.work.linker-standard.order.context-pack-seed refs=key.role.linker key.output.context-pack -->
## Context Pack Seed

- `STD-KEYSTONE-044`
- `DEC-WORKS-009`
- Artifact Graph 기준서
- Metadata parsing rule
- Relation direction and propagation rule
- Source surface handoff owner
- Candidate budget과 omitted summary rule
- Reader context brief handoff
- Author Change Set handoff
- Coordinator worker assignment seed

<!-- key: id=key.work.linker-standard.order.stop-conditions refs=key.section.stop-conditions key.role.linker key.boundary.read-only -->
## Stop Conditions

- Linker가 문서나 code를 직접 수정해야만 설명 가능한 구조가 된다.
- metadata parsing rule이 required impact relation을 과도하게 확정한다.
- Linker graph interpretation ownership이 source edit authority로 해석된다.
- candidate budget이 `required` 후보를 숨기거나 생략 근거를 잃게 만든다.
- 후보 등급화가 자동 수정 또는 자동 acceptance로 해석된다.
- Worker assignment 배정 책임이 Linker로 넘어간다.

<!-- key: id=key.work.linker-standard.order.verification refs=key.topic.verification key.role.linker -->
## Verification

Allowed:

- `rg -n "Artifact Discovery|Impact Analysis|Stale/Gap Review|linker_report" 00_docs/standards/skills/linker`
- `rg -n "Metadata parsing rule|key.refs|keystone:|metadata_gaps" 00_docs/standards/skills/linker/key-standard-linker.md`
- `rg -n "candidate_budget|omitted_summary|required" 00_docs/standards/skills/linker/key-standard-linker.md`
- `rg -n "source_surface_handoffs|graph_interpretation|operational graph interpretation" 00_docs/standards/skills/linker/key-standard-linker.md`
- Linker 기준서와 Artifact Graph 기준서의 link와 scope consistency 확인

<!-- key: id=key.work.linker-standard.order.expected-output refs=key.contract.output key.role.linker -->
## Expected Output

- `keystone-linker` 기준서와 색인

<!-- key: id=key.work.linker-standard.order.review-points refs=key.topic.review key.role.linker key.topic.responsibility-boundary -->
## Review Points

- Linker가 Reader나 Coordinator 책임을 흡수하지 않는지 확인한다.
- Linker report가 후보와 evidence로 남고 수정 권한으로 해석되지 않는지 확인한다.
- metadata parsing 결과가 declared, observed, inferred evidence를 구분하는지 확인한다.
- Linker가 graph interpretation owner로 남고 Author/Coordinator의 source edit authority를
  대체하지 않는지 확인한다.

<!-- key: id=key.work.linker-standard.order.progress-record refs=key.topic.progress-update key.step.s07 -->
## Progress Record

S07 완료는 main acceptance 후에만 `key-progress.md`에 기록한다.
