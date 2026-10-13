---
doc_type: progress
created_at: "2026-10-12"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-10-12", accepted_by: main}
work_status: complete
work_ref: R025/work-hierarchy-definition
step_ref: R025/S02
key:
  id: key.work.work-hierarchy-definition.progress.definition
  refs: [key.work.work-hierarchy-definition.order]
---

# R025/S02 정의 확정과 기준 정합화

S01 조사 결과와 사용자 답변을 바탕으로 정의·기준 정합화를 완료하고 Main이 이 범위를 수락했다.
공통 기준은 목표 계약으로 반영했으며 실제 runtime·설치본·기존 corpus 적용은 수행하지 않았다.

## 반영한 사용자 결정

1. 부모·하위 Round 생성은 사용자 결정이며 AI는 필요 시 권유하고 기다린다.
2. Work는 사용자 지정 또는 AI의 범위 내 판단으로 선택적으로 생성하고 이유·범위·관계를 안내한다.
3. G01/Q01: Task는 재개에 필요한 내용만 Step 기록에 남기고 독립 상태·수락 절차를 두지 않는다.
4. G01/Q02: Work는 기본적으로 Round 작업서 안에 구분하고 필요할 때만 파일을 분리한다.

질답은 `clarify/20261012T091957Z-work-hierarchy-definition.md`에 보존했다.
모든 Task의 영속 ID·상태 추적과 Work마다 별도 작업서 생성은 선택하지 않은 대안이다.

## 정합화와 검증

- Project: 용어, 선택적 Work·Task, 파일·상태·식별·변경·완료 책임과 구현 적용 경계를 명문화했다.
- Author: Work 생성·안내·선택적 파일 분리와 Task 기록, Work 없는 질답 위치를 정합화했다.
- Reader: Round 직접 Step 복구와 선택적 Work 탐색, Task의 재개 단서 역할을 명시했다.
- Coordinator 개발 명세: 같은 생성·실행 경계를 추가하고 문서 전체의 기존 pending 상태를 보존했다.
- R024 관리 상태 기준: 정의 확정과 실제 wire·runtime 전환을 구분했다. Task를 상태 항목에
  추가하거나 현재 저장 형식을 변경하지 않았다.

Work가 없으면 전체 목표·완료 조건은 Round가 직접 소유하도록 기본 구조에서 도출했다.
새 Step은 기존 Round 단위 S01 규칙을 유지해 local Round 내 중복을 금지하고, Work는 제목·범위와
필요한 stable ID로 구분한다. 기존 ID·번호·이력과 하위 Round의 2단계 제한은 변경하지 않았다.

다섯 기준서의 변경 diff를 대조했고 기존 frontmatter·ID/ref/typed-relation comment를 보존했다.
본 개정의 수락은 이번 범위에 한정하며 Coordinator의 다른 pending 의미를 수락하지 않는다.
S03에서 사례별 생성·지정·변경·종료·복구와 후속 구현 경계를 검증한다.
