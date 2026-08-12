---
doc_type: work_order
created_at: "2026-08-07"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-10", accepted_by: main}
work_status: complete
finalization: {state: complete, acceptance_ref: R010/S05/main-acceptance}
key:
  id: key.work.agent-behavior-evaluation.order
  refs:
    - key.doc.work
    - key.topic.work-sequence
    - key.topic.work-recovery
    - key.topic.change-set
    - key.topic.impact-review
    - key.topic.artifact-graph
    - key.topic.verification
    - key.work.decisions.dec-works-029
  relations:
    depends_on:
      - target: key.work.authority-chain-snapshot-closure.order
      - target: key.work.graph-transaction-source-correctness.order
      - target: key.work.work-state-runtime.order
    supersedes:
      - target: key.work.work-state-agent-evaluation.order
work_gates:
  - dependency: key.work.authority-chain-snapshot-closure.order
    applies_to: {steps: [S05], work_completion: true}
    condition: {work_status: complete, approval_state: accepted}
    optional: false
  - dependency: key.work.graph-transaction-source-correctness.order
    applies_to: {steps: [S05], work_completion: true}
    condition: {work_status: complete, approval_state: accepted}
    optional: false
  - dependency: key.work.work-state-runtime.order
    applies_to: {steps: [S05], work_completion: true}
    condition: {work_status: complete, approval_state: accepted}
    optional: false
---

# R010 Product Direction Realignment 작업서 및 Change Set

이 문서의 경로와 Work owner ID는 R010/S05 이력과 기존 참조를 보존하기 위해 유지한다. 현재
권위 있는 S05 의미는 actual agent 실행이 아니라 `DEC-WORKS-029`에 따른 R010 제품 방향 재정렬이다.

<!-- key: id=key.work.agent-behavior-evaluation.order.goal refs=key.section.goal key.topic.impact-review -->
## Goal

R010/S01-S04와 main source, 별도 S05 구현 branch를 Keystone의 제품 목표에 다시 대입해 각 변경을
`retain | simplify | optional_extension | retire`로 분류한다. 기준서가 구현보다 먼저 권위를 갖도록
교정 순서를 확정하고, S06이 수행할 bounded source/test/document Change Set과 S07 제품 흐름
verification을 준비한다.

<!-- key: id=key.work.agent-behavior-evaluation.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- R010 이전 baseline, main의 S01-S04와 별도 S05 branch 변경 inventory
- Artifact Graph, SourceUnit, locator, lifecycle, transaction, closure, Work State, release와 agent-eval
  surface의 목적 기여도·consumer·compatibility 분류
- Accepted 기준서와 pending revision, installed skill contract와 repository runtime의 의미 비교
- Git/tree, scoped SHA-256, HMAC, external key, receipt, attestation의 목적·위협 모델·운영 비용 구분
- 기준서→산출물 trace, stale detection, work recovery와 acceptance에 직접 필요한 최소 contract
- S06 exact source/test/document candidates, 제거 순서, compatibility와 rollback boundary
- S07 실제 제품 workflow와 non-browser verification 기준

Exclude:

- S05에서 code/config/schema/test/skill source를 수정하는 작업
- S01-S04의 과거 acceptance/finalization evidence 삭제 또는 실패로 소급 변경
- 별도 S05 branch merge, live model/reviewer/network 실행과 external credential 사용
- R011 planned 문서 의미, 외부 소비 프로젝트, publication과 version release
- 측정된 병목이 없는 hash/cache 최적화

<!-- key: id=key.work.agent-behavior-evaluation.order.source-context refs=key.section.source-context key.topic.impact-review -->
## Source Context

- `DEC-WORKS-029`
- R010 round index와 S01-S07 Work Order/Progress
- R010 이전 baseline `d36feb7`, main subject `435751c`, frozen S05 branch subject `915e26a`
- `00_docs/standards/bootstrap/key-standard-bootstrap.md`
- `00_docs/standards/artifacts/key-standard-artifact-graph.md`
- Project, Author, Reader, Linker, Coordinator와 Subagent standards/contracts
- `00_docs/convention.md`

