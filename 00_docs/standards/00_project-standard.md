# Keystone Project Standard

## Purpose

This standard defines the project-wide rules for building the Keystone
skill-system. The project goal is to create four new independent skills that
turn human-readable 기준서 and 작업서 documents into a structured clarification,
authoring, reading, and main-agent to subagent work system.

## Applies To

- Standards and work packages under `00_docs/`
- The future Keystone skill source files
- Policy, scope, document, and skill-contract clarification behavior
- Standards/work-order authoring behavior
- Standards/work-order reading and work-preparation behavior
- Runtime coordination behavior between main agent and subagents
- Documentation that must remain compatible with the future Keystone
  coordination skill

## Does Not Apply To

- Unrelated local IDE files
- External installed skills except where they are used as prototype references
- Automatic use of external workflow skills without explicit user invocation or
  an accepted Keystone document rule
- Persistent worker handoff documents unless explicitly requested

## Core Rules

### STD-KEYSTONE-001: Human-readable source documents are authoritative

기준서, 작업서, progress records, decisions, and scope documents must remain
readable by a person. Agent-facing runtime packs, handoffs, and reviewer briefs
are derived from source documents and must not override them.

### STD-KEYSTONE-002: 기준서 and 작업서 have separate responsibilities

기준서 define project policies, standards, domain rules, and reusable guidance.
작업서 define the concrete work goal, scope, sequence, completion criteria,
stop/report conditions, and verification path for AI work.

### STD-KEYSTONE-003: 기준서 may form a parent-child hierarchy

Large standards should be split through meaningful parent and child 기준서. A
parent 기준서 should summarize feature names, short descriptions, and reference
documents so main can navigate to the final detailed 기준서 needed for the
current work.

### STD-KEYSTONE-004: Coordinator compatibility is a first-class requirement

Every work order step must contain enough information for the main agent to
derive a Current Step Brief, Context Pack, worker handoff boundaries, reviewer
focus, stop conditions, and verification path.

### STD-KEYSTONE-005: Main owns orchestration decisions

Subagents may investigate, implement bounded work, or review a diff only after
main has provided concrete context. Subagents must not reinterpret the full work
order, expand scope, or spawn additional subagents.

### STD-KEYSTONE-006: Work must be recoverable from documents

If a user says "run the next step", main should be able to recover the current
step, goal, completion criteria, standards, expected scope, risks, and
verification from `00_docs/`.

### STD-KEYSTONE-007: Source document changes require explicit approval

Meaningful changes to standards, work orders, scope, acceptance criteria, or
progress state require explicit approval. Related but unapproved changes should
be reported instead of silently applied.

### STD-KEYSTONE-008: Minimal structure comes before expansion

Use the minimal `00_docs/` structure first. Add scope, decisions, coordination,
change request, or derived agent documents only when the work needs them.

### STD-KEYSTONE-009: Keystone skills are explicitly invoked

Keystone should assume the user explicitly names the skill they want to use.
The skill-system must not depend on broad automatic activation. If another
workflow skill such as Superpowers is useful, use it only when the user invokes
it or an accepted Keystone 기준서 or 작업서 explicitly permits that use.

### STD-KEYSTONE-010: 기준서 reduce repeated context

Long-lived project policy, architecture, conventions, domain rules, and reusable
decisions belong in 기준서. 작업서 should reference those 기준서 instead of
copying the same policy into each dated or one-off task document.

### STD-KEYSTONE-011: 작업서 slice work for goal assignment

작업서 should divide work into units that can be assigned as clear goals. Each
unit needs a purpose, scope, completion criteria, stop/report conditions,
verification, and the 기준서 references needed to do the work without rereading
the whole project.

### STD-KEYSTONE-012: Main agent is the supervisor

The main agent should preserve its context and act as supervisor: recover the
goal, read only necessary documents, prepare assignments, route work to
role-based subagents, receive reports, decide repairs, and make final
acceptance decisions.

### STD-KEYSTONE-013: Subagents are role-based, not speed-first

Subagents should be selected by role such as explorer, code modifier, reviewer,
or verifier. Parallelism is allowed only when goals and write scopes are clearly
independent. Correctness, context preservation, and report quality take priority
over raw speed.

### STD-KEYSTONE-014: Superpowers is an optional quality-assist layer

Superpowers may help during document creation or implementation design. For
example, an authoring skill may define the document location, format, and
required sections while Superpowers brainstorming helps refine the actual
infra, server, or code-development content inside those sections. Superpowers
outputs are supporting input; Keystone 기준서 and 작업서 remain the source of
truth after acceptance.

### STD-KEYSTONE-015: Document root resolution is explicit and ordered

Document paths must be English. The default root is `00_docs/`. If multiple
instructions mention a document root, resolve it in this order: current user
instruction, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `agent.md`, then default
`00_docs/`.

### STD-KEYSTONE-016: Standards and works use index-based trees

Future 기준서 live under `standards/` and future 작업서 live under `works/`.
Both trees may have unlimited depth. Every node has `00_index.md`; child links
and common rules guide readers downward. A node with no child documents is the
final node.

### STD-KEYSTONE-017: Final detail files use local slugs

Final 기준서 files use `standard-{slug}.md`. Final 작업서 files use
`work-{slug}.md`. Progress files use `progress.md`. The slug should be the
shortest local name that clearly distinguishes the file inside its folder.

### STD-KEYSTONE-018: Work steps are Goal units

작업서 steps should be written as assignable Goal units. Each step should be
small enough for one role-based subagent assignment and clear enough for main
to judge the report as accept, repair, verify, or escalate.

