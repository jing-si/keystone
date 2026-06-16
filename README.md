# Keystone

Document-driven AI workflow skills for turning standards and work orders into
supervised main-agent and role-based subagent execution.

## Overview

Keystone is a skill-system project for AI-assisted work management. Its goal is
to make human-readable source documents the stable foundation for agent work:

```text
standards + work orders -> main agent -> role-based subagents
```

The project separates long-lived policies from task execution details:

- 기준서 define reusable standards, policies, architecture rules, domain rules,
  and verification expectations.
- 작업서 define concrete goals, execution steps, completion criteria,
  stop/report conditions, and verification paths.

This avoids repeating the same context across dated one-off planning documents
and lets the main agent read only the documents needed for the current task.

## Planned Skills

Keystone is planned as four independent but cooperating skills:

| Skill | Responsibility |
|---|---|
| `keystone-clarify` | Collect high-impact policy, scope, document, and skill-contract decisions by topic before source documents are changed. |
| `keystone-author` | Create and revise 기준서 and 작업서 as reusable source documents. |
| `keystone-reader` | Navigate relevant 기준서 and 작업서, orient to a project, and prepare main-agent work context. |
| `keystone-coordinator` | Assign role-based goals to subagents, receive reports, and keep the main agent in a supervisory role. |

## Document Model

Keystone source documents are designed for both people and LLMs. Source
documents remain authoritative; agent-facing packs and handoffs are optional
derived documents.

The default document root is:

```text
00_docs/
```

Future Keystone documents should use English paths and index-based trees:

```text
00_docs/
  standards/
    00_index.md
    ...
  works/
    00_index.md
    ...
```

## Current Status

This repository currently contains the documentation foundation for the
Keystone skill-system. The initial skill source files have not been implemented
yet.

Start with:

- [`00_docs/context-map.md`](00_docs/context-map.md)
- [`00_docs/standards/00_project-standard.md`](00_docs/standards/00_project-standard.md)
- [`00_docs/works/00_index.md`](00_docs/works/00_index.md)

## Relationship To Prototype Skills

The existing `work-package-doc-architect` and `subagent-work-coordinator` skills
are prototype references for this project. They are not final runtime
dependencies and are expected to be replaced by Keystone skills.

Superpowers may be used as an explicit supporting workflow for brainstorming,
planning, TDD, debugging, review, or skill testing, but accepted Keystone source
documents remain the source of truth.
