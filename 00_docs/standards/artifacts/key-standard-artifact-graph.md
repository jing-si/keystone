---
doc_type: standard
approval: {state: accepted, accepted_at: "2026-08-05", accepted_by: main}
key:
  id: key.standard.artifact.graph
  refs:
    - key.topic.artifact-graph
    - key.topic.keystone-metadata
    - key.topic.code-anchor
    - key.topic.impact-review
    - key.topic.verification
---

# Keystone Artifact Graph 기준서

<!-- key: id=key.standard.artifact.graph.purpose refs=key.topic.artifact-graph key.doc.source -->
## 목적

이 기준서는 Keystone Artifact Graph의 상세 기준을 정의한다. Artifact Graph는 사람의 의도,
원천 문서(2), 결정(6), 작업서(4)를 그 결과로 만들어지거나 통제되는 산출물(output artifact)과
연결하기 위한 Keystone의 관계 계층이다. 산출물은 skill source, code, config, schema, API,
test, generated file, 문서 산출물처럼 여러 surface를 가질 수 있지만, graph의 핵심 관계는
`문서/결정/작업서 -> 산출물`이다.

<!-- key: id=key.standard.artifact.graph.scope refs=key.topic.artifact-graph key.topic.keystone-metadata key.topic.code-anchor -->
## 적용 범위

1. Source document, document section과 독립적으로 참조·변경·대체·검증되는 document item
2. Decision
3. Work order, work node, work step
4. Capability
5. Output artifact
6. Output artifact surface: skill source, code, config, schema, API, test, generated file,
   document artifact
7. Verification evidence
8. Worker assignment와 worker report에서 참조되는 artifact
9. Artifact relation direction, propagation, stale handling, metadata gap, lifecycle 기준

<!-- key: id=key.standard.artifact.graph.out-of-scope refs=key.topic.artifact-graph key.boundary.scope-control -->
## 적용하지 않는 범위

1. 모든 함수와 파일을 완전한 code index로 만드는 것
2. LSP, AST, grep, Sourcegraph류 도구가 더 잘 처리하는 모든 call/reference 관계를 수동
   metadata로 복제하는 것
3. Metadata만으로 실제 code behavior를 확정하는 것
4. Metadata relation만으로 자동 수정이나 자동 acceptance를 수행하는 것

<!-- key: id=key.standard.artifact.graph.standard-relations refs=key.doc.standard key.topic.artifact-graph -->
## 기준 관계

1. Parent 기준서: `../01_key-project-standard.md`
2. 상위 규칙: `STD-KEYSTONE-001`, `STD-KEYSTONE-015`, `STD-KEYSTONE-017`,
   `STD-KEYSTONE-018`, `STD-KEYSTONE-023`, `STD-KEYSTONE-025`, `STD-KEYSTONE-027`,
   `STD-KEYSTONE-044`, `STD-KEYSTONE-046`
3. 관련 스킬 기준서: `../skills/linker/key-standard-linker.md`
4. 관련 결정(6): `00_docs/works/key-decisions.md`의 `DEC-WORKS-009`, `DEC-WORKS-010`,
   `DEC-WORKS-013`, `DEC-WORKS-024`
5. 충돌 처리: 이 기준서와 parent 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의
   결정(6)을 받는다. 결정 전까지는 parent 기준서를 임시 우선 기준으로 삼는다.

<!-- key: id=key.standard.artifact.graph.ownership-boundary refs=key.topic.artifact-graph key.role.linker key.role.author key.role.coordinator -->
## Artifact Graph ownership boundary

Artifact Graph ownership은 graph model, graph interpretation, source edit authority,
acceptance authority로 나눈다.

1. Artifact Graph 기준서는 graph model language를 정의한다.
   - Node kind, artifact namespace, relation vocabulary, relation direction, propagation rule,
     stale handling, metadata gap, locator, lifecycle 기준은 이 기준서가 소유한다.
2. Linker는 Artifact Graph의 유일한 canonical mutation decision owner다.
   - Linker는 source document, 키메타(9), 코드 앵커(18), repository evidence를 read-only로
     해석해 declared/observed/inferred evidence와 후보를 보고하고, artifact ID, capability node,
     relation, provenance, locator, lifecycle과 replacement mutation을 결정한다.
   - Linker의 graph mutation ownership은 어느 source surface의 물리적 write authority도 포함하지 않는다.
3. Author는 source document metadata 변경을 반영한다.
   - 기준서(3), 작업서(4), 결정(6) 기록, 진행 기록(5), Markdown frontmatter의 `key.id`,
     `key.refs`, section-level key comment 수정은 Author 영역이다.
4. Output artifact는 원천 문서(2), 결정(6), 작업서(4)가 요구하거나 통제한 산출물이다.
   - Linker는 산출물이 관련 기준서(3), 작업서(4), 결정(6)과 연결되어 있는지, stale하거나 gap이
     있는지 read-only로 보고할 수 있다.
   - 산출물의 종류가 skill source인지 code인지보다, 어떤 원천 문서나 작업서에서 만들어졌고 어떤
     기준의 지배를 받는지가 graph 판단의 우선 기준이다.
5. Repository source surface 변경은 Main이 처리한다.
   - 작은 명확한 변경은 Main direct로 처리할 수 있다. 위임이 필요하고 사용자가 허락한 경우
     Coordinator가 bounded worker assignment로 조율한다.
6. Repo-local Keystone skill source는 output artifact의 한 surface일 수 있지만 원천 문서(2)가
   아니다.
   - Skill source 수정은 명시 scope 안의 Main direct 또는 사용자 허락을 받은 Coordinator
     assignment로 처리한다.
7. Main은 최종 수락 책임을 가진다.
   - Linker report는 evidence와 handoff input이며 직접 수정 권한, 자동 수정 근거, 자동
     acceptance, Main acceptance가 아니다.
8. Validator는 transaction과 reconstructed graph의 기계적 조건만 진단한다.
   - Validator는 mutation, source meaning, scope, attestation, acceptance 또는 write를 결정하지 않는다.

