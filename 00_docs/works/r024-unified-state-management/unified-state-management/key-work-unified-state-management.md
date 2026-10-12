---
doc_type: work_order
created_at: "2026-09-14"
document_lifecycle: active
approval: {state: pending}
work_status: planned
key:
  id: key.work.unified-state-management.order
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.work-recovery
    - key.topic.progress-update
    - key.topic.verification
    - key.boundary.scope-control
    - key.standard.project
    - key.standard.skill.author
    - key.work.derived-projection-normalization.order
    - key.work.current-work-state-simplification.order
    - key.work.author-terminal-status-reconciliation.order
---

# 상태 통합 관리 작업서

## Goal

Keystone에서 현재 상태를 어디에 기록하고 어떤 절차로 변경하는지 파악한 뒤, 상태를 일관되게
관리하면서 한 번의 상태 변경에 드는 탐색·기록·대조·검증 비용을 줄인다.

관리 중인 대상의 세부 현재 상태는 별도의 계층형 상태 문서 트리에서만 관리한다. 상태 문서는
현재 작업 확인의 단일 창구이자 현재 상태의 소유자이며, 작업서 이력을 매번 재생하는 사본이 아니다.
작업서는 개시·종료 표식과 중요한 사건·날짜·근거를 보존한다. 다른 색인·참고 문서의 상태 복제를
없애 반복 갱신 부담을 줄인다. 완료된 Round를 포함한 기존 문서 전체에 새 틀을 소급 적용한다.
구체적 저장 형식·계층과 이전 절차는 후속 질답과 조사로 정한다.

## 사용자 방향 — 상태 저장 권위와 문서 역할

1. 상태의 수가 많으므로 단일 파일 대신 Round 문서처럼 계층 구조의 상태 저장을 둔다.
2. 세부 현재 상태는 상태 전용 문서에서만 조회·변경한다. Round 작업서에는 `open` / `closed`
   개시·종료 표식과 날짜·종료 사유를 남긴다. 이는 원본 문서의 모든 상태값을 제거한다는 초기
   방향을 구체화한 예외이며, 세부 실행 상태를 중복 관리하는 것은 아니다.
3. 중요한 진행·결정·수락·검증 이력과 근거는 계속 해당 Round가 소유한다. 현재의 공통 결정 등
   기존 소유 예외를 이번 방향만으로 재배치하지 않는다.
4. 이력의 기록 수준은 현재 정도면 충분하다. 중요한 내용만 기록하며 디버깅용 상세 로그,
   모든 상태 전이의 자동·전수 기록이나 이벤트 재생 체계를 새 요구사항으로 만들지 않는다.
5. 과거 사실은 현재 상태값의 중복이 아니다. 과거 기록을 현재 상태에 맞춰 다시 쓰거나
   이력 전체를 상태 관리 문서로 옮기지 않는다.
6. 새 상태 관리 체계는 완료된 Round를 포함한 기존 문서 전체에 소급 적용한다. 상태값의
   이동만으로 끝내지 않고, 기존 텍스트의 상태 저장·변경·조회 관련 설명과 규칙도 새 틀에
   맞춰 개편한다. 과거 결정·수락·검증 사실과 근거는 보존하며 현재 규칙과 구분한다.

질답 근거: `clarify/20260914T045522Z-unified-state-management.md`

## 현재 상태와 작업 이력의 분리 계약

### 상태의 의미와 기록 위치

1. `complete`는 해당 작업과 필요한 검증이 끝난 작업 완료다. 수락·최종 정리가 남을 수 있으며
   그 경우 상태 트리에서 제외하지 않는다.
2. `closed`는 더 이상 관리할 일이 없는 관리 종료다. `open`은 관리 대상이며 그 안에서 여러
   세부 실행 상태를 가질 수 있다. Round 작업서의 관리 표식은 `open` / `closed`로 제한한다.
