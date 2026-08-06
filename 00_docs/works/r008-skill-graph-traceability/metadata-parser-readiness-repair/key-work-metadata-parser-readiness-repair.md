---
doc_type: work_order
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-06", accepted_by: main}
work_status: complete
key:
  id: key.work.metadata-parser-readiness-repair.order
  refs:
    - key.doc.work
    - key.topic.keystone-metadata
    - key.topic.artifact-graph
    - key.topic.work-recovery
    - key.topic.verification
    - key.topic.change-set
---

# Metadata Parser and Readiness Repair 작업서 및 Change Set

<!-- key: id=key.work.metadata-parser-readiness-repair.order.goal refs=key.section.goal key.topic.keystone-metadata -->
## Goal

Keystone compact metadata의 공백 구분 다중 값을 손실 없이 해석하고, owner/ref readiness가
기준서의 namespace·locator 정책과 같은 의미를 보고하도록 정합화한다.

<!-- key: id=key.work.metadata-parser-readiness-repair.order.scope refs=key.section.scope key.topic.artifact-graph -->
## Scope

Include:

- `skills/keystone-linker/scripts/graph_runtime/metadata.py` compact metadata parsing
- `skills/keystone-linker/scripts/graph_runtime/scanner.py` owner/ref readiness diagnostic
- 관련 metadata, reference-index, context-readiness regression test
- 실제 여섯 `skills/keystone-*/SKILL.md`의 provenance와 governance snapshot 검증
- `key.doc.*`, `key.contract.*`, `key.section.*`, `key.step.*`, `key.output.*`,
  `key.artifact.*` ref를 owner-required ID와 controlled taxonomy 중 어디에 둘지 기존 수락 기준으로
  분류
- `skill_source` file-level artifact의 machine locator 판정 정합화
- Docs/repository scope freshness, recursion guard와 fail-soft cache behavior 회귀 확인
- Cache schema v2/v3에서 v4로의 disposable migration, truncated discovery path-set freshness와
  locator field 보존
- 실제 `00_docs` 전체를 fresh external cache로 scan한 readiness acceptance evidence

Exclude:

- 기존 corpus의 compact comment를 comma 형식으로 일괄 변환하는 migration
- 모든 dangling ref와 legacy locator를 이 Work에서 일괄 수정하는 cleanup
- Typed relation 의미, graph transaction wire 또는 acceptance/finalization 상태 체계 변경
- 외부 dependency, Python 지원 버전, global install, packaging과 publish 변경

<!-- key: id=key.work.metadata-parser-readiness-repair.order.source-context refs=key.section.source-context key.topic.artifact-graph -->
## Source Context

- `00_docs/standards/01_key-project-standard.md`의 `STD-KEYSTONE-015`, `017`, `018`, `025`
- `00_docs/standards/artifacts/key-standard-artifact-graph.md`의 metadata admission, typed relation,
  locator, stale/gap, generated index와 validation scope
- `00_docs/standards/skills/linker/key-standard-linker.md`의 metadata parsing과 reference-index readiness
- `00_docs/convention.md`의 standard-library-only, fail-soft diagnostic와 test 규칙
- R006 Reference Index and Context Readiness accepted 결과
- R007 Contract Execution Reconciliation accepted 결과와 repository validation evidence

<!-- key: id=key.work.metadata-parser-readiness-repair.order.baseline refs=key.topic.impact-review key.topic.verification -->
## Baseline Findings

1. 설치된 여섯 Keystone skill package와 repository source는 파일 단위로 일치한다.
2. R002 work order에서 여섯 skill owner로 향하는 inferred `produces` relation은 복구된다.
3. Compact parser는 `governed_by=A B`와 `refs=A B`에서 첫 값만 유지하고 후속 bare token을
   진단 없이 버린다.
4. 이 동작으로 여섯 skill의 child standard와 Init의 bootstrap standard를 포함한 governance
   target 7개가 graph snapshot에서 사라진다.
5. R008 작성 전 repository readiness는 `dangling_ref` 266 errors와 `locator_gap` 130 warnings를
   보고했지만 repository graph validator는 diagnostics 0으로 통과했다. 병행 문서 변경 후 재검토
   시점에는 294 errors와 124 warnings로 바뀌었으므로 고정 숫자보다 분류별 corpus envelope를
   acceptance evidence로 사용해야 한다.
