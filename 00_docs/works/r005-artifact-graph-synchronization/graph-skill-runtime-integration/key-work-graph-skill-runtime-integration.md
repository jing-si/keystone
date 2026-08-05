---
doc_type: work_order
created_at: "2026-08-05"
status: active
approval: {state: accepted, accepted_at: "2026-08-05", accepted_by: user}
work_status: accepted
key:
  id: key.work.graph-skill-runtime-integration.order
  refs: [key.doc.work, key.topic.artifact-graph, key.topic.skill-contract, key.topic.finalization, key.topic.change-set]
---

# Graph Skill Runtime Integration 작업서 및 Change Set

## Goal

Graph-relevant 문서·구현 변경이 별도 사용자 요청 없이 Linker synchronization을 시작하고,
surface owner 적용과 검증 결과가 R004 finalization evidence로 수렴하도록 설치 skill runtime을
통합한다.

## Prerequisite

- R005 S01·S02 accepted

## Scope

Include:

- Author `document_delta`, document metadata patch 적용과 Change Set sync
- Coordinator assignment/report의 pre-implementation graph context와 `artifact_delta`
- Main direct 구현의 동일 artifact delta·attestation·application report 계약
- Linker graph mutation mode, surface patch, reconstruction과 transaction result
- Surface owner `confirm | reject | needs_revision` attestation
- `applied | failed | stale_baseline` application result
- Graph-relevant change automatic trigger와 safe `not_required` 근거
- R004 finalization에 graph sync required/state/evidence 후속 확장
- Pending·conflicted·failed transaction의 resume와 scoped gate
- Installed runtime contract와 package interface 정합성

Exclude:

- Linker의 자연어 문서 또는 implementation logic 직접 수정
- Coordinator 권한 자동 생성
- User decision이 필요한 scope·capability·acceptance 선택 자동화
- External consumer project 변경
- Global install·publish

## Change Set

- Expected output: Author, Coordinator, Linker와 필요한 Main/Reader/Init runtime contract 개정
- Impact seeds: graph delta, mutation, attestation, application, finalization evidence
- Required candidates: installed skill sources, package reference, R004 finalization runner interface
- Excluded: consuming project source, central registry
- Verification: runtime cross-read, protocol fixtures, package smoke, failure/resume

## Completion Criteria

- [x] Author와 Coordinator/Main이 relation을 독자적으로 확정하지 않는다.
- [x] Linker가 exact mutation을 결정하지만 source를 직접 수정하지 않는다.
- [x] Graph-relevant change에서 synchronization이 자동 시작된다.
- [x] 의미·scope·authority 결정이 필요한 경우에만 Main/User로 중단한다.
- [x] Surface attestation과 application result가 transaction에 회수된다.
- [x] Verified transaction만 graph sync 완료 evidence가 된다.
- [x] Main acceptance는 보존하고 required graph sync 미완료는 finalization을 차단한다.
- [x] Coordinator 사용 권한과 Main direct 경계를 기존 정책보다 확대하지 않는다.

## Verification

- Author→Linker→Coordinator/Main과 Coordinator/Main→Linker→Author 양방향 protocol fixture
- Missing attestation, rejected mutation, stale baseline, partial apply와 resume
- Runtime standard/source cross-read, package command smoke와 `git diff --check`

## Stop Conditions

1. S01·S02가 accepted되지 않았다.
2. Graph sync를 이유로 Coordinator 권한이나 work scope를 자동 확대해야 한다.
3. Linker가 source content를 직접 수정해야 한다.
4. Finalization 연동이 R004 accepted 의미를 취소하거나 소급 변경해야 한다.
