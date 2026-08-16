---
doc_type: work_order
created_at: "2026-08-17"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-17", accepted_by: main}
work_status: complete
key:
  id: key.work.author-terminal-status-reconciliation.order
  refs:
    - key.doc.work
    - key.topic.progress-update
    - key.topic.acceptance
    - key.topic.verification
    - key.topic.skill-contract
    - key.topic.question-flow
    - key.topic.document-authoring
    - key.topic.work-recovery
    - key.standard.skill.author
    - key.standard.skill.clarify
---

# Author Terminal Status Reconciliation 작업서 및 Change Set

<!-- key: id=key.work.author-terminal-status-reconciliation.order.goal refs=key.section.goal key.topic.progress-update -->
## Goal

Step·Work·Round 상태가 실제로 전이될 때 Author가 권위 source와 기존 current/navigation 상태
요약을 bounded하게 대조하도록 종료 계약을 명확히 한다. Optional projection은 없어도 되지만
존재하는 비역사적 projection이 stale 상태로 남은 채 closure가 완료되는 것은 허용하지 않는다.

큰 검토 주제에서 나온 여러 수정 항목은 실제 문서 적용 관련성에 따라 그룹으로 구성한다.
Clarify는 그룹 안에서 질문을 반드시 하나씩 진행하고, 그룹에 필요한 질문이 끝나면 Author가
그룹의 문서 수정 범위를 한 번 반영한다. 대주제별 Q&A log는 이 흐름의 기억 복구만 돕고 결정,
평가, 진행 상태 또는 원천 문서 권위를 갖지 않는다.

<!-- key: id=key.work.author-terminal-status-reconciliation.order.problem refs=key.topic.work-recovery key.topic.verification -->
## 문제와 근거

1. Author 기준과 skill은 Main acceptance 뒤 Work/Progress/index/Context Map 동기화를 이미
   요구한다.
2. 그러나 `active_steps`, `global_state`, aggregate state 중심 표현만으로는 사람이 작성한
   실행순서·navigation 상태 표가 종료 reconciliation 대상인지 명확하지 않다.
3. R012의 authoritative Round·Progress와 canonical Work State는 terminal accepted 상태지만,
   Context Map의 R012/S02-S04 요약에는 중간 `in progress | planned` 상태가 남았다.
4. Work State는 이 narrative 표를 current authority로 읽지 않으므로 diagnostics 0이어도 사람용
   navigation projection의 불일치를 별도로 막아야 한다.
5. 현재 Clarify 계약은 한 topic씩 질문하고 topic 종료 뒤 reflection과 update plan을 만들지만,
   하나의 큰 검토 결과를 관련 문서 수정 단위로 먼저 그룹화해 순차 처리하는 계약은 없다.
6. 질문이 여럿인 topic을 완료할 때마다 문서를 수정하면 같은 수정 범위를 반복해서 열 수 있고,
   반대로 모든 topic이 끝날 때까지 미루면 이미 결정된 범위와 대화 맥락을 잃을 수 있다.
7. 질문·답변 기록에 별도 group decision, Author application, 완료·평가 field를 두면 단순 기억
   보조 log가 또 하나의 판단·상태 source처럼 해석될 위험이 있다.

<!-- key: id=key.work.author-terminal-status-reconciliation.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- Author 기준의 `Acceptance finalization`, Progress ownership과 Verification에 terminal status
  reconciliation 경계 추가
- 상태 전이 때만 exact Round/Step ref를 bounded source set에서 확인하는 절차
- Step, Work, child Round와 parent Round 종료별 최소 동기화 대상 명시
- Optional projection의 부재 허용과 existing non-historical projection의 stale 금지 구분
- Historical narrative, as-of snapshot과 과거 진행 로그 보존 규칙
- 설치된 Author skill의 self-contained runtime contract 정합화
- Project Author 기준과 installed skill의 계약 parity를 확인하는 focused regression test
- 현재 `00_docs/key-context-map.md`의 R012/S02-S04 상태 요약 정정
- 큰 검토 주제에서 나온 항목의 관련성 기반 Clarify 그룹 구성과 순차 처리 계약
- 같은 대상 문서·section, 답변 간 결합과 원자적 적용 필요성을 사용하는 AI 그룹 판단 기준
- 그룹 안에서 항상 한 번에 하나의 질문만 진행하는 불변 조건
- 각 답변 뒤 최소 Q&A log를 갱신하고, 그룹 질문이 모두 끝난 뒤 그룹 범위의 원천 문서를
  한 번 수정하는 Author 경계
- 작업서 node 아래 `clarify/{YYYYMMDDTHHmmssZ}-{topic-slug}.md` 경로에 추적되는 대주제별 log
  파일을 하나 두고 그 안에 `G01`/`Q01` 계층으로 모든 그룹과 실제 질문·답변·답변일시를
  기록하는 형식. 파일명 timestamp는 UTC를 사용한다.
