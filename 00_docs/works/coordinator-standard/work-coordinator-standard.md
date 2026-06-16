# Coordinator Standard 작업서(4)

## Goal

`keystone-coordinator`의 main-supervised subagent workflow 계약을 정리한다.

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

## Source Context

- `00_docs/standards/00_project-standard.md`
- `00_docs/standards/skills/coordinator/00_index.md`
- `00_docs/standards/skills/coordinator/standard-coordinator.md`
- `00_docs/works/00_index.md`

## Completion Criteria

- [ ] Coordinator가 current step과 completion criteria를 복구할 수 있다.
- [ ] Scope가 worker handoff boundary로 변환된다.
- [ ] Review points가 reviewer focus로 변환된다.
- [ ] Main acceptance 전에는 accepted로 표시하지 않는다.

## Recommended Approach

Coordinator 기준서는 runtime orchestration에 집중한다. 문서 수정이나 결정 수집은 Author와
Clarify로 남긴다.

## Context Pack Seed

- `STD-KEYSTONE-030`
- progress/report status rule
- high-risk work stop condition

## Stop Conditions

- current step이 복구되지 않는다.
- work unit이 subagent-sized Goal이 아니다.
- high-risk implementation이 main/user decision 없이 필요하다.

## Verification

Allowed:

- `rg -n "Current Step Brief|Context Pack|accepted" 00_docs/standards/skills/coordinator/standard-coordinator.md`
- `git diff --check`

## Expected Output

- 현재 work order step을 runtime handoff로 변환할 수 있는 Coordinator 기준서

## Review Points

- High-risk work가 자동 worker-routable로 처리되지 않는지 확인한다.
- Worker `DONE`과 main acceptance가 분리되는지 확인한다.

## Progress Record

S05 완료는 main acceptance 후에만 `progress.md`에 기록한다.
