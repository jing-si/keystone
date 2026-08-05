---
doc_type: work_order
created_at: "2026-08-05"
status: active
approval: {state: accepted, accepted_at: "2026-08-05", accepted_by: user}
work_status: accepted
key:
  id: key.work.artifact-graph-synchronization-standard.order
  refs: [key.doc.work, key.topic.artifact-graph, key.topic.keystone-metadata, key.topic.finalization, key.topic.change-set]
---

# Artifact Graph Synchronization Standard 작업서 및 Change Set

## Goal

기준서가 존재하는 Keystone 프로젝트에서 문서 의미와 실제 산출물을 capability-first Artifact
Graph로 연결하기 위한 역할·권한·metadata·transaction·finalization 기준을 확정하고 후속 runtime의
권위 있는 source contract를 만든다.

## Prerequisite

- R004 Acceptance Finalization accepted

## Accepted Direction

1. Capability를 문서와 구현 사이의 안정적인 중심 node로 우선 사용하되, 단일 schema 제약이나
   특정 정책 구현처럼 capability가 과한 경우 문서 item과 artifact의 직접 연결을 허용한다.
2. Linker는 canonical graph mutation의 유일한 결정자다.
3. Author는 문서 의미와 문서 키메타의 물리적 반영을 소유한다.
4. Coordinator 또는 Main direct는 구현 의미와 repository anchor의 물리적 반영을 소유한다.
5. Graph-relevant 변경은 선택적 권고가 아니라 graph synchronization lifecycle을 자동 시작한다.
6. Linker mutation은 surface owner attestation, 적용, 재구성, validator 통과 뒤에만 verified다.
7. 프로젝트 전체 coverage와 current transaction completeness를 구분한다.
8. 기존 metadata는 읽기 호환하고 신규 또는 의미가 변경된 metadata부터 canonical 형식으로
   수렴한다.

## Scope

Include:

- Linker graph mutation authority와 source edit authority 분리
- Author `document_delta`, Coordinator/Main `artifact_delta`
- Capability-first node admission과 직접 연결 예외
- Canonical node, relation, provenance, locator, lifecycle metadata
- Markdown과 repository anchor의 canonical source 표현
- `declared`, `observed`, `inferred` evidence와 mutation admission
- Surface attestation과 exact patch contract
- Baseline digest 기반 optimistic concurrency
- `proposed`, `awaiting_attestation`, `ready_to_apply`, `applying`,
  `partially_applied`, `verified`, `conflicted`, `failed` transaction 상태
- Rename, move, removal, replacement와 history evidence
- Current transaction completeness와 project graph coverage 분리
- R004 finalization runtime의 graph sync disposition·evidence 후속 확장
- Pending transaction의 Change Set·Progress 복구 정보
- 기존 accepted 결정의 관련 claim을 새 claim으로 부분 대체하는 기록

Exclude:

- `skills/**`, parser, validator와 runtime executable 구현
- Code/config/schema/API/test anchor 실제 수정
- 별도 중앙 graph registry 또는 영구 graph database
- 기존 source corpus의 일괄 metadata migration
- 모든 local helper·generated artifact에 anchor 부여
- Uptendo 등 외부 프로젝트의 source나 문서 수정
- 외부 프로젝트 검증을 R005 acceptance gate로 사용

## Change Set

- Intent: 문서 그래프에 머문 Keystone Artifact Graph를 실제 산출물까지 연결하는 폐루프 운영
  계약으로 확장한다.
- Changed nodes: Project, Artifact Graph, Author, Linker, Coordinator와 finalization 관련 기준
  후보
- Impact seeds: `DEC-WORKS-009`, `DEC-WORKS-018`, `DEC-WORKS-021`, metadata admission,
  Change Set, finalization validator
- Required candidates: 관련 기준서, 결정 기록, Context Map, work indexes
- Excluded: repo-local skill source와 executable runtime
- Verification: relation 방향, 권한 경계, transaction 상태, metadata compatibility, temporal metadata,
  Markdown과 `git diff --check`
- Acceptance: Main이 기준 간 충돌 없음과 S02 runtime 입력의 완결성을 확인한 뒤 결정한다.

## Completion Criteria

- [x] Linker의 graph mutation authority와 source surface writer가 구분된다.
- [x] Author·Coordinator/Main·Linker·Validator·Main/User의 권한과 금지가 닫힌다.
- [x] Capability-first와 직접 연결 예외의 admission 기준이 정의된다.
- [x] Canonical metadata와 기존 metadata compatibility가 정의된다.
- [x] Attestation, baseline, partial apply, resume와 verification 상태가 정의된다.
- [x] Project coverage 부족이 current transaction 완료를 자동 차단하지 않는다.
- [x] Graph-relevant change trigger와 finalization evidence가 R004 의미를 깨지 않고 확장된다.
- [x] R004 accepted 문서와 Step 상태를 소급 변경하지 않는다.
- [x] S01에서 `skills/**`와 repository source를 수정하지 않는다.

## Verification

- Project·Artifact Graph·Author·Linker·Coordinator·finalization 기준의 권한과 상태를 비교한다.
- Typed relation 방향과 provenance, locator, lifecycle 의미를 비교한다.
- 새 claim의 부분 supersession target과 item metadata를 검증한다.
- Link, index, temporal metadata, Markdown과 `git diff --check`를 검증한다.

## Stop Conditions

1. R004가 accepted되지 않았다.
2. Linker가 문서 자연어 또는 구현 logic을 직접 수정해야 한다.
3. Graph mutation이 scope·acceptance criteria 또는 Main acceptance를 자동 변경해야 한다.
4. S01 수락에 parser·validator executable 구현이 필요하다.
5. 외부 소비 프로젝트 상태가 S01 완료 조건이 된다.
