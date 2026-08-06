---
doc_type: work_order
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-06", accepted_by: user}
work_status: planned
key:
  id: key.work.skill-context-contract-integration.order
  refs: [key.doc.work, key.topic.skill-contract, key.topic.work-recovery, key.topic.change-set]
---

# Skill Context Contract Integration 작업서 및 Change Set

## Goal

Accepted S01 기준을 self-contained installed skill 계약에 반영해 Reader가 세션 orientation과
docs-scope readiness를 시작하고 Linker가 내부 index enrichment를 안전하게 수행하도록 한다.

## Prerequisite

- R006 S01 complete and accepted

## Scope

Include:

- Reader, Linker, Author, Coordinator skill source와 필요한 Init/Clarify 정합화
- Docs-first readiness, lazy repository enrichment, freshness와 recursion guard 계약
- Cache/source authority, fail-soft fallback와 hidden internal payload
- Contract test와 기존 runtime contract regression

Exclude:

- Index executable runtime 구현
- 실제 global skill installation
- User-facing CLI나 source cache file

## Completion Criteria

- [ ] 관련 skill source가 S01 기준과 일치한다.
- [ ] Permissionless Linker 호출이 Coordinator authority를 확장하지 않는다.
- [ ] Readiness payload와 cache는 사용자에게 기본 노출되지 않는다.
- [ ] Contract와 regression test가 통과한다.

## Stop Conditions

1. S01이 complete and accepted가 아니다.
2. Skill 계약이 source write 또는 새 user decision을 요구한다.
3. Runtime 구현 없이는 계약을 명세할 수 없는 새 범위가 발견된다.
