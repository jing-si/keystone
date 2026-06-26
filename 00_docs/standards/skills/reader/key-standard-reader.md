---
doc_type: standard
key:
  id: key.standard.skill.reader
  refs:
    - key.role.reader
    - key.topic.document-navigation
    - key.topic.work-preparation
    - key.topic.work-round
    - key.topic.artifact-graph
    - key.boundary.read-only
    - key.contract.output
---

# keystone-reader 기준서

<!-- key: id=key.standard.skill.reader.purpose refs=key.role.reader key.topic.document-navigation key.topic.work-preparation -->
## 목적

이 기준서는 `keystone-reader`의 상세 계약을 정의한다. `keystone-reader`는 원천 문서(2)와
아티팩트 그래프(14)를 읽어 프로젝트를 파악하고, 관련 기준서(3), 작업서(4), capability, code,
API, test artifact 후보를 찾고, main이 다음 작업을 준비할 수 있도록 read-only context를 만든다.

<!-- key: id=key.standard.skill.reader.scope refs=key.role.reader key.topic.document-navigation key.topic.work-preparation key.topic.artifact-graph key.contract.output -->
## 적용 범위

1. `keystone-reader`의 trigger와 non-trigger condition
2. Orientation, Navigator, Work Prep mode의 workflow와 output
3. 문서 root, standards/works tree, active work round와 active work 탐색 방식
4. 아티팩트 그래프(14), capability, code/API/test artifact 탐색 방식
5. Repository snapshot과 document-to-repository 또는 graph-to-repository mismatch reporting
6. Reader의 read-only boundary, stop condition, verification 기준

<!-- key: id=key.standard.skill.reader.out-of-scope refs=key.role.reader key.boundary.read-only -->
## 적용하지 않는 범위

1. 원천 문서(2), code, config, 진행 기록(5), 결정(6), generated file 수정
2. 기준서(3)나 작업서(4)의 creation/revision
3. high-impact topic 결정(6) 수집 또는 수락
4. subagent assignment, worker handoff 확정, report acceptance
5. persistent `agent/` 문서 생성
6. Skill implementation file 작성

<!-- key: id=key.standard.skill.reader.standard-relations refs=key.role.reader key.doc.standard key.topic.skill-contract key.topic.work-round key.topic.artifact-graph -->
## 기준 관계

1. Parent 기준서: `../../01_key-project-standard.md`
2. 상위 규칙: `STD-KEYSTONE-001`, `STD-KEYSTONE-010`, `STD-KEYSTONE-011`,
   `STD-KEYSTONE-012`, `STD-KEYSTONE-015`, `STD-KEYSTONE-017`,
   `STD-KEYSTONE-018`, `STD-KEYSTONE-020`, `STD-KEYSTONE-023`,
   `STD-KEYSTONE-024`, `STD-KEYSTONE-025`, `STD-KEYSTONE-026`,
   `STD-KEYSTONE-027`, `STD-KEYSTONE-040`
3. 충돌 처리: 이 기준서와 parent 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의
   결정(6)을 받는다. 결정 전까지는 parent 기준서를 임시 우선 기준으로 삼는다.
4. 상세화 범위: 이 기준서는 `STD-KEYSTONE-040`의 Reader 책임을 구현 가능한 수준으로
   상세화한다.

<!-- key: id=key.standard.skill.reader.skill-identity refs=key.role.reader key.topic.skill-contract -->
## Skill identity

1. Skill name: `keystone-reader`
2. Primary role: read-only project orientation, document and artifact navigation, work preparation
3. Primary user: main agent 또는 Keystone 문서를 탐색하려는 사용자
4. Output authority: Reader output은 source of truth가 아니며, 원천 문서(2)를 대체하지
   않는다.

<!-- key: id=key.standard.skill.reader.trigger-condition refs=key.role.reader key.topic.document-navigation key.topic.work-preparation -->
## Trigger condition

`keystone-reader`는 다음 경우에 사용할 수 있다.

1. 프로젝트의 현재 문서 구조와 활성 작업을 파악해야 한다.
2. 현재 요청과 관련된 기준서(3), 작업서(4), 진행 기록(5)을 찾아야 한다.
3. 사용자가 "run the next step"처럼 현재 step 복구가 필요한 요청을 한다.
4. main이 구현이나 문서 수정을 시작하기 전에 관련 source context를 준비해야 한다.
5. document-to-repository 또는 graph-to-repository mismatch를 read-only로 확인하고 보고해야 한다.
6. subagent handoff를 확정하기 전 Goal, context, verification, risk를 준비해야 한다.

<!-- key: id=key.standard.skill.reader.non-trigger-condition refs=key.role.reader key.boundary.read-only -->
## Non-trigger condition

`keystone-reader`는 다음 경우에 사용하지 않는다.

1. 새 기준서(3)나 작업서(4)를 작성하거나 수정해야 한다.
2. high-impact topic 결정(6)을 수집하거나 수락해야 한다.
3. subagent에게 작업을 실제 배정하거나 report를 acceptance해야 한다.
4. code, config, generated file, persistent agent-facing 문서를 수정해야 한다.
5. 사용자가 문서 탐색이 아니라 특정 구현 변경을 명확히 요청했고 source context가 이미
   충분하다.