- Q&A log의 비권위·비평가 성격, 선택적 질문 단위 키메타와 필요한 경우에만 작업서에서
  log를 참조하는 규칙
- Project Clarify·Author 기준과 설치된 두 skill의 self-contained runtime contract 정합화
- Clarify 그룹 처리와 Q&A log 계약을 고정하는 focused regression test

Exclude:

- 상태 전이가 없는 일반 문서 수정에서의 reconciliation 실행
- document root 전체에 대한 무조건적 전수 수정
- historical Progress 로그나 accepted evidence의 소급 rewrite
- 범용 Markdown 표 parser, 자동 문서 updater 또는 새 persistent projection artifact
- canonical Work State의 authority 또는 schema 변경
- 기본 종료 경로에 Linker graph, full repository/package/installer 검증 강제
- finalization manifest, acceptance event, snapshot, key, receipt 또는 외부 evidence 생성
- Q&A log를 decision record, Progress, 평가 자료, completion evidence 또는 source authority로 사용
- 그룹별 Q&A 파일, 질문별 파일 또는 미응답 질문을 반복하는 별도 remaining-question section 생성
- `Group Decision`, `Author Application`, 질문 충분성, 그룹 완료 상태 같은 해석용 field 추가
- Q&A log의 매 답변 기록을 이유로 full Author source application, graph reconstruction, Work State
  또는 package-wide verification 실행

<!-- key: id=key.work.author-terminal-status-reconciliation.order.baseline refs=key.topic.progress-update key.topic.acceptance -->
## 수락된 방향

1. Terminal reconciliation은 `work_status`, `approval.state`, `round_status` 또는 `active_steps`가
   실제로 바뀔 때만 수행한다.
2. 기본 후보 범위는 owning Progress와 Work/Round index, root works index, Context Map이며 해당
   Round/Step exact ref가 있는 current/navigation 요약만 갱신한다.
3. Optional projection은 생략 가능하지만 존재하는 current/navigation projection은 stale 상태로
   남길 수 없다.
4. Historical narrative와 as-of 기록은 current summary로 오인되지 않는 한 보존한다.
5. 기본 검증은 exact-ref 검색, canonical Work State와 focused contract test로 제한한다.
6. 하나의 대주제에서 나온 항목은 질문 순서나 개수가 아니라 함께 영향을 받는 문서·section,
   답변 사이의 의미 결합과 한 번에 적용해야 일관성이 유지되는지를 AI가 판단해 그룹화한다.
7. 그룹 안에서는 한 번에 하나의 질문만 진행한다. 질문이 충분히 끝나면 그 그룹의 결정된 수정
   범위를 Author가 한 번 반영한 후 다음 그룹으로 이동한다.
8. 대주제별 Q&A log에는 모든 그룹을 함께 기록한다. 답변을 받을 때마다 질문, 답변과
   답변일시만 가볍게 갱신하고, 별도의 group decision·Author application·평가·상태를 두지 않는다.
9. 비어 있는 답변은 미응답으로 해석하며 별도 remaining-question 목록을 만들지 않는다.
10. 실제 원천 문서에 영향을 준 질문만 선택적으로 관련 key ref를 가질 수 있다. 이 ref와
    작업서의 선택적 log link는 탐색 보조일 뿐 edit authority나 평가 근거가 아니다.

기본 Q&A log는 다음 최소 구조를 사용한다. 파일 단위는 대주제, `G01`은 함께 수정할 범위,
`Q01`은 실제로 한 번에 진행한 질문이다. 영향 참조가 필요한 질문에만 heading 바로 앞에
선택적 키메타를 추가한다.

```markdown
# {대주제}

## G01 - {수정 범위}

### Q01 - {질문 요약}

- 질문:
- 답변:
- 답변일시:
```

<!-- key: id=key.work.author-terminal-status-reconciliation.order.execution-plan refs=key.topic.work-sequence key.topic.verification -->
## 실행 계획

| Step | 상태 | 변경 범위 | 완료 경계 |
|---|---|---|---|
| R013/S01 | complete, accepted | Author 기준서와 기준서 index | 상태 전이 trigger, bounded 후보, terminal 단위별 sync와 historical 예외를 명확히 했다 |
| R013/S02 | complete, accepted | `skills/keystone-author/SKILL.md`, 기존 focused contract test | project source와 installed contract가 같은 의미를 가지며 회귀 test로 고정했다 |
| R013/S03 | complete, accepted | 현재 Context Map R012 요약과 직접 관련 검증 | R012/S02-S04가 authoritative source와 일치하고 Work State·focused test가 통과했다 |
| R013/S04 | complete, accepted | Project Clarify·Author 기준, 두 installed skill, focused contract test | 관련성 기반 그룹, 질문 단위 log와 그룹 종료 후 한 번의 문서 반영 계약을 동일하게 재현했다 |

