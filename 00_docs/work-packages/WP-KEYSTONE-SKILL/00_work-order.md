# WP-KEYSTONE-SKILL Work Order

This work order is a human-readable execution plan. It is also structured so the
future Keystone coordination skill can derive Current Step Briefs and Context
Packs at runtime.

## Work Package

- ID: WP-KEYSTONE-SKILL
- Overview: `00_index.md`
- Progress: `progress.md`

## Source Standards

Primary:

- `00_docs/standards/00_project-standard.md`

Supporting:

- `work-package-doc-architect` as a prototype reference
- `subagent-work-coordinator` as a prototype reference

## Overall Scope

Included:

- Create and maintain the `00_docs/` source documents for the Keystone
  skill-system
- Define the four intended Keystone skill roles before implementation
- Define the final skill names: `keystone-clarify`, `keystone-author`,
  `keystone-reader`, and `keystone-coordinator`
- Define the `keystone-clarify` Plan Mode decision collection and Default Mode
  document update workflow
- Define document root resolution and English path rules
- Define initial project setup behavior and Keystone config files
- Define 기준서 and 작업서 Git policy choices
- Define Keystone output language policy boundaries
- Define the future `standards/` and `works/` tree policies
- Define how reusable 기준서 and current 작업서 reduce repeated context
- Define how Superpowers can be used as an explicit supporting workflow without
  replacing Keystone source documents
- Define the main-agent supervisor model and role-based subagent model
- Define reader modes, derived document policy, progress/report statuses, and
  standards-led verification
- Shape work order steps so main can later coordinate subagents safely
- Identify when work can be delegated and when main or user decision is needed

Excluded:

- Implementing the skill source code in this document step
- Creating persistent `agent/` handoff documents by default
- Modifying installed external skills or prototype skills
- Automatically invoking Superpowers without explicit user instruction or
  accepted document authorization
- Moving existing `work-packages/` documents to `works/` without user approval
- Broad project setup, build tooling, publishing, or marketplace integration
  unless approved in a later step

Conditionally allowed:

- Small document refinements that keep the approved skill-system goal unchanged
- Adding `scope.md` only if the next accepted work requires it
- Recording accepted policy decisions in `decisions.md`

## Steps

## Step S01. Establish Document Foundation

### Purpose

Create the minimal source document set for the Keystone skill-system project so
the main session can recover the project goal, standards, current step, scope,
verification path, and next action.

### Completion Criteria

- [ ] `00_docs/context-map.md` exists and links active standards and work
  packages.
- [ ] `00_docs/standards/00_project-standard.md` defines project-wide rules for
  document authority, the four planned skill roles, and coordinator
  compatibility.
- [ ] `00_docs/work-packages/WP-KEYSTONE-SKILL/00_index.md` states the package
  goal, status, source standards, and current step.
- [ ] `00_docs/work-packages/WP-KEYSTONE-SKILL/00_work-order.md` contains
  coordinator-compatible steps.
- [ ] The foundation records that Keystone uses reusable 기준서 and 작업서 instead
  of repeated dated planning documents as the primary context source.
- [ ] The foundation records that Superpowers is optional, explicit, and
  subordinate to accepted Keystone source documents.
- [ ] The foundation records the accepted document root, tree, and file naming
  policies.
- [ ] The foundation records initial project setup, Keystone config files,
  source document Git policy, and Keystone output language policy.
- [ ] The foundation records the reader modes, derived document policy,
  progress/report statuses, and standards-led verification policy.
- [ ] `00_docs/work-packages/WP-KEYSTONE-SKILL/progress.md` records the current
  step without marking implementation complete.

### Related Standards

- Standard: `00_docs/standards/00_project-standard.md`
- Related rules: `STD-KEYSTONE-001`, `STD-KEYSTONE-002`,
  `STD-KEYSTONE-003`, `STD-KEYSTONE-004`, `STD-KEYSTONE-008`,
  `STD-KEYSTONE-009`, `STD-KEYSTONE-010`, `STD-KEYSTONE-011`,
  `STD-KEYSTONE-012`, `STD-KEYSTONE-013`, `STD-KEYSTONE-014`,
  `STD-KEYSTONE-015`, `STD-KEYSTONE-016`, `STD-KEYSTONE-017`,
  `STD-KEYSTONE-018`, `STD-KEYSTONE-019`, `STD-KEYSTONE-020`,
  `STD-KEYSTONE-021`, `STD-KEYSTONE-022`, `STD-KEYSTONE-023`,
  `STD-KEYSTONE-024`, `STD-KEYSTONE-025`, `STD-KEYSTONE-026`,
  `STD-KEYSTONE-027`, `STD-KEYSTONE-028`

### Work Scope

Included:

