---
doc_type: standard
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
assignment(19)를 만들 수 있는 artifact context seed를 제공한다.

Linker는 Artifact Graph의 operational interpretation owner다. 이 ownership은 graph state,
relation evidence, impact candidate, stale candidate, metadata gap 판단 권위이며 source edit
authority를 포함하지 않는다.

<!-- key: id=key.standard.skill.linker.scope refs=key.role.linker key.topic.artifact-graph key.topic.impact-review -->
## 적용 범위

1. `keystone-linker`의 trigger와 non-trigger condition
2. Artifact Discovery, Impact Analysis, Stale/Gap Review, Worker Assignment Seed mode
3. Metadata, code anchor, repository evidence 기반 artifact 후보 탐색
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
   `STD-KEYSTONE-030`, `STD-KEYSTONE-044`
4. 관련 기준서: `../reader/key-standard-reader.md`, `../author/key-standard-author.md`,
   `../coordinator/key-standard-coordinator.md`
5. 관련 결정(6): `00_docs/works/key-decisions.md`의 `DEC-WORKS-009`
6. 충돌 처리: 이 기준서와 parent 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의
   결정(6)을 받는다. 결정 전까지는 parent 기준서를 임시 우선 기준으로 삼는다.

<!-- key: id=key.standard.skill.linker.skill-identity refs=key.role.linker key.topic.skill-contract -->
## Skill identity

1. Skill name: `keystone-linker`
2. Primary role: operational graph interpretation owner, artifact discovery, impact candidate
   generation, stale/gap candidate reporting, worker assignment seed preparation
3. Primary user: main agent, Coordinator, reviewer
4. Output authority: Linker output은 graph interpretation evidence와 handoff seed이며 원천
   문서(2), code, test, Main acceptance를 대체하지 않는다.

<!-- key: id=key.standard.skill.linker.trigger-condition refs=key.role.linker key.topic.impact-review key.topic.artifact-graph -->
## Trigger condition

`keystone-linker`는 다음 경우에 사용할 수 있다.

1. 기준서(3), 작업서(4), 결정(6) 변경이 code/config/schema/API/test artifact에 영향을 줄 수
   있다.
2. Code/config/schema/test 변경이 source document나 decision을 stale하게 만들 수 있다.
3. 새 기능을 작성하기 전에 기존 capability(16), API, reusable code, test를 찾아야 한다.
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
2. 설정된 document root(1)
3. 현재 work 또는 변경 의도
4. 관련 기준서(3), 작업서(4), 진행 기록(5), 결정(6) 기록
5. Known `key.id`, `key.refs`, capability(16), code, config, schema, API, test seed
6. 필요한 경우 changed documents, changed code files, changed tests, diff summary
7. 필요한 경우 Change Set(17) 또는 worker assignment(19) 준비 목적

Input이 부족하면 Linker는 추측해서 후보를 확정하지 않고 `risks_and_gaps` 또는
`NEEDS_CONTEXT` 성격의 recommended next action으로 보고한다.

<!-- key: id=key.standard.skill.linker.common-workflow refs=key.role.linker key.topic.artifact-graph key.topic.impact-review -->
## Common workflow

Linker는 mode와 무관하게 다음 순서를 따른다.

1. 설정된 document root(1)를 해석한다.
2. Artifact Graph 기준서를 읽어 metadata admission, typed relation, stale handling 기준을
   확인한다.
3. Input seed를 `key.id`, `key.refs`, capability(16), code, config, schema, API, test, path,
   symbol, keyword로 분리한다.
4. 키메타(9)와 코드 앵커(18)를 검색한다.
5. Repository evidence를 함께 확인한다.
6. Declared relation, observed relation, inferred relation을 구분한다.
7. Impact candidate를 `required`, `strong_candidate`, `weak_candidate`, `informational`,
   `excluded`로 등급화한다.
8. Reuse candidate와 test candidate를 분리해 보고한다.
9. Metadata gap과 stale candidate를 mechanical/semantic으로 분리한다.
10. Relation direction과 propagation 기본값을 Artifact Graph 기준서에 따라 해석한다.
11. 수정이 필요한 경우 직접 수정하지 않고 source surface별 handoff owner를 분류해 Author 또는
    Coordinator로 넘길 next action을 제안한다.

<!-- key: id=key.standard.skill.linker.metadata-parsing refs=key.role.linker key.topic.keystone-metadata key.topic.code-anchor key.topic.artifact-graph -->
## Metadata parsing rule

Linker는 초기 구현에서 다음 metadata surface를 우선 읽는다.

1. Markdown YAML frontmatter의 `key.id`와 `key.refs`
2. Markdown heading 바로 위 section-level comment

   ```markdown
   <!-- key: id=key.standard.example.section refs=key.topic.example key.doc.source -->
   ## Example section
   ```

3. Code, config, schema, API, test artifact 안의 `keystone:` line comment
4. Repository path, symbol, test name, config key 같은 locator evidence

Parsing과 normalization은 다음 기준을 따른다.

1. `key.id`와 code anchor `id`는 stable artifact identity로 보고 locator와 분리한다.
2. `key.refs`는 탐색 후보 edge로만 사용하고 required impact relation으로 확정하지 않는다.
3. Code anchor의 `provides`, `uses`, `implements`, `verifies`, `governed_by`, `documents`,
   `supersedes`, `derived_from`만 초기 typed relation으로 normalize한다.
