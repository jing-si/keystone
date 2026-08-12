---
doc_type: work_round
created_at: "2026-08-07"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-11", accepted_by: main}
round_status: accepted
key:
  id: key.work.round.r010-production-control-plane-hardening.index
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.artifact-graph
    - key.topic.finalization
    - key.role.coordinator
    - key.topic.verification
    - key.work.decisions.dec-works-029
global_state:
  active_round: none
  latest_accepted_round: R010
  active_steps: []
---

# R010 Standards-to-Product Alignment 작업서 색인

R010은 기준서·결정·작업서를 code, config, schema, API와 test에 연결하고 현재 작업 상태를
문서에서 복구하는 Keystone의 제품 핵심을 강화한다. S01-S04의 correctness 결과와 당시 수락
이력은 보존하되, R010/S05부터 `DEC-WORKS-029`에 따라 외부 키·HMAC 영수증·실제 agent 평가·독립
reviewer·평균 8.5 점수를 core completion gate에서 분리한다.

R010의 남은 목표는 더 강한 감사 인프라가 아니라 더 단순하고 설명 가능한 기준서 기반
프로젝트 관리 흐름이다.

<!-- key: id=key.work.round.r010.execution-order refs=key.topic.work-sequence key.topic.work-recovery -->
## 실행 순서

Active steps: []

| 순서 | Work | 경로 | 상태 | 현재 의미 |
|---|---|---|---|---|
| S01 | Production Control Plane Hardening | `production-control-plane-hardening/00_key-index.md` | complete, accepted | 당시 correctness·release 기반 구현 이력을 보존하며 S05의 현재 적합성 감사 대상이다 |
| S02 | Authority Chain and Snapshot Closure | `authority-chain-snapshot-closure/00_key-index.md` | complete, accepted | snapshot·scope 검증은 유지 후보이고 외부 키·HMAC·과도한 phase chain은 단순화 후보다 |
| S03 | Graph, Transaction and Source Correctness | `graph-transaction-source-correctness/00_key-index.md` | complete, accepted | SourceUnit·locator·lifecycle·mutation correctness는 핵심 유지 후보이고 HMAC receipt는 단순화 후보다 |
| S04 | Deterministic Work State Runtime | `work-state-runtime/00_key-index.md` | complete, accepted | repository-derived work recovery는 핵심 유지 후보이며 release/finalization 결속은 필요 범위로 축소 검토한다 |
| S05 | Product Direction Realignment | `agent-behavior-evaluation/00_key-index.md` | complete, accepted, finalized | main/frozen source와 consumer disposition 및 S06-A~E Change Set을 수락·최종화했다 |
| S06 | Standards-to-Product Core Simplification | `whole-flow-self-host-e2e/00_key-index.md` | complete, accepted | Lean Core 계약으로 기준서와 runtime을 단순화하고 암호학적 감사·agent gate를 core에서 분리했다 |
| S07 | Product Workflow Verification and Closure | `production-candidate-85-closure/00_key-index.md` | complete, accepted, finalized | 실제 기준서→영향→구현·검증→복구·수락 흐름과 terminal recovery로 R010을 닫았다 |

기존 S05-S07 경로와 Work owner ID는 참조 안정성과 계획 이력을 위해 유지한다. 현재 권위 있는
Goal과 criterion은 각 문서의 새 `product-alignment`, `core-simplification`, `product-workflow`
claim이며, 과거 actual-agent·8.5 계획 claim은 `supersedes` 관계로 대체한다.

<!-- key: id=key.work.round.r010.product-improvement-map refs=key.topic.work-sequence key.topic.verification -->
## 제품 개선 목록

| ID | Step | 개선 항목 | 기본 disposition |
|---|---|---|---|
| PM-01 | S05 | 기준서 기반 제품 목표와 기본 신뢰 경계 고정 | retain |
| PM-02 | S05 | S01-S04 source·contract·runtime·test inventory 분류 | review |
| PM-03 | S05 | Git/SHA freshness와 HMAC·외부 key 경계 분리 | simplify |
| PM-04 | S05 | Actual agent/reviewer/redaction/score gate 분리 | retire from core |
| PM-05 | S06 | Artifact Graph의 SourceUnit·locator·lifecycle correctness 보존 | retain |
| PM-06 | S06 | Repository-derived Work State와 중단 복구 보존 | retain |
| PM-07 | S06 | Closure·receipt·release consumer 최소화 | simplify |
| PM-08 | S06 | audit/QA 확장의 core dependency 제거; 이번 R010에서는 모듈을 만들지 않음 | retire current |
| PM-09 | S07 | 기준서→산출물 trace와 stale detection 검증 | verify |
| PM-10 | S07 | 작업 발견·진행·중단·재개·수락 흐름 검증 | verify |
| PM-11 | S07 | 설치·기본 CI·compatibility와 운영 복잡도 검증 | verify |

<!-- key: id=key.work.round.r010.realignment-boundary refs=key.work.decisions.dec-works-029 key.boundary.scope-control -->
## 재정렬 경계

