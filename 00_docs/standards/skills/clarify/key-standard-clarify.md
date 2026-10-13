---
doc_type: standard
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-10-13", accepted_by: main}
key:
  id: key.standard.skill.clarify
  refs:
    - key.role.clarify
    - key.doc.decision
    - key.topic.question-flow
    - key.topic.document-authoring
    - key.topic.work-recovery
    - key.output.edit-plan
    - key.topic.impact-review
    - key.topic.keystone-metadata
    - key.topic.code-anchor
    - key.topic.artifact-graph
---

# keystone-clarify 기준서

<!-- key: id=key.standard.skill.clarify.purpose refs=key.role.clarify key.doc.decision key.output.edit-plan -->
## 목적

이 기준서는 `keystone-clarify`의 상세 계약을 정의한다. `keystone-clarify`는 원천 문서(2)
또는 스킬 계약에 영향을 주는 high-impact topic을 하나씩 명확히 하고, 수락된 결정(6)과
문서 update plan을 `keystone-author`가 안전하게 적용할 수 있게 만든다. 큰 검토 결과가 여러
topic을 포함하면 먼저 실제 문서 수정 관련성으로 그룹화하고, 그룹별 질문과 Author 적용을
순차적으로 닫는다.

<!-- key: id=key.standard.skill.clarify.scope refs=key.role.clarify key.doc.decision key.topic.question-flow key.output.edit-plan -->
## 적용 범위

1. `keystone-clarify`의 trigger와 non-trigger condition
2. Topic-scoped question collection
3. Reflection, decision summary, edit plan
4. Init 또는 Author로의 handoff와 resume
5. Impact update 대상과 stop condition
6. 대주제별 수정 그룹 구성, 질문별 Q&A log handoff와 그룹 종료별 Author 적용

<!-- key: id=key.standard.skill.clarify.out-of-scope refs=key.role.clarify key.topic.skill-contract key.topic.external-assist -->
## 적용하지 않는 범위

1. 사소한 typo, wording, formatting 질문을 생성하기
2. 원천 문서(2), code, config, schema, API, test, generated/codegen artifact 수정
3. 스킬 구현 파일 작성
4. 기준서(3)나 작업서(4)를 직접 생성하거나 넓은 범위에서 재작성하기
5. 외부 보조 스킬(12)을 자동 실행 대상으로 만들기
6. project-local setting이 아닌 common/global instruction file에 Keystone setup 결과 쓰기

<!-- key: id=key.standard.skill.clarify.standard-relations refs=key.role.clarify key.doc.standard key.topic.skill-contract -->
## 기준 관계

1. Parent 기준서: `../../01_key-project-standard.md`
2. 상위 규칙: `STD-KEYSTONE-001`, `STD-KEYSTONE-006`, `STD-KEYSTONE-007`,
   `STD-KEYSTONE-014`, `STD-KEYSTONE-015`, `STD-KEYSTONE-016`,
   `STD-KEYSTONE-023`, `STD-KEYSTONE-041`, `STD-KEYSTONE-050`,
   `STD-KEYSTONE-045`, `STD-KEYSTONE-046`, `STD-KEYSTONE-051`, `STD-KEYSTONE-052`
3. 관련 결정(6): `00_docs/works/key-decisions.md`
4. 충돌 처리: 이 기준서와 parent 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의
   결정(6)을 받는다. 결정 전까지는 parent 기준서를 임시 우선 기준으로 삼는다.
5. 상세화 범위: 이 기준서는 `STD-KEYSTONE-041`의 Clarify behavior를 구현 가능한 수준으로
   상세화한다.

<!-- key: id=key.standard.skill.clarify.skill-identity refs=key.role.clarify key.topic.skill-contract -->
## Skill identity

1. Skill name: `keystone-clarify`
2. Primary role: high-impact topic clarification and author-ready document update planning
3. Primary user: main agent 또는 문서 정책 결정을 확정하려는 사용자
4. Output authority: Clarify output은 사용자가 수락하기 전까지 원천 문서(2)를 대체하지
   않는다.

<!-- key: id=key.standard.skill.clarify.runtime-authority refs=key.role.clarify key.topic.runtime-independence key.topic.user-decision -->
## 런타임 권위와 질문 경계

이 문서는 Keystone 저장소에서 Clarify를 개발·검수하기 위한 원천 명세다. 배포된 Clarify의
실행 계약은 설치된 skill package 안에서 완결되어야 하며, 소비 프로젝트의
`standards/skills/clarify/**`를 required input으로 요구하지 않는다.

Clarify는 실제 사용자 결정만 다룬다. 안전한 기본값, 명시된 우선순위, repository evidence와
설치된 skill contract로 판단할 수 있는 사항은 질문하지 않는다. 특정 호스트 AI의 내부 mode나
질문 UI를 계약으로 삼지 않는다.

<!-- key: id=key.standard.skill.clarify.required-input refs=key.role.clarify key.topic.question-flow key.output.edit-plan key.topic.impact-review -->
## Required input

