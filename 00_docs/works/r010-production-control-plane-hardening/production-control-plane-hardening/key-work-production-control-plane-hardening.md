---
doc_type: work_order
created_at: "2026-08-07"
document_lifecycle: active
approval: {state: pending}
work_status: in_progress
key:
  id: key.work.production-control-plane-hardening.order
  refs:
    - key.doc.work
    - key.topic.artifact-graph
    - key.topic.finalization
    - key.role.coordinator
    - key.topic.change-set
    - key.topic.verification
---

# Production Control Plane Hardening 작업서 및 Change Set

<!-- key: id=key.work.production-control-plane-hardening.order.goal refs=key.section.goal key.topic.verification -->
## Goal

서로 다른 Keystone runtime이 같은 source와 lifecycle을 동일하게 해석하고, transaction,
Coordinator closure와 finalization 성공이 manifest 자기신고가 아니라 실제 source 상태와
실행 가능한 evidence에 결속되도록 만든다.

<!-- key: id=key.work.production-control-plane-hardening.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- Document/artifact/relation lifecycle domain과 claim-level supersession 정합화
- Schema-v2 executable patch와 실제 resulting digest 결속, physical target 중복 차단
- 신규 transaction 기본 v2, 명시적 legacy-v1 compatibility와 mixed-patch 차단
- Supported text source의 inline/companion canonical SourceUnit 해석 통일
- Artifact flat `depends_on`과 legacy Work-completion gate 분리
- Coordinator closure schema v2의 repository root, assignment/report, scope·digest, Linker·Author
  evidence와 work-completion gate actual-state 검증
- Finalization global state의 round/Step prefix, source category와 status semantic invariant
- Retired impact seed와 명백한 parser false-positive 회귀 방지
- Agent-level scenario 명세·evidence validator와 clean-checkout release gate의 fail-closed
  security/plan 기반

Exclude:

- Publication, push, merge, marketplace와 외부 소비 프로젝트 변경
- Python 외부 dependency 추가
- Repository-wide metadata migration과 unrelated refactor/formatting
- Correctness와 무관한 adjacency/cache 성능 최적화
- Phase-separated snapshot/authority: R010/S02
- Package-owned classification과 optional patch·source/lifecycle·mutation 후속 correctness: R010/S03
- Repository-derived global work state와 shared runtime: R010/S04
- 실제 skill invocation·transcript·review evidence 생성과 반복 agent eval 실행: R010/S05
- Whole-flow self-host: R010/S06
- Independent CI/RC 실행, version transition과 terminal finalization: R010/S07

<!-- key: id=key.work.production-control-plane-hardening.order.source-context refs=key.section.source-context key.topic.artifact-graph -->
## Source Context

- 사용자 제공 zero-base review와 P0/P1 수정 순서
- `00_docs/standards/artifacts/key-standard-artifact-graph.md`
- `00_docs/standards/skills/linker/key-standard-linker.md`
- `00_docs/standards/skills/coordinator/key-standard-coordinator.md`
- `00_docs/standards/skills/author/key-standard-author.md`
- `00_docs/convention.md`

<!-- key: id=key.work.production-control-plane-hardening.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: success evidence를 canonical source bytes와 package-owned runner 결과에 결속한다.
- Required candidates: Linker/Coordinator/Author runtime, installed skill contracts, references,
  adversarial unit/integration/self-host fixtures와 R010 recovery documents
- Compatibility: v1 historical reads and accepted finalization history remain readable; new writes
  fail closed on non-canonical evidence.
- Acceptance owner: Main
- Graph handling: changed document and repository surfaces are classified after implementation;
  canonical graph mutation is not inferred from file changes alone.

<!-- key: id=key.work.production-control-plane-hardening.order.approach refs=key.section.recommended-approach key.topic.verification -->
## Recommended Approach

1. Review의 실패 시나리오를 adversarial test로 재현한다.
2. Lifecycle과 SourceUnit처럼 여러 runtime이 공유하는 의미는 하나의 executable policy/resolver로 둔다.
3. Schema-v2 success는 planned digest, current bytes, assignment context와 package-owned runner
   evidence의 equality를 직접 확인한다.
4. 기존 v1 read path는 유지하되 새 생성 경로는 명시적 compatibility option 없이는 거부한다.
5. 전체 package suite와 actual corpus validation을 하나의 release gate에서 다시 실행한다.

