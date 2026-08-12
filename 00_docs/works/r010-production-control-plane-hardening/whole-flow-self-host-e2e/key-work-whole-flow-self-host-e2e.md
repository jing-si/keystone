---
doc_type: work_order
created_at: "2026-08-07"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-11", accepted_by: main}
work_status: complete
finalization: {state: complete, acceptance_ref: R010/S06/main-acceptance}
key:
  id: key.work.whole-flow-self-host-e2e.order
  refs:
    - key.doc.work
    - key.topic.work-sequence
    - key.topic.work-recovery
    - key.topic.change-set
    - key.topic.artifact-graph
    - key.topic.integration-verification
    - key.topic.verification
    - key.work.decisions.dec-works-029
  relations:
    depends_on:
      - target: key.work.agent-behavior-evaluation.order
work_gates:
  - id: r010-s06-start-product-direction-realignment
    dependency: key.work.agent-behavior-evaluation.order
    applies_to: {steps: [S06], work_completion: false}
    condition: {work_status: complete, approval_state: accepted}
    optional: false
  - id: r010-s06-completion-product-direction-realignment
    dependency: key.work.agent-behavior-evaluation.order
    applies_to: {steps: [], work_completion: true}
    condition: {work_status: complete, approval_state: accepted}
    optional: false
---

# Standards-to-Product Core Simplification 작업서 및 Change Set

이 문서의 경로와 Work owner ID는 기존 R010/S06 계획 참조를 보존한다. 현재 S06은 과거의
agent-evidence 중심 whole-flow 계획을 실행하지 않고, S05가 수락한 교정 Change Set을 기준서와
runtime에 반영한다.

<!-- key: id=key.work.whole-flow-self-host-e2e.order.goal refs=key.section.goal key.topic.artifact-graph -->
## Goal

Artifact Graph와 Work State의 제품 핵심은 보존하면서 HMAC·external key·receipt chain·실제 agent
evidence·과도한 release/finalization 결속을 기본 경로에서 제거한다. 기준서 변경이 관련
code/config/schema/API/test에 누락 없이 연결되는 능력은 유지하되, 변경 위험과 무관한 검증·문서·산출물
비용은 요구하지 않는다. 수락 가능한 기준서 의미를 먼저 확정하고 runtime이 그 의미를 구현하도록 정렬한다.

<!-- key: id=key.work.whole-flow-self-host-e2e.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- S05의 accepted disposition inventory와 exact Change Set
- Pending Artifact Graph, Author, Coordinator, Linker와 Subagent standards의 제품 경계 정리
- Source-owned ID/ref, SourceUnit, locator, lifecycle, graph reconstruction와 stale/impact 핵심 보존
- Repository-derived Work State, active work recovery와 consumer parity의 최소 contract 보존
- Git/tree와 scoped raw-byte SHA-256 기반 baseline/current/result 확인
- Default closure/apply/release path의 external key·HMAC·agent evidence dependency 제거
- 일반 작업, 조건부 검증과 명시적 release 검증을 분리하는 위험 기반 계층형 검증
- 의미·상태가 실제로 바뀐 원천 문서만 갱신하고 파생 가능한 상태 중복을 줄이는 문서 최소화
- 외부 evidence/trust 폴더나 durable 검증 산출물 없이 완료되는 기본 작업 경로
- Historical read compatibility와 current-write contract 단순화
- Runtime, installed package, generator와 release gate의 current contract 정합화
- 제거 전 consumer search, safe migration, rollback과 deleted-surface verification

Exclude:

- 새로운 graph relation, product feature 또는 work-state hierarchy: R011 또는 별도 Work
- Optional audit/actual-agent QA 확장 구현
- External credential, model/reviewer/network 실행, publication과 version bump
- Historical Work/Progress/finalization evidence 재작성
- 일반 작업마다 full package·installer·historical compatibility 검증을 강제하는 정책
- 사용자 요청 없이 Coordinator, Superpowers 또는 특정 개발 workflow를 강제하는 정책
- S05 Change Set에 없는 opportunistic refactor와 formatting