Clarify는 다음 input을 사용할 수 있어야 한다.

1. 사용자 요청 또는 main의 current clarification topic
2. 현재 topic과 관련된 원천 문서(2), 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 후보
3. 이미 수락된 decision summary와 edit plan이 있는 경우 그 내용
4. 변경 대상 원천 문서(2), section, 승인 범위 후보
5. affected document 후보와 affected artifact 후보
6. 민감 정보, local-only path, common/global instruction file, config write 여부와 관련된
   risk context
7. Modularization topic인 경우 Linker report, reuse candidate, worker report, reviewer
   finding, 또는 사용자가 제시한 유사 capability나 reusable artifact 근거
8. 큰 검토 결과를 처리하는 경우 대주제, 수정 후보 목록, Work node locator와 기존
   명확화 로그(21) locator

Input이 부족하면 Clarify는 high-impact decision을 추정하지 않고 incomplete result,
open question, stop condition으로 보고한다.

<!-- key: id=key.standard.skill.clarify.trigger-condition refs=key.role.clarify key.doc.decision key.topic.impact-review -->
## Trigger condition

`keystone-clarify`는 다음 경우에 사용할 수 있다.

1. 정책, 범위, 문서 구조, 스킬 계약, cross-document consistency에 영향을 주는 결정(6)이
   필요하다.
2. 원천 문서(2)를 의미 있게 바꾸기 전에 사용자 의도를 명확히 해야 한다.
3. 복수 document root나 기존 문서 채택·이동·대체처럼 초기화 중 실제 사용자 결정이 필요하다.
4. 문서 변경이 여러 기준서(3), 작업서(4), 진행 기록(5), 결정(6), 파생 에이전트 문서(8)에
   영향을 줄 수 있다.
5. current task의 방향이 기존 원천 문서(2)와 충돌한다.
6. main이 추론으로 진행하면 잘못된 feature, workflow, policy, acceptance criteria를 만들
   위험이 있다.
7. 기존 capability, reusable artifact, 또는 유사 implementation 후보가 evidence와 함께 발견되어
   reuse, extend, extract shared module, create new, investigate first 중 어떤 방향을 택할지
   결정해야 한다.

<!-- key: id=key.standard.skill.clarify.non-trigger-condition refs=key.role.clarify key.topic.skill-contract -->
## Non-trigger condition

`keystone-clarify`는 다음 경우에 사용하지 않는다.

1. 사소한 수정마다 high-impact 질문을 만들기
2. 이미 수락된 결정(6)과 대상 문서가 명확해 Author가 처리해야 하는 단일 문서 update
3. Reader가 수행해야 하는 read-only orientation 또는 document navigation
4. Author가 수행해야 하는 기준서(3) 또는 작업서(4) 작성 자체
5. Coordinator가 수행해야 하는 formal workflow orchestration, report handling,
   acceptance flow
6. 구현 code, config, schema, API, test, generated/codegen artifact 수정이나 테스트 실행 자체
7. 유사 기능 후보가 단순 keyword overlap이거나 local helper 수준이라 high-impact decision이
   아니다.
8. Linker report, worker report, reviewer finding, 사용자 제공 근거 같은 evidence 없이
   Clarify가 repository 유사성을 직접 확정해야 한다.
9. 기존 기준서(3), 작업서(4), 또는 Coordinator assignment scope가 reuse/extend 방향을 이미
   명확히 정했고 worker가 local implementation detail로 안전하게 처리할 수 있다.

<!-- key: id=key.standard.skill.clarify.topic-boundary kind=claim refs=key.role.clarify key.doc.decision key.topic.question-flow key.topic.document-authoring key.topic.work-recovery -->
## 대주제, 그룹과 topic 경계

Clarify는 대주제 안의 여러 수정 후보를 처리할 수 있지만 질문은 언제나 한 번에 하나의
high-impact decision topic만 다룬다.

1. 대주제는 "Keystone 개선 사항 검토"처럼 하나의 검토 요청과 그 결과로 나온 수정 후보 전체를
   뜻한다. 기록 대상 대주제 하나는 명확화 로그(21) 파일 하나에 대응한다. 단일 중요 질문도
   기록하며, 중요성 낮은 일반 질답을 이 그룹 workflow로 끌어들이지 않는다.
2. 그룹은 질문 묶음이나 별도 결정이 아니라, 답변 뒤 한 번에 반영할 원천 문서 수정 범위다.
   Group에는 `G01`, `G02`처럼 파일 안의 순서 식별자와 짧은 수정 범위 제목만 둔다.
3. 질문을 시작하기 전에 AI가 수정 후보를 그룹화한다. 같은 원천 문서·section을 바꾸는지,
   답변들을 함께 해석해야 하는지, 하나만 먼저 반영하면 모순·재작업이 생기는지, 하나의 검증
   경계로 닫을 수 있는지를 우선 판단한다.
