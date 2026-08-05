---
doc_type: work_round
created_at: "2026-08-05"
status: active
approval:
  state: accepted
  accepted_at: "2026-08-05"
  accepted_by: user
round_status: accepted
key:
  id: key.work.round.r005-artifact-graph-synchronization.index
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.artifact-graph
    - key.topic.keystone-metadata
    - key.topic.finalization
---

# R005 Artifact Graph Synchronization 작업서 색인

이 round는 기준서가 존재하는 Keystone 프로젝트에서 문서 의미와 실제
code/config/schema/API/test 산출물을 capability-first Artifact Graph로 연결하고,
Author·Coordinator·Linker가 graph-relevant 변경을 하나의 검증 가능한 synchronization
lifecycle로 수렴시키는 운영 모델을 기준·runtime·검증에 반영한다. R004가 accepted된 후
시작하며 R004의 accepted 이력은 다시 열지 않는다.

<!-- key: id=key.work.round.r005-artifact-graph-synchronization.execution-order refs=key.topic.work-sequence key.topic.artifact-graph -->
## 실행 순서

Active steps: []

| 순서 | Work | 경로 | 상태 | 목적 |
|---|---|---|---|---|
| S01 | Artifact Graph Synchronization Standard | `artifact-graph-synchronization-standard/00_key-index.md` | accepted | graph mutation authority, surface ownership, metadata와 transaction 계약을 기준서에 확정했다 |
| S02 | Graph Runtime and Validator | `graph-runtime-validator/00_key-index.md` | accepted | parser, adapter, planner, reconciler와 package-owned validator를 구현·검증했다 |
| S03 | Graph Skill Runtime Integration | `graph-skill-runtime-integration/00_key-index.md` | accepted | Author·Coordinator·Linker·Main direct와 finalization runtime을 graph synchronization lifecycle에 연결했다 |
| S04 | Graph Integration Verification | `graph-integration-verification/00_key-index.md` | accepted | Keystone 저장소 내부의 합성 fixture와 package CLI로 graph lifecycle을 통합 검증했다 |

<!-- key: id=key.work.round.r005-artifact-graph-synchronization.reading-rules refs=key.topic.work-recovery key.topic.artifact-graph -->
## 읽기 규칙

1. R005는 accepted이며 active Step이 없다.
2. S01 수락 전 S02~S04 구현을 시작하지 않는다.
3. R004는 accepted 선행 round로 읽고 그 작업 기록을 소급 수정하지 않는다.
4. 공통 방향은 `00_docs/works/key-decisions.md`의 `DEC-WORKS-024`를 따른다.
5. 현재 transaction 완결성과 프로젝트 전체 graph coverage를 구분한다.

<!-- key: id=key.work.round.r005-artifact-graph-synchronization.boundaries refs=key.boundary.scope-control key.topic.artifact-graph -->
## Round 경계

- Keystone 자체의 범용 graph synchronization 계약과 runtime만 다룬다.
- Uptendo를 포함한 외부 소비 프로젝트의 source·문서·migration을 직접 수정하거나 fixture로
  복사하지 않는다.
- 외부 프로젝트 검증은 R005 acceptance 조건이 아니며, 실제 사용에서 발견한 새 문제는 후속
  corrective round로 다룬다.
- 별도 중앙 graph registry를 source of truth로 도입하지 않는다.
- 모든 파일·symbol에 metadata를 강제하거나 기존 corpus를 일괄 migration하지 않는다.
- Global install, plugin publishing과 marketplace 등록은 범위 밖이다.
