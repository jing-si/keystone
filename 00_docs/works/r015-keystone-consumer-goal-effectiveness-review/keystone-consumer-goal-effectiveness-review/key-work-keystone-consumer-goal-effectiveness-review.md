---
doc_type: work_order
created_at: "2026-08-24"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-10-13", accepted_by: user}
work_status: complete
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

2026-10-13 사용자가 최종 정책·고정 안내문·후속 구현 범위를 수용한 검토 결과다.
R015/S01~S02 검토는 완료했으며 구현은 [R015-A](../r015-A/00_key-index.md)에 편성한다.
이 문서는 수용된 정책과 사례 근거를 보존한다. 부모 R015 완료나 하위 구현 완료를 뜻하지 않는다.

제품 목표와 비용 정책의 사용자 검토 과정은
[R015 Goal and Cost Policy Review](clarify/20260825T030236Z-r015-goal-and-cost-policy-review.md)에
비권위 Q&A 기록으로 보존한다.

<!-- key: id=key.work.keystone-consumer-goal-effectiveness-review.order.goal refs=key.section.goal key.claim.r010.product-management-core key.claim.r010.product-value-criteria -->
## Goal

Keystone은 개발 방법론 자체보다 Round를 나누고 작업을 편성·복구하는 개발 관리 하네스다.
Uptendo에서 확인한 관리 효과를 유지하면서, 착수·진행·병렬 작업·변경 대응·종료·재개 흐름에서
언제 문서를 신뢰하고 언제 정합성을 확인할지 정한다. 반복적인 문서 확인이 실제 구현보다
많은 시간을 쓰는 문제를 줄이되, 사람의 의도와 기준서·작업서·코드 연결의 정확성을 보존한다.
R015는 전반적인 관리 흐름을, R018은 탐색·검토 알고리즘을 개선한다.

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
## 현재 판정과 사용자 방향 — 2026-10-13 반영

사용자는 Uptendo에서 Round 분리와 작업 편성의 효과에 만족했다. R015는 소비 프로젝트의
모든 결함을 고치거나 검사 도구를 확장하는 Round가 아니다. 관리 흐름 전체에서 반복 확인의
비용과 연결 정합성 사이의 균형을 찾고, 후속 구현의 정책·범위·수용 조건을 정리한다.
아래 정책은 이번 대화에서 합의한 R015 개선 방향이다. 아직 공통 기준·설치 스킬·runtime에
적용된 계약으로 취급하지 않으며, 최종 Work Order 수용과 구현 승인은 구분한다.

<!-- key: id=key.work.keystone-consumer-goal-effectiveness-review.order.gaps refs=key.topic.artifact-graph key.topic.work-recovery key.topic.context-readiness -->
## 문제 소유권과 기존 개선의 활용

| 항목 | R015에서의 처리 |
|---|---|
| 반복 확인·종료 점검·변경 대응 | 관리 흐름의 정책과 수용 조건을 정한다. |
| 탐색·파싱 속도 | [R018](../../r018-keymeta-bounded-discovery/keymeta-bounded-discovery/key-work-keymeta-bounded-discovery.md)의 개선을 활용한다. 같은 알고리즘 개선을 재설계하지 않는다. |
| 상태 중복·갱신 책임 | [R024](../../r024-unified-state-management/unified-state-management/key-work-unified-state-management.md)가 소유한다. Closed List 정책의 저장·갱신 접점만 후속 대조한다. |
| Round·Work·Step·Task 정의 | [R025](../../r025-work-hierarchy-definition/work-hierarchy-definition/key-work-work-hierarchy-definition.md)의 정의를 활용한다. Round·Step 기본 틀과 선택적 Work·Task를 설명한다. |
| 작은 작업의 절차 부담 | 별도 지시가 없으면 Keystone 흐름을 따른다. 크기만으로 자동 생략하거나 매번 간소화를 묻지 않는다. 사용자 예외와 R025의 선택적 단위는 존중한다. |
| 기준 개정 중 권위 충돌 | 확정 내용·검토 중 내용·현재 작업 영향·선택지를 설명하고 사용자 결정을 받는다. 같은 결정을 반복해서 묻지 않는다. |
| Uptendo의 C# 안내 잔존 | 소비 프로젝트의 문서 정리 과제다. 이 사례만으로 Keystone 자동 탐지 의무를 추가하지 않는다. |
| 코드의 명시적 그래프 관계 부족 | AI가 정확하고 효율적으로 연결을 확인할 수 있으면 결함으로 단정하지 않는다. 실제 누락·잘못된 연결·탐색 부담을 기준으로 판단한다. |
| Linker의 Step 부재 오진 | 재현된 도구 문제 후보다. 아래 합의된 역할 분담을 별도 구현 범위로 구체화한다. |

