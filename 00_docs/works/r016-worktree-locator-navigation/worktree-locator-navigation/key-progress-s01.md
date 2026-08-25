---
doc_type: progress
created_at: "2026-08-25"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-25", accepted_by: main}
work_status: complete
step_ref: R016/S01
work_ref: R016/worktree-locator-navigation
key:
  id: key.work.worktree-locator-navigation.progress.s01
  refs:
    - key.work.worktree-locator-navigation.order
    - key.standard.project.std-keystone-061
    - key.standard.artifact.graph.worktree-navigation-metadata
    - key.standard.skill.reader.context-readiness
    - key.standard.skill.author.worktree-locator-writing
    - key.standard.skill.coordinator.worktree-locator-gate
    - key.standard.subagent.execution-environment
    - key.acceptance.worktree-locator.owner-sequence
    - key.acceptance.worktree-locator.targeted-reader
    - key.acceptance.worktree-locator.absent-policy
    - key.acceptance.worktree-locator.stale-policy
    - key.acceptance.worktree-locator.strategy-retained
    - key.acceptance.worktree-locator.no-locking
---

# R016/S01 Worktree Locator Policy and Metadata Contract 진행 기록

## 결과

- Work status: `complete`
- Approval state: `accepted`
- 변경: Project·Artifact Graph·Reader·Author·Coordinator·Subagent 기준서에 Worktree 비강제,
  `key.worktree.path` shape, Coordinator→Author→fresh confirmation gate, exact-path navigation,
  missing/stale no-global-scan과 user-memory residual risk를 정렬했다.
- 실행 위치: primary worktree를 사용해 R016 Work Order에는 `key.worktree`를 추가하지 않았다.
- 검증: Linker docs-first readiness `pass`, 225/225 parsed, error 0, affected-source structural
  diagnostic 0. `git diff --check` 통과.
- Resume point: 완료. S02 skill runtime과 Linker metadata parser 구현으로 이어졌다.
