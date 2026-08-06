---
doc_type: standard
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-06", accepted_by: main}
key:
  id: key.standard.skill.linker
  refs:
    - key.role.linker
    - key.topic.artifact-graph
    - key.topic.impact-review
    - key.topic.keystone-metadata
    - key.topic.code-anchor
    - key.output.worker-assignment-seed
---

# keystone-linker 기준서

<!-- key: id=key.standard.skill.linker.purpose refs=key.role.linker key.topic.artifact-graph key.topic.impact-review -->
## 목적

이 기준서는 `keystone-linker`의 상세 계약을 정의한다. `keystone-linker`는 원천 문서(2),
키메타(9), 코드 앵커(18), repository evidence를 read-only로 조사해 문서, capability(16),
code, config, schema, API, test artifact의 연결과 impact/stale/gap 후보를 찾고, Coordinator가 worker
assignment(19)를 만들 수 있는 artifact context seed를 제공하며 graph-relevant change에는 exact
canonical mutation과 synchronization transaction proposal을 만든다.

Linker는 Artifact Graph의 유일한 canonical mutation decision owner다. 이 ownership은 graph
state, relation evidence, 후보 판단과 artifact ID, capability node, relation, provenance, locator,
lifecycle, replacement mutation의 결정을 포함하지만 source edit authority는 전혀 포함하지 않는다.

<!-- key: id=key.standard.skill.linker.scope refs=key.role.linker key.topic.artifact-graph key.topic.impact-review -->
## 적용 범위

1. `keystone-linker`의 trigger와 non-trigger condition
2. Artifact Discovery, Impact Analysis, Stale/Gap Review, Worker Assignment Seed mode
3. Metadata, code/config/schema/API/test anchor, repository evidence 기반 artifact 후보 탐색
4. Impact candidate 등급화
5. Metadata gap과 stale candidate 보고
6. Reuse candidate와 test candidate 보고
7. Coordinator worker assignment 준비를 위한 output contract
8. Graph reconstruction, relation normalization, relation direction, propagation 판단
9. Source surface별 handoff owner 분류

<!-- key: id=key.standard.skill.linker.out-of-scope refs=key.role.linker key.boundary.read-only -->
## 적용하지 않는 범위

1. 원천 문서(2), code, config, schema, API, test, generated file 수정
2. 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 기록 작성
3. High-impact decision 질문 수집 또는 수락
4. Worker assignment를 실제 worker에게 배정
5. Subagent report acceptance 또는 Main acceptance 결정
6. Metadata 후보를 자동으로 source에 반영하기
7. 단순 파일명 검색만으로 충분한 좁은 작업을 불필요하게 artifact graph workflow로 키우기

<!-- key: id=key.standard.skill.linker.standard-relations refs=key.role.linker key.doc.standard key.topic.artifact-graph -->
## 기준 관계

1. Parent 기준서: `../../01_key-project-standard.md`
2. Artifact Graph 기준서: `../../artifacts/key-standard-artifact-graph.md`
3. 상위 규칙: `STD-KEYSTONE-001`, `STD-KEYSTONE-015`, `STD-KEYSTONE-017`,
   `STD-KEYSTONE-018`, `STD-KEYSTONE-023`, `STD-KEYSTONE-025`, `STD-KEYSTONE-027`,
   `STD-KEYSTONE-030`, `STD-KEYSTONE-044`, `STD-KEYSTONE-045`, `STD-KEYSTONE-046`
4. 관련 기준서: `../reader/key-standard-reader.md`, `../author/key-standard-author.md`,
   `../coordinator/key-standard-coordinator.md`
5. 관련 결정(6): `00_docs/works/key-decisions.md`의 `DEC-WORKS-009`, `DEC-WORKS-010`,
   `DEC-WORKS-013`, `DEC-WORKS-024`
6. 충돌 처리: 이 기준서와 parent 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의
   결정(6)을 받는다. 결정 전까지는 parent 기준서를 임시 우선 기준으로 삼는다.

<!-- key: id=key.standard.skill.linker.skill-identity refs=key.role.linker key.topic.skill-contract -->
## Skill identity

