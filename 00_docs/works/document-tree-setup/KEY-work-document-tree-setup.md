---
doc_type: work_order
key:
  id: key.work.document-tree-setup.order
  refs:
    - key.doc.work
    - key.topic.document-system
    - key.topic.work-sequence
    - key.role.author
---

# Document Tree Setup 작업서(4)

<!-- key: id=key.work.document-tree-setup.order.goal refs=key.doc.work key.topic.document-system key.topic.work-sequence -->
## Goal

`00_docs/works/` 아래에 기준서/기능별 work node를 만들고, 실행 순서를
`00_docs/works/00_KEY-index.md`에서 관리하도록 정리한다.

<!-- key: id=key.work.document-tree-setup.order.scope refs=key.doc.work key.topic.document-system key.section.scope -->
## Scope

Include:

- `00_docs/works/00_KEY-index.md`
- `00_docs/works/KEY-decisions.md`
- S00-S07에 해당하는 work node
- `00_docs/KEY-context-map.md`와 README의 active work link 보정
- Author 기준서의 작업서 생성 표준 보강

Exclude:

- Skill source 생성
- S01-S07 accepted 처리
- `scope.md` 또는 persistent `agent/` 문서 생성
- `00_docs/`와 README 외 파일 변경

Conditionally allowed:

- 링크 일관성을 위한 좁은 기준서 문구 보정

<!-- key: id=key.work.document-tree-setup.order.source-context refs=key.doc.source key.doc.standard key.role.author -->
## Source Context

- `00_docs/KEY-context-map.md`
- `00_docs/standards/00_KEY-project-standard.md`
- `00_docs/standards/skills/author/KEY-standard-author.md`
- `00_docs/works/KEY-decisions.md`

<!-- key: id=key.work.document-tree-setup.order.completion-criteria refs=key.doc.work key.topic.verification key.topic.work-sequence -->
## Completion Criteria

- [ ] S00-S07 work node가 각각 존재한다.
- [ ] 각 work node는 `00_KEY-index.md`, `KEY-work-{slug}.md`, `KEY-progress.md`를 가진다.
- [ ] 실행 순서는 `00_docs/works/00_KEY-index.md`에서 확인된다.
- [ ] umbrella work node가 active work로 남아 있지 않다.
- [ ] stale `work-packages/` 링크가 남아 있지 않다.

<!-- key: id=key.work.document-tree-setup.order.recommended-approach refs=key.doc.work key.topic.document-system -->
## Recommended Approach

Main session이 직접 처리한다. 작업 구조와 progress 기준을 바꾸는 작업이므로 변경 후 링크와
상태를 전체적으로 검증한다.

<!-- key: id=key.work.document-tree-setup.order.context-pack-seed refs=key.doc.work key.topic.document-system key.role.author -->
## Context Pack Seed

- 사용자 승인: work를 step별/기준서별 node로 분리
- `works/00_KEY-index.md`가 순서를 관리한다는 결정
- Author 기준서에 반영할 작업서 생성 표준

<!-- key: id=key.work.document-tree-setup.order.stop-conditions refs=key.doc.work key.section.scope -->
## Stop Conditions

- 삭제하려는 umbrella work에 보존해야 할 unique 정보가 있다.
- 실행 순서와 work identity를 분리할 수 없다.
- `00_docs/`와 README 밖 변경이 필요하다.

<!-- key: id=key.work.document-tree-setup.order.verification refs=key.topic.verification key.doc.work -->
## Verification

Allowed:

- `rg --files 00_docs`
- `rg -n "WP-KEYSTON[E]|work-keystone-skill-syste[m]" 00_docs README.md`
- `git diff --check`
- `rg -n "[ \t]+$" 00_docs README.md`

<!-- key: id=key.work.document-tree-setup.order.expected-output refs=key.doc.work key.topic.document-system key.topic.work-sequence -->
## Expected Output

- 기준서/기능별 work node
- 순서를 관리하는 `works/00_KEY-index.md`
- S00부터 시작하는 개별 progress

<!-- key: id=key.work.document-tree-setup.order.review-points refs=key.topic.review key.doc.work key.topic.document-system -->
## Review Points

- 기준서 구조와 작업 순서가 분리되었는지 확인한다.
- S01-S07이 아직 accepted로 표시되지 않았는지 확인한다.
- 각 work가 하나의 reviewable goal을 가지는지 확인한다.

<!-- key: id=key.work.document-tree-setup.order.progress-record refs=key.topic.progress-update key.doc.work -->
## Progress Record

진행 상태는 `KEY-progress.md`에 기록한다. S00은 main acceptance 후에만 accepted로 표시한다.
