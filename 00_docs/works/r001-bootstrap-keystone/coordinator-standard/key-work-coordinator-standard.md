---
doc_type: work_order
key:
  id: key.work.coordinator-standard.order
  refs:
    - key.doc.work
    - key.role.coordinator
    - key.role.subagent
    - key.standard.subagent
    - key.topic.orchestration
    - key.topic.acceptance
---

# Coordinator Standard 작업서(4)

<!-- key: id=key.work.coordinator-standard.order.goal refs=key.role.coordinator key.topic.main-supervised key.role.subagent key.topic.workflow key.section.goal -->

## Goal

`keystone-coordinator`의 main-supervised bounded worker workflow 계약을 정리한다.

<!-- key: id=key.work.coordinator-standard.order.scope refs=key.role.coordinator key.section.scope key.output.current-step-brief key.output.context-pack key.topic.report-handling key.doc.derived-agent key.standard.subagent -->

## Scope

Include:

- Current Step Brief와 Context Pack 구성
- subagent 기준서 기반 purpose preset, authority, injected skill contract routing
- default bounded worker contract
- worker assignment와 worker report contract
- Main context checkpoint
- source conflict와 stale work order reason code
- single workspace guard
- report handling
- review, verification, repair, escalation, acceptance flow
- progress/report status 분리
- derived agent document policy

Exclude:

- 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 기록 작성 자체
- high-risk implementation 자동 위임
- persistent handoff 기본 생성
- 추가 subagent 생성 허용
- 별도 작업 격리 또는 통합 절차

Conditionally allowed:

- current work step field와 Coordinator runtime output 사이의 link 보정

<!-- key: id=key.work.coordinator-standard.order.source-context refs=key.section.source-context key.role.coordinator key.doc.standard key.work.index key.standard.subagent -->

## Source Context

- `00_docs/standards/01_key-project-standard.md`
- `00_docs/standards/subagents/key-standard-subagents.md`
- `00_docs/standards/skills/coordinator/00_key-index.md`
- `00_docs/standards/skills/coordinator/key-standard-coordinator.md`
- `00_docs/works/key-decisions.md`
- `00_docs/works/00_key-index.md`
- `00_docs/works/r001-bootstrap-keystone/00_key-index.md`

<!-- key: id=key.work.coordinator-standard.order.completion-criteria refs=key.topic.acceptance key.role.coordinator key.topic.current-step key.topic.worker-handoff key.topic.reviewer-focus key.standard.subagent -->

## Completion Criteria

- [ ] Coordinator가 current step과 completion criteria를 복구할 수 있다.
- [ ] Purpose preset, authority, injected skill contract는 subagent 기준서를 따른다.
- [ ] Domain-specific injected skill이 없으면 `keystone-default-bounded-worker` contract를
      사용한다.
- [ ] Scope가 worker handoff boundary로 변환된다.
- [ ] Worker assignment가 goal, authority, scope, workspace guard, stop condition,
      return report contract를 포함한다.
- [ ] Current Step Brief와 worker report review가 Main context checkpoint를 통해 global intent,
      accepted decision, current work identity, preserved boundary를 확인할 수 있다.
- [ ] Source conflict, stale work order, stale progress record, accepted decision propagation
      누락이 reason code와 review focus로 분리된다.
- [ ] Worker report가 report handling, review, verification, repair, escalation 판단으로 이어진다.
- [ ] Single workspace에서 한 번에 하나의 file-writing worker만 허용된다.
- [ ] Worker가 전체 작업서(4)를 재해석하거나 scope를 확장하거나 추가 subagent를 생성하지 않는다.
- [ ] Worker `DONE`과 Main acceptance가 분리된다.
- [ ] Main acceptance 전에는 accepted로 표시하지 않는다.

<!-- key: id=key.work.coordinator-standard.order.recommended-approach refs=key.section.recommended-approach key.role.coordinator key.topic.orchestration key.topic.responsibility-boundary -->

## Recommended Approach

