---
doc_type: progress
created_at: "2026-10-12"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-10-12", accepted_by: main}
work_status: complete
work_ref: R018/keymeta-bounded-discovery
step_ref: R018/S04
key:
  id: key.work.keymeta-bounded-discovery.progress.verification
  refs: [key.work.keymeta-bounded-discovery.order]
---

# R018/S04 소비 규모 검증과 종료

## 검증 결과

- Linker package 전체: 394개 통과 (13.370초).
- Shared/contract suite: 144개 실행, 실패 없음. Python 3.9 환경에서 `tomllib`가 필요한 1개 skip.
- Reader package: 3개 통과.
- Bounded discovery 회귀 18개: exact owner, mode, unresolved/stale/duplicate, budgets, rooted include,
  symlink/root escape, companion-only, unsupported source와 legacy plain JSON 호환을 포함한다.
- Parse reuse 회귀 2개: targeted expansion+view의 Kotlin lexical scan 1회와 raw-byte 변경 무효화.
- 기존 supported language·malformed metadata·companion·source view·dependency/wire 회귀 통과.
- 임시 설치 runtime의 bounded_discovery/scanner/adapters/readiness byte parity와 독립 v4 CLI 통과.
  실제 사용자 설치 경로는 갱신하지 않았다. Installer source 변경도 없다.
- 임시 pycache 경로에서 compileall, `git diff --check` 통과.
- R018 Work anchor의 `produces`를 따라 readiness·metadata parser 소스 3개만 읽는 self-host 검증 통과.
  `ReferenceScanner._paths` 호출을 금지해 전체 열거가 없음을 검증했다.

## 성능 근거

### 동일 환경 파서 비교

351,579-byte Kotlin 입력을 이전 HEAD adapter와 변경 adapter에서 각각 1회 측정했다.
입력은 `key.code.benchmark` anchor와 `val normalField = 12345 + otherField` 줄 9,500개다.
기존 3.189811초, 변경 0.185760초로 17.17배 개선됐으며 metadata blocks는 동일하다.
이 값은 해당 fixture·환경의 단일 비교이며 모든 소스의 속도 보장은 아니다.

### 읽기 전용 Uptendo 검증

사용자가 제공한 `/Users/joung/workspace/uptendo`의 다음 Work를 anchor로 사용했다.
`00_docs/works/r019-board-comment-management/r019-A/board-comment-collection/key-work-board-comment-collection.md`
Work의 recorded worktree도 동일한 root다.

- 해당 Work 문서, board worker 기준, API Board controller·test·migration, common Board test와
  board MyBatis source 중 확인한 35개 경로, 331,750 bytes를 명시적으로 전달했다.
- Source view 포함 targeted readiness: 0.073172 / 0.069930 / 0.070538초.
- Whole-tree enumeration 0회, skipped source 0개, source digest 측정 전후 동일.
- Path-set digest: `sha256:f7bb1e05edcff86360cf0d22277fd447dbe1ea247d8d0baded214d70aa94109c`.
- Source generation: `sha256:915ae92e72cb14f2e1fd059fb63f2ae371f659e8c0fd95c145e17116e2af97d0`.
- 범위 밖 refs는 `owner_unresolved`, `bounded_coverage_incomplete`, `complete: false`로 반환했다.
  이는 repository 전체 관계 복구나 consumer acceptance를 뜻하지 않는다.

## 회귀 발견과 수정

최종 회귀에서 legacy docs scan이 일반 JSON 이력 파일을 새 unsupported error로 보고하는 문제가
발견됐다. 기존 mode-less 경로에서는 원래 admission을 보존하고, explicit targeted source만 해당
diagnostic을 보고하도록 수정한 뒤 회귀 테스트를 추가했다. 공유 suite의 일시적인 임시 Git 디렉터리
정리 오류는 독립 재실행에서 재현되지 않았으며 최종 전체 shared suite는 실패 없이 끝났다.

## 경계와 수락

- Routine Reader/Linker는 명시적 targeted v4를 사용한다. Mode 없는 v2/v3는 기존 caller 호환용으로
  유지하며 신규 routine preparation에 사용하지 않는다. 제거에는 별도 migration 검증이 필요하다.
- Cache를 새 authoritative registry로 만들지 않았다. Bounded 경로는 캐시를 열지 않고 source를
  직접 읽으며, 알려진 owner locator를 current bytes에 다시 결속한다.
- 기존 Artifact Graph·Linker 상세 기준서는 pending으로 유지했다. R018 의미의 accepted 권위는
  Project 기준서의 R018 계약이며, unrelated pending 정책을 수락하지 않았다.
- Browser, 소비 프로젝트 수정, publish, 실제 전역 설치와 R015 변경은 수행하지 않았다.

Main은 S01~S03 산출물과 위 검증을 대조해 S04와 R018을 complete / accepted로 수락했다.
Owning Progress·Round·root index·Context Map을 정합화하고 fresh Work State로 종료를 확인한다.
