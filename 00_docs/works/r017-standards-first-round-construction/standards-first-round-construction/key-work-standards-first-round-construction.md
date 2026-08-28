---
doc_type: work_order
created_at: "2026-08-26"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-26", accepted_by: main}
work_status: complete
key:
  id: key.work.standards-first-round-construction.order
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.document-authoring
    - key.topic.skill-contract
    - key.topic.verification
    - key.boundary.scope-control
    - key.standard.project
    - key.standard.skill.author
    - key.work.decisions.dec-works-034
---

# Standards-First Round Construction 작업서

## 문서 상태

이 문서는 사용자와 합의한 Round 생성 흐름을 기준서와 Author runtime에 반영한
`accepted / complete` Work Order다. R017/S01~S03의 accepted 이력을 보존하면서 누락됐던 하위
세션 작명 요구를 S04 기준서와 S05 runtime·test에 보정했다.

<!-- key: id=key.work.standards-first-round-construction.order.goal refs=key.section.goal key.topic.document-authoring key.topic.skill-contract -->
## Goal

사용자가 대화로 계획과 검토를 마친 뒤 Round 생성을 요청하면, Author가 생성-실행 분리,
standards-first와 closure verification을 보장하는 작업 구조를 만든다. 생성 요청만 있으면
`planned / pending`으로 중단하고, 같은 요청이나 후속 메시지에 진행 지시가 있으면 실행을
이어간다. 세 제약 밖의 Step 이름, 개수와 분할 방식은 Round Goal에 맞게 자율적으로 구성한다.

사용자-facing 개념은 Round와 Step을 중심으로 유지한다. Work Order는 Round와 Step의 Goal,
Scope, completion criteria와 verification을 기록하는 내부 원천 문서이며, 사용자에게 별도의
실행 단계처럼 설명하지 않는다.

<!-- key: id=key.work.standards-first-round-construction.order.user-direction refs=key.topic.work-sequence key.topic.document-authoring -->
## 수락된 사용자 방향

1. `계획·검토 → Round 생성 → 명시적 진행 요청 → 기준서 정합화 → 구현 → 검증`은 권장 기본
   흐름이며 모든 Round에 동일한 Step topology를 강제하는 고정 schema가 아니다.
2. 계획과 검토는 Round 생성 전 사용자와의 커뮤니케이션으로 진행한다.
3. 사용자가 충분히 검토한 계획으로 Round 생성을 요청하면 Author가 실행 가능한 Step 구조를
   원천 문서에 기록한다.
4. 코드 변경을 포함하는 Round에는 첫 코드 구현 Step보다 앞선 기준서 정합화 Step이 반드시
   존재해야 한다.
5. 이 요구는 dependency engine을 강화하려는 것이 아니라 Author가 생성하는 Round 구조와
   순서를 일관되게 만들기 위한 지침이다.
6. Round 생성 요청은 기본적으로 작업 문서 생성까지만 승인하며, 같은 요청이나 후속 메시지에
   명시적인 진행 지시가 없으면 어떤 Step도 시작하지 않는다.
7. `작업서 생성 이후 작업을 바로 진행해주세요`처럼 생성과 진행이 같은 요청에 명시되면 Round
   생성 뒤 첫 실행 가능 Step을 이어서 진행할 수 있다.
8. 사용자가 생성된 Round를 추가 검토·수정하려는 상황에서 계획 수용이나 문서 생성 요청을 코드
   수정 승인으로 확대 해석하지 않는다.
9. 하위 세션은 `-` 뒤 Excel column 방식 대문자 영문 번호로 표기하며 숫자·혼합·의미 문자열을
   suffix에 사용하지 않는다.

- Clarify log: `clarify/20260826T052015Z-child-session-naming.md`

<!-- key: id=key.work.standards-first-round-construction.order.terminology refs=key.topic.work-round key.topic.work-sequence -->
## 사용자-facing 용어

| 용어 | 사용 의미 |
|---|---|
| Round | 사용자와 합의한 하나의 계획을 실행·검증하고 닫는 작업 차수 |
| Step | Round 안에서 순서대로 수행하는 Goal unit |
| Work Order | Round와 Step의 실행 계약을 보존하는 내부 원천 문서 |

