---
doc_type: progress
created_at: "2026-10-12"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-10-12", accepted_by: main}
work_status: complete
work_ref: R026/idea-notes
step_ref: R026/S03
key:
  id: key.work.idea-notes.progress.verification
  refs: [key.work.idea-notes.order, key.standard.skill.ideas]
---

# R026/S03 검색 품질·관리 비용 검증

## 검증 결과

- Helper: `python3 -B -m unittest discover -s skills/keystone-ideas/tests` — 17개 통과.
- 설치/release 연결: `test_release_gate_security.py` — 7개 통과. Clean 임시 사본에서
  실제 staging·manifest·rollback을 확인하며 사용자 전역 설치는 수행하지 않는다.
- Reader progressive context 5개, source ownership 계약 4개, standards-first 계약 5개 통과.
- 신규 기준·작업서·스킬·코드의 affected graph: 오류·경고 0.
- 스킬 frontmatter/name/description/placeholder/fence: 저장소 parser로 검사 통과.
  Skill Creator quick_validate는 환경의 PyYAML 부재로 실행되지 않았다. 새 dependency는 추가하지 않았다.
- Dirty 작업 트리에 release 전용 installer check를 직접 호출한 추가 시도는
  `source_dirty`를 허용하지 않는 manifest 비교에서 거절됐다. 깨끗한 임시 fixture의
  installer 회귀는 통과했다. 전체 repository release gate 통과로 주장하지 않는다.

## Main의 합성 시나리오 점검

12개 노트(검색 CSV, 정기 보고서 이메일, 로그인 문자 인증, 다크 모드, XLSX 내보내기,
다국어 정렬, 첨부파일 용량, 알림 묶음, 키보드 탐색, PDF 보고서, 기간 필터, 실패 재시도)를
임시 소비 프로젝트에 넣었다. 현재 Main이 스킬 절차에 따라 검색어를 선택하고 실제 helper
결과·본문을 읽어 아래 관련성을 판단했다. 독립 모델 평가나 운영 정확도 측정은 아니다.

| 요청 의미 | 검색 표현 | 기계 후보 | Main 판단 |
|---|---|---|---|
| 엑셀로 뽑는 아이디어 | 엑셀 / CSV / 내보내기 | 001, 005 | 두 후보 모두 관련 |
| 로그인 본인 확인 | 로그인 / 문자 / 일회용 | 003 | 문자 인증 관련 |
| 야간 눈부심 | 야간 / 눈부심 / 다크 | 004 | 다크 모드 관련 |
| 보고서 인쇄용 파일 | 다운로드 / 보고서 | 001, 002, 010 | 본문 확인 후 010만 관련, 두 incidental 후보 제외 |
| 음성 녹음 | 음성 / 녹음 | 없음 | 검색 범위에서 없음으로 안내, 의미적 부재를 단정하지 않음 |

관련 항목이 알려진 위 4건에서 선택 누락은 없었다. 이 작은 자기 점검을 일반 검색 recall로
확대하지 않는다. 유사 등록은 001·005의 공통 표와 한 질문을 만들고 원문 bytes 무변경을
확인했다. 합성 답변 "001에 관리자 전용 추가" 뒤 해당 본문만 편집하고 원래 날짜와
나머지 11개 항목의 의미를 보존했다. 별도 013을 생성하고 실제 삭제한 뒤 원문 바이트가
돌아오고 다음 번호가 다시 013임을 확인했다. 삭제 결과도 직전 항목의 공통 표로 생성했다.

## 합성 규모 관찰

12개 핵심 사례에 무관한 짧은 노트를 추가해 같은 검색을 수행했다. 각 규모에서 파일 하나를
일관성 확인까지 두 번 읽는다. 시간은 한 번의 로컬 관찰이며 성능 보장/상한이 아니다.

| 노트 수 | 원문 bytes | 실제 읽은 bytes | 반환 항목 | JSON 출력 bytes | 관찰 scan ms |
|---|---:|---:|---:|---:|---:|
| 12 | 2049 | 4098 | 2 | 1413 | 0.40 |
| 50 | 23139 | 46278 | 2 | 1415 | 0.57 |
| 200 | 106490 | 212980 | 2 | 1418 | 2.02 |

출력 문맥량은 제한되지만 파일 읽기는 선형 증가한다. 이 결과는 DB·인덱스 또는 자동 분할을
도입할 근거가 아니다. 실제 반복 주제와 읽기 부담이 생기면 승인된 범위에서만 분할한다.

## 한계와 수락

자연어 관련성은 AI 판단이며 검색 완전성을 보장하지 않는다. 읽기 digest 재확인은
원자적인 다중 writer 잠금이 아니다. 동시 변경·중복 ID를 감지하면 쓰기를 멈추고 사용자
편집을 보존한다. 스킬 지침의 모든 대화 분기를 자동 시험한 것으로 주장하지 않는다.
Main은 이 한계를 숨기지 않는 초기 스킬과 관련 검증 범위를 수락했다.