<!-- key: id=key.work.agent-behavior-evaluation.order.method refs=key.topic.impact-review key.topic.verification -->
## 분류 방법

각 변경 단위는 source owner, current consumer, user value, failure mode, compatibility, 운영 비용과
검증 방법을 기록하고 다음 하나로 분류한다.

| Disposition | 기준 |
|---|---|
| `retain` | 기준서↔산출물 trace, stale detection, work recovery 또는 안전한 scope 적용에 직접 필요하다 |
| `simplify` | 목적은 필요하지만 schema·actor·key·evidence layer가 사용자 가치보다 복잡하다 |
| `optional_extension` | 외부 감사, 조직 분리, 실제 agent QA처럼 특정 운영 요구에서만 가치가 있다 |
| `retire` | 현재 제품 목표·consumer가 없거나 다른 기본 수단으로 충분하며 유지 비용이 더 크다 |

판정에는 최소한 다음 질문을 사용한다.

1. 이 기능이 없으면 기준서와 관련 코드·test를 찾거나 stale을 판단할 수 없는가?
2. 이 기능이 없으면 active work와 다음 작업을 문서에서 복구할 수 없는가?
3. Git commit/tree와 scoped source digest로 해결되지 않는 실제 위협이 있는가?
4. 새 secret, 외부 actor, 별도 evidence root나 반복 실행을 일반 사용자에게 요구하는가?
5. Accepted standard가 이 의미를 소유하는가, 아니면 pending Work가 구현을 앞서갔는가?
6. 제거 또는 단순화가 historical read와 installed package를 어떻게 보존하는가?

<!-- key: id=key.work.agent-behavior-evaluation.order.initial-direction refs=key.work.decisions.dec-works-029 key.topic.impact-review -->
## 초기 개선 방향

| 영역 | 초기 disposition | S05 확인 사항 |
|---|---|---|
| Source-owned ID/ref와 Artifact Graph direct trace | retain | owner/ref, stale와 impact 흐름이 실제 product scenario를 충족하는지 확인 |
| SourceUnit·locator·lifecycle·strict mutation | retain | parser entrypoint parity와 false-positive 경계 확인 |
| Repository-derived Work State | retain | active work recovery와 consumer parity의 최소 API 확인 |
| Complete snapshot·scope·before/after digest | simplify | 전체 path/phase schema 대신 필요한 assignment scope와 changed set으로 축소 가능성 확인 |
| HMAC owner receipt·external Coordinator/Main key | retire from current | producer와 mandatory consumer를 제거하고 구 wire는 historical read only로 제한 |
| Closure v2/v3·finalization v5/v6 다중 wire | simplify | current write wire 하나와 historical read adapter 경계 확인 |
| Actual agent invocation·reviewer·redaction·pricing | retire from current | frozen branch를 병합하지 않고 이번 R010에서 optional 모듈을 만들지 않음 |
| Release gate | simplify | 기본 package/readiness/graph/workflow 검사만 남길 경계 확인 |
| 평균 8.5·dual reviewer·adjudication·RC lineage | retire | 사용자 가치 criterion으로 대체 확인 |

<!-- key: id=key.work.agent-behavior-evaluation.order.verified-inventory refs=key.topic.impact-review key.topic.change-set -->
## Verified Source and Consumer Inventory

Inventory 기준은 R010 이전 `d36feb7`, 현재 main source `435751c`, frozen S05 source `915e26a`다.
현재 worktree의 R010/R011 문서 수정은 source implementation inventory에 섞지 않았다.

