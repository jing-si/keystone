---
doc_type: work_order
created_at: "2026-08-05"
status: active
approval: {state: accepted, accepted_at: "2026-08-05", accepted_by: user}
work_status: accepted
key:
  id: key.work.graph-runtime-validator.order
  refs: [key.doc.work, key.topic.artifact-graph, key.topic.keystone-metadata, key.topic.verification, key.topic.change-set]
---

# Graph Runtime and Validator 작업서 및 Change Set

## Goal

동일 source surface에서 deterministic graph를 재구성하고 canonical mutation, optimistic
transaction과 기계적 무결성 evidence를 제공하는 portable runtime과 validator를 구현한다.

## Prerequisite

- R005 S01 accepted

## Scope

Include:

- Markdown document/item metadata parser
- Existing flat metadata와 canonical metadata normalization
- Generic line-comment, Kotlin/Java, SQL, XML, YAML adapter
- Comment를 지원하지 않거나 안정적으로 해석할 수 없는 surface의 source-adjacent companion
  metadata fallback
- Node/relation/provenance/lifecycle/locator reconstruction
- Document/artifact delta input과 graph planner
- Attestation, application result와 graph reconciler
- Source digest 기반 stale baseline 검출
- Duplicate ID, missing target, invalid relation, malformed metadata, locator, supersession cycle,
  orphan, retired reference 검사
- Machine-readable diagnostics, stable exit code와 package command/interface
- Changed seed 중심 traversal과 optional derived cache
- Project extension이 core rule을 약화하지 못하는 경계

Exclude:

- Author·Coordinator·Linker skill runtime contract 수정
- 자동 source patch 적용
- Semantic relation 또는 acceptance 자동 결정
- Central graph registry와 persistent database
- 특정 framework AST 또는 Kotlin compiler plugin
- 외부 소비 프로젝트 source와 fixture

## Change Set

- Expected output: Linker-owned graph runtime, validator, interface reference와 tests
- Impact seeds: S01 canonical schema, graph transaction, R004 finalization validator interface
- Required candidates: installer/package surface, Linker package, Author finalization integration point
- Excluded: external repositories, global install, publishing
- Verification: unit tests, fixture tests, CLI smoke, failure mapping, install smoke

## Completion Criteria

- [x] 모든 지원 surface가 같은 canonical graph model로 정규화된다.
- [x] 기존과 canonical metadata를 읽기 호환한다.
- [x] Inferred relation을 mutation source로 자동 승격하지 않는다.
- [x] Stale baseline과 partial application을 verified로 오인하지 않는다.
- [x] Validator가 source 수정·semantic 판단·acceptance 권한을 갖지 않는다.
- [x] Package command가 parseable diagnostics와 stable exit code를 반환한다.
- [x] Derived cache 없이 source-only reconstruction이 가능하다.
- [x] 외부 프로젝트 source 없이 검증 가능하다.

## Implementation Result

- Linker package에 canonical model, metadata parser, surface adapters, planner, reconciler와
  diagnostic-only validator/runner/hook를 구현했다.
- `produced_from` reconstruction, owner/surface matrix, exact transaction closure, strict companion
  schema와 multi-source relation identity merge를 포함한다.
- Linker 81 tests와 기존 Author 41 tests, installer smoke, CLI help, Python/shell syntax 및
  `git diff --check`를 통과했다.

## Verification

- Parser/adapter/normalization unit test
- Transaction state machine과 failure/resume test
- Invalid relation, duplicate, missing target, stale locator와 cycle fixture
- Package command, timeout, malformed output, missing validator와 installer smoke test
- 필요한 build/type/lint test와 `git diff --check`

## Stop Conditions

1. S01이 accepted되지 않았다.
2. Runtime이 특정 소비 프로젝트 구조나 언어를 core 전제로 요구한다.
3. Validator가 source edit, semantic relation 결정 또는 acceptance 권한을 요구한다.
4. Package portability가 외부 프로젝트 source 복사를 요구한다.