R018은 완료·수락됐고 R025는 정의·기준 정합화가 완료됐다. R024도 상태 저장 계약과 소비자
연결을 구체화했다. 문서·저장소 구현·실제 설치·소비 프로젝트 이전은 각각 구분하며, 이전
시점의 상태를 현재로 고정하지 않는다. 다른 Round의 상태·우선순위나 자동 dependency gate를
R015에서 변경하지 않는다.

<!-- key: id=key.work.keystone-consumer-goal-effectiveness-review.order.improvement-candidates refs=key.topic.verification key.boundary.scope-control -->
## 합의된 개선 정책

### 초기 안내와 운영 방식

1. 완료된 R025의 정의에 따라 Round·Work·Step·Task를 예시로 설명한 뒤 일반형·스프린트형의
   점검 시점을 비교하고 사용자가 선택하게 한다. Round·Step은 기본이며 Work·Task는 선택적이다.
2. 일반형은 각 Round의 영향 범위를 점검하고 Closed List 길이에 따라 전체 점검을 제안한다.
3. 스프린트형은 하위 Round의 영향 범위를 점검하고 최상위 Round의 종료 Step에서 전체를 점검한다.
   중간 5회 안내는 적용하지 않는다. 전체 점검 Step에 최상위 Round 범위 점검을 포함해 중복을 피한다.
   종료 순서는 전체 점검(최상위 자체 범위 포함) → 결과 반영·후속 기록 → 최상위 Round Closed →
   목록 정리다. 최상위 Closed 이벤트도 목록에 추가하되, 방금 점검한 동일 종료 건은 처리한 것으로
   정리한다. 다른 병렬 추가 항목과 재개 후 재종료 건까지 제거하지 않는다.
4. 신규 프로젝트는 Init에서, 기존 프로젝트는 업데이트 후 첫 Round 생성·종료 등 정책이 필요한
   시점에 한 번 설명하고 선택받는다. 선택은 R024의 단일 상태 파일에 보존하고 사용자 변경 요청이
   있을 때 바꾼다. 단순 문서 읽기나 매 작업마다 다시 묻지 않는다. 이는 후속 적용 정책이다.

사용자 안내는 [작업 구성·운영 방식 고정 안내문](templates/work-structure-and-review-mode.ko.md)의
출력 본문을 그대로 사용한다. 2026-10-13 사용자가 승인한 관계도 → 단위 사용법 → 실제 예시 →
운영 방식 선택 순서를 보존하며, 문구·트리·굵기·역할 표기와 선택 질문을 임의 재작성하지 않는다.
전문은 이 작업서에 중복 보관하지 않는다. 후속 Init·기존 프로젝트 안내 연결의 수용 조건에는
원본 본문 일치와 Markdown 줄바꿈 보존을 포함한다.

### 라운드 점검

1. Round 생성 시 작업서에 라운드 정합성 점검 Step을 편성해 사용자가 범위와 결과를 인지하게 한다.
2. 해당 기능의 수락된 의도·결정이 작업서·기준서·코드 연결에 일관되게 반영됐는지 확인한다.
   작업서에 쓰였다는 이유만으로 기준서를 자동 변경하지 않는다.
3. 범위는 그 Round의 기능·변경·관련 연결과 연결 유효성을 확인하는 데 필요한 상대편까지다.
   관련 없는 영역 전체를 검사하지 않는다.
4. 기준 변경 또는 근거 있는 no_change, 중요한 구현 연결, 이동·삭제·대체 후 관계와
   보류·후속 사항을 확인한다. 단순 ID 검사에 한정하지 않는다.
5. 진행 중에는 기존 문서·연결을 기본적으로 신뢰한다. 기준서 변경의 국소 영향 파악과 발견된
   문제 대응은 작업 자체에 포함하되 반복 전체 정합성 검사로 확대하지 않는다.

### 전체 점검과 Closed List

1. 전체 점검은 프로젝트의 선언된 메타데이터·그래프 연결을 검사하고 중요한 기준서–코드
   관계의 의미·누락도 검토한다. 코드 정상 동작이나 테스트 통과 여부는 이 점검의 대상이 아니다.
