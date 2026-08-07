# Keystone

Keystone is a document-mediated control plane for keeping human intent,
standards, work recovery, artifact links, and bounded agent execution aligned.

Human-readable source documents are the authority:

```text
project foundation -> standards and work orders -> artifact graph -> implementation
```

Keystone separates long-lived project meaning from task execution details:

- 기준서 define reusable policies, architecture, terminology, authority, and
  verification expectations.
- 작업서 and progress records make interrupted work recoverable from documents.
- The Artifact Graph connects documents to code, config, schema, API, and test
  artifacts without making every missing relation a blocker.

## Skills

Keystone consists of six independent, cooperating Codex skills:

| Skill | Responsibility |
|---|---|
| `keystone-init` | Inspect, initialize, or safely repair the minimum Keystone foundation and R000 work recovery scaffold. |
| `keystone-author` | Create and revise project standards, work orders, progress records, decisions, indexes, and Change Sets. |
| `keystone-reader` | Read existing Keystone documents, recover active work, and prepare a focused context brief. |
| `keystone-clarify` | Resolve one actual high-impact user decision at a time, then return control to the caller. |
| `keystone-linker` | Read graph evidence without editing source surfaces, decide canonical graph mutations, and report exact owner-applied synchronization patches. |
| `keystone-coordinator` | With scoped user permission, provide Keystone context, execute directly or orchestrate an external-skill worker, and supervise document, metadata, graph, verification, and finalization closure. |

Each installed skill package contains its own runtime contract. A consuming
project does not need project-local `standards/skills/**` files. The documents
under this repository's `00_docs/standards/skills/**` are development and review
specifications for Keystone itself.

## Local Installation

Install or refresh all six skills from this checkout:

```bash
bash ./reinstall-local-keystone-skills.sh
```

The script installs into `${CODEX_HOME}/skills` when `CODEX_HOME` is set and
otherwise uses `~/.codex/skills`. It validates all six packages in a temporary
staging directory before replacing the same-named Keystone skill directories,
keeps replaced packages under `.keystone-backups`, records the source revision
and package version from [`VERSION`](VERSION) in `.keystone-install.json`, and
verifies the installed result before committing the replacement. Other installed skills are
not touched.

To install into a different Codex home:

```bash
CODEX_HOME=/path/to/codex-home bash ./reinstall-local-keystone-skills.sh
```

Restart Codex after installation so the updated skill definitions are loaded.

## Release Verification

The repository release gate runs only from a clean checkout. The RC profile verifies package tests,
readiness, full graph reconstruction, historical finalization compatibility, Coordinator actual-state
closure, installer parity and rollback, and independently attested agent-behavior evidence. List the
planned phases without executing them with:

```bash
/bin/sh scripts/run_release_gate.sh --profile rc --list
```

Use the shell launcher for authoritative release checks. It starts the gate with an isolated Python
runtime and a minimal environment; direct invocation of the Python entrypoint is intended only for
development tests and is not release evidence.

An actual RC run also requires an external evidence root, results manifest, reviewer key, trusted
reviewer ID, and a separately configured key fingerprint. The 12 required scenarios are defined in
[`scripts/agent_eval_scenarios.json`](scripts/agent_eval_scenarios.json); the validator fails closed when
the evidence or trust material is absent, stale, malformed, symlinked, or not bound to the current
commit and release-package bytes.

Use the `production` profile only after Main acceptance and schema-v5 finalization have placed the
Context Map in terminal `active_round: none` state. Production adds validation of the latest accepted
Round's current finalization manifest. Reviewer HMAC proves possession of the configured key; release
operators must still establish reviewer independence and that the recorded agent execution actually
occurred.

## Starting a Project

For a project without Keystone documents, invoke `keystone-init` directly. A
direct Init request already grants initialization consent; Init does not ask for
the same consent again. It may ask a concise built-in setup question when a
real choice remains, such as the document root. The default root is `00_docs`.

```text
$keystone-init Initialize Keystone in this project.
```

