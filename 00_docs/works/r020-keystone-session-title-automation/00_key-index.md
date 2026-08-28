---
doc_type: work_round
created_at: "2026-08-28"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-28", accepted_by: main}
round_status: accepted
key:
  id: key.work.round.r020-keystone-session-title-automation.index
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.work-recovery
    - key.topic.initialization
    - key.topic.skill-contract
    - key.topic.verification
    - key.boundary.scope-control
    - key.standard.project
    - key.standard.skill.reader
---

# R020 Keystone Session Title Automation 작업서 색인

R020은 R019의 project-local terminal title opt-in을 유지하면서, Round focus가 정해진 현재
Codex thread의 이름을 package-local Python helper로 자동 변경한다.

<!-- key: id=key.work.round.r020.execution-order refs=key.topic.work-sequence key.topic.initialization -->
## 실행 순서

| 순서 | Step | 상태 | 목적 |
|---|---|---|---|
| S01 | Automatic Thread Name Contract | accepted | current-thread-only 권한, child Round ref와 fallback 경계를 기준서에 정렬했다 |
| S02 | Python Helper and Reader Integration | accepted | App Server `thread/name/set` helper와 Reader 호출을 구현했다 |
| S03 | Verification and Closure | accepted | protocol·회귀·Work State 검증 후 Round를 닫았다 |

- Active Step: 없음

<!-- key: id=key.work.round.r020.boundaries refs=key.boundary.scope-control key.topic.initialization -->
## Round 경계

- 현재 프로세스의 `CODEX_THREAD_ID`가 가리키는 thread만 변경한다.
- 제목 형식은 `프로그래스 {local Round ref}:{대표 문구}`이며 대표 문구는 5자 이내다.
- child Work/Step이면 parent ref가 아니라 `R015-AE` 같은 local child Round ref를 사용한다.
- 사용자 전역 config, Codex DB 직접 수정, plugin, MCP와 daemon은 포함하지 않는다.
- 자동 변경 실패 시 concrete `/rename` 명령을 제안하고 Keystone 작업을 막지 않는다.
- R015와 R018의 source, 상태와 우선순위는 변경하지 않는다.
- Browser, Playwright, publish와 installer 작업은 포함하지 않는다.

## 복구 규칙

1. R020 목표와 Step 상태는 이 Index에서 확인한다.
2. 세부 권한, 수용 기준과 검증은 Work Order를 읽는다.
3. 실제 실행 결과와 resume point는 aggregate Progress를 읽는다.