사용자 응답과 지침에서는 `Work Order 생성`보다 `Round 생성`, `Step 구성`을 우선한다. 파일이나
문서 책임을 설명할 때만 Work Order라는 용어를 사용한다.

<!-- key: id=key.work.standards-first-round-construction.order.creation-stop-boundary refs=key.topic.work-round key.topic.work-sequence key.boundary.stop-condition -->
## Round 생성 후 중단 경계

1. `Round를 만들어 주세요`, `작업서를 만들어 주세요`처럼 생성만 요청하면 Round Index, Work
   Order, Progress와 필요한 navigation source만 작성한다.
2. 생성된 Round는 `planned / pending`, Active Step 없음으로 두고 생성 결과와 다음 실행
   후보를 보고한 뒤 중단한다.
3. 같은 사용자 요청에 `만들고 바로 진행해 주세요`, `작업서 생성 이후 작업을 바로 진행해
   주세요`가 함께 있거나, 이후 사용자가 `이 Round를 진행해 주세요`, `S01을 진행해 주세요`,
   `구현을 진행해 주세요`처럼 명시적으로 요청한 경우에만 Step 실행을 시작한다.
4. 계획 승인, Round 내용 수용, 단순한 긍정, 생성 결과 확인, 향후 문서 검토·수정 예정은
   명시적 실행 요청이 아니다.
5. Round 생성 뒤 추가 문서 수정 요청을 받으면 승인된 문서 범위만 수정하고, 별도 실행 지시가
   없으면 기준서 Step이나 코드 Step을 시작하지 않는다.
6. 생성 요청과 실행 요청의 의미가 불명확하면 구현으로 확대하지 않고 Round를 planned 상태로
   유지한다.

<!-- key: id=key.work.standards-first-round-construction.order.core-constraints refs=key.topic.work-round key.topic.work-sequence key.topic.verification key.boundary.scope-control -->
## 핵심 불변조건과 자율성 경계

Author가 생성하는 Round에는 다음 세 제약만 공통으로 고정한다.

1. **생성-실행 분리**: Round 생성만 요청되면 작업 문서 생성 후 중단한다. 같은 요청 또는 후속
   요청의 명시적 진행 지시가 있으면 생성 뒤 실행을 이어갈 수 있다.
2. **Standards-first**: Round에 유지될 production code/config/schema/API/generated/codegen 또는
   skill source 구현이 있으면 첫 production 구현 전에 기준서 정합화를 수행한다. 기존 accepted
   기준서가 충분하면 근거 있는 `no_change`로 닫을 수 있다.
3. **Closure verification**: Round 완료 전 accepted 기준서 의미, 실제 구현과 필요한 verification
   evidence의 정합성을 확인한다.

다음 구조는 Round Goal에 맞게 자율적으로 정할 수 있다.

- Step의 이름과 개수
- 하나 또는 여러 구현 Step
- 구현별 focused verification과 마지막 통합 verification의 배치
- 독립 Step의 병행 실행
- 문서 전용 Round, 조사 Round와 production 구현 Round의 서로 다른 topology

문서 전용 Round에는 구현 Step을 만들지 않는다. 조사·실험 Round가 production 구현을 수락하지
않는다면 조사와 사용자 판단 대기 구조를 사용할 수 있다. 반대로 Round 결과로 repository에
유지될 production 구현이 생기면 standards-first와 closure verification을 생략하지 않는다.

<!-- key: id=key.work.standards-first-round-construction.order.required-behavior refs=key.topic.document-authoring key.topic.work-sequence key.boundary.scope-control -->
## 필요한 Author 동작

1. Author는 Round 생성 요청에서 계획된 변경 surface를 확인한다.
2. 생성 요청만 있으면 작업 문서를 `planned / pending`, Active Step 없음으로 만들고 실행을
   중단한다.
3. 같은 요청이나 후속 메시지에서 명시적 진행 요청을 받으면 생성 뒤 첫 실행 가능 Step부터
   이어서 진행할 수 있다.
4. Round가 유지될 production code, config, schema, API, generated/codegen 또는 skill source
   구현을 포함하면 첫 production 구현 Step 앞에 기준서 정합화 Step을 둔다.
5. 기준서 정합화 Step은 다음을 확인한다.
   - 사용자와 합의한 intended behavior와 scope
   - 적용 기준서와 accepted decision
   - 구현이 지켜야 할 boundary와 verification expectation
   - 관련 기준서의 실제 수정 필요 여부