4. Unknown relation, malformed metadata, duplicate ID, missing target은 mechanical stale candidate로
   보고한다.
5. Import, call, filename, keyword, heading overlap은 observed 또는 inferred evidence로 분리해
   보고한다.
6. Confidence는 evidence type을 기준으로 `declared`, `observed`, `inferred`로 우선 구분하고,
   candidate 등급은 Artifact Graph 기준서의 `required`, `strong_candidate`, `weak_candidate`,
   `informational`, `excluded`를 따른다.
7. Parser가 이해하지 못한 metadata는 조용히 버리지 않고 `metadata_gaps` 또는 `risks_and_gaps`에
   기록한다.

<!-- key: id=key.standard.skill.linker.mode-contract refs=key.role.linker key.contract.output key.topic.artifact-graph -->
## Mode contract

### Artifact Discovery Mode

현재 요청과 관련된 capability(16), code, config, schema, API, test artifact 후보를 찾는다.

Output focus:

1. Seed artifacts
2. Affected capabilities
3. Code/config/schema/API/test candidates
4. Reuse candidates
5. Evidence and confidence

### Impact Analysis Mode

변경된 source document, decision, code diff, test diff가 다른 artifact에 줄 영향 후보를 찾는다.

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
test candidates, stale risks를 정리한다.

Output focus:

1. Artifact context
2. Reuse candidates
3. Required tests
4. Metadata sync risks
5. Document sync candidates

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
        surface: source_document_frontmatter | section_comment | decision_record
        recommended_change:
        reason:
    coordinator:
      - artifact:
        surface: code_anchor | config_anchor | schema_anchor | api_anchor | test_anchor
        recommended_change:
        reason:
    main_or_clarify:
      - topic:
        reason:
  graph_owner_note:
    interpretation_owned_by: keystone-linker
    edit_authority: author_or_coordinator_only
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
```

`candidate_budget`은 후보가 많아 output을 줄였을 때만 사용한다. Linker는 `required` 후보를
자의적으로 숨기지 않으며, 생략이 필요하면 `omitted_summary`에 evidence type, keyword, path
범위, 생략 이유를 남긴다.

<!-- key: id=key.standard.skill.linker.handoff refs=key.role.linker key.role.author key.role.coordinator -->
## Handoff boundary

1. 문서 metadata 또는 source document 수정이 필요하면 `keystone-author`가 처리한다.
2. Code/config/schema/API/test metadata 수정이나 implementation이 필요하면 `keystone-coordinator`가 worker
   assignment(19)로 조율한다.
3. High-impact decision이 필요하면 `keystone-clarify`가 topic을 정리한다.
4. Current step과 work context가 부족하면 `keystone-reader`가 context brief를 만든다.
5. Linker report는 후보와 evidence이며 acceptance 또는 수정 권한이 아니다.
6. Linker는 handoff 대상과 recommended change를 graph 관점에서 제안할 수 있지만, Author 또는
   Coordinator의 source edit authority를 대체하지 않는다.

<!-- key: id=key.standard.skill.linker.stop-condition refs=key.role.linker key.boundary.read-only key.topic.impact-review -->
## Stop condition

Linker는 다음 상황에서 중단하거나 main/user 결정(6)을 요청한다.

1. 설정된 document root(1)를 확신 있게 해석할 수 없다.
2. Seed가 너무 모호해 관련 artifact 후보를 의미 있게 등급화할 수 없다.
3. 민감한 정보, local-only path, private data가 필요하다.
4. 후보를 판단하려면 code 실행, build, test execution, 외부 network access가 필요하지만 승인되지
   않았다.
5. Artifact graph mismatch가 current task 방향을 바꿀 수 있다.
6. Metadata stale/gap 후보가 source authority 또는 acceptance criteria 변경을 요구한다.
7. Linker가 직접 문서나 code를 수정해야만 진행할 수 있다.

<!-- key: id=key.standard.skill.linker.verification refs=key.role.linker key.topic.verification key.topic.artifact-graph -->
## Verification

Linker 기준은 다음 방법으로 검증한다.

1. Linker contract만 보고 trigger와 non-trigger를 구분할 수 있어야 한다.
2. 네 mode의 output focus가 서로 구분되어야 한다.
3. Linker가 원천 문서(2), code, config, schema, API, test를 직접 수정하지 않는다는 경계가 명확해야 한다.
4. Linker report가 Coordinator worker assignment의 artifact context seed로 사용될 수 있어야 한다.
5. Linker의 operational graph interpretation ownership이 source edit authority로 해석되지
   않아야 한다.
6. Mechanical stale, semantic stale, metadata gap을 구분할 수 있어야 한다.
7. Source surface별 handoff owner를 Author, Coordinator, Main/Clarify로 분리할 수 있어야 한다.
8. Candidate 발견이 자동 수정 또는 자동 acceptance로 해석되지 않아야 한다.
9. Verification command:
   - `rg --files 00_docs`
   - `rg -n "keystone-linker|linker_report|Artifact Discovery|Impact Analysis|Stale/Gap Review" 00_docs/standards`
   - `rg -n "source_surface_handoffs|graph_interpretation|operational graph interpretation" 00_docs/standards/skills/linker/key-standard-linker.md`