1. Skill name: `keystone-linker`
2. Primary role: operational graph interpretation owner, artifact discovery, impact candidate
   generation, stale/gap candidate reporting, worker assignment seed preparation
3. Primary user: main agent, Coordinator, reviewer
4. Output authority: Linker output은 graph interpretation evidence와 handoff seed이며 원천
   문서(2), output artifact, Main acceptance를 대체하지 않는다.

<!-- key: id=key.standard.skill.linker.runtime-authority refs=key.role.linker key.topic.runtime-independence key.topic.artifact-graph -->
## 런타임 권위와 호출 경계

이 문서는 Keystone 저장소에서 Linker를 개발·검수하기 위한 원천 명세다. 배포된 Linker의
실행 계약과 graph 해석 규칙은 설치된 skill package 안에서 완결되어야 하며, 소비 프로젝트의
`standards/skills/linker/**`를 required input으로 요구하지 않는다.

Linker는 source surface에 대해 read-only이므로 Main이 필요하다고 판단하면 별도 사용자 허락 없이 사용할 수 있다.
Artifact Graph evidence가 적거나 없으면 오류나 profile 부족으로 보지 않고 확인 가능한 관계와
gap을 fail-soft로 보고한다.

<!-- key: id=key.standard.skill.linker.trigger-condition refs=key.role.linker key.topic.impact-review key.topic.artifact-graph -->
## Trigger condition

`keystone-linker`는 다음 경우에 사용할 수 있다.

1. 기준서(3), 작업서(4), 결정(6) 변경이 산출물(output artifact)에 영향을 줄 수 있다.
2. Output artifact 변경이 source document, decision, work order를 stale하게 만들 수 있다.
3. 새 기능이나 산출물을 작성하기 전에 기존 capability(16), API, reusable code, test, skill
   source, generated artifact 후보를 찾아야 한다.
4. Metadata가 오래되었거나 누락되었는지 확인해야 한다.
5. Coordinator가 worker assignment(19)를 만들기 전에 affected artifact 후보가 필요하다.
6. Reviewer가 기존 capability 재사용 여부와 metadata stale 여부를 검토해야 한다.
7. Change Set(17)의 impact seed, required candidates, optional candidates, excluded scope를
   정리해야 한다.

<!-- key: id=key.standard.skill.linker.non-trigger-condition refs=key.role.linker key.boundary.read-only -->
## Non-trigger condition

`keystone-linker`는 다음 경우에 사용하지 않는다.

1. 원천 문서(2)를 직접 작성하거나 수정해야 한다.
2. Code implementation을 직접 수행해야 한다.
3. High-impact decision을 질문으로 수집해야 한다.
4. Worker assignment를 실제 worker에게 배정해야 한다.
5. Metadata 없이 단순 파일명 검색만으로 충분한 좁은 작업이다.
6. 민감한 정보, local-only path, private data가 필요하지만 정책이나 승인 범위가 불명확하다.

<!-- key: id=key.standard.skill.linker.required-input refs=key.role.linker key.topic.artifact-graph -->
## Required input

Linker는 다음 input을 사용할 수 있어야 한다.

1. 사용자 요청 또는 main의 current task
2. 존재하는 경우 설정된 document root(1)
3. 현재 work 또는 변경 의도
4. 존재하는 관련 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 기록
5. Known `key.id`, `key.refs`, capability(16), output artifact, code, config, schema, API, test seed
6. 필요한 경우 changed documents, changed output artifact files, changed code/config/schema/API/test
   files, diff summary
7. 필요한 경우 Change Set(17) 또는 worker assignment(19) 준비 목적

Input이 부족하면 Linker는 추측해서 후보를 확정하지 않고 `risks_and_gaps` 또는
`NEEDS_CONTEXT` 성격의 recommended next action으로 보고한다.

<!-- key: id=key.standard.skill.linker.common-workflow refs=key.role.linker key.topic.artifact-graph key.topic.impact-review -->
## Common workflow

Linker는 mode와 무관하게 다음 순서를 따른다.