4. 대상 문서, acceptance/verification 경계와 적용 시점이 서로 독립적이면 별도 그룹으로 나눈다.
   단순 번호 인접성, 질문 개수나 표시 순서만으로 묶지 않는다.
5. 사용자가 그룹 판단을 AI에 위임하면 위 기준과 현재 evidence로 가장 작은 일관된 수정 범위를
   선택한다. 그룹화가 사용자 소유 scope나 의미를 새로 바꾸는 경우에만 별도 질문한다.
6. 하나의 그룹을 선택한 뒤 그 그룹에 필요한 topic을 한 번에 하나씩 질문한다. 같은 topic의
   targeted follow-up은 허용하지만 다음 topic을 같은 질문에 합치지 않는다.
7. 현재 그룹에 문서 적용을 막는 material question이 더 없으면 caller에 통합 edit plan을
   반환한다. 별도 `Group Decision`, 그룹 평가나 완료 상태 artifact를 만들지 않는다.
8. Caller가 그룹 범위를 Author로 한 번 반영한 뒤 다음 그룹을 선택한다. 모든 그룹이 끝나면
   Clarify를 시작하기 전 원래 작업을 자동으로 resume한다.

<!-- key: id=key.standard.skill.clarify.modularization-decision-topic refs=key.role.clarify key.topic.impact-review key.topic.artifact-graph -->
## Modularization decision topic

Modularization decision topic은 기존 capability(16), output artifact, code/config/schema/API/test
artifact, 또는 유사 implementation 후보가 발견되어 reuse, extend, extract shared module,
create new, investigate first 중 어떤 방향으로 갈지 결정해야 하는 high-impact topic이다.

Clarify는 modularization 가능성을 제안할 수 있지만 repository 유사성을 직접 확정하지 않는다.
유사 기능 후보 발견과 evidence 등급화는 Linker report, Coordinator worker report, reviewer
finding, 또는 사용자가 제공한 근거를 input으로 사용한다.

Clarify는 다음 조건을 모두 만족할 때 modularization decision topic을 제안한다.

1. 기존 capability 또는 reusable artifact 후보가 evidence와 함께 발견되었다.
2. 새 구현을 만들면 중복 구현, policy drift, document drift, test drift 중 하나가 생길 수 있다.
3. 선택에 따라 문서, 기준서(3), 작업서(4), API contract, schema, test, acceptance criteria,
   verification, 또는 implementation scope가 달라진다.
4. Reuse, extend, extract shared module, create new, investigate first 중 선택이 필요하다.
5. Linker report, worker report, reviewer finding, 또는 사용자가 제시한 구체 근거가 있다.

Clarify는 다음 경우 modularization decision topic을 제안하지 않는다.

1. 유사성이 단순 keyword overlap뿐이다.
2. 단순 local helper 중복이나 같은 파일 안의 작은 함수 추출 수준이다.
3. 기존 기준서(3), 작업서(4), 결정(6), 또는 Coordinator assignment가 reuse/extend 방향을 이미
   명확히 정했다.
4. Worker가 assignment scope 안에서 local implementation detail로 안전하게 처리할 수 있다.
5. Evidence가 부족해 Linker 또는 investigate worker가 먼저 필요하다. 이 경우 Clarify는
   `investigate_first` 또는 `author_edit_ready: false`로 보고한다.

Modularization 선택지는 다음 vocabulary를 우선 사용한다.

1. `reuse_existing`: 기존 capability/provider를 그대로 사용한다.
2. `extend_existing`: 기존 capability/provider를 승인 범위 안에서 확장한다.
3. `extract_shared_module`: 중복 구현 후보에서 공통 module을 추출하고 기존/신규 구현이 함께
   사용하게 한다.
4. `create_new`: 중복 위험을 인지하고 신규 구현으로 둔다.
5. `investigate_first`: evidence가 부족하므로 Linker 또는 investigate worker를 먼저 수행한다.

`extract_shared_module`은 shared architecture, public interface, API/schema/test scope에 영향을 줄
가능성이 높으므로 high-impact decision으로 취급한다. Clarify는 이 선택을 코드 수정 지시로
바꾸지 않고 Author와 Coordinator handoff에 남긴다.

Clarify 질문은 evidence와 선택지를 분리해 구성한다.

```yaml
modularization_question:
  evidence:
    candidate_capability:
    candidate_artifact:
    source: linker_report | worker_report | reviewer_finding | user_request
    confidence: declared | observed | inferred
    duplication_or_drift_risk:
    affected_documents_or_tests_or_api:
  options:
    - reuse_existing
    - extend_existing
    - extract_shared_module
    - create_new
    - investigate_first
```

<!-- key: id=key.standard.skill.clarify.question-contract refs=key.role.clarify key.topic.question-flow key.doc.decision -->
## 질문 수집 계약

