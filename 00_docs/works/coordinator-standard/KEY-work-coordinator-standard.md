---
doc_type: work_order
key:
  id: key.work.coordinator-standard.order
  refs:
    - key.doc.work
    - key.role.coordinator
    - key.role.subagent
    - key.topic.orchestration
    - key.topic.acceptance
---

# Coordinator Standard 작업서(4)

<!-- key: id=key.work.coordinator-standard.order.goal refs=key.role.coordinator key.topic.main-supervised key.role.subagent key.topic.workflow key.section.goal -->

## Goal

`keystone-coordinator`의 main-supervised subagent workflow 계약을 정리한다.

<!-- key: id=key.work.coordinator-standard.order.scope refs=key.role.coordinator key.section.scope key.output.current-step-brief key.output.context-pack key.topic.report-handling key.doc.derived-agent -->

## Scope

Include:

- Current Step Brief와 Context Pack 구성
- role-based subagent routing
- report handling
- review, verification, acceptance flow
- progress/report status 분리
- derived agent document policy

Exclude:

- 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 기록 작성 자체
- high-risk implementation 자동 위임
- persistent handoff 기본 생성

Conditionally allowed:

- current work step field와 Coordinator runtime output 사이의 link 보정

<!-- key: id=key.work.coordinator-standard.order.source-context refs=key.section.source-context key.role.coordinator key.doc.standard key.work.index -->

## Source Context

- `00_docs/standards/00_KEY-project-standard.md`
- `00_docs/standards/skills/coordinator/00_KEY-index.md`
- `00_docs/standards/skills/coordinator/KEY-standard-coordinator.md`
- `00_docs/works/00_KEY-index.md`

<!-- key: id=key.work.coordinator-standard.order.completion-criteria refs=key.topic.acceptance key.role.coordinator key.topic.current-step key.topic.worker-handoff key.topic.reviewer-focus -->

## Completion Criteria

- [ ] Coordinator가 current step과 completion criteria를 복구할 수 있다.
- [ ] Scope가 worker handoff boundary로 변환된다.
- [ ] Review points가 reviewer focus로 변환된다.
- [ ] Main acceptance 전에는 accepted로 표시하지 않는다.

<!-- key: id=key.work.coordinator-standard.order.recommended-approach refs=key.section.recommended-approach key.role.coordinator key.topic.orchestration key.topic.responsibility-boundary -->

## Recommended Approach

Coordinator 기준서는 runtime orchestration에 집중한다. 문서 수정이나 결정 수집은 Author와
Clarify로 남긴다.

<!-- key: id=key.work.coordinator-standard.order.context-pack-seed refs=key.output.context-pack key.standard.project.std-keystone-043 key.topic.progress-status key.boundary.high-risk-work -->

## Context Pack Seed

- `STD-KEYSTONE-043`
- progress/report status rule
- high-risk work stop condition

<!-- key: id=key.work.coordinator-standard.order.stop-conditions refs=key.section.stop-conditions key.topic.current-step key.topic.subagent-sizing key.boundary.high-risk-work -->

## Stop Conditions

- current step이 복구되지 않는다.
- work unit이 subagent-sized Goal이 아니다.
- high-risk implementation이 main/user decision 없이 필요하다.

<!-- key: id=key.work.coordinator-standard.order.verification refs=key.topic.verification key.role.coordinator key.verification.git-diff-check key.topic.standard-verification -->

## Verification

Allowed:

- `rg -n "Current Step Brief|Context Pack|accepted" 00_docs/standards/skills/coordinator/KEY-standard-coordinator.md`
- `git diff --check`

<!-- key: id=key.work.coordinator-standard.order.expected-output refs=key.contract.output key.role.coordinator key.topic.runtime-handoff key.doc.work-order -->

## Expected Output

- 현재 work order step을 runtime handoff로 변환할 수 있는 Coordinator 기준서

<!-- key: id=key.work.coordinator-standard.order.review-points refs=key.section.review-points key.role.coordinator key.boundary.high-risk-work key.topic.worker-done key.topic.main-acceptance -->

## Review Points

- High-risk work가 자동 worker-routable로 처리되지 않는지 확인한다.
- Worker `DONE`과 main acceptance가 분리되는지 확인한다.

<!-- key: id=key.work.coordinator-standard.order.progress-record refs=key.topic.progress-update key.topic.main-acceptance key.step.s05 -->

## Progress Record

S05 완료는 main acceptance 후에만 `KEY-progress.md`에 기록한다.