1. 설정된 document root(1)와 존재하는 graph evidence를 해석한다.
2. 설치된 Linker contract의 graph 규칙과 존재하는 프로젝트 Artifact Graph policy를 사용해
   metadata admission, typed relation, stale handling 기준을 확인한다.
3. Input seed를 `key.id`, `key.refs`, source document, decision, work order, output artifact,
   capability(16), code, config, schema, API, test, path, symbol, keyword로 분리한다.
4. 키메타(9)와 코드 앵커(18)를 검색한다.
5. Repository evidence를 함께 확인한다.
6. Declared relation, observed relation, inferred relation을 구분한다.
7. Impact candidate를 `required`, `strong_candidate`, `weak_candidate`, `informational`,
   `excluded`로 등급화한다.
8. Reuse candidate와 test candidate를 분리해 보고한다.
9. Metadata gap과 stale candidate를 mechanical/semantic으로 분리한다.
10. Relation direction과 propagation 기본값을 Artifact Graph 기준서에 따라 해석한다.
11. Reuse, extend, extract shared module, create new 선택에 따라 scope, acceptance criteria,
    API/schema contract, shared architecture, document consistency, verification이 달라지면
    `keystone-clarify`의 modularization decision topic을 recommended next action으로 제안한다.
12. Evidence가 부족해 reuse 또는 modularization 방향을 정할 수 없으면 `investigate_first`
    성격의 추가 Linker review 또는 Coordinator investigation을 제안한다.
13. 수정이 필요한 경우 직접 수정하지 않고 source/output surface별 handoff owner를 분류해 Author,
    Main direct, 또는 Coordinator로 넘길 next action을 제안한다.
14. Graph-relevant delta이면 evidence admission을 적용해 canonical mutation을 결정하고 exact
    per-surface patch, baseline digest, attestation 요구를 가진 synchronization proposal을 만든다.
15. Surface owner 결과를 받은 뒤 source를 다시 읽어 graph를 재구성하고 validator evidence와
    함께 transaction state를 판정한다. Linker는 어느 단계에서도 patch를 직접 적용하지 않는다.

<!-- key: id=key.standard.skill.linker.metadata-parsing refs=key.role.linker key.topic.keystone-metadata key.topic.code-anchor key.topic.artifact-graph -->
## Metadata parsing rule

Linker는 초기 구현에서 다음 metadata surface를 우선 읽는다.

1. Markdown YAML frontmatter의 `key.id`와 `key.refs`
2. Markdown heading 바로 위 section-level comment

   ```markdown
   <!-- key: id=key.standard.example.section refs=key.topic.example key.doc.source -->
   ## Example section
   ```

3. Markdown heading·list item 바로 위의 item-level comment와 table row 첫 번째 cell 안의 compact
   item comment

   ```markdown
   <!-- key: id=key.rule.example.independent-rule supersedes=key.rule.example.old-rule -->
   - Independently replaceable rule

   | <!-- key: id=key.acceptance.example.contract requires_verification_of=key.claim.example.contract --> `AC-01` | expected result |
   ```

4. Code, config, schema, API, test artifact 안의 `keystone:` line comment
5. Repository path, heading, visible item ID, symbol, test name, config key 같은 locator evidence

Parsing과 normalization은 다음 기준을 따른다.

1. `key.id`와 code anchor `id`는 stable artifact identity로 보고 locator와 분리한다.
2. `key.refs`는 탐색 후보 edge로만 사용하고 required impact relation으로 확정하지 않는다.
3. Document item은 부모 document와 section의 `governed_by`, source authority와 lifecycle을
   상속할 수 있지만 `id`와 `supersedes`는 상속하지 않는다. Effective `governed_by`는 부모
   effective set과 child declared set의 ordered union이며 inherited target을 child의 typed
   relation으로 복제하지 않는다.
4. Decision의 일부만 대체되면 decision document 전체가 아니라 declared `key.claim.*`
   relation을 impact seed로 사용한다. Claim metadata가 없으면 부분 대체를 확정하지 않고
   metadata gap으로 보고한다.
