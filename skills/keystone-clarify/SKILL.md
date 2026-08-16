---
name: keystone-clarify
description: "Use for actual high-impact Keystone user decisions when project meaning, policy, scope, document authority, conflicting valid choices, or evidence-backed modularization cannot be resolved safely. When one broad review yields multiple changes, group them by coherent document-application scope and still ask exactly one question at a time. Return lightweight Q&A-log and group-ready Author handoffs to the caller. Do not use for built-in setup defaults, routine edits, document authoring, implementation, repository investigation, or worker orchestration."
---

<!-- keystone: id=key.skill.clarify kind=output_artifact artifact_kind=skill_source -->
<!-- keystone: produced_from=key.work.skill-runtime-implementation.order -->
<!-- keystone: governed_by=key.standard.project key.standard.skill.clarify -->

# keystone-clarify

## Purpose

Clarify exactly one high-impact user decision topic at a time, then return the accepted decision and a
bounded handoff so the caller can resume the interrupted Init, Author, Coordinator, or Main flow. When
one broad review contains several changes, group them by shared document-application scope and close one
group before moving to the next.

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

## Internal Index and Graph Management Boundary

Accepted operational rules for owner/ref cache location, refresh, docs/repository scan timing, and
transaction/repository validation scope are not a user decision topic. Do not ask the user how a
permissionless Linker should scan, index, or validate. Treat cache failure with source fallback and a
risk report.

Ask one high-impact question only when Linker evidence leaves multiple valid choices about project
meaning, policy, scope, or authority. Coverage debt alone is not permission to ask for scope expansion.
In decision and edit-plan metadata, use `requires_verification_of` for a verification requirement; it
does not promote to `verifies` before an actual test artifact or verification result supplies evidence.

## Fixed Workflow Boundaries

Do not ask the user to choose mechanics already fixed by accepted Keystone policy. Current source and
diff verification, optional disposable caches, source-owner writes, the two-level Round maximum, and
the absence of mandatory external evidence are operational boundaries rather than decision topics.

If a plan would require a child below a child, return it to Author/Main as
`NEEDS_SCOPE_CHANGE / work_order_restructure`. Ask one Clarify question only when the remaining choice
among reducing the Goal, creating sibling children, or opening a separate parent Round materially
changes user-owned scope or meaning. Never ask whether to recreate a retired manifest, key, receipt,
snapshot, or external evidence directory for current work.

## Inputs and Evidence

Use the current topic, user request, accepted decisions, relevant source documents and work context when
they exist, known affected surfaces, and risk context. For modularization, require concrete evidence from
a Linker report, repository finding, worker/reviewer report, or the user.

When available evidence identifies stable document-item or claim IDs, preserve them in the result. If a
decision replaces only part of an earlier decision or rule, identify the affected claim and the retained
meaning separately; do not describe a partial replacement as document-level or whole-decision
supersession. Clarify may carry Linker evidence but does not infer missing graph relations on its own.

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
8. After every user answer, give the caller only the actual question, answer, answer timestamp, and
   group/question locator needed for a lightweight Author log append. Do not add evaluation or status.
9. Return to the caller so the interrupted work resumes.

Do not combine unrelated decisions merely to shorten the conversation. Finish reflection and handoff for
the current topic before moving to another.

## Broad Subject and Group Queue

When the caller supplies several findings from one broad review, organize them before asking questions.

1. Keep one broad subject for the complete review. It maps to one Work-attached clarification log.
2. Define a group as one coherent source-document application boundary, not as a decision or status.
   Assign only an ordered locator and a short edit-scope title such as `G01`.
3. Group findings when they affect the same documents or sections, their answers must be interpreted
   together, applying one early could create inconsistency or rework, or one verification boundary can
   close them together.
4. Split findings when their target documents, acceptance meaning, application timing, and verification
   are independent. Do not group merely by adjacent numbering, presentation order, or question count.
5. If the user delegates grouping, choose the smallest coherent application boundary from accepted
   sources and evidence. Ask the user only if grouping would change user-owned scope or meaning.
6. Select one group and ask exactly one decision question. Continue only that topic's targeted follow-up
   until sufficient, then proceed to the next topic in the same group.
7. When no material question blocks the group, consolidate its topic results into one Author-ready edit
   plan. Do not create a `Group Decision`, group score, evaluation, or completion artifact.
8. Let the caller invoke Author once for that group's source changes, then continue with the next group.
   After every group is handled, resume the task that originally requested Clarify.

The caller owns persistence. For a known Work node, have it create or update
`clarify/{YYYYMMDDTHHmmssZ}-{topic-slug}.md` through Author. Keep all groups for the broad subject in that
one file using `# {broad subject}`, `## G01 - {edit scope}`, and `### Q01 - {question summary}`. Record only
`질문`, `답변`, and `답변일시`. A blank answer already means unanswered; do not add a remaining-question
section. Do not put `Group Decision`, `Author Application`, sufficiency, evaluation, score, group status,
or work status in the log. Add optional question-level key metadata only when the answer actually affects
a source document; it remains a navigation hint, not authority or evaluation evidence.

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
      - path:
        item_or_claim_ids:
        partial_supersession:
          superseding_id:
          superseded_ids:
          retained_meaning:
        reason:
        required_change:
    inspect_only_candidates:
    excluded:
  affected_artifact_candidates:
  edit_plan:
    - path:
      target_item_or_claim_ids:
      relation_changes:
      legacy_term_review:
      required_change:
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

Item or claim IDs in this result are Author handoff locators, not edit authority. Include relation changes
such as `supersedes` only when the accepted decision or supplied Linker evidence establishes them. For a
partial supersession, name the new and old claim IDs, state what meaning remains authoritative, and add
legacy-term review when former names or identifiers may remain in active items.

For a resolved non-trivial topic, include the completeness check and a recording hint. The hint does not
grant write authority. Record cross-round decisions in the project's shared decision record and narrower
decisions near their round/work when such locations exist. Do not create those records directly.

During grouped clarification, let the caller accumulate topic results only inside the current group.
Create the source-document edit handoff once, after every material question in that group is resolved.
Keep this agent-facing queue and completeness state out of the clarification log.

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
7. Never convert a document-level impact guess into an item/claim relation without accepted decision or
   Linker evidence.

## Verification

Check that Clarify:

1. Runs without a consuming-project `standards/skills/clarify/**` document.
2. Asks about one actual high-impact decision at a time.
3. Does not ask about built-in setup mechanics, safe defaults, internal routing, or local skill standards.
4. Lets Init ask built-in setup questions directly.
5. Does not claim or depend on Plan Mode or another host mode.
6. Returns enough decision, completeness, and resume context for Init or Author to continue.
7. Never edits files and hides structured payloads by default.
8. Preserves affected item/claim IDs and represents partial supersession without retiring unaffected
   meaning.
9. Groups a broad review by coherent source-application scope before questioning while preserving the
   exactly-one-question invariant.
10. Separates per-answer lightweight log handoff from per-group source-document application and resumes
    the original task after all groups.
11. Keeps one minimal, non-authoritative clarification log per broad subject without decision,
    evaluation, or status fields.
