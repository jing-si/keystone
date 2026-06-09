---
doc_type: work_package
work_package_id: WP-KEYSTONE-SKILL
title: Keystone Skill-System Foundation
status: active
owner_lane: main-session
work_type:
  - skill-design
  - documentation
  - implementation
risk_level: medium
---

# WP-KEYSTONE-SKILL: Keystone 스킬 시스템 기반

## 요약

이 작업 패키지는 Keystone 스킬 시스템의 첫 버전을 정의하고 구축한다. 최종 산출물은
공유 기준서(3)와 작업서(4)를 통해 협력하는 네 개의 독립 스킬이다.

1. Clarification 스킬: 정책, 범위, 문서 결정사항을 명확히 한다.
2. Authoring 스킬: 기준서와 작업서를 작성한다.
3. Reading/work-preparation 스킬: 기준서와 작업서를 읽고 작업을 준비한다.
4. Subagent coordination 스킬: subagent 작업 배정과 보고 흐름을 조율한다.

이 프로젝트는 사람이 읽을 수 있는 문서에서 시작한다. 의도한 workflow가 구현 전에
안정적인 기준서, 작업서, 진행 상태(progress status), 결정 기록(decision record)에
의존하기 때문이다.

Keystone은 날짜 기반의 일회성 planning flow와 의도적으로 다르다.

1. 기준서: 장기 정책과 결정(6)을 담는다.
2. 작업서: 현재 AI 작업의 구체적 goal, execution unit, report condition,
   verification path를 담는다.
3. Superpowers: brainstorming, planning, TDD, debugging, review, skill testing을 위한
   명시적 quality-assist 참고 자료로만 사용한다.
4. 권위: 수락된 Keystone 원천 문서(2)가 계속 권위를 가진다.

## 목표

다음 flow를 지원하는 유지보수 가능한 Keystone 스킬 시스템을 만든다.

1. 기준서와 작업서를 읽는다.
2. Main agent가 현재 goal과 context를 복구한다.
3. 필요한 경우 subagent coordination으로 bounded work를 배정한다.
4. Main agent가 report, repair, verification, acceptance를 감독한다.

## 담당 영역

담당 영역은 다음처럼 나눈다.

1. Main session
   - standards interpretation
   - work-order update
   - scope control
   - skill-boundary 결정(6)
   - final acceptance
2. Subagent
   - main session이 구체적 Context Pack을 준비한 뒤에만 사용한다.
   - bounded investigation, implementation, review에만 사용한다.

Main agent는 bulk executor가 아니라 supervisor로 동작해야 한다. Context를 보존하고,
role-based goal을 subagent에게 배정하며, report를 받고, repair를 결정하고, 최종 결과를
accept하거나 reject한다.

## 원천 기준서

주 기준서:

- `00_docs/standards/00_project-standard.md`

보조 참고:

- 향후 authoring 스킬을 위한 참고용 prototype인 `work-package-doc-architect`
- 향후 coordination 스킬을 위한 참고용 prototype인 `subagent-work-coordinator`

## 문서

1. 작업서(4): `00_work-order.md`
2. 진행 기록(5): `progress.md`
3. 결정 기록(decision record): `decisions.md`

별도 `scope.md`나 `agent/` 문서는 아직 만들지 않는다. 구체적인 유지보수 또는
coordination 필요가 생길 때만 추가한다.

## 현재 구조 메모

이 패키지는 `works/` tree 정책이 수락되기 전에 만들어졌기 때문에 현재
`00_docs/work-packages/` 아래에 남아 있다. 자동으로 이동하지 않는다. 기존 문서를
migration하기 전에 사용자에게 묻는다. 새 Keystone 작업 문서는
`00_docs/works/` tree를 사용해야 한다.

## 현재 상태

- Status: active
- Current step: S01

## 완료 기준

- 프로젝트가 최소 `00_docs/` 원천 문서(2) set을 가진다.
- Keystone 스킬 시스템 goal이 명확히 기록되어 있다.
- 네 개의 계획된 Keystone 스킬 역할이 명확히 기록되어 있다.
- `keystone-clarify` topic 결정(6) workflow가 명확히 기록되어 있다.
- Superpowers integration boundary가 선택적이고 명시적인 것으로 기록되어 있다.
- main-agent supervisor model과 role-based subagent model이 명확히 기록되어 있다.
- document root, standards/works tree, final file naming policy가 명확히 기록되어 있다.
- reader mode, progress/report status, 파생 에이전트 문서(8) policy,
  standards-led verification이 명확히 기록되어 있다.
- 작업서 step은 향후 coordination 스킬이 현재 step을 복구하고 runtime Context Pack을
  만들 수 있도록 구조화되어 있다.
- 문서 기반이 main session에 의해 수락되거나 수정되기 전에는 구현을 시작하지 않는다.