<!-- key: id=key.standard.artifact.graph.source-surface refs=key.topic.artifact-graph key.topic.keystone-metadata key.topic.code-anchor key.role.linker key.role.author key.role.coordinator -->
## Graph source and output surface

Artifact Graph는 source relation과 output artifact surface를 구분한다. Graph 판단은
`source_document/decision/work_order -> output_artifact` 관계를 우선 보고, 실제 수정 권한은
산출물이 놓인 surface별 lane으로 분리한다.

| Surface | 예 | canonical mutation owner | attestation·수정 owner |
|---|---|---|---|
| Source document frontmatter | `key.id`, `key.refs` | Linker | Author |
| Source document section/item comment | heading, list item, table row의 `<!-- key: id=... -->` | Linker | Author |
| Decision record | `DEC-*` | Linker가 impact를 해석하고 Clarify 또는 Main이 결정을 보강한다 | Author |
| Work order output declaration | completion criteria, expected output, target path | Linker | Author |
| Output artifact: skill source | `skills/keystone-*/SKILL.md` | Linker | Main direct for small approved scope, otherwise Coordinator |
| Output artifact: repository source | code, config, schema, API, test, generated/codegen source | Linker | Main direct 또는 허락된 Coordinator |
| Output artifact: document artifact | generated or maintained Markdown artifact outside source authority | Linker | Author, Main direct, or permitted Coordinator |
| Code anchor | `keystone: id=...`, `provides=...` | Linker | Main direct 또는 허락된 Coordinator |
| Config anchor | config key anchor, feature flag metadata | Linker | Main direct 또는 허락된 Coordinator |
| Schema anchor | DB, message, validation schema anchor | Linker | Main direct 또는 허락된 Coordinator |
| API contract anchor | OpenAPI, RPC contract, route contract anchor | Linker | Main direct/허락된 Coordinator for repository contract, Author for source document section |
| Test anchor | `verifies=...` | Linker | Main direct 또는 허락된 Coordinator |
| Generated reverse index or cache | derived graph index | Linker가 stale 여부를 판단한다 | 초기에는 직접 수정자 없음 |

API contract가 Keystone source document section으로 표현되면 source document metadata로 보아
Author가 수정한다. API contract가 OpenAPI file, route contract, RPC contract, schema file,
code annotation처럼 repository source surface에 있으면 Main direct 또는 허락된 Coordinator가
수정한다.

<!-- key: id=key.standard.artifact.graph.fail-soft refs=key.topic.artifact-graph key.topic.initialization key.role.linker -->
## 핵심 능력과 fail-soft

Artifact Graph는 Keystone의 핵심 능력이지만 모든 프로젝트가 첫날부터 모든 relation과 anchor를
가져야 한다는 뜻은 아니다.

1. Graph metadata 부재만으로 초기화 상태를 `partial`이나 실패로 만들지 않는다.
2. Linker는 존재하는 문서, relation, code anchor와 repository evidence만으로 graph를 해석한다.
3. Evidence가 부족하면 `metadata gap`과 검사 불가능 항목을 확정 오류와 구분해 보고한다.
4. Gap 보고는 자동 수정, Coordinator 호출, 사용자 질문이나 작업 중단을 의미하지 않는다.
5. 프로젝트가 발전하면서 기준서와 산출물의 의미 있는 연결부터 점진적으로 추가한다.

Generated reverse index나 cache가 필요해지면 별도 결정(6)과 bounded workflow를 먼저 둔다.

<!-- key: id=key.standard.artifact.graph.synchronization-contract refs=key.topic.artifact-graph key.topic.change-set key.topic.verification key.role.linker key.role.author key.role.coordinator -->
## Canonical graph synchronization contract

Graph-relevant change는 `document_delta` 또는 `artifact_delta`를 입력으로 synchronization
transaction을 자동 시작한다. 이 자동 trigger는 기존 user-approved scope를 넓히거나
Coordinator permission, worker assignment, acceptance를 자동 생성하지 않는다. 범위 밖 patch가
필요하면 transaction은 그 surface를 적용하지 않고 `conflicted`로 보고한다.

```yaml
change_delta:
  kind: document_delta | artifact_delta
  source_surface:
  changed_locators: []
  semantic_summary:
  baseline_digest: sha256:<64-lowercase-hex> | absent
  graph_relevant: true | false
```

Capability가 문서와 구현 사이의 기본 중심 node다. 여러 artifact에 걸친 기능, 재사용 가능한
behavior 또는 장기 안정성이 필요한 의미는 capability를 거친다. 단일 schema constraint,
특정 policy implementation 또는 한 artifact에만 국한되어 capability가 별도 의미를 만들지
못하는 bounded case는 document item에서 artifact로 직접 relation을 선언할 수 있다. 이 예외는
Linker mutation에 `direct_relation_reason`을 기록하고 broad topic·path overlap에는 사용하지 않는다.

Canonical wire model은 JSON object로 직렬화 가능한 다음 field를 사용한다.

```yaml
graph_node:
  id:
  kind: source_document | document_section | document_item | claim | decision | work_order | work_step | capability | output_artifact | verification_result
  artifact_kind: skill_source | code | config | schema | api | test | generated_file | doc_artifact | none
  locator: {path:, heading:, symbol:, test_name:, config_key:, schema_name:}
  lifecycle: active | deprecated | removed
  provenance: {produced_from: [], governed_by: []}
graph_relation:
  source:
  relation: produces | provides | uses | implements | verifies | depends_on | governed_by | documents | supersedes | derived_from
  target:
  evidence: declared | observed | inferred
  provenance: {surface:, locator:, attested_by:}
  lifecycle: active | deprecated | removed
```