2. R024가 통합할 단일 상태 파일에서 `closed_list`와 `full_check_wait_for`를 함께 관리한다.
   별도 점검 상태 파일이나 R015 전용 schema version은 추가하지 않고 R024 저장 계약을 따른다.
   상위·하위 Round의 Closed 이벤트를 종료 사유와 관계없이 Closed List에 추가한다.
   Complete는 작업 완료, Closed는 관리 종료이며 서로 다르다.
   Round 재개 시 Closed List에 해당 항목이 있으면 제거하고 없으면 그대로 둔다. 대기 목록은
   유지하며 재종료 시 Closed List에 다시 추가한다. 과거 Closed 항목으로 재개된 대기를 해소하지 않는다.
3. `full_check_wait_for`는 기본적으로 빈 배열이며 전체 점검을 기다려야 할 Round 식별자만
   저장한다. open/closed 상태는 중복 저장하지 않는다.
4. 각 Round의 Closed 이벤트에서 Closed List에 항목을 추가한 뒤 안내 조건을 판단한다.
   대기 배열이 비어 있으면 일반형의 기존 규칙대로 양수인 목록 길이가 5의 배수일 때 안내한다.
   거절하면 목록을 유지하고 다음 5의 배수에서 안내한다. 스프린트형의 기본 종료 점검은 유지한다.
5. 대기 배열에 값이 있으면 5의 배수 안내보다 대기 조건을 우선한다. Closed List는 계속 누적하되,
   대기 항목이 모두 Closed List에 포함되기 전에는 전체 점검 안내를 하지 않는다.
   모두 포함되면 개수와 관계없이 안내한다. 거절해도 두 목록을 유지하므로 이후 Round가 Closed될
   때마다 같은 조건을 다시 판단해 안내한다. 별도 count·마지막 안내 위치·거절 상태는 두지 않는다.
   단순 조회·세션 재개로 안내를 반복하지 않는다. 여기서 완료 조건은 Complete가 아니라 Closed다.
6. 사용자는 주기 이전에도 전체 점검을 요청할 수 있다. 일반형의 전체 점검은 별도 Round나 Step을
   만들지 않고 범위 안내·동의·결과 보고로 가시화한다.
7. 점검 시작 시 새 스냅샷과 두 목록의 대상 항목을 고정한다. 점검 대상은 대기 Round만이 아니라
   스냅샷의 Closed List 전체다. 전체 점검 완료 시 이번에 점검한 Closed 항목과 해소된 대기
   항목만 제거한다. 점검 중 추가된 Closed 항목·새 대기 조건은 보존한다. 추가 항목이 없다면
   두 배열은 비워진다. 부분 점검·보류에서는 제거하지 않는다.
8. Closed List는 점검 문맥의 출발점이다. 전체 연결 검사 범위를 해당 Round로만 제한하지 않는다.
   취소·생략도 작업서를 확인하되 구현 완료로 간주하지 않는다.
9. 단일 파일의 실제 필드 배치와 종료 재시도·동시 갱신 처리는 R024의 상태·사건 계약에 맞춘다.
   점검 중 같은 Round가 재개·재종료되면 새 Closed 항목을 이전 점검 결과로 제거하지 않는다.
10. 스프린트 종료에서는 위 종료 순서에 따라 방금 점검한 최상위 Round의 Closed 건도 정리한다.
    이는 점검 시작 목록 밖의 임의 항목을 제거하는 허용이 아니라, 전체 점검에 포함된 최상위 자체
    범위의 동일 종료 건에만 적용하는 규칙이다.

### 점검 순서와 병렬 작업

1. 전체 점검 직전에 파일 수정을 잠시 멈추고 현재 저장소에서 관리할 소스·문서·상태 변경을
   진행 중인 변경까지 포함해 커밋한다. 그 커밋과 두 목록을 고정해 별도 점검 워크트리를 만든 뒤
   원래 공간의 병렬 작업을 재개한다. Round 종료마다 커밋을 강제하지 않는다.
   이 커밋은 스냅샷 보존이며 포함된 작업의 완료·수락이 아니다. 비밀정보·임시 산출물을 무조건
   추가하거나 커밋 검사 실패를 강제로 우회하지 않는다.
2. Closed List 작업서에서 변경 의도·수락 결정을 읽고 관련 기준서 반영을 대조한 뒤,
   기준서를 바탕으로 프로젝트 전체 연결을 확인한다.
3. 참조 대상을 입력 범위에서 찾지 못하면 현재 저장소의 연결된 문서·대상을 실제로 찾아 대조한다.
   검사 입력 밖이라는 이유만으로 끊어진 연결로 판정하지 않는다. 무관한 참조까지 재귀적으로
   모두 읽지 않으며 해당 연결의 판단에 필요한 범위만 확장한다.
