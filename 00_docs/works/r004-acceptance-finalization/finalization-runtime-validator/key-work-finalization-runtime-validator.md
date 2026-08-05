---
doc_type: work_order
created_at: "2026-08-04"
status: active
approval: {state: accepted, accepted_at: "2026-08-04", accepted_by: user}
work_status: accepted
key:
  id: key.work.finalization-runtime-validator.order
  refs: [key.doc.work, key.topic.finalization, key.topic.verification, key.topic.skill-source, key.topic.change-set]
---

# Finalization Runtime and Validator 작업서 및 Change Set

## Goal

Main acceptance 직후 기존 Progress/Change Set의 finalization을 자동 시작하고 문서 수렴을
executable evidence로 검증하는 runtime contract과 portable validator command/interface를 구현한다.

## Prerequisite

- R004 S01 accepted

## Scope

Include:

- Main/Author/Coordinator와 필요한 Reader/Linker/Init runtime contract 반영
- `skills/keystone-author/scripts/`의 core validator
- active-step 참조 drift, stale 단수 current 문맥, early-work·disposition·gate·risk·namespace 후보 검사
- Machine-readable diagnostics, exit code, fail-closed reason과 finalization resume
- Project config/adapter extension과 core 규칙 약화 금지
- 지원되는 경우 pre-commit/CI wrapper 연결

Exclude:

- Validator의 자동 문서 수정·acceptance·finalization 완료 기록
- 소비 프로젝트에 core validator source 복사
- Uptendo 직접 수정, global install·publish

## Completion Criteria

- [x] Acceptance trigger가 별도 사용자 요청 없이 finalization을 시작한다.
- [x] Scoped hard gate가 동일 work의 다음 implement 상태 전이만 차단한다.
- [x] Core validator가 Author package command/interface로 실행된다.
- [x] `validator_unavailable`/`validator_execution_failed`가 fail-closed로 복구된다.
- [x] Project extension이 core 규칙과 authority를 약화하지 못한다.
- [x] Validator와 hook은 진단 전용이며 finalization 완료를 직접 기록하지 않는다.

## Verification

- Unit/fixture test, package command smoke test, invalid config·missing validator·process failure test
- Repo-local skill contract 비교, `git diff --check`, 필요한 build/type/lint test

## Stop Conditions

1. S01 수락 전이다.
2. Validator portability가 특정 소비 프로젝트 구조를 강제한다.
3. Hook이 source edit 또는 acceptance 권한을 필요로 한다.

## Implementation Result and Change Set

- Main acceptance: R004/S02 accepted on 2026-08-05 after independent SPEC/QUALITY PASS.
- Runtime sources: `keystone-author`, `keystone-reader`, `keystone-coordinator` contracts updated;
  Linker와 Init은 S02 runtime 책임 변경이 없어 의도적으로 수정하지 않았다.
- Package artifacts: Author bundled validator, fail-closed runner, interface reference와 30개
  unit/smoke regression test를 추가했다.
- Installer: source·installed validator/runner 존재와 package command smoke를 검증한다.
- Hook/CI: 이 repository에는 연결할 지원 surface가 없어 추가하지 않았다. Runtime과 installer가
  stable package command를 제공하며 S03가 소비 repository wrapper 시나리오를 검증한다.
- Verification: Python unit/smoke 30건, Bash syntax, `git diff --check`, independent SPEC/QUALITY review.
- Residual/deferred: S03 Uptendo 회귀 fixture와 repository hook 시나리오는 planned 상태로 남는다.