- `00_docs/context-map.md`
- `00_docs/standards/00_project-standard.md`
- `00_docs/work-packages/WP-KEYSTONE-SKILL/00_index.md`
- `00_docs/work-packages/WP-KEYSTONE-SKILL/00_work-order.md`
- `00_docs/work-packages/WP-KEYSTONE-SKILL/progress.md`
- `00_docs/work-packages/WP-KEYSTONE-SKILL/decisions.md`

Excluded:

- Skill implementation files
- Optional `agent/` documents
- Optional `scope.md` unless a concrete need appears
- Changes outside `00_docs/`
- Changes to prototype installed skills
- Superpowers workflow execution
- Moving existing `work-packages/` documents to `works/` without user approval

Conditionally allowed:

- Naming or wording refinements inside the listed documents that preserve the
  stated Keystone skill-system goal

### Recommended Approach

This step is documentation creation and should be handled by the main session
using `work-package-doc-architect`. Do not send a worker unless the main session
first prepares a narrow documentation Context Pack and decides review is needed.
The prototype skill is used only to shape documents; it is not a final Keystone
dependency.

### Context Pack Seed

When preparing a later subagent handoff, main should include:

- The Keystone skill-system goal from `00_index.md`
- The four planned skill roles from `context-map.md`
- The explicit Superpowers integration boundary from `00_project-standard.md`
- The main-agent supervisor and role-based subagent rules from
  `00_project-standard.md`
- Document tree, file naming, derived document, progress/report, and
  verification rules from `00_project-standard.md`
- Initial project setup, Keystone config, Git policy, and Keystone output
  language rules from `00_project-standard.md`
- Project rules from `00_project-standard.md`
- Current step and status from `progress.md`
- The included and excluded scope above
- The rule that derived agent documents are not created by default
- Verification by file existence and structure checks

### Stop And Report Conditions

- The user changes the intended Keystone skill-system goal
- A document change would alter standards, scope, or acceptance criteria beyond
  this approved foundation
- A document change would make Superpowers automatic or more authoritative than
  accepted Keystone source documents
- A document change would migrate existing package paths without user approval
- Implementation files are needed before document acceptance
- Optional documents appear necessary but have not been approved
- Verification shows missing or inconsistent document links

### Verification Method

Allowed checks:

- `rg --files 00_docs`
- Read the created Markdown files for structure and link consistency

Forbidden until explicitly allowed:

- Skill implementation changes
- Persistent `agent/` documents
- Generated files
- Broad formatting or repository cleanup

### Review Points

Reviewer should check:

- Minimal document set exists under `00_docs/`
- Documents are human-readable source documents, not agent-only config
- Keystone's Superpowers integration is explicit and bounded
- The main-agent supervisor model is reflected in the documents
- The accepted tree/file/status/verification policies are reflected in the
  documents
- The work order can produce a Current Step Brief and Context Pack
- Optional documents were not created without need
- Progress does not falsely mark implementation complete

### Progress Record

Record progress in `progress.md`. Complete S01 only after the main session
accepts the document foundation.

## Step S02. Define Keystone Skill-System Contract

### Purpose

Turn the project goal into explicit contracts for the four planned Keystone
skills: trigger conditions, non-goals, required inputs, document creation and
reading behavior, main/subagent role split, runtime outputs, and failure or
escalation behavior.

### Completion Criteria

- [ ] The four planned Keystone skill roles are described in source documents
  or approved implementation notes.
- [ ] The final skill names are `keystone-clarify`, `keystone-author`,
  `keystone-reader`, and `keystone-coordinator`.
- [ ] Trigger and non-trigger conditions are clear for each skill.
- [ ] `keystone-clarify` trigger boundary, Plan Mode topic collection, and
  Default Mode document update behavior are clear.
- [ ] 기준서 and 작업서 responsibilities are clear.
- [ ] Parent-child 기준서 navigation behavior is clear.
- [ ] `standards/` and `works/` tree rules are clear.
- [ ] `00_index.md`, `standard-{slug}.md`, `work-{slug}.md`, and
  `progress.md` file naming rules are clear.
- [ ] Initial project setup and Keystone config behavior are clear.
- [ ] 기준서 and 작업서 Git policy choices are clear.
- [ ] Keystone output language policy is scoped to Keystone artifacts only.
- [ ] Reusable 기준서 vs dated/repeated task document behavior is clear.
- [ ] Derived agent document types and creation/update conditions are clear.
- [ ] `keystone-reader` Orientation, Navigator, and Work Prep modes are clear.
- [ ] Orientation Mode output is document-led, repository-aware, read-only, and
  includes mismatch reporting without automatic fixes.