Coordinator 기준서는 runtime orchestration에 집중한다. 문서 수정이나 결정 수집은 Author와
Clarify로 남긴다. Worker는 주입된 skill contract 안에서 local planning을 할 수 있지만,
Coordinator 역할이나 Main acceptance를 대체하지 않는다.

<!-- key: id=key.work.coordinator-standard.order.context-pack-seed refs=key.output.context-pack key.standard.project.std-keystone-043 key.topic.progress-status key.boundary.high-risk-work key.standard.subagent -->

## Context Pack Seed

- `STD-KEYSTONE-032`
- `STD-KEYSTONE-043`
- `00_docs/standards/subagents/key-standard-subagents.md`
- purpose preset, authority, injected skill contract, default bounded worker contract
- Main context checkpoint
- source conflict reason code
- single workspace guard
- progress/report status rule
- high-risk work stop condition

<!-- key: id=key.work.coordinator-standard.order.stop-conditions refs=key.section.stop-conditions key.topic.current-step key.topic.subagent-sizing key.boundary.high-risk-work key.standard.subagent -->

## Stop Conditions

- current step이 복구되지 않는다.
- work unit이 bounded worker assignment로 자를 수 없다.
- high-risk implementation이 main/user decision 없이 필요하다.
- worker authority, scope, injected skill contract, stop condition이 불명확하다.
- domain-specific injected skill이 없는데 default bounded worker contract도 없다.
- accepted decision이 관련 work order나 progress record에 전파되지 않아 current task 방향을
  바꿀 수 있다.
- file-writing worker가 필요한데 single workspace guard가 없다.
- 여러 file-writing worker를 동시에 배정해야만 진행할 수 있다.
- 기존 사용자 변경이나 다른 agent 변경을 덮어쓸 위험이 있다.

<!-- key: id=key.work.coordinator-standard.order.verification refs=key.topic.verification key.role.coordinator key.topic.standard-verification -->

## Verification

Allowed:

- `rg -n "Worker assignment|worker_report|single workspace|injected skill|accepted" 00_docs/standards/skills/coordinator/key-standard-coordinator.md`
- `rg -n "keystone-default-bounded-worker|main_context_checkpoint|source_conflict|stale_work_order|accepted_decision_not_propagated" 00_docs/standards`
- `rg -n "branch|worktree|merge gate|remote push|commit checkpoint|repo-integrator|task branch|session branch" 00_docs/standards 00_docs/works`
- Coordinator 관련 기준서와 작업서의 link와 scope consistency 확인

<!-- key: id=key.work.coordinator-standard.order.expected-output refs=key.contract.output key.role.coordinator key.topic.runtime-handoff key.doc.work-order -->

## Expected Output

- 현재 work order step을 bounded worker assignment로 변환할 수 있는 Coordinator 기준서

<!-- key: id=key.work.coordinator-standard.order.review-points refs=key.section.review-points key.role.coordinator key.boundary.high-risk-work key.topic.worker-done key.topic.main-acceptance key.standard.subagent -->

## Review Points

- High-risk work가 자동 worker-routable로 처리되지 않는지 확인한다.
- Worker `DONE`과 main acceptance가 분리되는지 확인한다.
- Worker가 전체 작업서(4)를 재해석하거나 scope를 확장하지 않는지 확인한다.
- Injected skill이 worker authority를 올리지 않는지 확인한다.
- Default bounded worker contract가 missing skill contract로 해석되지 않는지 확인한다.
- Main context checkpoint가 accepted decision과 current work identity를 보존하는지 확인한다.
- 모델 변경 후 old execution term이 stale work order로 남지 않았는지 확인한다.
- Single workspace guard가 file-writing worker boundary를 충분히 제한하는지 확인한다.

<!-- key: id=key.work.coordinator-standard.order.progress-record refs=key.topic.progress-update key.topic.main-acceptance key.step.s05 -->

## Progress Record

S05 완료는 main acceptance 후에만 `key-progress.md`에 기록한다.