6. 기준서 의미가 부족하거나 달라지면 기준서와 필요한 결정을 먼저 수정하고 Main review 가능한
   상태로 만든다.
7. 기존 accepted 기준서가 합의된 의미를 이미 충분히 표현하면 문구를 억지로 바꾸지 않고
   `no_change`와 그 근거를 Step 결과로 기록한다.
8. 구현 Step은 앞선 기준서 Step에서 확정한 의미와 scope를 code/config/schema/API/test 또는
   skill source에 반영한다.
9. Round closure 전에는 기준서의 intended behavior, 실제 구현과 관련 test evidence가
   일치하는지
   확인한다.
10. 코드 변경이 없는 문서 전용 Round에는 구현 Step을 만들지 않으며, 목적과 scope에 필요한
   문서 Step만 구성한다.
11. 조사·실험 Round는 production 구현을 수락하지 않는 범위에서 별도 topology를 사용할 수 있다.
12. 세 핵심 제약을 만족하면 Step 이름, 개수, 구현·검증 분할과 독립 Step 병행은 Round Goal에
    맞게 구성한다.
13. Author는 Round 생성 시 아직 수행하지 않은 기준서·구현·검증 Step을 자동으로
   `in_progress`, `complete` 또는 `accepted`로 승격하지 않는다.

<!-- key: id=key.work.standards-first-round-construction.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- Round/Step 중심 사용자-facing 용어와 Work Order의 내부 문서 역할
- Round 생성 요청과 명시적 Round/Step 실행 요청의 분리
- 생성 직후 `planned / pending`, Active Step 없음으로 중단하는 기본 경계
- 같은 요청에서 Round 생성 후 즉시 진행을 명시하는 통합 요청 처리
- 구현을 포함하는 Round의 기준서 정합화 선행 Step 규칙
- Round closure 전 기준서·구현·verification evidence 정합성 확인
- 핵심 제약 밖의 Goal별 Step topology 자율성
- 기존 기준서가 충분할 때 근거 있는 `no_change`로 닫는 경계
- Project Standard와 Author Standard의 공통·상세 계약 정렬
- repo-local `keystone-author` skill source의 Round 생성 지침
- standards-first 구조를 검증하는 focused contract test
- R017 Work/Progress와 필요한 navigation source 정합화
- `-` 경계와 Excel column 방식 하위 Round·Step 식별자
- 기존 단일 소문자 child Round의 read-only historical compatibility
- canonical/generated Work State runtime의 대문자 다문자 child ref 복구

Exclude:

- dependency evaluator, `depends_on`, `work_gates`와 Work State schema 변경
- 기존 `R010-a` 계열 source와 accepted history의 rename·migration
- 대화 중 계획·검토를 별도 persistent 문서나 자동화 runtime으로 만드는 작업
- 모호한 긍정이나 계획 수용을 실행 승인으로 추론하는 동작
- 모든 Round를 하나의 고정 Step 이름·개수·형태로 강제하는 schema
- 모든 코드 변경에서 의미 없는 기준서 문구 수정을 강제하는 규칙
- 기존 accepted Round의 Step 구조와 이력 소급 변경
- R015 Goal, scope, 상태와 우선순위 변경
- browser, Playwright, screenshot, publish와 installer 작업

<!-- key: id=key.work.standards-first-round-construction.order.execution-plan refs=key.topic.work-sequence key.topic.verification -->
## 실행 계획

| Step | 상태 | 변경 범위 | 완료 경계 |
|---|---|---|---|
| R017/S01 | accepted | 공통 결정, Project Standard와 Author Standard | 생성-실행 분리, standards-first, closure verification와 유연한 topology 경계가 accepted policy로 정의됐다 |
| R017/S02 | accepted | `skills/keystone-author/SKILL.md` | Author가 생성-only와 생성+진행을 구분하고 세 핵심 제약 안에서 Goal별 Step 구조를 구성한다 |
| R017/S03 | accepted | `skills/tests/test_standards_first_round_contract.py`, Work State와 R017 source | 생성 요청 변형, production·문서·조사 Round topology, no-change와 closure 검증이 focused test를 통과했다 |
| R017/S04 | accepted | 공통 결정, Project Standard와 Author Standard | 하위 세션 `-` 경계, 대문자 Excel suffix, legacy 호환과 금지 형식을 accepted policy로 정의했다 |
| R017/S05 | accepted | Author skill, canonical/generated Work State runtime, focused·shared tests | `A → Z → AA → AZ → BA → ZZ → AAA`와 하위 Round·Step 복구를 구현·검증했다 |

