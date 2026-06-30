---
doc_type: standard_index
key:
  id: key.standard.skill.coordinator.index
  refs:
    - key.role.coordinator
    - key.role.subagent
    - key.standard.subagent
    - key.topic.verification
    - key.topic.acceptance
    - key.contract.output
    - key.contract.report
---

# keystone-coordinator 기준서 색인

이 색인은 `keystone-coordinator` child 기준서로 이동하기 위한 기준이다.

<!-- key: id=key.standard.skill.coordinator.index.documents refs=key.role.coordinator key.role.subagent key.topic.verification key.topic.acceptance -->
## 문서

1. `key-standard-coordinator.md`
   - `keystone-coordinator`의 목적, trigger/non-trigger, Goal assignment, Context Pack,
     worker assignment/report, bounded worker routing, 외부 코딩 스킬 injected skill 선택,
     report handling, review, verification, acceptance flow를 정의한다.

<!-- key: id=key.standard.skill.coordinator.index.parent-standard refs=key.role.coordinator key.doc.standard key.topic.skill-contract key.standard.subagent -->
## Parent 기준서

1. `../../01_key-project-standard.md`
   - Keystone 공통 용어, main/subagent 책임, 작업서(4) Goal unit, 진행 상태와 report
     status, worker assignment/report, 기준서-led verification, 파생 에이전트 문서(8) 정책을
     정의한다.
2. `../../subagents/key-standard-subagents.md`
   - Subagent purpose preset, authority, injected skill contract, report status, single
     workspace guard, 외부 코딩 스킬 주입 경계, 공통 금지와 stop condition을 정의한다.

<!-- key: id=key.standard.skill.coordinator.index.reading-rules refs=key.role.coordinator key.doc.standard key.topic.work-execution -->
## 읽기 규칙

1. Coordinator의 공통 orchestration 정책은 `../../01_key-project-standard.md`의
   `STD-KEYSTONE-016`, `STD-KEYSTONE-022`, `STD-KEYSTONE-024`,
   `STD-KEYSTONE-025`, `STD-KEYSTONE-030`, `STD-KEYSTONE-031`,
   `STD-KEYSTONE-032`, `STD-KEYSTONE-033`, `STD-KEYSTONE-043`을 먼저 확인한다.
2. Artifact graph impact/stale 후보가 필요하면 `../linker/00_key-index.md`를 읽는다.
3. Subagent purpose preset, authority, report status를 확인해야 하면
   `../../subagents/key-standard-subagents.md`를 읽는다.
4. Coordinator 구현 또는 상세 계약 검토가 필요하면 `key-standard-coordinator.md`를 읽는다.
5. Parent 기준서와 이 child 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의
   결정(6)을 받는다. 결정 전까지는 parent 기준서를 임시 우선 기준으로 삼는다.