1. 한 번에 하나의 focused decision topic을 묻는다.
2. 선택지가 있으면 실제 영향과 tradeoff를 짧게 설명한다.
3. 사용자가 답하면 의미가 명확한 답변과 해석이 필요한 답변을 구분한다. 예·아니요나 명확한
   선택은 바로 기록한다. 요약·추리·분석하여 새 문장으로 구성해야 하면 `[확인 대기]` 해석을
   먼저 기록하고 사용자에게 의도를 확인한다. 확인 또는 명확한 교정은 같은 질문의 답변을
   확정하며, 이미 명확한 확인을 재확인하거나 확인 자체에 새 질문 번호를 부여하지 않는다.
4. 답변 의미의 확정과 topic의 충분성은 구분한다. 매 답변을 저장한 뒤에도 충분하지 않으면
   같은 topic에 대해서만 targeted follow-up을 새 파생 질문으로 추가한다.
5. 사용자가 AI에 판단을 위임했고 수락된 기준, repository evidence 또는 안전한 default가 있으면
   그 근거로 진행할 수 있다.
6. 답이 충분하지 않으면 `author_edit_ready: false`, unresolved `open_questions`, Author-ready
   `edit_plan` 없음으로 incomplete result를 반환한다.
7. 충분하면 decision summary, working assumptions, `decision_completeness_check`,
   `decision_recording_hint`, Author handoff용 edit plan을 만든다.
8. Clarify는 원천 문서(2)를 직접 수정하지 않는다.
9. 기록 대상이면 첫 질문 전 로그와 질문 entry를 생성하도록 caller에 요청한다. 매 답변의
   질문, 답변 또는 확인 대기 해석, 실제 답변일시와 locator를 전달한다. Caller는 Author의
   lightweight log append로 저장하고 해당 entry 재읽기로 성공을 확인한 뒤 같은 그룹 질문을
   계속한다. 전달만으로 저장이 끝났다고 보지 않는다. 실패 시 다음 질문·의존 원문 적용을
   멈추고 같은 entry 저장을 재개하며 이미 받은 답변을 다시 설명하도록 요구하지 않는다.
10. 답변별 log handoff에는 평가, 질문 충분성, `Group Decision`, `Author Application` 또는 작업
    상태를 넣지 않는다. 답변 내 `[확인 대기]`·`[폐기]` 표시는 기록 구분이며 평가가 아니다.
    원천 문서용 edit plan은 현재 그룹의 material question이 모두 끝날 때만 통합한다.

<!-- key: id=key.standard.skill.clarify.question-recording kind=claim refs=key.standard.project.std-keystone-060 key.role.clarify key.role.author key.topic.work-recovery -->
## 기록 선택, 질문 변경과 필요 시 복구

1. 기록 여부는 질문 수가 아니라 결정 중요성과 후속 근거 필요성으로 판단한다. 중요성이 낮고
   후속 근거가 필요 없는 대화는 일반 질답으로 처리하며 문서를 강제하지 않는다. 기록 대상이면
   최초 시작 시 생성하고, 도중 중요해졌으면 필요한 이전 맥락만 가져와 기록을 시작한다.
2. 작업서가 있으면 그 위치의 `clarify/`를 사용한다. 작업서나 별도로 승인된 기록 위치가 없으면
   caller에 위치·권한 미해결을 반환한다. 임의 위치·Round/Work 자동 생성이나 기록 생략으로
   해결하지 않는다. 사용자의 명시적 기록 금지는 지키되 필요한 결정 근거의 한계를 알린다.
3. 기본 번호는 파일 전체에서 `Q01`, `Q02`로 증가한다. 파생은 `Q01-A`, `Q01-B`, … `Q01-AA`
   등 대문자 Excel-column suffix를 사용한다. 재파생은 같은 기본 질문의 다음 suffix로 추가하고
   직접 원인 질문을 본문에 남긴다. 같은 적용 그룹에서는 관련 질문 가까이에 두고 다른 그룹에는
   원인 링크를 둔다. 기존 번호를 다시 매기거나 중간의 빈 번호를 재사용하지 않는다.
4. 질문 구조 변경은 폐기와 추가다. 미응답·확인 대기 질문을 폐기하면 답변에 `[폐기]`와
   원인 질문·이유를 남기고 대기 해석은 필요한 맥락으로 보존한다. 변경 질문은 별도 번호로
   추가하여 원인과 대체 대상을 연결한다. 단순 파생은 원 질문을 폐기하지 않는다.
5. 확정 답변의 변경은 이전 기록을 보존하고 새 질문·답변에서 변경 의도와 원 질문을 연결한다.
   기존 원문에 이미 반영했다면 영향을 재검토하며 과거 그룹 적용을 무조건 되풀이하지 않는다.
   AI의 폐기 설명을 사용자 발언으로 기록하거나 과거 답변시각을 추정하지 않는다.
6. 원 질문 밖이지만 대주제 안의 파생 질문은 생성 이유를 설명하고 독립 질문으로 진행한다.
   대주제 또는 승인 범위를 벗어나면 진행 범위를 먼저 확인한다. 연결 번호가 범위 확장 권한이나
   동일 적용 그룹을 뜻하지 않는다.