6. Corpus에는 현재 parser가 놓치는 compact `refs` continuation token 1,341개와
   `governed_by` continuation token 7개가 관찰됐다.
7. Freshness token은 budget 안에서 실제 읽은 source만 포함하고, OwnerRecord는 유효한
   `test_name`, `config_key`, `schema_name` locator를 보존하지 못한다.
8. 기존 cache table이 v3 `updated_at` column을 갖지 않고 현재 freshness row도 없으면 refresh가
   매번 source fallback으로 끝날 수 있다.

<!-- key: id=key.work.metadata-parser-readiness-repair.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: source metadata 문법과 executable parser/readiness 결과를 일치시킨다.
- Impact seeds: `key.standard.project.std-keystone-015`,
  `key.standard.artifact.graph.generated-index`, `key.standard.skill.linker.metadata-parsing`,
  `key.skill.init`, `key.skill.reader`, `key.skill.author`, `key.skill.clarify`,
  `key.skill.linker`, `key.skill.coordinator`
- Required candidates: compact parser, reference scanner, parser/index/readiness tests, 여섯 skill
  snapshot
- Conditional candidates: taxonomy allowlist 또는 namespace owner 문서, `skill_source` locator policy
- Excluded: unrelated graph planner/reconciler, Author finalization runtime, consuming-project source,
  repository-wide metadata migration
- Acceptance owner: Main
- Graph handling: implementation delta를 Linker가 다시 분류하고, required synchronization이 있으면
  verified transaction 전에는 Work를 닫지 않는다.

<!-- key: id=key.work.metadata-parser-readiness-repair.order.approach refs=key.section.recommended-approach key.topic.verification -->
## Recommended Approach

1. 공백 구분 `refs`와 `governed_by`를 실제 source 형식으로 재현하는 실패 test를 먼저 추가한다.
2. Comma list와 YAML list 호환성을 유지하면서 continuation token을 결정적으로 정규화한다.
3. 알 수 없는 bare token을 조용히 버리지 않고 stable diagnostic 또는 명시적 parse failure로
   처리한다.
4. 실제 여섯 `SKILL.md`에서 project/child/bootstrap governance와 R002 production relation을
   snapshot으로 검증한다.
5. Unresolved ref를 namespace별로 분류하고, 수락된 기준으로 판정할 수 없는 taxonomy/owner
   선택만 Clarify에 넘긴다.
6. `skill_source`와 모든 supported locator field가 validator/readiness 양쪽에서 같은 의미로
   보존되는지 검증한다.
7. Discovery path-set digest와 completeness를 freshness에 포함하고 v2/v3 cache fixture가 한 번의
   recovery 뒤 v4 generation으로 재사용되는지 검증한다.
8. 실제 `00_docs` 전체를 fresh cache로 scan해 owner-required error를 0으로 만들고, 남은 warning은
   code, path와 승인 근거를 가진 allowlist로만 허용한다.

<!-- key: id=key.work.metadata-parser-readiness-repair.order.completion refs=key.topic.acceptance key.topic.integration-verification -->
## Completion Criteria

- [x] 공백 구분 다중 `refs`와 `governed_by`를 재현하는 test가 수정 전 실패하고 수정 후 통과한다.
- [x] Parser가 compact comma list와 YAML list compatibility를 유지한다.
- [x] Bare continuation token이 진단 없이 사라지지 않는다.
- [x] 여섯 skill owner와 R002 work order, project/child/bootstrap standard target이 예상 relation으로
  복구된다.
- [x] Owner-required ID와 controlled taxonomy ref가 근거 있는 정책으로 구분된다.
- [x] `skill_source` locator의 readiness와 validator 판정이 정합하다.
- [x] 실제 `00_docs` readiness가 owner-required error 0이며 남은 warning은 승인된 근거로 설명된다.
- [x] Truncated discovery는 fresh/full generation으로 재사용되지 않고 completeness debt를 보존한다.
- [x] Cache v2/v3 fixture가 반복 source fallback 없이 v4로 복구된다.
- [x] `heading`, `symbol`, `test_name`, `config_key`, `schema_name` locator 값이 index wire에서 보존된다.
- [x] Linker 175-test baseline, Author 73-test baseline, Reader와 skill contract suite가 회귀 없이
  통과한다.
