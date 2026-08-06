---
doc_type: work_order
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-06", accepted_by: user}
work_status: complete
key:
  id: key.work.python-convention-incremental-refactoring.order
  refs: [key.doc.work, key.doc.convention, key.topic.clean-code, key.topic.verification, key.topic.change-set]
---

# Python Convention and Incremental Refactoring 작업서 및 Change Set

## Goal

Keystone Python runtime의 설계·오류·typing·test 기준을 문서화하고, 외부 동작을 유지하면서
큰 모듈의 책임을 작은 단계로 분리한다.

## Scope

Include:

- `00_docs/convention.md` Python convention
- Python module size, I/O 결합, private cross-module import와 policy 중복 감사
- 1차: `metadata.py`에서 YAML subset parser 분리
- 2차: navigation ref parser의 공개 경계와 scanner private import 제거
- 3차: graph validator를 support, snapshot, transaction 책임으로 분리
- 4차: finalization validator의 source-reading support 분리
- 5차: impact candidate와 namespace manifest section 분리
- 6차: finalization state와 graph synchronization closure section 분리
- 7차: Step·active Step·transition·early-work validation 분리
- 8차: domain model과 canonical JSON wire serialization 분리
- 9차: impact traversal·candidate presentation과 transaction planning 분리
- 10차: transaction wire predicate·normalization·mutation closure helper 분리
- 11차: transaction patch·attestation·apply-result evidence 수집 분리
- 12차: transaction header·input delta·canonical mutation 검증 분리
- 13차: transaction lifecycle state·verified reconstruction closure 분리
- 14차: canonical companion JSON parser와 shared metadata support 분리
- 15차: declared/effective source hierarchy와 authority clamp 분리
- 16차: declared relation·work gate·inferred production relation builder 분리
- 각 단계의 characterization/full regression/self-host verification
- 다음 단계 우선순위와 resume point 기록

Exclude:

- repository-wide formatting 또는 경로 일괄 이동
- 외부 formatter/linter/type-check dependency 도입
- public wire/schema/diagnostic 동작 변경
- 이전 R007 기능 변경과 외부 소비 프로젝트 pilot

## Completion Criteria

- [x] 적용 범위와 점진적 migration 규칙을 포함한 Python convention 초안이 존재한다.
- [x] YAML subset parser가 독립 모듈과 test를 갖고 기존 metadata behavior를 유지한다.
- [x] graph validator 공개 API를 유지하면서 snapshot과 transaction 책임을 분리한다.
- [x] finalization source-reading helper를 분리하고 CLI 동작을 유지한다.
- [x] impact·namespace와 finalization closure section을 독립 함수로 분리한다.
- [x] finalization CLI를 section validator를 조합하는 얇은 orchestration façade로 만든다.
- [x] 기존 model import를 유지하면서 canonical JSON wire serialization을 분리한다.
- [x] 기존 planner import를 유지하면서 impact candidate 책임을 분리한다.
- [x] transaction lifecycle validator에서 순수 wire와 reconstruction helper를 분리한다.
- [x] transaction evidence 수집을 immutable result 경계로 분리한다.
- [x] transaction input과 canonical mutation 검증을 immutable result 경계로 분리한다.
- [x] transaction façade에서 lifecycle state와 verified reconstruction closure를 분리한다.
- [x] companion JSON parser를 source metadata parser와 분리하고 기존 import를 유지한다.
- [x] source hierarchy와 relation 조립을 독립적인 immutable result 경계로 분리한다.
- [x] Linker, Author, skill contract와 self-host validation이 통과한다.
- [x] 다음 리팩터링 후보가 위험도와 dependency 순서로 기록된다.
- [x] Main이 convention과 점진적 리팩터링 결과를 검토한다.

## Stop Conditions

1. Public import 또는 wire compatibility 변경이 필요하다.
2. 외부 dependency나 Python 지원 버전 변경이 필요하다.
3. 현재 dirty worktree의 기존 변경과 구분할 수 없는 충돌이 발생한다.