7. 질답 로그는 작업 기록이며 새 세션·일반 진행 상태 확인의 필수 입력이 아니다. 현재 맥락이
   부족한 질답 복구, 과거 답변·근거 확인, 사용자 요청에 필요한 부분만 읽는다. 확정 답변을
   재질문하지 않고 확인 대기는 해석 확인부터 이어가며 폐기 질문은 미응답으로 복구하지 않는다.
   현재 대화에 충분한 맥락이 있으면 다시 읽지 않는다.

<!-- key: id=key.standard.skill.clarify.handoff-resume refs=key.role.clarify key.output.edit-plan key.topic.handoff -->
## Handoff와 resume

1. 완료된 decision result는 Clarify를 요청한 Init, Author, Coordinator 또는 Main에 반환한다.
2. 호출자는 별도 재호출을 사용자에게 요구하지 않고 중단한 단계에서 원래 요청을 resume한다.
3. Handoff에는 결정, 근거, working assumptions, 영향을 받는 문서·artifact 후보, 열린 질문,
   stop condition을 포함한다.
4. 문서 반영은 Author가, 구현 또는 위임은 Main이나 허락된 Coordinator가 담당한다.
5. Clarify result는 edit authority나 acceptance를 자동으로 만들지 않는다.
6. 답변별 handoff는 명확화 로그(21)의 생성·질문별 저장만 요청한다. Source-document handoff는 현재 그룹의
   질문이 모두 끝난 뒤 한 번만 만들고, caller가 적용 결과를 확인한 뒤 다음 그룹으로 이동한다.
7. 모든 그룹이 끝나면 caller는 별도 사용자 재호출 없이 Clarify 이전의 원래 task와 resume point로
   돌아간다.

<!-- key: id=key.standard.skill.clarify.reflection-edit-plan refs=key.role.clarify key.output.edit-plan key.doc.decision -->
## Reflection and edit plan

Clarify result는 다음을 포함해야 한다.

1. `topic`: 결정한 주제
2. `decision_summary`: 사용자가 수락한 결정(6). Incomplete result에서는 null 또는 unresolved로
   표시한다.
3. `rationale`: 주요 이유와 tradeoff
4. `working_assumptions`: 이후 작업에서 사용할 가정
5. `affected_documents`: Author가 검토해야 하는 원천 문서(2). 반드시 수정해야 하는 update
   target, inspect-only 후보, excluded 후보를 구분한다.
6. `affected_artifact_candidates`: source document, decision, work order가 만들거나 통제하는
   output artifact 영향 후보. 필요하면 skill source, code, config, schema, API, test,
   generated file 같은 surface를 함께 표시한다.
7. `edit_plan`: 문서별 변경 요약. Incomplete result에서는 Author-ready `edit_plan`을 만들지
   않고 누락 사유를 보고한다.
8. `routing_handoff`: 복수 surface나 권한 경계가 있는 file-changing work의 target surface,
   추천 주체와 report 후보. 이 값은 edit authority가 아니라 optional routing context다.
9. `stop_conditions`: 적용 중 중단해야 하는 조건
10. `open_questions`: 아직 남은 질문. 현재 topic을 완료하기 위해 필요한
   `unresolved_current_topic`과 이번 topic 밖의 `out_of_topic` 질문을 구분한다.
11. `decision_completeness_check`: decision이 Author handoff 가능한 수준인지 확인한 결과
12. `decision_recording_hint`: 수락된 결정(6)을 어디에 기록해야 하는지에 대한 권장 위치와
    이유. Hint는 기록 권한이 아니며, 실제 기록은 Author 또는 Main이 승인 범위 안에서
    처리한다.
13. `modularization_decision`: modularization topic인 경우 reuse, extend, extract shared module,
    create new, investigate first 중 어떤 방향을 선택했는지와 그 근거. Modularization topic이
    아니면 생략한다.

High-impact topic, User Decision result, 또는 Author handoff가 있는 non-trivial Clarify result는
`decision_completeness_check`를 포함해야 한다. 단순 오탈자, wording, formatting처럼 실제
User Decision이 없는 작업은 Clarify의 non-trigger이며 이 output 계약을 적용하지 않는다.

결정(6)을 만들거나 바꾸는 non-trivial Clarify result는 `decision_recording_hint`를 포함해야
한다. 영구 결정 기록이 필요하지 않으면 Clarify는 기록이 필요하지 않은 이유를 보고한다.

Grouped clarification에서 각 topic의 `clarify_result`는 caller가 현재 그룹 안에서만 누적한다.
현재 그룹의 material question이 모두 끝났을 때만 affected document와 edit plan을 하나의 Author
handoff로 합친다. 이 agent-facing 누적 상태는 명확화 로그(21)에 평가·상태 field로 복제하지 않는다.

Affected documents는 다음 shape을 우선 사용한다.