5. Code/config/schema/API/test anchor와 document item의 `provides`, `uses`, `implements`, `verifies`,
   `governed_by`, `documents`, `supersedes`, `derived_from`, `depends_on`만 초기 typed relation으로
   normalize한다.
   단, API anchor의 `provides=key.capability.*`는 API interpretation rule에 따라 예외 근거가
   있을 때만 provider relation으로 확정한다.
6. Output artifact의 `authority.produced_from` 또는 동등한 declared provenance를 읽으면
   target source document·decision·work order에서 output artifact로 향하는 `produces` edge를
   generated/inferred evidence로 파생한다. `produced_from`을 typed relation으로 normalize하거나
   source surface에 역방향 relation을 중복 기록하지 않는다.
7. `produced_from` target이 없거나 유효한 source로 해석되지 않으면 unresolved provenance
   또는 metadata gap으로 보고하고 `derived_from`으로 추정하지 않는다.
8. `legacy_terms`는 typed relation으로 만들지 않는다. Replacement 또는 removed item의 검색
   seed로 사용하고, active/pending 권위 item의 일치 항목과 archived/rejected/history evidence를
   구분해 semantic stale, informational 또는 excluded candidate로 분류한다.
9. Progress나 verification evidence가 legacy term 제거를 완료했다고 선언했는데 active source
   item에 같은 표현이 남아 있으면 semantic stale candidate로 보고한다.
10. Unknown relation, malformed metadata, duplicate ID, missing target은 mechanical stale candidate로
   보고한다.
11. Import, call, filename, keyword, heading overlap은 observed 또는 inferred evidence로 분리해
   보고한다.
12. `revised_by`는 revision-history evidence로 탐색할 수 있지만 typed relation으로
    normalize하지 않는다. 이 field만으로 authority, impact propagation, `supersedes`,
    `produces`, `governed_by`를 파생하지 않는다.
13. `revised_by` evidence가 공식 의미를 필요로 하면 적합한 typed relation, decision,
    Change Set 또는 revision record 후보로 handoff한다. Target 누락·의미 모호성은
    informational 또는 unknown revision evidence로 보고하고 relation error로 단정하지 않는다.
14. Confidence는 evidence type을 기준으로 `declared`, `observed`, `inferred`로 우선 구분하고,
   candidate 등급은 Artifact Graph 기준서의 `required`, `strong_candidate`, `weak_candidate`,
   `informational`, `excluded`를 따른다.
15. Parser가 이해하지 못한 metadata는 조용히 버리지 않고 `metadata_gaps` 또는 `risks_and_gaps`에
   기록한다.

<!-- key: id=key.standard.skill.linker.api-interpretation refs=key.role.linker key.topic.api key.topic.artifact-graph key.work.decisions.dec-works-010 -->
## API interpretation rule

Linker는 API artifact를 기본적으로 contract artifact로 해석한다.

1. API seed나 API diff가 들어오면 먼저 `implements` relation과 repository evidence를 통해
   implementing code/config/schema artifact 후보를 찾는다.
2. Implementing artifact가 `provides`하는 capability를 affected capability 후보로 보고한다.
3. API contract 변경은 implementing artifact, verifying test, source document, related
   capability를 `required` 또는 `strong_candidate` 후보로 올릴 수 있다.
4. API artifact 자체를 capability provider로 판단하지 않는다.
5. API anchor에 `provides=key.capability.*`가 있거나 API가 provider처럼 보이면 accepted decision
   또는 명시된 예외 relation policy를 확인한다.
6. 예외 근거가 없으면 API provider relation으로 확정하지 않고 `risks_and_gaps` 또는
   `recommended_next_action`으로 보고한다.

<!-- key: id=key.standard.skill.linker.mode-contract refs=key.role.linker key.contract.output key.topic.artifact-graph -->
## Mode contract

### Artifact Discovery Mode

현재 요청과 관련된 capability(16)와 output artifact 후보를 찾는다.

Output focus:

1. Seed artifacts
2. Source document, decision, work order가 만드는 output artifact 후보
3. Affected capabilities
4. Code/config/schema/API/test/skill/generated surface별 후보
5. Reuse candidates
6. Evidence and confidence

### Impact Analysis Mode