Locator는 path와 함께 heading, symbol, test name, config key 또는 schema name처럼 parser가
기계적으로 확인 가능한 field만 canonical mutation에 사용한다. 자유 자연어만 있는 locator는
note일 수 있지만 apply target은 아니다. Relation은 항상 `source relation target` 방향으로
기록하며 reverse edge는 cache에서만 파생한다. `produced_from`은 provenance이고 typed relation이
아니며, Linker가 source `produces` output 방향 edge를 재구성할 수 있다.

Evidence admission은 다음과 같다.

1. `declared`: source metadata/anchor에 명시되어 Linker가 canonical mutation에 수용할 수 있다.
2. `observed`: repository 구조에서 관찰된 후보이며 해당 surface owner가 의미를 `confirm`해야만
   canonical mutation에 수용할 수 있다.
3. `inferred`: 탐색·검토 후보로만 유지하며 attestation만으로도 자동 mutation하지 않는다.

<!-- key: id=key.standard.artifact.graph.source-representation refs=key.topic.artifact-graph key.topic.keystone-metadata key.topic.code-anchor -->
## Canonical source representation and digest

Markdown source document metadata는 frontmatter와 item comment가 canonical이다. Repository
source의 language comment anchor가 안전하고 구조적으로 표현 가능하면 이를 canonical로 쓰고,
그렇지 않거나 복수 relation·locator·lifecycle을 보존해야 하면 source-adjacent companion
`<source>.keystone.json`을 canonical anchor surface로 쓴다. 중앙 registry는 만들지 않는다.

Companion file은 `schema_version: 1`, `source`, `nodes`, `relations`를 가진 UTF-8 JSON object다.
`source`는 `{path: <repository-relative-path>, surface: <surface-kind>, baseline_digest:
<sha256-or-absent>}` object이며 companion이 설명하는 원본 source를 가리킨다.
각 node/relation은 위 canonical wire model을 따르고 array order는 의미를 갖지 않는다. JSON
serializer는 key를 lexicographic order로 쓰고 불필요한 whitespace를 제거할 수 있지만 digest는
직렬화 결과가 아니라 apply 직전 source file의 실제 UTF-8 raw bytes에 대해 SHA-256을 계산해
`sha256:<64 lowercase hex>`로 기록한다. 각 exact patch는 자기 target source마다 baseline digest를
가진다. 새 file의 wire value는 문자열 `absent`이며 다른 null·빈 문자열 표현을 사용하지 않는다.

Generated reverse index와 cache는 선택적·파생·비권위 artifact다. Cache miss는 source를 다시
parse하며, cache와 source가 다르면 cache를 폐기한다. Cache는 transaction state, attestation,
apply result 또는 acceptance evidence를 대신하지 않는다.

<!-- key: id=key.standard.artifact.graph.transaction-wire refs=key.topic.artifact-graph key.topic.verification key.topic.work-recovery -->
## Synchronization transaction wire and state machine

```yaml
graph_transaction:
  schema_version: 1
  transaction_id:
  scope_ref:
  input_deltas: []
  canonical_mutations:
    - operation: add | update | remove
      entity: node | relation
      before:
      after:
      evidence: declared | observed
      direct_relation_reason:
  surface_patches:
    - patch_id:
      owner: author | main | coordinator
      surface: document_metadata | code_anchor | config_anchor | schema_anchor | api_anchor | test_anchor | companion_metadata
      target_path:
      baseline_digest:
      exact_patch:
      required: true | false
  attestations:
    - patch_id:
      owner:
      decision: confirm | reject | needs_revision
      evidence:
  apply_results:
    - patch_id:
      result: applied | failed | stale_baseline
      resulting_digest:
      evidence:
  state: proposed | awaiting_attestation | ready_to_apply | applying | partially_applied | verified | conflicted | failed
  reconstruction:
  mechanical_validation:
  coverage_debt: []
```

Linker proposal은 exact per-surface patch와 baseline을 포함한다. Owner는 자기 surface의 의미와
patch만 attestation한다. `reject`는 proposal과 source evidence가 양립하지 않음을 뜻하며
`conflicted`, `needs_revision`은 Linker 재계획을 요구한다. Apply 직전 baseline이 다르면 patch를
쓰지 않고 `stale_baseline`으로 기록한다. Apply 결과는 `applied | failed | stale_baseline`만 쓴다.

허용 전이는 다음과 같다.

1. `proposed -> awaiting_attestation`
2. `awaiting_attestation -> ready_to_apply | conflicted`
3. `ready_to_apply -> applying | conflicted`
4. `applying -> partially_applied | verified | conflicted | failed`
5. `partially_applied -> applying | conflicted | failed`
6. `conflicted -> proposed`는 새 baseline과 revised mutation/patch로 재계획할 때만 허용한다.
7. `failed -> proposed`는 원인을 보존하고 새 attempt를 만들 때만 허용한다.

`verified`는 모든 required patch의 `confirm`, apply 직전 baseline 일치, 모든 required result의
`applied`, Linker의 source 재구성 결과가 canonical mutation과 일치함, mechanical validator
통과가 모두 있을 때만 terminal success다. 일부 patch 적용 뒤 중단되면 `partially_applied`로
남기고 이미 적용한 result/digest를 보존한다. Resume은 current digest와 recorded resulting
digest가 같은 patch는 재적용하지 않고, 남은 patch baseline을 다시 확인한다. Orphan relation,
missing target 또는 removed node를 가리키는 active relation은 validator error다. Retired ID를
history/provenance가 참조하는 것은 허용하지만 active semantic relation은 replacement를 명시하거나
제거해야 한다.

<!-- key: id=key.standard.artifact.graph.change-lifecycle refs=key.topic.artifact-graph key.topic.keystone-metadata key.topic.verification -->
## Rename, removal, compatibility and coverage

1. Rename/move 뒤에도 의미와 responsibility가 같으면 stable ID를 유지하고 locator만 갱신한다.
2. 의미가 달라지면 새 ID와 `new supersedes old` relation을 검토한다. Removed ID는 재사용하지
   않고 lifecycle과 history/provenance evidence를 보존한다.
