---
doc_type: work_round
created_at: "2026-08-25"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-25", accepted_by: main}
round_status: accepted
key:
  id: key.work.round.r016-worktree-locator-navigation.index
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.work-recovery
    - key.topic.work-execution
    - key.topic.keystone-metadata
    - key.topic.skill-contract
    - key.topic.verification
    - key.boundary.scope-control
    - key.work.decisions.dec-works-033
---

# R016 Worktree Locator and Targeted Work Discovery 작업서 색인

R016은 Coordinator가 구현 환경으로 Git worktree를 생성하거나 선택한 경우 그 실제 경로를
코드 수정 전에 canonical Work Order 키메타에 기록하고, Reader와 실행자가 기록된 경로만
직접 탐색하도록 계약을 정렬한다.

이 Round는 S01~S03의 기준서, skill runtime, parser와 regression을 완료하고 Main acceptance를
거쳐 `complete / accepted`로 닫혔다. Active R015의 상태나 범위는 변경하지 않았다.

<!-- key: id=key.work.round.r016.execution-order refs=key.topic.work-sequence key.topic.work-execution -->
## 실행 순서

| 순서 | Step | 상태 | 목적 |
|---|---|---|---|
| S01 | Worktree Locator Policy and Metadata Contract | accepted | `key.worktree.path`, 기록 owner, canonical source와 omission/stale 경계를 기준서에 정의했다 |
| S02 | Coordinator, Author, Reader and Parser Integration | accepted | worktree 생성·기록·재확인 gate와 locator 기반 직접 탐색을 skill runtime과 metadata parser에 구현했다 |
| S03 | Targeted Discovery Verification and Closure | accepted | 전역 worktree scan 부재, owner 분리, stale/missing locator와 기존 workflow 보존을 focused regression으로 검증했다 |

- Active Step: 없음

세부 Goal, Scope, completion criteria와 검증 계획은 Work Order에서, 실제 상태와 resume point는
aggregate Progress에서 확인한다.

<!-- key: id=key.work.round.r016.boundaries refs=key.boundary.scope-control key.topic.work-execution -->
## Round 경계

- Worktree 사용 자체, branch 전략, writer 수나 integration 전략을 강제하지 않는다.
- Worktree가 선택된 Work에만 `key.worktree.path` 기록을 요구한다.
- 전체 worktree 열거, repository-wide 자동 탐색, atomic claim과 lock registry는 도입하지 않는다.
- 기록 누락으로 발견하지 못한 별도 worktree는 사용자 기억에 의존하는 운영 위험으로 남긴다.
- R014와 R015의 source, 상태, 우선순위와 accepted history를 변경하지 않는다.

<!-- key: id=key.work.round.r016.reading-rules refs=key.topic.work-recovery key.topic.work-sequence -->
## 복구 규칙

1. R016 목표와 Step 상태는 이 Index에서 확인한다.
2. 정책 방향, 변경 surface, completion criteria와 stop condition은 Work Order를 읽는다.
3. 실제 실행 상태, 검증 evidence와 resume point는 Progress를 읽는다.
4. Accepted history, verification과 residual risk는 Step/aggregate Progress에서 확인한다.