- [ ] Explicit Superpowers integration conditions are clear.
- [ ] Main-agent supervisor responsibilities are clear.
- [ ] Role-based subagent responsibilities are clear.
- [ ] Goal assignment behavior for subagent-sized work units is clear.
- [ ] Work step fields are clear: `Goal`, `Scope`, `Source Context`,
  `Completion Criteria`, `Stop Conditions`, `Verification`, and
  `Expected Output` are required; `Suggested Role` is optional.
- [ ] Progress status and subagent report status are separate and defined.
- [ ] Standards-led verification and handoff checklist behavior are clear.
- [ ] Main-agent responsibilities and subagent limits are clear.
- [ ] Required document inputs and runtime outputs are defined.
- [ ] Escalation conditions are aligned with the future coordination skill.

### Related Standards

- Standard: `00_docs/standards/00_project-standard.md`
- Related rules: `STD-KEYSTONE-001`, `STD-KEYSTONE-002`, `STD-KEYSTONE-003`,
  `STD-KEYSTONE-004`, `STD-KEYSTONE-005`, `STD-KEYSTONE-006`,
  `STD-KEYSTONE-007`, `STD-KEYSTONE-009`, `STD-KEYSTONE-019`,
  `STD-KEYSTONE-021`,
  `STD-KEYSTONE-025`, `STD-KEYSTONE-026`, `STD-KEYSTONE-027`,
  `STD-KEYSTONE-028`

### Work Scope

Included:

- Skill contract content for the four planned Keystone skills
- Source document updates needed to capture approved behavior
- Identification of reusable behavior from `work-package-doc-architect` and
  `subagent-work-coordinator` as prototype references
- Superpowers integration rules as an optional supporting workflow
- Goal assignment and role-based subagent boundaries
- Work step field contract for coordinator-compatible 작업서 steps
- Clarify mode contract for topic-scoped decision collection and reflection
- Initial setup contract for `.keystone/config.yaml` and
  `.keystone/config.local.yaml`
- 기준서 and 작업서 Git publication policy choices
- Keystone output language policy boundaries
- Reader mode contracts
- Orientation Mode output contract and document-to-repository mismatch policy
- Document tree and filename contracts
- Progress/report status contracts
- Derived document and impact update contracts
- Standards-led verification contracts

Excluded:

- Implementation code before the contract is accepted
- Changing external installed skills
- Collapsing the four planned Keystone skills into one skill
- Making Superpowers mandatory or automatic
- Replacing reusable 기준서 with repeated dated task documents
- Creating a persistent runtime handoff format unless explicitly approved
- Migrating the current `work-packages/` package to `works/` without user
  decision

Conditionally allowed:

- Update `decisions.md` when accepted contract decisions change or accumulate
- Add a dedicated standard document if `00_project-standard.md` becomes too broad

### Recommended Approach

Main should draft the contract from the current documents and user direction.
If ambiguities materially affect behavior, use the future `keystone-clarify`
contract: gather the questions and decisions for one topic in Plan Mode, use
`request_user_input` or an equivalent selection UI when available, summarize the
reflection and edit plan, then apply the related source-document updates
together in Default Mode. This step may use a read-only explorer only to inspect
existing skill examples or local skill conventions. Superpowers may be used as a
supporting workflow only when explicitly invoked or when an accepted Keystone
standard/work order allows a specific quality-assist use. For example, Keystone
authoring can define the document format, location, and required sections for an
infra setup 기준서 or 작업서 while Superpowers brainstorming helps refine the
actual infra, server, and code-development content.

### Context Pack Seed

When preparing a subagent handoff, main should include:

- Current Keystone skill-system goal and non-goals
- The four planned skill roles and their boundaries
- The `keystone-clarify` topic decision workflow and accepted decisions
- Initial project setup and Keystone config rules
- Source document Git policy and Keystone output language policy
- Accepted document tree and file naming policies
- Reader modes and expected outputs
- Orientation Mode repository snapshot and read-only mismatch handling
- Superpowers as optional supporting input, not source of truth
- 기준서 as reusable long-lived policy and 작업서 as goal-oriented execution
  document
- Work step field contract and optional `Suggested Role` rule
- Main-agent supervisor model and role-based subagent model
- Progress/report statuses
- Standards-led verification checklist rules
- Relevant rules from `00_project-standard.md`
- The exact documents or skill examples to inspect
- Boundaries against modifying installed external skills
- Expected output format for findings or proposed contract text

### Stop And Report Conditions

- The contract would change the approved skill-system goal
- The contract would blur the boundary between the four planned skills
- The contract would require source-document edits from an incomplete
  high-impact clarification topic
- The contract would make Superpowers mandatory, automatic, or authoritative
  over accepted Keystone documents