You can also start with an Author request. Author detects the missing foundation,
asks once whether to initialize, hands the request to Init, and resumes the
original writing task after initialization.

```text
$keystone-author Create the initial project standard.
```

Before Keystone exists, ordinary repository inspection—such as reading code,
README files, and configuration—belongs to the host AI's normal capabilities.
Reader does not control or replace that inspection. Once Keystone documents
exist, Reader uses them to navigate standards and recover work more reliably.

For an existing project, repository evidence can feed R000 and Author. For an
empty project, Init and Author use only explicit user input and verified facts;
Clarify is used when project purpose, policy, terminology, or authority requires
an actual user decision.

## Bootstrap Document Model

Init creates only the bounded foundation scaffold and does not invent or approve
project meaning:

```text
.keystone/
  config.yaml
00_docs/                       # configurable; this is the default
  key-context-map.md
  standards/
    00_key-index.md
  works/
    00_key-index.md
    key-decisions.md
    r000-project-foundation/
      00_key-index.md
      project-foundation/
        00_key-index.md
        key-work-project-foundation.md
        key-progress.md
```

Author creates the initial `standards/01_key-project-standard.md`. Init reaches
`ready` only after the project standard is accepted and the work state is
recoverable. Existing files are preserved; partial initialization is repaired
by adding only missing, non-conflicting scaffold files.

Ordinary work rounds start at `R001`, and steps start at `S01`. `R000` is
reserved for the exceptional Project Foundation round before standards exist.

## Operating Boundaries

- Source documents remain authoritative; internal handoff payloads are hidden
  unless they are needed for audit, debugging, or verification.
- Stable source-owned IDs and refs provide the default lookup path. Reader starts
  with docs-only context readiness; Linker lazily enriches repository artifact
  context through a disposable external index. The typed graph remains optional
  and is materialized only for semantic traversal that needs it.
- Freshness covers worktree identity, the sorted discovery path set, and raw file
  bytes. Cache loss, staleness, corruption, or contention falls back to source
  discovery and never makes the cache authoritative.
- Linker is source-write-free and may be used without separate permission. It is the sole canonical
  graph mutation decision owner; Author, Main, or a permitted Coordinator attest and apply patches only
  on their own source surfaces.
- Coordinator always requires user permission for its work scope. Directly
  invoking `keystone-coordinator` counts as that permission.
- Without an external coding skill, Coordinator may execute bounded repository work directly. With an
  external skill, that worker owns implementation while Coordinator owns context provisioning and
  Keystone closure supervision through Linker and Author.
- Keystone does not force a worktree, workspace, concurrency, or delegation
  strategy. The user, host, or injected worker contract chooses the execution
  environment.
- Missing graph evidence produces a partial result, not an automatic failure.

## Repository Status and Sources

The authoritative current round and acceptance state remain in the source documents so README status
does not become a competing authority. Runtime packages include bounded acceptance finalization and
Artifact Graph synchronization contracts; consult these sources for current status:

- [`00_docs/key-context-map.md`](00_docs/key-context-map.md)
- [`00_docs/standards/01_key-project-standard.md`](00_docs/standards/01_key-project-standard.md)
- [`00_docs/standards/bootstrap/key-standard-bootstrap.md`](00_docs/standards/bootstrap/key-standard-bootstrap.md)
- [`00_docs/works/00_key-index.md`](00_docs/works/00_key-index.md)
- [`00_docs/works/r008-skill-graph-traceability/00_key-index.md`](00_docs/works/r008-skill-graph-traceability/00_key-index.md)
- [`00_docs/works/r009-coordinator-keystone-closure/00_key-index.md`](00_docs/works/r009-coordinator-keystone-closure/00_key-index.md)
- [`00_docs/works/r010-production-control-plane-hardening/00_key-index.md`](00_docs/works/r010-production-control-plane-hardening/00_key-index.md)

The older `work-package-doc-architect` and `subagent-work-coordinator` projects
remain historical prototype references, not runtime dependencies.

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).
