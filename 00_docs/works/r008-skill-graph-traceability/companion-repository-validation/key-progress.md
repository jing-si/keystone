---
doc_type: progress
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-07", accepted_by: main}
work_status: complete
step_ref: R008/S04
work_ref: R008/companion-repository-validation
finalization: {state: complete, acceptance_ref: R008/S04/main-acceptance}
key:
  id: key.work.companion-repository-validation.progress
  refs:
    - key.topic.progress-update
    - key.topic.artifact-graph
    - key.topic.keystone-metadata
    - key.topic.verification
---

# Companion and Repository Validation 진행 기록

## 현재 상태

- Step: R008/S04
- Work status: complete
- Approval state: accepted
- Active: false
- Finalization state: complete
- Acceptance ref: R008/S04/main-acceptance
- Resume point: R008/S05 executable patch와 per-Step finalization closure RED fixture

Active steps: []

## 준비 증거

- Non-UTF-8 binary와 valid adjacent companion을 reconstruct하면 source text의 불필요한 UTF-8
  decode에서 `UnicodeDecodeError`가 발생한다.
- Companion physical patch target `<source>.keystone.json`과 logical graph source `<source>`가
  transaction omission 검사에서 같은 identity로 normalize되지 않는다.
- 6 MiB Markdown fixture의 `coverage: full` validation은 `source_too_large` warning과 exit 0을
  반환했다.
- Full manifest의 `ghost.md`는 `declared - discovered` 검사 부재로 diagnostic 없이 통과했다.
- Discovery는 raw bytes를 보존하지만 graph reconstruction은 path에서 source를 다시 읽는다.

## 다음 작업

1. R008/S05에서 executable patch body와 deterministic replay를 구현한다.
2. Failure reason별 retry와 모든 accepted Step의 finalization closure를 검증한다.

## 구현 및 검증 결과

- Companion-backed artifact는 logical `<source>` identity와 physical
  `<source>.keystone.json` patch target을 내부 helper로 구분한다. Omission과 observed mutation
  matching은 logical identity를 사용하고 baseline/apply/resulting digest는 physical bytes에
  결속된다.
- Binary source는 text decode 없이 raw-byte SHA-256만 검증하고 companion JSON만 UTF-8로
  parse한다. Repository discovery와 source-only reconstruction도 같은 captured bytes를 사용한다.
- Repository envelope는 mode, complete, discovered path digest, discovered/parsed/omitted/
  declared-only/skipped source와 count를 반환하며 core runner가 이를 보존한다.
- `coverage: full`의 truncation, oversized, unreadable, omitted와 declared-only path는 error이고,
  `subset`은 explicit warning/debt와 incomplete evidence를 유지한다.
- Reconstruction 후 captured physical bytes와 absent source를 재확인해 validation 중 변경은
  `source_generation_changed`로 fail-closed 처리한다.
- Binary discovery/reconstruction, logical/physical transaction, plan→attest→apply→verify,
  bidirectional manifest, budget/unreadable와 mixed-generation fixtures를 포함한 Linker 208 tests가
  통과했다. Coordinator 27, Author 75, Reader 2, skill contract 18 tests도 통과했다.
- Fresh docs readiness: owners 924, refs 2,889, errors 0, warnings 129, complete true.
- Fresh repository readiness: owners 930, refs 2,889, typed edges 20, errors 0, warnings 124,
  complete true.
- Actual repository validation: 235 sources discovered/parsed, skipped 0, complete true,
  diagnostics 0. Compileall과 `git diff --check`도 통과했다.
- Graph sync: `not_applicable`; canonical node/relation/provenance 선언은 바뀌지 않았고 source
  identity와 validation completeness의 기계적 해석만 강화했다.
