---
doc_type: work_round
created_at: "2026-08-28"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-28", accepted_by: main}
round_status: accepted
key:
  id: key.work.round.r019-keystone-session-title.index
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
    - key.standard.skill.init
    - key.standard.skill.reader
---

# R019 Keystone Session Title Display 작업서 색인

R019는 Keystone을 사용하는 신뢰된 프로젝트에서만 Codex CLI 터미널 제목에 작업 중 표시,
현재 thread 제목과 task progress가 나타나도록 프로젝트 로컬 설정을 선택적으로 구성한다.
활성 Round가 선택되면 Reader는 `프로그래스 {Round ref}:{대표 문구}` 형식의 `/rename` 명령을
제안해 thread 제목과 Round focus를 연결한다.

<!-- key: id=key.work.round.r019.execution-order refs=key.topic.work-sequence key.topic.initialization -->
## 실행 순서

| 순서 | Step | 상태 | 목적 |
|---|---|---|---|
| S01 | Project-Scoped Session Title Contract | accepted | 프로젝트 로컬 설정 권한, opt-in과 세션 제목 제안 경계를 기준서에 정렬했다 |
| S02 | Init and Reader Skill Integration | accepted | Init의 bounded config edit와 Reader의 Round 기반 rename 제안을 구현했다 |
| S03 | Verification and Closure | accepted | 계약·설정 syntax·회귀 검증 후 Round를 닫았다 |

- Active Step: 없음

<!-- key: id=key.work.round.r019.boundaries refs=key.boundary.scope-control key.topic.initialization -->
## Round 경계

- 소비 프로젝트의 `.codex/config.toml` 중 `tui.terminal_title`만 선택적으로 변경한다.
- 사용자 전역 `~/.codex/config.toml`과 다른 Codex 설정 key는 변경하지 않는다.
- 별도 plugin, hook, daemon, App Server 또는 외부 service를 만들지 않는다.
- Reader는 `/rename` 명령을 제안할 뿐 slash command 실행을 가장하지 않는다.
- R015와 R018의 source, 상태와 우선순위는 변경하지 않는다.
- Browser, Playwright, publish와 installer 작업은 포함하지 않는다.

## 복구 규칙

1. R019 목표와 Step 상태는 이 Index에서 확인한다.
2. 세부 권한, 수용 기준과 검증은 Work Order를 읽는다.
3. 실제 실행 결과와 resume point는 aggregate Progress를 읽는다.
