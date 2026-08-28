---
doc_type: work_order
created_at: "2026-08-26"
document_lifecycle: active
approval: {state: pending}
work_status: planned
key:
  id: key.work.keymeta-bounded-discovery.order
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.context-readiness
    - key.topic.artifact-graph
    - key.topic.keystone-metadata
    - key.topic.skill-contract
    - key.topic.verification
    - key.boundary.scope-control
    - key.standard.project
    - key.standard.artifact.graph
    - key.standard.skill.linker
  relations:
    produces:
      - key.code.linker.context-readiness
      - key.code.linker.metadata-parser
---

# Keymeta-First Bounded Discovery 작업서 및 Change Set

## 문서 상태

이 문서는 키메타 중심 bounded discovery를 위한 `planned / pending` Work Order다. Round 생성만
승인됐으며 사용자의 별도 진행 요청 전에는 기준서·runtime·skill source·test 구현을 시작하지
않는다.

<!-- key: id=key.work.keymeta-bounded-discovery.order.goal refs=key.section.goal key.topic.context-readiness key.topic.keystone-metadata -->
## Goal

키메타가 단순히 repository-wide scan 뒤 발견되는 metadata가 아니라, 선택된 Work·문서·artifact를
출발점으로 필요한 owner/ref/source만 찾고 확장하는 탐색 계약으로 실제 동작하게 한다.

Routine Work preparation과 context readiness는 anchor, 명시적 locator, Work가 선언한 relation,
fresh bounded index evidence와 확인된 source path set을 사용해 필요한 context를 복구하고 끝낸다.
Cache miss, stale index 또는 owner 미확인을 이유로 자동 full repository graph reconstruction으로
확장하지 않는다. Full scan은 명시적 graph audit, release verification 또는 실제 scope conflict를
조사할 때만 별도 mode로 실행한다.

정확성 하한은 유지한다. Bounded 결과가 불완전하면 `implementation unavailable`, unresolved owner,
stale index 또는 incomplete coverage를 정직하게 보고하며, source authority·raw-byte digest·relation
admission·diagnostic 의미를 비용 절감 목적으로 낮추지 않는다.

<!-- key: id=key.work.keymeta-bounded-discovery.order.user-direction refs=key.topic.context-readiness key.boundary.scope-control -->
## 수락된 사용자 방향

1. 목표는 `never scan`이 아니라 `no implicit full scan`이다. 전체 repository 검증 기능을 없애지
   않고 routine preparation에서 자동 실행하지 않는다.
2. Discovery는 다음 세 mode를 구분한다.
   - `targeted`: 이미 알고 있는 Work/document/artifact path, raw-byte digest와 relation에서 시작해
     필요한 source만 확장한다. Routine preparation의 기본 mode다.
   - `lookup`: bounded evidence에 target ID의 owner path가 없을 때 exact-ID owner 검색을 수행한다.
     검색 범위와 비용을 응답에 노출하며 graph 전체 reconstruction과 구분한다.
   - `audit`: repository 전체 owner/ref/relation/duplicate/coverage를 검증한다. 명시적 graph audit,
     release verification 또는 scope conflict에서만 사용한다.
3. `targeted` 결과는 repository completeness를 주장하지 않는다. 필요한 owner를 찾지 못하면
   `owner_unresolved`, `implementation_unavailable` 또는 `bounded_coverage_incomplete`처럼 stable
   diagnostic으로 끝내고 자동 `audit`으로 승격하지 않는다.
4. Anchor는 가능한 경우 stable ID뿐 아니라 source path와 raw-byte digest를 포함한다. Stable ID에
   path를 결합해 identity/locator 분리 원칙을 깨지 않는다.
5. Cache/index는 빠른 locator 후보로만 사용하고 source authority가 되지 않는다. 새 authoritative
   registry나 repository-generated index가 필요하면 구현 전에 별도 사용자 결정을 받는다.
6. 비용 절감은 복구 정확성·권위·추적성·scope 안전성과 근거 정직성을 낮추는 방식으로 달성하지
   않는다.

<!-- key: id=key.work.keymeta-bounded-discovery.order.problem refs=key.topic.context-readiness key.topic.artifact-graph -->
## 문제 정의와 관찰 근거

1. 현재 repository scope discovery는 include/exclude와 ignored directory를 적용하기 전에 전체
   tree를 열거해 bounded request도 대규모 worktree·build·dependency tree의 탐색 비용을 낸다.
2. Generic code adapter는 문자 단위 루프에서 남은 source substring을 반복 생성하고, 하나의
   source를 diagnostics·metadata·refs·source views 경로에서 여러 번 lexical scan한다.
3. `include_source_views`는 동일 discovery snapshot을 사용하지만 graph reconstruction을 위해
   source metadata를 다시 parse하고 cache를 우회한다.
