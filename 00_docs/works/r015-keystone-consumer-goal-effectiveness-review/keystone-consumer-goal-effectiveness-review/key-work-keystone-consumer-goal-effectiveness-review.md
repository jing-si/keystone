---
doc_type: work_order
created_at: "2026-08-24"
document_lifecycle: draft
approval: {state: pending}
work_status: in_progress
key:
  id: key.work.keystone-consumer-goal-effectiveness-review.order
  refs:
    - key.doc.work
    - key.topic.work-recovery
    - key.topic.work-sequence
    - key.topic.context-readiness
    - key.topic.artifact-graph
    - key.topic.verification
    - key.boundary.scope-control
    - key.topic.skill-contract
    - key.standard.project
    - key.standard.artifact.graph
    - key.standard.skill.reader
    - key.standard.skill.author
    - key.standard.skill.linker
    - key.claim.r010.product-management-core
    - key.claim.r010.product-value-criteria
---

# Keystone Consumer Goal Effectiveness Review 작업서

## 문서 상태

이 문서는 Uptendo 소비 프로젝트에서 확인한 Keystone 운영 결과를 정리한 `draft / in_progress`
Work Order다. 구현을 기다리는 확정 작업서가 아니라, R015/S01에서 목표·판정·근거·문제 소유권과
개선 우선순위를 검토하고 수정하는 현재 작업 대상이다. 사용자 검토가 끝난 뒤 R015/S02에서만
최종 완성본으로 확정한다.

여기에 적힌 개선 후보는 아직 기준서·skill runtime·code·test 수정 승인이 아니다. 최종본은
후속 구현이 해결책 중심으로 과도하게 확장되지 않도록, 먼저 목표와 수용 증거를 고정하는 데
사용한다.

제품 목표와 비용 정책의 사용자 검토 과정은
[R015 Goal and Cost Policy Review](clarify/20260825T030236Z-r015-goal-and-cost-policy-review.md)에
비권위 Q&A 기록으로 보존한다.

<!-- key: id=key.work.keystone-consumer-goal-effectiveness-review.order.goal refs=key.section.goal key.claim.r010.product-management-core key.claim.r010.product-value-criteria -->
## Goal

실제 소비 프로젝트에서 Keystone이 문서나 절차의 양을 늘리는 도구가 아니라, 사람의 의도부터
현재 작업과 실제 산출물·검증까지를 필요한 비용으로 연결하는 project control plane으로
동작하게 할 영구 지향 기준과 개선 수용 조건을 확정한다.

R015는 다음 두 대분류 목표를 함께 달성한다.

### A. Keystone 적용 프로젝트의 목표 달성 효과성

1. **복구 정확성**: 새 세션이 제품 목표, 현재 accepted authority, 검토 중 overlay, 활성
   Round·Work·Step과 다음 행동을 잘못된 상태 없이 복구한다.
2. **산출물 추적성**: 중요한 사람 의도·결정·Work가 실제 code, config, schema, API와 test
   artifact로 추적된다.
3. **상태 권위 무결성**: 실행, dependency, verification, Main acceptance와 document lifecycle을
   잘못 승격하거나 축약하지 않는다.
4. **범위·병렬 안전성**: 병렬 작업과 dirty worktree에서도 승인 범위, source freshness와 관련
   없는 변경을 구분해 충돌과 재작업을 줄인다.
5. **근거 정직성**: evidence가 부족하면 성공으로 추정하지 않고 `unknown`, blocker 또는 추가
   확인 필요를 드러낸다.

### B. Keystone 운영 비용 효율성

1. **토큰 비용**: 초기 orientation과 작업 준비에 읽는 source, context payload와 반복 설명을
   목표 달성에 필요한 범위로 제한한다.
2. **작업 시간**: 불필요한 도구 호출, 전체 scan, 검증 반복과 사용자 왕복을 줄인다.
3. **문서 유지 비용**: Work 위험보다 많은 문서, 중복 상태와 수동 projection을 만들지 않는다.
4. **검증 비용**: affected verification으로 충분한 작업에 full corpus·repository·package·installer
   검증을 기본 요구하지 않는다.
