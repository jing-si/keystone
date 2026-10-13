---
doc_type: progress
created_at: "2026-10-12"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-10-12", accepted_by: main}
work_status: complete
work_ref: R025/work-hierarchy-definition
step_ref: R025/S03
key:
  id: key.work.work-hierarchy-definition.progress.verification
  refs: [key.work.work-hierarchy-definition.order, key.standard.project]
---

# R025/S03 정의 일관성 검증

## 사례 대조

아래 결과는 수락 대상 기준의 의미·문서 대조이며 새 형식의 runtime 실행 테스트가 아니다.

| 사례 | 생성·지정·변경·종료·복구 판단 | 결과 |
|---|---|---|
| Work 없는 작은 Round | 사용자 생성 Round가 전체 목표·완료 조건을 소유하고 Step을 직접 지정·복구. 숨은 Work 없이 Step 검증 후 상위 완료 판단 | Project STD-026, Author·Reader와 일치 |
| 사용자가 특정 과제를 Work로 지정 | 같은 Round 안의 section으로 구분, Work의 범위·완료 조건·Step 소속을 기록. 사용자 구분과 충돌하는 재분할은 사용자 판단 | Project STD-026, Author와 일치 |
| AI가 복수 Work를 생성 | 독립 결과·완료 조건·범위·의존성 분리의 실익 확인 후 생성, 이유·관계 사후 안내. 완료 조건 약화·상위 범위 확대 금지 | Uptendo R004 용례와 생성 권한 계약에 적용 가능 |
| 새 부모·하위 Round 필요 | AI는 권유하고 사용자 결정 대기. Work 생성 권한으로 Round를 대신 만들지 않음 | Project 용어·STD-026, Author·Coordinator 경계 일치 |
| Task 없는 Step | Step의 Goal·Scope·완료 조건·검증으로 실행·수락. 빈 Task 문서·상태 불필요 | 기존 Goal unit 유지 |
| 여러 Task가 있는 Step | AI가 수정·생략 가능, 남은 항목·제약 등 재개 정보만 Step 기록에 보존. Task 체크 완료와 Step 수락을 분리 | G01/Q01 및 Project·Author·Reader와 일치 |
| Work 파일 분리 | 기본은 Round 작업서 section, 크기·독립 관리 필요 시 분리하고 참조. 같은 계약·상태 복제 금지 | G01/Q02와 일치, 모든 Work의 파일 생성 의무 없음 |
| 복수 Work의 Step 번호 | local Round에서 새 S번호 중복 금지, 과거 중복은 source path로 식별하고 번호·수락 이력 보존 | 기존 STD-026 번호 원칙과 R004 조사 결과 정합화 |
| 하위 Round와 단일 Work 중첩 | Work 분리 실익이 없으면 목표 모델에서 생략 가능. 기존 R019-A 문서는 이동·합치지 않음 | 선택적 단위와 과거 기록 보존을 분리 |
| 저장 모드 전환 전 복구 | 기존 Work node·Progress와 R024 wire 유지. 신규 모델의 기계 처리 지원을 주장하지 않음 | Project·Author·Reader·관리 상태 기준의 적용 경계 일치 |

## 후속 적용 범위

1. 별도 승인할 구현: Work 없는 Round→Step과 한 작업서 안의 복수 Work·Step 소속·locator를
   runtime·schema가 복구하도록 확장하고 dependency·finalization·선택·종료 검증을 보강한다.
2. Skill source/template: Author 생성·안내·질답 위치, Reader/Coordinator 선택과 복구를
   위 계약에 맞춘다. 문서상의 규칙만으로 설치본 동작 변경을 주장하지 않는다.
3. R024 후속 전환: 상태 parent·order locator와 소비자 지원을 함께 검증한 뒤 corpus 이전·
   설치를 명시적으로 수행한다. Task는 독립 상태 항목으로 추가하지 않는다.
4. 기존 Work·Step ID·경로·수락 이력은 보존한다. 임의 새 Round 생성·소급 재번호화는 하지 않는다.

## 검증 범위와 한계

기준서의 역할·생성·파일·상태·수락 경계를 위 사례로 대조했다. Coordinator 개발 기준서는
전체 pending을 유지하며 이 범위의 정책 권위는 수락된 Project 기준이다. 구현·설치·이전은
R025 Scope 밖이므로 검증 완료 대상으로 계산하지 않는다. 비용 감소 실측·전체 graph 감사도
수행하지 않았으며 bounded source 대조와 Work State 검증으로 이번 문서 변경을 확인한다.

## 검증 결과와 Main 수락

- 다섯 기준서의 변경 직전 baseline과 현재 diff를 직접 검토했다. 기존 metadata comment,
  frontmatter 및 관련 없는 변경을 보존했고 새 의미를 위 10개 사례와 대조했다.
- `git diff --check`가 통과했다. R025 문서·공통 색인·Context Map 및 관련 기준 범위의
  형식 검증이며 코드 테스트를 수행한 것으로 표현하지 않는다.
- `python3 -B scripts/work_state_runtime.py --root .`가 pass, diagnostics `[]`로
  R015/S01과 R025/S03을 복구했다. S01·S02 수락과 S03 실행 상태가 source와 일치했다.
- Main은 정의·기준·사례 검증과 후속 적용 범위 명시를 확인해 S03 및 R025 문서 범위를
  수락한다. 종료 상태를 반영한 후 같은 Work State 조회로 최종 source 정합성을 확인한다.
- 종료 후 repository 및 설치된 Reader의 Work State가 모두 pass, diagnostics `[]`로
  R025를 accepted 이력에서 복구했다. active_rounds `[R015]`, active_steps `[R015/S01]`로
  다른 작업을 보존했고 R025 활성 Step은 없다. 이 검증은 기존 형식의 종료 복구 확인이다.
- 최종 `git diff --check`, 다섯 기준서의 기존 frontmatter·metadata 보존, R025 Markdown
  링크·code fence 및 두 질답의 답변 기록 검사를 통과했다.
