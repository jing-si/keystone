---
doc_type: work_order
tags:
  - 작업서
  - 기준서
  - 원천문서
  - 문서체계
  - 스킬계약
---

# Project Standard 작업서(4)

<!-- tags: 작업서, 기준서, 문서체계 -->
## Goal

`00_docs/standards/00_KEY-project-standard.md`를 현재 `works/` 구조와 네 Keystone 스킬 역할에
맞게 parent 기준서로 정리한다.

<!-- tags: 기준서, 원천문서, 문서체계, 스킬계약 -->
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

<!-- tags: 원천문서, 기준서, 문서체계 -->
## Source Context

- `00_docs/standards/00_KEY-project-standard.md`
- `00_docs/standards/00_KEY-index.md`
- `00_docs/standards/skills/00_KEY-index.md`
- `00_docs/works/00_KEY-index.md`

<!-- tags: 검증, 기준서, 스킬계약 -->
## Completion Criteria

- [ ] Parent 기준서가 현재 works tree를 설명한다.
- [ ] Child 기준서가 참조하는 STD ID가 유지된다.
- [ ] 전체 기준서가 상세 계약을 과도하게 반복하지 않는다.
- [ ] Approval, progress, verification policy가 명확하다.

<!-- tags: 기준서, 문서체계 -->
## Recommended Approach

Parent 기준서는 공통 정책과 child link에 집중한다. 스킬별 상세 규칙은 별도 work에서 다룬다.

<!-- tags: 작업서, 기준서, 문서체계 -->
## Context Pack Seed

- `00_docs/works/KEY-decisions.md`
- 현재 S00-S07 실행 순서
- child 기준서 목록

<!-- tags: 범위, 기준서, 스킬계약 -->
## Stop Conditions

- STD ID를 제거해야 할 것처럼 보인다.
- 새 high-impact 정책 결정이 필요하다.
- child 기준서 전체 재작성 없이는 충돌을 해소할 수 없다.

<!-- tags: 검증, 기준서 -->
## Verification

Allowed:

- `rg -n "STD-KEYSTONE|works/" 00_docs/standards/00_KEY-project-standard.md`
- `git diff --check`

<!-- tags: 기준서, 문서체계 -->
## Expected Output

- 현재 구조와 일치하는 parent 기준서

<!-- tags: review, 기준서, 문서체계 -->
## Review Points

- 기준서가 작업 순서를 직접 관리하지 않는지 확인한다.
- child 기준서로 내려가는 navigation이 명확한지 확인한다.

<!-- tags: progress-update, 작업서 -->
## Progress Record

S01 완료는 main acceptance 후에만 `KEY-progress.md`에 기록한다.