S02는 S01의 기준 문안이 확정된 뒤 진행한다. S03은 S01-S02 결과를 함께 검증한다. S04는
terminal status projection과 별개의 Clarify 그룹 적용 경계를 다루며, 앞 Step의 상태를 자동
전이하지 않는다.

<!-- key: id=key.work.author-terminal-status-reconciliation.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

| Surface | Owner | Required change | Verification |
|---|---|---|---|
| Author Standard | Author | acceptance finalization과 verification에 bounded terminal reconciliation 추가 | 문안·scope·historical boundary review |
| Author Standard Index | Author | Author 책임 요약에 terminal status reconciliation 추가 | index link와 설명 일치 |
| Author Skill Source | Main | self-contained installed contract에 같은 trigger·scope·stop boundary 반영 | standard/skill phrase parity |
| Shared Contract Test | Main | existing projection stale 금지와 historical 보존 계약 고정 | focused `unittest` |
| Current Context Map | Author | R012/S02-S04 navigation 상태를 terminal source와 일치시킴 | exact-ref 검색과 Work State |
| Project Standard | Author | Work-attached clarification log의 경로, 비권위와 선택적 key ref 경계 추가 | source/derived/log authority 문안 review |
| Clarify Standard and Index | Author | 관련성 기반 그룹 queue, 한 질문 불변 조건, 답변 log와 그룹 종료 handoff 추가 | workflow·scope·output contract review |
| Author Standard and Index | Author | 답변별 lightweight log 갱신과 그룹 종료별 원천 문서 적용을 분리 | mode·write boundary review |
| Clarify and Author Skill Sources | Main | 두 installed skill에 self-contained group/log/application 계약 반영 | standard/skill phrase parity |
| Clarify Group Contract Test | Main | 대주제 파일, 그룹·질문 구조, 금지 field와 적용 시점 계약 고정 | focused `unittest` |

<!-- key: id=key.work.author-terminal-status-reconciliation.order.completion refs=key.topic.acceptance key.topic.verification -->
## Completion Criteria

<!-- key: id=key.acceptance.author-terminal-status.trigger -->
- `R013-CC-01` Author terminal reconciliation이 실제 상태 전이에서만 실행되고 일반 문서 수정의
  기본 비용이 되지 않는다.
<!-- key: id=key.acceptance.author-terminal-status.bounded-scope -->
- `R013-CC-02` 후보 탐색이 owning Round subtree, root works index, Context Map의 exact ref로
  제한되고 관련 없는 문서를 자동 수정하지 않는다.
<!-- key: id=key.acceptance.author-terminal-status.projection-freshness -->
- `R013-CC-03` Optional projection은 부재할 수 있지만 존재하는 비역사적 current/navigation
  projection은 authoritative Progress·Round state와 일치해야 한다.
<!-- key: id=key.acceptance.author-terminal-status.history-preservation -->
- `R013-CC-04` Historical log, as-of snapshot과 과거 진행 서술은 소급 수정하지 않는다.
<!-- key: id=key.acceptance.author-terminal-status.unit-boundaries -->
- `R013-CC-05` Step, Work, child Round와 parent Round 종료별 최소 동기화 대상과 parent gate 경계가
  구분된다.
<!-- key: id=key.acceptance.author-terminal-status.closure-gate -->
- `R013-CC-06` 비역사적 projection conflict가 남으면 closure complete를 보고하지 않고 충돌을
  해결하거나 residual action으로 남긴다.
<!-- key: id=key.acceptance.author-terminal-status.contract-parity -->
- `R013-CC-07` Project Author 기준과 installed Author skill이 같은 종료 계약을 가지며 focused
  contract test가 이를 검증한다.
<!-- key: id=key.acceptance.author-terminal-status.current-repair -->
- `R013-CC-08` 현재 Context Map의 R012/S02-S04 상태가 complete + accepted source와 일치한다.
<!-- key: id=key.acceptance.author-terminal-status.grouping-boundary -->
- `R013-CC-09` Clarify 그룹은 질문 개수나 표시 순서가 아니라 함께 영향을 받는 문서·section,
  답변 결합과 원자적 수정 필요성을 기준으로 AI가 구성한다.
<!-- key: id=key.acceptance.author-terminal-status.single-question -->
- `R013-CC-10` 각 그룹 안에서 한 번에 하나의 질문만 진행하는 불변 조건이 유지된다.
<!-- key: id=key.acceptance.author-terminal-status.clarification-log -->
- `R013-CC-11` 하나의 대주제에 추적되는 Q&A log 파일 하나를 만들고 모든 그룹을 `G01`
  아래의 `Q01` 구조로 기록하며, 질문·답변·답변일시 외의 상태·평가 필드를 요구하지 않는다.
