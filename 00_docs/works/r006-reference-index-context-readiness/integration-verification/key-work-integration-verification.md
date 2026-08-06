---
doc_type: work_order
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-06", accepted_by: user}
work_status: planned
key:
  id: key.work.r006-integration-verification.order
  refs: [key.doc.work, key.topic.verification, key.topic.work-recovery, key.topic.finalization, key.topic.change-set]
---

# Integration Verification 작업서 및 Change Set

## Goal

R006 기준·skill·runtime이 사용자에게 내부 관리 명령을 노출하지 않고 신선한 owner/ref context를
제공하며 기존 graph finalization 계약과 함께 동작함을 통합 검증한다.

## Prerequisite

- R006 S03 complete and accepted

## Scope

Include:

- First Reader docs scan, cached reuse와 stale refresh
- Code context 요청의 lazy repository scan와 no-recursion fallback
- Author write 뒤 invalidation과 Coordinator fresh-context reuse
- Multi-agent cache serialization과 temporary installed package parity
- 기존 Author, Linker, runtime-contract regression
- R006 work/round finalization과 global navigation 정합화

Exclude:

- Real global install와 publication
- Browser verification와 external repository pilot
- User-facing cache/index command

## Completion Criteria

- [ ] Cross-skill readiness와 invalidation scenario가 통과한다.
- [ ] Cache failure가 source-authoritative fallback을 깨지 않는다.
- [ ] Temporary install package가 repo-local 계약과 일치한다.
- [ ] 전체 관련 test와 `git diff --check`가 통과한다.
- [ ] R006 S01-S04가 complete and accepted로 finalization된다.

## Stop Conditions

1. S03이 complete and accepted가 아니다.
2. 실제 global install 또는 external repository 변경이 필요하다.
3. Integration failure가 새 high-impact project 의미 결정을 요구한다.