- [x] Repository graph validator와 `git diff --check`가 통과한다.
- [x] Main이 변경 결과, residual diagnostics와 graph sync disposition을 검토한다.

## Acceptance Result

- Main acceptance: 2026-08-06
- Compact multi-value parser, exact taxonomy/owner policy, docs-scope external-owner warning,
  `skill_source` locator, freshness completeness와 disposable cache v4 recovery를 수락했다.
- Fresh docs readiness: owners 922, refs 2,883, errors 0, warnings 129
  (`locator_gap` 124, `out_of_scope_ref` 5), first cache `refreshed`, second cache `reused`.
- Fresh repository readiness: owners 928, refs 2,883, typed edges 20, errors 0,
  `locator_gap` warnings 124.
- Graph sync: `not_applicable`. 기존 skill owner와 `produces`·`governed_by` relation은 유지되고
  canonical node/relation mutation은 필요하지 않다.

<!-- key: id=key.work.metadata-parser-readiness-repair.order.review-points refs=key.section.review-points key.topic.impact-review -->
## Review Points

- 기존 compact/YAML metadata 입력과 public diagnostic compatibility가 유지되는가
- 다중 값 복구가 관계 방향이나 evidence 종류를 바꾸지 않는가
- Taxonomy 예외가 broad prefix suppression으로 mechanical stale을 숨기지 않는가
- `skill_source` locator 규칙이 다른 code/config/schema/test artifact 규칙을 약화하지 않는가
- Source scan, cache와 serialization ordering이 deterministic한가
- Budget 밖 path 변경이 freshness token에서 사라지지 않는가
- Cache repair가 fail-soft source 결과를 유지하면서 다음 invocation의 재사용을 복구하는가

<!-- key: id=key.work.metadata-parser-readiness-repair.order.verification refs=key.topic.verification -->
## Verification

- `PYTHONPATH=skills/keystone-linker/scripts python3 -m unittest discover -s skills/keystone-linker/tests -p 'test_*.py'`
- `PYTHONPATH=skills/keystone-author/scripts python3 -m unittest discover -s skills/keystone-author/tests -p 'test_*.py'`
- `python3 -m unittest discover -s skills/keystone-reader/tests -p 'test_*.py'`
- `python3 -m unittest discover -s skills/tests -p 'test_*.py'`
- Installed Linker package의 docs/repository scope readiness를 새 external cache에서 각각 실행
- Cache v2 migration, locked/corrupt cache와 scan truncation fixture
- `python3 skills/keystone-linker/scripts/validate_graph.py --root . --scope repository`
- Actual six-skill snapshot에서 expected `produces`, `governed_by`, `derived_from` relation 비교
- `python3 -m compileall`과 `git diff --check`

<!-- key: id=key.work.metadata-parser-readiness-repair.order.expected-output refs=key.contract.output key.topic.work-recovery -->
## Expected Output

- Compact multi-value parsing과 readiness diagnostic을 복구한 Linker runtime source
- 실제 Keystone source 형식을 고정하는 regression test
- Before/after readiness diagnostic과 relation snapshot 비교
- 남은 metadata gap, taxonomy debt와 locator debt 목록
- Discovery completeness와 cache migration before/after evidence
- Graph sync disposition과 Main acceptance에 필요한 verification evidence

<!-- key: id=key.work.metadata-parser-readiness-repair.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. 공백 continuation을 하나의 field 값으로 해석할 수 없는 유효 compact 문법이 발견된다.
2. Namespace를 taxonomy로 허용할지 stable owner를 만들지 서로 타당한 선택이 남는다.
3. 기존 public wire, diagnostic code 또는 Python 지원 버전의 호환성 없는 변경이 필요하다.
4. 전체 corpus migration이나 unrelated graph runtime 수정 없이는 완료할 수 없다.
5. 기존 사용자 변경과 target source가 충돌해 안전한 bounded diff를 만들 수 없다.
6. Required graph synchronization이 필요하지만 exact mutation/patch 또는 verification evidence가
   준비되지 않았다.