<!-- key: id=key.work.whole-flow-self-host-e2e.order.source-context refs=key.section.source-context key.topic.impact-review -->
## Source Context

- `DEC-WORKS-029`
- Accepted S05 disposition inventory와 Change Set
- S01-S04 historical Work/Progress/finalization evidence
- Current pending standards와 installed skill contracts
- R010 baseline/main/frozen-branch diff와 consumer map
- `00_docs/convention.md`

<!-- key: id=key.work.whole-flow-self-host-e2e.order.sequence refs=key.topic.work-sequence key.topic.verification -->
## Implementation Sequence

1. S05 Change Set의 대상 path, current consumer, keep/remove contract와 compatibility를 fresh source에서
   다시 확인한다.
2. 기준서, package contract와 README를 Lean Core Contract와 계층형 검증 의미로 정렬한다. 의미가
   pending인 상태에서 implementation contract를 먼저 확정하지 않는다.
3. Release/closure/owner-apply의 current consumer를 no-secret contract로 바꾸고 agent-eval,
   external key·receipt·snapshot producer와 installer coupling을 제거한다.
4. 구 graph/closure/finalization validator는 historical read-only adapter로 격리하고 current
   completion·apply·release success를 만들지 못하게 한다.
5. 변경 surface별 targeted regression을 먼저 실행하고, 아래 escalation condition에 해당할 때만
   graph/package/installer/historical 검증을 추가한다.
6. 설치 package의 current contract와 기본 release plan을 확인한 뒤 S07의 실제 제품 흐름 검증으로 넘긴다.

<!-- key: id=key.work.whole-flow-self-host-e2e.order.minimum-contract refs=key.topic.artifact-graph key.topic.work-recovery -->
## Minimum Product Contract

기본 사용자는 다음 입력만으로 Keystone 핵심 흐름을 사용할 수 있어야 한다.

- 하나의 document root와 accepted project standard
- 기준서·결정·작업서의 stable owner/ref metadata
- repository source와 Git working tree
- 필요한 경우의 scoped file digest
- 사용자 승인과 일반적인 test/build command

기본 흐름은 reviewer key, Coordinator/Main private key, evidence root, transcript, pricing table,
agent provider, external clock 또는 독립 조직을 요구하지 않는다.

기본 작업은 다음 순서로 종료할 수 있어야 한다.

1. 관련 기준서·결정·활성 Work를 읽고 영향 후보를 찾는다.
2. 승인된 범위에서 source를 변경하고 current diff를 확인한다.
3. 변경 surface와 직접 관련된 test/lint/typecheck를 실행한다.
4. 실제 상태·증거·다음 작업이 달라졌을 때만 Progress를 갱신한다.
5. 기준서와 operative source가 충돌하면 통과시키지 않고 bounded risk로 보고한다.

Disposable readiness cache와 OS temporary output은 source discovery의 최적화일 뿐 authority나 제품
산출물이 아니다. 사용할 수 없거나 외부 경로 권한이 없으면 사용자에게 별도 trust/evidence 폴더
권한을 요구하지 않고 source scan으로 fail-soft fallback한다.

<!-- key: id=key.work.whole-flow-self-host-e2e.order.verification-policy refs=key.topic.verification key.topic.artifact-graph key.topic.work-recovery -->
## Risk-based Verification Policy

| 계층 | 적용 조건 | 필수 검증 |
|---|---|---|
| Default Work | 일반적인 기준서·code·test 변경 | 관련 문서 탐색, scope/diff check, targeted test, 필요한 Progress update |
| Escalated | metadata/relation, multi-surface contract, Graph/Work State, package/installer 또는 historical adapter 변경 | 해당 subsystem의 graph reconstruction, recovery/parity, package/installer 또는 compatibility test |
| Release | 사용자가 release/publish/install 검증을 요청 | full package·repository·installer plan과 release postflight |

