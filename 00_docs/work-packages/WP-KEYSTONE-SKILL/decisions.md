# WP-KEYSTONE-SKILL Decisions

This document records accepted Keystone policy decisions. If this document
conflicts with standards or work orders, resolve the source document conflict
before using derived agent documents or implementation plans.

| ID | Related Step | Decision | Reason | Status |
|---|---|---|---|---|
| DEC-001 | S02 | Keystone final output is four independent skills: `keystone-clarify`, `keystone-author`, `keystone-reader`, and `keystone-coordinator`. | Preserve separate clarification, authoring, reading/preparation, and coordination responsibilities. | accepted |
| DEC-002 | S02 | Document paths are English. `00_docs/` is the default root, not a fixed root. Current user instruction can override the current run. Persistent project-local settings resolve through `.keystone/config.local.yaml`, `.keystone/config.yaml`, then explicit Keystone settings in a project-local agent instruction file. Common/global instruction files are setup suggestions only. | Keep paths portable while making project-local settings the durable authority. | accepted |
| DEC-003 | S02 | Future 기준서 use `standards/`; future 작업서 use `works/`. Both use unlimited-depth folder trees with `00_index.md` at every node. | Minimize context by letting people and LLMs navigate downward through indexes. | accepted |
| DEC-004 | S02 | Final detail files use `standard-{slug}.md`, `work-{slug}.md`, and `progress.md`. | Keep final documents identifiable without repeating full paths in filenames. | accepted |
| DEC-005 | S02 | No explicit leaf metadata is needed; a node with no child documents is the final node. | Avoid redundant metadata and keep documents natural to read. | accepted |
| DEC-006 | S02 | 상위 기준서 and 상위 작업서 may contain summary, links, scope, and common rules. Final 기준서 contains detailed rules; final 작업서 contains execution steps. | Share one node model for 기준서 and 작업서 while preserving their different targets. | accepted |
| DEC-007 | S02 | 작업서 steps are Goal units for subagent assignment. | Make work naturally assignable and reviewable. | accepted |
| DEC-008 | S02 | `keystone-reader` has Orientation, Navigator, and Work Prep modes. | Support initial project orientation, targeted document navigation, and goal preparation without mixing reading with clarification ownership. | accepted |
| DEC-009 | S02 | Optional derived agent documents keep four types: `agent/00_agent-pack.md`, `agent/step-context.md`, `agent/worker-handoff.md`, and `agent/reviewer-brief.md`. They are created only when needed. | Support LLM-friendly handoffs without making maintenance cost the default. | accepted |
| DEC-010 | S02 | Source changes should update clearly affected related source and derived documents together; uncertain impact requires stopping and asking. | Preserve document consistency without guessing at unclear meaning changes. | accepted |
| DEC-011 | S02 | Main is supervisor. Actual modifications are normally delegated to subagents; low-risk document, typo, and small local changes may skip reviewer/verifier. | Preserve main context while avoiding unnecessary coordination overhead. | accepted |
| DEC-012 | S02 | Default subagent roles are explorer, worker/code-modifier, reviewer, and verifier. | Keep roles clear and reportable. | accepted |
| DEC-013 | S02 | Progress status and report status are separate. Progress uses `planned`, `ready`, `assigned`, `reported`, `reviewing`, `verifying`, `accepted`, `blocked`; reports use `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, `NEEDS_SCOPE_CHANGE`, `BLOCKED`. | Separate workflow state from subagent report outcome. | accepted |
| DEC-014 | S02 | Verification is 기준서-led. Main extracts verification criteria into a Verification Checklist and may assign a verifier Goal. | Keep verification at the correct policy level while avoiding direct subagent document rereads. | accepted |
| DEC-015 | S02 | Superpowers can be used only when the user explicitly allows it. It remains supporting input, not Keystone source of truth. | Preserve explicit skill invocation and avoid automatic workflow changes. | accepted |
| DEC-016 | S03 | Initial skill source lives under repo-local `skills/`. | Make the Git repository the source of truth and keep future plugin packaging possible. | accepted |
| DEC-017 | S02 | Existing `work-packages/WP-KEYSTONE-SKILL` documents are not automatically migrated to `works/`; ask the user before migration. | Avoid unapproved path churn while recording the future structure policy. | accepted |
| DEC-018 | S02 | `keystone-clarify` is a separate skill for high-impact topic decisions. It gathers topic questions in Plan Mode, uses `request_user_input` or equivalent selection UI when available, summarizes reflection and edit plans, then supports related source-document updates in Default Mode. | Keep clarification deliberate without making every minor edit a question, and preserve consistency when decisions affect multiple documents. | accepted |
| DEC-019 | S02 | Keystone initial shared project settings are recorded in `.keystone/config.yaml` by default after Plan Mode setup. Personal, local-only, or sensitive overrides belong in `.keystone/config.local.yaml`. Existing project-local agent instruction files may be used only if the user chooses that storage location. Keystone never writes to common/global instruction files. | Avoid repeated setup questions while keeping project-level choices explicit, portable, and independent of AI-specific instruction file conventions. | accepted |
| DEC-020 | S02 | 기준서 and 작업서 Git policy supports four choices: track both, track 기준서 only, track neither, or ask each time. Derived agent documents are ignored by default. | Let projects choose collaboration vs privacy tradeoffs, including fully local source documents when needed. | accepted |
| DEC-021 | S02 | Keystone output language policy applies only to Keystone artifacts and must not override unrelated task language, code comments, commit messages, README files, external tools, or non-Keystone skills. | Keep Keystone documents consistent without leaking language policy into unrelated work. | accepted |
| DEC-022 | S02 | Every 작업서 step must include `Goal`, `Scope`, `Source Context`, `Completion Criteria`, `Stop Conditions`, `Verification`, and `Expected Output`. Field content may be short for simple steps. `Suggested Role` is optional and recommended when delegation is likely. | Keep steps recoverable and coordinator-compatible without forcing long templates for small or low-risk work. | accepted |
| DEC-023 | S02 | `.keystone/config.yaml` is tracked by Git by default as shared project policy. `.keystone/config.local.yaml` is ignored by Git by default as a local/private override. Sensitive settings or documents require user confirmation before writing, tracking, publishing, or deriving documents. | Share stable project policy while keeping private or sensitive data out of Git and derived documents by default. | accepted |
| DEC-024 | S02 | `keystone-reader` Orientation Mode is document-led, repository-aware, and read-only. It outputs document root, project summary, shallow repository snapshot, active document map, current work status, recommended read order, operational boundaries, risks/gaps, next action, sources read, and assumptions. Document-to-repository mismatches are reported for user/main decision instead of being fixed automatically. | Catch stale documents and repo-state drift early without letting a read-only orientation step silently change source documents or code. | accepted |

## Decision Notes

- `keystone-clarify` owns high-impact policy, scope, document, and skill-contract
  decision collection before source documents are changed.
- `keystone-clarify` also owns initial Keystone setup questions when project
  settings do not yet contain enough information.
- `keystone-author` owns 기준서 and 작업서 creation and revision.
- `keystone-reader` owns project orientation, document navigation, and work
  preparation.
- `keystone-coordinator` owns Goal assignment, subagent routing, reports,
  review, verification, and acceptance flow.
- 기준서 are primarily human-readable documents for people and LLMs. 작업서 are
  readable by people but primarily structured for LLM work preparation and
  subagent execution.
- Existing prototype skills remain references only:
  `work-package-doc-architect` and `subagent-work-coordinator` are not final
  runtime dependencies.
