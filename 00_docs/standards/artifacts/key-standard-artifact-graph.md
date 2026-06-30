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
6. API artifact
7. Test artifact
8. Worker assignment와 worker report에서 참조되는 artifact

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
4. 충돌 처리: 이 기준서와 parent 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의
   결정(6)을 받는다. 결정 전까지는 parent 기준서를 임시 우선 기준으로 삼는다.

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

Artifact ID는 path나 line number가 아니라 의미와 책임을 기준으로 정한다.

<!-- key: id=key.standard.artifact.graph.typed-relation refs=key.topic.artifact-graph key.topic.code-anchor -->
## Typed relation

초기 typed relation은 다음을 사용한다.

1. `provides`: code artifact가 capability를 제공한다.
2. `uses`: artifact가 다른 capability, API, code artifact를 사용한다.
3. `implements`: code artifact가 API 또는 결정된 contract를 구현한다.
4. `verifies`: test artifact가 capability, API, decision, code behavior를 검증한다.
5. `governed_by`: artifact가 기준서(3)나 결정(6)의 규칙을 따른다.
6. `documents`: source document가 artifact를 설명한다.
7. `supersedes`: 새 artifact가 기존 artifact를 대체한다.
8. `derived_from`: artifact가 다른 artifact나 source에서 파생되었다.

`key.refs`는 넓은 관련성이나 탐색 후보를 표현한다. Impact propagation과 execution boundary는
가능한 한 typed relation과 repository evidence를 기준으로 판단한다.

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

<!-- key: id=key.standard.artifact.graph.impact-candidate refs=key.topic.impact-review key.topic.artifact-graph -->
## Impact candidate

Impact candidate는 다음 등급으로 보고한다.

1. `required`: 직접 typed relation, 명시된 acceptance criteria, 직접 code/config/schema/test
   dependency로
   반드시 검토해야 한다.
2. `strong_candidate`: 같은 capability, API, decision, 주요 domain keyword를 공유해 검토
   우선순위가 높다.
3. `weak_candidate`: 넓은 topic overlap이나 간접 evidence가 있다.
4. `informational`: 참고 evidence로만 남긴다.
5. `excluded`: 현재 scope에서 제외한다는 이유가 있다.

Candidate 발견은 수정 허가가 아니다. 실제 변경은 승인 범위, source authority, artifact
authority, Coordinator workflow를 따른다.

<!-- key: id=key.standard.artifact.graph.verification refs=key.topic.verification key.topic.artifact-graph -->
## Verification

Artifact Graph 기준은 다음 방법으로 검증한다.

1. Metadata admission policy만 보고 어떤 artifact에 metadata를 붙일지 판단할 수 있어야 한다.
2. `key.refs`와 typed relation의 책임 차이가 명확해야 한다.
3. Locator와 stable ID가 분리되어야 한다.
4. Mechanical stale과 semantic stale을 구분할 수 있어야 한다.
5. Impact candidate 등급이 자동 수정 또는 자동 acceptance로 해석되지 않아야 한다.
6. Verification command:
   - `rg --files 00_docs`
   - `rg -n "key.capability|key.code|key.api|key.test|keystone-linker" 00_docs/standards`
