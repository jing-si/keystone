---
doc_type: standard
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

이 기준서는 Keystone Artifact Graph의 상세 기준을 정의한다. Artifact Graph는 사람의 의도와
원천 문서(2)를 capability, code, config, schema, API, test artifact와 연결하기 위한 Keystone의
관계 계층이다.

<!-- key: id=key.standard.artifact.graph.scope refs=key.topic.artifact-graph key.topic.keystone-metadata key.topic.code-anchor -->
## 적용 범위

1. Source document와 document section
2. Decision
3. Work order, work node, work step
4. Capability
5. Code artifact
6. Config artifact
7. Schema artifact
8. API artifact
9. Test artifact
10. Verification evidence
11. Worker assignment와 worker report에서 참조되는 artifact
12. Artifact relation direction, propagation, stale handling, metadata gap, lifecycle 기준

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
   `STD-KEYSTONE-044`
3. 관련 스킬 기준서: `../skills/linker/key-standard-linker.md`
4. 관련 결정(6): `00_docs/works/key-decisions.md`의 `DEC-WORKS-009`
5. 충돌 처리: 이 기준서와 parent 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의
   결정(6)을 받는다. 결정 전까지는 parent 기준서를 임시 우선 기준으로 삼는다.

<!-- key: id=key.standard.artifact.graph.ownership-boundary refs=key.topic.artifact-graph key.role.linker key.role.author key.role.coordinator -->
## Artifact Graph ownership boundary

Artifact Graph ownership은 graph model, graph interpretation, source edit authority,
acceptance authority로 나눈다.

1. Artifact Graph 기준서는 graph model language를 정의한다.
   - Node kind, artifact namespace, relation vocabulary, relation direction, propagation rule,
     stale handling, metadata gap, locator, lifecycle 기준은 이 기준서가 소유한다.
2. Linker는 Artifact Graph의 operational interpretation owner다.
   - Linker는 source document, 키메타(9), 코드 앵커(18), repository evidence를 read-only로
     해석해 declared relation, observed relation, inferred relation, impact candidate, stale
     candidate, metadata gap, reuse candidate, test candidate를 판단하고 보고한다.
   - Linker의 graph interpretation ownership은 source edit authority를 포함하지 않는다.
3. Author는 source document metadata 변경을 반영한다.
   - 기준서(3), 작업서(4), 결정(6) 기록, 진행 기록(5), Markdown frontmatter의 `key.id`,
     `key.refs`, section-level key comment 수정은 Author 영역이다.
4. Coordinator는 code/config/schema/API/test source surface 변경을 조율한다.
   - Code anchor, config anchor, schema anchor, repository API contract anchor, test anchor,
     implementation edit은 bounded
     worker assignment로 처리한다.
5. Main 또는 사용자는 최종 수락 책임을 가진다.
   - Linker report는 evidence와 handoff input이며 직접 수정 권한, 자동 수정 근거, 자동
     acceptance, Main acceptance가 아니다.

<!-- key: id=key.standard.artifact.graph.source-surface refs=key.topic.artifact-graph key.topic.keystone-metadata key.topic.code-anchor key.role.linker key.role.author key.role.coordinator -->
## Graph source surface

Artifact Graph source surface는 graph 판단 대상과 실제 수정 권한을 분리하기 위해 다음 기준을
따른다.

| Surface | 예 | 판단 owner | 수정 owner |
|---|---|---|---|
| Source document frontmatter | `key.id`, `key.refs` | Linker | Author |
| Source document section comment | `<!-- key: id=... refs=... -->` | Linker | Author |
| Decision record | `DEC-*` | Linker가 impact를 해석하고 Clarify 또는 Main이 결정을 보강한다 | Author |
| Code anchor | `keystone: id=...`, `provides=...` | Linker | Coordinator |
| Config anchor | config key anchor, feature flag metadata | Linker | Coordinator |
| Schema anchor | DB, message, validation schema anchor | Linker | Coordinator |
| API contract anchor | OpenAPI, RPC contract, route contract anchor | Linker | Coordinator for repository contract, Author for source document section |
| Test anchor | `verifies=...` | Linker | Coordinator |
| Generated reverse index or cache | derived graph index | Linker가 stale 여부를 판단한다 | 초기에는 직접 수정자 없음 |

