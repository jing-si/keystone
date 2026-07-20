---
name: keystone-clarify
description: "Use for exactly one actual high-impact Keystone user decision at a time when project meaning, policy, scope, document authority, conflicting valid choices, or evidence-backed modularization cannot be resolved safely. Return a decision and author-ready handoff to the caller. Do not use for built-in setup defaults, routine edits, document authoring, implementation, repository investigation, or worker orchestration."
---

<!-- keystone: id=key.skill.clarify kind=output_artifact artifact_kind=skill_source -->
<!-- keystone: produced_from=key.work.skill-runtime-implementation.order -->
<!-- keystone: governed_by=key.standard.project key.standard.skill.clarify -->

# keystone-clarify

## Purpose

Clarify exactly one high-impact user decision topic, then return the accepted decision and a bounded
handoff so the caller can resume the interrupted Init, Author, Coordinator, or Main flow.

This installed contract is self-contained. Do not require a consuming-project Clarify standard or
`standards/skills/clarify/**`. Project source documents and accepted decisions define project meaning
when they exist. Clarify output is not a source-document edit, implementation, or acceptance result.

## Use Clarify For

Use Clarify only when a real user choice can materially change one of these:

1. Project purpose, scope, policy, terminology, or authority relationships.
2. A meaningful source-document or skill-contract direction.
3. Which of multiple valid document roots is authoritative.
4. Whether existing documents should be adopted, moved, replaced, or left separate.
5. A conflict between current user direction and authoritative project documents.
6. An evidence-backed modularization choice among reuse, extend, extract shared module, create new, or
   investigate first when the choice changes architecture, scope, API/schema/test obligations, or
   verification.
7. Sensitive data handling, destructive migration, external publication or cost, or expansion beyond
   the delegated scope.

Do not use Clarify for:

1. Missing Keystone documents by itself.
2. Built-in metadata, filenames, index format, basic Context Map shape, internal routing representation,
   or the absence of project-local skill standards.
3. A safe default or explicit priority that already resolves the matter.
4. Routine wording, formatting, or narrowly scoped edits.
5. Repository investigation, document authoring, implementation, testing, or worker orchestration.
6. A modularization guess without Linker, worker, reviewer, repository, or user evidence.

## Initialization Boundary

Init may directly ask built-in setup questions such as whether to use the default document root. This
does not require Clarify. Clarify becomes appropriate only when setup exposes an actual project decision,
such as conflicting valid roots, existing-document adoption/move/replace, or uncertain project meaning.

After resolving the topic, return the result to Init or Author and let the caller resume automatically;
do not tell the user to invoke the original skill again.

Clarify is not tied to a host execution mode or question API. Use the interaction mechanism available in
the current environment, but never claim to have activated or switched a mode unless the host actually
did so.

## Inputs and Evidence

Use the current topic, user request, accepted decisions, relevant source documents and work context when
they exist, known affected surfaces, and risk context. For modularization, require concrete evidence from
a Linker report, repository finding, worker/reviewer report, or the user.

Do not require project-local skill standards. If evidence is insufficient to decide the current topic,
return it as unresolved rather than inventing project meaning or an Author-ready edit plan.

## One-Topic Question Flow

1. Reduce the issue to one decision whose alternatives have distinct practical effects.
2. Present only the evidence necessary to understand that decision.
3. Ask one focused question and briefly explain the meaningful tradeoffs.
4. Judge whether the answer is sufficient for this topic.
5. If not, ask only a targeted follow-up about the same topic.
6. If the user delegates judgment and accepted standards, repository evidence, or a safe default support
   one choice, make the bounded recommendation and state its basis.
7. Once sufficient, summarize the decision, rationale, assumptions, affected documents/artifacts, and
   any recording or edit handoff.
8. Return to the caller so the interrupted work resumes.

Do not combine unrelated decisions merely to shorten the conversation. Finish reflection and handoff for
the current topic before moving to another.

## Modularization Decision

Treat modularization as a Clarify topic only when evidence shows meaningful duplication or drift risk and
the choice changes architecture, public contracts, documentation, tests, scope, or verification. Use one
of these outcomes:

- `reuse_existing`
- `extend_existing`
- `extract_shared_module`
- `create_new`
- `investigate_first`

When evidence is weak, choose `investigate_first` as a recommendation, keep the decision unresolved, and
hand read-only discovery to Linker or a permitted investigation flow. Clarify does not establish
repository similarity on its own.

## Result Contract

For a resolved or unresolved topic, keep enough structure for the caller to resume:

```yaml
clarify_result:
  topic:
  status: resolved | unresolved
  decision_summary:
  rationale:
  working_assumptions:
  affected_documents:
    update_targets:
    inspect_only_candidates:
    excluded:
  affected_artifact_candidates:
  edit_plan:
  optional_routing_context:
  stop_conditions:
  open_questions:
    unresolved_current_topic:
    out_of_topic:
  decision_completeness_check:
    selected_option:
    rejected_options:
    affected_source_documents:
    affected_work_orders:
    acceptance_or_status_impact:
    author_edit_ready: true | false
  decision_recording_hint:
    scope: global | round | work | none | unresolved
    recommended_path:
    reason:
  modularization_decision:
  resume:
    caller:
    interrupted_step:
    next_action:
```

For an unresolved topic, set `author_edit_ready: false`, list only current-topic questions that block the
decision, and omit an actionable edit plan. Keep unrelated future questions in `out_of_topic`.

For a resolved non-trivial topic, include the completeness check and a recording hint. The hint does not
grant write authority. Record cross-round decisions in the project's shared decision record and narrower
decisions near their round/work when such locations exist. Do not create those records directly.

Only include routing context when multiple surfaces, authority boundaries, or audit needs make it useful.
Document edits go to Author, implementation may remain Main direct, and delegated work goes to
Coordinator only when the user has permitted Coordinator for that work scope.

## Default User Response

Show one focused question when a decision is unresolved. When resolved, briefly state the decision,
rationale, affected documents or surfaces, readiness to resume, and next action.

Keep the full `clarify_result` agent-facing unless the user requests it or handoff, audit, debugging, or
verification requires it. Apply the Payload Disclosure Gate: do not print raw `*_output`, `*_result`,
`*_report`, `worker_assignment`, or routing payload blocks by default.

## Boundaries and Stop Conditions

1. Handle one decision topic at a time.
2. Never edit source documents, config, code, schema, API, tests, generated files, or skill source.
3. Never orchestrate workers or grant Coordinator permission.
4. Never manufacture acceptance or infer a high-impact choice from vague input.
5. Stop the current topic when answers conflict, evidence is insufficient, sensitive information may be
   recorded, or the choice would exceed delegated scope.
6. If implementation or investigation must happen before the decision, return an unresolved result and
   the bounded next action.

## Verification

Check that Clarify:

1. Runs without a consuming-project `standards/skills/clarify/**` document.
2. Asks about one actual high-impact decision at a time.
3. Does not ask about built-in setup mechanics, safe defaults, internal routing, or local skill standards.
4. Lets Init ask built-in setup questions directly.
5. Does not claim or depend on Plan Mode or another host mode.
6. Returns enough decision, completeness, and resume context for Init or Author to continue.
7. Never edits files and hides structured payloads by default.