```yaml
affected_documents:
  update_targets:
    - path:
      sections:
      reason:
      required_change:
  inspect_only_candidates:
    - path:
      reason:
      evidence:
  excluded:
    - path:
      reason:
```

`decision_completeness_check.affected_source_documents`는 `affected_documents`의 요약 또는
mirror field다. 두 필드가 다르게 해석될 수 있으면 structured `affected_documents`를 우선한다.

Routing handoff는 다음 shape을 우선 사용한다.

```yaml
routing_handoff:
  target_surfaces:
    - source_document | skill_source | repository_source | mixed
  recommended_lanes:
    - keystone-author | keystone-coordinator | main_direct
  required_reports:
    - author_patch_report | worker_assignment | worker_report | main_direct_change_report
```

Open questions는 다음 shape을 우선 사용한다.

```yaml
open_questions:
  unresolved_current_topic:
    - question:
      reason:
  out_of_topic:
    - question:
      reason:
```

Decision completeness check는 다음 shape을 우선 사용한다.

```yaml
decision_completeness_check:
  selected_option:
  rejected_options:
  rationale:
  affected_source_documents:
  affected_work_orders:
  affected_artifact_candidates:
  acceptance_or_status_impact:
  recording_scope: global | round | work | none | unresolved
  recording_reason:
  author_edit_ready: true | false
```

Decision recording hint는 다음 shape을 우선 사용한다.

```yaml
decision_recording_hint:
  scope: global | round | work | none | unresolved
  recommended_path:
  reason:
  requires_author_update: true | false
```

Modularization decision은 다음 shape을 우선 사용한다.

```yaml
modularization_decision:
  status: proposed | accepted | rejected | needs_linker_report | out_of_scope
  trigger_evidence:
    source: linker_report | worker_report | reviewer_finding | user_request
    summary:
  similar_artifacts:
    - key_id:
      kind: capability | code | config | schema | api | test
      locator:
      evidence: declared | observed | inferred
      risk:
  options:
    - reuse_existing
    - extend_existing
    - extract_shared_module
    - create_new
    - investigate_first
  selected_option:
  rationale:
  impact:
    affected_documents:
    affected_capabilities:
    affected_code_config_schema_api_test:
    verification_needed:
  handoff:
    author:
    linker:
    coordinator:
```

판단 기준은 다음을 따른다.

1. 여러 round에 영향을 주는 결정(6)은 `works/key-decisions.md`를 권장한다.
2. 특정 round 안에서만 유효한 결정(6)은 해당 round의 `key-decisions.md`를 권장한다.
3. 특정 work node 안에서만 유효한 결정(6)은 해당 work node의 `key-decisions.md`를 권장한다.
4. `none`은 영구 결정 기록이 필요하지 않은 경우에 사용한다.
5. `unresolved`는 decision이 아직 충분하지 않아 기록 위치를 정할 수 없는 경우에 사용한다.
6. 결정 기록 위치가 불명확하면 Clarify는 직접 기록하지 않고 Author handoff에
   `decision_recording_hint`를 포함한다.
7. Hint는 기록 권한이 아니며, 실제 원천 문서(2) 반영은 Author 또는 Main이 승인 범위 안에서
   처리한다.
8. `author_edit_ready`가 `false`이면 Clarify result는 Author가 바로 적용할 수 있는 edit
   instruction이 아니다. Main 또는 사용자는 남은 open question을 먼저 결정해야 한다.
9. 사용자의 답이 decision을 확정하기에 부족하면 `author_edit_ready: false`, unresolved
   `open_questions`, Author-ready `edit_plan` 없음으로 보고한다.
10. `acceptance_or_status_impact`가 있으면 progress status, acceptance criteria, status semantics를
    바꾸는지 분리해 보고한다.
11. Modularization decision이 `investigate_first` 또는 `needs_linker_report`이면 Author-ready
    `edit_plan`을 만들지 않고 필요한 Linker 또는 Coordinator investigation을 next action으로
    남긴다.
12. `create_new`를 선택하면 제외한 reuse candidate와 이유를 Author handoff 또는 Change Set
    후보에 남긴다.
13. `extract_shared_module`을 선택하면 shared architecture, public interface, API/schema/test,
    verification impact를 별도로 보고하고 Coordinator workflow로 넘긴다.

Clarify result가 file-changing work로 이어지면 Main은 `STD-KEYSTONE-046`에 따라 Author,
허락된 Coordinator 또는 Main direct로 실행 주체를 분리한다. 복수 surface나 권한 경계가 있을
때만 routing context를 명시적으로 남긴다.
Clarify가 decision summary와 edit plan을 만들었다는 사실은 source document나 skill source 수정
권한을 대체하지 않는다.

<!-- key: id=key.standard.skill.clarify.user-response refs=key.role.clarify key.contract.output key.topic.skill-contract -->
## 기본 사용자 응답

Clarify는 `clarify_result`를 agent-facing structured payload로 유지한다. 기본 사용자 응답은
다음 항목만 짧게 보여준다.