변경된 source document, decision, work order, output artifact diff가 다른 artifact에 줄 영향 후보를 찾는다.

Output focus:

1. Required candidates
2. Strong candidates
3. Weak candidates
4. Excluded candidates
5. Recommended next skill

### Stale/Gap Review Mode

Metadata locator, relation, semantic mismatch 후보를 찾는다.

Output focus:

1. Mechanical stale candidates
2. Semantic stale candidates
3. Metadata gaps
4. Verification or reviewer recommendation

### Worker Assignment Seed Mode

Coordinator가 worker assignment(19)를 만들 수 있도록 artifact candidates, reuse candidates,
test candidates, stale/gap risks, document sync candidates, metadata sync risks를 정리한다.

Output focus:

1. Artifact context
2. Reuse candidates
3. Required tests
4. Metadata sync risks
5. Document sync candidates

### Graph Synchronization Mode

Graph-relevant `document_delta | artifact_delta`가 둘 이상의 source surface에 coordinated patch를
요구할 때 canonical mutation을 결정하고 source owner가 attest/apply할 exact patch transaction을
제안한다. 단일 source surface delta는 owner의 direct refresh와 validation으로 처리한다.
Transaction trigger는 current scope, Coordinator permission, worker assignment 또는 acceptance를
자동 생성하지 않는다.

1. Delta locator와 각 source의 UTF-8 raw-byte SHA-256 baseline을 수집한다.
2. `declared` evidence는 admissible로, `observed` evidence는 surface-owner `confirm` 조건으로
   수용하며 `inferred` evidence는 mutation에서 제외한다.
3. Owner/ref-first로 node와 direct lookup을 정규화한다. Multi-hop, semantic role, dependency,
   verification evidence 또는 reuse 분석이 필요한 relation만 typed graph projection에 추가하며
   capability를 모든 artifact의 필수 중심 node로 만들지 않는다.
4. Artifact Graph 기준서의 canonical node/relation/provenance/locator/lifecycle schema와 relation
   direction을 사용한다.
5. Markdown metadata, safe language anchor 또는 `<source>.keystone.json` companion 중 해당
   surface의 canonical representation을 골라 exact patch를 만든다. 중앙 registry를 만들지 않는다.
6. Attestation이 모두 `confirm`이고 baseline이 유효할 때만 apply handoff를 ready로 만든다.
7. Apply 후 source를 cache 없이 재구성하고 mutation과 일치하는지 비교한다. Derived cache는
   선택적·비권위이며 source mismatch 시 폐기한다.
8. Orphan relation, removed target을 향한 active relation, unresolved locator와 duplicate ID를
   mechanical failure로 보고한다. Retired ID의 history/provenance reference는 허용한다.

Output focus:

1. Input deltas and graph relevance
2. Canonical mutations and evidence admission
3. Exact surface patches and baseline digests
4. Required surface-owner attestations
5. Transaction state and resumable apply results
6. Reconstruction and mechanical validation evidence
7. Current transaction completeness and separate project coverage debt

<!-- key: id=key.standard.skill.linker.output-contract refs=key.role.linker key.contract.output key.topic.impact-review -->
## Output contract

Linker는 다음 fields를 우선 사용해 보고한다.

