---
doc_type: progress
created_at: "2026-08-26"
document_lifecycle: active
approval: {state: pending}
work_status: planned
work_ref: R018/keymeta-bounded-discovery
key:
  id: key.work.keymeta-bounded-discovery.progress
  refs:
    - key.topic.progress-update
    - key.topic.work-recovery
    - key.topic.work-sequence
    - key.topic.context-readiness
    - key.topic.artifact-graph
    - key.topic.keystone-metadata
    - key.topic.verification
    - key.work.keymeta-bounded-discovery.order
---

# Keymeta-First Bounded Discovery 진행 기록

## 현재 상태

- Round: `R018`
- Work: `keymeta-bounded-discovery`
- Round status: `planned`
- Work status: `planned`
- Approval state: `pending`
- Active Step: 없음
- Planned Steps: [`R018/S01`, `R018/S02`, `R018/S03`, `R018/S04`]
- Accepted Steps: []
- Status effect: Round 문서만 생성했으며 기준서·runtime·skill source·test 실행 상태는 변경하지
  않았다.
- Execution location: current worktree. Linked worktree를 선택하지 않았으므로 Work Order에
  `key.worktree` locator를 기록하지 않는다.
- Resume point: 사용자의 명시적 진행 요청 후 `R018/S01 Keymeta-Bounded Discovery Contract`를
  시작한다.

## 생성 근거

1. 사용자는 키메타를 전체 탐색을 피하기 위한 장치로 만들었으나 현재 readiness가 그 목적대로
   동작하지 않는다고 판단했다.
2. 사용자 지시에 따라 이 문제는 R015와 분리된 신규 Round가 소유한다.
3. R015와 겹치는 범위의 제거는 이번 변경에 포함하지 않으며 R015 source를 수정하지 않는다.
4. 읽기 전용 진단에서 repository tree 선행 열거, source adapter의 반복 substring scan, 동일 source
   재파싱과 source-view cache bypass가 주요 비용으로 확인됐다.

## 문서 생성 결과

1. R018 parent Round와 하나의 Work node를 `planned / pending`으로 작성했다.
2. 키메타 anchor 중심 bounded expansion과 routine no-full-scan을 Goal로 정의했다.
3. Standards-first S01, runtime S02, hot-path 최적화 S03과 closure verification S04를 계획했다.
4. Source authority·diagnostic honesty·explicit full-audit 기능을 비용 절감으로 낮추지 않는
   불변조건을 기록했다.
5. Persistent registry나 correctness 하한 변경이 필요하면 중단하고 사용자 결정을 받도록 했다.
6. 사용자 검토를 반영해 목표를 `never scan`이 아닌 `no implicit full scan`으로 좁히고,
   `targeted / lookup / audit` 세 mode와 bounded completeness diagnostic 경계를 계획에 추가했다.

## 계획 보정 결과

1. `targeted`는 routine 기본 mode이며 repository completeness를 주장하지 않는다.
2. `lookup`은 exact-ID owner 검색 범위와 비용을 노출하고 full graph reconstruction과 구분한다.
3. `audit`만 repository 전체 coverage를 검증하며 자동 mode escalation은 금지한다.
4. Unresolved owner는 실패를 숨기지 않고 stable incomplete diagnostic으로 반환한다.
5. 이번 보정은 문서 계획만 변경했으며 R018 Step이나 구현을 시작하지 않았다.

## 검증 상태

- Round 생성 후 Work State, metadata/ref와 Markdown 구조 검증을 실행한다.
- 구현·성능 수용 기준은 아직 실행하지 않았으며 완료로 표시하지 않는다.

## 다음 단계

R018은 생성만 완료된 상태다. 사용자가 Round 또는 S01 진행을 명시하기 전에는 작업을 시작하지
않는다.