Escalation은 아래 조건만 사용한다.

1. 기준서 의미나 independently addressable metadata가 바뀌면 Linker impact/stale review를 추가한다.
2. 여러 source surface의 canonical meaning을 함께 바꾸면 bounded graph synchronization을 추가한다.
3. Graph runtime이나 Work State runtime을 바꾸면 해당 focused reconstruction/recovery suite를 추가한다.
4. Package, generator 또는 installer를 바꾸면 staging/parity/rollback을 추가한다.
5. Historical adapter를 바꾸면 해당 wire fixture만 추가한다.
6. 분류 근거가 불충분하면 한 단계 높은 검증으로 올리되 전체 release plan을 자동 선택하지 않는다.

문서는 의미나 상태가 실제로 달라질 때만 갱신한다. 기준서는 정책 변경, Work Order는 Goal/Scope/criteria
변경, Progress는 실제 상태·증거·resume point 변경, Context Map과 root/round/work index는 active pointer나
집계 상태 변경이 있을 때만 수정한다. 일반 작업은 새 finalization manifest, receipt, snapshot,
acceptance-event 또는 agent-evaluation 산출물을 만들지 않는다.

<!-- key: id=key.work.whole-flow-self-host-e2e.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: 제품 핵심의 traceability/recovery는 보존하고 기본 작업 비용을 최소화한다.
- Required candidates: pending standards, installed skill contracts, Coordinator closure/snapshot,
  Linker transaction/application, Work State, finalization/release runtime과 corresponding tests
- Conditional candidates: readiness cache default/fallback, historical adapters, generator manifests와
  package/installer/release verification
- Removal candidates: agent-eval core gate, reviewer HMAC, external trust inputs와 unused evidence wire
- Excluded: R011, external projects, optional audit product와 unrelated cleanup
- Acceptance owner: Main
- Graph handling: 기준서·metadata 의미가 바뀐 surface만 Linker impact seed로 전달하고, exact
  multi-surface canonical mutation이 확인된 경우에만 graph synchronization을 사용한다.

<!-- key: id=key.work.whole-flow-self-host-e2e.order.exact-change-set refs=key.topic.change-set key.topic.verification key.claim.r010.audit-runtime-current-disposition -->
## Exact S06 Change Set

아래 세 phase는 S05 inventory를 위험 기반 계층형 검증에 맞춰 재구성한 implementation boundary다.
각 phase는 변경한 surface의 targeted regression을 통과한 뒤 다음 phase로 넘어간다.

### S06-A Lean Core Contract

먼저 다음 pending standard를 current no-secret 의미로 수정하고 Main review 가능한 상태로 만든다.

- `00_docs/standards/artifacts/key-standard-artifact-graph.md`
- `00_docs/standards/skills/author/key-standard-author.md`
- `00_docs/standards/skills/coordinator/key-standard-coordinator.md`
- `00_docs/standards/skills/linker/key-standard-linker.md`
- `00_docs/standards/subagents/key-standard-subagents.md`

같은 의미를 다음 package contract와 운영 문서에 반영한다.

- `skills/keystone-author/SKILL.md`
- `skills/keystone-author/references/finalization-validator.md`
- `skills/keystone-coordinator/SKILL.md`
- `skills/keystone-coordinator/references/closure-validator.md`
- `skills/keystone-linker/SKILL.md`
- `skills/keystone-linker/references/graph-runtime.md`
- `README.md`

Current contract는 다음과 같다.

1. Linker는 transaction과 exact patch를 계획하고 source owner는 자기 surface의 baseline을 write 직전
   재검사해 직접 적용한 뒤 `applied | failed | stale_baseline`과 resulting digest를 반환한다.
2. Current graph success는 current source reconstruction, transaction equality와 repository graph
   validation으로 판정한다. External owner key, HMAC receipt와 disjoint evidence root를 요구하지 않는다.
