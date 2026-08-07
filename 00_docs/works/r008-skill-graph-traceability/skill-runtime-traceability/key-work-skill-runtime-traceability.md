---
doc_type: work_order
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-07", accepted_by: main}
work_status: complete
key:
  id: key.work.skill-runtime-traceability.order
  refs:
    - key.doc.work
    - key.topic.skill-source
    - key.topic.code-anchor
    - key.topic.artifact-graph
    - key.topic.verification
    - key.topic.change-set
---

# Skill Runtime Traceability and Self-Host E2E 작업서 및 Change Set

<!-- key: id=key.work.skill-runtime-traceability.order.goal refs=key.section.goal key.topic.artifact-graph -->
## Goal

Keystone 기준서와 Work Order에서 skill source, 핵심 runtime boundary와 대표 contract test까지
필요한 의미 관계를 추적하고, S01-S06에서 정합화한 전체 workflow를 실제 Keystone corpus와
새 세션 복구 시나리오로 검증한다.

<!-- key: id=key.work.skill-runtime-traceability.order.scope refs=key.section.scope key.topic.code-anchor -->
## Scope

Include:

- 여섯 `skills/keystone-*/SKILL.md` owner와 governing standard/provenance relation 재검증
- Linker의 metadata parsing, context readiness, graph validation public boundary
- Author의 acceptance finalization validator public boundary
- Reader-Linker readiness contract와 package-level graph contract/E2E test 중 independently
  referenceable한 대표 test
- Linker가 `required` 또는 `strong_candidate`로 분류한 최소 code/test anchor
- Test artifact의 실제 검증 의미에 맞는 `verifies` target과 locator
- Anchor 추가 뒤 impact, stale, reuse와 metadata-gap 재검토
- 실제 corpus의 readiness→dependency→graph synchronization→multi-Step finalization E2E
- 빈/partial/conflicted initialization, 중단 후 resume, dependency waiting/invalid/cycle,
  partial transaction resume와 cache corruption/contention scenario
- Repository evidence 안의 prompt injection을 authority로 승격하지 않는 agent-level evaluation
- README current-source navigation과 root/round/context index가 최신 accepted/active round를
  일관되게 가리키는지 확인

Exclude:

- 모든 Python module, private helper와 unit test의 일괄 anchor화
- Path나 line number를 stable ID로 사용하는 metadata
- 의미 근거가 없는 capability node 또는 broad import/call relation 생성
- 기존 기준서의 정책 의미 변경, 2~4주 외부 소비 프로젝트 pilot, global install과 publish

<!-- key: id=key.work.skill-runtime-traceability.order.source-context refs=key.section.source-context key.topic.artifact-graph -->
## Source Context

- R008/S01-S06의 accepted result와 residual diagnostics
- `00_docs/standards/01_key-project-standard.md`의 `STD-KEYSTONE-015`, `017`, `018`, `023`, `025`, `027`
- `00_docs/standards/artifacts/key-standard-artifact-graph.md`의 metadata admission, capability,
  locator, metadata gap, impact와 verification relation
- `00_docs/standards/skills/linker/key-standard-linker.md`의 Artifact Discovery와 Stale/Gap Review
- R002 Skill Runtime Implementation work order와 R007 verification evidence

<!-- key: id=key.work.skill-runtime-traceability.order.baseline refs=key.topic.impact-review key.topic.verification -->
## Baseline Findings

1. Production repository anchor는 현재 여섯 `SKILL.md` owner에 집중되어 있다.
2. Skill owner는 R002 production provenance와 project governance를 가지지만 child governance는
   S01 전 parser에서 누락된다.
3. 실제 repository typed graph에는 핵심 runtime/test를 연결하는 declared `verifies` edge가 없다.
4. Test suite와 progress evidence는 존재하지만 어떤 stable behavior나 contract를 검증하는지
   source graph에서 직접 탐색할 수 없다.
5. R007 verification은 subsystem suite와 repository validator를 통과했지만 실제 session의
   readiness, dependency, graph transaction과 모든 accepted Step finalization을 하나로 연결한
   self-host E2E는 없다.
6. README current-source navigation은 아직 R006 round를 가리킨다. Root works index 제목의
   작업서 번호 오기는 R008 작업서 재구성 시 `(4)`로 바로잡았다.

<!-- key: id=key.work.skill-runtime-traceability.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

- Intent: 과잉 annotation 없이 기준서에서 operative runtime과 verification evidence까지 탐색한다.
- Impact seeds: `key.standard.project.std-keystone-015`,
  `key.standard.artifact.graph.metadata-admission`, `key.standard.artifact.graph.metadata-gap`,
  `key.work.skill-runtime-implementation.order`, 여섯 `key.skill.*` owner
- Required candidates: Linker가 required로 분류한 public contract/runtime/test boundary
- Optional candidates: 재사용 또는 독립 impact review 가치가 있는 strong candidate
- Excluded: local helper, trivial wrapper, 모든 unit test, generated/cache artifact
- Acceptance owner: Main
- Graph handling: 여러 source surface에 canonical relation이 추가되면 Linker가 exact mutation과
  patch를 결정하고 각 owner가 자기 surface만 attest/apply한다.

<!-- key: id=key.work.skill-runtime-traceability.order.approach refs=key.section.recommended-approach key.topic.artifact-graph -->
## Recommended Approach