6. 민감한 문서나 local-only path를 읽어야 하지만 사용자 승인 또는 project policy가
   불명확하다.

<!-- key: id=key.standard.skill.reader.required-input refs=key.role.reader key.topic.work-preparation -->
## Required input

Reader는 다음 input을 사용할 수 있어야 한다.

1. 사용자 요청 또는 main의 current task
2. 현재 repository root
3. 현재 instruction context
4. 설정된 document root(1) 또는 이를 해석하기 위한 project-local setting
5. 필요한 경우 target mode: Orientation, Navigator, Work Prep

Input이 부족하면 Reader는 추측해서 수정하지 않고 `risks_and_gaps` 또는 stop condition으로
보고한다.

<!-- key: id=key.standard.skill.reader.common-workflow refs=key.role.reader key.topic.document-navigation key.topic.work-preparation key.topic.work-round key.topic.artifact-graph -->
## Common workflow

Reader는 mode와 무관하게 다음 순서를 따른다.

1. 설정된 document root(1)를 `STD-KEYSTONE-010`에 따라 해석한다.
2. `key-context-map.md`가 있으면 먼저 읽어 active standards와 active work를 파악한다.
3. `standards/00_key-index.md` 또는 해당 project의 standards index를 읽는다.
4. `works/00_key-index.md` 또는 해당 project의 root works index를 읽어 active round를 찾는다.
5. Active round index를 읽어 round 내부 실행 순서와 active work node를 확인한다.
6. Active work node의 index, 작업서(4), 진행 기록(5)을 읽어 `round_id`, `work_id`,
   `current_step`을 함께 복구한다.
7. 현재 요청과 관련된 child index만 따라 내려가며 관련 없는 branch를 읽지 않는다.
8. 요청 또는 current work에 관련 키메타(9)가 있으면 같은 `key.id`를 참조하는
   문서를 탐색 후보로 확인한다.
9. 요청 또는 current work에 capability, API, code, test 단서가 있으면 코드 앵커(18),
   typed relation, locator, 실제 repository reference를 함께 탐색한다.
10. 키메타와 코드 앵커 탐색은 link, path, heading, keyword, import/call/reference 탐색과 함께
    사용한다.
11. 필요한 경우 shallow repository snapshot을 만든다.
12. output에는 항상 `sources_read`, `assumptions`, `risks_and_gaps`,
   `recommended_next_action`을 포함한다.

<!-- key: id=key.standard.skill.reader.mode-contract refs=key.role.reader key.contract.output key.topic.work-preparation -->
## Mode contract

<!-- key: id=key.standard.skill.reader.orientation-mode refs=key.role.reader key.topic.document-navigation key.topic.work-round -->
### Orientation Mode

Orientation Mode는 project-level overview를 만든다.

1. 읽기 범위: instruction, 설정된 document root(1), context map, standards index, root works
   index, active round index, active work, shallow repository snapshot
2. 금지: document, code, config, 진행 기록(5), 결정(6), generated file 수정
3. Repository snapshot 제한:
   - repository root
   - top-level directory
   - key config/build file
   - expected skill/source directory
   - Git status summary
   - 명백한 document-to-repository mismatch signal
4. Output field:
   - `document_root`
   - `project_summary`
   - `repository_snapshot`
   - `active_document_map`
   - `artifact_graph_summary`
   - `active_round`
   - `round_id`
   - `round_index`
   - `work_id`
   - `current_step`
   - `current_work_status`
   - `recommended_read_order`
   - `operational_boundaries`
   - `risks_and_gaps`
   - `recommended_next_action`
   - `sources_read`
   - `assumptions`

<!-- key: id=key.standard.skill.reader.navigator-mode refs=key.role.reader key.topic.document-navigation key.contract.output key.topic.work-round key.topic.artifact-graph -->
### Navigator Mode

Navigator Mode는 현재 요청과 관련된 원천 문서(2)를 찾는다.

1. Input: 사용자 요청, current task, known document root
2. 읽기 범위: standards index, root works index, active round index, parent 기준서, 관련 child
   기준서, active work, 관련 아티팩트 그래프(14) 후보
3. Output field:
   - `request_summary`
   - `key_ref_queries`
   - `matched_documents`
   - `matched_artifacts`
   - `key_ref_matched_candidates`
   - `relations`
   - `mismatches`
   - `active_round`
   - `round_id`
   - `round_index`
   - `work_id`
   - `recommended_read_order`
   - `why_each_document_matters`
   - `missing_or_ambiguous_documents`
   - `sources_read`
   - `assumptions`
4. 금지: 관련 없는 branch 전체를 읽거나, 문서 부재를 조용히 새 문서 생성으로 해결하기

<!-- key: id=key.standard.skill.reader.work-prep-mode refs=key.role.reader key.topic.work-preparation key.contract.output key.topic.work-round key.topic.artifact-graph -->
### Work Prep Mode

