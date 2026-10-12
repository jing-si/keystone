---
doc_type: work_round
created_at: "2026-09-14"
document_lifecycle: active
approval: {state: pending}
round_status: planned
key:
  id: key.work.round.r024-unified-state-management.index
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.work-recovery
    - key.boundary.scope-control
    - key.standard.project
    - key.work.unified-state-management.order
---

# R024 상태 통합 관리 작업서 색인

Keystone 상태의 기록 위치와 갱신 절차를 조사하고, 상태 변경에 필요한 반복 기록·대조 비용을
줄인다. 세부 현재 상태는 별도 계층형 상태 트리에서만 조회·변경하고, 작업서에는 `open` / `closed`
표식과 개시·종료 날짜, 종료 사유 및 중요 이력을 남긴다. `complete`는 작업 완료이고 `closed`는
관리 종료다. 종료 대상은 상태 트리에서 제외하며 재개 시 다시 등록한다. 참고 문서는 현재 상태를
복제하지 않는다. 완료된 Round를 포함한 기존 문서 전체에 소급 적용하며, 상태값뿐 아니라 관련
설명·규칙·조회 안내도 새 틀에 맞춰 개편한다. 상태 문서의 구체적 구조와 이전 절차는 추가로
구체화한다.

## 계획

| 순서 | Step | 목적 |
|---|---|---|
| S01 | 상태 기록·갱신 현황 조사 | 원본·중복 표시·이력과 상태 전이별 비용을 확인한다 |
| S02 | 통합 방식 결정·기준 정합화 | 질답 결과와 조사 근거로 저장·변경·조회 계약을 정한다 |
| S03 | 통합 관리 적용 | 확정된 계약에 따라 필요한 문서·런타임을 변경한다 |
| S04 | 비용·정합성 검증 | 상태 복구 정확성과 갱신 비용 개선을 함께 확인한다 |

## 문서와 복구

- Work 색인: `unified-state-management/00_key-index.md`
- Goal·Scope·Step 계약: `unified-state-management/key-work-unified-state-management.md`
- 실제 실행 상태와 resume point: `unified-state-management/key-progress.md`

현재는 생성만 승인된 계획이다. 질답은 계획 구체화를 위한 것이며 Step 실행이나 구현 승인을
대체하지 않는다. 다른 Round의 상태 저장 위치와 관련 텍스트는 개편 대상이지만,
그 작업 범위·상태 의미·우선순위는 변경하지 않는다.
