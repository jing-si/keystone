# WP-KEYSTONE-SKILL Progress

## Current Step

S01

## Last Accepted Step

None

## Step Status

| Step | Status | Main Acceptance | Notes |
|---|---|---|---|
| S01 | in_progress | pending | Document foundation is being created and must be accepted by main session |
| S02 | planned | pending | Define the four-skill Keystone contract after S01 is accepted |
| S03 | planned | pending | Implement the initial Keystone skill set after S02 is accepted |

## Recent Worker Results

- None

## Recent Reviewer Results

- None

## Pending Decisions

- Decide whether to migrate the current `work-packages/WP-KEYSTONE-SKILL`
  documents into the future `works/` tree.
- Decide whether optional `scope.md` is needed after S02 begins.

## Accumulated Discoveries

- At project start, this repository had no existing `00_docs/` directory.
- No `docs/convention.md` file was found.
- Git is not initialized in this directory, so verification cannot rely on Git
  diff or status.
- Keystone is a skill-system project, not a single skill project.
- The final output is four new independent skills: policy/scope/document
  clarification, standards/work-order authoring, standards/work-order reading
  and work preparation, and subagent coordination.
- `work-package-doc-architect` and `subagent-work-coordinator` are prototype
  references and are expected to be replaced, not kept as final dependencies.
- Keystone should be explicitly invoked by the user, not automatically applied.
- Keystone is intended to avoid repeated context from dated one-off plan
  documents by storing reusable policy in 기준서 and current execution in 작업서.
- Superpowers can be integrated as an optional supporting workflow for
  brainstorming, planning, TDD, debugging, review, or skill testing, but
  accepted Keystone 기준서 and 작업서 remain authoritative.
- The main agent should act as supervisor: preserve context, assign role-based
  goals to subagents, receive reports, decide repairs, and make final
  acceptance decisions.
- Subagents should be role-based, such as explorer, code modifier, reviewer, or
  verifier, and should optimize for correctness and context preservation before
  parallel speed.
- Final skill names are `keystone-clarify`, `keystone-author`,
  `keystone-reader`, and `keystone-coordinator`.
- `keystone-clarify` is for high-impact topic decisions. It should gather
  related questions in Plan Mode, prefer `request_user_input` or an equivalent
  selection UI when available, summarize the reflection and edit plan, then
  update related source documents together in Default Mode.
- Future document paths are English. Document root resolution order is current
  user instruction, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `agent.md`, then
  default `00_docs/`.
- Future 기준서 live under `standards/`; future 작업서 live under `works/`.
  Both trees use unlimited-depth folder nodes with `00_index.md`.
- Final 기준서 files use `standard-{slug}.md`; final 작업서 files use
  `work-{slug}.md`; progress files use `progress.md`.
- `keystone-reader` has Orientation, Navigator, and Work Prep modes.
- Derived agent document types are kept as optional 4 types and are created
  only when needed.
- Progress status and subagent report status are separate.
- Verification is standards-led; main extracts criteria into a Verification
  Checklist and may assign a verifier Goal.
- Repository-local `skills/` is the source of truth for initial Keystone skill
  implementation.

## Next Recommended Action

Review and accept or amend Step S01 documents, then proceed to Step S02 to
define the four-skill Keystone contract, including clarify topic decisions,
Superpowers integration, Goal-based assignment, and role-based subagent
boundaries.
