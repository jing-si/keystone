---
doc_type: work_round
created_at: "2026-08-26"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-26", accepted_by: main}
round_status: accepted
key:
  id: key.work.round.r017-standards-first-round-construction.index
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.work-recovery
    - key.topic.document-authoring
    - key.topic.skill-contract
    - key.topic.verification
    - key.boundary.scope-control
    - key.standard.project
    - key.standard.skill.author
    - key.work.decisions.dec-works-034
---

# R017 Standards-First Round Construction 작업서 색인

R017은 사용자와의 계획·검토가 끝나 Round를 생성할 때 생성-실행 분리, standards-first와
closure verification 세 제약만 고정하고 나머지 Step 구조는 Goal에 맞게 구성하도록 Author의
Round 생성 지침을 정렬한다. 사용자-facing 작업 단위는 Round와 Step으로 표현하고, Work Order는
그 구조를 기록하는 내부 원천 문서로만 사용한다.

이 Round는 최초 S01~S03을 수락한 뒤 누락된 하위 세션 작명 요구가 확인되어 다시 열렸다.
S04에서 `-`와 Excel column 방식 대문자 suffix를 기준서에 정합화하고 S05에서 Author skill,
Work State runtime과 회귀 테스트까지 구현·검증해 다시 `complete / accepted`로 닫았다. Active
R015의 상태와 실행 순서는 변경하지 않았다.

<!-- key: id=key.work.round.r017.execution-order refs=key.topic.work-sequence key.topic.document-authoring -->
## 실행 순서

| 순서 | Step | 상태 | 목적 |
|---|---|---|---|
| S01 | Standards-First Round Policy | accepted | 생성-실행 분리, standards-first, closure verification와 유연한 Step 구성 경계를 공통 결정·기준서에 정의했다 |
| S02 | Author Round Creation Guidance | accepted | Author가 세 핵심 제약을 지키면서 같은 요청의 생성+진행과 Goal별 Step 변형을 처리하도록 skill source에 반영했다 |
| S03 | Contract Verification and Closure | accepted | 생성-only·생성+진행, standards-first와 여러 유효 Step topology를 contract test로 검증했다 |
| S04 | Child Session Naming Policy | accepted | 하위 Round·Step의 `-` 경계와 Excel column 방식 대문자 suffix를 결정·기준서에 정의했다 |
| S05 | Naming Runtime and Reverification | accepted | Author skill, Work State 호환 parser와 회귀 테스트를 구현하고 R017을 다시 검증했다 |

- Active Step: 없음

세부 Goal, Scope, completion criteria와 검증 계획은 Work Order에서, 실제 상태와 resume point는
aggregate Progress에서 확인한다.

<!-- key: id=key.work.round.r017.boundaries refs=key.boundary.scope-control key.topic.document-authoring -->
## Round 경계

- 사용자와의 계획·검토는 Round 생성 전 대화 단계로 유지한다.
- 사용자-facing 설명은 `Round 생성`과 `Step 구성`을 우선하고, `Work Order`는 원천 문서를
  가리킬 때만 사용한다.
- Round 생성 요청만 받았으면 작업 문서를 `planned / pending`, Active Step 없음으로 기록한 뒤
  중단한다. 같은 요청이나 후속 요청에 명시적인 Round/Step 진행 지시가 있어야 실행을 시작한다.
- `작업서 생성 이후 작업을 바로 진행해주세요`처럼 같은 요청에서 생성 후 실행까지 명시하면
  Round 생성 뒤 첫 실행 가능 Step을 이어서 진행할 수 있다.
- 계획 수용, 생성 결과 확인, 이후 문서 수정 예정이라는 표현을 구현 승인으로 추론하지 않는다.
- 세 핵심 제약 밖의 Step 이름, 개수, 구현·검증 분할과 병렬 구성은 Round Goal에 맞게 정한다.
- Dependency engine이나 `work_gates` 변경은 이번 Round의 목적이 아니다.
- 기존 기준서가 합의된 의미를 이미 충분히 표현하면 기준서 Step은 근거 있는 `no_change`로
  닫을 수 있으며 의미 없는 문구 수정을 강제하지 않는다.
- R015와 accepted Round의 상태, 우선순위와 이력은 변경하지 않는다.

<!-- key: id=key.work.round.r017.reading-rules refs=key.topic.work-recovery key.topic.work-sequence -->
## 복구 규칙

1. R017 목표와 Step 상태는 이 Index에서 확인한다.
2. 사용자 방향, 상세 생성 규칙, 변경 surface와 completion criteria는 Work Order를 읽는다.
3. 실제 문서 작성 상태, 검증과 resume point는 Progress를 읽는다.
4. R017/S01~S05는 accepted됐다. 후속 변경은 별도 Round에서 수행한다.
