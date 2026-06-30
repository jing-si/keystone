---
doc_type: work_order
key:
  id: key.work.author-standard.order
  refs:
    - key.doc.work
    - key.role.author
    - key.topic.document-authoring
    - key.topic.work-creation
    - key.boundary.approval
---

# Author Standard 작업서(4)

<!-- key: id=key.work.author-standard.order.goal refs=key.role.author key.topic.document-authoring key.topic.work-creation key.section.goal -->

## Goal

`keystone-author`의 문서 작성/수정 계약과 작업서 생성 표준을 정리한다.

<!-- key: id=key.work.author-standard.order.scope refs=key.role.author key.section.scope key.doc.standard key.doc.work key.boundary.approval -->

## Scope

Include:

- Create, Revise, Clarify-Apply, Normalize, Progress Update mode
- 기준서(3) 작성 규칙
- 작업서(4) 생성 표준
- index와 progress update boundary
- approval boundary와 source edit gate

Exclude:

- high-impact decision collection
- implementation code
- persistent handoff 기본 생성

Conditionally allowed:

- 작업서 생성 표준을 반영하기 위한 root works index와 round index link 보정

<!-- key: id=key.work.author-standard.order.source-context refs=key.section.source-context key.role.author key.doc.standard key.doc.decision-record -->

## Source Context

- `00_docs/standards/01_key-project-standard.md`
- `00_docs/standards/skills/author/00_key-index.md`
- `00_docs/standards/skills/author/key-standard-author.md`
- `00_docs/works/key-decisions.md`

<!-- key: id=key.work.author-standard.order.completion-criteria refs=key.topic.acceptance key.role.author key.topic.work-creation key.topic.responsibility-boundary -->

## Completion Criteria

- [ ] Author가 새 작업서를 `works/` tree에 만든다는 점이 명확하다.
- [ ] 작업서가 기준서 구조에 종속되지 않는다는 표준이 명확하다.
- [ ] 작업 순서는 기준서가 아니라 active round index나 상위 work plan이 관리한다.
- [ ] progress update가 main acceptance와 worker report를 혼동하지 않는다.
- [ ] Clarify와 Author의 책임 경계가 명확하다.

<!-- key: id=key.work.author-standard.order.recommended-approach refs=key.section.recommended-approach key.role.author key.topic.document-authoring key.topic.responsibility-boundary -->

## Recommended Approach

Author 기준서는 문서 작성 책임에 집중한다. Clarify 질문 수집이나 Coordinator runtime flow는
가져오지 않는다.

<!-- key: id=key.work.author-standard.order.context-pack-seed refs=key.output.context-pack key.standard.project.std-keystone-042 key.work.decisions.dec-works-002 key.boundary.source-edit-gate -->

## Context Pack Seed

- `STD-KEYSTONE-042`
- `DEC-WORKS-002`
- Source edit gate와 approval boundary

<!-- key: id=key.work.author-standard.order.stop-conditions refs=key.section.stop-conditions key.boundary.approval key.boundary.source-edit-gate key.boundary.scope-control -->

## Stop Conditions

- 승인 없이 scope, acceptance criteria, status semantics를 바꿔야 한다.
- Author가 code/schema/generated output을 수정해야 한다.
- 작업서 생성 표준이 기준서 실행 순서를 고정하게 만든다.

<!-- key: id=key.work.author-standard.order.verification refs=key.topic.verification key.role.author key.topic.standard-verification -->

## Verification

Allowed:

- `rg -n "작업서 생성|works/00_key-index|기준서 구조" 00_docs/standards/skills/author/key-standard-author.md`
- Author 기준서와 Project Standard의 work model consistency 확인

<!-- key: id=key.work.author-standard.order.expected-output refs=key.contract.output key.role.author key.topic.work-creation key.doc.standard -->

## Expected Output

- 작업서 생성 표준이 포함된 Author 기준서

<!-- key: id=key.work.author-standard.order.review-points refs=key.section.review-points key.role.author key.boundary.approval key.topic.work-sequence -->

## Review Points

- Author가 approved source document edit만 수행하도록 제한되는지 확인한다.
- 작업서 생성 위치와 순서 관리 위치가 분리되어 있는지 확인한다.

<!-- key: id=key.work.author-standard.order.progress-record refs=key.topic.progress-update key.topic.main-acceptance key.step.s03 -->

## Progress Record

S03 완료는 main acceptance 후에만 `key-progress.md`에 기록한다.
