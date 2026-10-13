---
doc_type: work_order
created_at: "2026-10-13"
document_lifecycle: active
approval: {state: pending}
work_status: complete
key:
  defined_steps: [S01, S02, S03, S04, S05]
  id: key.work.r015-a.management-flow.order
  refs:
    - key.standard.project
    - key.work.keystone-consumer-goal-effectiveness-review.order
---

# R015-A 관리 흐름 개선 구현 작업서

## Goal

문서의 반복 확인 비용을 줄이면서 작업서·기준서·코드 연결의 정합성을 보존한다.
[부모의 수용된 정책·16개 시나리오](../../keystone-consumer-goal-effectiveness-review/key-work-keystone-consumer-goal-effectiveness-review.md)와
[고정 안내문](../../keystone-consumer-goal-effectiveness-review/templates/work-structure-and-review-mode.ko.md)을
원본으로 사용하며 전문을 복제하지 않는다.

## 생성·실행 경계

2026-10-13 사용자가 R015 하위 구현 Round 생성과 부모의 참고 문서 구조 조정을 승인했다.
최초에는 planned/pending으로 생성했다. 이후 같은 날 사용자 구현 승인으로 S01~S05를 진행했다.
구현·검증은 완료했고 사용자 수용 대기다. 설치·배포·Uptendo 변경은 수행하지 않았다.

## Source Context와 병렬 작업

- R024: state/current.json 단일 상태 파일, 상태별 그룹·사건 로그·digest·lock·pending 복구를 구현했다.
  생성 시 complete/pending이며 최종 수락 전이다. 저장 계약은 현행 기준서를 따른다.
- R025: 단위 정의·기준 정합화 complete/accepted. runtime·wire 적용 완료로 확대하지 않는다.
- R026: 아이디어 노트 complete/accepted. 아이디어 기능은 이 Round 수정 범위 밖이다.
- R027: 질답 기록·질문 변경 스킬 작업 진행 중. Author·Reader·공통 기준 파일이 겹칠 수 있다.
  해당 변경을 재확인하고 보존하며 질답 정책을 재설계하지 않는다.
- 현재 repository는 legacy 문서 상태 복구 모드다. R024 구현 완료만으로 실제 corpus 이전을 가정하지 않는다.

## Scope

포함: Init 고정 안내·운영 방식 선택, Author 점검 Step·최소 Step 정의 metadata,
Reader/Linker 역할 연결, 단일 상태 파일의 두 목록·Closed/재개 처리, 점검 스냅샷·대기·결과 반영,
스프린트 종료, 필요한 기준·스킬 source·runtime·관련 테스트.

예상 위치: 00_docs/standards/01_key-project-standard.md, key-standard-managed-work-state.md,
관련 skills 기준과 skills/keystone-{init,author,reader,linker,coordinator}/,
scripts/managed_work_state.py 및 관련 integration·runtime 생성기, skills/tests/의 관련 검사.
정확한 변경 파일은 착수 시 좁힌다. 생성된 사본은 canonical source와 생성기로 관리한다.

제외: R018 탐색 알고리즘 재설계, R026 아이디어·R027 질답 정책 변경, 모든 문서 metadata 일괄 보강,
기존 corpus 자동 이전, 전역 설치·배포, Uptendo 수정, 코드 동작 테스트를 Keystone 점검 정책으로 강제.

## Step 계획

### R015-A/S01 · 기준 정합화

- Goal/Scope: 부모 정책과 R024·R025·R027 최신 계약을 대조하고 관련 기준을 정합화한다.
- Completion: 안내·점검·목록·재개·스프린트 종료와 역할 책임을 정의한다. 일치하는 기준은 이유 있는 no_change로 둔다.
- Verification: R024 상태 계약 및 R027 공유 표면을 대조한다. 코드 변경 전 00_docs/convention.md 존재 여부와 적용 규칙을 확인한다.
- Stop: R024 저장 의미나 수용 여부 때문에 구현 기준이 불명확하거나 사용자 정책 변경이 필요하다.

### R015-A/S02 · 안내와 작업 편성

- Goal/Scope: 고정 안내문 재사용, 최초 운영 방식 선택, 점검 Step과 최소 Step 정의 metadata를 적용한다.
- Completion: 신규·기존 첫 적용에 동일 문안을 사용하고 불필요한 재질문·필수 Work/Task를 만들지 않는다.
- Verification: 문안 일치, Round 직접 Step/선택 Work, 실제 Step 부재와 정의 미식별 구분을 확인한다.
- Stop: 정의 metadata를 기존 문서 전체에 강제하거나 Linker에 광범위한 본문 의미 해석이 필요해진다.

### R015-A/S03 · 상태와 안내 조건