```yaml
linker_report:
  request_summary:
  mode:
  seed_artifacts:
    - key_id:
      locator:
      reason:
  affected_capabilities:
    required:
    strong_candidates:
    weak_candidates:
  output_artifact_candidates:
    required:
    strong_candidates:
    weak_candidates:
    informational:
  code_candidates:
    required:
    strong_candidates:
    weak_candidates:
  api_candidates:
    required:
    strong_candidates:
    weak_candidates:
  config_candidates:
    required:
    strong_candidates:
    weak_candidates:
  schema_candidates:
    required:
    strong_candidates:
    weak_candidates:
  test_candidates:
    required:
    strong_candidates:
    weak_candidates:
  document_candidates:
    required:
    strong_candidates:
    weak_candidates:
  reuse_candidates:
    - key_id:
      locator:
      evidence:
      reuse_decision_hint:
      modularization_decision_needed: true | false
      modularization_reason:
  metadata_gaps:
    - artifact:
      expected_metadata:
      reason:
  stale_candidates:
    mechanical:
    semantic:
  excluded_candidates:
    - artifact:
      reason:
  relations:
    declared:
    observed:
    inferred:
  graph_interpretation:
    status: ok | partial | blocked
    basis:
      - artifact_graph_standard
      - project_standard
    evidence_mode:
      declared:
      observed:
      inferred:
  source_surface_handoffs:
    author:
      - artifact:
        surface: source_document_frontmatter | section_comment | decision_record | api_contract_source_section
        recommended_change:
        reason:
    coordinator:
      - artifact:
        surface: code_anchor | config_anchor | schema_anchor | api_anchor | test_anchor
        recommended_change:
        reason:
    main_direct_or_coordinator:
      - artifact:
        surface: output_artifact | skill_source | generated_file | repository_source
        recommended_change:
        reason:
    main_or_clarify:
      - topic:
        reason:
        suggested_decision_options:
          - reuse_existing
          - extend_existing
          - extract_shared_module
          - create_new
          - investigate_first
  graph_owner_note:
    canonical_mutation_decided_by: keystone-linker
    edit_authority: author_main_direct_or_coordinator_only
  candidate_budget:
    applied: true | false
    truncated:
      required:
      strong_candidates:
      weak_candidates:
      informational:
    omitted_summary:
  risks_and_gaps:
  recommended_next_action:
    skill:
    reason:
  graph_synchronization:
    schema_version: 1
    transaction_id:
    graph_relevance:
      relevant: true | false
      disposition: required | not_applicable | deferred
      reason:
    input_deltas:
      - kind: document_delta | artifact_delta
        source_surface:
        baseline_digest: sha256:<64-lowercase-hex> | absent
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
        baseline_digest: sha256:<64-lowercase-hex> | absent
        exact_patch:
        required: true | false
    attestations:
      - patch_id:
        decision: confirm | reject | needs_revision
        evidence:
    apply_results:
      - patch_id:
        result: applied | failed | stale_baseline
        resulting_digest:
    transaction_state: proposed | awaiting_attestation | ready_to_apply | applying | partially_applied | verified | conflicted | failed
    reconstruction:
    mechanical_validation:
    coverage_debt: []
```

`candidate_budget`은 후보가 많아 output을 줄였을 때만 사용한다. Linker는 `required` 후보를
자의적으로 숨기지 않으며, 생략이 필요하면 `omitted_summary`에 evidence type, keyword, path
범위, 생략 이유를 남긴다.

<!-- key: id=key.standard.skill.linker.user-response refs=key.role.linker key.contract.output key.topic.skill-contract -->
## 기본 사용자 응답

Linker는 `linker_report`를 agent-facing structured payload로 유지한다. 기본 사용자 응답은 다음
항목만 짧게 보여준다.

1. 요청 요약과 graph interpretation status
2. required 후보와 strong candidate의 대표 항목
3. 주요 stale/gap/reuse risk
4. source surface별 handoff owner 요약: Author, Coordinator, Main/Clarify
5. 다음 권장 행동과 주요 근거 문서 또는 artifact

후보가 많으면 required 후보는 숨기지 않고, strong/weak/informational 후보는 count와 대표
근거로 압축한다. Full `linker_report`는 사용자가 요청하거나 Coordinator/Author handoff,
audit/debug, verification evidence에 필요할 때만 노출한다. Optional `keystone-viewer`는 Linker
report를 표현할 수 있지만 candidate 등급, risk, handoff owner, recommended next action을
바꾸지 않는다.

사용자-facing 응답을 보내기 전에는 `STD-KEYSTONE-045`의 Payload Disclosure Gate를 적용한다.
Full payload 요청, handoff, audit/debug, verification evidence 필요성이 없으면 `*_output`,
`*_result`, `*_report`, `worker_assignment`, `keystone_routing_decision` 원문 block을 기본
응답에 노출하지 않는다. 기본 응답은 payload 의미를 graph status, 후보 count와 대표 근거,
stale/gap risk, handoff owner, 다음 행동, 주요 출처로 압축한다.

