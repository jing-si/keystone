---
doc_type: work_order
created_at: "2026-08-04"
status: active
approval:
  state: accepted
  accepted_at: "2026-08-04"
  accepted_by: user
work_status: accepted
key:
  id: key.work.acceptance-finalization-standard.order
  refs: [key.doc.work, key.topic.acceptance, key.topic.finalization, key.topic.verification, key.topic.change-set]
---

# Acceptance Finalization Standard 작업서 및 Change Set

## Goal

`DEC-WORKS-021`의 acceptance finalization 결정을 프로젝트·Bootstrap·Author·Reader·Coordinator 기준에
일관되게 확정하고 runtime·validator 구현의 권위 있는 source contract를 만든다.

## Scope

Include:

- 기존 `accepted`와 Progress/Change Set의 `finalization.state` 하위 상태 의미
- operative artifact·문서 의미·active steps·gate·risk·namespace 변경 trigger
- 복수 `active_steps`와 상태 영향 없는 `early_work`
- 자동 시작, 영향 문서별 disposition과 부분 성공 금지
- 동일 work scoped hard gate, 독립 work 병행 조건과 긴급 우회 부채
- Runtime 필수 절차, executable validator, pre-commit/CI 안전망의 책임 분리
- `validator_unavailable`, `validator_execution_failed` fail-closed
- `keystone-author/scripts/` core validator와 project extension 권한 경계

Exclude:

- Repo-local `skills/**` 및 validator executable 구현
- Uptendo 원천 문서·code·migration 수정
- Global install, packaging, publishing

## Completion Criteria

- [x] `DEC-WORKS-021`과 관련 기준서가 충돌 없이 일치한다.
- [x] Finalization trigger·exclusion·disposition·hard gate·exception이 구분된다.
- [x] 단수 current step을 권위로 사용하지 않고 복수 active steps와 early work가 구분된다.
- [x] Runtime, validator, hook, package과 project extension 권한이 분리된다.
- [x] Validator 부재·실패·충돌의 fail-closed가 정의된다.
- [x] 의미가 바뀐 기준서 approval과 결정 기록이 일치한다.
- [x] S01에서 `skills/**`를 수정하지 않는다.

## Verification

- 관련 기준서의 상태 이름, trigger, gate, authority와 stop condition을 비교한다.
- `key.id`, link, Markdown, temporal metadata와 `git diff --check`를 검증한다.

## Stop Conditions

1. R003이 accepted되지 않았다.
2. Finalization이 다른 work/step 상태 수정 권한이나 Main acceptance를 자동 생성해야 한다.
3. S01 수락에 runtime·validator 구현이 필요하다.
