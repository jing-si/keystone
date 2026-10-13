---
doc_type: standard
created_at: "2026-10-13"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-10-13", accepted_by: main}
key:
  id: key.standard.management-review
  refs:
    - key.standard.project
    - key.standard.managed-work-state
    - key.work.keystone-consumer-goal-effectiveness-review.order
---

# 관리 흐름과 연결 점검

사용자가 수용한 R015 정책을 R015-A에서 실행 가능한 계약으로 정합화한다.

## 안내·편성

승인된 한국어 고정 안내문을 package reference로 배포한다. 신규 Init 또는 기존 프로젝트 첫
Round 생성·종료에서 운영 방식을 한 번 선택받는다. 일상 Reader 조회는 선택 질문을 반복하지 않는다.
일반형은 Round 범위 점검 Step과 5회 전체 점검 안내, 스프린트형은 하위 범위 점검과 최상위 전체
점검 Step을 편성한다. Round·Step 기본과 선택 Work·Task, 사용자 Round 생성 결정을 보존한다.

## 단일 상태와 사건

R024 current.json v2에 선택적 review 객체를 둔다. 없는 기존 v2는 미설정으로 읽고 자동 이전하지
않는다. review는 mode(general/sprint), closed_list, full_check_wait_for를 소유한다. count·마지막
안내 상태는 없다. 재종료와 새 대기 조건 보호용 occurrence token은 같은 객체 내부에만 보존하며
추가 상태 원장·파일을 만들지 않는다. 설정은 명시적 사용자 선택 뒤 수행한다.
모든 Round Closed에서 중복 없이 목록 추가, 재개에서 제거한다. Work·Step Closed는 횟수가 아니다.
대기 없음: general에서 양수 길이가 5배수인 Closed 사건만 안내한다. 대기 있음: 전부 closed_list에
포함되기 전에는 안내하지 않고 충족하면 매 Closed마다 안내한다. 거절은 목록을 변경하지 않는다.

## 스냅샷·완료

현재 관리 대상 변경을 커밋할 짧은 동안 쓰기를 조정한 뒤 별도 점검 워크트리를 만든다. 사용자
코드 실행·commit hook 우회·비밀정보 추가를 자동화하지 않는다. Main이 Git 작업과 검토를 수행한다.
점검 시작 ticket은 커밋과 대상 occurrence를 담은 일시적 세션 자료다. 필수 영구 evidence 파일이 아니다.
Closed 작업서→기준서→전체 선언 연결을 확인하고 진행 중 변경은 기존 내용과 충돌만 필요한 범위에서
본다. 큰 변경은 보류·담당 Round 대기 등록, 도구 미확인은 부분 점검이다. 두 경우 목록을 유지한다.
종료 점검 중인 최상위 자신을 대기로 등록하지 않는다.
점검 수정은 현재 관련 부분과 대조해 국소 반영한다. 결과 반영·후속 기록을 마친 뒤 Main의 완료
확인으로 점검한 occurrence만 제거한다. 새 종료·재종료·대기 등록은 보존한다. runtime은 의미 점검이나
사용자 수락을 자동 수행하지 않는다. 스프린트는 최상위 범위를 포함해 점검하고 결과 반영 후 Closed,
같은 종료 건을 정리한다. 시작 이후 재개된 최상위 건은 이전 점검으로 정리하지 않는다.

## Step 정의

새·수정 작업서는 key.defined_steps에 local Step ID(S01 등)를 최소 정의로 기록한다. 이는 Step
본문 계획의 식별 정보이며 상태나 별도 registry가 아니다. 진행 step_ref를 정의로 승격하지 않는다.
Linker는 명시 정의에서 존재를 판정하고 없으면 work_gate_step_unidentified로 본문 확인을 요구한다.
정의 목록이 명시돼 있고 대상이 없을 때만 work_gate_step_invalid다. Reader·AI가 본문 의미를 판단하며
기존 문서 전체를 소급 보강하지 않는다. managed Work State는 기존 heading 호환을 유지한다.
