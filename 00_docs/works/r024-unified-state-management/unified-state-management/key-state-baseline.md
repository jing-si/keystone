---
doc_type: work_scope
created_at: "2026-10-12"
document_lifecycle: active
approval: {state: pending}
key:
  id: key.work.unified-state-management.baseline
  refs:
    - key.work.unified-state-management.order
    - key.standard.project
---

# 상태 관리 현황과 비용 기준선

R024/S01의 중간 조사 기록이다. 새 상태 모델이나 S01 완료 수락을 대신하지 않는다.
기준 commit은 `5194901`이며 측정은 R024 활성화 문서 변경 전에 수행했다.

## 현재 상태의 권위와 소비자

| 종류 | 현재 소유 위치 | 소비 경로와 이전 시 확인 대상 |
|---|---|---|
| Round | Round Index의 round_status·approval | Work State의 hierarchy, session-title의 후보 필터 |
| Work | aggregate key-progress.md의 work_status·approval | Work State와 Linker dependency; legacy Work Index fallback |
| Step | combined 또는 개별 Step Progress | Work State active_steps·Step 후보·소유권 검증 |
| 문서 lifecycle·승인 | 각 원천 문서 frontmatter | Linker metadata·effective authority; 작업 상태와 별도 의미 |
| 최종 정리 | Progress의 선택적 finalization | 후속 구현 gate·Author 복구; complete와 수락만으로 대체 불가 |
| 선택적 실행 phase | ready·assigned·reported·reviewing·verifying 등 | 현재 기본 work_status와 별도; 사용 범위 추가 조사 필요 |

Project STD-KEYSTONE-019/020/024/055/058과 Author Progress ownership가 근거다.
현재 기본 작업 상태는 planned·in_progress·blocked·complete·cancelled·superseded다.
ready는 선택적 phase이고 running은 현재 기본 상태값이 아니다.
생성·수락·결정일 기록은 있으나 모든 상태 전이의 날짜를 전수 기록하는 계약은 아니다.

## 구현 영향 경로

- `scripts/work_state_runtime.py`: `_discover_sources`는 works 전체에서 지원 source를 수집한다.
  `_effective_work_states`는 aggregate Progress를, `_dependency_evaluations`는 실행·승인 조건을
  읽는다. `derive_work_state`의 Round·Step 및 historical compatibility 해석도 함께 확인해야 한다.
- `scripts/generate_work_state_runtimes.py`: canonical runtime을 Reader·Author·Coordinator의
  package-local 사본과 manifest로 생성한다. 한 사본만 수정하면 독립 package 계약이 깨진다.
- `skills/keystone-linker/scripts/graph_runtime/dependency.py`: 별도로 aggregate Progress 상태를
  읽고 기본 complete + accepted 조건을 판정한다. Work State만 고쳐서는 소비자가 일치하지 않는다.
- `skills/keystone-reader/scripts/keystone_session_title.py`: hierarchy의 status에서 accepted·cancelled를
  제외하고 complete를 수락 대기로 표시한다. open/closed 전환 시 이 경계도 바뀐다.
- 관련 검증 후보: `skills/tests/test_work_state_runtime.py`, session-title runtime/contract,
  `skills/keystone-linker/tests/test_dependency_runtime.py`, Author finalization tests.

위 연결은 소스의 실제 읽기 경로에서 확인한 영향 후보이며 새 typed relation 선언은 아니다.
위 작업서와 구현 4개 파일의 bounded owner/ref 탐색은 원문 5개를 확보했다. 외부 참조 owner는
범위 밖이어서 owner_unresolved가 남았다. 전체 그래프 정합성이나 impact 완결성을 주장하지 않는다.
탐색 source digest: `sha256:22996f1c68a165c047afafc1e05d5fc6e393990283627303434a5dc9459929f1`.

## 대표 전이의 현재 갱신 후보

| 전이 | 상태 소유자 갱신 | 추가 대조 후보 | 검증 경로 |
|---|---|---|---|
| Step 완료·수락 | Step Progress; combined라면 aggregate와 분리 | aggregate 활성 Step, Work Order 실행 표, 해당 Round 요약 | Work State 소유권·active_steps, 승인 근거 |
| Work 완료·수락 | aggregate Progress | Work Index 선택적 상태, Round 집계와 실행 표 | effective Work state·dependency 일치 |
| Round 수락·종료 | Round Index 및 완료 근거 | root works index·Context Map의 해당 Round 요약 | parent/child 조건, terminal reconciliation |

현재 Author 계약은 존재하는 현재 요약만 대조하고 historical 서술은 보존한다.
위 표는 모든 전이에 모든 파일을 수정한다는 뜻이 아니다.
R023에는 상태 필드·현재 요약 후보가 9개 Markdown 파일, R018에는 10개 파일에 나타난다.
범위는 해당 Round subtree와 root works index·Context Map이며 work_status·round_status·approval,
Active Step과 해당 Round 표 행을 검색했다. 이 수치는 서로 다른 Step 소유자도 포함하므로
중복 사본 수나 실제 수정 파일 수로 해석하지 않는다.

