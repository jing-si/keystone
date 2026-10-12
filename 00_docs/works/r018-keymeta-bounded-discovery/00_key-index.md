---
doc_type: work_round
created_at: "2026-08-26"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-10-12", accepted_by: main}
round_status: accepted
key:
  id: key.work.round.r018-keymeta-bounded-discovery.index
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.work-recovery
    - key.topic.context-readiness
    - key.topic.artifact-graph
    - key.topic.keystone-metadata
    - key.topic.verification
    - key.boundary.scope-control
    - key.standard.project
    - key.standard.artifact.graph
    - key.standard.skill.linker
---

# R018 Keymeta-First Bounded Discovery 작업서 색인

R018은 키메타를 repository-wide parse의 표식으로만 소비하지 않고, 선택된 Work·문서·artifact의
탐색 anchor와 bounded source expansion 근거로 사용하도록 Reader·Linker readiness를 정렬한다.
Routine Work 준비는 필요한 source set에서 끝나야 하며, full repository graph reconstruction은
명시적 audit mode, release verification 또는 실제 scope conflict에만 사용한다. Owner 위치를
추가로 찾아야 할 때는 exact-ID lookup을 별도 비용 단계로 노출하고 targeted request를 조용히
repository audit으로 확장하지 않는다.

이 Round는 2026-10-12 사용자 진행 지시로 시작했으며 S01~S04를 구현·검증하고 Main이 수락했다.

<!-- key: id=key.work.round.r018.execution-order refs=key.topic.work-sequence key.topic.context-readiness -->
## 실행 순서

| 순서 | Step | 상태 | 목적 |
|---|---|---|---|
| S01 | Keymeta-Bounded Discovery Contract | complete / accepted | 키메타 anchor, source expansion, cold-start fallback와 full-scan 경계를 기준서·결정에 정합화한다 |
| S02 | Keymeta-Seeded Discovery Runtime | complete / accepted | routine readiness가 anchor와 bounded path set으로 owner/ref를 복구하도록 scanner·index·query 흐름을 구현한다 |
| S03 | Parser and Projection Hot-Path Optimization | complete / accepted | source admission 의미를 유지하면서 반복 lexical scan·재파싱·불필요한 projection 비용을 제거한다 |
| S04 | Consumer-Scale Verification and Closure | complete / accepted | 대형 Kotlin source와 대규모 ignored tree에서 정확성·범위·성능 기준을 검증하고 Round를 닫는다 |

- Active Step: 없음

세부 Goal, Scope, completion criteria와 검증 계획은 Work Order에서, 실제 상태와 resume point는
aggregate Progress에서 확인한다.

<!-- key: id=key.work.round.r018.boundaries refs=key.boundary.scope-control key.topic.context-readiness -->
## Round 경계

- R018은 Keystone 기준서, Linker/Reader skill runtime, graph runtime과 관련 test만 대상으로 한다.
- Routine `targeted` preparation은 선택된 anchor와 확인된 source set 밖으로 자동 확장하지 않으며
  repository completeness를 주장하지 않는다.
- Owner 위치가 필요한 경우 exact-ID `lookup`을 별도 단계로 실행하고 실제 검색 범위를 보고한다.
- Full repository scan과 graph reconstruction은 명시적 `audit`·release·scope-conflict 경로로
  보존한다.
- Cache와 generated index는 계속 폐기 가능한 비권위 파생물이며 source authority를 대체하지 않는다.
- Cache miss나 stale index를 성공으로 위장하거나 필요한 source omission을 숨기지 않는다.
- Persistent registry, 새 repository write surface 또는 user-facing runtime interface가 필요해지면
  구현을 중단하고 별도 사용자 결정을 받는다.
- R015의 source, Goal, scope, 상태와 우선순위는 이번 Round에서 수정하지 않는다.
- Browser, Playwright, publish와 installer 작업은 포함하지 않는다.

<!-- key: id=key.work.round.r018.reading-rules refs=key.topic.work-recovery key.topic.work-sequence -->
## 복구 규칙

1. R018 목표와 Step 상태는 이 Index에서 확인한다.
2. intended behavior, scope, acceptance와 stop condition은 Work Order를 읽는다.
3. 실제 실행 상태, 검증 evidence와 resume point는 Progress를 읽는다.
4. R018은 완료·수락됐으며 활성 Step은 없다.