4. 호출자는 anchor 결과만 필요해도 전체 owners·refs·diagnostics·typed graph를 materialize한 뒤
   응답 이후에 필터링한다.
5. 실제 소비 저장소의 323KB Kotlin test source는 metadata anchor 하나를 찾는 adapter scan 1회에
   약 9.5초가 걸렸고, 23만여 filesystem entry 중 22만여 ignored entry를 방문한 뒤 bounded 35개
   source를 고르는 데 약 7.3초가 걸렸다.

이 evidence는 성능 수치만의 문제가 아니라 키메타와 progressive bounded discovery의 intended
behavior가 runtime에서 지켜지지 않는 문제를 보여준다.

<!-- key: id=key.work.keymeta-bounded-discovery.order.invariants refs=key.topic.keystone-metadata key.boundary.scope-control key.topic.verification -->
## 제품 불변조건

1. Source document, 키메타, code anchor와 repository evidence가 권위이며 cache/index는 비권위다.
2. 키메타 anchor는 source admission 이후의 label이 아니라 discovery seed와 expansion evidence다.
3. Routine readiness는 full repository coverage를 성공 조건으로 요구하지 않는다.
4. `targeted` 결과는 bounded completeness만 주장하며 repository completeness를 추론하지 않는다.
5. Bounded source omission과 unresolved owner는 stable diagnostic으로 노출하며 pass로 축약하지
   않는다.
6. Exact-ID `lookup`은 실제 검색 범위를 노출하고 full graph reconstruction과 구분한다.
7. Full repository validation 기능은 제거하지 않고 명시적 `audit` mode로 격리한다.
8. 동일 source bytes에 대한 node, ref, relation, lifecycle, locator와 diagnostic 결과는 최적화 전후
   의미가 같아야 한다.
9. Source view는 동일 reconstructed snapshot을 재사용하고 source generation에 결속한다.
10. Cold start에서도 외부 폴더 권한, persistent registry 또는 repository write를 자동 요구하지
   않는다.

<!-- key: id=key.work.keymeta-bounded-discovery.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- Project·Artifact Graph·Linker 기준의 keymeta-first bounded discovery 의미 정합화
- selected Work/document/artifact ID와 locator를 이용한 seed resolution
- `targeted | lookup | audit` discovery mode와 명시적 mode transition
- relation type과 caller intent에 따른 bounded source expansion
- docs-first owner/ref lookup과 lazy repository artifact lookup의 실제 scope 분리
- cold/missing/stale cache의 bounded fail-soft 결과와 full-scan escalation 조건
- include/exclude와 ignored directory를 traversal 전에 적용하는 path discovery
- source adapter의 position-based lexical scan과 동일 source parse 결과 재사용
- owner/ref, typed graph와 source view가 하나의 immutable snapshot을 공유하는 projection
- anchor/query 입력과 bounded 응답 shape 또는 기존 readiness wire의 호환 확장
- 대형 Kotlin source, ignored tree, stale cache와 selected-Work fixture 회귀 테스트
- repository-local Linker/Reader skill source, graph runtime과 관련 contract test
- R018 Work/Progress와 필요한 navigation source 정합화

Exclude:

- R015 source, Goal, scope, 상태, 우선순위와 중복 범위 정리
- 소비 프로젝트 source 수정
- 키메타·code anchor·companion의 canonical 의미를 약화하는 최적화
- full repository audit와 release validation 기능 삭제
- 모든 source를 항상 포함하는 중앙 authoritative registry
- 승인 없는 persistent storage, daemon, background watcher 또는 repository-generated index
- unrelated Work State, dependency, transaction, finalization과 worker orchestration 변경
- browser, Playwright, screenshot, publish와 installer 작업

<!-- key: id=key.work.keymeta-bounded-discovery.order.execution-plan refs=key.topic.work-sequence key.topic.verification -->
## 실행 계획

| Step | 상태 | 변경 범위 | 완료 경계 |
|---|---|---|---|
| R018/S01 | planned | Project·Artifact Graph·Linker 기준, 필요한 결정과 R018 source | `targeted / lookup / audit`, no-implicit-full-scan, bounded completeness와 correctness 하한이 accepted 의미로 정렬된다 |
| R018/S02 | planned | Linker scanner/index/query/readiness와 Reader·Linker skill contract | routine readiness가 anchor에서 bounded source set을 만들며 cache miss만으로 full scan하지 않는다 |
| R018/S03 | planned | language adapter, metadata parse, source view projection과 focused tests | 동일 의미를 유지하면서 substring copy, 반복 lexical scan과 snapshot 재구성 중복이 제거된다 |
| R018/S04 | planned | affected suites, self-host fixture와 read-only consumer-scale benchmark | bounded/full mode 분리, correctness parity, 성능 기준과 accepted standard↔implementation 정합성이 검증된다 |

