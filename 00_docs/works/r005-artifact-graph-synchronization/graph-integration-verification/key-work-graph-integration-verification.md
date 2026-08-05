---
doc_type: work_order
created_at: "2026-08-05"
status: active
approval: {state: accepted, accepted_at: "2026-08-05", accepted_by: user}
work_status: accepted
key:
  id: key.work.graph-integration-verification.order
  refs: [key.doc.work, key.topic.artifact-graph, key.topic.integration-verification, key.topic.verification]
---

# Graph Integration Verification 작업서

## Goal

Keystone 저장소 안에서 생성한 공개 합성 fixture와 설치 package command만으로 metadata
normalization, graph transaction, skill lifecycle, finalization gate와 규모 대응을 executable
evidence로 검증한다.

## Prerequisite

- R005 S01~S03 accepted

## Verification Layers

1. Parser·adapter unit verification
   - Markdown frontmatter/item, compact/multiline metadata
   - Generic line comment, Kotlin/Java, SQL, XML, YAML, companion metadata
   - Existing flat metadata와 canonical metadata의 동일 graph normalization
2. Graph transaction state verification
   - 정상 attestation/apply/verify
   - Reject, stale baseline, partial apply, validator failure와 resume
3. Synthetic consumer repository end-to-end verification
   - Greenfield document-to-code
   - Existing code with zero anchors and bounded current change
   - Standard change impact propagation
   - Rename/move, removal/replacement
   - Author document patch와 repository patch의 부분 적용
4. Package and CLI verification
   - Installed Linker validator command, JSON diagnostics와 exit code
   - Missing validator, timeout, malformed output, unsupported schema version
   - R004 Author finalization interface 연동
5. Scale and determinism verification
   - 수백·수천 합성 artifact 중 소수 changed seed traversal
   - Required candidate 비누락과 candidate budget
   - Source-only reconstruction과 optional derived cache 결과 일치

## Expected Oracles

- Exact node ID, relation direction, target, evidence와 observed locator
- Expected impact grade와 stale/gap classification
- Expected transaction state와 diagnostic code
- Project graph coverage가 partial이어도 current transaction이 verified일 수 있음
- Required graph sync가 verified가 아니면 finalization complete 불가

## Completion Criteria

- [x] 모든 지원 metadata surface가 expected golden graph와 일치한다.
- [x] 기존·canonical metadata compatibility가 executable evidence로 확인된다.
- [x] Attestation 없는 observed relation과 모든 inferred relation은 자동 적용되지 않는다.
- [x] Rename·move는 ID를 유지하고 locator만 갱신한다.
- [x] Removal·replacement가 orphan active relation을 남기지 않는다.
- [x] Stale baseline과 partial apply가 verified로 오인되지 않는다.
- [x] Current transaction completeness와 project coverage가 구분된다.
- [x] Required candidate가 candidate budget으로 숨겨지지 않는다.
- [x] Installed package CLI와 finalization 연동이 통과한다.
- [x] 모든 검증은 Keystone 저장소 내부 fixture만 사용한다.
- [x] Main이 residual risk를 확인하고 S04와 R005를 수락한다.

## Exclusions

- Uptendo 또는 다른 외부 프로젝트 source, 문서, migration 복사·수정·실행
- 외부 프로젝트 상태나 결과를 R005 acceptance 조건으로 사용
- 실제 프로젝트 graph coverage 또는 성능을 보편적 보장으로 선언

## Stop Conditions

1. S01~S03가 accepted되지 않았다.
2. 검증을 위해 외부 소비 프로젝트 source가 필요하다.
3. 실패 시나리오가 validator의 source edit·semantic decision·acceptance 권한을 요구한다.
4. 합성 규모 검증 결과를 실제 모든 프로젝트의 성능 보장으로 표현해야 한다.