3. Replacement가 없으면 removal mutation이 inbound active relation을 제거·retire하는 patch를
   포함해야 하며 orphan을 남기지 않는다.
4. Legacy metadata는 parser가 read compatibility로 수용한다. 새 metadata와 의미가 변경된
   metadata는 canonical representation으로 수렴시키되 기존 corpus를 bulk migration하지 않는다.
5. Current transaction completeness는 transaction scope의 delta, required patch, attestation,
   baseline, apply, reconstruction, validation으로 판정한다. Project graph coverage는 별도 debt
   지표이며 transaction 밖 legacy gap만으로 current transaction의 `verified`를 차단하지 않는다.

Acceptance finalization은 graph relevance와 `required | not_applicable | deferred` disposition을
기록한다. Required이면 verified transaction evidence가 finalization evidence에 포함되어야 한다.
미완료 required graph sync는 finalization `complete`만 차단하고 Main acceptance를 취소하거나
R004 accepted 기록을 소급 변경하지 않는다.

<!-- key: id=key.standard.artifact.graph.record-model refs=key.topic.artifact-graph key.contract.output -->
## Graph record model

Graph record model은 새 source file format이 아니다. Linker report, worker assignment context,
generated index 후보가 같은 field 의미를 쓰도록 하기 위한 conceptual view다. Canonical source와
transaction wire에서는 앞 절의 `graph_node`와 `graph_relation` field가 유일한 normative schema다.
아래 `artifact_node.authority` view는 그 schema의 `provenance.produced_from`,
`provenance.governed_by`, `artifact_kind`와 verification relation을 표시용으로 묶은 파생 view이며
별도 입력 schema가 아니다.

Artifact node는 다음 field 의미를 우선 사용한다.

```yaml
artifact_node:
  id: key.<namespace>.<meaningful-name>
  kind: source_document | document_section | document_item | claim | decision |
        work_order | work_step | capability | output_artifact | verification_result
  artifact_kind: skill_source | code | config | schema | api | test |
                 generated_file | doc_artifact | none
  locator:
    path:
    heading:
    symbol:
    test_name:
    config_key:
    schema_name:
  lifecycle: active | deprecated | removed
  authority:
    intended_behavior: source_document | decision
    produced_from:
      - source_document | decision | work_order
    governed_by:
      - standard | decision
    operative_evidence: skill_source | code | config | schema | api_contract | generated_file | doc_artifact
    verification_evidence: test | verification_result
```

`authority.produced_from`은 output artifact가 어느 source document, decision 또는 work
order의 산출물인지 기록하는 provenance field다. 이 field 자체는 typed relation이
아니며 `derived_from`과 혼용하지 않는다.

Artifact relation은 다음 field 의미를 우선 사용한다.

```yaml
artifact_relation:
  source: key.<id>
  relation: produces | provides | uses | implements | verifies | depends_on |
            governed_by | documents | supersedes | derived_from
  target: key.<id>
  evidence: declared | observed | inferred
  source_surface: document_metadata | code_anchor | config_anchor |
                  schema_anchor | api_anchor | test_anchor |
                  repository_evidence | generated_index | linker_report
  confidence_note:
```

`declared` relation은 source document metadata나 code/config/schema/API/test anchor에 선언된
relation이다. `observed` relation은 import, call, file path, symbol, test name, config key처럼
repository evidence에서 관찰된 relation이다. `inferred` relation은 의미적으로 관련 가능성이
있지만 자동 수정 근거가 아닌 후보 relation이다.

<!-- key: id=key.standard.artifact.graph.namespace refs=key.topic.artifact-graph key.topic.key-prefix -->
## Artifact namespace

Artifact ID namespace는 다음을 우선 사용한다.

1. `key.doc.*`: source document 또는 document section
2. `key.decision.*`: 수락된 결정
3. `key.work.*`: 작업서, work node, step
4. `key.capability.*`: 사람이 이해하는 기능적 능력
5. `key.output.*`: 기준서(3), 결정(6), 작업서(4)가 만든 산출물을 surface와 무관하게 가리킬 때
   쓰는 일반 namespace
6. `key.api.*`: 외부 또는 내부 계약
7. `key.code.*`: stable code artifact 또는 의미 있는 symbol
8. `key.config.*`: runtime config, feature flag, policy config 같은 설정 artifact
9. `key.schema.*`: DB schema, message schema, validation schema 같은 구조화 contract
10. `key.test.*`: capability, API, behavior를 검증하는 test artifact
11. `key.skill.*`: repo-local Keystone skill source나 skill behavior contract를 별도 namespace로
    추적할 필요가 있을 때 쓰는 output artifact namespace
12. `key.verification.*`: stable verification result나 verification evidence가 반복 참조될 때 쓰는
    artifact
13. `key.rule.*`: 기준서나 결정 안에서 독립적으로 참조·변경·폐기할 수 있는 규칙
14. `key.claim.*`: 결정이나 설명 안에서 다른 claim과 별도로 대체될 수 있는 의미 주장
15. `key.acceptance.*`: 독립적으로 검증하고 결과를 추적할 필요가 있는 acceptance 항목

Artifact ID는 path나 line number가 아니라 의미와 책임을 기준으로 정한다.
모든 command result를 artifact node로 만들 필요는 없으며, 일회성 검증 결과는 worker report나
verification note에 둘 수 있다.

<!-- key: id=key.standard.artifact.graph.document-item-metadata refs=key.topic.artifact-graph key.topic.keystone-metadata key.topic.impact-review -->
## Document item metadata

Document item은 Markdown 문서 안에서 다른 항목과 독립적으로 참조·변경·대체·검증할 수 있는
의미 단위다. 문서와 section metadata가 있어도 아래 항목은 필요할 때 별도의 stable `key.id`를
가질 수 있다.

1. 번호가 있는 normative rule, 금지·허용·필수 조건
2. 결정과 결정 안에서 부분적으로 대체될 수 있는 claim
3. Work step, completion criterion과 acceptance criterion
4. Capability, API·schema·config contract 또는 책임 처분
5. 여러 문서가 참조하거나 독립적인 lifecycle을 가질 수 있는 표의 행
6. 과거 변경에서 반복적으로 stale candidate가 된 의미 단위