<!-- key: id=key.work.production-control-plane-hardening.order.completion refs=key.topic.acceptance key.topic.integration-verification -->
## Completion Criteria

Work Order는 아래 criterion의 불변 statement만 소유한다. 현재 state와 evidence는 S01 Progress의
`Criterion Status`에서 관리한다.

<!-- key: id=key.acceptance.r010.foundation.lifecycle-wire -->
- `R010-S01-CC-01` Document claim supersession과 draft relation이 canonical v2 wire에서 유효하고
  retired relation policy와 충돌하지 않는다.
<!-- key: id=key.acceptance.r010.foundation.applied-digest-binding -->
- `R010-S01-CC-02` Schema-v2 `applied.resulting_digest`가 `expected_after_digest`와 다르면 in-memory와
  wire validator 모두 실패한다.
<!-- key: id=key.acceptance.r010.foundation.physical-target-v2 -->
- `R010-S01-CC-03` Transaction 하나의 physical target당 patch 하나만 허용하고 신규 planner는
  기본 v2이며 legacy v1은 명시적 opt-in만 허용한다.
<!-- key: id=key.acceptance.r010.foundation.source-unit-companion-parity -->
- `R010-S01-CC-04` Supported text source와 adjacent companion을 readiness와 reconstruction이 같은
  SourceUnit policy로 해석하고 duplicate identity를 fail-closed로 진단한다.
<!-- key: id=key.acceptance.r010.foundation.artifact-dependency-separation -->
- `R010-S01-CC-05` Artifact flat dependency가 Work-completion gate로 승격되지 않는다.
<!-- key: id=key.acceptance.r010.foundation.coordinator-closure-v2 -->
- `R010-S01-CC-06` Coordinator closure v2가 실제 root/scope/digest, assignment context,
  Linker/Author runner evidence와 closure target gate를 검증한다.
<!-- key: id=key.acceptance.r010.foundation.finalization-v5 -->
- `R010-S01-CC-07` Finalization v5가 global source equality뿐 아니라 event round, active Step과
  source category semantics를 검증한다.
<!-- key: id=key.acceptance.r010.foundation.parser-impact-regression -->
- `R010-S01-CC-08` Retired seed와 parser false-positive의 bounded regression test가 통과한다.
<!-- key: id=key.acceptance.r010.foundation.verification-suite -->
- `R010-S01-CC-09` Affected package suites, cross-skill/self-host, external-cache compileall,
  historical R008/R009 finalization, repository readiness와 full graph validation이 통과한다.
<!-- key: id=key.acceptance.r010.foundation.release-security -->
- `R010-S01-CC-10` Release gate가 inherited execution environment, 축소된 plan, malformed success
  envelope, stale/ambiguous evidence와 untrusted reviewer key를 fail-closed로 거절한다.
<!-- key: id=key.acceptance.r010.foundation.work-decomposition -->
- `R010-S01-CC-11` Phase-separated closure, shared work state, actual agent evidence, whole-flow와
  terminal RC/finalization이 R010/S02-S07의 독립 reviewable goal로 분리된다.
<!-- key: id=key.acceptance.r010.foundation.evidence-replay -->
- `R010-S01-CC-12` S01 technical criterion을 current candidate subject에서 replay하고 evidence ref,
  subject commit과 generation/result digest를 S01 Progress에 기록한다.

<!-- key: id=key.work.production-control-plane-hardening.order.post-completion-acceptance refs=key.topic.acceptance -->
## Post-Completion Acceptance Gate

아래 항목은 S01 completion의 선행 조건이 아니다. Completion evidence가 모두 준비된 뒤 Main이
별도로 평가한다.

<!-- key: id=key.acceptance.r010.foundation.main-acceptance-review -->
- `R010-S01-PA-01` Main이 S01의 implemented correctness hardening과 verification evidence를 검토해
  acceptance를 결정한다. S01 acceptance는 S02/S03의 completion gate이며 R010 terminal
  acceptance가 아니다.

<!-- key: id=key.work.production-control-plane-hardening.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. Historical v1 transaction 또는 accepted finalization을 해석할 compatibility path가 사라진다.
2. Actual-state 검증에 source edit, graph mutation, Main acceptance 권한을 validator에 줘야 한다.
3. External model/API 실행, publication 또는 dependency 추가가 필수로 바뀐다.
4. 기존 사용자·agent 변경을 덮어써야 한다.