### STD-KEYSTONE-019: Reader has three modes

`keystone-reader` supports Orientation Mode, Navigator Mode, and Work Prep Mode.
Orientation Mode creates a compact project map from instructions, document
root, standards/works structure, active work, major code areas, and documents
to read. Navigator Mode finds relevant documents. Work Prep Mode prepares Goal,
context, verification, and role suggestions without finalizing subagent
handoffs.

### STD-KEYSTONE-020: Derived agent documents are optional but supported

Keystone may keep four derived agent document types when useful:
`agent/00_agent-pack.md`, `agent/step-context.md`,
`agent/worker-handoff.md`, and `agent/reviewer-brief.md`. Do not create them
by default. If source documents change, update any affected derived documents
with them. Source documents always win on conflict.

### STD-KEYSTONE-021: Impact updates preserve document consistency

When a source document change clearly affects related parent, child, work,
progress, decision, or derived agent documents, update those related documents
together. If the impact range or meaning change is uncertain, stop and ask the
user before editing uncertain documents.

### STD-KEYSTONE-022: Progress and report status are separate

Progress status describes workflow state: `planned`, `ready`, `assigned`,
`reported`, `reviewing`, `verifying`, `accepted`, or `blocked`. Subagent report
status describes a returned report: `DONE`, `DONE_WITH_CONCERNS`,
`NEEDS_CONTEXT`, `NEEDS_SCOPE_CHANGE`, or `BLOCKED`.

### STD-KEYSTONE-023: Verification is standards-led

기준서 define the primary verification expectations. Main extracts relevant
verification criteria from 기준서 and passes them to workers as a Verification
Checklist. When needed, main assigns a separate verification Goal to a verifier
subagent. 작업서 may add local verification notes but should not silently weaken
기준서 verification.

### STD-KEYSTONE-024: Skill source lives in the repository

The repository is the source of truth for the four Keystone skills:
`skills/keystone-clarify`, `skills/keystone-author`,
`skills/keystone-reader`, and `skills/keystone-coordinator`. The initial
distribution shape is a skills repo, with room to add plugin metadata later.

### STD-KEYSTONE-025: Clarify is topic-scoped and mode-aware

`keystone-clarify` is used for high-impact decisions that affect policy, source
documents, work scope, skill contracts, or cross-document consistency. It should
not turn every minor edit into a question. In Plan Mode, it gathers the
questions and decisions needed for one topic, using `request_user_input` or an
equivalent selection UI when available. After the topic is sufficiently decided,
it summarizes the reflection and document update plan. In Default Mode, related
source documents are updated together, including affected standards, works,
progress, decisions, and optional derived agent documents.

## Expected Behavior

- A main agent can inspect `00_docs/context-map.md` to find active standards and
  work packages.
- A clarification skill can gather topic-scoped high-impact decisions before
  source documents are changed.
- A main agent can inspect a work package and identify the current step from
  `progress.md`.
- A document-reading skill can locate only the relevant 기준서 and 작업서 needed
  for the current requested work.
- A document-reading skill can run Orientation, Navigator, or Work Prep Mode
  according to the user's request.
- People and LLMs can follow `00_index.md` files downward through standards and
  works trees without loading unrelated branches.
- Reusable 기준서 keep common policy out of repeated task documents.
- A work order step can be converted into a bounded subagent task without
  requiring the subagent to rediscover the whole project.
- The main agent can assign role-based goals to subagents and make final
  decisions from their reports.
- Superpowers can be used as an explicit supporting workflow without replacing
  Keystone source documents.
- Derived agent documents can be created when useful without becoming source
  documents.
- High-risk work is documented as requiring main or user decision before
  implementation.

## Existing Patterns To Reuse

- `work-package-doc-architect` document structure and templates as a prototype
  reference for the future authoring skill
- `subagent-work-coordinator` orchestration loop, Context Pack rules, scope
  model, stop conditions, and review loop as a prototype reference for the
  future coordination skill

## Forbidden Changes Without Approval

- Changing the meaning of the Keystone skill-system goal
- Collapsing the four planned Keystone skills into one skill without approval
- Treating the prototype skills as final dependencies
- Editing source documents from an incomplete high-impact clarification topic
- Automatically invoking Superpowers or any external workflow skill without user
  instruction or accepted document authorization
- Replacing reusable 기준서 with repeated dated task documents
- Creating future active 작업서 under `work-packages/` instead of `works/`
  without user approval
- Adding a `leaf` metadata field where child presence already determines final
  node status
- Treating derived agent documents as source documents
- Marking work complete before main acceptance
- Adding persistent agent-facing handoff documents by default
- Expanding work into implementation code, schema, generated output, or global
  configuration changes without a work order step and approval

## Escalation Conditions

- The source documents conflict with the current user direction
- The boundary between the four planned Keystone skills is unclear
- A high-impact clarification topic cannot be resolved confidently
- A requested workflow would make Superpowers output more authoritative than
  accepted Keystone 기준서 or 작업서
- A work unit cannot be assigned as a clear goal with reviewable output
- A document change has unclear impact on related standards, works, progress,
  decisions, or derived agent documents
- A step needs API contract, schema, auth/security, generated/codegen, or shared
  architecture changes
- The current step, completion criteria, or applicable standard cannot be
  recovered confidently
- A subagent result may overwrite user or other-agent changes
- Verification cannot be run or fails for an unclear reason

## Related Work Packages

- `00_docs/work-packages/WP-KEYSTONE-SKILL/00_index.md`