4. 진행 중 작업은 기준서 등에 이미 반영된 변경이 기존 작업서·수락 결정과 충돌하는지를
   필요한 범위에서 확인한다. 아직 없는 구현·연결의 완결성을 철저히 추적하지 않으며 그 부재만으로
   점검을 막지 않는다. 해당 작업이 Closed되면 이후 전체 점검의 정식 대상이 된다.
5. 관련 기준·코드·관계가 변하지 않은 기존 점검 결과는 재사용한다. 의미 검토는 변경된 기능,
   공통 기준, Round 사이 연결과 누락 의심 지점에 집중하고 실제 검토·재사용·미확인 범위를 밝힌다.
6. 과거 실행 워크트리 locator는 이력이다. 종료 작업 점검을 위해 해당 경로를 따라가거나,
   삭제된 경로를 정합성 결함으로 보고하거나, 기록을 일괄 고치지 않는다. 실행 재개와 현재 소스의
   점검은 다른 절차다. 이 방향을 Reader의 현행 targeted navigation 계약과 후속 정합화한다.
7. 점검 결과는 고정한 커밋 시점에 한정한다. 필요한 수정 사항을 정리하고 현재 작업 공간과
   대조한다. 관련 부분이 그대로면 수정 사항을 반영하고, 달라졌다면 변경된 관련 부분만 다시
   확인한다. 의미 판단이 필요하거나 수정 범위가 커졌다면 이유·영향·선택지를 사용자에게 설명한다.
   점검본으로 파일이나 상태 파일 전체를 덮어쓰지 않는다. 독립된 점검 워크트리에서 진행 중 Work를
   재개하지 않는다.
8. 결과 반영과 사용자 판단·후속 처리 기록을 마친 뒤 이번에 처리한 Closed 항목과 해소된 대기
   항목만 제거한다. 점검 중 새로 추가되거나 재개 후 재종료된 항목은 보존한다. 반영·기록이
   미완료인 상태에서 목록부터 제거하지 않는다.

### 발견 사항·완료·재개

1. 단순 상태·참조 불일치는 점검 안에서 수정한다. 기준 의미나 구현 변경은 이유·영향·선택지를
   설명하고 사용자 판단을 받는다. 이 정책의 수락은 현재 Uptendo 수정 승인이 아니다.
2. 수정 범위가 크면 발견 문제, 변경 대상, 영향, 별도 작업이 필요한 이유를 설명하고
   “Round를 생성할까요?”라고 제안한다. 부모·하위 배치는 사용자가 선택하며 기존 계층 제한을
   지킨다. 생성 승인을 구현 착수 승인으로 해석하지 않는다.
3. 작업서·기준서에 기록된 보류·후속 처리 결정이 현재 근거와 맞으면 그대로 존중한다.
   별도 문제 목록을 중복 관리하거나 같은 결정을 반복해서 묻지 않는다. 근거·영향 변화 시 다시 판단을 요청한다.
4. 모든 문제 해결이 점검 완료의 조건은 아니다. 정한 범위를 확인하고 발견 사항을 수정 완료,
   사용자 결정 대기 또는 후속 작업으로 정리하면 점검 자체는 완료할 수 있다.
5. 도구 오류·접근 불가 등으로 필요한 범위를 확인하지 못하면 부분 점검으로 남기고 목록을 유지한다.
   다음에는 미확인 범위부터 재개하되 이미 확인한 부분도 관련 근거가 바뀌면 재확인한다.
6. 고정 스냅샷의 Closed List 전체를 점검하고 발견 사항을 정리하면 점검을 완료할 수 있다.
   진행 중인 작업의 미완성은 완료를 막지 않으며, 기존 내용과의 충돌 여부만 필요한 범위에서 본다.
7. 진행 중인 큰 변경 때문에 Closed 작업의 정합성을 판단하기 어렵다면 이번 전체 점검을 보류한다.
   보류 이유와 관련 Round를 설명하고 `full_check_wait_for`에 등록한다. 두 목록을 유지하며
   대기 Round가 모두 Closed된 뒤 안내·동의를 거쳐 새 스냅샷의 Closed List 전체를 점검한다.
8. 종료 전 전체 점검을 수행 중인 최상위 Round 자신을 `full_check_wait_for`에 넣지 않는다.
   자기 Closed를 기다리느라 종료 점검을 완료하지 못하는 순환 대기를 방지한다. 보류 원인이 그
   Round 자체의 미완료 변경이면 해당 변경을 마친 뒤 종료 점검을 재개한다.