| Source group | Verified producer/consumer evidence | Disposition | S06 contract |
|---|---|---|---|
| Artifact Graph core | `skills/keystone-linker/scripts/graph_runtime/`의 `source_unit.py`, `metadata.py`, `scanner.py`, `lifecycle_policy.py`, `impact.py`, `classification.py`, `planner.py`, `reconciler.py`, transaction/wire/validation modules와 package tests | retain | Source-owned ID/ref, SourceUnit, locator, lifecycle, stale/impact, transaction plan/reconstruct/validate를 보존한다 |
| Work State core | `scripts/work_state_runtime.py`, generator/manifest, Reader·Author·Coordinator vendored copies, `skills/tests/test_work_state_runtime.py`, installer와 release consumers | retain | repository document에서 active Work/Step, criteria, evidence와 next action을 복구하는 단일 runtime을 보존한다 |
| Owner-apply HMAC | canonical 2,080-line runtime, generator, Author/Coordinator copies와 runners, installer requirements, Linker application-evidence, cross-skill tests | retire current producer | 일반 owner가 baseline/current/result digest를 확인해 직접 적용하고 apply result를 반환한다. External key·receipt·evidence root는 요구하지 않는다 |
| Coordinator closure | `validate_closure.py` schema 1과 `closure_v2.py`/`closure_v3.py`, snapshot/acceptance producers, package and cross-skill tests | simplify | current closure는 scope, current diff, verification와 durable Progress만 사용한다. v1-v3 wire는 historical read only다 |
| Author finalization | schema v1-v6 validator/runner, global/section/step modules, graph-owner input과 release consumers | simplify | current acceptance는 Work/Progress/index/Context Map 동기화와 graph/work-state 검증으로 닫는다. v1-v6 manifest는 historical read only다 |
| Release gate | `scripts/run_release_gate.py`, shell launcher, README와 release tests | simplify | package tests, readiness, Work State, repository graph, installer, compile와 clean pre/postflight만 기본 gate로 둔다 |
| Agent evaluation | scenario spec, 884-line validator, release mandatory step와 세 test surfaces | retire | scenario/validator와 mandatory step을 제거하고 agent evidence가 없어도 기본 release가 통과해야 한다 |
| Frozen S05 branch | actual runner/reviewer/adapter/redaction runtime과 7개 신규 test/fixture surface, main release/validator 수정 | retire/unmerged | `915e26a`를 병합하지 않고 Git history 및 분석 근거로만 보존한다 |

### Exact frozen-branch exclusion

다음 `435751c..915e26a` 신규 implementation은 S06 source가 아니다.

- `scripts/agent_eval_adapters/codex_cli.py`
- `scripts/agent_eval_evidence.py`
- `scripts/agent_eval_runtime.py`
- `scripts/review_agent_evals.py`
- `scripts/run_agent_evals.py`
- `skills/tests/fixtures/agent_eval_fixture_adapter.py`
- `skills/tests/test_agent_eval_codex_adapter.py`
- `skills/tests/test_agent_eval_reviewer.py`
- `skills/tests/test_agent_eval_runner.py`
- `skills/tests/test_agent_eval_runtime.py`

Branch에서 수정한 `scripts/agent_eval_scenarios.json`, `scripts/run_release_gate.py`,
`scripts/validate_agent_evals.py`, README와 release/agent security tests도 가져오지 않는다.

### Standards and installed-contract drift

- HMAC·external application authority와 schema-v3 actor chain을 현재 의미로 쓰는 pending standard는
  Artifact Graph, Author, Coordinator, Linker와 Subagent 다섯 문서다. S06은 이 문서를 먼저 수정한다.
- Repository와 `${CODEX_HOME:-~/.codex}/skills`의 `SKILL.md` raw-byte digest 비교에서 Init·Clarify는 같고
  Reader·Author·Linker·Coordinator는 다르다. 외부 설치 tree를 직접 덮지 않고 temporary staging에서
  여섯 package parity를 검증한다.
- Accepted Reader standard와 Work State core는 유지한다. HMAC 제거를 이유로 source discovery,
  work recovery 또는 graph correctness를 약화하지 않는다.

<!-- key: id=key.work.agent-behavior-evaluation.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: R010 구현을 기준서 기반 제품관리 목표와 최소 신뢰 경계에 다시 맞춘다.
- Required document candidates: R010 index/S05-S07, decisions, Context Map, root works index와 관련
  pending standards