<!-- key: id=key.acceptance.author-terminal-status.log-authority -->
- `R013-CC-12` Q&A log에는 `Group Decision`, `Author Application`, 별도 remaining-question
  section이 없고, 결정·평가·진행·source authority로 사용되지 않는다.
<!-- key: id=key.acceptance.author-terminal-status.group-application -->
- `R013-CC-13` 답변별 log 갱신은 lightweight append로 닫고, 원천 문서는 해당 그룹의 질문이
  모두 끝났을 때 그 그룹의 수정 범위만 한 번 반영한 뒤 다음 그룹으로 이동한다.
<!-- key: id=key.acceptance.author-terminal-status.optional-log-ref -->
- `R013-CC-14` 실제 원천 문서에 영향을 준 질문에만 선택적 key ref를 둘 수 있으며, 작업서는
  필요할 때만 log를 링크하고 어느 경우에도 이를 자동 수정·수락 근거로 사용하지 않는다.
<!-- key: id=key.acceptance.author-terminal-status.group-contract-parity -->
- `R013-CC-15` Project Clarify·Author 기준과 installed 두 skill이 같은 그룹·log·적용 경계를
  가지며 focused contract test가 이를 검증한다.

<!-- key: id=key.work.author-terminal-status-reconciliation.order.verification refs=key.topic.verification -->
## Verification

1. 변경된 Author 기준 section과 installed skill의 trigger, bounded scope, optional/stale 구분,
   historical preservation과 closure gate 문안을 대조한다.
2. 기존 `skills/tests/test_progress_ownership_contract.py`에 terminal reconciliation contract test를
   추가하고 focused `unittest`를 실행한다.
3. R012/S02-S04 exact ref를 owning R012 source, root works index와 Context Map에서 검색해
   current/navigation 요약을 대조한다.
4. 상태 문서 변경 후 `python3 scripts/work_state_runtime.py --root .`을 실행한다.
5. Markdown metadata, 관련 link와 `git diff --check`를 확인한다.
6. Graph, package, repository와 installer 전체 검증은 관련 surface가 추가로 바뀌거나 사용자가
   release 검증을 요청할 때만 수행한다.
7. Project Clarify·Author 기준과 installed 두 skill에서 그룹 기준, 한 질문 불변 조건, log 경로,
   최소 field, 금지 field, 답변별 log와 그룹별 source application 문안을 대조한다.
8. `skills/tests/test_clarify_group_application_contract.py`에 대주제 하나에 여러 그룹·질문이 있는
   fixture, 미응답 blank 해석, 선택적 key ref와 비권위 경계를 추가해 focused `unittest`를 실행한다.
9. Q&A log 기록 자체가 Work State, graph 또는 package-wide 검증을 호출하지 않는지 계약 수준에서
   확인한다.

<!-- key: id=key.work.author-terminal-status-reconciliation.order.stop refs=key.boundary.stop-condition key.topic.work-sequence -->
## Stop Conditions

1. Current/navigation summary와 historical narrative를 기존 문서 구조에서 구분할 수 없어
   소급 rewrite 위험이 생긴다.
2. Exact-ref 확인만으로 bounded 후보를 만들 수 없어 document root 전체 parser나 새 marker
   정책이 필요해진다.
3. Author 계약 변경이 canonical Work State authority나 schema 변경을 요구한다.
4. 기존 accepted 문서의 의미를 바꾸거나 새로운 user decision이 필요해진다.
5. 관련 없는 graph/package/installer surface 수정 없이는 검증할 수 없다.
6. 그룹 후보가 서로 다른 문서 의미를 함께 바꾸지만 관련성 근거가 없어 안전한 수정 범위를
   정할 수 없다.
7. Q&A log를 source authority나 평가 자료로 사용해야만 workflow를 구현할 수 있다.
8. 답변별 log 갱신과 그룹별 원천 문서 반영을 분리할 수 없어 모든 질문마다 무거운 Author
   application 또는 repository 검증이 필요해진다.

<!-- key: id=key.work.author-terminal-status-reconciliation.order.expected-output refs=key.topic.work-recovery key.topic.verification -->
## Expected Output

- 상태 전이 때만 실행되는 lightweight Author terminal reconciliation 기준
- Project standard와 installed Author skill의 동일한 self-contained 계약
- 계약 drift를 막는 focused regression test
- authoritative R012 종료 상태와 일치하는 Context Map navigation 요약
- 관련성 기반 Clarify 그룹 queue와 한 번에 한 질문을 보장하는 기준·runtime 계약
- 대주제별 최소 Q&A log 형식과 Work node 아래의 정확한 `clarify/` 경로
- 답변별 lightweight log 갱신과 그룹 종료별 Author source application 경계
- 실행한 검증, residual risk와 다음 resume point가 기록된 Progress