5. **장기 운영 비용**: 새 persistent evidence·compatibility 체계와 metadata를 미래 유지 가치가
   비용을 정당화할 때만 추가한다.

<!-- key: id=key.work.keystone-consumer-goal-effectiveness-review.order.cost-policy refs=key.topic.verification key.boundary.scope-control -->
## 목표 하한과 비용 투자 기준

### 영구 목표 하한

다음 항목은 비용 절감을 이유로 낮추지 않는 최소 목표 하한이다.

1. 목표·현재 권위·활성 작업·다음 행동을 잘못된 상태 없이 복구한다.
2. 실행·dependency·verification·acceptance·document lifecycle을 서로 잘못 승격하거나 축약하지
   않는다.
3. 중요한 Work는 사람 의도에서 관련 production artifact와 verification evidence까지 추적할 수
   있다.
4. 사용자 승인 범위와 제외 범위를 넘지 않으며 병렬 변경을 조용히 덮어쓰지 않는다.
5. 근거가 부족하면 성공으로 추정하지 않고 불확실성, blocker 또는 추가 확인 필요를 드러낸다.

이 하한의 실제 충족 가능성과 충분성은 후속 실제 Work에서 검증할 수 있지만, R015에서는
잠정 규칙이 아니라 비용 최적화가 훼손할 수 없는 영구 지향 기준으로 사용한다.

### 한계효용 기반 비용 투자

1. 목표 하한 미달 상태에서는 비용 절감을 위해 목표 달성도를 조용히 낮추지 않는다.
2. 목표 하한을 충족하고 비용 증가가 낮거나 완만한 구간에서는, 추가 비용보다 목표 달성·안전·
   복구 증가가 의미 있게 크면 승인 범위 안에서 더 투자할 수 있다.
3. 비용 증가가 가속되거나 추가 목표 달성 증가가 둔화하면 추가 투자를 중단하거나 선택적 후속
   Work로 분리한다.
4. 비용과 목표 달성이 모두 크게 증가해도 목표 하한을 넘는 선택적 개선이면 기본 실행하지 않고
   사용자 승인을 받는다.
5. 목표 하한 자체를 달성하려면 고비용 작업이 필수인 경우, 생략하거나 성공으로 축약하지 않고
   예상 효과·비용·대안을 제시해 사용자 승인을 받는다.

### 고비용 사용자 승인 경계

다음 작업 형태로 진입할 때는 예상 효과, 비용과 더 작은 대안을 제시하고 사용자 허락을 받는다.

1. focused source로 판단 가능한데 전체 document corpus나 repository artifact를 적재한다.
2. affected verification으로 충분한데 전체 package·repository·installer 검증을 실행한다.
3. 하나의 개선을 위해 여러 skill·기준서·Round를 동시에 변경한다.
4. 새 persistent projection, manifest, evidence 또는 compatibility 체계를 추가한다.
5. unrelated dirty worktree 때문에 같은 조사·검증을 반복한다.
6. 실제 agent 반복 평가처럼 토큰과 시간이 실행 횟수에 따라 계속 증가한다.

R015는 이 대분류·소분류와 승인 경계를 확정한다. 작업별 토큰·시간 history의 저장 방식, 수집
runtime과 그 history를 이용한 반복 개선은 R015에서 만들지 않으며 별도 Work Order에서 다룬다.

<!-- key: id=key.work.keystone-consumer-goal-effectiveness-review.order.evaluation refs=key.topic.verification key.boundary.scope-control -->
## 평가 원칙

1. 소비 프로젝트의 현행 기준선을 정답으로 가정하지 않는다. 그 기준선과 Keystone 기본 동작이
   위 제품 목표에 효과적이고 효율적인지를 평가한다.
