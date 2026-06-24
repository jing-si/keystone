---
doc_type: standard_index
tags:
  - coordinator
  - subagent
  - verification
  - acceptance
---

# keystone-coordinator 기준서 색인

이 색인은 `keystone-coordinator` child 기준서로 이동하기 위한 기준이다.

<!-- tags: coordinator, subagent, verification, acceptance -->
## 문서

1. `KEY-standard-coordinator.md`
   - `keystone-coordinator`의 목적, trigger/non-trigger, Goal assignment, Context Pack,
     subagent routing, report handling, review, verification, acceptance flow를 정의한다.

<!-- tags: coordinator, 기준서, 스킬계약 -->
## Parent 기준서

1. `../../00_KEY-project-standard.md`
   - Keystone 공통 용어, main/subagent 책임, 작업서(4) Goal unit, 진행 상태와 report
     status, 기준서-led verification, 파생 에이전트 문서(8) 정책을 정의한다.

<!-- tags: coordinator, 기준서, 작업실행 -->
## 읽기 규칙

1. Coordinator의 공통 orchestration 정책은 `../../00_KEY-project-standard.md`의
   `STD-KEYSTONE-004`, `STD-KEYSTONE-005`, `STD-KEYSTONE-012`,
   `STD-KEYSTONE-013`, `STD-KEYSTONE-018`, `STD-KEYSTONE-020`,
   `STD-KEYSTONE-022`, `STD-KEYSTONE-023`, `STD-KEYSTONE-030`을 먼저 확인한다.
2. Coordinator 구현 또는 상세 계약 검토가 필요하면 `KEY-standard-coordinator.md`를 읽는다.
3. Parent 기준서와 이 child 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의
   결정(6)을 받는다. 결정 전까지는 parent 기준서를 임시 우선 기준으로 삼는다.