모든 문장, bullet, 표 행에 metadata를 붙이지 않는다. 단순 설명, 예시, 순서 없는 열거,
상위 의미를 반복하는 문장과 독립적으로 변경하거나 참조할 수 없는 조각은 부모 metadata를
상속한다. 표시 번호나 표의 visible ID는 locator이며 stable `key.id`를 대신하지 않는다.

Document item metadata의 최소 선언은 `id`다. `refs`, typed relation, `lifecycle`과
`legacy_terms`는 해당 항목에 실제로 필요한 경우에만 선언한다.

Heading과 list item은 대상 바로 위 comment를 사용한다.

```markdown
<!-- key: id=key.rule.verification.graph-validation -->
- Artifact Graph가 관련되면 graph validation을 verification 후보에 포함한다.
```

Markdown 표는 행 사이의 comment로 표 구조를 깨뜨리지 않는다. 독립 node가 필요한 행은 첫 번째
cell 안에 compact comment를 두고 visible row ID를 locator로 유지한다.

```markdown
| <!-- key: id=key.acceptance.worker.planning-grouping verifies=key.claim.worker.planning-boundary --> `PA-PLAN-01` | 입력 | 기대 결과 |
```

Document item은 부모 document와 section의 `governed_by`, source authority와 lifecycle을
기본 상속한다. `id`와 `supersedes`는 상속하지 않는다. Item lifecycle이 부모와 다를 때만
명시하며, 자식 선언은 부모의 source authority를 조용히 확대하거나 변경할 수 없다.

결정 전체가 하나의 대체 단위이면 `key.decision.*`를 사용한다. 결정의 일부 의미만 후속 결정이
대체하고 나머지는 유지하면 그 부분을 `key.claim.*`으로 분리하고 새 claim에서 이전 claim으로
`supersedes`를 선언한다. 문서 전체 relation으로 부분 대체를 표현하지 않는다.

`legacy_terms`는 `supersedes` 또는 명시적인 deprecated/removed lifecycle이 있는 item에서만
사용하는 검색 보조 metadata다. 정확한 과거 이름, identifier, route, table·column 이름처럼
기계적으로 검색 가능한 표현만 기록하고 `batch`, `handler`, `plan` 같은 넓은 일반 단어는
단독 legacy term으로 사용하지 않는다. `legacy_terms`는 typed relation이 아니며 replacement
item이나 removed item의 의미 사전을 보조한다.

```markdown
<!--
key:
  id: key.claim.worker.planning-query-chunk
  supersedes:
    - key.claim.worker.pk-batch-planning
  legacy_terms:
    - WorkOrderBatchJob
    - Planning Tick Job
    - PK batch
-->
```

기존 corpus에 item metadata가 없다는 사실만으로 초기화나 문서 전체를 실패시키지 않는다.
새로 작성하거나 의미를 변경한 독립 항목은 metadata admission policy에 따라 item metadata를
검토하고, 기존 항목의 누락은 Linker가 evidence에 따라 metadata gap 후보로 보고한다.

<!-- key: id=key.standard.artifact.graph.api-artifact-policy refs=key.topic.artifact-graph key.topic.api key.work.decisions.dec-works-010 -->
## API artifact policy

API artifact는 first-class artifact지만 기본적으로 capability provider가 아니라 contract artifact로
본다.

1. `key.api.*`는 외부 또는 내부 caller가 의존하는 API, route, RPC, command/query, message
   contract, plugin interface 같은 contract를 나타낸다.
2. Capability는 기본적으로 code/config/schema artifact가 `provides`한다.
3. Code/config/schema artifact는 API 또는 결정된 contract를 `implements`한다.
4. Test는 API 또는 capability를 `verifies`할 수 있고, source document는 API 또는 capability를
   `documents`할 수 있다.
5. API 변경은 implementing artifact, verifying test, source document, related capability의
   impact/stale 후보를 만들 수 있다.
6. API artifact 자체를 capability provider로 보려면 accepted decision 또는 명시된 예외 relation
   policy가 필요하다.
7. 예외가 없으면 `provides` relation에 `key.api.* -> key.capability.*`를 기본 허용하지 않는다.

Graph record model의 `api_contract` operative evidence는 operative contract evidence를 뜻하며,
API artifact가 capability provider라는 뜻은 아니다.

<!-- key: id=key.standard.artifact.graph.typed-relation refs=key.topic.artifact-graph key.topic.code-anchor -->
## Typed relation

초기 typed relation은 다음을 사용한다.

1. `produces`: source document, decision, 또는 work order가 output artifact를 산출하거나 요구한다.
2. `provides`: code/config/schema artifact가 capability를 제공한다.
3. `uses`: artifact가 다른 capability, API, code artifact를 의미적으로 사용한다.
4. `implements`: code/config/schema artifact가 API 또는 결정된 contract를 구현한다.
5. `verifies`: test artifact가 capability, API, decision, code behavior를 검증한다.
6. `governed_by`: artifact가 기준서(3)나 결정(6)의 규칙을 따른다.
7. `documents`: source document가 artifact를 설명한다.
8. `supersedes`: 새 artifact가 기존 artifact를 대체한다.
9. `derived_from`: artifact가 다른 artifact나 source에서 파생되었다.
10. `depends_on`: source artifact/work가 target artifact/work의 의미·산출·선행 상태에 의존한다.

`produced_from`은 이 typed relation 목록에 추가하지 않는다. Output artifact에 선언된
`authority.produced_from: <source>`은 Linker나 generated index가 `<source> produces <output>`의
역방향 edge로 파생할 수 있다. 파생 edge의 evidence는 `inferred` 또는 generated
evidence로 표시하고 source surface에 양방향 relation을 중복 기록하지 않는다.
Target이 존재하지 않거나 work order로 해석할 수 없으면 unresolved provenance
또는 metadata gap으로 보고한다.

