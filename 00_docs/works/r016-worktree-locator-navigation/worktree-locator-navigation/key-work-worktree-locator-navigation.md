---
doc_type: work_order
created_at: "2026-08-25"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-25", accepted_by: main}
work_status: complete
key:
  id: key.work.worktree-locator-navigation.order
  refs:
    - key.doc.work
    - key.topic.work-recovery
    - key.topic.work-sequence
    - key.topic.work-execution
    - key.topic.keystone-metadata
    - key.topic.skill-contract
    - key.topic.verification
    - key.boundary.scope-control
    - key.standard.project
    - key.standard.artifact.graph
    - key.standard.skill.reader
    - key.standard.skill.author
    - key.standard.skill.coordinator
    - key.standard.subagent
    - key.work.decisions.dec-works-018
    - key.work.decisions.dec-works-033
---

# Worktree Locator and Targeted Work Discovery 작업서 및 Change Set

<!-- key: id=key.work.worktree-locator-navigation.order.goal refs=key.section.goal key.topic.work-recovery key.topic.work-execution -->
## Goal

구현 작업을 Git linked worktree에서 시작할 때 Coordinator가 생성하거나 선택한 정확한 worktree
경로를 코드 수정 전에 canonical Work Order 키메타에 기록하고, 이후 Reader·Main·Coordinator가
그 locator에 의존해 대상 worktree만 직접 탐색하도록 한다.

전체 worktree를 매 세션 열거하거나 repository-wide로 추측 탐색하는 비용을 만들지 않으면서,
Work와 실제 실행 위치의 연결을 사람이 읽을 수 있는 source에 남겨 동일 작업을 다른 위치에서
중복 시작할 가능성을 줄인다.

<!-- key: id=key.work.worktree-locator-navigation.order.problem refs=key.topic.work-recovery key.topic.work-execution -->
## 문제와 근거

1. 현재 Coordinator는 current workspace state와 시작 시점 Git/diff baseline을 요구하지만,
   Work Order와 선택된 linked worktree 사이의 persistent locator를 정의하지 않는다.
2. Reader의 Linker freshness는 현재 worktree identity를 사용하지만 active Work가 어느 linked
   worktree에서 실행되는지는 복구하지 않는다.
3. 하나의 Git repository에 여러 worktree가 등록될 수 있고, branch-local 또는 untracked Work
   source는 다른 worktree의 세션에 자동으로 보이지 않는다.
4. 매번 모든 worktree를 열거하고 각 source와 상태를 확인하면 초기 탐색 비용이 커지고 R014의
   progressive context loading 방향을 약화한다.
5. Work Order 키메타에 exact locator가 있으면 selected Work를 읽은 뒤 해당 경로만 확인할 수 있다.
6. 현재 Linker metadata parser는 `key.worktree`를 known field로 인정하지 않아 그대로 추가하면
   `unknown_metadata_field` 진단을 만든다.

<!-- key: id=key.work.worktree-locator-navigation.order.direction refs=key.topic.work-execution key.topic.keystone-metadata -->
## 사용자 방향

상세 질문과 답변은
`clarify/20260825T030754Z-worktree-locator-navigation.md`에 비권위 memory log로 기록한다.

1. R015와 결합하지 않고 별도 Round/Work로 생성한다.
2. 최초 구현을 linked worktree에서 시작하는 경우 코드 수정 전에 Work Order 키메타에 실제
   worktree 위치를 기록한다.
3. 기록된 locator를 탐색의 기본 source로 사용하고, 누락을 보완하기 위해 전체 worktree를
   자동으로 훑지 않는다.
4. Locator가 없어서 별도 worktree를 발견하지 못하는 예외는 사용자의 기억에 의존하는 운영
   위험으로 수용한다.
5. Atomic claim, lock registry 또는 자동 중복 실행 차단은 이번 범위에 포함하지 않는다.
6. 구현 작업에서는 Coordinator가 worktree 생성·선택과 검증을 주로 담당한다.
7. Author는 canonical Work Order의 문서 키메타를 기록하고, Reader는 그 locator를 소비한다.
8. Main이 Coordinator 없이 직접 구현하는 작은 작업에서는 Main이 같은 pre-start handoff와
   재확인 책임을 수행한다.

<!-- key: id=key.work.worktree-locator-navigation.order.metadata-contract refs=key.topic.keystone-metadata key.topic.work-recovery -->
## 계획된 키메타 계약

Worktree를 선택한 Work Order는 다음 형태의 document metadata를 가진다.

```yaml
key:
  id: key.work.example.order
  refs:
    - key.doc.work
  worktree:
    path: /absolute/path/to/target-worktree
```

1. `key.worktree`는 Work Order document node에만 선언하는 operational navigation metadata다.
2. `path`는 target worktree에서 확인한 canonical absolute root path다. Branch와 HEAD는 locator에
   중복 저장하지 않고 대상 경로에서 현재 값을 확인한다.
