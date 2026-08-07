---
doc_type: work_order
created_at: "2026-08-07"
document_lifecycle: active
approval: {state: pending}
work_status: planned
key:
  id: key.work.graph-transaction-source-correctness.order
  refs:
    - key.doc.work
    - key.topic.work-sequence
    - key.topic.work-recovery
    - key.topic.artifact-graph
    - key.topic.change-set
    - key.topic.integration-verification
    - key.topic.verification
  relations:
    depends_on:
      - target: key.work.production-control-plane-hardening.order
work_gates:
  - dependency: key.work.production-control-plane-hardening.order
    applies_to:
      steps: []
      work_completion: true
    condition:
      work_status: complete
      approval:
        state: accepted
    optional: false
---

# Graph, Transaction and Source Correctness 작업서 및 Change Set

<!-- key: id=key.work.graph-transaction-source-correctness.order.goal refs=key.section.goal key.topic.artifact-graph -->
## Goal

Optional patch가 실제 적용될 때 required patch와 동일한 owner·baseline·byte 검증을 받게 하고,
SourceUnit, lifecycle inheritance와 canonical mutation policy를 모든 parser/planner/validator
entrypoint에서 동일하게 적용한다. Planner를 우회한 structured input, non-UTF-8 source와 문자열
안의 가짜 anchor도 성공 경로를 만들지 못하게 한다.

<!-- key: id=key.work.graph-transaction-source-correctness.order.improvements refs=key.topic.work-sequence key.topic.verification -->
## 개선 항목

| ID | 개선 항목 | 구현 순서 | 핵심 근거 |
|---|---|---|---|
| PC85-03 | Optional patch fail-closed control | 1 | applied subset의 confirm·baseline·result equality |
| PC85-05 | SourceUnit·source parser 해석 단일화 | 2 | raw bytes 우선, companion fallback와 lexical masking |
| PC85-06 | Domain-aware lifecycle inheritance | 3 | document item과 output artifact 상속 분리 |
| PC85-07 | Canonical mutation strict schema | 4 | exact fields와 validator policy recheck |

<!-- key: id=key.work.graph-transaction-source-correctness.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- Applied required/optional patch의 confirm, baseline, expected/result/current digest invariant
- Partial resume와 finalization에서 실제 applied patch 전체 재검증
- Non-UTF-8 supported source, inline/companion selection과 raw-byte binding
- Supported generic language의 comment/string/template/raw-string boundary
- Document/item/output-artifact lifecycle·approval·authority inheritance matrix
- Canonical mutation exact schema와 relation/lifecycle/scope/evidence policy 재검사

Exclude:

- Coordinator phase/snapshot과 Linker classification: R010/S02
- Derived global state, agent eval과 release orchestration: R010/S04-S05
- Full AST parser, repository-wide metadata migration와 새 relation type
- Historical accepted transaction/finalization 의미 재작성

<!-- key: id=key.work.graph-transaction-source-correctness.order.source-context refs=key.section.source-context key.topic.artifact-graph -->
## Source Context

- R010/S01 transaction/SourceUnit/lifecycle strictness implementation과 regression evidence
- `00_docs/standards/artifacts/key-standard-artifact-graph.md`
- `00_docs/standards/skills/linker/key-standard-linker.md`
- `00_docs/standards/skills/author/key-standard-author.md`
- `00_docs/convention.md`

<!-- key: id=key.work.graph-transaction-source-correctness.order.pc85-03 refs=key.topic.artifact-graph key.topic.verification -->
## PC85-03 Optional patch fail-closed control

Implementation:

1. `applied patches ⊆ confirmed patches`와 `applied patches ⊆ baseline-checked patches`를
   reconciler와 wire validator에 모두 적용한다.
2. Optional patch는 자기 owner의 confirm과 fresh baseline evidence가 있을 때만 apply한다.
3. 모든 applied patch는 `resulting_digest == expected_after_digest == current source digest`를
   만족해야 한다.
4. Finalization과 partial resume는 required patch뿐 아니라 실제 applied된 optional patch를
   다시 검증한다.
5. Already-applied patch는 current digest가 recorded result와 같을 때만 skip한다.

Verification:

- Optional 미적용 완료와 confirm 후 적용은 통과한다.
- Unattested apply, stale baseline, source redrift와 forged result는 실패한다.
- Required/optional mixed transaction의 모든 허용·금지 상태 전이를 탐색한다.

Done when: structured input을 직접 만들어도 applied optional patch의 owner·baseline·exact bytes
검증을 우회할 수 없다.

<!-- key: id=key.work.graph-transaction-source-correctness.order.pc85-05 refs=key.topic.artifact-graph key.topic.verification -->
## PC85-05 SourceUnit·source parser 해석 단일화

Implementation:

1. SourceUnit은 raw bytes를 먼저 캡처하고 source decode 실패 시 valid companion이 있으면
   companion을 canonical surface로 선택한다.
2. Decode 성공 여부, inline declaration, companion 존재와 identity conflict를 하나의 resolver
   policy로 판정한다.
3. Companion evidence를 logical source raw bytes와 companion bytes에 함께 결속한다.
4. Generic language adapter는 string, template literal과 raw string을 masking한 뒤 실제 comment
   anchor만 metadata candidate로 인정한다.
5. 모호한 anchor는 declared node가 아니라 diagnostic/observed candidate로 남긴다.

Verification:

- UTF-16 또는 binary-like supported source+valid companion은 통과한다.
- Companion 없는 unsupported encoding은 stable diagnostic을 반환한다.
- Java/Kotlin, JavaScript/TypeScript, C/C++, Go, Rust, C#, Swift와 Shell의
  string/template/raw-string 가짜 anchor는 무시하고 실제 comment는 인식한다.
