---
doc_type: work_order
created_at: "2026-07-25"
status: active
approval:
  state: accepted
  accepted_at: "2026-07-25"
  accepted_by: main
work_status: accepted
key:
  id: key.work.dependency-integration-verification.order
  refs:
    - key.doc.work
    - key.topic.integration-verification
    - key.topic.artifact-graph
    - key.topic.work-recovery
---

# Dependency Integration Verification 작업서

<!-- key: id=key.work.dependency-integration-verification.order.goal refs=key.section.goal key.topic.integration-verification -->
## Goal

수락된 dependency/work gate 기준과 repo-local runtime source가 대표 정상·오류·불확실
시나리오에서 일관된 판정을 제공하는지 검증하고 R003의 최종 수락 근거를 만든다.

<!-- key: id=key.work.dependency-integration-verification.order.precondition refs=key.topic.work-sequence key.step.s02 -->
## 선행 조건

- S01 기준과 결정이 수락되어야 한다.
- S02 repo-local `SKILL.md` 구현이 완료되어야 한다.

<!-- key: id=key.work.dependency-integration-verification.order.scope refs=key.section.scope key.topic.verification -->
## Scope

Include:

- 문서 fixture 또는 정적 input/output scenario
- 기준서, 결정, skill source의 관계 목록과 상태 의미 비교
- legacy HTML과 structured metadata의 호환 및 충돌 판정
- R007/R008 형태의 단계별 pipeline false-cycle 검증
- 신규 ID, link, index, status, Markdown과 YAML 정합성 검증
- 결과에 따른 progress, Context Map과 round index 동기화

Exclude:

- 브라우저·Playwright 검증
- production parser, scheduler 또는 UI 구현
- Uptendo repository 직접 검증이나 수정
- global install, plugin packaging, marketplace와 publish

<!-- key: id=key.work.dependency-integration-verification.order.scenarios refs=key.topic.integration-verification key.topic.artifact-graph -->
## 검증 시나리오

1. Dependency가 없는 작업
2. 충족된 legacy work-level dependency
3. 미충족 dependency가 있지만 독립 step은 진행 가능한 작업
4. S08-S11과 source 완료만 target complete를 기다리는 structured gate
5. 존재하지 않는 target
6. Self-dependency와 duplicate dependency
7. 직접적인 work-level cycle
8. Work-level로는 cycle처럼 보이지만 expanded step graph는 비순환인 pipeline
9. Target이 cancelled 또는 superseded인 경우
10. Legacy HTML과 structured metadata가 일치하는 경우
11. 두 표현이 충돌하는 경우
12. 존재하지 않는 source step ID
13. Optional dependency
14. Unknown relation 또는 알 수 없는 work status

<!-- key: id=key.work.dependency-integration-verification.order.expected refs=key.contract.output key.topic.work-recovery -->
## 기대 판정

각 시나리오는 `satisfied`, `waiting`, `unresolvable`, `invalid`, `unknown` 중 하나와 근거를
제공해야 한다. 어떤 판정도 source 문서의 lifecycle, approval 또는 `work_status`를 자동으로
변경하지 않아야 한다.

<!-- key: id=key.work.dependency-integration-verification.order.completion refs=key.topic.acceptance key.topic.verification -->
## Completion Criteria

- [x] 14개 시나리오의 기대 판정과 실제 runtime 계약 해석이 일치한다.
- [x] R007/R008 pipeline이 false cycle로 확정되지 않는다.
- [x] dangling, self, duplicate, invalid step과 실제 cycle이 구분된다.
- [x] Bootstrap, Artifact Graph, Linker와 runtime source의 관계 목록이 일치한다.
- [x] Reader와 Coordinator가 dependency 판정만으로 상태나 할당을 변경하지 않는다.
- [x] Author가 structured metadata와 본문 권위를 일관되게 유지한다.
- [x] 신규 `key.id`, path, link, index, status와 temporal metadata가 유효하다.
- [x] `git diff --check`와 Markdown/YAML 구조 검사를 통과한다.
- [x] Global install, packaging, publish와 Uptendo source는 변경되지 않았다.
- [x] Main이 실제 결과와 residual risk를 검토하고 R003을 수락했다.

<!-- key: id=key.work.dependency-integration-verification.order.verification refs=key.topic.verification -->
## Verification

- `git diff --check`
- 신규 `key.id` duplicate와 index/path/link 존재 검사
- frontmatter YAML parse와 Markdown fence 균형 검사
- 기준서와 `skills/keystone-*/SKILL.md` relation/status vocabulary 비교
- 14개 scenario의 expected classification table 검토
- 변경 파일이 R003 Change Set 범위 안인지 확인

<!-- key: id=key.work.dependency-integration-verification.order.stop refs=key.boundary.stop-condition -->
## Stop Conditions

1. S01과 S02가 수락되지 않았거나 서로 충돌한다.
2. 문서 fixture만으로 검증할 수 없어 executable 구현의 별도 승인이 필요하다.
3. Uptendo 또는 외부 저장소 접근·수정이 필요하다.
4. 기존 변경을 보존할 수 없거나 scope가 packaging/install/publish로 확장된다.