Work Prep Mode는 main이 다음 작업을 실행하거나 subagent handoff를 준비할 수 있게 한다.
단, final handoff를 확정하지 않는다.

1. Input: current task 또는 active work step
2. 읽기 범위: 관련 기준서(3), root works index, active round index, work node index,
   작업서(4), 진행 기록(5), completion criteria, verification note, related capability/API/code/test
   artifact 후보
3. Output field:
   - `active_round`
   - `round_id`
   - `round_index`
   - `work_id`
   - `goal`
   - `source_context`
   - `applicable_standards`
   - `impact_seeds`
   - `artifact_candidates`
   - `key_ref_queries`
   - `key_ref_matched_candidates`
   - `current_step`
   - `scope`
   - `completion_criteria`
   - `verification`
   - `suggested_role`
   - `stop_conditions`
   - `risks_and_gaps`
   - `sources_read`
   - `assumptions`
4. 금지: subagent assignment 확정, progress status 변경, implementation 시작

<!-- key: id=key.standard.skill.reader.mismatch-handling refs=key.role.reader key.topic.document-navigation key.topic.artifact-graph key.boundary.read-only -->
## Mismatch handling

원천 문서(2), 아티팩트 그래프(14), repository state가 충돌하면 Reader는 다음처럼 처리한다.

1. 자동 수정하지 않는다.
2. mismatch의 source와 evidence를 기록한다.
3. 영향을 받는 문서, 작업, capability, code, API, test artifact 후보를 식별한다.
4. 사용자 또는 main에게 선택지를 제시한다.
   - 문서 업데이트를 준비한다.
   - code work를 준비한다.
   - 추가 read-only 조사를 진행한다.
   - 현재 작업을 중단한다.
5. mismatch가 current task correctness에 영향을 주면 `recommended_next_action`에
   decision need를 포함한다.

<!-- key: id=key.standard.skill.reader.metadata-handling refs=key.role.reader key.topic.document-navigation key.topic.keystone-metadata key.topic.code-anchor key.topic.artifact-graph -->
## 키메타와 코드 앵커 handling

Reader는 키메타(9)와 코드 앵커(18)를 관련 문서와 artifact 탐색 단서로 사용한다.

1. 같은 `key.id`를 참조하는 문서는 관련 문서 후보로 검토한다.
2. 같은 `key.refs`가 있어도 자동으로 관련 문서나 artifact라고 확정하지 않는다.
3. `key.refs`나 typed relation이 없어도 관련 없음으로 단정하지 않는다.
4. Navigator Mode와 Work Prep Mode output에는 사용한 `key.refs`, 코드 앵커 typed relation,
   발견한 문서/code/API/test 후보를 포함한다.
5. 키메타와 코드 앵커 탐색 결과는 title, path, link, heading, keyword, 실제 code reference
   근거와 함께 판단한다.
6. Declared relation, observed relation, inferred relation을 구분해 보고한다.
7. Inferred relation은 impact candidate이며 자동 수정 근거가 아니다.

<!-- key: id=key.standard.skill.reader.stop-condition refs=key.role.reader key.boundary.read-only key.topic.work-preparation -->
## Stop condition

Reader는 다음 상황에서 중단하거나 main/user 결정(6)을 요청한다.

1. 설정된 document root(1)를 확신 있게 해석할 수 없다.
2. active round, current step, completion criteria, applicable standard를 복구할 수 없다.
3. 원천 문서(2)가 현재 사용자 방향과 충돌한다.
4. 문서 변경이 필요한데 Reader mode가 read-only라 처리할 수 없다.
5. 민감한 원천 문서(2)나 local-only path를 읽어야 하지만 권한 또는 policy가 불명확하다.
6. document-to-repository 또는 아티팩트 그래프(14) mismatch가 current task의 방향을 바꿀 수 있다.
7. 관련 기준서(3) 또는 작업서(4)가 없어서 정상적인 Work Prep output을 만들 수 없다.

<!-- key: id=key.standard.skill.reader.verification refs=key.role.reader key.contract.output key.topic.verification -->
## Verification

Reader 기준은 다음 방법으로 검증한다.

1. Reader contract만 보고 trigger와 non-trigger를 구분할 수 있어야 한다.
2. Mode별 output field가 `STD-KEYSTONE-040`의 상위 Reader 책임과 일관되어야 한다.
3. Reader output은 원천 문서(2)를 대체하거나 수정하지 않아야 한다.
4. Work Prep Mode output은 coordinator가 `round_id`, `work_id`, `current_step`을 가진
   final handoff를 만들기 전 단계로 사용할 수
   있어야 한다.
5. 키메타 또는 코드 앵커를 사용한 경우 output에서 사용한 `key.refs`, typed relation, 후보 문서와
   artifact를 확인할 수 있어야 한다.
6. Reader는 아티팩트 그래프(14) 후보를 보고할 수 있지만 code/config/test를 수정하지 않아야 한다.
7. Verification command:
   - `rg --files 00_docs`
   - Reader 관련 기준서를 읽어 link와 scope consistency 확인
