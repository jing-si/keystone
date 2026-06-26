---
doc_type: work_order
key:
  id: key.work.project-standard.order
  refs:
    - key.doc.work
    - key.doc.standard
    - key.doc.source
    - key.topic.document-system
    - key.topic.skill-contract
---

# Project Standard 작업서(4)

<!-- key: id=key.work.project-standard.order.goal refs=key.doc.work key.doc.standard key.topic.document-system -->
## Goal

`00_docs/standards/01_key-project-standard.md`를 현재 `works/` 구조와 네 Keystone 스킬 역할에
맞게 parent 기준서로 정리한다.

<!-- key: id=key.work.project-standard.order.scope refs=key.doc.standard key.doc.source key.topic.document-system key.topic.skill-contract -->
## Scope

Include:

- 표준 용어
- 원천 문서(2)와 파생 에이전트 문서(8) 권위
- `standards/`와 `works/` tree 정책
- progress/report status
- verification과 acceptance policy
- 네 스킬의 상위 역할

Exclude:

- 스킬별 상세 계약 중복 작성
- Skill source 생성
- S02-S07 progress 변경

Conditionally allowed:

- Child 기준서와 충돌하는 좁은 parent rule 보정

<!-- key: id=key.work.project-standard.order.source-context refs=key.doc.source key.doc.standard key.topic.document-system -->
## Source Context

- `00_docs/standards/01_key-project-standard.md`
- `00_docs/standards/00_key-index.md`
- `00_docs/standards/skills/00_key-index.md`
- `00_docs/works/00_key-index.md`
- `00_docs/works/r001-bootstrap-keystone/00_key-index.md`

<!-- key: id=key.work.project-standard.order.completion-criteria refs=key.topic.verification key.doc.standard key.topic.skill-contract -->
## Completion Criteria

- [ ] Parent 기준서가 현재 works tree를 설명한다.
- [ ] Child 기준서가 참조하는 STD ID가 유지된다.
- [ ] 전체 기준서가 상세 계약을 과도하게 반복하지 않는다.
- [ ] Approval, progress, verification policy가 명확하다.

<!-- key: id=key.work.project-standard.order.recommended-approach refs=key.doc.standard key.topic.document-system -->
## Recommended Approach

Parent 기준서는 공통 정책과 child link에 집중한다. 스킬별 상세 규칙은 별도 work에서 다룬다.

<!-- key: id=key.work.project-standard.order.context-pack-seed refs=key.doc.work key.doc.standard key.topic.document-system -->
## Context Pack Seed

- `00_docs/works/key-decisions.md`
- 현재 S00-S07 실행 순서
- child 기준서 목록

<!-- key: id=key.work.project-standard.order.stop-conditions refs=key.section.scope key.doc.standard key.topic.skill-contract -->
## Stop Conditions

- STD ID를 제거해야 할 것처럼 보인다.
- 새 high-impact 정책 결정이 필요하다.
- child 기준서 전체 재작성 없이는 충돌을 해소할 수 없다.

<!-- key: id=key.work.project-standard.order.verification refs=key.topic.verification key.doc.standard -->
## Verification

Allowed:

- `rg -n "STD-KEYSTONE|works/" 00_docs/standards/01_key-project-standard.md`
- `git diff --check`

<!-- key: id=key.work.project-standard.order.expected-output refs=key.doc.standard key.topic.document-system -->
## Expected Output

- 현재 구조와 일치하는 parent 기준서

<!-- key: id=key.work.project-standard.order.review-points refs=key.topic.review key.doc.standard key.topic.document-system -->
## Review Points

- 기준서가 작업 순서를 직접 관리하지 않는지 확인한다.
- child 기준서로 내려가는 navigation이 명확한지 확인한다.

<!-- key: id=key.work.project-standard.order.progress-record refs=key.topic.progress-update key.doc.work -->
## Progress Record

S01 완료는 main acceptance 후에만 `key-progress.md`에 기록한다.
