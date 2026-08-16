---
doc_type: work_round
created_at: "2026-08-17"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-17", accepted_by: main}
round_status: accepted
key:
  id: key.work.round.r013-author-terminal-status-reconciliation.index
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.progress-update
    - key.topic.acceptance
    - key.topic.verification
    - key.topic.question-flow
    - key.topic.document-authoring
    - key.standard.skill.author
    - key.standard.skill.clarify
---

# R013 Author Terminal Status Reconciliation 작업서 색인

R013은 Step·Work·Round 상태가 실제로 전이될 때만 Author가 bounded status projection을
대조하도록 종료 계약을 명확히 한다. 현재 상태와 navigation을 위한 기존 요약은 owning
Progress·Round source와 맞추되, 명시적인 historical narrative와 as-of 기록은 보존한다.

또한 하나의 큰 검토 주제에서 나온 항목을 실제 문서 수정 관련성에 따라 그룹화하고, Clarify가
그룹 안의 질문을 하나씩 마친 뒤에만 Author가 그 그룹의 문서 범위를 한 번 반영하는 계약을
계획한다. 대주제별 Q&A log는 기억 복구용 Work attachment이며 결정·평가·상태 권위를 갖지 않는다.

이 Round는 S01-S04를 구현·검증하고 Main acceptance로 complete + accepted 상태로 닫았다.

<!-- key: id=key.work.round.r013.execution-order refs=key.topic.work-sequence key.topic.progress-update -->
## 실행 순서

| 순서 | Step | 상태 | 목적 |
|---|---|---|---|
| S01 | Author Terminal Reconciliation Standard | complete, accepted | 상태 전이 시 bounded projection 후보와 historical 예외를 구분하는 Author 기준을 명확히 했다 |
| S02 | Author Runtime Contract and Regression | complete, accepted | 설치된 Author skill에 같은 계약을 반영하고 focused contract test로 고정했다 |
| S03 | Current Projection Repair and Verification | complete, accepted | R012 상태 요약 불일치를 정정하고 Work State·focused test로 검증했다 |
| S04 | Clarify Group Application Contract | complete, accepted | 관련성 기반 그룹, 질문 단위 log와 그룹 종료 후 Author 반영 계약을 기준서·skill·test에 고정했다 |

현재 active Step은 없다. S01-S04의 실행 증거와 acceptance는
`author-terminal-status-reconciliation/key-progress.md`와 Step Progress에서 확인한다.

<!-- key: id=key.work.round.r013.boundaries refs=key.boundary.scope-control key.topic.verification -->
## Round 경계

- 상태가 전이되지 않은 일반 문서 변경에는 terminal reconciliation을 실행하지 않는다.
- 검사 범위는 owning Round subtree, root works index와 Context Map의 exact Round/Step ref로 제한한다.
- 명시적인 historical log, as-of snapshot과 과거 진행 서술은 소급 수정하지 않는다.
- 범용 Markdown 상태 parser, 자동 updater, 새 persistent projection artifact를 만들지 않는다.
- 일반 종료에 full graph, package, repository 또는 installer 검증을 강제하지 않는다.
- Clarify 그룹은 질문 개수나 표시 순서가 아니라 함께 수정해야 하는 문서·section과 원자적
  일관성을 기준으로 AI가 구성한다.
- 질문은 항상 한 번에 하나만 진행하고, Q&A log 갱신과 그룹 종료 후 원천 문서 반영을 구분한다.
- Q&A log에 별도 group decision, Author application, 평가 또는 진행 상태를 만들지 않는다.

<!-- key: id=key.work.round.r013.reading-rules refs=key.topic.work-recovery key.topic.work-sequence -->
## 복구 규칙

1. R013 목표와 Step 순서는 이 Index를 읽는다.
2. 상세 범위, completion criteria와 Change Set은 Work Order를 읽는다.
3. 실제 상태, 증거와 다음 action은 Progress를 읽는다.
4. R013은 accepted history이며 후속 변경은 새 Work scope에서 시작한다.