API contract가 Keystone source document section으로 표현되면 source document metadata로 보아
Author가 수정한다. API contract가 OpenAPI file, route contract, RPC contract, schema file,
code annotation처럼 repository source surface에 있으면 Coordinator가 bounded worker assignment로
수정한다.

Generated reverse index나 cache가 필요해지면 별도 결정(6)과 bounded workflow를 먼저 둔다.

<!-- key: id=key.standard.artifact.graph.record-model refs=key.topic.artifact-graph key.contract.output -->
## Graph record model

Graph record model은 새 source file format이 아니다. Linker report, worker assignment context,
generated index 후보가 같은 field 의미를 쓰도록 하기 위한 conceptual shape다.

Artifact node는 다음 field 의미를 우선 사용한다.

```yaml
artifact_node:
  id: key.<namespace>.<meaningful-name>
  kind: document_section | decision | work_order | work_step | capability |
        code_symbol | code_module | api_contract | config_key |
        schema_contract | test_case | verification_result
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
    operative_evidence: code | config | schema | api_contract
    verification_evidence: test | verification_result
```

Artifact relation은 다음 field 의미를 우선 사용한다.

```yaml
artifact_relation:
  source: key.<id>
  relation: provides | uses | implements | verifies |
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
5. `key.api.*`: 외부 또는 내부 계약
6. `key.code.*`: stable code artifact 또는 의미 있는 symbol
7. `key.config.*`: runtime config, feature flag, policy config 같은 설정 artifact
8. `key.schema.*`: DB schema, message schema, validation schema 같은 구조화 contract
9. `key.test.*`: capability, API, behavior를 검증하는 test artifact
10. `key.verification.*`: stable verification result나 verification evidence가 반복 참조될 때 쓰는
    artifact

Artifact ID는 path나 line number가 아니라 의미와 책임을 기준으로 정한다.
모든 command result를 artifact node로 만들 필요는 없으며, 일회성 검증 결과는 worker report나
verification note에 둘 수 있다.

<!-- key: id=key.standard.artifact.graph.typed-relation refs=key.topic.artifact-graph key.topic.code-anchor -->
## Typed relation

초기 typed relation은 다음을 사용한다.

1. `provides`: code/config/schema artifact가 capability를 제공한다.
2. `uses`: artifact가 다른 capability, API, code artifact를 의미적으로 사용한다.
3. `implements`: code/schema/config artifact가 API 또는 결정된 contract를 구현한다.
4. `verifies`: test artifact가 capability, API, decision, code behavior를 검증한다.
5. `governed_by`: artifact가 기준서(3)나 결정(6)의 규칙을 따른다.
6. `documents`: source document가 artifact를 설명한다.
7. `supersedes`: 새 artifact가 기존 artifact를 대체한다.
8. `derived_from`: artifact가 다른 artifact나 source에서 파생되었다.

`key.refs`는 넓은 관련성이나 탐색 후보를 표현한다. Impact propagation과 execution boundary는
가능한 한 typed relation과 repository evidence를 기준으로 판단한다.

<!-- key: id=key.standard.artifact.graph.relation-propagation refs=key.topic.artifact-graph key.topic.impact-review key.topic.code-anchor -->
## Relation direction and propagation

Typed relation은 source에서 target으로 읽는다. Reverse relation은 source surface에 중복 기록하지
않고 generated reverse index나 Linker report에서 파생할 수 있다.

| Relation | Direction | 기본 impact 해석 |
|---|---|---|
| `provides` | code/config/schema artifact -> capability | capability 변경 시 provider는 `required`; provider 변경 시 capability는 `strong_candidate` 이상 |
| `uses` | artifact -> capability/API/code artifact | target 변경 시 source는 `strong_candidate`; source 변경 시 target은 보통 `informational` |
| `implements` | code/schema/config -> API/contract/decision | contract 변경 시 implementer는 `required` |
| `verifies` | test -> capability/API/decision/code behavior | target 변경 시 test는 `required` |
| `governed_by` | artifact -> standard/decision | governing source 변경 시 artifact는 `required` 또는 `strong_candidate` |
| `documents` | source document/section -> artifact | artifact 변경 시 document는 `strong_candidate`; broad mention은 `key.refs`로 둔다 |
| `supersedes` | new artifact -> old artifact | old reference 발견 시 stale 또는 `required` review 후보 |
| `derived_from` | derived/generated artifact -> source artifact | source 변경 시 derived artifact는 regeneration 또는 review 후보 |

제한은 다음과 같다.

1. 모든 import, call, filename overlap을 typed relation으로 승격하지 않는다.
2. Repository tool이 더 잘 처리하는 structural dependency는 observed evidence로 보고할 수 있다.
3. Typed relation은 semantic relation일 때만 source surface에 선언한다.
4. `uses`는 단순 import, local helper call, private implementation detail에는 기본적으로 쓰지
   않는다.
5. `derived_from`은 generated artifact, schema-derived type, API client generated from API
   contract처럼 파생 관계가 명확한 경우에 우선 사용한다.

<!-- key: id=key.standard.artifact.graph.metadata-admission refs=key.topic.code-anchor key.topic.artifact-graph key.boundary.scope-control -->
## Metadata admission policy

Artifact metadata는 모든 code symbol에 붙이지 않는다. 다음 조건 중 하나에 해당하는 artifact에
우선 부여한다.

1. 사람이 수락한 기준서(3)나 결정(6)과 직접 연결된다.
2. 새 기능 작성 전에 재사용 후보로 발견되어야 한다.
3. Module 또는 service 경계를 넘는 API나 contract다.
4. Domain rule, policy, security, auth, billing, data consistency처럼 의미 있는 behavior를 가진다.
5. Runtime config, feature flag, schema, validation rule처럼 behavior나 compatibility에 직접
   영향을 주는 contract다.
6. 중요한 regression 또는 contract test다.
7. 여러 작업서(4)에서 반복 참조될 가능성이 높다.

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
authority, Coordinator workflow를 따른다.

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

S09 Integration Verification은 최소한 다음 case를 사용해 Artifact Graph model을 검증한다.

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

<!-- key: id=key.standard.artifact.graph.verification refs=key.topic.verification key.topic.artifact-graph -->
## Verification

Artifact Graph 기준은 다음 방법으로 검증한다.

1. Graph model ownership과 graph interpretation ownership을 구분할 수 있어야 한다.
2. Source document metadata 수정 owner와 code/config/schema/API/test anchor 수정 owner를 구분할 수
   있어야 한다.
3. Metadata admission policy만 보고 어떤 artifact에 metadata를 붙일지 판단할 수 있어야 한다.
4. `key.refs`와 typed relation의 책임 차이가 명확해야 한다.
5. Relation direction과 propagation 기본값을 보고 impact candidate 등급을 설명할 수 있어야 한다.
6. Locator와 stable ID가 분리되어야 한다.
7. Mechanical stale, semantic stale, metadata gap을 구분할 수 있어야 한다.
8. Impact candidate 등급이 자동 수정 또는 자동 acceptance로 해석되지 않아야 한다.
9. Generated graph index가 source of truth나 Linker write target으로 해석되지 않아야 한다.
10. Verification command:
   - `rg --files 00_docs`
   - `rg -n "key.capability|key.code|key.config|key.schema|key.api|key.test|keystone-linker" 00_docs/standards`
   - `rg -n "Artifact Graph ownership boundary|Metadata gap|Relation direction|Generated graph index" 00_docs/standards/artifacts/key-standard-artifact-graph.md`