위 R017/S01~S03은 이 Round 자체의 실행 순서다. 모든 미래 Round에 같은 세 Step을 강제하지
않는다. 공통 계약은 생성-실행 분리, production 구현 전 standards-first와 closure verification
세 제약뿐이며 별도 dependency나 gate 체계를 추가하지 않는다.

<!-- key: id=key.work.standards-first-round-construction.order.change-set refs=key.topic.change-set key.topic.verification -->
## Change Set

| Surface | Owner | Required change | Verification |
|---|---|---|---|
| Shared Decision and Project Standard | Author | 생성-실행 분리, standards-first, closure verification와 topology 자율성 정의 | 기존 Work model, authority와 verification 규칙 대조 |
| Author Standard | Author | 생성-only·생성+진행, production surface 분류와 세 핵심 제약 상세화 | create mode, 작업서 생성 표준과 scope boundary 검토 |
| Author Skill Source | Main | self-contained runtime 계약에 핵심 제약과 Goal별 Step 구성 동작 반영 | standard/skill contract parity |
| Work State Runtime | Main | 대문자 다문자 child Round·Step ref와 legacy 소문자 child Round 입력 호환 반영 | canonical/generated parity와 runtime regression |
| Focused Contract Test | Main | 생성-only·생성+진행, 문서 수정, production·문서·조사 Round와 여러 유효 topology 검증 | focused Python test |
| R017 Work Sources | Author | 실제 Step 상태, 검증 evidence와 resume point 기록 | canonical Work State와 exact-ref 확인 |

<!-- key: id=key.work.standards-first-round-construction.order.completion refs=key.topic.verification key.topic.document-authoring -->
## Completion Criteria

<!-- key: id=key.acceptance.standards-first-round.terminology -->
- `R017-CC-01` 사용자-facing 작업 흐름이 `계획·검토 → Round 생성 → Step 실행`으로 표현되고
  Work Order는 내부 원천 문서 역할로 구분된다.
<!-- key: id=key.acceptance.standards-first-round.structure -->
- `R017-CC-02` 구현 surface를 포함하는 새 Round에는 첫 구현 Step 앞에 기준서 정합화 Step이
  반드시 구성된다.
<!-- key: id=key.acceptance.standards-first-round.standard-result -->
- `R017-CC-03` 기준서 Step이 intended behavior, scope, boundary와 verification expectation을
  확인하고 `updated | no_change` 결과와 근거를 남길 수 있다.
<!-- key: id=key.acceptance.standards-first-round.no-forced-edit -->
- `R017-CC-04` 기존 accepted 기준서가 충분한 경우 의미 없는 문구 수정 없이 구현을 준비할 수
  있으며 기준서 검토 Step 자체는 생략되지 않는다.
<!-- key: id=key.acceptance.standards-first-round.author-contract -->
- `R017-CC-05` Project·Author 기준서와 installed-ready Author skill source가 같은 Round 생성
  규칙과 금지 경계를 표현한다.
<!-- key: id=key.acceptance.standards-first-round.verification -->
- `R017-CC-06` focused contract test가 구현 Round의 필수 Step 순서, 문서 전용 Round의 최소 구조,
  미실행 Step 상태 비승격을 검증한다.
<!-- key: id=key.acceptance.standards-first-round.scope -->
- `R017-CC-07` dependency/Work State 변경, 기존 Round 소급 개편과 R015 변경이 범위에서 제외된다.
<!-- key: id=key.acceptance.standards-first-round.creation-stop -->
- `R017-CC-08` Round 생성만 요청하면 작업 문서를 `planned / pending`, Active Step 없음으로 만든
  뒤 중단하고, 같은 요청이나 후속 메시지의 명시적 진행 지시가 있을 때만 Step을 시작한다.
