---
doc_type: standard_index
key:
  id: key.standard.subagent.index
  refs:
    - key.role.subagent
    - key.topic.formal-workflow
    - key.topic.work-execution
    - key.contract.output
---

# Subagent 기준서 색인

이 색인은 Keystone subagent 공통 기준서로 이동하기 위한 기준이다.

<!-- key: id=key.standard.subagent.index.documents refs=key.role.subagent key.topic.work-execution key.contract.output -->
## 문서

1. `key-standard-subagents.md`
   - Keystone helper/subagent의 bounded worker model, purpose preset, authority,
     injected skill contract, report status, single workspace guard, 공통 금지와 stop
     condition을 정의한다.

<!-- key: id=key.standard.subagent.index.parent-standard refs=key.role.subagent key.doc.standard key.topic.skill-contract -->
## Parent 기준서

1. `../01_key-project-standard.md`
   - Keystone 공통 용어, Main supervisor 책임, 실행 역할 제한, progress/report status
     분리, 기준서-led verification, Coordinator anchor를 정의한다.

<!-- key: id=key.standard.subagent.index.reading-rules refs=key.role.subagent key.doc.standard key.topic.work-execution key.standard.subagent -->
## 읽기 규칙

1. Subagent purpose preset, authority, report status, workspace guard를 정의하거나 변경할 때는
   `../01_key-project-standard.md`의 `STD-KEYSTONE-030`, `STD-KEYSTONE-031`,
   `STD-KEYSTONE-032`, `STD-KEYSTONE-043`을 먼저 확인한다.
2. Coordinator가 어떤 subagent를 선택해야 하는지 검토할 때는
   `key-standard-subagents.md`를 읽은 뒤 `../skills/coordinator/key-standard-coordinator.md`를
   읽는다.
3. Parent 기준서와 이 기준서가 충돌하면 충돌을 보고하고 사용자 또는 main의 결정(6)을
   받는다. 결정 전까지는 parent 기준서를 임시 우선 기준으로 삼는다.