1. 결정할 topic 또는 이미 수락된 decision summary
2. 선택한 방향과 핵심 rationale
3. 남은 질문: unresolved current-topic question만 우선 표시
4. Author-ready 여부와 영향을 받는 주요 원천 문서(2)
5. 다음 권장 행동: Author 적용, 추가 질문, Linker/Coordinator handoff

Full `clarify_result`는 사용자가 요청하거나 Author handoff, audit/debug, verification evidence에
필요할 때만 노출한다. Optional `keystone-viewer`는 Clarify result를 audience별 view로 표현할 수
있지만 decision summary, open question, author-ready 판단을 바꾸지 않는다.

사용자-facing 응답을 보내기 전에는 `STD-KEYSTONE-045`의 Payload Disclosure Gate를 적용한다.
Full payload 요청, handoff, audit/debug, verification evidence 필요성이 없으면 `*_output`,
`*_result`, `*_report`, `worker_assignment`, `keystone_routing_decision` 원문 block을 기본
응답에 노출하지 않는다. 기본 응답은 payload 의미를 topic/decision 요약, rationale, open
question, 영향 문서, 다음 행동, 주요 출처로 압축한다.

<!-- key: id=key.standard.skill.clarify.impact-update refs=key.role.clarify key.topic.impact-review key.output.edit-plan key.topic.keystone-metadata key.topic.code-anchor key.topic.artifact-graph -->
## Impact update

수락된 clarify result가 문서에 반영될 때는 다음 규칙을 따른다.

1. 관련 parent 기준서와 child 기준서가 함께 영향을 받으면 `keystone-author`가 둘 다
   검토할 수 있게 edit plan에 포함한다.
2. 작업서(4)의 scope, completion criteria, status semantics에 영향을 주면 명시적으로
   보고한다.
3. 진행 기록(5)은 main acceptance 없이 완료 상태로 바꾸지 않는다.
4. 결정(6)은 장기 정책이나 여러 문서에 영향을 주는 경우에 기록한다.
5. 파생 에이전트 문서(8)는 이미 존재하고 명확히 영향받을 때만 edit plan에 포함한다. 새로
   생성하는 경우는 `STD-KEYSTONE-016`의 명시적 필요 조건을 따른다.
6. 키메타(9)가 있는 topic이나 문서가 관련되면 같은 `key.id`를 참조하는 문서를
   affected document 후보로 검토한다.
7. 같은 `key.refs`가 있어도 자동으로 edit plan에 포함하지 않는다.
8. `key.refs`가 없어도 관련 없음으로 단정하지 않는다.
9. 결정이 capability, code, config, schema, API, test artifact에 영향을 줄 수 있으면 코드 앵커(18)나
   아티팩트 그래프(14) 기반 affected artifact 후보를 edit plan에 분리해 기록한다.
10. Modularization decision이 수락되면 affected capability, excluded reuse candidate,
    verification 필요성, Linker report reference, Coordinator handoff 필요성을 edit plan 또는
    Author handoff에 분리해 기록한다.
11. 영향 범위가 불확실하면 문서 수정을 멈추고 사용자 또는 main 결정(6)을 요청한다.

<!-- key: id=key.standard.skill.clarify.initialization-boundary refs=key.role.clarify key.role.init key.topic.question-flow key.topic.initialization -->
## 초기화 질문 경계

1. Document root 기본값을 사용할지처럼 내장 초기 설정은 Init이 직접 묻는다.
2. Keystone 문서가 없다는 사실, 기본 metadata/file/index 형식, skill별 프로젝트 기준서 부재는
   Clarify topic이 아니다.
3. 복수의 유효한 root, 기존 문서 채택·이동·대체, 프로젝트 목적·범위·정책처럼 사용자의 의미
   결정이 필요한 경우만 Clarify가 한 topic씩 다룬다.
4. 결정 뒤에는 결과를 Init에 반환하고 중단한 초기화를 resume한다.
5. Clarify는 `.keystone/config.yaml`이나 project source document를 직접 수정하지 않는다.

<!-- key: id=key.standard.skill.clarify.stop-condition refs=key.role.clarify key.topic.skill-contract key.topic.impact-review -->
## Stop condition

Clarify는 다음 상황에서 중단하거나 main/user 결정(6)을 요청한다.

1. Topic이 여러 high-impact 결정을 동시에 포함해 하나의 질문으로 다룰 수 없다.
2. 사용자의 답이 서로 충돌하거나 기존 원천 문서(2)와 충돌한다.
3. 적용하려는 변경이 승인된 scope 또는 acceptance criteria를 바꾼다.
4. 변경 대상 문서나 section이 불명확하다.
5. 민감한 정보, local-only path, private data를 기록해야 할 수 있다.
6. 외부 보조 스킬(12)을 automatic/must-use로 바꾸는 결과가 된다.
7. Clarify topic을 넘는 implementation, config/schema/API/test artifact 수정, auth/security,
   generated/codegen, publishing 실행 결정이 먼저 필요하다.
