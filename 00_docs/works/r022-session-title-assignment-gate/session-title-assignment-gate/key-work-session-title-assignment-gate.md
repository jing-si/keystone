---
doc_type: work_order
created_at: "2026-08-28"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-28", accepted_by: main}
work_status: complete
key:
  id: key.work.session-title-assignment-gate.order
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.skill-contract
    - key.topic.verification
    - key.boundary.scope-control
    - key.standard.project
    - key.standard.skill.init
    - key.standard.skill.reader
  relations:
    produces:
      - key.skill.reader
      - key.code.reader.keystone-session-title
      - key.test.r020.keystone-session-title-runtime
---

# Session Title Assignment Gate 작업서

## Goal

Keystone Reader 세션의 첫 native title을 기존 라운드의 실제 수행 의도가 명확할 때만
`RNNN[-SUFFIX]:대표문구`로 유도한다. 선택되지 않은 상태에서는 미완료 라운드와 자유로운
검토·조사·확인 경로를 안내하되 특정 라운드를 자동 선택하지 않는다.

## 수락된 사용자 방향

1. 최초로 정해진 native title은 세션 동안 유지되는 것으로 취급한다.
2. `프로그래스` prefix를 제거하고 thread-title에는 `R015:효과검토` 같은 값만 넣는다.
3. active 라운드가 하나여도 자동 선택하지 않는다.
4. active뿐 아니라 `accepted`, `cancelled`가 아닌 미완료 부모·하위 라운드를 후보로 안내한다.
5. 기존 라운드 수행, 자유로운 신규 검토·조사·확인, 상태 확인을 모두 허용한다.
6. Round ref 언급만으로 할당하지 않으며 수행 의도가 명확할 때만 제목 힌트를 넣는다.
7. 후보는 최대 10개, 초과분은 `외 N개`로 표시한다.
8. 후보는 상태가 아니라 parent Round 번호 오름차순으로 정렬하고 각 parent 바로 아래에 child
   suffix를 Excel-column 오름차순으로 들여써서 묶는다.

## Scope

Include:

- Project·Init·Reader assignment-gate 기준 정렬
- Python 3.9+ standard-library `UserPromptSubmit` hook 수정
- incomplete Round projection, parent→child canonical ordering와 10개 제한
- 명시적 기존 라운드 수행 감지와 비할당 요청 fail-open
- parent와 Excel-column child Round ref 제목 힌트
- focused/shared tests, installer와 실제 새 Codex 세션 검증

Exclude:

- 일반 자연어를 별도 LLM으로 분류하는 추가 호출
- 세션 중 두 번째 native retitle 보장
- Codex SQLite, rollout, App Server와 사용자 전역 config 수정
- plugin, MCP, daemon, watcher와 외부 network service
- unrelated R015·R018 구현 또는 상태 변경
- browser·Playwright 검증

## 실행 계획

| Step | 상태 | 변경 범위 | 완료 경계 |
|---|---|---|---|
| R022/S01 | accepted | Project·Init·Reader 기준과 Work source | 선택·비선택·제목 형식·후보 제한을 일관되게 정의함 |
| R022/S02 | accepted | hook runtime, project config와 tests | 명시적 할당만 title hint를 queue하고 나머지는 원 요청을 보존함 |
| R022/S03 | accepted | focused/shared tests, install, live CLI와 Progress | 새 세션 동작과 회귀를 검증하고 source를 complete/accepted로 정합화함 |

## Completion Criteria

- [x] `$keystone-reader` 단독 요청은 특정 라운드를 자동 선택하거나 title hint를 넣지 않는다.
- [x] `accepted`, `cancelled`를 제외한 부모·하위 라운드를 parent 번호와 child Excel suffix 오름차순으로 최대 10개 안내한다.
- [x] 후보가 10개를 넘으면 남은 개수를 표시한다.
- [x] `R016-A를 진행·시작·계속·전환`하는 명시적 수행 요청만 할당으로 처리한다.
- [x] `R016-B가 완료되었습니다. 확인해 주세요`는 할당으로 처리하지 않는다.
- [x] 할당 제목은 `R016-A:대표문구`이며 대표문구는 어떤 작업인지 사용자의 주 언어로 설명하는 5자 이내 문구다.
- [x] 자유로운 검토·조사·확인과 상태 확인은 Keystone title hint 없이 Reader로 전달된다.
- [x] hook 실패는 원 요청을 계속하는 fail-open이다.
- [x] focused/shared tests, skill validation, compileall, installer와 실제 새 세션 검증이 통과한다.

## Verification

1. 순수 함수 테스트로 incomplete Round 정렬·10개 제한·parent/child label을 검증한다.
2. 할당·의존성 확인·자유 검토·상태 확인 prompt 사례를 검증한다.
3. 재진입, queue 실패와 opt-out fail-open 회귀를 검증한다.
4. Reader/Init/project contract, shared suite, compileall과 diff를 검증한다.
5. 설치본을 갱신하고 새 Codex 세션에서 title과 Spinner·Task progress를 확인한다.

## Stop Conditions

1. 제목 변경에 Codex DB, rollout 또는 global config 직접 수정이 필요하다.
2. 명시적 수행 의도가 없는 Round 언급을 안전하게 할당으로 분류해야 한다.
3. native title이 첫 accepted prompt 이후 자동 재생성된다는 보장이 필요하다.