<!-- key: id=key.acceptance.standards-first-round.combined-request -->
- `R017-CC-09` `작업서 생성 이후 작업을 바로 진행해주세요`처럼 같은 요청에 생성과 진행이 함께
  명시되면 Round 생성 뒤 첫 실행 가능 Step을 이어서 진행한다.
<!-- key: id=key.acceptance.standards-first-round.flexible-topology -->
- `R017-CC-10` 세 핵심 제약을 만족하는 범위에서 production·문서·조사 Round가 서로 다른 Step
  이름, 개수, 분할과 병행 구조를 가질 수 있으며 하나의 고정 pipeline을 강제하지 않는다.
<!-- key: id=key.acceptance.standards-first-round.child-session-naming -->
- `R017-CC-11` `-`는 직전 Round 또는 Step의 직접 하위 세션 경계이며 suffix는 숫자·의미
  문자열을 섞지 않은 Excel column 방식 대문자 영문 번호를 사용한다.
<!-- key: id=key.acceptance.standards-first-round.child-session-rollover -->
- `R017-CC-12` 새 하위 Round·Step 식별자가 `A → Z → AA → AZ → BA → … → ZZ → AAA` 순서를
  따르고 기존 단일 소문자 child Round는 historical compatibility 입력으로만 읽힌다.

<!-- key: id=key.work.standards-first-round-construction.order.verification refs=key.topic.verification -->
## Verification

1. Project Standard의 Work model, Author 기준서의 create mode·작업서 생성 표준과 새 원칙을
   대조한다.
2. repo-local Author skill source가 사용자-facing Round/Step 용어, implementation surface 판정,
   기준서 정합화 Step과 `no_change` 경계를 빠짐없이 표현하는지 확인한다.
3. `skills/tests/test_standards_first_round_contract.py`로 생성-only, `작업서 생성 이후 작업을 바로
   진행해주세요`, 생성 후 추가 문서 수정, production·문서·조사 Round, 여러 유효 Step topology와
   미실행 상태 사례를 검증한다.
4. 변경된 Markdown metadata, stable ID/ref, link와 `git diff --check`를 확인한다.
5. Step 또는 Round 상태 변경 시 `python3 scripts/work_state_runtime.py --root .`로 R017과 기존
   active Round를 검증한다.
6. Graph-relevant metadata가 바뀌면 affected-scope 검증만 추가한다. Package, installer와 browser
   검증은 변경 surface나 별도 요청이 없으면 실행하지 않는다.

<!-- key: id=key.work.standards-first-round-construction.order.stop refs=key.boundary.stop-condition key.boundary.scope-control -->
## Stop Conditions

1. 기준서 정합화 Step이 실제 구현 의미를 확정하지 못하고 형식적 문서 수정만 강제한다.
2. 세 핵심 제약을 보장하기 위해 모든 Round의 Step 이름, 개수와 분할 구조를 고정해야 한다.
3. Round/Step 용어 변경이 persisted schema, Work State identity 또는 기존 historical source
   migration으로 확장된다.
4. Author가 사용자와 합의되지 않은 기능 범위, acceptance criteria 또는 dependency gate를
   새로 만들어야 한다.
5. 구현 범위가 Author skill source, canonical/generated Work State runtime과 해당 regression을
   넘어 다른 Keystone 동작으로 확장된다.
6. R015 또는 기존 accepted Round의 상태·우선순위·이력을 변경해야 한다.
7. 명시적 진행 요청 없이 기준서, skill source, code 또는 test 수정을 시작해야 한다.

<!-- key: id=key.work.standards-first-round-construction.order.expected-output refs=key.topic.verification key.topic.document-authoring -->
## Expected Output

1. Round 생성과 실행 승인을 분리하되 같은 요청의 즉시 진행을 허용하는 accepted boundary
2. Standards-first와 closure verification만 고정하는 Round 생성 정책
3. Goal별 Step topology 자율성을 보존하는 repo-local Author skill contract
4. 생성 요청 변형과 production·문서·조사 Round를 검증하는 focused regression
5. R017 Step별 실제 evidence와 지속 가능한 resume point
6. Excel 방식 하위 Round·Step 식별자와 legacy 소문자 입력 호환을 구현한 runtime·regression

## 현재 다음 행동

R017/S01~S05와 Round가 accepted됐다. 후속 변경은 별도 Round에서 수행한다.