8. Modularization topic에서 유사 기능 evidence가 부족해 Clarify가 repository 유사성을 직접
   확정해야만 진행할 수 있다.
9. Modularization 선택이 shared architecture, API/schema/test scope, acceptance criteria를 바꾸지만
   사용자 또는 main decision이 없다.
10. 수정 후보 사이의 문서·section 관계를 판단할 evidence가 없어 일관된 그룹 경계를 만들 수
    없다. 이 경우 먼저 Linker 또는 bounded repository investigation을 요청한다.

<!-- key: id=key.standard.skill.clarify.verification refs=key.role.clarify key.topic.verification key.output.edit-plan -->
## Verification

Clarify 기준은 다음 방법으로 검증한다.

1. Clarify contract만 보고 trigger와 non-trigger를 구분할 수 있어야 한다.
2. 한 topic 질문 수집과 호출자 handoff/resume의 책임 차이가 명확해야 한다.
3. Clarify는 원천 문서(2)를 수정하지 않는다는 경계가 명확해야 한다.
4. Reflection과 edit plan만 보고 Author가 문서 update 범위를 판단할 수 있어야 한다.
5. 내장 초기 설정 질문은 Init, 실제 사용자 의미 결정은 Clarify라는 경계가
   `STD-KEYSTONE-050`과 Bootstrap 기준에 일관되어야 한다.
6. 키메타와 코드 앵커 기반 affected 후보가 있으면 edit plan에서 후보와 실제 반영 여부를
   구분할 수 있어야 한다.
7. Modularization decision topic은 Linker report, worker report, reviewer finding, 또는 사용자
   제공 근거를 input으로 사용하고 Clarify가 repository 유사성을 직접 확정하지 않아야 한다.
8. Modularization 선택지가 reuse, extend, extract shared module, create new, investigate first의
   의미와 handoff boundary를 구분해야 한다.
9. 기본 사용자 응답은 structured payload를 그대로 노출하지 않고 decision, rationale, open
   question, affected documents, next action을 요약해야 한다.
10. File-changing handoff가 있으면 Author, 허락된 Coordinator, Main direct 중 필요한 실행
    주체를 edit plan 또는 recommended next action에서 분리해야 한다.
11. Verification command:
   - `rg --files 00_docs`
   - Clarify 관련 기준서를 읽어 link와 scope consistency 확인
12. 프로젝트 로컬 Clarify 기준서가 없어도 설치된 contract로 한 topic 질문과 resume 결과를
    제공할 수 있어야 한다.
13. 큰 검토 결과를 질문 전에 관련성 기반 수정 그룹으로 나누고, 그룹 안에서도 한 번에 하나의
    질문만 진행해야 한다.
14. 명확화 로그(21)는 기록 대상 대주제별 파일 하나, `G01`/`Q01`과 파생 suffix,
    질문·답변·답변일시의 최소 구조를 사용한다. 확인 대기·폐기 표시는 기록만 구분하고
    decision·evaluation·status authority를 만들지 않아야 한다.
15. 답변별 log append와 그룹 종료별 source-document application이 분리되고, log 기록만으로
    Work State, graph 또는 package-wide verification을 실행하지 않아야 한다.
16. 현재 그룹 적용 뒤 다음 그룹으로, 모든 그룹 뒤 원래 작업으로 사용자 재호출 없이 resume할
    수 있어야 한다.
17. 명확한 답변은 즉시 저장하고 해석 확인 전 중단·교정·확정과 저장 실패 뒤 재개를 구분한다.
    로그 전달만으로 다음 질문을 시작하지 않는다.
18. 폐기·대체·단순 파생·재파생·확정 답변 번복에서 질문 ID와 원인 관계를 보존한다.
19. 현재 맥락 충분 여부·필요한 근거에 따라 로그 읽기와 문서 없는 일반 질답을 구분한다.

<!-- key: id=key.standard.skill.clarify.internal-management-boundary refs=key.role.clarify key.role.linker key.topic.question-flow key.boundary.scope-control -->
## 내부 index/graph 관리와 사용자 결정 경계

1. Owner/ref index 생성 위치, cache refresh, docs/repository scan 시점, transaction/repository
   validation scope 같은 accepted 운영 규칙은 사용자 decision topic이 아니다.
2. Clarify는 permissionless Linker의 scan/index/validation 방법을 사용자에게 선택시키지 않는다.
   Cache/index 실패는 source fallback과 risk report로 처리한다.
3. Linker evidence가 서로 양립 가능한 project meaning, policy, scope 또는 authority 선택을 남길
   때만 한 high-impact question을 만든다. Coverage debt만으로 scope 확대를 묻지 않는다.
4. 검증 요구를 기록하는 decision/edit plan은 `requires_verification_of`를 사용하고 실제 evidence를
   얻기 전 `verifies`로 승격하지 않는다.