## R021 시뮬레이션과 후속 진단 — 2026-10-13

소비 저장소 `/Users/joung/workspace/uptendo`, HEAD `c5e914d3fb197e05020816e8ac2197b2f7c3fbf7`와
당시 로컬 문서를 읽기 전용으로 검사했다. 합의한 점검 정책을 시험한 것이며 고정 커밋의 별도
점검 워크트리를 실제 생성한 실행은 아니다. Closed List도 아직 없어 상태 분류를 대신 사용했다.
R021 하위 Work는 complete/accepted 18, complete/pending 4, in_progress/pending 1,
planned/pending 1이었다. 이 분류를 실제 Closed 이벤트나 최종 수용으로 치환하지 않는다.

- R021 문서·기준서 198개와 표본 코드 4개를 처리했다. 202개 파일의 검사 전후 바이트는 동일했다.
  의미 대조는 V·U·W 중심이며 R021 전체 의미 검토나 프로젝트 전체 점검 완료가 아니다.
- V의 수락된 무효 푸시·Shop 선택 정보 정책이 알림·외부 연동 기준서에 반영됐고 대응 코드도
  찾았다. U의 표시·정렬·페이저 기준 반영은 확인했지만 Work 수용 대기는 유지했다.
- W의 기준 선반영은 S01 수용·S03 진행 기록으로 설명됐다. HTTP 400 원인 미확정도 기록돼 있어
  이를 곧바로 기준서 오류로 판정하지 않았다. 당시 W 실행 위치를 읽은 방식은 위 현재 저장소
  기준 원칙으로 교정하며, 이후 점검의 필수 절차로 재사용하지 않는다.
- 표본 코드 4개에 그래프 owner ID가 없었지만, AI가 파일명·작업서·기준서로 연결할 수 있었다.
  메타데이터 부재 자체를 제품 결함이나 일괄 보강 대상으로 판정하지 않는다.
- 제한 입력의 미해결 참조 416건은 중복 제외 122개 대상이었다. 현재 `00_docs` Markdown 899개에서
  owner를 찾아 122개 모두 유일한 소유 문서를 확인했다. 연결된 R017-D·F aggregate Progress도
  complete/accepted였다. 416건은 끊어진 연결 수가 아니며 모든 관계의 의미 검토 완료도 아니다.
- Linker의 R021-B·G·J·K Step 부재 진단 12건은 본문에 정의된 Step 대신 metadata의 `step_ref`만
  등록한 결과였다. 본문 정의를 메모리의 registry에 보충하는 원인 분리 실험에서 12→0건으로
  줄었다. 원천 코드·문서를 수정한 패치나 운영 수정 검증은 아니다.
- 참조 문서를 확장하면 그 문서 자체의 진단도 추가될 수 있다. 원래 R021의 12건과 확장된 검사
  전체 진단을 혼동하지 않으며 범위·도구 해석 문제를 소비 프로젝트 결함과 분리한다.

재확인 locator(모두 소비 저장소 상대 경로):

- `00_docs/works/r021-post-release-mobile-patches/r021-V/expected-delivery-and-shop-metadata-outcomes/key-work-expected-delivery-and-shop-metadata-outcomes.md`
- 같은 Work의 `key-progress-align-expected-outcomes.md`
- `00_docs/standards/14_key-notification-standard.md`의 §6·R021-V 절
- `00_docs/standards/08_key-external-integration-standard.md`의 R021-V 절
- `00_docs/standards/05_key-backoffice-standard.md`의 R021-U·W 절
- `00_docs/works/r021-post-release-mobile-patches/r021-W/preview-entry-and-augmentation-failure-tracing/key-progress-implement-preview-tracing.md`
- `00_docs/works/r021-post-release-mobile-patches/r021-B/dashboard-product-ranking-visual-hierarchy/key-work-dashboard-product-ranking-visual-hierarchy.md`의 S01~S03
- Keystone 구현 `skills/keystone-linker/scripts/graph_runtime/dependency.py`의 `evaluate_dependency_sources`

## Step 연결의 합의와 미확정 항목

2026-10-13 사용자 합의: 최소 메타데이터로 Step 정의를 공유하고 Reader·AI가 의미를 판단한다.

1. Author는 새로 생성하거나 수정하는 Step의 정의 위치에 최소 식별 메타데이터를 함께 관리한다.
   사용자가 직접 관리할 의무나 별도 Step 정의 목록을 만들지 않는다.