2. schema 통과, 문서 완전성, 목표 기여를 분리한다. 형식상 유효해도 복구·권위·추적·운영 비용을
   악화하면 제품 간극이다.
3. accepted source와 pending overlay를 구분하며, 최신 문서라는 이유로 pending 의미를 current
   authority로 승격하지 않는다.
4. Keystone core/runtime 결함, 제품 기본값·guidance 문제, 소비 프로젝트 자체 repair를 분리한다.
   사례 프로젝트의 모든 결함을 Keystone 구현 문제로 전환하지 않는다.
5. sandbox cache 실패처럼 source fallback으로 복구되고 소비 프로젝트 밖에서 발생한 현상은
   제품 구조 결함과 별도로 기록한다.
6. 모든 source에 metadata를 붙이거나 모든 Work에 같은 문서 묶음을 요구하지 않는다. 직접 추적은
   사용자 의미, 재사용, 보안·계약 또는 회귀 위험이 큰 artifact에 한정한다.
7. 비용은 단순 최소값이 아니라 목표 하한을 만족한 뒤의 한계효용으로 판단한다. 정확한 토큰·시간
   history가 없는 현재는 작업 형태 기반 승인 경계를 사용하며 숫자를 임의로 만들지 않는다.

<!-- key: id=key.work.keystone-consumer-goal-effectiveness-review.order.case-study refs=key.topic.context-readiness key.topic.artifact-graph -->
## Uptendo 사례 기준선

2026-08-24 검토 당시 다음 evidence를 확인했다.

- Canonical Work State는 271개 source를 오류·경고 없이 읽고 active `R015`, child `R015-o`,
  Step `R015-o/S01`과 R015-P의 dependency wait를 복구했다.
- 검토 중 R015-K가 다른 작업에 의해 `complete / accepted`로 바뀐 뒤에도 새 source generation에서
  최신 상태를 다시 복구했다.
- Docs-first graph는 421개 source를, repository scan 기준선은 1,894개 source를 읽었다.
- `00_docs`에는 421개 파일이 있었고 R015 subtree에는 120개 파일이 있었다.
- 루트 운영 문서, current Gradle/Kotlin server와 workflow, Work·Progress·Change Set, inline code/test
  metadata와 Git-ignored scratch source를 대조했다.
- 검토 종료 시 Uptendo worktree에는 85개 변경·추가 경로가 있었으며, 검토 자체는 그 source를
  수정하거나 되돌리지 않았다.

동시 작업으로 source 수와 generation은 바뀔 수 있다. 최종본에서는 숫자의 고정 자체보다 같은
제품 판정과 분류가 current source에서 재현되는지를 확인한다.

<!-- key: id=key.work.keystone-consumer-goal-effectiveness-review.order.verdict refs=key.claim.r010.product-value-criteria -->
## 현재 판정

Keystone은 Uptendo에서 **현재 작업 복구 원장으로는 효과적으로 동작**했다. Work State는 현재
Round·Step·Gate를 정확히 복구했고, 최근 Work Order는 목적, scope, gate, completion criteria,
stop condition과 verification을 제공했다.

반면 **단순하고 선택적인 project control plane으로서는 부분 성공**이다. 현재 authority의 표현,
소비 프로젝트 진입 문서와 실제 runtime의 정합성, Work에서 실제 artifact로 가는 직접 관계,
Linker의 source admission/Step contract와 작업 위험 대비 문서 유지 비용이 제품 목표를 방해할 수
있는 간극으로 남았다.

## 확인된 강점

1. Work State가 aggregate Progress에서 active parent·child Round, Step과 Gate 대기를 복구한다.
2. 최근 Work Order는 실행 범위뿐 아니라 제외 범위, 중단 조건과 미수행 verification을 명시한다.
3. source generation 변화가 생기면 최신 source를 다시 읽어 오래된 세션 상태를 고정하지 않는다.
4. Work completion, approval, Round acceptance와 dependency를 분리해 child 결과를 부모 성공으로
   자동 승격하지 않는다.
