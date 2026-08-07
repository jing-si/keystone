---
doc_type: progress
created_at: "2026-08-07"
document_lifecycle: active
approval: {state: pending}
work_status: planned
step_ref: R010/S03
work_ref: R010/graph-transaction-source-correctness
finalization: {state: pending}
key:
  id: key.work.graph-transaction-source-correctness.progress
  refs:
    - key.topic.progress-update
    - key.topic.work-recovery
    - key.topic.artifact-graph
    - key.topic.verification
    - key.acceptance.graph-source.package-classification
    - key.acceptance.graph-source.optional-applied-control
    - key.acceptance.graph-source.optional-omission
    - key.acceptance.graph-source.nonutf8-companion
    - key.acceptance.graph-source.lexical-anchor
    - key.acceptance.graph-source.source-unit-parity
    - key.acceptance.graph-source.cross-domain-inheritance
    - key.acceptance.graph-source.canonical-mutation-strict
    - key.acceptance.graph-source.prerequisite-verification
---

# Graph, Transaction and Source Correctness 진행 기록

## 현재 상태

- Step: R010/S03
- Work status: planned
- Approval state: pending
- Active: false
- Finalization state: pending
- Dependency evaluation: waiting — S02 `complete + accepted`는 Work completion에만 적용된다.
- Resume point: Main이 작업서를 수락하면 PC85-04 classification과 PC85-03 optional patch RED
  fixture부터 시작한다.

## 계획 기준선

- PC85-04: Package-owned Linker classification
- PC85-03: Optional patch fail-closed control
- PC85-05: SourceUnit·source parser 해석 단일화
- PC85-06: Domain-aware lifecycle inheritance
- PC85-07: Canonical mutation strict schema
- 상태 경계: 계획 수립만 완료했으며 implementation/verification completion을 주장하지 않는다.

## Criterion Status

| Criterion ID | State | Evidence ref | Subject | Generation/result digest |
|---|---|---|---|---|
| `key.acceptance.graph-source.package-classification` | pending | — | — | — |
| `key.acceptance.graph-source.optional-applied-control` | pending | — | — | — |
| `key.acceptance.graph-source.optional-omission` | pending | — | — | — |
| `key.acceptance.graph-source.nonutf8-companion` | pending | — | — | — |
| `key.acceptance.graph-source.lexical-anchor` | pending | — | — | — |
| `key.acceptance.graph-source.source-unit-parity` | pending | — | — | — |
| `key.acceptance.graph-source.cross-domain-inheritance` | pending | — | — | — |
| `key.acceptance.graph-source.canonical-mutation-strict` | pending | — | — | — |
| `key.acceptance.graph-source.prerequisite-verification` | pending | S02 acceptance와 S03 verification 대기 | — | — |

## 진행 로그

1. 2026-08-07: 사용자의 graph·transaction correctness 요구를 하나의 reviewable S03 Work로
   분리했다.
2. 2026-08-07: S01 acceptance를 시작 gate가 아닌 S03 completion gate로 기록해 S02와 병행할 수
   있게 했다.
3. 2026-08-07: 후속 검토에서 PC85-04 package-owned classification을 S03으로 이동하고 S02
   accepted snapshot/phase contract를 S03 completion dependency로 고정했다.
4. 2026-08-07: completion criterion에 stable ID를 부여하고 상태·evidence 소유를 Progress로
   분리했다.

## 다음 작업

1. Package-owned classification의 forged/stale/omitted/substitution fixture를 만든다.
2. Optional patch unattested/stale/source-redrift 상태 전이 fixture를 만든다.
3. Non-UTF-8 companion, false anchor, lifecycle inheritance와 malicious mutation fixture를 만든다.
