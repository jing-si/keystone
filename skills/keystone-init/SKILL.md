---
name: keystone-init
description: "Inspect, initialize, repair, or configure a bounded optional Keystone integration. Use for direct initialization requests, Init handoffs, and explicit requests to enable Keystone session title display in one ready project; inspect is read-only, initialize/repair own the fixed scaffold and R000, and configure may change only its named project-local integration."
---

<!-- keystone: id=key.skill.init kind=output_artifact artifact_kind=skill_source -->
<!-- keystone: produced_from=key.work.skill-runtime-implementation.order -->
<!-- keystone: governed_by=key.standard.project key.standard.bootstrap key.standard.skill.init -->
<!-- keystone: derived_from=key.work.decisions.dec-works-020 -->

# keystone-init

## Purpose

Make a project recoverable by creating or repairing Keystone's minimum document foundation, then start project-standard authoring. Support:

- `inspect`: detect and report state without writing.
- `initialize`: create the fixed scaffold for an uninitialized project.
- `repair`: fill only missing, non-conflicting scaffold in a partial project.
- `configure`: apply one explicitly requested optional Keystone integration in a ready project without
  changing bootstrap state.

This installed contract is self-contained. Never require a project standard, Context Map, work order, progress record, Artifact Graph, or project-local Init/Author/Clarify standard as a prerequisite. Never create `standards/skills/**` in a consuming project.

## Consent and Required Context

A direct Init request includes consent to initialize within its stated scope; do not ask for initialization consent again. A handoff from another file-changing skill must preserve the once-given consent for the same conversation and scope.

Use:

1. Mode: `inspect`, `initialize`, `repair`, or `configure`.
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

An existing accepted Keystone corpus may be adopted as `ready` without retroactively creating config or R000 when one root and active work are recoverable. Missing Artifact Graph relations, document-item or claim metadata, Linker reports, Coordinator outputs, or project-local skill standards never make the state `partial`.

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

## Fixed Bootstrap Write Authority

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

Scaffold templates may use stable section or item metadata where the fixed template already defines an independently recoverable work step or acceptance item. Do not require exhaustive `key.rule.*`, `key.claim.*`, or `key.acceptance.*` coverage, invent project-specific item IDs, migrate existing item metadata, or treat missing item metadata as a bootstrap defect. Item-level admission and source metadata repair belong to Author after project meaning is available; stale/gap interpretation belongs to read-only Linker.

Give every newly created Markdown scaffold document an immutable `created_at: "YYYY-MM-DD"` using the actual creation date. Keep draft/pending approval free of `accepted_at`; Author records it only after Main or an authorized user accepts the current meaning. If Init records an actual decision, include `결정일: YYYY-MM-DD`. Do not add a general `updated_at`.

## Optional Codex Project Integration

`Keystone 세션 제목 표시` is opt-in and separate from the fixed bootstrap scaffold.

1. During `initialize` or `repair`, ask exactly once:
   `IntelliJ·터미널 탭에 Keystone 작업 세션 제목을 표시할까요? (yes/no)`
2. On `yes`, the only additional write authority is the repository root's `.codex/config.toml`, limited
   to `tui.terminal_title` and the Keystone Reader `hooks.UserPromptSubmit` command shown below. On `no`,
   do not create or modify that config and continue initialization or repair.
3. In a ready project, an explicit natural-language request such as `Keystone 세션 제목 표시를 켜줘`
   selects `configure` and is itself consent for the same bounded write. Do not ask the yes/no question
   again.
4. Set the value in this order:

   ```toml
   [tui]
   terminal_title = ["activity", "thread-title", "task-progress"]

   [[hooks.UserPromptSubmit]]
   [[hooks.UserPromptSubmit.hooks]]
   type = "command"
   command = '"$HOME/.codex/skills/keystone-reader/scripts/keystone_session_title.py" --hook'
   ```

   The TOML single-quoted value must contain the path's double quotes directly. Do not prefix those
   double quotes with backslashes; a literal backslash can make the shell treat the quote as part of
   the executable name and return exit code 127.

5. If `.codex/config.toml` does not exist, create `.codex/` and the smallest valid file containing the
   tables above. If it exists, re-read current bytes, parse it as TOML, and create or replace only the
   two named targets; preserve every other table, key, comment, and ordering as far as the target-line
   patch allows. Never reserialize the whole file merely to apply this setting.