<!-- key: id=key.standard.skill.linker.handoff refs=key.role.linker key.role.author key.role.coordinator -->
## Handoff boundary

1. 문서 metadata 또는 source document 수정이 필요하면 `keystone-author`가 처리한다.
2. Repository source output artifact metadata 수정이나 implementation이 필요하면 작은 명확한
   범위는 Main direct로 처리할 수 있고, 위임이 필요하면 사용자 허락을 받은
   `keystone-coordinator`가 조율한다.
3. High-impact decision이 필요하면 `keystone-clarify`가 topic을 정리한다.
4. Active/실행 가능 Step과 work context가 부족하면 `keystone-reader`가 context brief를 만든다.
5. Linker report는 후보와 evidence이며 acceptance 또는 수정 권한이 아니다.
6. Linker는 handoff 대상과 recommended change를 graph 관점에서 제안할 수 있지만, Author 또는
   Coordinator의 source edit authority를 대체하지 않는다.
7. Reuse 또는 modularization 선택이 scope, shared architecture, API/schema/test, document
   consistency, acceptance criteria, verification에 영향을 주면 Linker는 `keystone-clarify`
   modularization decision topic을 handoff로 제안한다.
8. Skill source, code, config, schema, API, test는 모두 output artifact의 surface로 보고한다.
   수정은 Main direct 또는 허락된 Coordinator로 넘긴다.
9. 복수 surface나 권한 경계가 있을 때만 명시적인 routing context를 남긴다.

<!-- key: id=key.standard.skill.linker.stop-condition refs=key.role.linker key.boundary.read-only key.topic.impact-review -->
## Stop condition

Linker는 다음 상황에서 중단하거나 main/user 결정(6)을 요청한다.

1. 복수 document root가 충돌해 read scope를 안전하게 정할 수 없다.
2. Seed가 너무 모호해 관련 artifact 후보를 의미 있게 등급화할 수 없다.
3. 민감한 정보, local-only path, private data가 필요하다.
4. 후보를 판단하려면 code 실행, build, test execution, 외부 network access가 필요하지만 승인되지
   않았다.
5. Artifact graph mismatch가 current task 방향을 바꿀 수 있다.
6. Metadata stale/gap 후보가 source authority 또는 acceptance criteria 변경을 요구한다.
7. Linker가 직접 문서나 code를 수정해야만 진행할 수 있다.

Graph metadata나 relation의 단순 부재는 stop condition이 아니다.

<!-- key: id=key.standard.skill.linker.verification refs=key.role.linker key.topic.verification key.topic.artifact-graph -->
<!-- key: id=key.standard.skill.linker.dependency-interpretation refs=key.role.linker key.topic.artifact-graph key.topic.work-sequence -->
## Dependency interpretation

1. Linker는 `depends_on`을 source -> target semantic relation으로 정규화하고 `work_gates`를
   relation과 분리된 execution evidence로 해석한다.
2. Relation target, gate scope/condition, legacy conflict, duplicate/self/invalid step을 검증하고
   cycle은 expanded event graph evidence가 있을 때만 확정한다.
3. Dependency 판정을 work status mutation, automatic assignment/cancellation/acceptance로 바꾸지 않는다.
4. Graph evidence가 부족하면 `unknown`/`unresolvable`과 필요한 Author/Main handoff를 보고한다.

## Verification

Linker 기준은 다음 방법으로 검증한다.

1. Linker contract만 보고 trigger와 non-trigger를 구분할 수 있어야 한다.
2. 네 mode의 output focus가 서로 구분되어야 한다.
3. Linker가 원천 문서(2)나 output artifact를 직접 수정하지 않는다는 경계가 명확해야 한다.
4. Linker report가 Coordinator worker assignment의 artifact context seed로 사용될 수 있어야 한다.
5. Linker의 canonical graph mutation decision ownership이 source edit authority로 해석되지
   않아야 한다.
