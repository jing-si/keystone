# Keystone Project Standard

## Purpose

This standard defines the project-wide rules for building the Keystone
skill-system. The project goal is to create four new independent skills that
turn human-readable 기준서 and 작업서 documents into a structured clarification,
authoring, reading, and main-agent to subagent work system.

## Applies To

- Standards and work packages under `00_docs/`
- The future Keystone skill source files
- Keystone project setup and project-local Keystone settings
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

Meaningful changes to accepted standards, work orders, scope, acceptance
criteria, or progress state require explicit approval. While a work step is
`in_progress`, edits inside that step's approved work scope may be made by
main. Changes that alter the approved goal, scope, acceptance criteria, status
semantics, or source-document authority still require explicit approval.
Related but unapproved changes should be reported instead of silently applied.

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

Document paths must be English. `00_docs/` is the default root, not a fixed
root. Current user instruction may override the document root for the current
run. Persistent project-local settings are resolved in this order:
`.keystone/config.local.yaml`, `.keystone/config.yaml`, then an explicit
Keystone settings block in a project-local agent instruction file. Common or
globally injected instruction files such as `AGENTS.md`, `CLAUDE.md`,
`GEMINI.md`, or `agent.md` may provide setup suggestions, but they do not
become persistent Keystone settings until accepted into project-local settings.
When a configured project-local root exists, Keystone uses that root even if
`00_docs/` does not exist.

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
to judge the report as accept, repair, verify, or escalate. Every work step
must include `Goal`, `Scope`, `Source Context`, `Completion Criteria`,
`Stop Conditions`, `Verification`, and `Expected Output`. These fields are
required for recoverability and coordinator compatibility, but their content
may be short for simple or low-risk steps. `Scope` should include
Include/Exclude boundaries when useful. `Suggested Role` is optional and
recommended when delegation is likely; main may choose or override the role.

### STD-KEYSTONE-019: Reader has three modes

`keystone-reader` supports Orientation Mode, Navigator Mode, and Work Prep Mode.
Orientation Mode is document-led, repository-aware, and read-only. It creates a
compact project orientation from instructions, document root, standards/works
structure, active work, and a shallow repository snapshot. Its output should
include `document_root`, `project_summary`, `repository_snapshot`,
`active_document_map`, `current_work_status`, `recommended_read_order`,
`operational_boundaries`, `risks_and_gaps`, `recommended_next_action`,
`sources_read`, and `assumptions`. The repository snapshot is limited to the
repository root, top-level directories, key config/build files, expected
skill/source directories, Git status summary, and obvious document-to-repository
mismatch signals. If source documents and repository state conflict,
Orientation Mode must report the mismatch and ask the user or main agent to
choose whether to update documents, prepare code work, or investigate further.
It must not modify documents, code, config, progress, decisions, or generated
files. Navigator Mode finds relevant documents. Work Prep Mode prepares Goal,
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

Progress status describes workflow state: `planned`, `ready`, `in_progress`,
`assigned`, `reported`, `reviewing`, `verifying`, `accepted`, or `blocked`.
`in_progress` means main is actively working inside the approved work scope.
`assigned` means a subagent or separate worker owns the current unit. Subagent
report status describes a returned report: `DONE`, `DONE_WITH_CONCERNS`,
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
equivalent selection UI when available. After the topic is sufficiently decided
and the user or main session accepts the decision summary and edit plan, it
summarizes the reflection and document update plan. In Default Mode, accepted
related source-document updates are applied together, including affected
standards, works, progress, decisions, and optional derived agent documents.

### STD-KEYSTONE-026: Initial project setup is recorded in Keystone config

On first Keystone use in a project, Keystone checks for existing project
settings before asking setup questions. If settings are missing or the document
root decision is unclear, `keystone-clarify` should ask setup questions in Plan
Mode with `request_user_input` or an equivalent selection UI when available.
Common or globally injected settings may be shown as recommended choices, but
they must not be accepted silently. The accepted shared project settings are
recorded in `.keystone/config.yaml` by default so future Keystone runs do not
repeat the same setup questions. Personal, local-only, or sensitive overrides
belong in `.keystone/config.local.yaml`. If the user explicitly prefers an
existing project-local agent instruction file, Keystone may record a Keystone
settings block there instead. Keystone must never write to common or globally
injected instruction files.

Initial setup should cover at least:

- document root: default `00_docs/`, an existing project document folder, or a
  newly specified folder
- source document Git policy for 기준서 and 작업서
- derived agent document Git policy
- Keystone output language policy
- setup storage location: `.keystone/config.yaml` by default, or an explicit
  project-local agent instruction file if the user chooses it

The default shared config schema is:

```yaml
version: 1
document_root: 00_docs
source_docs_git_policy: track_standards_and_works
derived_agent_docs_git_policy: ignore
output_language_policy: dominant_conversation_language
```

### STD-KEYSTONE-027: Source document Git policy is explicit

Keystone treats 기준서 and 작업서 as source documents, but their Git publication
policy is a project setting rather than an assumption. During initial setup,
`keystone-clarify` should explain the tradeoff and offer choices equivalent to:
track 기준서 and 작업서, track 기준서 only, track neither, or ask for each document
change. Derived agent documents are ignored by Git by default unless explicitly
approved. `.keystone/config.yaml` is shared project policy and is tracked by
Git by default. `.keystone/config.local.yaml` is a local/private override and is
ignored by Git by default. Documents or settings containing secrets,
credentials, private user data, customer data, local-only paths, sensitive
environment details, or unpublished business information require user
confirmation before writing, tracking, publishing, or deriving documents from
that content.

### STD-KEYSTONE-028: Output language policy applies only to Keystone artifacts

Keystone output language is a project setting for Keystone-generated artifacts
only: clarification prompts, 기준서, 작업서, Keystone summaries, handoffs, and
reports. It must not override the user's requested language for unrelated
tasks, code comments, commit messages, README files, external tools, or
non-Keystone skills. If the user explicitly requests a language for a specific
task, that task-specific instruction wins. Initial setup should offer choices
equivalent to dominant current conversation language, existing project document
language, English, or ask each time.

## Expected Behavior

- A main agent can inspect `00_docs/context-map.md` to find active standards and
  work packages.
- A clarification skill can gather topic-scoped high-impact decisions before
  source documents are changed.
- Keystone can record initial project settings in `.keystone/config.yaml` and
  reuse them on later runs.
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
- 기준서 and 작업서 Git policy can be chosen per project without making derived
  agent documents tracked by default.
- Shared Keystone config can be tracked while local/private overrides remain
  ignored by default.
- Keystone artifact language can be configured without changing unrelated task
  language.
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
- Creating a new document root before checking current instruction files and
  project-local Keystone settings
- Writing Keystone setup results to common or globally injected instruction
  files
- Treating common/global instruction settings as persistent project settings
  without project-local acceptance
- Tracking or publishing sensitive source documents without explicit approval
- Letting Keystone output language override unrelated user requests, code,
  commits, README files, external tools, or non-Keystone skills
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
- Initial project settings are missing and document root, Git policy, or
  Keystone output language cannot be inferred safely
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