1. S01-S06 이후 fresh repository index로 Artifact Discovery와 Stale/Gap Review를 다시 수행한다.
2. Metadata admission policy에 따라 public boundary와 핵심 contract/E2E test만 후보로 남긴다.
3. Stable ID, locator, relation direction과 source owner를 Linker evidence로 확인한다.
4. Test가 실제 수행하는 behavior에만 `verifies`를 선언하고 단순 file/name overlap은 제외한다.
5. Required candidate를 먼저 반영하고 optional candidate는 reuse/impact 가치가 명확할 때만
   포함한다.
6. Source reconstruction과 validator/readiness를 함께 실행해 새 anchor가 duplicate, dangling,
   stale locator를 만들지 않았는지 확인한다.
7. 각 agent-level scenario는 입력, expected authority boundary, expected diagnostic/status와
   resume point를 고정하고 실제 새 세션에서 재현한다.
8. External pilot과 OS/CI matrix는 R008 acceptance evidence와 분리해 후속 round candidate로 남긴다.

<!-- key: id=key.work.skill-runtime-traceability.order.completion refs=key.topic.acceptance key.topic.integration-verification -->
## Completion Criteria

- [x] Fresh Linker report가 required/strong/weak/excluded code·test 후보를 구분한다.
- [x] 여섯 skill owner의 production provenance와 project/child/bootstrap governance가 유지된다.
- [x] 선택한 runtime/test anchor가 metadata admission policy를 만족하고 owner가 유일하다.
- [x] 대표 contract/E2E test의 `verifies` target이 존재하며 실제 검증 behavior와 일치한다.
- [x] Private helper, trivial wrapper와 전체 unit test가 불필요하게 graph node로 승격되지 않는다.
- [x] Anchor locator와 typed relation direction이 validator와 semantic review를 통과한다.
- [x] Linker, Author, Reader와 skill contract 전체 suite가 통과한다.
- [x] Docs/repository readiness와 repository graph validator가 새 mechanical stale 없이 통과한다.
- [x] Graph synchronization이 required이면 verified transaction과 owner apply evidence가 존재한다.
- [x] Actual corpus readiness→dependency→graph synchronization→multi-Step finalization E2E가 통과한다.
- [x] Init/resume/cache/dependency/partial-apply/prompt-injection scenario가 expected status와
  authority boundary를 재현한다.
- [x] External pilot, global install과 publication 미검증 범위가 후속 round candidate로 기록된다.
- [x] README, Context Map, root/round/work index의 current navigation이 같은 active/latest state를
  가리킨다.
- [x] Main이 relation 의미, test evidence와 residual coverage debt를 검토한다.

<!-- key: id=key.work.skill-runtime-traceability.order.review-points refs=key.section.review-points key.topic.impact-review -->
## Review Points

- Anchor가 path가 아니라 stable responsibility를 식별하는가
- Governing standard, produced source와 verifying test의 relation 방향이 올바른가
- Test 이름이 아니라 실제 assertion/fixture behavior가 `verifies` 근거인가
- Capability node를 만들지 않고 direct relation으로 충분한 좁은 contract가 있는가
- Candidate 선정이 모든 code/test를 graph화하는 migration으로 확장되지 않았는가

<!-- key: id=key.work.skill-runtime-traceability.order.verification refs=key.topic.verification -->
## Verification

- Linker Artifact Discovery/Stale-Gap report와 before/after relation snapshot 비교
- `PYTHONPATH=skills/keystone-linker/scripts python3 -m unittest discover -s skills/keystone-linker/tests -p 'test_*.py'`
- `PYTHONPATH=skills/keystone-author/scripts python3 -m unittest discover -s skills/keystone-author/tests -p 'test_*.py'`
- `python3 -m unittest discover -s skills/keystone-reader/tests -p 'test_*.py'`
- `python3 -m unittest discover -s skills/tests -p 'test_*.py'`
- Installed Linker package의 fresh docs/repository readiness
- `python3 skills/keystone-linker/scripts/validate_graph.py --root . --scope repository`
- Anchor owner uniqueness, relation target existence와 locator 확인
- S01-S06 behavior를 연결한 self-host scenario runner 또는 reproducible command log
- `python3 -m compileall`과 `git diff --check`

<!-- key: id=key.work.skill-runtime-traceability.order.expected-output refs=key.contract.output key.topic.work-recovery -->
## Expected Output

- Linker가 승인 후보로 분류한 최소 runtime/test anchor set
- 기준서·Work Order·skill source·runtime·test를 잇는 source-owned graph relation
- Representative verification evidence와 source locator
- Actual corpus self-host E2E 결과와 failed scenario별 resume evidence
- Excluded candidate와 residual coverage debt 설명
- Graph sync/validation 결과와 Main acceptance evidence

<!-- key: id=key.work.skill-runtime-traceability.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. R008/S01-S06 결과가 아직 불안정하거나 source-only reconstruction이 재현되지 않는다.
2. Stable owner 또는 `verifies` target의 의미를 여러 유효 선택 중 결정해야 한다.
3. Anchor 추가가 public runtime behavior, wire 또는 diagnostic 의미 변경을 요구한다.
4. Scope가 모든 runtime module/test의 bulk annotation으로 확장된다.
5. Existing source changes와 겹쳐 bounded patch 또는 owner attestation을 안전하게 만들 수 없다.
6. Required graph transaction이 conflicted, partially applied 또는 mechanically unverified 상태다.
