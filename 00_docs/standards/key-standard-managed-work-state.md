---
doc_type: standard
created_at: "2026-10-12"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-10-12", accepted_by: main}
key:
  id: key.standard.managed-work-state
  refs:
    - key.standard.project
    - key.work.unified-state-management.order
---

# 관리 중인 작업의 상태 저장 계약

R024에서 합의한 현재 작업 상태와 작업서 사건 기록 분리를 정의한다. 이 계약은 새 저장 모드의
구현 기준이다. 기존 corpus는 명시적 이전이 끝나기 전까지 기존 Work State 해석을 유지하며,
이 계약의 수락만으로 기존 저장소가 이전됐다고 판단하지 않는다.

## 권위와 범위

1. 현재 상태는 document root 아래 **`state/current.json` 한 파일**이 소유한다.
   `schema_version: 2`, `states: {실행 상태명: [관리 대상, ...]}` 구조로 상태 → Round·Work·Step을
   묶는다. Round별 파일을 만들지 않는다. closed 항목·그룹은 없고 모두 종료되면 `states: {}`를 유지한다.
2. 저장 항목은 `ref`, `kind`(round/work/step), `parent`, `order_path`, `approval`, `finalization`이다.
   `execution`은 소속 그룹명이 소유하며 항목에 중복 저장하지 않는다. 변경 API·소비자 projection은
   이 그룹명을 execution으로 복원한다. 실행·승인·최종 정리는 독립이며 Task는 도입하지 않는다.
3. 실행 상태는 planned/in_progress/blocked/complete/cancelled/superseded, 승인은
   pending/accepted/rejected, 최종 정리는 null 또는 pending/in_progress/complete/waived다.
   null은 최종 정리 절차가 요구되지 않음을 뜻한다. complete가 자동 closed를 뜻하지 않는다.
4. `parent`는 같은 Round의 관리 항목을 참조한다. Round는 null parent다. R025의 선택적 Work
   정의는 Project STD-KEYSTONE-026을 따른다. R015-A에서는 Step의 parent를 같은 Round 또는
   그 안의 Work로 허용한다. 활성 자식을 남긴 채 부모를 종료하지 않는다.
5. `order_path`는 저장소 내 작업서의 상대 경로다. 외부 경로, symlink와 hardlink를 허용하지 않는다.
6. 기준서 자체의 승인·lifecycle, 문서 metadata 전반의 이전은 이 작업 상태 wire의 범위 밖이다.
   해당 이전은 별도 범위 확정 후 소비자와 함께 적용한다.

## 사건 기록

1. 작업서에 별도 open/closed 현재 상태 필드를 만들지 않는다. 생성 시 상태에 등록하되 planned로
   시작할 수 있다. `open`은 관리 중이라는 개념일 뿐 저장 필드가 아니다.
2. 생성·상태 변경·종료·재개마다 작업서에 사람이 읽는 사건 행과 `keystone-work-event` JSON
   comment를 남긴다. ref, event(created/updated/closed/reopened), at(날짜 또는 timezone 있는
   ISO timestamp), note, result를 기록한다. updated에는 before도 기록하고 closed에는 reason을 둔다.
   동일 값 갱신은 사건을 추가하지 않는다. 구형 created/reopened의 result 생략은 호환 입력이다.
3. 종료 사유는 complete/skipped/cancelled/superseded다. complete 종료는 execution=complete,
   approval=accepted이며 finalization이 null/complete/waived일 때만 가능하다. 취소·대체 종료는
   execution 값도 일치해야 한다. skipped는 명시적 수행 생략 사유가 필요하다.
4. 과거 사건을 현재 상태에 맞춰 고치거나 지우지 않는다. 재개에는 이전 closed 사건이 필요하다.
   상태 항목과 사건이 모두 없으면 unknown, 마지막 사건이 생성·변경·재개인데 항목이 없으면 missing이다.
5. 일상 조회는 단일 상태 파일만 읽는다. 사건 조회는 요청된 ref와 exact 작업서만 읽으며 종료 문서
   전체를 탐색하지 않는다. 현재 상태를 얻기 위해 과거 사건 전체를 재생하지 않는다.

## 쓰기와 복구

1. Writer는 읽은 current.json 전체의 SHA-256을 expected digest로 전달한다. 최초 생성은 null이며,
   일치하지 않으면 stale 진단으로 변경하지 않는다. 기존 수락은 호출자가 제공하는 근거이며
   runtime이 자동 수락하지 않는다.
2. 상태 쓰기는 상태 root의 단일 배타 lock으로 직렬화한다. busy면 기다리거나 강제 해제하지 않고
   진단한다. Read는 lock이나 파일을 생성하지 않으며 쓰기 중·변경 감지 시 불완전함을 보고한다.
   강제 종료로 남은 lock은 자동 회수하지 않는다. 관리자가 소유 프로세스 종료를 확인하고
   잠금을 정리한 후 pending recover를 실행한다.
3. 생성·상태 변경·종료·재개는 작업서와 상태 파일의 전후 바이트를 담은 일시적인 pending transaction을
   상태 root에 먼저 기록한다. 각 파일은 atomic replace하고 완료하면 pending을 제거한다.
   이는 외부 acceptance evidence나 전수 이력 저장소가 아니라 부분 쓰기 복구용이다.
4. pending이 있으면 정상 상태를 반환하지 않는다. 명시적 recover는 각 파일이 before 또는
   after일 때만 after로 수렴한다. 둘 다 아니면 conflict로 멈추고 다른 편집을 덮어쓰지 않는다.
5. JSON 중복 key, schema 오류, ID·parent 불일치, 경로 이탈, 상태 vocabulary 오류와 사건 오류는
   stable diagnostic으로 보고한다. 손상된 상태를 구형 문서 조회로 조용히 대체하지 않는다.