6. If TOML is invalid, `[tui]` is duplicated or structurally conflicting, the key is duplicated, or a
   safe minimal patch cannot be determined, write nothing and report the conflict. Do not guess or
   replace the file.
7. Never edit `~/.codex/config.toml`, another project, or any profile, provider, authentication,
   permission, notification, telemetry, IntelliJ, or unrelated Codex key. Do not introduce a plugin,
   daemon, watcher, App Server, or network dependency.
8. Report that Codex loads a project-local config and command hook only for a trusted project. Codex may
   ask the user to trust the project hook once. This host condition does not change Keystone's
   initialization or ready state.

## Workflow

1. Inspect repository state, settings, root candidates, scaffold, and existing-change risk.
2. Return a no-write state report immediately in `inspect` mode.
3. Resolve safe built-in settings or ask Init's own concise setup question when needed.
4. During `initialize` or `repair`, ask the optional session-title question once and apply or skip it
   according to the answer. In `configure`, apply only the explicitly requested optional integration
   and do not scaffold or repair Keystone sources.
5. Handoff one semantic conflict or User Decision topic to Clarify only when necessary, then resume.
6. For `uninitialized`, create only missing fixed scaffold files and R000 templates.
7. For `partial`, preserve all existing files and dates, and repair only missing non-conflicting scaffold. Never replace `created_at` with the repair date or infer a missing legacy date.
8. Record verified repository facts and user instructions as R000 evidence; Main performs ordinary pre-Keystone code/README/config inspection.
9. Handoff project-standard drafting to Author with evidence and accepted decisions.
10. After Author returns, Main verifies and accepts the project standard when no User Decision remains.
11. Validate actual files, links, statuses, document root, R000 recovery, and project-standard acceptance before reporting `ready`.
12. Resume the original skill, request, and exact interrupted step automatically.

Initialization and repair are idempotent: never overwrite an existing file unconditionally, duplicate valid scaffold, move existing documents, perform broad normalization, or migrate document, section, item, or claim metadata automatically. Preserve user and other-agent changes.

## Context Readiness Boundary

Session orientation and cache/index readiness for a usable Keystone foundation are Reader work and are
not an Init mode. Init never scaffolds or repairs Linker's external cache and never treats it as source
of truth. A missing, stale, or corrupt graph/index cache does not lower the initialization state; source
documents and recovery invariants determine that state. After initialize or repair, hand first
orientation to Reader, whose repository artifact scan remains lazy until the resumed request needs it.

Do not invent project-specific `depends_on` targets or `work_gates` in the fixed R000 scaffold. During
repair, report missing or conflicting dependency targets as recovery risks without creating future IDs,
rewriting relations, or changing work status. Dependency gaps alone do not change initialization state.

## Lean Bootstrap Boundary

Create only the source documents needed to make project meaning recoverable.

1. Keep R000 and scaffold state in their owning source documents. Do not add duplicated current-state
   pointers, generated projections, or compatibility artifacts as initialization prerequisites.
2. Do not create a graph cache, finalization manifest, acceptance event, external evidence directory,
   key, receipt, or snapshot to prove initialization occurred.
3. Let Reader derive session context and let Author/Main establish and accept project meaning after the
   scaffold exists. Init never turns file creation into acceptance.
4. Preserve historical or project-specific material already present, but do not recreate a retired
   producer merely because an old record names it.

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
5. Work would exceed the fixed bootstrap authority or the explicitly selected optional integration
   authority.
6. Sensitive storage, external publication, or another high-risk action lacks authority.

## Verification

Verify that:

1. `inspect` made no changes and state came from actual files.
2. Initialize/repair changed only missing fixed scaffold and preserved existing content.
3. Document-root priority and conflicts were handled correctly.
4. R000 and its first step are `R000`/`S01`, and project-standard authoring stayed with Author.
5. No project-local skill standards, profiles, mandatory routing payloads, or host-mode claims were introduced.
6. `ready` includes accepted project meaning and recoverable work, not merely file existence.
7. New scaffold documents have their actual creation date, pending documents omit `accepted_at`, and repair preserves existing dates without speculative backfill.
8. The original request and caller resume automatically after initialization.
9. Missing document-item or claim metadata did not change initialization state, and no exhaustive item metadata was invented or migrated.
10. Project-specific dependencies and gates were not inferred or created, and dependency gaps did not mutate initialization state.
11. Session-title `yes` or explicit `configure` changed only the project-local target key; `no`, invalid
    or conflicting TOML, and every global path remained no-write.
