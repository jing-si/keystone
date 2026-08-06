---
doc_type: work_round
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-06", accepted_by: user}
round_status: in_progress
key:
  id: key.work.round.r006-reference-index-context-readiness.index
  refs: [key.doc.work, key.topic.work-round, key.topic.work-sequence, key.topic.artifact-graph, key.topic.work-recovery]
---

# R006 Reference Index and Context Readiness 작업서 색인

R006은 source-owned stable ID와 ref를 기본 탐색 계약으로 복구하고, Reader의 docs-first context
readiness와 Linker의 외부 파생 index를 연결한다. Typed graph는 의미 탐색이 필요한 경우에,
graph transaction은 multi-surface 변경에만 사용한다. R003-R005 accepted 기록은 변경하지 않는다.

<!-- key: id=key.work.round.r006.execution-order refs=key.topic.work-sequence key.topic.work-recovery -->
## 실행 순서

Active steps: [S04]

| 순서 | Work | 경로 | 상태 | 목적 |
|---|---|---|---|---|
| S01 | Reference Index Contract Standard | `reference-index-contract-standard/00_key-index.md` | complete | accepted — owner/ref-first identity, 상태·검증·상속·readiness 계약을 전체 기준서에 확정했다 |
| S02 | Skill Context Contract Integration | `skill-context-contract-integration/00_key-index.md` | complete | accepted — Reader·Linker·Author·Coordinator installed skill 계약을 기준서와 동기화했다 |
| S03 | Index Runtime Implementation | `index-runtime-implementation/00_key-index.md` | complete | accepted — 외부 파생 owner/ref index, freshness와 lazy graph runtime을 구현했다 |
| S04 | Integration Verification | `integration-verification/00_key-index.md` | in_progress | cross-skill 흐름과 설치 package layout을 검증하고 round를 finalization한다 |

<!-- key: id=key.work.round.r006.reading-rules refs=key.topic.work-recovery key.topic.artifact-graph -->
## 읽기 규칙

1. 현재 active Step은 S04이다.
2. S01-S03은 complete and accepted이며 S04 검증과 finalization만 남아 있다.
3. 공통 방향은 `00_docs/works/key-decisions.md`의 `DEC-WORKS-025`를 따른다.
4. R003-R005의 accepted 기록은 역사적 evidence로 읽고 R006에서 소급 수정하지 않는다.
5. Owner/ref index는 source of truth가 아니라 재생성 가능한 외부 파생물이다.

<!-- key: id=key.work.round.r006.boundaries refs=key.boundary.scope-control key.topic.runtime-independence -->
## Round 경계

- Keystone repository의 기준서, repo-local skill source와 package-owned runtime만 다룬다.
- User-facing global CLI, 외부 DB, global install, publication과 외부 소비 repository는 범위 밖이다.
- Reader와 Linker는 repository source를 수정하지 않는다.
- Typed graph를 모든 artifact에 강제하거나 기존 corpus를 일괄 migration하지 않는다.