## 검증

정상 생성·일반 갱신·수락 대기·종료·재개, 기록 누락, parent 종료 차단, stale writer,
pending recovery·외부 편집 충돌, malformed JSON·상태, 경로 이탈과 symlink를 검증한다.
일상 조회에서 작업서 read가 0회인지 확인하고 구형 Work State 회귀를 유지한다.
사용자가 분리한 이번 구현 완료는 소비자 통합·package 검증으로 판단한다. 실제 설치·corpus 이전의 완료와 혼동하지 않는다.

## Package 연결과 호환 경계

Canonical backend와 integration은 `scripts/`에 있으며 Reader·Author·Coordinator·Linker에
독립 사본을 생성한다. Dependency policy는 Linker의 동일 executable policy를 배포한다.
Legacy corpus는 marker 없는 schema v5 경로를 보존하고, 명시적으로 전환한 corpus는 기본 호출로
schema v6를 사용한다. 전체 corpus 개편 및 실제 설치는 이번 구현과 분리한 후속 작업이다.

2026-10-13 정정: 분산된 v1 Round 파일은 사용자 의도를 잘못 해석한 구현이었다. 저장 wire는 v2로
전환하며 비어 있지 않은 `state/rounds/`가 있으면 `state_layout_legacy`로 중단한다. v1 파일을
무시하거나 자동 합치지 않는다. 외부에 v1 데이터가 있으면 별도 이전에서 중복 ref·parent·이력을
검증하고 그룹형 current.json으로 합친 뒤 구형 파일을 제거한다. 이 저장소에는 이전할 v1 데이터가
없다. Legacy 문서 호환 경로와 Work State v6 소비 계약은 유지한다. 관리 대상 약 50개는 예상 규모이며
하드 제한·자동 종료 기준이 아니다. manifest는 모드 설정이고 lock/pending은 임시 복구 자료로,
현재 상태를 나눠 소유하는 추가 문서가 아니다.

## 2026-10-12 소비자 연결과 전환 경계

- 이번 구현 완료 범위는 설치 가능한 skill/runtime 연결과 검증이다. 설치된 스킬 교체와 기존
  corpus 전체 개편은 사용자가 구분한 후속 작업이며 이 저장소에서 지금 실행하지 않는다.
- 전환 완료 프로젝트는 `{document_root}/state/manifest.json`에
  `{"schema_version": 1, "mode": "managed"}`를 둔다. 이는 상태가 아닌 명시적 저장 계약 선택이다.
  파일이 없으면 legacy 호환 경로, 있으면 managed 경로를 사용하며 손상 시 legacy로 fallback하지 않는다.
  `--managed`는 전환 준비 중 같은 경로를 검증하는 명시적 선택이다. 단순 state 디렉터리 생성은 전환이 아니다.
- 현재 상태 목록은 state JSON만 읽는다. 실행 준비 조회는 등록된 Work Order의 계획·gate만 더 읽고,
  닫힌 작업은 실제 dependency target에 한해 정확한 locator로 조회한다. 등록된 Work의 `key.id`는
  기존 identity이며, 종료 dependency의 `work_state_targets`는 `{dependency ID: {ref, order_path}}`
  형태의 비권위 탐색 locator다. target의 실제 key.id와 마지막 종료 사건을 검증한다. 누락·취소·skip은
  완료로 추정하지 않는다. 이 locator에 상태를 복제하지 않는다.
- 등록 Work의 Step 목록은 state와 작업서의 `### R024/S01` 같은 계획 heading에서 얻는다.
  필수 gate가 막힌 Step은 건너뛰되 다음 실행 가능 Step을 반환한다. 동일 Work의 pending/in_progress
  finalization이 있으면 다음 구현 Step을 선택하지 않는다. 작업 전체 종료 gate와 Step gate는
  분리한다. optional gate는 차단하지 않으며 잘못된 gate·cycle은 진단한다.
- Reader·Coordinator·Linker는 같은 packaged dependency policy와 상태 snapshot으로 판단한다.
  Linker는 현재 상태를 매 호출 재검증하며 legacy Progress 상태로 덮어쓰지 않는다.
- Finalization은 상태 트리의 별도 필드를 사용하고 근거는 작업서에 남긴다. 기존 v1-v6 manifest는
  legacy corpus 전용이며 새 프로젝트에 재생성하지 않는다. 선택적 v7 검증은 현재 runtime binding과
  exact accepted target의 실행·승인·최종 정리를 검사한다. 검증 성공은 Main acceptance를 대신하지 않는다.
- 전체 소급 개편 시 historical metadata와 서술은 별도 작업으로 보존·정리한 뒤 marker를 마지막에
  추가한다. 이 구현 검증은 fixture에서 전환을 검증하며 실제 corpus 이전 완료를 주장하지 않는다.

## R015-A 선택적 점검 상태 확장

current.json v2는 선택적 review 객체를 지원한다. 기존 review 없는 v2는 그대로 읽고 쓰며
자동 설정·corpus 이전을 수행하지 않는다. review는 mode, closed_list, full_check_wait_for와
내부 closed_tokens/wait_tokens를 가진다. 토큰은 같은 ref의 새 종료·대기 등록을 이전 점검과
구분하는 occurrence 식별자이며 별도 상태·횟수·안내 위치가 아니다. Round 사건과 목록은
같은 transaction에서 갱신한다. Work·Step 종료는 횟수에 포함하지 않는다.
상세 정책·완료 경계는 [관리 흐름·연결 점검](key-standard-management-review.md)을 따른다.
기존 v2 reader가 확장 객체를 모를 수 있으므로 관련 패키지를 함께 배포하고 전환은 명시적으로 수행한다.