5. disposable cache가 없어도 raw source fallback으로 current recovery를 계속할 수 있다.

<!-- key: id=key.work.keystone-consumer-goal-effectiveness-review.order.gaps refs=key.topic.artifact-graph key.topic.work-recovery key.topic.context-readiness -->
## 목표 대비 간극과 소유권 후보

| Priority | 확인된 간극 | 사례 evidence | 1차 소유권 후보 | 제품 영향 |
|---|---|---|---|---|
| P0 | accepted authority와 pending overlay가 한눈에 분리되지 않음 | Uptendo의 Project Standard·Decision·Context/Works index는 pending인데 R005·R006 accepted Progress는 current core를 수용했다고 기록 | Keystone default/guidance + Uptendo repair | 새 세션이 규범 권위와 검토 중 의미를 혼동할 수 있음 |
| P0 | 실제 runtime과 소비 프로젝트 진입 문서가 drift | Uptendo `AGENTS.md`, `README.md`, `docs/project-operations.md`, `docs/runtime-topology.md`는 C#·Hangfire·dotnet을 안내하지만 current workflow/server는 Kotlin·Gradle·JobRunr | Uptendo repair; Keystone stale-entry detection 후보 | 첫 진입이 잘못된 구현·검증 경로를 유도 |
| P1 | Linker가 다른 Keystone 계약과 같은 Step/source 의미를 사용하지 않음 | Work Order에 선언된 R015-P S03·S04를 Gate target으로 인정하지 않고, Git-ignored `.superpowers` snapshot을 live owner와 중복 계산하며, mixed binary/JSON source view가 bounded fail-soft하지 않음 | Keystone core/runtime | 유효한 source가 구조 오류로 보이고 scratch가 graph를 오염시킴 |
| P1 | 중요한 Work에서 production/test artifact로 가는 직접 연결이 약함 | sampled Uptendo server·web source에 active/accepted Work의 stable relation이 드물고 Change Set은 경로 서술 중심 | Keystone default/guidance + selective project adoption | 영향·재사용·회귀 test 탐색이 사람 기억에 의존 |
| P2 | 작업 위험보다 문서·projection 유지 비용이 큼 | Uptendo `00_docs` 421개, R015 120개이며 Round/Work/Progress/Change Set과 여러 index에 상태가 반복됨 | Keystone product model/default | 작은 수정의 작성 비용과 stale projection 가능성이 증가 |
| P2 | shared dirty worktree에서 session freshness와 전역 검증 비용이 큼 | 검토 중 다른 Work 상태가 바뀌고 unrelated source가 전체 검증 결과에 영향을 줌 | Keystone workflow/default + project operation | 국소 작업이 오래된 기준선이나 관련 없는 실패에 막힐 수 있음 |

이 소유권은 S01 검토 후보이며 최종 결정이 아니다. 특히 stale Uptendo 운영 문서를 고치는 일과
그 drift를 더 빨리 발견하도록 Keystone을 개선하는 일은 별도 Work로 분리해야 한다.

<!-- key: id=key.work.keystone-consumer-goal-effectiveness-review.order.improvement-candidates refs=key.topic.verification key.boundary.scope-control -->
## 후보 개선 순서

1. **제품 목표와 authority recovery 확정**: accepted core와 pending overlay의 표시·복구 계약을
   단순하게 정의하고, 실제 소비 프로젝트에서 모호성이 사라지는 수용 시나리오를 만든다.
2. **Linker source/Step 계약 정합화**: Work Order future Step, Git-ignored scratch, unsupported or
   mixed source의 admission과 fail-soft 경계를 Reader·Author·Linker가 동일하게 해석한다.
3. **operative entry drift 발견 경계**: 현재 runtime/toolchain과 명시적 root entry document가
   충돌할 때 자동 수정 대신 bounded stale candidate를 보고하는 최소 경계를 검토한다.
