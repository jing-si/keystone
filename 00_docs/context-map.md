# Project Context Map

All active project planning documents live under `00_docs/`.

## Project

This repository is for the `keystone` skill-system project. The final output is
a set of new independent skills that work together through shared source
documents:

- a policy, scope, and document-decision clarification skill
- a standards/work-order authoring skill
- a standards/work-order reading and work-preparation skill
- a subagent coordination skill

The existing `work-package-doc-architect` and `subagent-work-coordinator` skills
are reference prototypes for this project. They are not final dependencies and
are expected to be replaced by new Keystone skills.

## Standards

| Area | Path | When to Read |
|---|---|---|
| Project | `00_docs/standards/00_project-standard.md` | Always for project-wide rules, document-source policy, skill-family roles, and coordinator compatibility |

## Default Document Tree Policy

Future Keystone documents should use English paths and the configured document
root. If no project instruction or project `agent.md` setting overrides it, the
root is `00_docs/`.

```text
00_docs/
  standards/
    00_index.md
    ...
  works/
    00_index.md
    ...
```

Every standards or works node should have `00_index.md` for navigation. Final
nodes have no child nodes and may include detail files such as
`standard-{slug}.md`, `work-{slug}.md`, and `progress.md`.

Keystone project setup choices such as document root, source document Git
policy, derived agent document Git policy, and Keystone output language policy
should be recorded in the project's `agent.md` after the initial setup
conversation.

## Work Packages

| Work Package | Path | Status | Responsible Area |
|---|---|---|---|
| WP-KEYSTONE-SKILL | `00_docs/work-packages/WP-KEYSTONE-SKILL/00_index.md` | active | Keystone skill-system design and implementation |

## Planned Keystone Skills

| Skill Role | Status | Purpose |
|---|---|---|
| `keystone-clarify` | planned | Collect high-impact policy, scope, document, and skill-contract decisions by topic before source documents are changed |
| `keystone-author` | planned | Create and revise 기준서 and 작업서 as reusable source documents, with structure that encourages subagent-sized work units |
| `keystone-reader` | planned | Orient to a project, navigate relevant 기준서 and 작업서, and prepare main-agent work while preserving main context |
| `keystone-coordinator` | planned | Assign role-based goals to subagents, receive reports, and keep the main agent in a supervisory role |

## Current Structure Note

The existing `WP-KEYSTONE-SKILL` package remains under `work-packages/` until
the user explicitly chooses whether to migrate it. New Keystone documents should
follow the `standards/` and `works/` tree policy above.

## Optional Workflow References

| Reference | Use Boundary |
|---|---|
| Superpowers | Optional quality-assist reference for brainstorming, planning, TDD, debugging, review, and skill testing when the user explicitly invokes it or an accepted Keystone document allows it |

## Prototype Skill References

| Skill | Purpose In This Project |
|---|---|
| `work-package-doc-architect` | Prototype reference for the future standards/work-order authoring skill |
| `subagent-work-coordinator` | Prototype reference for the future subagent coordination skill |

## Legacy References

No legacy planning documents are currently linked.
