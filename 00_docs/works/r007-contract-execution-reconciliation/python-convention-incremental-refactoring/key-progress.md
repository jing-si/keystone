---
doc_type: progress
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-06", accepted_by: user}
work_status: complete
step_ref: R007/S02
work_ref: R007/python-convention-incremental-refactoring
finalization: {state: complete, acceptance_ref: R007/main-acceptance}
key:
  id: key.work.python-convention-incremental-refactoring.progress
  refs: [key.topic.progress-update, key.doc.convention, key.topic.clean-code, key.topic.verification]
---

# Python Convention and Incremental Refactoring 진행 기록

## 현재 상태

- Step: R007/S02
- Work status: complete
- Approval state: accepted
- Active: false
- Finalization state: complete
- Acceptance ref: R007/main-acceptance
- Current phase: convention과 1~16차 refactor, 잔여 감사, 최종 검증·검토·acceptance 완료
- Resume point: 없음

## 초기 감사

| 우선순위 | 대상 | 규모 | 판단 |
|---|---|---:|---|
| 1 | source metadata parsing | orchestration 269 lines, companion 259 lines, hierarchy 156 lines, relations 105 lines | declaration·companion·hierarchy·relation 책임 분리 완료 |
| 2 | `validator.py` snapshot/transaction validator | façade 15 lines, 분리 모듈 3개 | public API를 유지한 책임 분리 완료 |
| 3 | `validate_finalization.py` | orchestration façade 107 lines | source·Step·transition·impact·closure 분리 완료 |
| 4 | `model.py` wire serialization | domain 350 lines, wire 236 lines | 공개 façade를 유지한 serialization 분리 완료 |
| 5 | `planner.py` | planning 267 lines, impact 199 lines | candidate traversal/presentation 분리 완료 |
| 6 | transaction validation | façade 39 lines, lifecycle 201 lines, input 251 lines, evidence 266 lines, wire helper 262 lines | orchestration·state·input·evidence·wire 책임 분리 완료 |

구현과 Main 검토 뒤 사용자가 2026-08-06에 결과를 수락했다. execution과 approval 전이를 분리해
기록하고 finalization을 완료했다.

## 변경 기록

- `00_docs/convention.md`에 runtime, dependency 방향, 선호 패턴, 함수·오류·test와 점진적
  리팩터링 규칙을 작성했다.
- 외부 lint/type dependency는 도입하지 않고 Python 3.9 standard-library-only를 유지했다.
- `graph_runtime/yaml_subset.py`로 strict YAML subset parser와 `MetadataError`를 이동하고
  `metadata.py`는 공개 parser를 조합하도록 축소했다.
- Parser 정상/nested/malformed compatibility test 3개를 추가했다.
- `parse_reference_declaration()` 공개 경계로 navigation ref 해석을 캡슐화하고 `scanner.py`의
  `_metadata`, `_strings` private import를 제거했다.
- `graph_runtime.validator`를 compatibility façade로 유지하고 공통 진단·경로, source snapshot,
  transaction validation을 각각 `validation_support.py`, `snapshot_validation.py`,
  `transaction_validation.py`로 분리했다.
- 공개 validator import와 최소 snapshot/transaction behavior characterization test 2개를
  추가했고 Linker 전체 회귀를 통과했다.
- `validate_finalization.py`의 source path·frontmatter scalar 해석을
  `finalization_support.py`로 분리하고 block/inline mapping, scoped path와 active step 순서를
  고정하는 characterization test 3개를 추가했다.
- impact candidate와 namespace entry 검증을 `finalization_sections.py`의 독립 함수로 옮기고
  candidate 진단 선행 순서와 namespace owner 정렬을 고정하는 test 2개를 추가했다.
- finalization state, legacy schema compatibility와 graph synchronization closure를 하나의 section
  validator로 분리하고 schema v3 정상 closure와 schema v2 차단을 고정하는 test 2개를 추가했다.
- Step 선언·source status, active Step aggregate source, schema v3/legacy transition을
  `finalization_steps.py`로 이동하고 early-work trace도 같은 Step validation 경계에서 분리했다.
- malformed collection의 진단 순서와 early-work field 순서를 고정하는 test 2개를 추가했으며,
  `validate_finalization.py`는 CLI와 section orchestration만 담당한다.
- canonical snapshot·transaction·attempt-history JSON 조립을 `graph_runtime/wire.py`로 옮기고
  `model.py`의 기존 공개 serialization 함수는 지연 import compatibility façade로 유지했다.
- transaction validator는 새 wire 경계를 직접 사용하며, façade와 직접 호출 결과가 같은지
  검증하는 characterization test 2개를 추가했다.