3. Coordinator closure는 assignment scope, current diff, verification 결과, document/graph disposition과
   durable Progress를 사용한다. Phase별 external-key receipt와 complete snapshot chain은 요구하지 않는다.
4. Main acceptance 뒤 Author는 실제 의미·상태가 바뀐 Work/Progress/decision/standard만 동기화한다.
   Index와 Context Map은 active pointer나 집계 상태가 달라졌을 때만 수정한다.
5. 구 closure v1-v3, finalization v1-v6, graph-validation v2/application-evidence wire는 historical
   input을 읽고 진단할 수 있지만 current completion·apply·release success authority를 만들지 않는다.
6. 일반 작업은 targeted verification으로 종료하고 graph/package/installer/historical 검증은 위
   escalation condition 또는 명시적 release 요청이 있을 때만 실행한다.
7. Coordinator, Superpowers와 외부 worker workflow는 사용자 요청이나 실제 delegation 필요가 있을
   때만 선택하며 core completion prerequisite가 아니다.

### S06-B Remove Mandatory Audit Paths

Current path에서 제거하거나 전환할 surface는 다음 다섯 그룹으로 한정한다.

1. Agent gate: `scripts/run_release_gate.py`, `README.md`,
   `scripts/{validate_agent_evals.py,agent_eval_scenarios.json}`와 관련 `skills/tests/test_*agent*`를
   no-agent 기본 release contract로 바꾼다.
2. Owner apply: `scripts/{generate_owned_surface_apply_runtimes.py,owned_surface_apply_runtime.py}`,
   Author/Coordinator의 `owned_surface_apply_runtime.py`·`run_owned_surface_apply.py`, 관련 shared test와
   `reinstall-local-keystone-skills.sh` coupling을 제거한다.
3. Closure producer: Coordinator의 `capture_assignment_snapshot.py`, `record_acceptance_event.py`, 관련
   test와 installer coupling을 제거하고 `validate_closure.py`의 no-secret base manifest를 current로 둔다.
4. Current consumers: Author package E2E, Linker graph integration과 Coordinator↔Author/Linker runner
   integration test를 owner-direct apply와 current source validation에 맞춘다.
5. Historical adapters: Linker application/transaction evidence, Coordinator closure v1-v3와 Author
   finalization v1-v6 parser·fixture는 read/diagnostic 전용으로 유지하고 current success path에서 분리한다.

삭제 전 current consumer가 0인지 `rg`와 import/CLI test로 확인한다. Historical adapter가 external key나
producer executable 없이는 읽지 못하면 `historical_structure_only` 진단으로 낮추고 pass authority로
변환하지 않는다. Frozen `915e26a` branch를 병합하거나 historical evidence를 재작성하지 않는다.

### S06-C Tiered Verification and Product Handoff

다음 core는 기능을 축소하지 않는다. 앞 phase의 coupling 제거와 fail-soft cache fallback에 필요한
최소 import/caller 변경만 허용한다.

- Artifact Graph: SourceUnit, metadata, scanner, locator/lifecycle, impact/classification,
  planner/reconciler와 graph model/relation/transaction/wire/validation
- Work State: canonical runtime, generator, manifest, Reader·Author·Coordinator copies와 parity tests
- Readiness: docs/repository owner-ref discovery와 source-scan fallback
- Safety: current diff/scope, baseline/result digest와 changed-surface targeted regression

Release canonical plan은 `preflight → package tests → shared skills tests → compileall → docs and
repository readiness → Work State → repository graph validation → installer staging/parity/rollback →
postflight`다. 이 plan은 release 요청에서만 실행한다. Dedicated actual-agent, Coordinator v2/v3,
archive-finalization과 current-finalization phase는 package compatibility tests가 이미 다루므로
기본 release plan에서 제거한다.

일반 작업 검증은 changed surface의 targeted test, `git diff --check`, 필요한 Work State recovery와
Linker impact review로 끝낸다. Package-wide, repository graph, installer와 historical compatibility는
해당 escalation condition이 충족된 경우에만 추가한다.

