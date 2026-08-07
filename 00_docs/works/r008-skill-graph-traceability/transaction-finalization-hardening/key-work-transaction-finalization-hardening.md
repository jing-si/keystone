---
doc_type: work_order
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-07", accepted_by: main}
work_status: complete
key:
  id: key.work.transaction-finalization-hardening.order
  refs:
    - key.doc.work
    - key.topic.artifact-graph
    - key.topic.acceptance
    - key.topic.change-set
    - key.topic.verification
---

# Transaction and Finalization Hardening 작업서 및 Change Set

<!-- key: id=key.work.transaction-finalization-hardening.order.goal refs=key.section.goal key.topic.acceptance -->
## Goal

Graph transaction이 실제 source bytes에 재적용 가능한 patch와 원인별 retry evidence를 보유하고,
하나의 acceptance event에 포함된 모든 Step과 global work source가 strict structured state로
finalization closure를 통과해야만 complete가 되도록 강화한다.

<!-- key: id=key.work.transaction-finalization-hardening.order.scope refs=key.section.scope key.topic.artifact-graph -->
## Scope

Include:

- `unified_diff | full_replacement` patch format과 patch body
- Baseline→patch→expected bytes→resulting digest replay validation
- Application failure reason과 same-input retry admission
- 모든 accepted Step별 progress path, finalization state와 acceptance ref
- Structured global `active_round`, `latest_accepted_round`, `active_steps` validation
- Context Map, root/round/work index identity와 distinct category source 검사
- Strict YAML frontmatter parse와 body example isolation

Exclude:

- Source owner 권한을 Linker나 validator로 이전
- Main acceptance 자동 부여
- Arbitrary patch language 또는 network apply service
- Sibling/future Step의 자동 status transition

<!-- key: id=key.work.transaction-finalization-hardening.order.baseline refs=key.topic.impact-review key.topic.verification -->
## Baseline Findings

1. `exact_patch`는 non-empty validation만 있어 audit/replay 가능한 patch를 보장하지 않는다.
2. Resulting digest와 reconstruction은 verified final state를 보지만 partial apply를 새 owner가
   이어받을 실제 patch body를 보장하지 않는다.
3. Failure state에는 transient/non-transient 원인 enum이 없어 동일 입력 retry를 제한할 수 없다.
4. Multi-Step manifest는 각 Step status/approval을 읽지만 top-level 한 progress의 finalization만
   source와 비교한다.
5. Active-step sources는 global round/latest-accepted state, source key identity와 distinct path를
   완전하게 확인하지 않는다.

<!-- key: id=key.work.transaction-finalization-hardening.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: apply/replay 가능한 transaction과 모든 accepted Step의 fail-closed finalization을 만든다.
- Required candidates: transaction model/wire/evidence/reconciler, finalization manifest/parser/validator
  및 E2E tests
- Conditional candidates: Linker/Author runtime contracts, schema compatibility note와 R007 fixture
- Acceptance owner: Main
- Authority: Linker가 canonical patch를 결정하고 각 source owner만 attest/apply하며 Author는
  acceptance finalization source만 수정한다.

<!-- key: id=key.work.transaction-finalization-hardening.order.approach refs=key.section.recommended-approach key.topic.verification -->
## Recommended Approach

1. 설명문 `exact_patch`가 기존 validator를 통과하는 RED fixture를 만든다.
2. Patch format/body와 optional expected-after digest를 wire에 명시하고 temporary tree에서 적용한다.
3. `transient_io`, `permission_denied`, `validation_failed`, `source_conflict`, `tool_failure`,
   `unknown` failure reason을 추가하고 verified transient만 same-input retry를 허용한다.
4. Top-level single progress path를 Step별 finalization entries로 정규화한다.
5. Strict frontmatter parser로 Step/global state를 읽고 category path와 key ID를 검증한다.
6. 두 accepted Step 중 하나가 incomplete인 fixture가 반드시 fail하는지 확인한다.

<!-- key: id=key.work.transaction-finalization-hardening.order.completion refs=key.topic.acceptance key.topic.integration-verification -->
## Completion Criteria

- [x] 모든 required patch가 declared format과 executable body를 가진다.
- [x] Baseline bytes+patch가 expected after bytes와 resulting digest를 재현한다.
- [x] Non-transient failure는 unchanged input retry를 허용하지 않는다.
- [x] Verified transient failure만 preserved history와 새 transaction ID로 same-input retry된다.
- [x] 모든 accepted Step의 progress finalization state와 acceptance ref가 검사된다.
- [x] Context Map/root/round/work sources의 global state와 key identity가 일치한다.
- [x] Category source path 중복과 body example의 state 오인이 차단된다.
- [x] R007 multi-Step fixture를 compatibility mode 또는 명시적 migration으로 검증한다.

<!-- key: id=key.work.transaction-finalization-hardening.order.verification refs=key.topic.verification -->
## Verification

- Unified diff/full replacement apply and digest tests
- Partial apply/resume, transient and non-transient retry matrix
- Two-Step complete/incomplete/mismatched acceptance fixtures
- Strict frontmatter/body-example and distinct-source tests
- Linker 175+, Author 73+ regression과 package E2E
- Repository graph validation과 `git diff --check`

<!-- key: id=key.work.transaction-finalization-hardening.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. Patch format이나 finalization schema compatibility에 사용자 결정이 필요하다.
2. Validator가 source owner write 또는 Main acceptance authority를 요구한다.
3. 기존 verified history를 변조하지 않고 migration evidence를 만들 수 없다.
4. Strict parse가 지원 대상 YAML 범위를 결정하지 못해 nondeterministic하다.
