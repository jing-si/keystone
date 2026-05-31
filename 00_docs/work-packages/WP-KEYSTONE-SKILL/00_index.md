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

# WP-KEYSTONE-SKILL: Keystone Skill-System Foundation

## Summary

This work package defines and builds the first version of the Keystone
skill-system. The final output is four new independent skills that cooperate
through shared 기준서 and 작업서 documents:

- a policy, scope, and document-decision clarification skill
- a standards/work-order authoring skill
- a standards/work-order reading and work-preparation skill
- a subagent coordination skill

The project starts with human-readable documents because the intended workflow
depends on stable standards, work orders, progress state, and decisions before
implementation begins.

Keystone intentionally differs from date-based one-off planning flows. Reusable
기준서 hold long-lived policies and decisions, while 작업서 hold the concrete
goal, execution units, report conditions, and verification path for current AI
work. Superpowers can still be used as an explicit quality-assist reference for
brainstorming, planning, TDD, debugging, review, or skill testing, but accepted
Keystone source documents remain authoritative.

## Goal

Create a maintainable Keystone skill-system that supports the flow:
기준서 + 작업서 -> main agent -> subagent coordination.

## Responsible Area

The main session owns standards interpretation, work-order updates, scope
control, skill-boundary decisions, and final acceptance. Subagents may be used
later only for bounded investigation, implementation, or review after the main
session prepares a concrete Context Pack.

The main agent should act as a supervisor rather than a bulk executor. It
preserves context, assigns role-based goals to subagents, receives reports,
decides repairs, and accepts or rejects the final result.

## Source Standards

Primary:

- `00_docs/standards/00_project-standard.md`

Supporting:

- `work-package-doc-architect` as a prototype reference for the future
  authoring skill
- `subagent-work-coordinator` as a prototype reference for the future
  coordination skill

## Documents

- Work order: `00_work-order.md`
- Progress: `progress.md`
- Decisions: `decisions.md`

No separate `scope.md` or `agent/` documents are created yet. Add them only
when a concrete maintenance or coordination need appears.

## Current Structure Note

This package currently remains under `00_docs/work-packages/` because it was
created before the `works/` tree policy was accepted. Do not move it
automatically. Ask the user before migrating existing documents. New Keystone
work documents should use the `00_docs/works/` tree.

## Current Status

- Status: active
- Current step: S01

## Completion Criteria

- The project has a minimal `00_docs/` source document set.
- The Keystone skill-system goal is stated clearly.
- The four planned Keystone skill roles are stated clearly.
- The `keystone-clarify` topic decision workflow is stated clearly.
- The Superpowers integration boundary is stated as optional and explicit.
- The main-agent supervisor model and role-based subagent model are stated
  clearly.
- The document root, standards/works tree, and final file naming policies are
  stated clearly.
- Reader modes, progress/report statuses, derived document policy, and
  standards-led verification are stated clearly.
- Work order steps are structured so the future coordination skill can recover
  the current step and build runtime Context Packs.
- Implementation is not started until the document foundation is accepted or
  amended by the main session.
