---
doc_type: work_order
created_at: "2026-08-28"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-28", accepted_by: main}
work_status: complete
key:
  id: key.work.keystone-session-title.order
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.initialization
    - key.topic.skill-contract
    - key.topic.verification
    - key.boundary.scope-control
    - key.standard.project
    - key.standard.skill.init
    - key.standard.skill.reader
  relations:
    produces:
      - key.skill.init
      - key.skill.reader
---

# Keystone Session Title Display 작업서

<!-- key: id=key.work.keystone-session-title.order.goal refs=key.section.goal key.topic.initialization -->
## Goal

Keystone을 사용하는 프로젝트가 명시적으로 선택한 경우에만 프로젝트 로컬 Codex 설정으로
터미널·IDE 탭에 작업 중 상태, 현재 thread 제목과 task progress를 표시한다. 활성 Round focus가
정해지면 Reader가 짧고 일관된 thread rename 명령을 제안해 탭 제목과 Keystone 작업 문맥을
연결한다.

## 수락된 사용자 방향

1. 기능명은 `Keystone 세션 제목 표시`를 사용한다.
2. 초기 설정에서 yes/no로 선택하고, 이후 자연어로 명시적으로 켜 달라고 요청해도 적용한다.
3. 설정은 소비 프로젝트의 `.codex/config.toml`에만 적용하고 `~/.codex/config.toml`은 건드리지
   않는다.
4. 활성 Round의 thread 제목 형식은 `프로그래스 {Round ref}:{대표 문구}`다. 대표 문구는 작업을
   구분할 수 있는 5자 이내 문구이며 잘려도 된다.
5. 별도 사용자-facing 도구는 만들지 않는다. Init이 설정을 담당하고 Reader가 rename 명령을
   제안한다.

<!-- key: id=key.work.keystone-session-title.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- Project·Init·Reader 기준의 프로젝트 로컬 Codex 설정 권한과 안전 경계
- Init 초기화 흐름의 opt-in 질문과 ready 프로젝트의 명시적 configure 요청
- `.codex/config.toml`의 `[tui] terminal_title` bounded create/replace
- `activity`, `thread-title`, `task-progress`의 고정 순서
- Reader가 Round focus 뒤 제안하는 `/rename 프로그래스 {Round ref}:{대표 문구}`
- 기존 Codex 설정 보존, invalid/ambiguous TOML의 no-write stop
- 관련 skill contract와 focused tests
- R019 Progress와 navigation source 정합화

Exclude:

- `~/.codex/config.toml` 또는 다른 프로젝트 수정
- 다른 Codex config key, profile, provider, auth, permission, notification와 telemetry 변경
- slash command의 programmatic 실행 또는 thread rename 성공 주장
- plugin, hook, daemon, watcher, App Server와 외부 network integration
- IntelliJ 자체 Rename Session 동작 제어
- R015·R018 source와 unrelated runtime 수정

<!-- key: id=key.work.keystone-session-title.order.execution-plan refs=key.topic.work-sequence key.topic.verification -->
## 실행 계획

| Step | 상태 | 변경 범위 | 완료 경계 |
|---|---|---|---|
| R019/S01 | accepted | Project·Init·Reader 기준과 R019 source | opt-in, project-only write authority와 rename suggestion 경계를 accepted 의미로 정렬했다 |
| R019/S02 | accepted | Init·Reader skill source와 focused test | 초기/후속 요청의 bounded config edit와 Round focus의 exact rename 제안을 구현했다 |
| R019/S03 | accepted | affected tests, Work State, graph, diff와 Progress | 설정 syntax와 범위 보존을 검증하고 Round source를 complete/accepted로 정합화했다 |

<!-- key: id=key.work.keystone-session-title.order.completion refs=key.topic.verification key.boundary.stop-condition -->
## Completion Criteria

- [x] 초기화 중 `Keystone 세션 제목 표시` opt-in 질문에 yes를 선택하면 프로젝트 로컬
      `.codex/config.toml`에만 설정한다.
- [x] no를 선택하면 `.codex/config.toml`을 만들거나 수정하지 않는다.
- [x] ready 프로젝트에서 사용자가 자연어로 명시적으로 켜 달라고 요청하면 재질문 없이 같은
      bounded 설정을 적용할 수 있다.
- [x] `[tui] terminal_title = ["activity", "thread-title", "task-progress"]`가 유효한 TOML로
      기록된다.
- [x] 기존 파일의 다른 table·key·comment는 보존하고 대상 key만 create 또는 replace한다.
- [x] invalid TOML, 중복/충돌 table 또는 안전한 최소 edit가 불가능한 구조에서는 쓰지 않고
      충돌을 보고한다.
- [x] `~/.codex/config.toml`과 다른 Codex 설정은 변경하지 않는다.
- [x] Round focus가 정해지면 Reader는 대표 문구를 5자 이내로 정해 exact `/rename` 명령을 한 번
      제안하되 실행 또는 성공을 주장하지 않는다.
- [x] Round focus 전에는 프로젝트 이름만 보이는 현재 기본 동작을 방해하지 않는다.
- [x] 별도 plugin, hook, daemon, App Server와 외부 network dependency가 없다.
- [x] 관련 contract tests, Codex strict-config, Work State와 `git diff --check`가 통과한다.

## Verification

1. Init·Reader 기준서와 skill source에서 opt-in, bounded write와 rename suggestion 문구를 대조한다.
2. 빈 config, 기존 `[tui]`, 다른 table/comment가 있는 fixture의 예상 최소 변경을 검증한다.
3. no 선택, invalid TOML과 global path 금지 계약을 검증한다.
4. Python 3.11+에서는 `tomllib`, 현재 Python 3.9 환경에서는 Codex `--strict-config`로 추천 설정
   syntax와 item identifier를 검증한다.
5. Focused unittest, Work State, compileall과 `git diff --check`를 실행한다.

## Stop Conditions

1. 프로젝트 로컬 config가 현재 Codex CLI에서 지원되지 않거나 target key가 공식 계약과 다르다.
2. 기존 config를 전체 재작성해야만 설정할 수 있다.
3. global config, host API, plugin, hook, daemon 또는 외부 service가 필요하다.
4. slash command를 agent가 직접 실행해야만 완료 가능한 요구로 범위가 바뀐다.