- The contract would prevent work from being sliced into role-based goals
- The contract would make derived agent documents mandatory by default
- The contract would weaken 기준서-led verification
- The contract would make source document Git tracking implicit rather than a
  project setting
- The contract would write Keystone setup results to common/global instruction
  files
- The contract would let Keystone output language override unrelated tasks
- The contract would allow Orientation Mode to modify documents, code, config,
  progress, decisions, or generated files
- The contract would let document-to-repository mismatches be fixed without
  user or main-agent decision
- A required behavior conflicts with external skill constraints
- The correct design needs implementation or packaging decisions first
- The step needs changes outside `00_docs/` without approval

### Verification Method

Allowed checks:

- Read affected source documents for consistency
- Confirm the contract can answer when the skill should and should not run

Forbidden until explicitly allowed:

- Implementation code changes
- Publishing or installing a skill
- Broad repository cleanup

### Review Points

Reviewer should check:

- Contract is specific enough to guide implementation of four skills
- `keystone-clarify` topic decision behavior is explicit
- Initial setup, Git policy, and Keystone output language behavior are explicit
- 기준서 and 작업서 responsibilities are explicit
- Superpowers integration is explicit and bounded
- Work units can become role-based subagent goals
- Work step fields are sufficient for recoverability and coordinator
  compatibility without forcing long templates for simple steps
- Reader modes and derived document policies are explicit
- Orientation Mode is document-led, repository-aware, read-only, and reports
  document-to-repository mismatches for decision
- Progress/report statuses and verification source are explicit
- Main/subagent boundaries are explicit
- Stop conditions are present
- Source documents remain human-readable

### Progress Record

Record progress in `progress.md` only after main acceptance.

## Step S03. Implement Initial Keystone Skill Set

### Purpose

Create the first implementation of the four planned Keystone skills after the
document foundation and skill-system contract are accepted.

### Completion Criteria

- [ ] Skill files for all four planned Keystone skills are created in the
  approved location.
- [ ] Skill source files live under repo-local `skills/`.
- [ ] Each skill description and body matches the accepted contract.
- [ ] The clarification skill supports topic-scoped high-impact decision
  collection and reflection before document edits.
- [ ] The authoring skill supports 기준서 and 작업서 creation and revision.
- [ ] The reading/work-preparation skill supports relevant document selection
  and context extraction.
- [ ] The coordination skill supports coordinator-compatible step recovery and
  bounded subagent handoff.
- [ ] The implementation does not duplicate or silently rewrite prototype skills.
- [ ] A lightweight verification confirms the skill files exist and are readable.

### Related Standards

- Standard: `00_docs/standards/00_project-standard.md`
- Related rules: `STD-KEYSTONE-001`, `STD-KEYSTONE-002`, `STD-KEYSTONE-003`,
  `STD-KEYSTONE-005`

### Work Scope

Included:

- Initial Keystone skill source files under `skills/keystone-clarify`,
  `skills/keystone-author`, `skills/keystone-reader`, and
  `skills/keystone-coordinator`
- Minimal references required by the accepted contract
- Documentation links back to `00_docs/`

Excluded:

- Publishing, marketplace registration, or installation changes unless approved
- Rewriting `work-package-doc-architect` or `subagent-work-coordinator`
- Depending on `work-package-doc-architect` or `subagent-work-coordinator` as
  final runtime skills
- Broad automation, code generation, or repository restructuring

Conditionally allowed:

- Small supporting reference files if the accepted contract requires them
- Small updates to `00_docs/` to reflect accepted implementation decisions

### Recommended Approach

Do not begin this step until S02 is accepted. Main should decide whether to
implement directly or delegate a bounded worker task after preparing a concrete
Context Pack. If the approved location is outside this repository, confirm write
permission before editing.

### Context Pack Seed

When preparing a subagent handoff, main should include:

- Accepted four-skill contract from S02
- Exact target files and directories under repo-local `skills/`
- Existing skill format examples to reuse
- Forbidden external skill modifications
- Verification commands or file-read checks

### Stop And Report Conditions

- The approved skill location is unclear
- The implementation would require changing installed external skills
- The implementation cannot keep the four planned skills independent
- Packaging, publishing, or install behavior is required but not approved
- Verification cannot confirm the skill files are readable

### Verification Method

Allowed checks:

- `rg --files` in the approved skill directory
- Read created skill files for structure and content

Forbidden until explicitly allowed:

- Publishing or marketplace operations
- Broad global skill registry changes
- Destructive file operations

### Review Points

Reviewer should check:

- Implementation matches the accepted four-skill contract
- Scope stays inside the approved skill location
- Prototype skills are referenced only as design inputs, not runtime dependencies
- Verification evidence is adequate

### Progress Record

Record progress in `progress.md` only after main acceptance.
