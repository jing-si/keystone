---
doc_type: progress
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-06", accepted_by: main}
work_status: complete
step_ref: R008/S01
work_ref: R008/metadata-parser-readiness-repair
finalization: {state: complete, acceptance_ref: R008/S01/main-acceptance}
key:
  id: key.work.metadata-parser-readiness-repair.progress
  refs:
    - key.topic.progress-update
    - key.topic.keystone-metadata
    - key.topic.artifact-graph
    - key.topic.verification
---

# Metadata Parser and Readiness Repair 진행 기록

## 현재 상태

- Step: R008/S01
- Work status: complete
- Approval state: accepted
- Active: false
- Finalization state: complete
- Acceptance ref: R008/S01/main-acceptance
- Resume point: R008/S02 unannotated heading과 document-item governance RED fixture

Active steps: []

## 준비 증거

- 설치된 여섯 Keystone package와 repository source 전체가 일치한다.
- Repository graph validator: pass, diagnostics 0
- Linker: 175 tests passed
- Author: 73 tests passed
- Reader: 2 tests passed
- Skill contracts: 11 tests passed
- R008 작성 전 repository readiness: 266 dangling-ref errors, 130 locator-gap warnings
- Parser에서 compact refs continuation 1,341개와 governed-by continuation 7개가 누락되는
  evidence를 확인했다.

## 작업서 준비 검증

- R008 source document와 index를 추가한 뒤 repository graph validator는 diagnostics 0으로
  통과했다.
- Fresh repository readiness는 owner 843개를 복구하고 duplicate owner를 보고하지 않았다.
- Fresh repository readiness는 283 dangling-ref errors와 130 locator-gap warnings를 보고했다.
- 증가한 17 errors는 새 R008 문서가 기존 corpus와 같은 `key.doc.*`, `key.section.*`,
  `key.contract.*` ref를 사용해 드러난 현재 parser/taxonomy gap이며 S01 scope에 포함한다.
- 병행 문서 변경이 반영된 재검토 시점의 fresh docs readiness는 294 dangling-ref errors와
  124 locator-gap warnings다. Baseline corpus가 변할 수 있으므로 이후에는 prefix/code별
  diagnostic envelope와 source digest를 함께 기록한다.
- R008을 S01-S07로 확장한 직후 fresh docs readiness는 owner 921개, duplicate owner 0,
  dangling-ref errors 319개와 locator-gap warnings 124개다. 새 Work가 추가한 generic ref도 S01의
  taxonomy/owner policy가 해결해야 하는 실제 self-host input으로 보존한다.
- 6 MiB Markdown fixture에서 repository `coverage: full`이 `source_too_large` warning과 exit 0을
  반환했으며, 존재하지 않는 manifest `ghost.md`도 누락 진단 없이 통과했다. Repository
  completeness 수정은 R008/S04로 분리한다.
- 비 UTF-8 binary companion decode와 heading hierarchy 문제는 각각 R008/S04와 S02로 분리한다.
- Work-order creation은 source-document owner/ref index refresh로 분류하고, code/test/skill-source
  graph mutation은 수행하지 않았다.

## 다음 작업

1. R008/S02에서 모든 Markdown heading과 actual enclosing section stack을 고정한다.
2. `governed_by`의 child 합성 의미와 document relation direction을 Clarify/Decision gate에서
   확정한다.

## 구현 및 검증 결과

- RED 9건으로 compact continuation 손실, scalar 뒤 bare token 무시, locator 값 손실,
  incomplete discovery cache 재사용, legacy cache 반복 fallback, taxonomy/owner 혼용과
  `skill_source` locator gap을 재현했다.
- Multi-value field만 공백 continuation을 허용하고 scalar 뒤 bare token은
  `malformed_metadata`로 진단한다. 기존 comma list와 YAML list는 유지한다.
- 실제 여섯 `SKILL.md`에서 project/child/bootstrap governance와 R002 inferred `produces`
  relation을 repository snapshot test로 고정했다.
- Broad prefix suppression을 피하기 위해 mixed namespace는 exact taxonomy ID를 사용하고,
  section/step/artifact/mode처럼 owner namespace와 겹치지 않는 vocabulary만 prefix로 허용한다.
- Docs scope의 `key.skill.*` ref는 `out_of_scope_ref` warning으로 보존하고 repository scope에서
  실제 owner를 확인한다.
- Freshness v4는 전체 discovered path set과 completeness를 포함한다. Incomplete generation은
  cache에 저장하지 않으며 legacy v2/v3 cache는 한 번의 source fallback과 atomic recovery 뒤
  재사용된다.
- OwnerRecord의 scalar locator wire는 기존 호환성을 유지하면서 heading, symbol, test name,
  config key, schema name의 실제 값을 보존한다. Locator kind를 구조화하는 wire 변경은 S06 범위다.
- 실제 docs readiness: owners 922, refs 2,883, errors 0, locator warnings 124,
  out-of-scope warnings 5; cache는 `refreshed` 뒤 `reused`.
- 실제 repository readiness: owners 928, refs 2,883, typed edges 20, errors 0,
  locator warnings 124.
- 남은 124 locator warning은 R001 legacy item 120개와 현행 skill standard verification item
  4개다. Source 탐색을 막지 않는 기존 warning이며 corpus 일괄 locator migration은 이 Work의
  제외 범위로 승인한다.
- Linker 185, Author 75, Reader 2, skill contract 18 tests passed.
- Repository graph validator: pass, diagnostics 0. `compileall`과 `git diff --check`: pass.
- Graph sync disposition: `not_applicable`; canonical node/relation/provenance mutation 없음.