- Goal/Scope: R024 단일 파일에 운영 방식·closed_list·full_check_wait_for와 사건 소비를 연결한다.
- Completion: 5배수 안내, 대기 우선, 충족 후 매 Closed 재안내, 재개 제거, 동일 종료 재시도 및 병렬 변경 보존.
- Verification: 부모 시나리오의 정상·거절·대기·재개·재종료·동시 쓰기·복구를 관련 테스트로 검증한다.
- Stop: 별도 count·안내 위치·독립 점검 상태 파일이나 기존 corpus 무승인 이전이 필요하다.

### R015-A/S04 · 점검과 결과 반영

- Goal/Scope: 현재 변경 커밋·점검 워크트리, Closed 작업서→기준서→연결 확인, 큰 변경 대기·부분 재개,
  현재 공간에 국소 수정 반영 및 스프린트 전체 점검→결과 반영→최상위 Closed→동일 건 정리를 구현한다.
- Completion: 진행 중 작업은 기존 내용과 충돌만 필요한 범위에서 보고, 실제 처리한 종료 건만 제거한다.
- Verification: 스냅샷 이후 추가·재종료 보존, 파일 전체 덮어쓰기 방지, 자기 대기 금지와 오류/미확인 구분.
- Stop: 큰 수정·사용자 의미 결정이나 승인 범위 밖 변경이 필요하다.

### R015-A/S05 · 통합 검증과 라운드 정합성 점검

- Goal/Scope: 부모 16개 수용 시나리오 및 스프린트 보완 규칙에 기준·구현·검증 근거를 대조한다.
- Completion: 관련 테스트와 기준/스킬/상태 연결이 일치하고 잔여 문제·후속 이전 범위를 보고한다.
- Verification: 실제 영향 범위의 contract/runtime 검사와 필요한 generated-copy 검증을 수행한다.
  브라우저는 요청 시에만 사용한다. 전체 release gate·설치 성공을 자동 요구하지 않는다.
- Stop: 미확인 범위가 남거나 테스트 성공을 사용자 수용으로 대신해야 한다.

## Completion Criteria

부모 정책과 고정 문안을 보존하고 16개 시나리오·스프린트 종료 보완을 실제 구현 근거로 검증한다.
기준·문서·스킬·runtime 연결을 확인하고 사용자 수용 뒤 상태를 정리한다. 하위 수용은 부모 자동 수용이 아니다.

## 구현 결과 — 2026-10-13

- 기준: `00_docs/standards/key-standard-management-review.md`와 관련 기준의 점검 책임·순서를 정합화했다.
- 안내: Init reference가 배포 원본이며 R015 고정 문안과 일치 테스트로 검증한다. 생성기로
  Author·Reader·Coordinator·Linker에 같은 본문·워크플로를 복제한다. 설치 패키지는 00_docs 없이 동작한다.
- 상태: `scripts/managed_work_state.py`의 review configure/defer/finish, review-ticket 및 Round 사건
  원자적 연동을 구현했다. 두 목록은 같은 current.json에 있으며 새 종료·대기 occurrence를 보존한다.
- 복구: 선택적 Work 없이 Round 직접 Step을 managed state 및 execution projection에서 지원한다.
- Linker: key.defined_steps를 정의로 사용한다. 정의 미식별은 warning/unknown으로 Reader 확인에 남기고
  gate는 차단한다. 명시된 정의에 없는 Step만 invalid다. 의미 검토를 자동 성공 처리하지 않는다.
- 점검 실행: Git 커밋·워크트리 생성·의미 검토·현재 공간 반영은 Main이 package workflow를 따라 수행한다.
  state helper는 실제 Git commit 여부나 AI 검토 품질을 인증하지 않고 명시된 완료 결과만 처리한다.
- 설치·기존 corpus 이전·Uptendo 실제 전체 점검은 수행하지 않았다. legacy에서 목록만 설정하고
  실제 Closed 사건은 구형 문서로 처리하는 혼합 전환을 금지한다.

## Verification 결과

- shared skills: 216 tests, OK (1 skipped).
- Linker: 398 tests, OK; Author: 96 tests, OK; Coordinator: 34 tests, OK; Reader: 3 tests, OK.
- 새 점검 동작·고정 문안·직접 Step 복구와 새 Step 정의/미식별 tests를 포함한다.
- 임시 Git fixture의 background gc 정리 경쟁은 테스트 프로세스에만 gc.auto=0을 적용해 재검증했다.
- generated runtime/reference parity, affected Python compileall, Work State와 문서 링크·diff를 검증했다.
- 브라우저·실제 설치·배포·소비 프로젝트 이전은 검증 범위 밖이다.