### Compatibility, rollback, and deletion gates

1. Historical fixture는 retired wire가 current success를 만들지 못함을 검증한다.
2. Public diagnostic/CLI removal은 README와 package contract를 같은 phase에서 수정한다.
3. 파일 이동과 behavior 변경을 섞지 않고 각 phase의 targeted regression 뒤 다음 phase로 넘어간다.
4. `${CODEX_HOME:-~/.codex}/skills`를 S06 중 직접 덮지 않는다. Package/installer surface가 바뀐
   phase에서만 installer temporary staging으로 여섯
   package tree와 runtime manifest parity를 확인한다.
5. R011, consuming projects, historical R010 evidence JSON과 frozen branch는 모든 phase에서 제외한다.

<!-- key: id=key.work.whole-flow-self-host-e2e.order.completion refs=key.topic.acceptance key.topic.verification -->
## Completion Criteria

<!--
key:
  id: key.acceptance.core-simplification.standards-first
  supersedes:
    - key.acceptance.whole-flow.prerequisite-finalization
-->
- `R010-S06R-CC-01` Lean Core Contract, 위험 기반 계층형 검증과 문서 최소화 경계가 implementation보다
  먼저 Main review 가능한 상태이며 runtime과 동일한 current meaning을 갖는다.
<!--
key:
  id: key.acceptance.core-simplification.graph-core
  supersedes:
    - key.acceptance.whole-flow.subsystem-binding
-->
- `R010-S06R-CC-02` Source-owned ID/ref, SourceUnit, locator, lifecycle와 stale/impact classification을
  보존하고 graph reconstruction은 graph-relevant 변경에서 통과한다.
<!--
key:
  id: key.acceptance.core-simplification.work-state-core
  supersedes:
    - key.acceptance.whole-flow.terminal-parity
-->
- `R010-S06R-CC-03` Active Work/Step, goal, criteria, evidence와 next action이 repository documents에서
  deterministic하게 복구된다.
<!--
key:
  id: key.acceptance.core-simplification.default-no-secret
  supersedes:
    - key.acceptance.whole-flow.actor-attribution
    - key.acceptance.whole-flow.phase-continuity
-->
- `R010-S06R-CC-04` 기본 apply/closure/work 경로가 external HMAC key, reviewer key, durable evidence
  root나 외부 폴더 권한 요청 없이 실행되고 Git/tree와 scoped SHA는 변경·freshness 용도로만 사용된다.
<!--
key:
  id: key.acceptance.core-simplification.agent-gate-removed
  supersedes:
    - key.acceptance.whole-flow.agent-evidence-binding
-->
- `R010-S06R-CC-05` Actual agent/reviewer/redaction/pricing evidence가 core completion과 release gate의
  필수 input 또는 step이 아니다.
<!--
key:
  id: key.acceptance.core-simplification.closure-minimum
  supersedes:
    - key.acceptance.whole-flow.crash-resume
-->
- `R010-S06R-CC-06` Closure와 resume는 scope, current diff, verification과 durable Progress만 요구하며
  불필요한 actor/receipt/schema chain이나 중복 상태 문서를 만들지 않는다.
<!--
key:
  id: key.acceptance.core-simplification.compatibility
  supersedes:
    - key.acceptance.whole-flow.prerequisite-verification
-->
- `R010-S06R-CC-07` 변경된 historical adapter와 package/installer surface에 한해 compatibility가
  통과하고 retired current-write path는 새 success authority를 만들지 않는다.
<!--
key:
  id: key.acceptance.core-simplification.verification
  supersedes:
    - key.acceptance.whole-flow.normal
    - key.acceptance.whole-flow.adversarial
-->
- `R010-S06R-CC-08` 모든 변경은 targeted regression과 diff check를 통과하고, escalation condition에
  해당할 때만 package/cross-skill, readiness, graph, compile 또는 installer 검증을 추가해 retained
  behavior regression이 없다.