1. S01-S04의 과거 `complete + accepted`와 finalization evidence를 삭제하거나 실패로 바꾸지 않는다.
2. 과거 수락은 당시 candidate의 이력이며 현재 제품 경계에서 모든 구현을 영구 유지한다는 뜻은 아니다.
3. S05는 source를 수정하는 구현 단계가 아니라 현재 상태 inventory, 기준서 우선순위와 교정
   Change Set을 확정하는 단계다.
4. S06 구현은 먼저 수락 가능한 기준서 의미를 확정한 뒤 시작한다. Pending 기준을 구현이 앞서지 않는다.
5. HMAC, 외부 key, 독립 reviewer와 실제 agent evidence는 별도 accepted threat model이나 제품 요구가
   없으면 core completion/release gate가 될 수 없다.
6. Git commit/tree와 scoped raw-byte SHA-256은 변경·freshness 확인에만 사용하며 암호화, 사람 신원
   또는 조직적 독립 증명으로 설명하지 않는다.
7. 삭제·호환성 중단·schema wire 제거는 S05 inventory와 consumer evidence 없이 추론하지 않는다.

<!-- key: id=key.work.round.r010.dependency-policy refs=key.topic.work-sequence key.topic.work-recovery -->
## Dependency policy

- S05는 S01-S04의 수락 이력을 input evidence로 사용하지만 그 구현을 현재 제품 경계에서 자동
  승인하지 않는다.
- S06은 S05가 `complete + accepted`이고 retain/simplify/optional/retire matrix, 대상 source,
  compatibility와 verification을 포함한 Change Set을 가진 뒤 시작한다.
- S07은 S06이 `complete + accepted`이고 실제 source 기준의 focused/package verification이 통과한
  뒤 시작한다.
- Dependency 결과는 status, 구현 권한이나 Main acceptance를 자동 생성하지 않는다.

<!--
key:
  id: key.work.round.r010.product-value
  supersedes:
    - key.work.round.r010.quality-target
-->
## Product Value Gate

R010은 점수표가 아니라 아래 사용자 가치로 판정한다.

1. 기준서나 작업서에서 관련 코드·설정·스키마·API·테스트를 직접 또는 의미 관계로 찾을 수 있다.
2. 산출물 변경에서 stale한 기준·작업·검증 후보를 설명 가능한 근거와 함께 찾을 수 있다.
3. 새 세션이 active Work, Step, goal, completion criteria, 현재 증거와 다음 작업을 문서에서 복구한다.
4. 문서 의미가 먼저 확정되고 implementation·verification·Progress가 그 의미를 추적한다.
5. 일반 사용자가 외부 secret, reviewer 운영이나 증거 보관 인프라 없이 기본 흐름을 완료한다.
6. 실패는 안정된 진단과 안전한 resume point를 제공하고 불필요한 새 schema·actor·key를 요구하지 않는다.

<!--
key:
  id: key.work.round.r010.product-subject-boundary
  supersedes:
    - key.work.round.r010.subject-lineage
-->
## Version and evidence boundary

Git commit/tree와 package digest는 검증한 source generation을 식별하는 데 사용한다. R010 completion은
고정 RC version, dual reviewer, candidate→terminal cryptographic lineage 또는 actual model evidence를
요구하지 않는다. Version 변경이나 publication은 별도 release 요청이 있을 때만 다룬다.

<!-- key: id=key.work.round.r010.boundaries refs=key.boundary.scope-control key.topic.verification -->
## Round 경계

- Publication, push, merge, 외부 소비 프로젝트 변경과 dependency 추가는 범위 밖이다.
- R011 planned 문서와 사용자가 진행 중인 변경을 R010 교정의 부수 효과로 수정하지 않는다.
- 성능 최적화는 측정된 병목이 있을 때만 별도 후보로 둔다. 현재는 schema·key·evidence 운영 복잡도
  축소를 우선한다.
- 선택적 audit/agent QA를 다시 도입하려면 독립 Goal, threat model, 비용과 non-blocking 소비 경계를
  먼저 수락한다.

<!-- key: id=key.work.round.r010.reading-rules refs=key.topic.work-recovery -->
## 복구 규칙

1. R010의 현재 목표와 남은 실행 순서는 이 index를 읽는다.
2. S01-S04 문서는 당시 수락된 구현과 evidence 이력으로 읽는다.
3. 현재 교정 방향과 disposition은 `DEC-WORKS-029`와 S05 Work Order/Progress를 읽는다.
4. S06은 수락된 교정 구현, S07은 제품 흐름 검증과 R010 closure만 소유한다.
5. R010은 terminal accepted history다. 현재 active state와 latest accepted Round는 canonical
   acceptance event, root index와 Context Map을 함께 확인한다.

## Superseded Historical Round Claims

다음 두 ID는 최초 R010 RC/점수 계획의 역사적 locator다. 현재 round gate가 아니며
`DEC-WORKS-029`와 이 문서의 Product Value Gate 및 Product Subject Boundary가 대체한다.

<!-- key: id=key.work.round.r010.quality-target kind=document_section refs=key.topic.acceptance key.topic.verification -->
- 평균 8.5, critical-area floor와 reviewer 기반 `Quality Target` — superseded.
<!-- key: id=key.work.round.r010.subject-lineage kind=document_section refs=key.topic.acceptance key.topic.finalization key.topic.verification -->
- RC candidate→terminal digest lineage requirement — superseded.