- Required output candidates for S06: Coordinator closure/snapshot, Linker transaction/application,
  Work State, release/agent-eval runtime과 focused tests
- Conditional candidates: current authority를 만들지 않는 historical compatibility adapter
- Excluded: R011, consuming projects, publication, version bump와 external provider integration
- Acceptance owner: Main
- Graph handling: S05는 read-only impact classification만 수행한다. S06의 multi-surface source
  change는 그때의 accepted Change Set과 fresh Linker classification을 사용한다.

<!-- key: id=key.work.agent-behavior-evaluation.order.completion refs=key.topic.acceptance key.topic.verification -->
## Completion Criteria

<!--
key:
  id: key.acceptance.product-alignment.boundary
  supersedes:
    - key.acceptance.agent-eval.runner-lifecycle
    - key.acceptance.agent-eval.actual-invocation
    - key.acceptance.agent-eval.repeated-settings
-->
- `R010-S05R-CC-01` 제품 목표, 기본 신뢰 경계와 core/non-core 기준이 `DEC-WORKS-029` 및 R010
  recovery 문서에서 일치한다.
<!--
key:
  id: key.acceptance.product-alignment.inventory
  supersedes:
    - key.acceptance.agent-eval.state-identity-binding
-->
- `R010-S05R-CC-02` R010 baseline→S01-S04→frozen S05 branch의 changed source, consumer와
  compatibility가 누락 없이 inventory된다.
<!--
key:
  id: key.acceptance.product-alignment.integrity-boundary
  supersedes:
    - key.acceptance.agent-eval.evidence-validation
-->
- `R010-S05R-CC-03` Git/tree, scoped SHA-256, HMAC, signature와 external attestation의 용도와
  non-goal이 구분되고 기본 경로에 secret이 필요하지 않다.
<!--
key:
  id: key.acceptance.product-alignment.agent-eval-disposition
  supersedes:
    - key.acceptance.agent-eval.adversarial-boundaries
    - key.acceptance.agent-eval.reviewer-separation
    - key.acceptance.agent-eval.adapter-binding
    - key.acceptance.agent-eval.matrix-schema-migration
    - key.acceptance.agent-eval.fixture-redaction
    - key.acceptance.agent-eval.negative-control-hidden-review
    - key.acceptance.agent-eval.execution-budget
-->
- `R010-S05R-CC-04` Actual agent/reviewer/redaction/pricing/score 체계가 core release gate에서 제거되고
  frozen branch와 historical plan disposition이 명시된다.
<!-- key: id=key.acceptance.product-alignment.accepted-history -->
- `R010-S05R-CC-05` S01-S04 acceptance/finalization은 이력으로 보존되고 현재 유지 의무와 구분된다.
<!-- key: id=key.acceptance.product-alignment.standards-first -->
- `R010-S05R-CC-06` Pending standards, installed contracts와 runtime 차이를 식별하고 S06은 기준서
  의미를 먼저 수락 가능한 상태로 만든 뒤 implementation을 시작한다.
<!-- key: id=key.acceptance.product-alignment.s06-change-set -->
- `R010-S05R-CC-07` S06 대상이 exact path/contract/test, retain/simplify/optional/retire disposition,
  compatibility, verification과 stop condition을 가진다.
<!-- key: id=key.acceptance.product-alignment.s07-product-flow -->
- `R010-S05R-CC-08` S07이 기준서→영향→구현·검증→Progress→복구·수락 제품 흐름과 운영 비용을
  검증하며 임의 점수나 외부 reviewer에 의존하지 않는다.
<!-- key: id=key.acceptance.agent-eval.prerequisite-verification -->
- `R010-S05R-CC-09` S02-S04 수락 이력을 prerequisite evidence로 보존하고 S05 document/impact
  verification이 통과한다.
<!-- key: id=key.acceptance.agent-eval.start-gates -->
- `R010-S05R-CC-10` S05 start gate의 과거 만족 상태와 현재 active Step이 일관되며 dependency가
  자동 acceptance나 source edit authority를 만들지 않는다.