4. **선택적 Work→artifact 추적**: public contract, shared service, schema/config/security boundary와
   중요한 regression test에만 direct `produces`·`revises`·`verifies` 관계를 요구한다.
5. **위험 기반 문서 수준**: 작은 single-surface Work는 최소 Work source와 aggregate Progress로
   충분하게 하고 child Round, per-Step Progress와 Change Set은 multi-surface, high-risk, parallel
   dependency work에만 사용한다.
6. **consumer cold-start acceptance**: 새 agent가 짧은 bounded source set으로 목표, authority,
   active Step, artifact/test와 수용 기준을 복구하고 관련 없는 source를 열지 않는지 검증한다.

## 최종 Work Order에서 확정할 항목

1. Keystone 적용 프로젝트의 목표 달성 효과성과 토큰·작업 시간 비용 효율성의 대분류·소분류가
   실제 소비 프로젝트 요구와 충분히 일치하는지
2. authority baseline/overlay 문제를 runtime projection, Author guidance, Init scaffold 또는 소비
   프로젝트 repair 중 어디에서 해결할지
3. Linker의 future Step·Git-ignore·mixed source 문제를 하나의 source admission contract로 묶을지
   독립 개선 Work로 나눌지
4. direct artifact relation이 필요한 “중요한 Work”의 최소 분류 기준
5. small/medium/high-risk Work별 기본 문서 surface와 optional projection 규칙
6. cold-start acceptance에서 영구 목표 하한과 고비용 승인 경계를 검증하되, 작업별 토큰·시간
   history 수집은 어떤 후속 Work로 분리할지

<!-- key: id=key.work.keystone-consumer-goal-effectiveness-review.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- Uptendo 사례 evidence와 Keystone 목표의 정합성 검토
- 현재 강점, 간극과 residual risk의 사실·추천 분리
- 각 간극의 Keystone core/default/guidance와 consumer repair 소유권 분류
- 목표 달성 효과성·비용 효율성의 대분류·소분류, 영구 목표 하한과 고비용 승인 경계 확정
- 후보 개선 우선순위, 후속 Work 분리 원칙과 수용 기준 확정
- R015 Work Order, Progress와 필요한 navigation source의 정합화

Exclude:

- Keystone standard, decision, skill source, runtime code와 test 수정
- Uptendo 문서, code, config, schema, API, test와 Work 상태 수정
- R014 Reader Progressive Context Loading의 범위·상태·우선순위 변경
- 작업별 토큰·시간 history 저장 형식, 수집 runtime과 history 기반 자동 개선 구현
- 모든 source의 metadata 일괄 추가 또는 과거 Work 이력 재작성
- browser, Playwright, screenshot, external publish와 설치 작업

<!-- key: id=key.work.keystone-consumer-goal-effectiveness-review.order.plan refs=key.topic.work-sequence key.topic.verification -->
## 실행 계획

| Step | 상태 | 작업 범위 | 완료 경계 |
|---|---|---|---|
| R015/S01 | in_progress | 현재 감사 결과를 목표 달성 효과성·비용 효율성 기준 Work Order 초안으로 정리하고 사용자 검토에 따라 수정 | 두 목표의 대분류·소분류, 영구 목표 하한, evidence, 판정, 소유권 후보와 개선 순서가 서로 모순 없이 reviewable하다 |
| R015/S02 | planned | S01 피드백을 반영해 미확정 항목, 후속 Work 분리와 cold-start acceptance를 확정 | 사용자가 최종 Work Order를 수용하고 구현 범위와 분리된 완성본이 된다 |

<!-- key: id=key.work.keystone-consumer-goal-effectiveness-review.order.completion refs=key.topic.verification key.topic.work-recovery -->
## Completion Criteria

<!-- key: id=key.acceptance.keystone-consumer-goal-review.goal -->
- `R015-CC-01` R015 목표가 Keystone 적용 프로젝트의 목표 달성 효과성과 토큰·작업 시간 비용
  효율성으로 구분되고, 각 소분류·영구 목표 하한·한계효용 투자·고비용 사용자 승인 경계가
  정의된다.
