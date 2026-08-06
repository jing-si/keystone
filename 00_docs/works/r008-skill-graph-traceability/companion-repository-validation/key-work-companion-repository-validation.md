---
doc_type: work_order
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: pending}
work_status: planned
key:
  id: key.work.companion-repository-validation.order
  refs:
    - key.doc.work
    - key.topic.artifact-graph
    - key.topic.keystone-metadata
    - key.topic.change-set
    - key.topic.verification
---

# Companion and Repository Validation 작업서 및 Change Set

<!-- key: id=key.work.companion-repository-validation.order.goal refs=key.section.goal key.topic.artifact-graph -->
## Goal

Binary/generated source의 companion metadata를 raw-byte identity로 안전하게 reconstruct하고,
repository `coverage: full`이 실제 누락·budget·동시 변경을 성공으로 숨기지 않는 fail-closed
validation envelope를 제공한다.

<!-- key: id=key.work.companion-repository-validation.order.scope refs=key.section.scope key.topic.verification -->
## Scope

Include:

- Adapter가 없는 source의 raw bytes와 companion JSON parse
- Logical `source_identity`와 physical `patch_target` 정규화
- Companion transaction omission과 owner/surface validation
- Repository full/subset completeness envelope
- `scan_truncated`, `source_too_large`, `source_unreadable` severity by requested coverage
- Manifest source set의 `discovered - declared`와 `declared - discovered`
- Immutable discovery bytes reconstruction 또는 post-reconstruction freshness verification

Exclude:

- Binary content 자체의 semantic parsing
- Unsupported generated format별 전용 adapter 개발
- Repository scan budget의 무제한 확대
- Subset coverage debt를 full coverage로 오인하는 완화

<!-- key: id=key.work.companion-repository-validation.order.baseline refs=key.topic.impact-review key.topic.verification -->
## Baseline Findings

1. Companion path는 존재해도 source를 먼저 UTF-8 text로 decode해 arbitrary binary가 실패한다.
2. Transaction scope는 patch `target_path`와 manifest source string을 직접 비교한다.
3. Repository scope는 discovered source로 manifest source를 덮어쓰고 manifest-only path를 검사하지
   않는다.
4. Full coverage에서도 scanner budget diagnostics는 warning이며 omitted source는 reconstruction에
   들어가지 않는다.
5. Discovery snapshot과 reconstruction read 사이에 source generation이 바뀔 수 있다.

<!-- key: id=key.work.companion-repository-validation.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: companion transaction과 repository validation의 source identity/completeness를 보장한다.
- Required candidates: scanner discovery model, graph reconstruction, validation CLI와 transaction
  source normalization tests
- Conditional candidates: validation envelope schema와 Linker runtime reference
- Acceptance owner: Main
- Graph handling: source identity는 graph node locator에, patch target은 owner-applied physical
  surface에 각각 보존한다.

<!-- key: id=key.work.companion-repository-validation.order.approach refs=key.section.recommended-approach key.topic.verification -->
## Recommended Approach

1. Non-UTF-8 binary+valid companion fixture로 current failure를 고정한다.
2. Adapter가 없으면 empty text와 raw bytes만 companion parser에 전달한다.
3. Companion suffix를 제거한 logical identity와 physical patch path를 별도 field/helper로 둔다.
4. Full/subset 요청, complete flag, discovered path digest, skipped와 omitted path를 envelope에 담는다.
5. Full coverage의 truncation/large/unreadable은 error, subset은 explicit coverage debt로 처리한다.
6. 양방향 manifest set 검증 뒤 discovery bytes로 reconstruct하거나 freshness token을 재확인한다.

<!-- key: id=key.work.companion-repository-validation.order.completion refs=key.topic.acceptance key.topic.integration-verification -->
## Completion Criteria

- [ ] Non-UTF-8 binary companion이 discover→parse→plan→attest→apply→reconstruct→verify된다.
- [ ] Companion patch target이 logical source omission으로 오진되지 않는다.
- [ ] `coverage: full`은 budget/unreadable/truncation이 있으면 pass하지 않는다.
- [ ] Full manifest의 missing, extra와 typo path가 양방향으로 진단된다.
- [ ] Subset coverage debt는 warning과 explicit omitted/skipped evidence를 유지한다.
- [ ] 한 validation envelope가 서로 다른 source generation을 혼합하지 않는다.
- [ ] Existing UTF-8 companion과 supported adapter regression이 유지된다.

<!-- key: id=key.work.companion-repository-validation.order.verification refs=key.topic.verification -->
## Verification

- Non-UTF-8 binary companion transaction E2E
- 5 MiB boundary, file-count/total-byte truncation과 unreadable-source fixtures
- Full/subset bidirectional manifest source-set tests
- Discovery와 reconstruction 사이 mutation/freshness test
- Repository graph validator, Linker full suite와 `git diff --check`

<!-- key: id=key.work.companion-repository-validation.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. Logical source identity와 physical patch path가 기존 public wire에서 구분되지 않는다.
2. Completeness envelope 변경이 compatibility decision 없이 기존 consumer를 깨뜨린다.
3. Immutable validation을 위해 unbounded repository memory 사용이 필요하다.
4. Binary source 의미를 companion evidence 없이 추론해야 한다.