<!-- key: id=key.work.agent-behavior-evaluation.order.verification refs=key.topic.verification -->
## Verification

- Git diff/log 기반 R010 changed-path·consumer inventory와 frozen branch non-merge 확인
- Old/new claim `supersedes`, key ID uniqueness, links, status와 recovery text 검사
- Pending standards와 installed/repository contract mismatch 목록
- S06/S07 work gates, completion criterion과 exclusions의 목적 정합성 검토
- Markdown/frontmatter, `git diff --check`와 문서 범위 확인

<!-- key: id=key.work.agent-behavior-evaluation.order.expected-output refs=key.topic.verification key.topic.work-recovery -->
## Expected Output

- R010 product-boundary decision과 개편된 S05-S07 recovery documents
- R010 source/consumer disposition inventory
- S06 exact simplification Change Set과 compatibility/verification matrix
- S07 product workflow scenario와 closure criteria
- Frozen S05 branch와 retired core-gate disposition

<!-- key: id=key.work.agent-behavior-evaluation.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. S01-S04 acceptance history를 삭제하거나 실패로 소급 변경해야 한다.
2. Accepted standard와 현재 source 차이를 확인하지 않고 코드 제거 범위를 확정해야 한다.
3. R011 또는 사용자 소유 변경을 R010 정리 목적으로 덮어써야 한다.
4. External credential, reviewer, model/network 실행이나 새 dependency가 S05 completion에 필요하다.
5. 삭제·schema 호환성 중단·설치 패키지 migration을 S05 문서 판단만으로 실행해야 한다.

## Superseded Historical Claims

다음 ID는 최초 S05 계획의 audit/agent-evaluation 조건을 가리키는 역사적 locator다. 현재
completion criterion이 아니며 위 `key.acceptance.product-alignment.*` claim이 그 의미를 대체한다.
`prerequisite-verification`과 `start-gates`만 이력·gate 보존 목적으로 현재 criterion에 남아 있다.

<!-- key: id=key.acceptance.agent-eval.runner-lifecycle -->
- `R010-S05-CC-01` fixture부터 signed result까지의 actual-eval lifecycle 요구 — superseded.
<!-- key: id=key.acceptance.agent-eval.actual-invocation -->
- `R010-S05-CC-02` 12개 actual skill/model invocation과 transcript 결속 요구 — superseded.
<!-- key: id=key.acceptance.agent-eval.repeated-settings -->
- `R010-S05-CC-03` 복수 model/reasoning setting 반복 실행 요구 — superseded.
<!-- key: id=key.acceptance.agent-eval.state-identity-binding -->
- `R010-S05-CC-04` complete snapshot과 executable/config identity 결속 요구 — superseded.
<!-- key: id=key.acceptance.agent-eval.adversarial-boundaries -->
- `R010-S05-CC-05` agent-eval adversarial scenario 요구 — superseded.
<!-- key: id=key.acceptance.agent-eval.reviewer-separation -->
- `R010-S05-CC-06` independent reviewer와 HMAC 경계 요구 — superseded.
<!-- key: id=key.acceptance.agent-eval.evidence-validation -->
- `R010-S05-CC-07` signed external evidence validation 요구 — superseded.
<!-- key: id=key.acceptance.agent-eval.adapter-binding -->
- `R010-S05-CC-10` invocation adapter와 provider identity digest 결속 요구 — superseded.
<!-- key: id=key.acceptance.agent-eval.matrix-schema-migration -->
- `R010-S05-CC-11` setting × repeat × scenario matrix schema 요구 — superseded.
<!-- key: id=key.acceptance.agent-eval.fixture-redaction -->
- `R010-S05-CC-12` sensitive fixture redaction manifest 요구 — superseded.
<!-- key: id=key.acceptance.agent-eval.negative-control-hidden-review -->
- `R010-S05-CC-13` seeded negative control과 hidden reviewer variation 요구 — superseded.
<!-- key: id=key.acceptance.agent-eval.execution-budget -->
- `R010-S05-CC-14` token/cost/time/attempt budget gate 요구 — superseded.
