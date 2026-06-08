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
- Initial local verification could not rely on Git diff/status. This is
  historical context and may not describe the current repository state.
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
- Future document paths are English. `00_docs/` is the default root, not a
  fixed root. Current user instruction may override the current run.
  Persistent project-local settings resolve through
  `.keystone/config.local.yaml`, `.keystone/config.yaml`, then explicit
  Keystone settings in a project-local agent instruction file. Common/global
  instruction files are setup suggestions only.
- Initial shared Keystone project setup should be recorded in
  `.keystone/config.yaml` after Plan Mode setup questions. Personal, local-only,
  or sensitive overrides belong in `.keystone/config.local.yaml`.
- 기준서 and 작업서 Git policy is a project setting with four choices: track
  both, track 기준서 only, track neither, or ask each time. Derived agent
  documents are ignored by Git by default.
- `.keystone/config.yaml` is tracked by Git by default as shared project policy;
  `.keystone/config.local.yaml` is ignored by Git by default as a local/private
  override.
- Sensitive settings or documents require user confirmation before writing,
  tracking, publishing, or deriving documents.
- Keystone output language policy applies only to Keystone artifacts and must
  not override unrelated task language, code comments, commit messages, README
  files, external tools, or non-Keystone skills.
- Future 기준서 live under `standards/`; future 작업서 live under `works/`.
  Both trees use unlimited-depth folder nodes with `00_index.md`.
- Final 기준서 files use `standard-{slug}.md`; final 작업서 files use
  `work-{slug}.md`; progress files use `progress.md`.
- 작업서 steps require `Goal`, `Scope`, `Source Context`,
  `Completion Criteria`, `Stop Conditions`, `Verification`, and
  `Expected Output`. `Suggested Role` is optional and recommended when
  delegation is likely.
- `keystone-reader` has Orientation, Navigator, and Work Prep modes.
- Orientation Mode is document-led, repository-aware, and read-only. It should
  include document root, project summary, shallow repository snapshot, active
  document map, current work status, recommended read order, operational
  boundaries, risks/gaps, next action, sources read, and assumptions. If
  documents and repository state conflict, it reports the mismatch and asks for
  user/main decision instead of modifying documents or code.
- Derived agent document types are kept as optional 4 types and are created
  only when needed.
- Progress status and subagent report status are separate. Progress uses
  `planned`, `ready`, `in_progress`, `assigned`, `reported`, `reviewing`,
  `verifying`, `accepted`, or `blocked`.
- Verification is standards-led; main extracts criteria into a Verification
  Checklist and may assign a verifier Goal.
- Repository-local `skills/` is the source of truth for initial Keystone skill
  implementation.

## Next Recommended Action

Review and accept or amend Step S01 documents, then proceed to Step S02 to
define the four-skill Keystone contract, including clarify topic decisions,
Superpowers integration, Goal-based assignment, and role-based subagent
boundaries.