3. 관리 종료 시 해당 작업서에 종료 사유와 종료 날짜를 남기고 상태 트리의 항목을 제거한다.
   작업서 자체는 삭제하지 않는다. `closed:complete`, `closed:skipped`, `closed:cancelled`는
   종료 사유를 함께 보여주는 표기 예다. 필드 구조와 전체 사유 목록은 S02에서 확정한다.
4. 상태 트리는 관리 중인 대상의 현재 상태만 소유한다. 작업서는 중요한 진행·결정·수락·검증과
   종료·재개의 사건, 발생 날짜, 근거를 보존한다. 과거 기록은 현재 상태로 소급 갱신하지 않는다.
5. 다른 색인·참고 문서는 대상과 상태 조회 경로의 참조만 유지하며 세부 현재 상태를 복제하지
   않는다. 상태 트리에 없다는 사실만으로 완료를 추론하지 않는다.
6. 일상적인 작업 확인에서는 종료 작업서를 반복 탐색하지 않는다. 과거 확인이나 재개 요청이
   있을 때 해당 기록을 직접 찾는다. 종료 기록도 확인할 수 없으면 완료가 아니라 미확인으로
   구분하며 이를 해결하려고 매번 전체 과거 문서를 읽지 않는다.

### 갱신과 이력 경계

| 사건 | 상태 문서 | 작업서 기록 |
|---|---|---|
| 작업 개시 | 관리 대상 등록 | `open` 표식과 개시 날짜 |
| 일상적인 세부 진행 변화 | 현재 상태 갱신 | 매번 같은 상태나 전이를 기록하지 않음 |
| 중요한 결과·결정·수락, 차단·해소 | 필요한 현재 상태 갱신 | 사건·날짜·근거 기록 |
| 관리 종료 | 해당 항목 제거 | `closed` 표식, 종료 사유·날짜와 근거 기록 |
| 실제 작업 재개 | 관리 대상으로 다시 등록 | `open` 표식, 재개 사유·날짜 기록; 이전 종료 이력 보존 |

종료된 작업서의 단순 오탈자 정리는 그 자체로 재개가 아니다. 실제 관리할 일이 다시 생길 때
재개한다. 개시·종료·재개와 중요한 사건에서는 두 기록의 일관성을 확인하지만, 일반 상태 변화마다
작업서와 여러 참고 문서를 함께 수정하지 않는다. 부분 반영·동시 수정의 탐지와 복구 절차는 S02에서
정한다. 모든 전이의 전수 기록이나 이벤트 재생 체계를 요구하지 않는다.

### R025와의 경계

Round·Work·Step·Task의 정의와 파일 경계는 R025에서 다룬다. R024는 해당 정의를 임의로 확정하거나
Task를 필수 상태 관리 단위로 추가하지 않는다. 상태 종류별 실제 기록 단위와 R025 결과의 적용은
S02에서 대조한다. 두 Round 사이의 자동 실행·완료 gate는 추가하지 않는다.

## 생성·실행 경계

1. Round와 Work는 `planned / pending`이며 Active Step은 없다.
2. 생성 후 질답으로 목표와 범위, 통합의 의미를 구체화한다. 답변은 계획에 반영하되 구현
   실행 승인으로 추론하지 않는다.
3. Step 실행은 별도 명시적 진행 요청을 받은 뒤 시작한다. Production 변경 전에는 S02에서
   기준서 의미와 실제 적용 범위를 확정한다.
4. 아래 Step 구성과 완료 기준은 질답을 반영 중인 계획이다. 확정된 사용자 방향은 이 Work의
   계획 근거이며, 기존 프로젝트 기준의 상태 저장 계약은 S02 정합화 전에 대체하지 않는다.

## 현재 조사 근거

- Project 기준 `Source-derived Work State projection`은 Round 상태를 Round Index에,
  Work 상태를 aggregate Progress에, Step 상태를 combined 또는 개별 Progress에 둔다.