3. Worktree 사용을 선택하지 않은 Work에는 `key.worktree`를 추가하지 않는다.
4. Worktree를 새로 만들거나 교체한 경우 substantive code/config/schema/API/test/skill-source
   수정 전에 canonical Work Order의 `path`를 기록하거나 갱신한다.
5. Canonical Work Order는 세션 시작점에서 읽을 수 있는 control-plane source다. Target branch에만
   기록되어 다른 세션에서 보이지 않는 값은 기록 완료로 간주하지 않는다.
6. Active Work에서 locator가 있으면 Reader와 Coordinator는 그 경로만 확인한다. Locator가 없으면
   현재 worktree를 사용하며 전체 Git worktree 목록을 fallback 탐색하지 않는다.
7. 기록된 path가 없거나 접근할 수 없거나 다른 Git common directory를 가리키면 stale/mismatch를
   보고하고 자동으로 다른 worktree를 찾지 않는다.
8. 완료된 Work의 locator는 당시 실행 위치의 이력으로 보존한다. Current navigation에는 active
   또는 사용자가 명시한 Work의 locator만 사용한다.
9. Absolute local path 공개가 허용되지 않는 프로젝트에서는 기록 전에 멈추고 별도 project
   decision을 받는다.

<!-- key: id=key.work.worktree-locator-navigation.order.owner-sequence refs=key.role.coordinator key.role.author key.role.reader key.topic.work-execution -->
## Owner와 pre-implementation 순서

1. Author가 `planned` Work Order를 만들고 필요한 Goal, Scope와 verification을 확정한다.
2. 구현이 승인되면 Coordinator가 current state와 existing-change risk를 확인하고 worktree를
   생성하거나 기존 worktree를 선택한다.
3. 외부 injected skill이 worktree를 만드는 경우에도 Coordinator가 exact path를 회수하며 실제
   구현 edit 전에 setup phase를 멈춘다.
4. Coordinator 또는 Main은 exact target root와 같은 Git common directory 여부를 확인해 Author에
   전달한다.
5. Author가 canonical Work Order의 `key.worktree.path`를 기록한다. Coordinator는 fresh source에서
   같은 locator를 다시 읽고 target worktree와 일치하는지 확인한다.
6. 위 순서가 끝난 뒤에만 Coordinator direct execution 또는 external-skill worker가 substantive
   repository edit를 시작한다.
7. Worktree 생성·선택은 Coordinator/Main 실행 환경 책임이고 Work Order metadata write는 Author
   책임이다. Reader는 source-write 없이 기록을 소비한다.

<!-- key: id=key.work.worktree-locator-navigation.order.scope refs=key.section.scope key.boundary.scope-control -->
## Scope

Include:

- `key.worktree.path`의 allowed shape, document-kind 제한, absolute path와 stale/mismatch 의미
- Worktree 선택 후 코드 수정 전 Coordinator→Author→Coordinator 기록·재확인 gate
- Main direct와 external injected skill의 같은 owner handoff 경계
- Reader의 selected Work Order 기반 exact-path navigation과 no-global-scan fallback
- Project, Artifact Graph, Reader, Author, Coordinator와 Subagent 기준서 정합화
- Reader, Author, Coordinator 설치 skill runtime 계약 정합화
- Linker metadata parser의 `key.worktree` admission과 malformed-shape 진단
- Focused parser, skill contract, targeted navigation과 no-scan regression
- Work State current authority, R014 progressive loading과 R015 active state 보존 검증

Exclude:

- R015 Work Order나 Progress의 변경 또는 R015 개선 후보와의 통합
- 기존 Work와 historical Work Order에 `key.worktree`를 일괄 backfill
- Git worktree 사용, branch 이름, writer 수, merge/rebase와 integration 전략 강제
- `git worktree list` 기반 전역 탐색, repository-wide worktree inventory 또는 자동 fallback
- Atomic claim, lock file, shared registry, stale claim 회수와 cross-machine coordination
- Worktree 생성·삭제 CLI 자체의 구현 또는 Git wrapper 도입
- Branch와 HEAD를 Work Order locator에 지속적으로 동기화하는 projection
- Work State schema나 active Round/Step authority 변경
- 실제 R016 구현을 위한 linked worktree 생성 또는 코드 수정

<!-- key: id=key.work.worktree-locator-navigation.order.execution-plan refs=key.topic.work-sequence key.topic.verification -->
## 실행 계획