2. Linker는 정의의 존재와 참조 대상, 연결 누락·충돌을 확인한다. 진행 기록의 `step_ref`를
   Step 정의로 간주하지 않는다. 본문 표현의 의미 해석을 계속 확대하는 방향은 채택하지 않는다.
3. Reader·AI는 본문을 읽고 Step의 목적·범위와 기준서·코드 연결의 내용 정합성을 판단한다.
4. 기존 문서의 메타데이터 부재만으로 결함을 확정하지 않는다. 필요한 경우 Reader·AI가 본문에서
   정의를 확인하고, 해당 문서를 수정하거나 점검 중 보완할 때 최소 메타데이터를 반영한다.
   기존 문서 전체를 일괄 보강하지 않는다.
5. Linker는 실제로 없는 참조와 입력에서 아직 정의를 식별하지 못한 참조를 구분한다.
   본문 확인 결과를 도구의 검증 완료로 혼동하지 않고 확인 근거와 범위를 구분한다.

역할 분담과 점진적 적용 원칙은 확정했다. 구체적인 필드·표기와 호환 처리는 R025 정의 및
기존 metadata 계약에 맞춰 후속 구현에서 설계한다. 이 합의는 runtime 구현 착수 승인이 아니다.

## 최종 수용안 — 후속 구현 범위

아래는 사용자 합의를 적용할 구현 묶음 제안이다. 새 Round·Work의 생성이나 실행 승인이 아니며,
R015 최종 수용과 실제 구현 착수는 구분한다. R018의 탐색 개선, R024의 단일 상태 관리,
R025의 단위 정의를 재구현하지 않고 각 결과에 연결한다.

| 묶음 | 목표·변경 범위 | 완료 조건 |
|---|---|---|
| A. 안내·작업 편성 | Init의 고정 안내문, 최초 운영 방식 선택, Author의 라운드/전체 점검 Step, 최소 Step 정의 metadata와 Reader·Linker 역할 계약 | 승인 안내문 그대로 출력, 신규·기존 첫 적용 선택, 필수 Step·선택 Work/Task 보존, 실제 Step 부재와 정의 미식별 구분 |
| B. 상태·안내 조건 | R024 단일 상태 파일의 운영 방식·두 목록, Closed/재개 사건 연결, 안내 판단과 목록 정리 | 5배수·대기 우선·매 Closed 재안내·재개 제거가 일관되고 재시도·병렬 변경에서 유실·중복 처리가 없음 |
| C. 점검 실행·결과 반영 | 현재 변경 커밋·점검 워크트리, Closed 작업서→기준서→연결 대조, 진행 중 충돌 확인, 보류·재개·국소 반영과 스프린트 종료 | 고정 스냅샷의 범위·한계를 보고하고, 현재 변경을 보존하며 실제 처리한 종료 건만 정리 |

권장 적용 순서는 각 묶음의 관련 기준 정합화 후 A·B를 준비하고, C에서 통합 흐름을 검증하는
것이다. B의 실제 저장 접점은 R024의 단일 파일 계약에 맞춘다. 설치·기존 프로젝트 이전은
위 구현의 검증 뒤 별도 적용 범위로 구분한다. 묶음을 Round로 나눌지, 같은 Round의 Work·Step으로
편성할지는 후속 생성 시 사용자 결정과 R025 기준에 따른다.

### 정책 수용 시나리오

다음은 문서상 입력·기대 결과 대조이며 runtime 테스트 통과 기록이 아니다.

