# Keystone

Document-mediated project control plane for keeping human intent, source
documents, artifact links, and bounded worker execution aligned.

## Overview

Keystone is a skill-system project for AI-assisted work management. Its goal is
to make human-readable source documents the stable foundation for agent work:

```text
standards + work orders + artifact graph -> main agent -> bounded worker assignments
```

The project separates long-lived policies from task execution details:

- 기준서 define reusable standards, policies, architecture rules, domain rules,
  and verification expectations.
- 작업서 define concrete goals, execution steps, completion criteria,
  stop/report conditions, and verification paths.

This avoids repeating the same context across dated one-off planning documents
and lets the main agent read only the documents needed for the current task.

In this repository, `00_docs/` is the bootstrap reference corpus for the future
Keystone skills. The source documents are written first, then the repo-local
skills will be generated from those accepted contracts.

## Planned Skills

Keystone is planned as five independent but cooperating skills:

| Skill | Responsibility |
|---|---|
| `keystone-clarify` | Collect high-impact policy, scope, document, and skill-contract decisions by topic before source documents are changed. |
| `keystone-author` | Create and revise 기준서 and 작업서 as reusable source documents. |
| `keystone-reader` | Navigate relevant 기준서 and 작업서, orient to a project, and prepare main-agent work context. |
| `keystone-linker` | Interpret the Artifact Graph read-only, discover document, capability, code, config, schema, API, and test artifact links, and report impact/stale/gap candidates plus handoff seeds. |
| `keystone-coordinator` | Turn Keystone context into bounded worker assignments, receive worker reports, and keep the main agent in a supervisory role. |

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
  key-context-map.md
  standards/
    00_key-index.md
    01_key-project-standard.md
    subagents/
      00_key-index.md
      key-standard-subagents.md
    ...
  works/
    00_key-index.md
    key-decisions.md
    r001-bootstrap-keystone/
      00_key-index.md
      ...
```

Keystone-managed Markdown files use the `key` filename prefix so they can be
routed to Keystone skills.

The main document branches are:

| Path | Purpose |
|---|---|
| `00_docs/key-context-map.md` | Current project map, active standards, active work round, and read order. |
| `00_docs/standards/` | Reusable 기준서 for source authority, artifact graph, subagents, and each planned skill. |
| `00_docs/works/` | 작업서, progress records, and accepted decisions for active work rounds. |

## Current Status

This repository currently contains the documentation foundation for the
Keystone skill-system. The initial repo-local skill source files under `skills/`
have not been implemented yet.

The authoritative current work status is maintained in:

- [`00_docs/key-context-map.md`](00_docs/key-context-map.md)
- [`00_docs/works/00_key-index.md`](00_docs/works/00_key-index.md)
- [`00_docs/works/r001-bootstrap-keystone/00_key-index.md`](00_docs/works/r001-bootstrap-keystone/00_key-index.md)

README intentionally does not duplicate active step status so project state
does not go stale. Skill source creation is intentionally deferred until the
relevant standards are accepted.

Start with:

- [`00_docs/key-context-map.md`](00_docs/key-context-map.md)
- [`00_docs/standards/01_key-project-standard.md`](00_docs/standards/01_key-project-standard.md)
- [`00_docs/works/00_key-index.md`](00_docs/works/00_key-index.md)
- [`00_docs/works/r001-bootstrap-keystone/00_key-index.md`](00_docs/works/r001-bootstrap-keystone/00_key-index.md)

## Relationship To Prototype Skills

The existing `work-package-doc-architect` and `subagent-work-coordinator` skills
are prototype references for this project. They are not final runtime
dependencies and are expected to be replaced by Keystone skills.

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).