`revised_by`는 문서·artifact의 개정 이력을 가리키는 revision-history evidence로
인식하되 공식 typed relation에 추가하지 않는다. `revised_by`만으로 authority,
impact propagation, `supersedes`, `produces`, `governed_by`를 추론하지 않는다. 정확한
의미가 필요하면 적합한 typed relation, 결정(6), Change Set(17) 또는 revision record로
명시한다. Target이 없거나 의미가 모호하면 relation error로 승격하지 않고
informational 또는 unknown revision evidence로 보고한다.

`key.refs`는 넓은 관련성이나 탐색 후보를 표현한다. Impact propagation과 execution boundary는
가능한 한 typed relation과 repository evidence를 기준으로 판단한다.

<!-- key: id=key.standard.artifact.graph.relation-propagation refs=key.topic.artifact-graph key.topic.impact-review key.topic.code-anchor -->
## Relation direction and propagation

Typed relation은 source에서 target으로 읽는다. Reverse relation은 source surface에 중복 기록하지
않고 generated reverse index나 Linker report에서 파생할 수 있다.

| Relation | Direction | 기본 impact 해석 |
|---|---|---|
| `produces` | source document/decision/work order -> output artifact | source 변경 시 output artifact는 `required`; output artifact 변경 시 source는 stale review 후보 |
| `provides` | code/config/schema artifact -> capability | capability 변경 시 provider는 `required`; provider 변경 시 capability는 `strong_candidate` 이상 |
| `uses` | artifact -> capability/API/code artifact | target 변경 시 source는 `strong_candidate`; source 변경 시 target은 보통 `informational` |
| `implements` | code/config/schema -> API/contract/decision | contract 변경 시 implementer는 `required` |
| `verifies` | test -> capability/API/decision/code behavior | target 변경 시 test는 `required` |
| `governed_by` | artifact -> standard/decision | governing source 변경 시 artifact는 `required` 또는 `strong_candidate` |
| `documents` | source document/section -> artifact | artifact 변경 시 document는 `strong_candidate`; broad mention은 `key.refs`로 둔다 |
| `supersedes` | new artifact -> old artifact | old reference 발견 시 stale 또는 `required` review 후보 |
| `derived_from` | derived/generated artifact -> source artifact | source 변경 시 derived artifact는 regeneration 또는 review 후보 |
| `depends_on` | source artifact/work -> target artifact/work | target 변경 시 source는 `required` 또는 `strong_candidate`; 실행 차단은 `work_gates`가 결정 |

제한은 다음과 같다.

1. 모든 import, call, filename overlap을 typed relation으로 승격하지 않는다.
2. Repository tool이 더 잘 처리하는 structural dependency는 observed evidence로 보고할 수 있다.
3. Typed relation은 semantic relation일 때만 source surface에 선언한다.
4. `uses`는 단순 import, local helper call, private implementation detail에는 기본적으로 쓰지
   않는다.
5. `derived_from`은 generated artifact, schema-derived type, API client generated from API
   contract처럼 파생 관계가 명확한 경우에 우선 사용한다.
6. Work order가 output artifact를 만든 provenance는 `produced_from` field와 역방향
   `produces` edge로 다루고 artifact-to-artifact 파생 `derived_from`으로 바꾸지 않는다.
7. `revised_by`는 revision-history evidence로만 사용하고 semantic relation이 필요하면
   해당 의미의 공식 typed relation 또는 Change Set으로 명시한다.

<!-- key: id=key.standard.artifact.graph.dependency-work-gate refs=key.topic.artifact-graph key.topic.work-sequence key.topic.work-recovery key.topic.verification -->
## Dependency and work gate

Dependency metadata는 의미 관계와 실행 gate를 다음처럼 분리한다.

```yaml
key:
  relations:
    depends_on:
      - target: key.work.target

work_gates:
  - dependency: key.work.target
    applies_to:
      steps: [S08, S09]
      work_completion: true
    condition:
      work_status: complete
    optional: false
```

1. `depends_on` 방향은 source -> target이며 source가 target의 의미·산출·선행 상태에
   의존함을 나타낸다. Relation 자체는 시작 금지·상태 전이·스케줄러 명령이 아니다.
2. `work_gates[].dependency`는 같은 source의 declared `depends_on` target을 가리켜야 한다.
3. `applies_to.steps`는 gate가 적용되는 source step ID 목록, `work_completion`은 source work
   종료 적용 여부다. 둘 중 하나 이상을 명시한다.
4. `condition.work_status`는 target이 충족해야 할 상태다. Project가 명시적으로
   확장하지 않으면 `complete`를 사용한다.
5. `optional: true`는 target 미충족을 blocking으로 사용하지 않는다는 뜻이지 relation이나
   검증을 삭제한다는 뜻이 아니다.
6. Legacy `<!-- keystone: depends_on=... -->`은 structured metadata가 없을 때만 relation
   evidence로 읽는다. 역사적 work-level dependency에 gate가 없으면 source start는 허용하고
   `work_completion: true`인 후보로 보고한다.
7. Structured/legacy target이 다르면 structured를 우선하고 `invalid` 또는 source conflict를 보고한다.

Dependency evaluation은 다음을 사용한다.

| 판정 | 의미 |
|---|---|
| `satisfied` | target이 존재하고 gate condition을 충족한다 |
| `waiting` | target이 유효하지만 condition을 아직 충족하지 않았다 |
| `unresolvable` | target이 없거나 cancelled/superseded 정책을 현재 evidence로 해소할 수 없다 |
| `invalid` | duplicate, self-reference, invalid step, conflict 또는 cycle이 있다 |
| `unknown` | 상태 evidence가 부족해 판정할 수 없다 |

Cancelled target은 수용된 대체·예외 결정이 없으면 `unresolvable`이다. Superseded target은
명시적 successor가 있어도 자동 대체하지 않고 declared relation 또는 Main/user 결정이 있을 때만
새 target으로 이동한다. Evaluation은 work status를 자동 수정하지 않는다.