| 상황 | 기대 결과 |
|---|---|
| 신규 Init / 기존 프로젝트 첫 정책 적용 | 고정 안내문 출력 후 한 번 선택하고 단일 상태 파일에 보존. 일상 조회에서 재질문하지 않음 |
| 작은 작업 / 선택적 Work·Task | Round·Step 기본 구조 유지. AI Work 생성 시 이유·범위 안내. Task 사용자 관리 의무 없음 |
| Step metadata 없는 기존 문서 | 본문 확인 필요로 구분. 실제 Step 부재로 단정하거나 전수 보강하지 않음 |
| 일반형, 대기 없음, 목록 길이 4→5 / 거절 후 9→10 | 각 5·10번째 Closed에서 안내. 0개나 단순 조회에서는 안내하지 않음 |
| 주기 전 수동 전체 점검 | 시작 시 Closed List 전체를 처리하고 완료한 항목만 제거. 남은 목록 길이로 이후 주기 판단 |
| 대기 목록 일부 미충족 / 전부 충족 | 미충족 동안 5배수 안내 억제. 모두 Closed List에 포함되면 개수와 무관하게 안내 |
| 대기 충족 안내 거절 후 다음 Closed | 두 목록 유지, 다음 Closed마다 조건을 다시 평가해 안내 |
| 종료 사유 complete/skipped/cancelled/superseded | 모두 Closed List에 추가하되 취소·생략을 구현 완료로 해석하지 않음 |
| Round 재개 / 재종료 | Closed List에서 해당 항목 제거 / 재추가. 대기 목록은 유지 |
| 점검 중 다른 Round 종료 / 같은 Round 재개·재종료 | 새 종료 건은 보존. 시작 시 Round ID만 같다는 이유로 새 건을 제거하지 않음 |
| 진행 중 변경의 구현·연결 미완성 | 기존 내용과 충돌만 필요한 범위에서 확인. 미완성 자체로 전체 점검을 막지 않음 |
| 큰 진행 중 변경으로 Closed 작업 판단 불가 | 전체 점검 보류, 담당 Round 대기 등록, 두 목록 유지. 현재 최상위 Round 자신은 등록하지 않음 |
| 도구 오류·접근 불가 / 기존 연결 문서가 검사 입력 밖 | 전자는 부분 점검·목록 유지. 후자는 필요한 상대편을 찾아 확인하고 즉시 결함으로 단정하지 않음 |
| 점검 후 현재 관련 부분 변경 | 해당 부분만 재확인하고 의미 판단·범위 확대 시 사용자에게 설명. 파일 전체 덮어쓰기 금지 |
| 점검 결과 반영·후속 기록 미완료 / 완료 | 미완료면 목록 정리하지 않음. 완료면 처리한 Closed 항목·해소된 대기 항목만 제거 |
| 스프린트 최상위 종료 | 최상위 범위 포함 전체 점검 → 결과 반영 → 최상위 Closed → 동일 종료 건 정리. 병렬 항목은 보존 |

### 후속 설계에서 구체화할 사항

- 최소 Step metadata의 필드·표기는 기존 metadata 계약과 R025 정의를 따른다.
- 두 목록의 필드 배치·종료 사건 재시도·동시 갱신·동일 Round 재종료 구분은 R024 사건·쓰기 계약을
  활용한다. 별도 count·마지막 안내 상태·독립 점검 상태 파일을 만들지 않는다.
- 이전 점검 재사용은 기존 기록에서 점검 범위·기준 커밋·판정과 관련 입력의 변화를 확인할 수
  있는 경우에 한한다. 근거가 부족하면 필요한 범위를 재확인한다. 새 영구 evidence 체계는 요구하지 않는다.
- 구체적 설계가 위 사용자 정책을 바꾸거나 새로운 상태·관리 의무를 요구하면 해당 지점만 다시
  사용자에게 설명한다. 단순 구현 방식 선택을 위해 이미 합의한 정책을 반복 질문하지 않는다.

### R015 최종 수용 경계

이번 수용 대상은 개발 관리 개선 정책, 고정 안내문, 소비 사례의 근거·한계, 위 후속 구현 범위와
수용 시나리오다. 실제 구현·설치·Uptendo 이전 완료나 runtime 테스트 성공을 의미하지 않는다.
사용자의 최종 수용 후 R015의 Step·Work 상태와 종료를 해당 상태 계약에 따라 정리한다.
이 문서 개정만으로 상태를 변경하거나 후속 Round를 자동 생성하지 않는다.

<!-- key: id=key.work.keystone-consumer-goal-effectiveness-review.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- 개발 관리 흐름의 효과성과 반복 확인 비용 평가
- 위 사용자 합의·소유권·R021 근거와 한계의 R015 문서 반영
- 라운드/전체 점검, Init 안내, Closed List, 진행 중 작업·후속 처리의 정책과 수용 조건
- 최소 Step metadata와 역할 분담·점진적 보완 합의 및 후속 구현 범위 분리
- R015 Work Order·Progress와 필요한 R015 navigation 정합화

Exclude:

- Keystone 공통 기준·결정·skill/runtime/code/test의 직접 수정과 설치
- Uptendo 문서·코드·운영 데이터·작업 상태 수정 및 이 Round에서의 실제 전체 점검 완료 선언
- R018·R024·R025 및 다른 Round의 범위·상태·우선순위 변경
- 토큰·시간 history 수집 runtime, metadata 일괄 보강, 새 영구 evidence 체계
- browser·Playwright·screenshot·publish·배포

