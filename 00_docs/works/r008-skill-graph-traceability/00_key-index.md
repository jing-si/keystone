---
doc_type: work_round
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: pending}
round_status: active
key:
  id: key.work.round.r008-skill-graph-traceability.index
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.artifact-graph
    - key.topic.keystone-metadata
    - key.topic.verification
---

# R008 Skill Graph and Self-Host Runtime Closure 작업서 색인

R008은 R007 이후 재검토에서 확인된 subsystem 간 의미 불일치를 Keystone 자체 corpus의 실제
workflow로 닫는다. Compact metadata와 owner/ref readiness를 출발점으로 Markdown hierarchy,
dependency execution, companion/repository validation, transaction/finalization, graph lifecycle과
wire compatibility를 순서대로 정합화한 뒤 skill runtime traceability와 self-host E2E로 검증한다.

<!-- key: id=key.work.round.r008.execution-order refs=key.topic.work-sequence key.topic.work-recovery -->
## 실행 순서

Active steps: [R008/S03]

| 순서 | Work | 경로 | 상태 | 목적 |
|---|---|---|---|---|
| S01 | Metadata Parser and Readiness Repair | `metadata-parser-readiness-repair/00_key-index.md` | complete | accepted — compact metadata, owner/ref readiness와 cache completeness를 정합화했다 |
| S02 | Markdown Hierarchy and Governance | `markdown-hierarchy-governance/00_key-index.md` | complete | accepted — 실제 heading hierarchy와 effective governance·relation 의미를 정합화했다 |
| S03 | Dependency Execution Graph | `dependency-execution-graph/00_key-index.md` | in_progress | Step registry, legacy candidate와 expanded-event cycle 판정을 구현한다 |
| S04 | Companion and Repository Validation | `companion-repository-validation/00_key-index.md` | planned | binary companion과 repository full-coverage validation을 fail-closed로 만든다 |
| S05 | Transaction and Finalization Hardening | `transaction-finalization-hardening/00_key-index.md` | planned | executable patch, failure retry와 모든 accepted Step finalization closure를 검증한다 |
| S06 | Graph Lifecycle and Wire Compatibility | `graph-lifecycle-wire-compatibility/00_key-index.md` | planned | relation evidence/lifecycle와 graph wire version 의미를 정합화한다 |
| S07 | Skill Runtime Traceability and Self-Host E2E | `skill-runtime-traceability/00_key-index.md` | planned | 핵심 runtime·test traceability와 실제 전체 workflow를 검증한다 |

현재 active Step은 `R008/S03`이다. S04-S06은 앞선 Step에서 확정된 source/runtime 의미를
차례로 baseline으로 사용하고, S07은 S01-S06 결과를 하나의 self-host workflow에서 검증한다.
이 순서는 round의 기본 실행 순서이며 별도 자동 acceptance gate나 상태 전이를 만들지 않는다.

<!-- key: id=key.work.round.r008.boundaries refs=key.boundary.scope-control key.topic.artifact-graph -->
## Round 경계

- 기존 기준서의 정책 의미를 임의로 바꾸지 않고 runtime과 source metadata의 불일치를 우선
  복구한다. `governed_by` 합성 의미와 graph wire version처럼 호환성 또는 authority 의미를
  바꾸는 선택은 구현 전에 Decision/Clarify gate를 통과한다.
- 전체 corpus metadata 일괄 변환, 모든 code/test symbol의 anchor화와 repository-wide cleanup은
  범위 밖이다.
- Global install, plugin packaging, marketplace, publish와 2~4주 외부 소비 프로젝트 pilot은
  수행하지 않고 별도 후속 round 후보로 남긴다.
- Namespace 또는 locator 정책에 서로 타당한 복수 선택이 남으면 구현 전에 Clarify로 넘긴다.
- R008 acceptance는 unit suite 통과만으로 닫지 않고 actual corpus readiness, repository
  completeness, dependency evaluation, graph transaction과 multi-Step finalization의 source-only
  reconstruction evidence를 요구한다.

<!-- key: id=key.work.round.r008.reading-rules refs=key.topic.work-recovery key.topic.artifact-graph -->
## 복구 규칙

1. Round 상태와 실행 순서는 이 파일을 기준으로 읽는다.
2. 각 Work의 Goal, Scope, Completion Criteria는 해당 `key-work-*.md`를 읽는다.
3. 실제 실행 상태와 resume point는 각 `key-progress.md`를 읽는다.
4. Source-document graph delta는 Linker가 분류하며 Author가 graph 결론을 대신 만들지 않는다.