검증은 target existence, duplicate target/gate, source-target self-reference, source step existence,
condition value, structured/legacy conflict를 검사한다. Cycle은 work node graph만으로 판정하지 않고
source step start/completion, target condition satisfaction, source work completion event를 펼친 expanded
event graph에서 판정한다.

<!-- key: id=key.standard.artifact.graph.metadata-admission refs=key.topic.code-anchor key.topic.artifact-graph key.boundary.scope-control -->
## Metadata admission policy

Artifact metadata는 모든 code symbol에 붙이지 않는다. 다음 조건 중 하나에 해당하는 artifact에
우선 부여한다.

1. 사람이 수락한 기준서(3)나 결정(6)과 직접 연결된다.
2. 기준서(3), 결정(6), 작업서(4)의 명시 산출물이며 `produces` 또는 `governed_by` relation으로
   추적해야 한다.
3. 새 기능 작성 전에 재사용 후보로 발견되어야 한다.
4. Module 또는 service 경계를 넘는 API나 contract다.
5. Domain rule, policy, security, auth, billing, data consistency처럼 의미 있는 behavior를 가진다.
6. Runtime config, feature flag, schema, validation rule처럼 behavior나 compatibility에 직접
   영향을 주는 contract다.
7. 중요한 regression 또는 contract test다.
8. 여러 작업서(4)에서 반복 참조될 가능성이 높다.

다음 artifact에는 기본적으로 metadata를 붙이지 않는다.

1. Local helper
2. Trivial wrapper
3. 단순 formatting function
4. Generated code
5. 일회성 script 또는 migration helper
6. 실험용 prototype

Generated code가 API contract나 schema의 operative output처럼 보여도 기본 anchor는 source
schema/API/config contract에 둔다. Generated file은 필요하면 `derived_from` relation 또는
regeneration candidate로 다룬다.

<!-- key: id=key.standard.artifact.graph.capability-node refs=key.topic.artifact-graph key.boundary.scope-control -->
## Capability node 기준

Capability node는 code symbol보다 안정적인 기능 단위가 필요할 때 만든다.

다음 조건 중 하나에 해당하면 capability node를 만들 수 있다.

1. 하나의 문서 의도나 결정(6)이 여러 code/config/schema/API/test artifact에 걸쳐 구현된다.
2. 새 기능 작성 전에 reuse 여부를 판단해야 하는 안정적 기능 단위다.
3. 기준서(3)나 결정(6)이 직접 govern하는 domain behavior다.
4. 여러 작업서(4)에서 반복 참조될 가능성이 높다.
5. Code symbol보다 오래 유지될 이름이 필요하다.

다음 경우에는 capability node를 만들지 않는다.

1. 단일 private helper와 1:1로만 대응한다.
2. 함수명 재표현에 불과하다.
3. 한 번 쓰고 폐기될 prototype behavior다.
4. Formatting, adapter, trivial wrapper 수준이다.

<!-- key: id=key.standard.artifact.graph.locator refs=key.topic.artifact-graph key.topic.code-anchor -->
## Locator

Artifact `key.id`는 locator와 분리한다. Locator는 path, symbol, test name, config key, schema
name 같은 현재 위치 evidence다.

예:

```yaml
key:
  id: key.code.auth.lockout-service.apply-policy
  kind: code_artifact

locator:
  path: src/auth/lockout_service.ts
  symbol: LockoutService.applyPolicy
```

파일 이동이나 symbol rename이 있어도 의미가 유지되면 `key.id`는 유지할 수 있다. 의미가 바뀌면
새 ID 또는 `supersedes` relation을 검토한다.

<!-- key: id=key.standard.artifact.graph.lifecycle-replacement refs=key.topic.artifact-graph key.topic.code-anchor -->
## Lifecycle and replacement

Artifact lifecycle은 필요할 때 `active`, `deprecated`, `removed`로 표현한다.

Replacement relation policy는 다음을 따른다.

1. Source surface에 직접 기록하는 canonical replacement relation은 `supersedes`를 우선 사용한다.
2. `replaced_by`는 generated reverse index에서 파생할 수 있지만 source relation으로 중복 기록하지
   않는다.
3. `aliases`는 typed relation이 아니라 locator 또는 name migration 보조 metadata다.
4. Removed artifact의 ID는 새 의미에 재사용하지 않는다.
5. 의미와 responsibility가 유지되면 locator 변경만 기록하고 새 ID를 만들지 않는다.

<!-- key: id=key.standard.artifact.graph.stale-handling refs=key.topic.artifact-graph key.topic.verification key.topic.review -->
## Stale metadata handling

Metadata stale은 두 종류로 나눈다.

1. Mechanical stale
   - target id 없음
   - locator path 없음
   - symbol 없음
   - duplicate id
   - broken relation
   - relation format 오류
2. Semantic stale
   - artifact는 존재하지만 더 이상 선언된 capability를 제공하지 않는다.
   - test는 존재하지만 더 이상 해당 behavior를 검증하지 않는다.
   - 문서와 code behavior가 의미상 충돌한다.
   - `uses` relation이 구현 세부사항으로 바뀌어 의미 관계로 보기 어렵다.
   - Active 또는 pending 권위 item에 superseded item의 `legacy_terms`가 허용 근거 없이 남아 있다.
   - Progress나 verification item이 구 표현 제거를 완료했다고 선언했지만 active source item에
     해당 표현이 남아 있다.

Mechanical stale은 verifier 또는 graph validation이 확인한다. Semantic stale은
`keystone-linker`와 reviewer가 후보로 보고하고 Main 또는 사용자가 판단한다.

<!-- key: id=key.standard.artifact.graph.metadata-gap refs=key.topic.artifact-graph key.topic.impact-review key.role.linker -->
## Metadata gap

Metadata gap은 artifact나 relation이 틀렸다는 뜻이 아니라, Artifact Graph에 포함될 필요가 높은
semantic anchor가 아직 source surface에 선언되지 않았다는 후보다.