- Work Index의 상태와 Context Map·Index의 전역 pointer는 선택적 호환 표시이며 원본을
  대체하지 않는다. Author의 `Terminal status reconciliation`은 상태 전이 시 기존 현재
  요약을 찾아 원본과 대조하도록 요구한다.
- R023에는 Progress 외에도 Work·Round Index, Work Order의 실행 표, root works index와
  Context Map에 종료 정보가 나타난다. 이는 반복 기록의 관찰 사례이며 모든 전이에서 모든
  파일을 반드시 고친다는 뜻은 아니다.
- R013의 문제 기록에는 원본이 종료됐지만 Context Map의 진행 요약이 남았고 Work State는
  해당 서술을 권위로 읽지 않아 진단하지 않았던 사례가 있다.
- 초기 Reader 조사에서 Work State schema v5는 진단 없이 통과했고 R015/S01이 활성,
  R018이 계획 상태로 복구됐다. 이는 당시 조회 결과이며 전체 서술 정합성이나 비용 개선의
  검증 결과가 아니다. 실제 갱신 비용은 아직 측정하지 않았다.

근거 문서:

- `00_docs/standards/01_key-project-standard.md`: STD-KEYSTONE-019/020/026/055/058/062
- `00_docs/standards/skills/author/key-standard-author.md`: Progress ownership와 종료 정합화
- `00_docs/works/r011-work-model-evolution/derived-projection-normalization/key-work-derived-projection-normalization.md`
- `00_docs/works/r012-current-work-state-simplification/current-work-state-simplification/key-work-current-work-state-simplification.md`
- `00_docs/works/r013-author-terminal-status-reconciliation/author-terminal-status-reconciliation/key-work-author-terminal-status-reconciliation.md`
- `00_docs/works/r023-session-title-work-authoring-gate/session-title-work-authoring-gate/key-work-session-title-work-authoring-gate.md`

## Scope

Include:

- Round·Work·Step 상태, 문서 lifecycle·approval, finalization 등 상태 종류별 기록·권위·갱신 주체 조사
- 현재 원본, 현재 상태의 반복 표시, 계산 결과, 과거 이력의 구분
- Step 완료·Work 완료·Round 수락 등 대표 전이의 읽기·수정 파일과 검증 비용 조사
- 계층형 상태 전용 문서와 원본 문서의 역할 분리, 상태별 단일 기록·조회·변경 위치 설계
- `open` / `closed` 관리 표식, `complete` 작업 완료, 종료 사유·날짜 및 재개 기록의 구분
- 관리 중인 대상만 유지하는 상태 트리와 작업서의 중요 이력, 종료·재개 시 두 기록의 정합성
- 완료된 Round를 포함한 기존 문서 전체의 현재 상태값 이전과 관련 설명·규칙·조회 안내 개편
- Round 소유의 중요 이력과 과거 사실·근거를 보존하면서 새 틀에 맞추는 문서 개편
- 결정된 범위의 기준서 정합화, 문서·skill/runtime 적용과 전환·호환 검증 계획

Exclude:

- 미정 저장 형식·위치, 새 API, 자동 상태 전이 또는 이전 절차의 임의 확정
- 작업서의 개시·종료 표식 외에 세부 현재 상태를 원본·색인·참고 문서에 중복 유지하는 구조
- 이력 전체의 상태 문서 이전, 디버깅용 상세 이력, 모든 전이의 전수 기록·이벤트 재생 체계
- 과거 acceptance·verification evidence의 삭제나 현재 상태로 소급 재작성
- R015·R018 등 다른 Round의 작업 범위·상태 의미·우선순위 변경. 상태 저장 위치와 관련
  텍스트를 새 틀에 맞추는 개편은 포함한다.
- 소비 프로젝트 전체 migration, 관련 없는 탐색 성능 개선, publish·global install

## 미정 사항

