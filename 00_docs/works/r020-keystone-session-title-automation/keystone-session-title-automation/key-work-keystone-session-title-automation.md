---
doc_type: work_order
created_at: "2026-08-28"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-28", accepted_by: main}
work_status: complete
key:
  id: key.work.keystone-session-title-automation.order
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.initialization
    - key.topic.skill-contract
    - key.topic.verification
    - key.boundary.scope-control
    - key.standard.project
    - key.standard.skill.reader
  relations:
    produces:
      - key.skill.reader
      - key.code.reader.keystone-session-title
      - key.test.r020.keystone-session-title-runtime
---

# Keystone Session Title Automation 작업서

<!-- key: id=key.work.keystone-session-title-automation.order.goal refs=key.section.goal key.topic.initialization -->
## Goal

Keystone 세션 제목 표시를 선택한 프로젝트에서 Round focus가 정해지면 현재 Codex thread 이름을
`프로그래스 {local Round ref}:{대표 문구}`로 자동 변경한다. 직접 child Round의 Work/Step은
`R015-AE` 같은 local ref를 보존하며 자동화 실패는 작업을 막지 않고 exact `/rename` fallback으로
복구한다.

## 수락된 사용자 방향

1. 영속 표시 항목은 `thread-title`을 유지한다.
2. 별도 MCP보다 package-local Python helper를 우선한다.
3. 직접 child Round가 선택되면 `R015-AE:대표문구` 형식으로 표시한다.
4. 사용자가 매번 `/rename`을 직접 실행하지 않아도 되게 한다.
5. 설정과 동작은 Keystone 세션 제목 표시를 선택한 프로젝트에만 적용한다.

<!-- key: id=key.work.keystone-session-title-automation.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- Project·Reader 기준의 automatic current-thread rename 권한과 fallback 경계
- package-local Python 3.9+ standard-library helper
- `CODEX_THREAD_ID`와 Codex App Server `thread/name/set` 사용
- parent와 Excel-column child Round ref validation
- 5자 이내 대표 문구와 deterministic title formatting
- 현재 thread·현재 repository cwd 확인
- focused protocol/policy tests와 affected shared tests
- R020 Progress와 navigation source 정합화

Exclude:

- Codex local SQLite/rollout 직접 수정
- 사용자 전역 Codex config 변경
- 다른 thread 또는 다른 프로젝트 rename
- plugin, MCP, hook, daemon, watcher와 외부 network service
- IntelliJ 자체 Rename Session 제어
- R015·R018 source와 unrelated runtime 수정
- browser 또는 Playwright 검증

<!-- key: id=key.work.keystone-session-title-automation.order.execution-plan refs=key.topic.work-sequence key.topic.verification -->
## 실행 계획

| Step | 상태 | 변경 범위 | 완료 경계 |
|---|---|---|---|
| R020/S01 | accepted | Project·Reader 기준과 R020 source | current-thread-only mutation, child local ref와 fail-soft fallback을 accepted 의미로 정렬했다 |
| R020/S02 | accepted | Python helper, Reader skill source와 focused tests | App Server rename adapter와 Round focus 연계를 구현했다 |
| R020/S03 | accepted | affected tests, Work State, graph, diff와 Progress | protocol과 회귀를 검증하고 Round source를 complete/accepted로 정합화했다 |

<!-- key: id=key.work.keystone-session-title-automation.order.completion refs=key.topic.verification key.boundary.stop-condition -->
## Completion Criteria

- [x] opt-in project에서 Round focus 뒤 현재 thread 이름을 자동 변경한다.
- [x] parent Round는 `프로그래스 R020:대표문구` 형식을 사용한다.
- [x] child Round는 `프로그래스 R015-AE:대표문구` 형식을 사용한다.
- [x] 대표 문구는 공백을 정규화하고 5자 이내로 제한한다.
- [x] `CODEX_THREAD_ID`가 없거나 malformed이면 외부 상태를 변경하지 않는다.
- [x] App Server가 확인한 thread cwd가 현재 repository와 다르면 변경하지 않는다.
- [x] SQLite, rollout과 사용자 전역 config를 직접 수정하지 않는다.
- [x] rename 실패 시 concrete `/rename` 명령을 반환하고 작업은 계속할 수 있다.
- [x] Python 3.9+ standard library만 사용한다.
- [x] focused tests, affected shared tests, compileall, Work State와 `git diff --check`가 통과한다.

## Verification

1. 순수 title policy에서 parent, `Z → AA`, 31번째 `AE`, malformed ref와 5자 truncation을 검증한다.
2. fake JSON-lines App Server로 initialize, thread/read, thread/name/set 순서와 오류 fallback을 검증한다.
3. 설치된 Codex CLI 0.150.1 schema에서 `thread/name/set` contract를 대조한다.
4. focused unittest, affected shared suite, compileall, Work State와 `git diff --check`를 실행한다.
5. metadata/relations가 바뀌면 repository graph affected scope를 검증한다.

## Stop Conditions

1. 현재 thread ID를 안전하게 식별할 수 없다.
2. rename에 Codex state DB 또는 rollout 직접 수정이 필요하다.
3. 다른 thread·project까지 변경할 수 있는 broad selector가 필요하다.
4. Python helper 실행마다 해제할 수 없는 대화형 권한 승인이 필요하다.
5. current TUI가 이름 변경을 읽지 못하고 resume 후에만 반영된다.
