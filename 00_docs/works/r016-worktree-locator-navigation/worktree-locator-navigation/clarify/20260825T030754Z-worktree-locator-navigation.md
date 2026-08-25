# Worktree locator and targeted work discovery

## G01 - Worktree locator와 owner 실행 순서

### Q01 - R015와 별도 Work로 분리할지

- 질문: 이 요구를 R015에 반영할지, 별도 Work로 생성할지
- 답변: R015와 별개로 작업을 생성한다.
- 답변일시: 2026-08-25

### Q02 - Worktree 탐색과 누락 위험을 어떻게 다룰지

- 질문: 전체 worktree 탐색이나 atomic claim 대신 Work Order 키메타의 locator에 의존할지
- 답변: Worktree에서 최초 작업을 시작하면 작업 전에 Work Order 키메타에 위치를 기록하고,
  탐색은 기록에 의존한다. 기록 누락은 사용자의 기억에 맡긴다.
- 답변일시: 2026-08-25

### Q03 - Worktree 생성과 키메타 기록 owner를 어떻게 나눌지

- 질문: Coordinator가 worktree를 생성·선택하고 Author가 canonical Work Order 키메타를 기록한
  뒤 Reader와 Coordinator가 그 기록을 소비하는 역할 분리를 적용할지
- 답변: 네, 그 역할 분리와 실행 순서로 진행한다.
- 답변일시: 2026-08-25T03:07:54Z