1. 상태 전용 문서의 경로·계층·저장 형식과 원본 문서 연결 방식
2. 실제 상태 종류별 기록 단위와 계산 결과의 조회 방식
3. 전체 기존 문서의 이전 절차와 호환 필요성, 병렬 작업 충돌과 실패 복구 방식
4. 비용 개선을 판단할 대표 시나리오와 수용 가능한 기준
5. 세부 실행 상태와 종료 사유의 전체 목록, 승인·최종 정리 상태와의 관계 및 날짜 필드 형식
6. 종료·재개 중 일부 기록만 반영된 경우의 탐지·복구, 기존 이력에서 날짜를 확인할 수 없는 경우

## Step 계획

### R024/S01 — 상태 기록·갱신 현황 조사

- **Goal:** 현재 상태 관리의 구조와 실제 갱신 부담을 근거로 설명한다.
- **Scope:** 상태 종류, canonical source, 중복 표시, 읽기·쓰기 주체와 대표 전이 경로를 조사한다.
- **Source Context:** Project의 상태·권위 기준, Author ownership·종료 계약, 위 조사 근거와 관련
  Work State 소비 경로. 구현 탐색이 필요하면 확인된 문서·artifact 범위로 좁힌다.
- **Completion Criteria:** 상태별 원본·표시·이력 목록과 전이별 수정 대상·검증 경로가 있고,
  비용 관찰과 미측정 항목이 분리돼 있다.
- **Stop Conditions:** 현재 원본과 historical 기록을 구분할 수 없거나 조사에 범위 밖 수정이 필요하다.
- **Verification:** 대표 Step·Work·Round 사례의 원문과 런타임 조회를 대조하고 측정 조건을 남긴다.
- **Expected Output:** 상태 관리 현황과 전이 비용의 기준선.

### R024/S02 — 통합 방식 결정·기준 정합화

- **Goal:** 확정된 사용자 의도를 저장·변경·조회·검증 계약으로 만든다.
- **Scope:** 별도 상태 트리의 구조와 세부 상태의 단일 수정 지점을 정하고, 작업서의 개시·종료
  표식 및 중요 이력, 상태 트리 제외·재등록과 기존 문서 소급 개편·호환 경계를 구체화한다.
- **Source Context:** 질답 결과, S01 근거, Project·Author 및 실제로 영향받는 소비자 기준.
- **Completion Criteria:** 통합 대상과 권위가 명확하고 전환·실패 복구·동시 수정 방침 및 검증 기준이
  확정돼 있다. 이력은 중요한 내용만 기존 수준으로 기록하며 새로운 전수 기록 의무를 두지 않는다.
  `complete`와 `closed`, 종료 사유와 재개 조건을 구분하고 상태 항목 부재를 완료로 오인하지 않는다.
  Production 구현 전에 기준서를 정합화하거나 충분한 accepted 기준의 `no_change` 근거를 남긴다.
- **Stop Conditions:** 사용자 결정이 미해결이거나 기존 수락 의미·이력을 안전하게 보존할 수 없다.
- **Verification:** 선택·제외 대안과 이유, 구현 범위와 기준의 일치 여부를 검토한다.
- **Expected Output:** 수락된 통합 계약과 구체화된 적용·검증 범위.

### R024/S03 — 통합 관리 적용

- **Goal:** 확정된 통합 계약을 실제 기록과 변경·조회 흐름에 적용한다.
- **Scope:** S02에서 특정한 문서·skill/runtime·test와 승인된 이전 대상만 변경한다.
  이전 대상은 완료된 Round를 포함한 기존 문서 전체이며, 상태값과 새 틀의 영향을 받는
  설명·규칙·조회 안내를 함께 개편한다.