| Step | 상태 | 변경 범위 | 완료 경계 |
|---|---|---|---|
| R016/S01 | accepted | 공통 결정, Project·Artifact Graph·Reader·Author·Coordinator·Subagent 기준서 | metadata 의미, owner 순서, direct navigation, omission/stale와 retained execution-strategy 경계를 정렬했다 |
| R016/S02 | accepted | Reader·Author·Coordinator skill source, Linker metadata parser와 필요한 runtime wiring | Coordinator setup과 Author 기록 뒤 구현이 시작되고 Reader가 exact locator만 소비하며 parser가 새 field를 기계적으로 검증한다 |
| R016/S03 | accepted | Focused package/shared tests, Work State, affected graph와 self-host scenario | valid/stale/missing/malformed locator, no-global-scan, Main/external-skill fallback과 기존 workflow 보존을 검증했다 |

각 Step은 Main acceptance 전까지 `pending`이며, 현재 사용자의 실행 승인으로 S01을 시작했다.

<!-- key: id=key.work.worktree-locator-navigation.order.change-set refs=key.topic.change-set key.topic.impact-review -->
## Change Set

| Surface | Owner | Required change | Verification |
|---|---|---|---|
| Shared Decision and Project Standard | Author | Worktree 선택 시 locator 기록과 기존 no-forced-strategy 경계를 공통 정책으로 정렬 | `DEC-WORKS-018`, `DEC-WORKS-033`과 project rule 대조 |
| Artifact Graph Standard | Author | `key.worktree`를 Work Order operational navigation metadata로 정의 | field shape, lifecycle와 locator/relation 분리 검토 |
| Reader Standard and Skill | Author / Main | selected Work의 exact path 탐색, missing/stale와 no-global-scan 경계 반영 | targeted navigation contract test |
| Author Standard and Skill | Author / Main | Coordinator/Main handoff 뒤 canonical Work Order에 pre-edit locator 기록 | create/revise and owner-boundary test |
| Coordinator/Subagent Standard and Coordinator Skill | Author / Main | worktree setup phase와 metadata confirmation 뒤 repository edit 시작 | direct/external-skill sequence test |
| Linker Metadata Parser | Main | `key.worktree.path`를 known validated field로 admission | valid and malformed parser tests, no unknown warning |
| R016 Work Sources | Author | 실제 Step 상태, evidence와 resume point만 기록 | Work State and exact-ref check |

<!-- key: id=key.work.worktree-locator-navigation.order.completion refs=key.topic.verification key.topic.work-recovery -->
## Completion Criteria

<!-- key: id=key.acceptance.worktree-locator.metadata-shape -->
- `R016-CC-01` `key.worktree.path`가 Work Order 전용 operational navigation metadata로 정의되고
  valid absolute path는 unknown-field 진단 없이 파싱된다.
<!-- key: id=key.acceptance.worktree-locator.owner-sequence -->
- `R016-CC-02` Coordinator가 worktree를 생성·선택하고 Author가 canonical Work Order에 기록한 뒤
  Coordinator가 재확인하기 전에는 substantive repository edit가 시작되지 않는다.
<!-- key: id=key.acceptance.worktree-locator.targeted-reader -->
- `R016-CC-03` Reader는 selected Work의 기록된 exact path만 탐색하며 전체 worktree 목록이나 다른
  worktree source를 fallback으로 훑지 않는다.
<!-- key: id=key.acceptance.worktree-locator.absent-policy -->
- `R016-CC-04` `key.worktree`가 없으면 current worktree를 사용하고 별도 worktree 누락은 사용자
  기억에 의존하는 명시적 residual risk로 남는다.
<!-- key: id=key.acceptance.worktree-locator.stale-policy -->
- `R016-CC-05` recorded path가 missing, inaccessible 또는 다른 Git common directory면
  stale/mismatch를 보고하고 자동 탐색으로 우회하지 않는다.
<!-- key: id=key.acceptance.worktree-locator.external-skill -->
- `R016-CC-06` injected skill이 worktree를 만드는 경우에도 setup 결과를 Coordinator가 회수하고
  Author 기록 gate 전에는 구현 edit로 넘어가지 않는다.
<!-- key: id=key.acceptance.worktree-locator.main-direct -->
- `R016-CC-07` Coordinator 없이 Main이 직접 구현하는 경우 같은 exact-path handoff, Author 기록과
  fresh confirmation 경계를 수행한다.
<!-- key: id=key.acceptance.worktree-locator.strategy-retained -->
- `R016-CC-08` Worktree·branch·writer·integration 전략을 Keystone이 강제하지 않는
  `DEC-WORKS-018` 의미와 R014 progressive loading 계약이 유지된다.
<!-- key: id=key.acceptance.worktree-locator.no-locking -->
- `R016-CC-09` Atomic claim, lock registry, global worktree inventory와 historical backfill이
  구현 범위에 들어오지 않는다.
<!-- key: id=key.acceptance.worktree-locator.workflow-parity -->
- `R016-CC-10` standards, installed skill source, metadata parser와 focused tests가 같은 owner 순서,
  locator 의미와 no-global-scan 경계를 사용하며 Work State와 affected graph가 통과한다.

