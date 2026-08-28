---
doc_type: work_order
created_at: "2026-08-28"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-28", accepted_by: main}
work_status: complete
key:
  id: key.work.session-title-permission-hardening.order
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
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

# Session Title Permission Hardening 작업서

<!-- key: id=key.work.session-title-permission-hardening.order.goal refs=key.section.goal key.topic.skill-contract -->
## Goal

Keystone Reader가 Round focus 뒤 세션 제목을 바꿀 때 default sandbox 실패를 수동 fallback으로
끝내지 않고, exact helper executable에만 명시적 host permission을 요청해 실제 자동 rename을
완료한다.

<!-- key: id=key.work.session-title-permission-hardening.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- exact helper executable에 한정된 권한 요청 Reader contract
- App Server 조기 종료 stderr 진단 보존과 subprocess 정리
- helper executable mode와 installer staging·installed-tree 검증
- default sandbox 실패와 escalated actual rename 회귀 검증
- 관련 기준서, Reader source, tests와 R021 Progress 정합화

Exclude:

- generic Python·shell approval
- Codex SQLite, rollout 또는 config 직접 수정
- plugin, MCP, daemon, watcher와 외부 network service
- 사용자 전역 config와 다른 thread·project 변경
- R015, R018, R020 상태 변경
- browser 또는 Playwright 검증

<!-- key: id=key.work.session-title-permission-hardening.order.execution-plan refs=key.topic.work-sequence key.topic.verification -->
## 실행 계획

| Step | 상태 | 변경 범위 | 완료 경계 |
|---|---|---|---|
| R021/S01 | accepted | Project·Reader 기준 | exact executable approval와 거부 fallback 의미를 정렬했다 |
| R021/S02 | accepted | helper, Reader skill, installer와 tests | stderr 보존, direct invocation과 executable 검증을 구현했다 |
| R021/S03 | accepted | focused/shared tests, installer, graph, Work State와 Progress | 회귀와 실제 승인 경로를 검증하고 Round를 정합화했다 |

## Completion Criteria

- [x] 기본 sandbox 실패의 App Server stderr가 diagnostic에 보존된다.
- [x] Reader는 helper를 `python3`나 shell wrapper로 호출하지 않는다.
- [x] 승인 대상은 exact helper executable로 제한된다.
- [x] installer는 source·staging·installed helper의 실행 가능 상태를 검사한다.
- [x] 승인된 실제 helper 실행은 current thread name을 변경하고 재확인한다.
- [x] focused·shared tests, compileall, installer 검증, graph, Work State와 diff check가 통과한다.

## Verification

1. 조기 종료 fake App Server가 stderr diagnostic과 자원 정리를 검증한다.
2. Reader·installer contract test가 direct executable과 narrow approval을 고정한다.
3. default sandbox 실패가 구체적인 Codex state 접근 오류를 반환하는지 확인한다.
4. exact helper executable의 escalated 실행이 `status: renamed`를 반환하는지 확인한다.
5. focused/shared tests, compileall, installer temporary install, graph, Work State와 diff를 검증한다.

## Stop Conditions

1. narrow executable approval이 아니라 generic interpreter approval만 가능하다.
2. 자동 rename에 Codex DB 또는 rollout 직접 수정이 필요하다.
3. helper가 현재 thread와 repository cwd를 확인할 수 없다.
4. installer가 executable mode를 보존하지 못한다.