- **Source Context:** 수락된 기준, S02 적용 범위, 현행 상태 복구·갱신 구현.
- **Completion Criteria:** 세부 현재 상태와 중복 표시가 기존 원본·색인·참고 문서에서 제거되고,
  별도 상태 트리에서만 조회·변경한다. 작업서의 개시·종료 표식과 중요 이력은 보존하며
  종료 시 트리 제외·종료 기록, 재개 시 재등록·재개 기록이 함께 반영된다. 중요한 이력·근거를 보존하고
  불완전한 변경과 충돌을 숨기지 않으며 이전 전후 상태 의미를 보존한다.
- **Stop Conditions:** 미승인 저장 권위나 API·schema 변경, 추가 migration 또는 이력 재작성이 필요하다.
- **Verification:** 영향받는 전이·복구·호환 경로를 집중 검증한다. 생성 사본이 실제 변경 대상이면
  그 범위의 parity도 확인한다.
- **Expected Output:** 통합 관리 구현·문서와 필요한 이전 결과, 검증 근거.

### R024/S04 — 비용·정합성 검증

- **Goal:** 갱신 부담 감소와 상태 의미·복구 정확성을 함께 입증한다.
- **Scope:** S01과 동일 조건의 대표 전이, 상태 소비자 일치, 이력 보존과 실패 복구를 검증한다.
- **Source Context:** S01 기준선, 수락된 S02 검증 계약, S03 변경 결과.
- **Completion Criteria:** 수정 파일 수·반복 기록·검증 비용의 전후 비교가 있고 합의된 기준을
  충족한다. 수락된 기준·구현·상태 문서가 일치하며 남은 한계가 명시돼 있다.
- **Stop Conditions:** 비용 감소를 입증할 수 없거나 원본 충돌·복구 누락이 남는다.
- **Verification:** 관련 focused tests, Work State와 affected-scope 정합성을 확인한다.
  일반 진행, complete 후 수락 대기, 종료, 재개, 기록 누락·부분 반영 사례를 대조하고
  일상 조회가 종료 작업서를 반복 탐색하지 않는지 확인한다.
- **Expected Output:** 전후 비교, 완료 검증과 재개 가능한 잔여 사항 기록.

## 순서와 경계

S01 → S02 → S03 → S04는 제안하는 기본 순서다. 생성 후 계획 질답은 이 Step 실행과 별개로
이어간다. Production 구현 전 수락된 기준 정합화와 Round 종료 전 검증은 유지한다.
다른 Round와의 실행 dependency는 현재 확정하지 않는다.

## Round Completion Criteria

- [ ] 상태별 원본·반복 표시·계산 결과·이력이 근거와 함께 구분돼 있다.
- [ ] 계층형 상태 전용 저장의 구조와 적용 범위가 사용자 결정과 기준서로 확정돼 있다.
- [ ] 세부 현재 상태는 별도 상태 트리에서만 관리하고 작업서에는 개시·종료 표식과 중요 이력을 둔다.
- [ ] `complete` 후 관리할 일이 남은 대상은 유지하고 `closed` 대상은 종료 기록을 보존한 뒤 제외한다.
- [ ] 종료·재개의 부분 반영과 기록 누락을 완료로 오인하지 않으며 필요한 복구가 가능하다.
- [ ] 다른 참고 문서의 상태 복제를 제거하고 일상 작업 확인에서 종료 문서의 반복 탐색을 피한다.
- [ ] 완료된 Round를 포함한 기존 문서 전체에 새 틀이 적용되고 관련 설명·규칙·조회 안내가
  일치한다. 과거 사실·근거는 보존되며 현재 규칙과 혼동되지 않는다.
- [ ] 중요 이력은 기존 수준과 소유 위치를 유지하고 디버깅용·전수 전이 기록을 새로 요구하지 않는다.
- [ ] 구현·이전 결과가 확정된 계약에 맞고 상태 복구·수락·이력 의미를 보존한다.
- [ ] 대표 전이의 비용이 동일 조건에서 비교되고 합의된 개선 기준을 충족한다.
- [ ] 필요한 검증과 문서 정합화가 완료되고 남은 위험이 기록돼 있다.