6. Mechanical stale, semantic stale, metadata gap을 구분할 수 있어야 한다.
7. Source/output surface별 handoff owner를 Author, Main direct, Coordinator, Main/Clarify로 분리할 수 있어야 한다.
8. Candidate 발견이 자동 수정 또는 자동 acceptance로 해석되지 않아야 한다.
9. 기본 사용자 응답은 required 후보, 주요 risk, handoff owner, next action을 요약하되 required
   후보를 조용히 생략하지 않아야 한다.
10. Skill source 후보는 output artifact surface의 한 종류일 뿐이며, graph model의 핵심은
    source document, decision, work order가 만드는 산출물과의 relation임을 확인할 수 있어야 한다.
11. Graph evidence가 없거나 적어도 fail-soft report를 제공하고 소비 프로젝트 로컬 Linker
    기준서를 요구하지 않아야 한다.
12. Verification command:
   - `rg --files 00_docs`
   - `rg -n "keystone-linker|linker_report|Artifact Discovery|Impact Analysis|Stale/Gap Review" 00_docs/standards`
   - `rg -n "source_surface_handoffs|graph_interpretation|operational graph interpretation" 00_docs/standards/skills/linker/key-standard-linker.md`

<!-- key: id=key.standard.skill.linker.reference-index-readiness refs=key.role.linker key.topic.artifact-graph key.topic.work-recovery key.boundary.read-only -->
## Owner/ref index와 context readiness mode

Owner/ref Index Readiness는 Linker의 permissionless internal mode다. User-facing command로 노출하지
않고 Reader나 다른 Keystone skill이 필요한 context scope를 전달해 호출한다.

1. 의미 있는 source artifact의 declared owner ID와 refs를 수집하고 duplicate owner, unresolved ref,
   locator gap을 진단한다. 모든 artifact에 typed relation이나 capability node를 요구하지 않는다.
2. Owner/ref reverse index는 repository 밖 disposable cache에 single writer로 생성한다. Source
   annotation, standard와 companion metadata가 source of truth이고 cache는 acceptance/transaction
   evidence가 아니다.
3. Freshness는 worktree identity, discovery scope 이름, sorted path set과 각 source raw-byte SHA-256
   digest로 결정한다. Git HEAD, mtime과 timestamp만으로 fresh를 선언하지 않는다.
4. Docs scope는 configured document root만, repository scope는 explicit include/exclude와 supported
   source/companion discovery를 사용한다. Repository scan은 artifact context가 필요할 때 lazy하다.
5. Cache lock/write/corruption 실패는 fail-soft diagnostic으로 남기고 raw source 탐색 결과를
   반환한다. Cache failure만으로 current work나 Reader orientation을 block하지 않는다.
6. Typed graph projection은 multi-hop/semantic-role/dependency/verification/reuse query가 필요할
   때 owner/ref index 위에 파생한다. Source에 relation이 없으면 broad similarity로 canonical edge를
   만들지 않는다.
7. Reader -> Linker와 Linker -> Reader 호출은 serialized recursion guard를 전달하며 initiating
   lane에 재진입하지 않는다.

<!-- key: id=key.standard.skill.linker.transaction-classification refs=key.role.linker key.topic.artifact-graph key.topic.change-set -->
## Direct refresh와 transaction 분류

1. 단일 source surface의 owner/ref 또는 metadata 변경은 surface owner가 직접 적용하고 Linker는
   index refresh와 validation만 수행한다.
2. 둘 이상의 source surface가 함께 바뀌어야 canonical meaning이 닫히는 경우에만 graph
   synchronization transaction을 제안한다.
3. Conflict reason은 `stale_baseline | reject | needs_revision | reconstruction_mismatch |
   transient_application_failure`로 보존한다. 모든 retry는 새 transaction ID와 attempt history를
   가진다.
4. Stale baseline retry는 하나 이상의 changed baseline이 필요하다. Reject/needs_revision은 같은
   baseline을 허용하되 mutation 또는 exact patch가 달라야 한다. Reconstruction mismatch는 baseline,
   mutation 또는 patch 중 하나가 달라야 한다. Verified transient failure는 동일 patch retry를 허용한다.
5. Transaction scope validation은 current work omission을 gate한다. Repository scope validation은
   전체 coverage debt를 보고하되 current transaction 밖 gap만으로 current work를 block하지 않는다.