<!-- key: id=key.acceptance.keystone-consumer-goal-review.evidence -->
- `R015-CC-02` 각 핵심 강점과 간극이 재확인 가능한 소비 프로젝트 source 또는 runtime 결과에
  연결되고 사실과 추천이 구분된다.
<!-- key: id=key.acceptance.keystone-consumer-goal-review.ownership -->
- `R015-CC-03` Keystone core/runtime, default/guidance와 consumer project repair 소유권이
  구분되어 사례 프로젝트 문제를 제품 구현 범위로 잘못 확대하지 않는다.
<!-- key: id=key.acceptance.keystone-consumer-goal-review.priority -->
- `R015-CC-04` 개선 후보가 목표 기여도, correctness risk와 운영 비용을 기준으로 우선순위화되고
  독립 후속 Work로 나눌 수 있다.
<!-- key: id=key.acceptance.keystone-consumer-goal-review.cold-start -->
- `R015-CC-05` Work State·Linker 의미 합의, authority recovery, operative entry, 중요한 artifact/test
  trace와 작은 Work 비용을 확인하는 consumer cold-start acceptance가 정의된다.
<!-- key: id=key.acceptance.keystone-consumer-goal-review.scope -->
- `R015-CC-06` Work Order 최종화와 개선 구현, Uptendo repair의 승인 범위가 분리되어 있다.
<!-- key: id=key.acceptance.keystone-consumer-goal-review.user-acceptance -->
- `R015-CC-07` 사용자가 최종 Work Order를 검토하고 완성본으로 수용한다.

<!-- key: id=key.work.keystone-consumer-goal-effectiveness-review.order.verification refs=key.topic.verification -->
## Verification

1. Project Standard 목적과 `DEC-WORKS-029`의 제품관리 핵심·가치 기준에 두 Goal, 영구 목표
   하한과 비용 투자 원칙이 일치하는지 대조한다.
2. Uptendo evidence를 current source와 canonical Work State/Linker 결과로 다시 확인하고 변동된
   숫자와 지속되는 구조 판정을 분리한다.
3. 각 간극이 Keystone core/default/guidance 또는 consumer repair로 분류된 근거를 검토한다.
4. 최종 후보가 후속 Work로 독립 실행 가능한 Goal, Scope, acceptance와 stop boundary를 갖는지
   확인한다.
5. R015 상태 변경 뒤 `python3 scripts/work_state_runtime.py --root .`로 active Round/Step과
   Progress authority를 검증한다.
6. 새 stable ID/ref, Markdown link, exact navigation과 `git diff --check`를 확인한다.
7. 현재는 code/skill runtime이 바뀌지 않으므로 package, repository, installer와 browser 검증을
   실행하지 않는다.

<!-- key: id=key.work.keystone-consumer-goal-effectiveness-review.order.stop refs=key.boundary.stop-condition key.boundary.scope-control -->
## Stop Conditions

1. 제품 목표, 문제 소유권 또는 개선 묶음에 서로 유효한 선택지가 있어 사용자 결정 없이는
   최종화할 수 없다.
2. current Uptendo evidence가 핵심 판정을 바꿀 정도로 달라져 재검토 없이 기존 결론을 유지할 수
   없다.
3. Work Order 교정이 아니라 Keystone 기준서·결정·skill/runtime 또는 Uptendo source 수정이
   필요해진다.
4. R014 상태 변경, 구현 우선순위 또는 다른 Round 재배치가 필요해진다.
5. 목표 달성 효과보다 metadata·문서 형식 보강 자체가 작업의 주목적이 된다.

## 현재 다음 행동

R015/S01에서 사용자가 Goal, 현재 판정, 간극별 소유권 후보와 개선 순서를 검토한다. 피드백은
R015 Work Order와 Progress에만 반영하고, 최종 수용 전에는 S02 완료나 개선 구현으로 넘어가지
않는다.
