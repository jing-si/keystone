# Management review workflow

Use this procedure for a requested Round check or a due/explicit full connection review. This is
Keystone document/metadata/code traceability, not application correctness testing. Reuse valid source
context; do not perform full review at every implementation step.

## Configuration and creation

- At Init or the first policy-relevant Round creation/closure, if review mode is unset, output
  `references/work-structure-and-review-mode.ko.md` verbatim as ordinary Markdown. Preserve wording,
  line breaks, tree, emphasis, and question. Do not add a box, code fence, colors, or translate/rewrite
  the approved Korean copy. For other languages explain that the approved fixed copy is Korean.
- Save the user's general/sprint choice with the package-local managed state CLI's `review configure`
  operation, using `mode` in payload JSON and the current singleton digest. Reconfiguration preserves
  both lists. Ordinary Reader orientation never prompts or changes mode.
- Do not silently migrate a legacy corpus or create a managed marker merely to use review state.
  The managed backend must own actual Round create/close/reopen events. If the project is legacy,
  explain the migration boundary and retain its existing execution until adoption is authorized.
- Author includes a visible Round connection-check Step at creation. For a top-level sprint, include
  full review instead of duplicating its local check. Use Round/Step as the base, Work/Task optionally.
- New/edited Work Orders declare `key.defined_steps: [S01, S02, ...]` at the definition source.
  It identifies the local plan, not state. Do not create duplicate registries or annotate the corpus.

## Round check

Read the feature's accepted intent/work plan, corresponding standards, code connections, declared
metadata/graph and necessary counterpart documents. Confirm changed standards or justified no_change,
move/delete/replacement references, and existing deferrals. Input omission is not a broken reference;
find the required current counterpart. Preserve old worktree locators as history. For this review use
the current repository snapshot, not an old execution worktree. Resume of implementation remains a
separate locator-sensitive procedure. Do not expand to unrelated features or test application behavior.

## Full review and snapshot

1. On actual Round Closed, the state mutation returns review_advice. Prompt only when prompt is true:
   general/no wait uses positive multiples of five; waiting suppresses periodic prompts until every
   waiting ref is in closed_list, then every Closed prompts. Refusal does not mutate either list.
   Work/Step closure and ordinary reads never count. Sprint full review is its planned terminal Step.
2. Coordinate a brief pause of writers, inspect managed source/doc/state changes including work in
   progress, and commit the snapshot using normal Git checks. Do not blindly add secrets/generated
   scratch, bypass hooks, or call the commit acceptance. Do not require each Round to commit at close.
   A writer that cannot pause means the snapshot is not ready; do not pretend live changes are included.
3. Capture `review-ticket --commit FULL_HASH [--sprint-round Rnnn]` from the original repository at this
   fixed state, then create an isolated review worktree of that exact commit. Resume original writers.
   Keep the ticket in session or a temporary external file, never a required permanent evidence store.
   It is bound to the original root: finish against that root, not the review worktree. Validate the
   recorded commit against the worktree HEAD; the state CLI does not execute Git or certify source reads.
4. Review every snapshot closed_list Work Order's change intent against standards, then inspect all
   declared graph connections and material standard/code alignment. Include the top-level sprint's
   own scope even though it has not closed. Existing unchanged evidence can be reused only with a
   known source baseline. Show reviewed/reused/unconfirmed scope accurately.
5. Ongoing work only needs bounded conflict checks against existing decisions/content. Missing unfinished
   code/links alone do not prevent completion. It becomes a full target after its Round closes.
6. A large ongoing revision that prevents judging closed work defers review. Explain the reason and
   register responsible Round refs using `review defer`: payload rounds, reason, and sprint_round when
   applicable. Never wait for the sprint itself; finish its own remaining work before retrying review.
   Preserve lists. Tool/access errors are partial review, not success; resume unconfirmed scope and
   recheck previously examined inputs only if relevant source changed.

## Findings, integration and cleanup

- Repair simple reference/state mistakes within approved scope. For meaning/code changes explain
  impact/options; for large repairs recommend a Round and ask whether to create it. User chooses its
  placement. Creation alone is not execution. Honor existing documented deferrals unless evidence changes.
- Do not merge/overwrite snapshot files wholesale into current work. Compare the exact affected current
  sections, apply unchanged-context fixes, and recheck changed context only. If meaning or scope grows,
  return that decision to the user. Keep unrelated parallel edits.
- Record scope, commit, disposition and remaining uncertainty in existing Work/Step records; a general
  full review needs no new Round or Step. Tool success is not semantic acceptance. Completion means
  scope checked and findings fixed or assigned a recorded user/follow-up disposition, not every defect fixed.
- After results are integrated and recorded, finish with payload ticket, outcome=complete,
  results_applied=true and the latest state digest. Partial/blocked/declined review never calls finish.
  Occurrence tokens ensure concurrently added/reclosed Rounds and newly registered waits survive.
- Sprint: full review including parent scope → results integration/recording → close parent through the
  normal state API → finish with the same sprint ticket. A reopened parent invalidates this ticket.
  A parent's newly appended identical closure is removed, unrelated closures remain. Neither completion
  command grants acceptance nor automatically closes work. On success remove the disposable review
  worktree after confirming no required unintegrated result remains.

## CLI operations

The package-local `scripts/managed_work_state.py --root ROOT` supports:

- `review --operation configure --payload-json FILE --expected-digest DIGEST` with `{mode: general|sprint}`.
- `review --operation defer --payload-json FILE --expected-digest DIGEST` with `{rounds: [R...], reason: ...,
  sprint_round: R...}` (sprint_round only for sprint termination).
- `review-ticket --commit HASH [--sprint-round R...]` returns a read-only ticket.
- `review --operation finish --payload-json FILE --expected-digest DIGEST` with `{ticket: ..., outcome:
  complete, results_applied: true}`. Use real JSON. DIGEST comes from list.sources; use none only if absent.

A successful operation is a mechanical state update, never proof of the content review. Recovery and
stale-write handling use R024's existing singleton lock, pending transaction and digest contract.