- Scanner, readiness, reconstruction과 validator의 selected surface·identity·relation이 일치한다.

Done when: 동일 raw source generation이 parser entrypoint에 따라 다른 canonical graph를 만들지
않는다.

<!-- key: id=key.work.graph-transaction-source-correctness.order.pc85-06 refs=key.topic.artifact-graph key.topic.verification -->
## PC85-06 Domain-aware lifecycle inheritance

Implementation:

1. Document→section/item과 document→output artifact의 inheritance matrix를 shared policy로 둔다.
2. Document item만 허용된 parent lifecycle/approval/authority를 상속하고 output artifact는 이를
   상속하지 않으며 lifecycle 기본값 `active`를 사용한다.
3. Non-active output artifact lifecycle은 artifact domain vocabulary로 직접 선언한다.
4. `governed_by` ordered union은 node kind별 정책을 적용하고 `produced_from`, ID, relation과
   approval은 output artifact에 상속하지 않는다.
5. Parser, effective metadata resolver, snapshot validation과 impact traversal이 같은 policy를
   사용한다.

Verification:

- Draft/pending document item은 parent 상태를 상속한다.
- Draft/pending document 안의 code artifact는 active이며 approval을 상속하지 않는다.
- Direct wire의 cross-domain lifecycle은 validator에서 실패한다.

Done when: node kind가 다른 parent state를 상속해 invalid graph/wire를 만들 수 없다.

<!-- key: id=key.work.graph-transaction-source-correctness.order.pc85-07 refs=key.topic.artifact-graph key.topic.verification -->
## PC85-07 Canonical mutation strict schema

Implementation:

1. Mutation object를 `operation`, `entity`, `before`, `after`, `evidence`,
   `direct_relation_reason` exact field set으로 고정한다.
2. Recursive duplicate/unknown field, non-finite value와 bool-as-int를 거절한다.
3. Wire validator가 relation direction, node/relation lifecycle domain, bounded direct
   item→artifact와 direct reason을 재검사한다.
4. Observed evidence를 owning surface patch/attestation과 결속하고 mutation source가 current scope
   안인지 확인한다.
5. `before` value를 transaction baseline snapshot과 비교한다.

Verification:

- `trusted`, `auto_accept`, `authority`, `confidence_override` field를 가진 wire는 실패한다.
- Wrong direction/lifecycle, unowned observed evidence, stale before와 out-of-scope mutation은
  실패한다.
- Planner 정상 출력은 serialize→parse→validate→reconstruct chain을 통과한다.

Done when: malicious direct transaction wire가 planner를 거치지 않아도 동일 policy에서 거절된다.

<!-- key: id=key.work.graph-transaction-source-correctness.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: 적용된 모든 patch와 canonical graph 의미를 exact source bytes와 shared policy에 결속한다.
- Required candidates: Linker transaction model/wire/reconciler, SourceUnit/scanner/adapters,
  lifecycle/mutation policy와 adversarial tests
- Conditional candidates: Reader readiness, Author graph finalization과 installed contract는 public
  output이 바뀌는 범위만 검토한다.
- Excluded: S02/S04/S05 owned runtime, full AST framework와 unrelated cleanup
- Acceptance owner: Main
- Graph handling: Linker가 canonical mutation을 결정하고 각 source owner만 자기 patch를
  attest/apply한다.

<!-- key: id=key.work.graph-transaction-source-correctness.order.completion refs=key.topic.acceptance key.topic.integration-verification -->
## Completion Criteria

- [ ] Applied optional patch도 owner confirm, fresh baseline과 expected/result/current digest equality를
      만족한다.
- [ ] Optional 미적용은 transaction completion을 막지 않으며 applied optional은 finalization에서
      재검사된다.
- [ ] Non-UTF-8 supported source+companion이 raw-byte binding으로 처리된다.
- [ ] String/template/raw-string의 가짜 metadata anchor가 declared node를 만들지 않는다.
- [ ] Scanner, readiness, reconstruction과 validator가 같은 SourceUnit 결과를 반환한다.
- [ ] Document lifecycle·approval·authority가 output artifact에 cross-domain 상속되지 않는다.
- [ ] Canonical mutation unknown field와 planner-bypass policy 위반이 실패한다.
- [ ] S01 Work가 `complete + accepted`이고 S03 focused/package/cross-skill verification이 통과한다.

<!-- key: id=key.work.graph-transaction-source-correctness.order.verification refs=key.topic.verification -->
## Verification

- Optional patch state-machine and executable-chain matrix
- Non-UTF-8 companion and scanner/reconstruction parity fixtures
- Generic language comment/string/template/raw-string lexical fixtures
- Lifecycle inheritance and malicious direct-wire matrix
- Linker full suite, affected Reader/Author suites, repository full graph validation
- External-cache compileall과 `git diff --check`

<!-- key: id=key.work.graph-transaction-source-correctness.order.expected-output refs=key.topic.verification key.topic.work-recovery -->
## Expected Output

- Optional patch invariant and reconciler/wire regression suite
- Unified SourceUnit selection and bounded lexical masking policy
- Domain-aware inheritance matrix and strict canonical mutation validator
- Contract/reference updates, cross-runtime parity fixtures와 Progress evidence

<!-- key: id=key.work.graph-transaction-source-correctness.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. Historical schema compatibility를 source history 변조 없이 보존할 수 없다.
2. Supported language의 comment/string boundary에 policy decision 없이 복수 valid 해석이 남는다.
3. Full AST/external parser dependency 없이는 8.5 종료 기준을 충족할 수 없다.
4. Linker나 validator가 source write 또는 Main acceptance 권한을 가져야 한다.
5. R010/S01과 다른 baseline에서 같은 file을 덮어써야 한다.