- typed relation traversal, impact grade와 candidate budget projection을 `graph_runtime/impact.py`로
  이동하고 `planner.py`는 canonical mutation·patch transaction planning에 집중하도록 축소했다.
- 기존 planner import는 새 impact 타입과 함수를 그대로 re-export하며, identity와 projection
  결과를 고정하는 characterization test 2개를 추가했다.
- locator·provenance·node·relation wire predicate, mechanical envelope 검증, normalized comparison과
  baseline+mutation closure를 `transaction_wire_validation.py`의 순수 공개 함수로 분리했다.
- canonical entity, envelope consistency와 mutation add/duplicate behavior를 직접 고정하는 test
  3개를 추가했다.
- patch·attestation·apply-result 검증과 evidence 집계를 `transaction_evidence.py`로 이동하고,
  lifecycle validator는 immutable evidence result만 소비하도록 축소했다.
- digest wire predicate를 공통 helper로 승격했으며 malformed collection 조기 반환, evidence 집합과
  patch→attestation→result 진단 순서를 고정하는 test 4개를 추가했다.
- transaction root vocabulary, input delta, coverage debt와 canonical mutation 검증을
  `transaction_input.py`로 이동하고 lifecycle validator에는 immutable normalized input을 전달한다.
- header diagnostic 순서, invalid collection normalization과 duplicate mutation identity를 직접 고정하는
  test 3개를 추가했다.
- lifecycle state별 evidence closure와 verified source reconstruction 판정을
  `transaction_lifecycle.py`로 이동하고 `transaction_validation.py`는 input→evidence→lifecycle을
  조합하는 façade로 축소했다.
- pre-apply evidence 금지, conflict reason evidence와 empty verified closure 진단 순서를 직접 고정하는
  test 3개를 추가했다.
- canonical companion JSON parser를 `companion.py`로 이동하고, metadata string normalization과
  deterministic snapshot ordering을 `metadata_support.py`의 공개 support 경계로 통합했다.
- 기존 `metadata.parse_companion` import를 re-export로 유지하고 direct parser behavior test 2개를
  추가했다.
- document→section→item effective metadata, approval·governance·source authority clamp를
  `source_hierarchy.py`의 immutable `SourceNodeResult`로 분리했다.
- 상속과 authority expansion diagnostic 순서를 직접 고정하는 test 2개를 추가했다.
- structured/legacy relation conflict, work gate와 inferred `produces` 조립을
  `source_relations.py`의 immutable `SourceRelationResult`로 분리했다.
- dependency gate와 inferred production relation behavior를 직접 고정하는 test 2개를 추가했다.

## 잔여 대형 모듈 감사

| 대상 | 판단 |
|---|---|
| `finalization_steps.py` | Step source·active aggregate·transition 정책이 한 finalization 단계로 결합되며 schema helper가 이미 분리되어 유지 |
| `finalization_sections.py` | closure·impact·namespace가 독립 공개 함수로 분리되어 유지 |
| `snapshot_validation.py` | reconstruction과 semantic validation 함수가 분리되어 유지 |
| `scanner.py` | adapter registry·discovery·scan이 하나의 bounded scanner application 경계라 유지 |
| `planner.py`, `reconciler.py` | graph sync planning과 transaction state machine이라는 각각의 domain workflow라 유지 |

Private cross-module import, broad `except Exception`, 새 policy vocabulary 중복은 발견되지 않았다.
추가 파일 분리는 현재 범위에서 behavior 근거 없이 abstraction만 늘리므로 수행하지 않는다.

Main 검토에서 public import·wire·diagnostic·exit code 회귀나 scope 밖 변경은 확인되지 않았다.
사용자 acceptance 뒤 work status를 complete, approval state를 accepted로 전이했다.

## Verification

- Linker: 175 tests passed
- Author: 73 tests passed
- Skill contracts: 11 tests passed
- Python compileall과 `git diff --check`: passed
- Keystone repository scope graph validation: pass, diagnostics 0

## 유지한 contract

- `metadata.MetadataError` import compatibility
- `parse_source`와 companion behavior
- `graph_runtime.validator`의 공개 validation façade
- `graph_runtime.model`의 기존 snapshot·transaction·attempt-history wire import
- `graph_runtime.planner`의 기존 impact grade·candidate traversal·budget projection import
- transaction diagnostic code·순서와 verified mutation reconstruction closure
- finalization CLI의 diagnostic code, envelope와 exit code
- JSON wire, diagnostic code와 exit code
- Python 3.9 standard-library-only runtime
