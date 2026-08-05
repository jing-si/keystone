---
doc_type: work_round
created_at: "2026-07-25"
status: active
approval:
  state: accepted
  accepted_at: "2026-07-25"
  accepted_by: main
round_status: accepted
key:
  id: key.work.round.r003-dependency-work-gate.index
  refs:
    - key.doc.work
    - key.topic.work-round
    - key.topic.work-sequence
    - key.topic.artifact-graph
    - key.topic.work-recovery
---

# R003 Dependency and Work Gate 작업서 색인

이 round는 기존 문서에서 사용되는 `depends_on`과 Keystone runtime의 공식 typed relation 목록
사이의 불일치를 해소한다. Artifact Graph의 의미 관계와 실제 실행 조건을 분리하고, 단계별
dependency를 복구·해석·검증할 수 있는 계약을 repo-local skill source까지 반영한다.

<!-- key: id=key.work.round.r003-dependency-work-gate.execution-order refs=key.topic.work-sequence key.doc.work key.topic.artifact-graph -->
## 실행 순서

| 순서 | Work | 경로 | 상태 | 목적 |
|---|---|---|---|---|
| S01 | Dependency and Work Gate Standard | `dependency-work-gate-standard/00_key-index.md` | accepted | 관계, gate, 상태 판정, 호환성과 검증 규칙을 기준서에 확정했다 |
| S02 | Dependency Runtime Implementation | `dependency-runtime-implementation/00_key-index.md` | accepted | 수락된 기준을 관련 repo-local `SKILL.md`에 구현했다 |
| S03 | Dependency Integration Verification | `dependency-integration-verification/00_key-index.md` | accepted | 대표 시나리오와 기준서/runtime 동기화를 검증하고 round를 마감했다 |

<!-- key: id=key.work.round.r003-dependency-work-gate.reading-rules refs=key.doc.source key.topic.work-recovery key.topic.artifact-graph -->
## 읽기 규칙

1. 프로젝트 방향은 `00_docs/key-context-map.md`를 먼저 읽는다.
2. 관계 모델은 `00_docs/standards/artifacts/key-standard-artifact-graph.md`를 기준으로 한다.
3. 현재 상태는 각 work node의 `key-progress.md`에서 확인한다.
4. S01 기준과 결정이 수락되기 전에는 S02 skill source를 수정하지 않는다.
5. S03 검증이 끝나기 전에는 round 또는 work를 accepted로 표시하지 않는다.

<!-- key: id=key.work.round.r003-dependency-work-gate.boundaries refs=key.boundary.scope-control key.topic.skill-source -->
## Round 경계

- Repo-local `skills/keystone-*/SKILL.md` 반영은 S02에 포함한다.
- Global install, plugin packaging, marketplace 등록과 publish는 포함하지 않는다.
- Uptendo의 R007/R008 문서 직접 수정은 포함하지 않고 검증 시나리오의 source example로만 사용한다.
- Dependency 판정만으로 작업 상태 변경, worker 자동 할당, 자동 취소를 수행하지 않는다.
