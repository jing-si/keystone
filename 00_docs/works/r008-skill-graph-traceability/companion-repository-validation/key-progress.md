---
doc_type: progress
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: pending}
work_status: planned
step_ref: R008/S04
work_ref: R008/companion-repository-validation
key:
  id: key.work.companion-repository-validation.progress
  refs:
    - key.topic.progress-update
    - key.topic.artifact-graph
    - key.topic.keystone-metadata
    - key.topic.verification
---

# Companion and Repository Validation 진행 기록

## 현재 상태

- Step: R008/S04
- Work status: planned
- Approval state: pending
- Active: false
- Finalization state: not started
- Resume point: binary companion와 repository completeness RED fixture 작성

Active steps: []

## 준비 증거

- Non-UTF-8 binary와 valid adjacent companion을 reconstruct하면 source text의 불필요한 UTF-8
  decode에서 `UnicodeDecodeError`가 발생한다.
- Companion physical patch target `<source>.keystone.json`과 logical graph source `<source>`가
  transaction omission 검사에서 같은 identity로 normalize되지 않는다.
- 6 MiB Markdown fixture의 `coverage: full` validation은 `source_too_large` warning과 exit 0을
  반환했다.
- Full manifest의 `ghost.md`는 `declared - discovered` 검사 부재로 diagnostic 없이 통과했다.
- Discovery는 raw bytes를 보존하지만 graph reconstruction은 path에서 source를 다시 읽는다.

## 다음 작업

1. Logical source identity와 physical patch surface wire를 분리한다.
2. Binary companion full transaction E2E를 작성한다.
3. Full/subset completeness envelope와 양방향 source-set 검사를 구현한다.
4. Captured bytes 또는 freshness recheck로 mixed generation을 막는다.