<!-- key: id=key.work.keystone-consumer-goal-effectiveness-review.order.plan refs=key.topic.work-sequence key.topic.verification -->
## 실행 계획

| Step | 상태 | 작업 범위 | 완료 경계 |
|---|---|---|---|
| R015/S01 | complete / accepted | 소비 사례·사용자 합의·시뮬레이션을 관리 흐름 개선 초안으로 정합화 | 사실·정책·권장안·미정 사항과 다른 Round 책임이 구분되고 검토 가능하다 |
| R015/S02 | complete / accepted | 남은 결정과 적용 범위·수용 시나리오를 확정 | 사용자가 최종 Work Order를 수용하고 후속 구현 승인과 분리된 완성본이 된다 |

<!-- key: id=key.work.keystone-consumer-goal-effectiveness-review.order.completion refs=key.topic.verification key.topic.work-recovery -->
## Completion Criteria

<!-- key: id=key.acceptance.keystone-consumer-goal-review.goal -->
- `R015-CC-01` 개발 관리 효과성과 비용 효율성, 영구 목표 하한과 고비용 승인 경계가 보존된다.
<!-- key: id=key.acceptance.keystone-consumer-goal-review.evidence -->
- `R015-CC-02` 초기 관찰·R021 시뮬레이션·재현 결과가 locator와 한계에 연결되며 전체 성공으로 과장되지 않는다.
<!-- key: id=key.acceptance.keystone-consumer-goal-review.ownership -->
- `R015-CC-03` R018 탐색·R024 상태·R025 정의·소비 프로젝트 정리와 R015 관리 정책의 책임이 분리된다.
<!-- key: id=key.acceptance.keystone-consumer-goal-review.priority -->
- `R015-CC-04` 합의와 권장안·미정 항목을 구분하고 후속 구현 후보가 독립적인 범위·수용 기준을 가진다.
<!-- key: id=key.acceptance.keystone-consumer-goal-review.cold-start -->
- `R015-CC-05` 초기 안내부터 작업 편성·진행·라운드/전체 점검·부분 재개까지 위 시나리오의 판단 기준이 정의된다.
<!-- key: id=key.acceptance.keystone-consumer-goal-review.scope -->
- `R015-CC-06` 코드 동작 검증과 연결 점검, 문서 최종화와 실제 구현·이전의 승인 범위가 분리된다.
<!-- key: id=key.acceptance.keystone-consumer-goal-review.user-acceptance -->
- `R015-CC-07` 남은 결정을 해소한 최종 Work Order를 사용자가 완성본으로 수용한다.

<!-- key: id=key.work.keystone-consumer-goal-effectiveness-review.order.verification refs=key.topic.verification -->
## Verification

1. Project 목적과 `DEC-WORKS-029`, 최신 R018·R024·R025의 소유 범위에 맞게 정책을 대조한다.
2. 사용자 합의와 추천·미확정을 구분하고 현재 runtime에 이미 적용됐다고 표현하지 않는다.
3. 위 후속 구현 표의 시나리오로 정상·거절·중간 점검·병렬 추가·부분 실패·진행 중 변경 사례를 검토한다.
4. 연결 문서 존재·의미, scope 경계와 도구 오진을 분리하고 sample 결과를 전체 완료로 확대하지 않는다.
5. 변경 문서의 metadata·Markdown link·기존 ID 보존과 scoped `git diff --check`를 확인한다.
6. 상태 전이가 없으면 Work State·종료 정합화는 반복 실행하지 않는다. metadata/relation 변경이
   있을 때만 해당 범위 Linker 확인을 수행한다. 문서 개정만으로 package·installer·브라우저 검증을 실행하지 않는다.

<!-- key: id=key.work.keystone-consumer-goal-effectiveness-review.order.stop refs=key.boundary.stop-condition key.boundary.scope-control -->
## Stop Conditions

1. 미정 정책을 사용자 결정 없이 확정해야 최종화할 수 있다.
2. 새로운 소비 프로젝트 근거가 핵심 판정을 바꾼다.
3. R015 문서 밖 기준·runtime·소비 프로젝트 수정이나 다른 Round 범위 변경이 필요해진다.
4. 점검 비용보다 metadata·문서 형식 보강 자체가 주목적이 된다.
5. 현재 점검 결과로 미래 변경까지 보장하거나 도구 미확인을 source 오류로 확정해야 한다.

## 현재 다음 행동

검토 결과는 수용됐다. R015-A 작업서에 구현·검증을 편성했으며, 실행 요청 시 해당 계획을 따른다.
