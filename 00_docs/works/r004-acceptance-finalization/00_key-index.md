---
doc_type: work_round
created_at: "2026-08-04"
status: active
approval:
  state: accepted
  accepted_at: "2026-08-04"
  accepted_by: user
round_status: accepted
key:
  id: key.work.round.r004-acceptance-finalization.index
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.acceptance
    - key.topic.finalization
    - key.topic.verification
---

# R004 Acceptance Finalization 작업서 색인

이 round는 Main acceptance를 구현 수용으로 보존하면서 영향 Keystone 원천 문서가
같은 시점으로 수렴하도록 기존 Progress/Change Set의 acceptance finalization, scoped hard gate, executable validator와
repository hook 안전망을 기준·runtime·검증에 반영한다. R003이 accepted된 후 시작한다.

<!-- key: id=key.work.round.r004-acceptance-finalization.execution-order refs=key.topic.work-sequence key.topic.finalization -->
## 실행 순서

| 순서 | Work | 경로 | 상태 | 목적 |
|---|---|---|---|---|
| S01 | Acceptance Finalization Standard | `acceptance-finalization-standard/00_key-index.md` | accepted | 기존 상태 체계를 보강하는 finalization·복수 active step·early work 계약을 닫았다 |
| S02 | Finalization Runtime and Validator | `finalization-runtime-validator/00_key-index.md` | accepted | 관련 skill runtime과 Author package bundled validator 구현·검증을 수락했다 |
| S03 | Finalization Integration Verification | `finalization-integration-verification/00_key-index.md` | accepted | Uptendo R008 합성 회귀 fixture, fail-closed과 hook 시나리오 검증을 수락했다 |

<!-- key: id=key.work.round.r004-acceptance-finalization.reading-rules refs=key.topic.work-recovery key.topic.acceptance key.topic.finalization -->
## 읽기 규칙

Active steps: []

1. R004 S01~S03는 모두 accepted이며 `active_steps`는 비어 있다.
2. `00_docs/works/key-decisions.md`의 `DEC-WORKS-021`을 공통 결정으로 사용한다.
3. 새로운 작업은 기존 accepted Round의 Step 상태를 다시 열지 말고 새 Round로 계획한다.

<!-- key: id=key.work.round.r004-acceptance-finalization.boundaries refs=key.boundary.scope-control key.topic.finalization -->
## Round 경계

- Core validator는 설치된 `keystone-author` package에 포함하고 소비 프로젝트에 source를 복사하지 않는다.
- Hook은 validator를 재호출하는 안전망이며 acceptance나 문서 수정 권한을 갖지 않는다.
- Uptendo R008/R010 원천 문서와 migration은 fixture/evidence로만 사용하고 직접 수정하지 않는다.
- Global install, plugin publishing과 marketplace 등록은 범위 밖이다.