<!-- key: id=key.work.keymeta-bounded-discovery.order.completion refs=key.topic.verification key.boundary.stop-condition -->
## Completion Criteria

- [ ] `targeted` Work 또는 문서 anchor 요청이 full repository enumeration·parse 없이 bounded
      source set과 freshness evidence를 만든다.
- [ ] Keymeta ID, refs, typed relations와 locator가 실제 discovery seed·expansion evidence로 사용된다.
- [ ] `targeted` 결과는 bounded completeness만 주장하고 unresolved owner·source omission을 stable
      diagnostic으로 반환한다.
- [ ] Exact-ID `lookup`은 검색 범위를 노출하고 full graph reconstruction 없이 owner 후보를
      반환하거나 unresolved로 끝난다.
- [ ] Cache miss·stale·unavailable 상태가 routine request를 자동 repository-wide scan으로 확장하지
      않으며 불완전성은 stable diagnostic으로 보고된다.
- [ ] Full repository scan은 명시적 `audit`·release·scope-conflict mode에서 계속 사용할 수 있다.
- [ ] Ignored directory와 include root는 하위 tree 방문 전에 prune되며 symlink·root escape 경계가
      유지된다.
- [ ] Supported source의 canonical node/ref/relation/diagnostic 결과가 최적화 전후 characterization
      fixture에서 동일하다.
- [ ] 하나의 source는 routine projection chain에서 한 번 lexical parse되고, source views는 같은
      immutable snapshot을 재사용한다.
- [ ] 300KB급 Kotlin anchor fixture의 lexical scan은 현재 기록된 약 9.5초 대비 같은 환경에서
      10배 이상 개선된다.
- [ ] 대규모 ignored tree가 있는 소비 저장소의 selected-Work bounded readiness는 명시된 source
      set과 residual gap을 10초 이내에 반환한다.
- [ ] Repository-local skill/runtime, installed package parity와 관련 focused·package·contract test가
      통과한다.
- [ ] R018 문서, 기준서, 구현과 verification evidence가 일치하고 Main acceptance 전 상태를
      완료로 표시하지 않는다.

<!-- key: id=key.work.keymeta-bounded-discovery.order.verification refs=key.topic.verification key.topic.context-readiness -->
## Verification

1. Characterization fixture로 기존 language surface의 node/ref/relation/diagnostic wire를 고정한다.
2. Instrumented filesystem fixture로 ignored tree와 include root가 traversal 전에 prune되는지
   확인한다.
3. Missing, stale, corrupt와 busy cache에서 routine bounded request가 full scan으로 확장하지 않고
   stable incomplete diagnostic을 반환하는지 검증한다.
4. Selected Work/document/artifact anchor가 direct owner/ref와 필요한 typed relation만 확장하는지
   테스트한다.
5. Unresolved owner가 automatic audit 없이 stable incomplete diagnostic으로 끝나는지 검증한다.
6. Exact-ID lookup이 검색 범위를 보고하고 graph reconstruction을 수행하지 않는지 검증한다.
7. Explicit repository audit가 complete path-set digest와 coverage를 계속 제공하는지 검증한다.
8. 대형 Kotlin/TS/Markdown fixture에서 parse call count와 성능 회귀를 측정한다.
9. Linker affected suite, Reader/Linker contract suite, self-host readiness, compileall과
   `git diff --check`를 실행한다.
10. 접근 가능한 소비 저장소에서는 source를 수정하지 않고 같은 bounded readiness 시나리오를
   재측정한다.

<!-- key: id=key.work.keymeta-bounded-discovery.order.stop refs=key.boundary.stop-condition key.topic.keystone-metadata -->
## Stop Conditions

1. Bounded cold-start owner resolution에 새 authoritative registry 또는 repository-generated index가
   필수라는 결론이 난다.
2. Source correctness를 유지하려면 routine request에서도 repository full coverage가 항상
   필요하다는 accepted 기준 충돌이 발견된다.
3. Cache freshness를 줄이는 방식이 raw-byte source generation 또는 source precedence를 약화한다.
4. Public wire·diagnostic compatibility를 깨는 변경이 별도 migration 결정 없이 필요해진다.
5. 소비 프로젝트 source 수정, external service, daemon, watcher, browser 또는 publish가 필요해진다.
6. S01 기준 정합화 전에 production runtime·skill source 구현이 필요해진다.

## 다음 단계

사용자가 R018 진행을 명시하면 S01에서 accepted 기준과 실제 discovery semantics의 차이를 정리하고,
필요한 정책 결정을 먼저 수락 가능한 상태로 만든다.
