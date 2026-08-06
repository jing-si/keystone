---
doc_type: work_order
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-06", accepted_by: user}
work_status: planned
key:
  id: key.work.index-runtime-implementation.order
  refs: [key.doc.work, key.topic.artifact-graph, key.topic.work-recovery, key.topic.verification, key.topic.change-set]
---

# Index Runtime Implementation 작업서 및 Change Set

## Goal

Reader와 Linker가 source authority를 침범하지 않고 docs-scope와 repository-scope owner/ref를
탐색하도록 package-internal Python runtime을 구현한다.

## Prerequisite

- R006 S02 complete and accepted

## Scope

Include:

- Unique owner, reverse ref, duplicate/dangling diagnostic model
- Docs-only와 lazy repository scanner
- Path-set + raw-byte digest freshness와 worktree identity
- Caller-supplied external SQLite cache, single writer와 fail-soft recovery
- Optional typed subgraph와 serialized recursion guard
- Immutable internal result API와 TDD

Exclude:

- Repository-local cache, central graph DB와 user-facing command
- Automatic source edit 또는 acceptance
- External consumer repository

## Completion Criteria

- [ ] Source-only reconstruction과 unique owner/ref lookup이 동작한다.
- [ ] Dirty/untracked/path-set 변경이 freshness를 무효화한다.
- [ ] Corrupt/missing cache는 source fallback으로 복구된다.
- [ ] Typed graph는 요청할 때만 materialize된다.
- [ ] Reader↔Linker recursion이 차단된다.
- [ ] 기존 Linker test가 함께 통과한다.

## Stop Conditions

1. S02가 complete and accepted가 아니다.
2. Source write 또는 persistent repository state가 필요하다.
3. External DB나 PATH command가 필수로 요구된다.