<!-- key: id=key.acceptance.core-simplification.scope-discipline -->
- `R010-S06R-CC-09` 실제 changed files가 S05 accepted Change Set과 일치하고 R011/user changes 및
  unrelated cleanup을 포함하지 않는다.

<!-- key: id=key.work.whole-flow-self-host-e2e.order.verification refs=key.topic.verification key.topic.integration-verification -->
## Verification

- 모든 변경: targeted regression, `git diff --check`, exact changed-path scope
- 기준서·metadata 변경: Linker impact/stale review
- Graph/Work State 변경: retained behavior focused reconstruction/recovery suite
- Package/generator/installer 변경: package regression과 staging/parity/rollback
- Historical adapter 변경: 해당 historical read/current-write isolation fixture
- 명시적 release: full canonical release plan과 postflight

<!-- key: id=key.work.whole-flow-self-host-e2e.order.expected-output refs=key.topic.verification key.topic.work-recovery -->
## Expected Output

- Accepted product-boundary standards와 aligned skill contracts
- Simplified default closure/application/release runtime
- Retained Artifact Graph and Work State behavior
- Removed/non-blocking agent-eval and cryptographic-audit dependencies
- 위험 기반 계층형 검증, 최소 문서 갱신과 S07 제품 workflow handoff

<!-- key: id=key.work.whole-flow-self-host-e2e.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. S05 accepted disposition과 exact source/consumer map 없이 삭제 또는 schema migration을 해야 한다.
2. 기준서 의미가 pending인 채 implementation contract를 먼저 확정해야 한다.
3. Historical evidence를 삭제하거나 current compatibility를 근거 없이 끊어야 한다.
4. External key, reviewer, model/network 실행이 core verification에 다시 필요해진다.
5. 일반 작업을 완료하기 위해 full release, package-wide, installer 또는 historical validation을
   조건 없이 실행해야 한다.
6. R011 또는 사용자 소유 변경을 덮거나 revised S06 Change Set 밖의 cleanup이 필요하다.

## Superseded Historical Claims

다음 ID는 최초 S06 whole-flow/audit 계획의 역사적 locator다. 현재 completion criterion이 아니며
`key.acceptance.core-simplification.*` claim이 대체한다.

<!-- key: id=key.acceptance.whole-flow.normal -->
- `R010-S06-CC-01` 다중 actor fixture whole-flow 완주 요구 — superseded.
<!-- key: id=key.acceptance.whole-flow.actor-attribution -->
- `R010-S06-CC-02` worker/Author/owner/finalization actor attribution 요구 — superseded.
<!-- key: id=key.acceptance.whole-flow.phase-continuity -->
- `R010-S06-CC-03` phase digest와 acceptance ref chain 연속성 요구 — superseded.
<!-- key: id=key.acceptance.whole-flow.subsystem-binding -->
- `R010-S06-CC-04` package classification·patch·Work State subject binding 요구 — superseded.
<!-- key: id=key.acceptance.whole-flow.agent-evidence-binding -->
- `R010-S06-CC-05` actual agent evidence와 commit/package/generation 결속 요구 — superseded.
<!-- key: id=key.acceptance.whole-flow.adversarial -->
- `R010-S06-CC-06` 열 개 adversarial scenario gate 요구 — superseded.
<!-- key: id=key.acceptance.whole-flow.terminal-parity -->
- `R010-S06-CC-07` fixture terminal Reader와 release-facing state parity 요구 — superseded.
<!-- key: id=key.acceptance.whole-flow.prerequisite-verification -->
- `R010-S06-CC-08` S01-S05와 whole-flow verification의 구 prerequisite 요구 — superseded.
<!-- key: id=key.acceptance.whole-flow.prerequisite-finalization -->
- `R010-S06-CC-09` S01-S05 finalization envelope chain 요구 — superseded.
<!-- key: id=key.acceptance.whole-flow.crash-resume -->
- `R010-S06-CC-10` 일곱 targeted crash/resume fixture 요구 — superseded.
