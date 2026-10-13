---
doc_type: work_round
created_at: "2026-10-12"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-10-12", accepted_by: main}
round_status: accepted
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
Round·Step을 기본 틀로 두고 Work·Task는 선택적으로 사용한다. 부모·하위 Round 생성은
사용자가 결정하며, Work는 사용자 지정 또는 AI 판단으로 Round 범위 안에서 구성한다.
AI가 Work를 생성하면 이유·범위·Round 및 Step과의 관계를 안내한다.

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

2026-10-12 사용자 실행 요청과 두 질답을 바탕으로 S01~S03의 조사·정의·기준 정합화·사례
검증을 완료했다. Main이 R025 문서 범위를 수락해 Round는 `accepted`, Work는
`complete / accepted`, active_steps는 `[]`다. 새 구조의 runtime·skill source 적용과 설치·
기존 corpus 이전은 S03에 명시한 후속 범위이며 이번 완료에 포함하지 않는다.