## 측정 조건과 결과

- 명령: `PYTHONDONTWRITEBYTECODE=1 python3 scripts/work_state_runtime.py --root .`
- 동일 current worktree에서 독립 subprocess 3회, Python 시작 비용 포함, perf_counter로 측정했다.
- 결과: 0.0683 / 0.0650 / 0.0678초. 모든 실행 pass, 오류·경고 없음.
- 읽은 source: 251개. active parent는 R015, active Step은 R015/S01이었다.
- source generation: `sha256:052027e87b5d335faadcbeabb406e4f28f3581001eee88ed91366fb26df604b4`.
- 기존 common/contract suite: 144개 실행, 143개 통과, 환경 조건 1개 skip, 10.439초.

이 결과는 현재 읽기 비용이다. 디스크 cache를 통제한 벤치마크나 실제 상태 쓰기 비용이 아니며
개선 효과를 입증하지 않는다. S04 비교 시 같은 입력 규모·명령·측정 방식으로 재측정한다.
실제 전이별 수정 파일·반복 기록 수, 쓰기·검증 비용과 규모 증가 효과는 아직 미측정이다.

## 다음 결정과 남은 조사

1. 사용자는 실행·승인·최종 정리를 독립 항목으로 유지하기로 했다. 기준서 자체의 승인·lifecycle도
   별도 문서 상태 영역으로 이전할지는 확인 중이다. 작업의 open/closed와 문서 유효성은 구분한다.
2. 상태 종류별 기록 단위와 문서 승인·lifecycle의 이전 방식, 종료 사유 및 날짜 미확인 처리,
   부분 반영·동시 수정 복구 계약을 S02에서 확정한다.
3. 종료 문서의 직접 조회와 일상 조회의 no-history-scan 경계를 검증할 fixture를 준비한다.
4. R025의 계층 정의나 R026의 아이디어 기록 범위를 이번 조사만으로 변경하지 않는다.

## 2026-10-12 구현 fixture 검증

실제 corpus 개편은 사용자가 설치 이후 별도 작업으로 분리했다. 아래 측정은 소급 이전 성능의
전후 비교가 아니라 새 조회가 관계없는 이력 수에 따라 확대되지 않는지 확인한 것이다.

- 조건: 동일 임시 repository, open Round 2개·Work 2개·Step 4개, 활성 marker 포함.
  동일 프로세스에서 evaluate_repository를 각 5회 실행해 perf_counter 중앙값을 비교했다.
- 관계없는 과거 파일 0개: source 5개, 중앙값 0.008361초, pass.
- 같은 fixture에 관계없는 과거 파일 1,000개 추가: source 5개, 중앙값 0.008378초, pass.
- 두 조건 모두 state 파일 2개·marker 1개·현재 Work Order 2개만 조회했다.
  이는 초기 legacy corpus 251개에 대한 subprocess 측정과 입력·측정 방식이 달라 속도 배율로
  비교하지 않는다. 디스크 cache를 통제한 성능 보장도 아니다.
- 일반 update의 지속 원본 수정은 Round state 파일 1개이며 작업서 bytes는 동일하다.
  create/close/reopen은 해당 state 파일과 사건을 추가할 작업서 2개를 변경한다.
  일시적인 lock·pending transaction은 지속 원본 수에 포함하지 않는다.
- Exact closure dependency만 해당 작업서를 추가 조회하고, 다른 archived 문서는 읽지 않는
  fixture 검증을 통과했다. 소급 개편 전후의 실제 프로젝트 지표는 후속 작업에서 측정한다.

## 2026-10-13 단일 상태 파일 정정 검증

위 2026-10-12 수치는 당시 분산 파일 구현의 역사적 측정이다. 최신 계약은 `state/current.json`
한 파일의 상태별 목록이며 이전 수치를 현행 구현의 성능 결과로 사용하지 않는다.

- 50개 Round를 서로 다른 상태 그룹에 등록해 실제 상태 파일이 1개이고 조회 source도 1개임을 검증했다.
- 일반 상태 변경도 current.json과 해당 작업서 2개를 갱신한다. 작업서에는 변경 전후·날짜·사유를
  append하며 다른 색인·참고 문서에는 상태값을 복제하지 않는다. 조회는 작업서 0개를 읽는다.
- 마지막 항목 종료 후 상태 파일에는 빈 states만 남는다. closed 항목·과거 사건은 포함하지 않는다.
- Round가 달라도 동일한 전체 파일 digest를 사용하므로 stale writer가 다른 Round 변경을 덮어쓰지 못한다.
- update 도중 중단한 fixture에서 recover 후 그룹 이동과 작업서 로그가 함께 일치함을 확인했다.
- 실제 운영 corpus의 소급 개편과 그 이후 성능 측정은 스킬 교체 뒤 후속 작업으로 남긴다.
