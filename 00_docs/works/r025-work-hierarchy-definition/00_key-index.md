---
doc_type: work_round
created_at: "2026-10-12"
document_lifecycle: active
approval: {state: pending}
round_status: planned
key:
  id: key.work.round.r025-work-hierarchy-definition.index
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.standard.project
    - key.work.work-hierarchy-definition.order
---

# R025 작업 계층 정의

Round·Work·Step·Task의 의미, 포함 관계, 사용자와 AI의 책임 및 문서 분리 기준을 명확히 한다.
기존 Work를 제거하는 것을 전제로 삼지 않고, 필수 Step과 AI가 필요할 때만 만드는 Task를 구분한다.

## 계획

| 순서 | Step | 목적 |
|---|---|---|
| S01 | 현행 계층과 용례 조사 | 정의·문서 구조·실제 사용의 차이를 확인한다 |
| S02 | 정의 확정과 기준 정합화 | 단위별 책임과 경계, 필수·선택 여부를 명문화한다 |
| S03 | 정의 일관성 검증 | 사례와 영향 문서를 대조하고 후속 적용 범위를 정리한다 |

## 문서

- Work 색인: `work-hierarchy-definition/00_key-index.md`
- 작업서: `work-hierarchy-definition/key-work-work-hierarchy-definition.md`
- 진행 기록: `work-hierarchy-definition/key-progress.md`

현재는 작업서 생성만 승인된 `planned / pending` 계획이며 Active Step은 없다.
생성 후에는 R024 상태 통합 관리 질답으로 돌아간다. R025 실행을 자동으로 시작하지 않는다.
