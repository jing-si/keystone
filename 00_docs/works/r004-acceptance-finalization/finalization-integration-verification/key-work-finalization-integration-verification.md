---
doc_type: work_order
created_at: "2026-08-04"
status: active
approval: {state: accepted, accepted_at: "2026-08-04", accepted_by: user}
work_status: accepted
key:
  id: key.work.finalization-integration-verification.order
  refs: [key.doc.work, key.topic.finalization, key.topic.integration-verification, key.topic.verification]
---

# Finalization Integration Verification 작업서

## Goal

구현 수용 후 Progress, Work Order, Change Set, index, standard, 복구 안내가 자동으로
수렴하고 누락·충돌·validator 장애에서 fail-closed로 복구되는지 검증한다.

## Prerequisite

- R004 S01·S02 accepted

## Verification Scenarios

1. Uptendo R008 S06-C accepted 후 active step set과 상위 상태 소유자 수렴
2. Progress, work index, round index의 서로 다른 active step 참조 검출
3. `현재`, `부터 진행`, `Worker S06-X` stale 문맥과 이력 문맥 구분
4. 해소된 implementation gate과 residual/deferred item 누락 검출
5. R008/R010 Flyway `V12` 충돌의 integration gate 요구
6. `validator_unavailable`, `validator_execution_failed`, runtime/validator conflict
7. 동일 work scoped hard gate와 독립 work 병행
8. 긴급 우회 부채 보존과 finalization resume
9. Project extension의 core 규칙 약화 거부
10. Pre-commit/CI wrapper가 동일 package validator를 호출
11. 복수 Step이 동등하게 활성화된 경우와 미래 Step early work의 상태 비영향

## Completion Criteria

- [x] 모든 시나리오에 executable evidence가 있다.
- [x] 부분 문서 갱신은 `finalization.state: complete`로 오인되지 않는다.
- [x] Hook 없음과 validator 없음을 구분한다.
- [x] R003과 R004 원천 문서, runtime, validator가 일관된다.
- [x] Main이 residual risk를 확인하고 S03과 R004를 수락한다.

## Stop Conditions

1. S02 runtime/validator가 수락되지 않았다.
2. Uptendo private source 내용을 fixture에 복사해야만 검증할 수 있다.
3. 실패 시나리오가 문서 수정·acceptance 권한을 validator에 요구한다.

## Executable Evidence

| Scenario | Evidence |
|---|---|
| 1 | accepted S06-C, 병렬 active S06-D, 세 상위 source의 동일 active set이 통과한다 |
| 2 | work/round/Context Map active ref drift가 `active_steps_source_mismatch`로 실패한다 |
| 3 | live `Worker S06-X`는 실패하고 historical disposition은 허용한다 |
| 4 | implementation gate·residual risk 범주 누락이 실패한다 |
| 5 | R008/R010 Flyway V12 중복 owner가 `namespace_collision`으로 실패한다 |
| 6 | validator 부재와 process output 실패를 서로 다른 reason code로 보존한다 |
| 7 | 수락되지 않은 병렬 Step 직접 전이를 거부하고 병렬 active 상태는 유지한다 |
| 8 | namespace 충돌 해소 후 기존 acceptance를 보존한 채 validator를 재개한다 |
| 9 | project extension 성공이 core 실패를 성공으로 바꾸지 못한다 |
| 10 | `check_finalization_hook.sh`가 동일 package runner를 호출한다 |
| 11 | 복수 active Steps는 동등하고 future early work는 planned 상태를 바꾸지 않는다 |

## Integration Result and Change Set

- 공개 합성 fixture만 사용했으며 Uptendo private source나 migration을 복사하지 않았다.
- `S06-C` 같은 suffix Step ref, `Worker S06-X` stale recovery 문맥을 core validator에 보완했다.
- Additive project extension은 core pass 뒤에만 실행되며 core failure를 약화하지 못한다.
- Pre-commit/CI가 재사용할 동일-package `check_finalization_hook.sh` wrapper를 추가했다.
- Repository 자체 hook 설치는 정책 선택이므로 자동 설치하지 않았다.
- Verification: S03 scenario 11건과 전체 Author test 41건, Bash syntax, installer smoke,
  `git diff --check` 통과.
- Main residual-risk review: 실제 소비 repository의 hook 채택 여부만 운영 선택으로 남으며
  validator 부재와 동일한 오류로 취급하지 않는다.