예시는 다음과 같다.

1. 기준서(3)나 결정(6)이 capability를 정의하지만 provider code anchor가 없다.
2. 중요한 API/schema/config가 작업서(4) completion criteria에 반복 등장하지만 artifact ID가 없다.
3. Test가 핵심 behavior를 검증하지만 `verifies` relation이 없다.
4. Repository evidence는 강하지만 declared relation이 없다.
5. Capability reuse 판단이 필요한데 capability node가 없다.
6. 독립적으로 대체되거나 검증되는 decision claim, normative rule, acceptance row에 item ID가
   없어 문서 전체보다 좁은 impact와 stale 여부를 판정할 수 없다.

Metadata gap은 자동 수정 근거가 아니다. Linker는 gap 후보와 evidence를 보고한다. Source
document metadata gap은 Author handoff로, code/config/schema/API/test anchor gap은 Coordinator
handoff로 넘긴다.

<!-- key: id=key.standard.artifact.graph.impact-candidate refs=key.topic.impact-review key.topic.artifact-graph -->
## Impact candidate

Impact candidate는 다음 등급으로 보고한다.

1. `required`: 직접 typed relation, 명시된 acceptance criteria, 직접 code/config/schema/API/test
   dependency로 반드시 검토해야 한다.
2. `strong_candidate`: 같은 capability, API, decision, 주요 domain keyword를 공유해 검토
   우선순위가 높다.
3. `weak_candidate`: 넓은 topic overlap이나 간접 evidence가 있다.
4. `informational`: 참고 evidence로만 남긴다.
5. `excluded`: 현재 scope에서 제외한다는 이유가 있다.

Candidate 발견은 수정 허가가 아니다. 실제 변경은 승인 범위, source authority, artifact
authority를 따르고, 위임이 필요하면 사용자 허락을 받은 Coordinator를 사용한다.

<!-- key: id=key.standard.artifact.graph.generated-index refs=key.topic.artifact-graph key.doc.derived-agent key.boundary.scope-control -->
## Generated graph index policy

Generated reverse index나 graph cache는 source of truth가 아니다.

1. Source of truth는 source document, 키메타(9), 코드 앵커(18), repository evidence다.
2. 초기 Keystone 기준에서는 Linker가 generated index를 직접 생성하거나 갱신하지 않는다.
3. Linker는 generated index 필요성, stale risk, omitted candidate를 report할 수 있다.
4. Generated index 작성이 필요해지면 별도 결정(6)과 bounded workflow를 먼저 둔다.
5. Generated index가 source document, code anchor, repository evidence와 충돌하면 source
   surface를 우선하고 generated index는 stale candidate로 보고한다.

<!-- key: id=key.standard.artifact.graph.simulation-cases refs=key.topic.integration-verification key.topic.artifact-graph key.topic.verification -->
## Simulation cases for later integration verification

R002 Bootstrap Runtime Standard와 후속 Skill Runtime Implementation은 최소한 다음 case를 사용해
Artifact Graph model을 검증한다.

1. Document-driven behavior change
   - Standard section changes.
   - Capability, provider code/config/schema, verifying test become required or strong
     candidates according to relation evidence.
2. Rename without semantic change
   - `key.id` remains stable.
   - Locator changes.
   - No new artifact ID is created.
3. Semantic drift
   - Symbol still exists.
   - Declared capability no longer matches behavior.
   - Semantic stale candidate is reported.
4. Metadata gap
   - Important API, config, schema, or test exists without anchor.
   - Gap is reported without automatic source change.
5. Generated code boundary
   - Generated file is not anchored by default.
   - Source schema/API/config contract remains the anchor.
6. Item-level partial supersession
   - A later decision supersedes one claim of an earlier decision while the remaining claims stay valid.
   - Impact propagation starts from the superseded claim rather than both documents in full.
7. Legacy term closure
   - An active item retains a legacy term after progress claims its removal.
   - The active item is reported as semantic stale while archived, rejected, or explicit historical
     evidence remains informational or excluded.

<!-- key: id=key.standard.artifact.graph.verification refs=key.topic.verification key.topic.artifact-graph -->
## Verification

Artifact Graph 기준은 다음 방법으로 검증한다.

1. Graph model language와 Linker의 canonical mutation decision ownership을 구분할 수 있어야 한다.
2. Source document metadata 수정 owner와 code/config/schema/API/test anchor 수정 owner를 구분할 수
   있어야 한다.
3. Metadata admission policy만 보고 어떤 artifact에 metadata를 붙일지 판단할 수 있어야 한다.
4. `key.refs`와 typed relation의 책임 차이가 명확해야 한다.
5. Relation direction과 propagation 기본값을 보고 impact candidate 등급을 설명할 수 있어야 한다.
6. Locator와 stable ID가 분리되어야 한다.
7. Mechanical stale, semantic stale, metadata gap을 구분할 수 있어야 한다.
8. Impact candidate 등급이 자동 수정 또는 자동 acceptance로 해석되지 않아야 한다.
9. Generated graph index가 source of truth나 Linker write target으로 해석되지 않아야 한다.
10. Graph evidence 부재가 초기화 실패나 자동 Coordinator 호출로 해석되지 않아야 한다.
11. Heading, list item과 table row의 독립 의미에 stable item ID를 부여할 수 있어야 한다.
12. 부분 대체는 document 전체가 아니라 claim-level `supersedes`로 표현할 수 있어야 한다.
13. Active item의 legacy term과 정상적인 historical evidence를 구분할 수 있어야 한다.
14. Verification command:
   - `rg --files 00_docs`
   - `rg -n "key.capability|key.code|key.config|key.schema|key.api|key.test|keystone-linker" 00_docs/standards`
   - `rg -n "Artifact Graph ownership boundary|Document item metadata|Metadata gap|Relation direction|Generated graph index" 00_docs/standards/artifacts/key-standard-artifact-graph.md`