<!-- key: id=key.work.worktree-locator-navigation.order.verification refs=key.topic.verification -->
## Verification

1. Project와 child 기준서에서 worktree strategy 선택과 locator 기록 의무가 구분되는지 대조한다.
2. Metadata parser에서 valid `key.worktree.path`, missing path, relative path, unknown child field와
   non-Work Order 선언을 focused fixture로 확인한다.
3. Reader fixture에서 recorded path만 열고 `git worktree list` 또는 sibling worktree traversal을
   호출하지 않는지 검증한다.
4. Coordinator/Author contract fixture에서 worktree setup, document-owner handoff, fresh confirmation,
   implementation edit 순서를 검증한다.
5. External-skill과 Main-direct fallback이 같은 gate를 지키며 Coordinator-only 강제로 바뀌지
   않는지 확인한다.
6. `python3 scripts/work_state_runtime.py --root .`로 R014 accepted, R015 active와 R016 planned가
   함께 손실 없이 복구되는지 확인한다.
7. R016 affected source graph reconstruction, metadata diagnostics, focused package/shared tests와
   `git diff --check`를 실행한다.
8. Release·installer·browser 검증은 관련 surface가 바뀌거나 별도 요청된 경우에만 수행한다.

<!-- key: id=key.work.worktree-locator-navigation.order.context-pack-seed refs=key.topic.work-recovery key.topic.work-execution -->
## Context Pack Seed

- `00_docs/works/key-decisions.md`: `DEC-WORKS-018`, `DEC-WORKS-033`
- `00_docs/standards/01_key-project-standard.md`: execution strategy, Reader/Author/Coordinator 역할
- `00_docs/standards/artifacts/key-standard-artifact-graph.md`: metadata admission과 locator 의미
- `00_docs/standards/skills/reader/key-standard-reader.md`
- `00_docs/standards/skills/author/key-standard-author.md`
- `00_docs/standards/skills/coordinator/key-standard-coordinator.md`
- `00_docs/standards/subagents/key-standard-subagents.md`
- `skills/keystone-reader/SKILL.md`
- `skills/keystone-author/SKILL.md`
- `skills/keystone-coordinator/SKILL.md`
- `skills/keystone-linker/scripts/graph_runtime/metadata.py`

<!-- key: id=key.work.worktree-locator-navigation.order.expected-output refs=key.topic.verification key.topic.work-recovery -->
## Expected Output

1. Accepted standards와 installed skill runtime이 공유하는 `key.worktree.path` contract
2. Coordinator/Main worktree setup → Author metadata write → fresh confirmation → implementation flow
3. Reader의 exact-path targeted discovery와 stale/missing report
4. Linker parser의 bounded metadata admission과 focused regression
5. R016 Step별 actual evidence, residual risk와 resume point

<!-- key: id=key.work.worktree-locator-navigation.order.review-points refs=key.topic.verification key.boundary.scope-control -->
## Review Points

1. Worktree 사용 선택과 locator 기록 의무를 혼동하지 않았는가?
2. Coordinator가 document source를 직접 수정하거나 Author가 worktree execution을 소유하지 않는가?
3. Canonical Work Order 기록이 target branch-local 기록으로 축소되지 않는가?
4. Reader가 편의를 이유로 global worktree scan이나 sibling traversal을 다시 도입하지 않는가?
5. `key.worktree`가 Artifact Graph relation이나 artifact locator와 잘못 합쳐지지 않는가?
6. 누락 위험을 숨기거나 atomic claim이 있는 것처럼 과장하지 않는가?
7. 기존 R014/R015와 Work State authority를 변경하지 않는가?

<!-- key: id=key.work.worktree-locator-navigation.order.stop refs=key.boundary.stop-condition key.boundary.scope-control -->
## Stop Conditions

1. Canonical Work Order가 어느 source/branch에 있어야 다른 세션에서 읽을 수 있는지 결정할 수 없다.
2. Absolute local path 기록이 project privacy 또는 repository policy와 충돌한다.
3. 구현에 global worktree registry, atomic claim, lock lifecycle 또는 cross-machine coordination이
   필요해진다.
4. Work State schema나 current Round/Step authority 변경 없이는 진행할 수 없다.
5. Coordinator가 Work Order document metadata를 직접 수정하거나 Author가 repository execution
   surface를 수정해야만 진행할 수 있다.
6. R015 범위·상태·우선순위 변경이나 historical Work Order backfill이 필요해진다.
7. 기존 사용자 또는 다른 agent 변경과 R016 patch를 안전하게 분리할 수 없다.

## 현재 다음 행동

R016은 S01~S03 구현과 검증을 완료하고 Main acceptance로 닫혔다. 후속 변경은 새 승인 범위에서
별도 Work로 진행한다.
