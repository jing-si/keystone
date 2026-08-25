---
doc_type: progress
created_at: "2026-08-25"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-25", accepted_by: main}
work_status: complete
work_ref: R016/worktree-locator-navigation
key:
  id: key.work.worktree-locator-navigation.progress
  refs:
    - key.topic.progress-update
    - key.topic.work-recovery
    - key.topic.work-sequence
    - key.topic.work-execution
    - key.topic.keystone-metadata
    - key.topic.verification
    - key.work.decisions.dec-works-033
    - key.work.worktree-locator-navigation.order
---

# Worktree Locator and Targeted Work Discovery 진행 기록

## 현재 상태

- Round: `R016`
- Work: `worktree-locator-navigation`
- Round status: `accepted`
- Work status: `complete`
- Approval state: `accepted`
- Active Step: 없음
- Planned Steps: []
- Accepted Steps: [`R016/S01`, `R016/S02`, `R016/S03`]
- Status effect: 기준서, skill runtime, parser, tests와 affected graph를 검증하고 R016을
  complete / accepted로 닫았다.
- Execution location: primary worktree `/Users/joung/workspace/keystone/keystone`. Linked worktree를
  선택하지 않았으므로 Work Order에 `key.worktree` locator를 추가하지 않는다.
- Resume point: 없음. 후속 변경은 별도 Work로 생성한다.

## 작업서 작성 결과

1. R015와 분리된 R016 parent Round와 하나의 Work node를 `planned / pending`으로 작성했다.
2. Worktree 사용 시에만 `key.worktree.path`를 코드 수정 전에 canonical Work Order에 기록하는
   방향을 Goal과 completion criteria로 정리했다.
3. Coordinator의 worktree 생성·선택, Author의 metadata write, Reader의 exact-path 소비와
   Main/external-skill fallback 역할을 분리했다.
4. Global worktree scan, atomic claim, lock registry와 historical backfill을 범위에서 제외했다.
5. Locator 누락은 자동 탐색으로 보완하지 않고 사용자 기억에 의존하는 residual risk로 기록했다.
6. R014 accepted source와 R015 active source, 현재 변경 파일을 수정하거나 상태 전이하지 않았다.

## 작업서 작성 검증

- `python3 scripts/work_state_runtime.py --root .`: `pass`, error/warning 0. R016은 `planned`이며
  active Round/Step에 포함되지 않았다.
- 같은 Work State에서 R014는 accepted, R015는 active / `R015/S01`을 유지했다.
- Linker docs-first readiness: `pass`, 225/225 source parsed, error 0. 기존 corpus warning은
  137건이며 R016 source 진단, duplicate ID, unresolved ref와 unknown metadata field 진단은 0건이다.
- `git diff --check`: 통과.

## 구현 결과

1. Accepted Project rule `STD-KEYSTONE-061`과 Artifact Graph·Reader·Author·Coordinator·Subagent
   상세 기준에 linked worktree setup, canonical Work Order write, fresh confirmation과 exact-path
   navigation을 정렬했다.
2. Reader·Author·Coordinator skill source에 같은 owner sequence, missing/stale handling과
   no-global-scan 경계를 구현했다.
3. Linker metadata parser가 Work Order document의 absolute `key.worktree.path`만 admission하고
   missing path, relative path, unknown child와 non-Work Order 선언을 malformed로 진단한다.
4. Focused shared test와 self-host graph anchor가 skill owner sequence와 accepted Project rule을
   검증한다.

## 최종 검증

- Linker package: 374 tests 통과.
- Shared skill suite: 108 tests 통과. R016 focused/self-host 재검증 4 tests 통과.
- Python compileall: scripts와 Reader·Author·Coordinator·Linker runtime 통과.
- Repository readiness: `pass`, repository scope 357/357 parsed, skipped 0, error 0. 기존 비차단
  locator warning 135건이며 R016 affected diagnostic은 0건이다.
- Repository graph validation: `pass`, 357/357 complete, error/warning 0.
- Skill validation: 공식 `quick_validate.py`는 PyYAML 부재로 시작하지 못했고, 동일 규칙의 Ruby
  표준 YAML fallback은 Reader·Author·Coordinator 모두 통과했다.
- Canonical Work State: `pass`, R016 accepted history, active Round/Step는 R015 / `R015/S01`만 유지.
  `git diff --check` 통과.

## 다음 단계

R016은 완료됐다. Locator 누락 시 별도 worktree 발견을 사용자 기억에 의존하는 residual risk와
child detailed standard의 기존 pending lifecycle은 그대로 유지한다.
