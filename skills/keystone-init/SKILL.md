---
name: keystone-init
description: "Inspect, initialize, or repair Keystone in a project that has no usable Keystone foundation or has a partial/conflicted setup. Use for direct initialization requests and Init handoffs from other Keystone skills; inspect is read-only, while initialize/repair create only the bounded bootstrap scaffold and R000 before handing project meaning to Author."
---

<!-- keystone: id=key.skill.init kind=output_artifact artifact_kind=skill_source -->
<!-- keystone: produced_from=key.work.skill-runtime-implementation.order -->
<!-- keystone: governed_by=key.standard.project key.standard.bootstrap key.standard.skill.init -->

# keystone-init

## Purpose

Make a project recoverable by creating or repairing Keystone's minimum document foundation, then start project-standard authoring. Support:

- `inspect`: detect and report state without writing.
- `initialize`: create the fixed scaffold for an uninitialized project.
- `repair`: fill only missing, non-conflicting scaffold in a partial project.

This installed contract is self-contained. Never require a project standard, Context Map, work order, progress record, Artifact Graph, or project-local Init/Author/Clarify standard as a prerequisite. Never create `standards/skills/**` in a consuming project.

## Consent and Required Context

A direct Init request includes consent to initialize within its stated scope; do not ask for initialization consent again. A handoff from another file-changing skill must preserve the once-given consent for the same conversation and scope.

Use:

1. Mode: `inspect`, `initialize`, or `repair`.
2. Repository root and current instructions.
3. User request and any handoff/resume context.
4. Existing `.keystone` settings, document conventions, files, and workspace risks.

Preserve `original_request`, `original_skill`, `initialization_reason`, `resume_step`, accepted user decisions, and existing-file risks across every handoff.

## State Detection

Inspect actual files and settings; never trust a single `initialized` flag.

- `uninitialized`: no Keystone configuration, authoritative document root, or R000 foundation is resolvable.
- `bootstrapping`: scaffold and R000 exist while the project standard is being authored, verified, or accepted.
- `partial`: required configuration, indexes, Context Map, decisions, or R000 files are incomplete.
- `conflicted`: root candidates, existing paths, settings, or user instructions conflict and cannot be merged safely.
- `ready`: one authoritative root is resolvable; Context Map, standards/works indexes, decisions, an accepted project standard, and recoverable work exist; no required User Decision remains open.

An existing accepted Keystone corpus may be adopted as `ready` without retroactively creating config or R000 when one root and active work are recoverable. Missing Artifact Graph relations, Linker reports, Coordinator outputs, or project-local skill standards never make the state `partial`.

## Document Root

Resolve candidates in this order:

1. Current explicit user instruction.
2. `.keystone/config.local.yaml`.
3. `.keystone/config.yaml`.
4. Explicit project-local agent setting.
5. One conflict-free existing document convention.
6. Default `00_docs`.

Apply safe explicit/default settings without unnecessary questions. Init may directly ask about built-in setup choices such as document root, tracking, output language, or storage location when a real choice remains. Do not claim to activate or switch any host execution mode.

Use Clarify only for one actual semantic decision at a time: choosing between conflicting authoritative roots, adopting/moving/replacing existing documents, project purpose/scope/policy/terminology/authority, sensitive storage, destructive migration, or external publication. Resume Init after the answer. Do not send default metadata, filenames, indexes, routing, or skill behavior to Clarify.

## Fixed Write Authority

`initialize` and `repair` may create only:

1. `.keystone/config.yaml`
2. `<document_root>/key-context-map.md`
3. `<document_root>/standards/00_key-index.md`
4. `<document_root>/works/00_key-index.md`
5. `<document_root>/works/key-decisions.md`
6. `<document_root>/works/r000-project-foundation/00_key-index.md`
7. `<document_root>/works/r000-project-foundation/project-foundation/00_key-index.md`
8. `<document_root>/works/r000-project-foundation/project-foundation/key-work-project-foundation.md`
9. `<document_root>/works/r000-project-foundation/project-foundation/key-progress.md`

R000 means the exceptional foundation round before standards exist. Its first and default step is `S01 Establish Project Standards`; all ordinary rounds also start at `R001` and steps at `S01`.

Create neutral draft/pending templates containing purpose, scope, source evidence, User Decision candidates, completion criteria, verification, and resume context. Do not create or fill `<document_root>/standards/01_key-project-standard.md`; Author owns project meaning. Do not approve project meaning or mark R000 accepted.

## Workflow

1. Inspect repository state, settings, root candidates, scaffold, and existing-change risk.
2. Return a no-write state report immediately in `inspect` mode.
3. Resolve safe built-in settings or ask Init's own concise setup question when needed.
4. Handoff one semantic conflict or User Decision topic to Clarify only when necessary, then resume.
5. For `uninitialized`, create only missing fixed scaffold files and R000 templates.
6. For `partial`, preserve all existing files and repair only missing non-conflicting scaffold.
7. Record verified repository facts and user instructions as R000 evidence; Main performs ordinary pre-Keystone code/README/config inspection.
8. Handoff project-standard drafting to Author with evidence and accepted decisions.
9. After Author returns, Main verifies and accepts the project standard when no User Decision remains.
10. Validate actual files, links, statuses, document root, R000 recovery, and project-standard acceptance before reporting `ready`.
11. Resume the original skill, request, and exact interrupted step automatically.

Initialization and repair are idempotent: never overwrite an existing file unconditionally, duplicate valid scaffold, move existing documents, perform broad normalization, or migrate metadata automatically. Preserve user and other-agent changes.

## Handoff and Output

Keep detailed state and handoff payloads agent-facing. They may contain:

```yaml
init_result:
  mode:
  state_before:
  state_after:
  document_root:
  created: []
  preserved: []
  conflicts: []
  missing_or_unverified: []
  author_handoff_required:
  resume:
    original_skill:
    original_request:
    step:
  verification:
  residual_risk:
  recommended_next_action:
```

By default, tell the user only the state, root, created/repaired items, conflicts or limits, verification, resume result, and next action. Do not dump raw structured payloads unless requested or required for handoff/audit/debug/verification.

## Fail-soft and Stop Conditions

- `inspect` is always read-only and may report partial orientation.
- Treat `partial` as repairable, not automatically fatal.
- In `conflicted`, preserve files, identify the single blocking topic, and do not guess.
- Separate confirmed errors from items that could not be inspected.
- If initialization is declined, write nothing and return available orientation plus how to run Init later.

Stop before writing when:

1. Multiple roots or existing-file meanings remain unresolved.
2. Progress requires overwriting, moving, or destructively normalizing existing content.
3. User instructions conflict with settings.
4. A required semantic User Decision is unresolved.
5. Work would exceed the fixed bootstrap authority.
6. Sensitive storage, external publication, or another high-risk action lacks authority.

## Verification

Verify that:

1. `inspect` made no changes and state came from actual files.
2. Initialize/repair changed only missing fixed scaffold and preserved existing content.
3. Document-root priority and conflicts were handled correctly.
4. R000 and its first step are `R000`/`S01`, and project-standard authoring stayed with Author.
5. No project-local skill standards, profiles, mandatory routing payloads, or host-mode claims were introduced.
6. `ready` includes accepted project meaning and recoverable work, not merely file existence.
7. The original request and caller resume automatically after initialization.
