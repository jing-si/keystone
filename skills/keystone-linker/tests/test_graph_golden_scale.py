import hashlib
import json
import tempfile
import time
import unittest
from dataclasses import replace
from pathlib import Path

from graph_runtime.adapters import MarkdownAdapter
from graph_runtime.metadata import parse_source
from graph_runtime.model import (
    ArtifactKind,
    AttestationDecision,
    Delta,
    DeltaKind,
    Evidence,
    GraphSnapshot,
    Lifecycle,
    Locator,
    MutationOperation,
    Node,
    NodeKind,
    PatchOwner,
    PatchSurface,
    Provenance,
    Relation,
    RelationType,
    SurfaceAttestation,
    TransactionState,
    transaction_wire,
)
from graph_runtime.planner import (
    ImpactGrade,
    PatchSpec,
    TraversalCandidate,
    candidate_budget_projection,
    changed_seed_candidates,
    plan_graph_sync,
)
from graph_runtime.reconciler import begin_application, begin_attestation, record_attestation
from graph_runtime.validator import reconstruct, validate_snapshot, validate_transaction


class GraphGoldenScaleTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)

    def tearDown(self):
        self.directory.cleanup()

    def write(self, relative, value, binary=False):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if binary:
            path.write_bytes(value)
        else:
            path.write_text(value, encoding="utf-8")
        return path

    def test_all_supported_surfaces_match_golden_graph_and_ignore_cache(self):
        sources = {
            "docs/a.md": "---\nkey: {id: key.doc.a, kind: source_document}\n---\n# A\n",
            "src/a.ts": "// keystone: id=key.ts.a\nconst a = 1;\n",
            "src/A.kt": "// keystone: id=key.kt.a\nclass A\n",
            "src/A.java": "// keystone: id=key.java.a\nclass A {}\n",
            "schema/a.sql": "-- keystone: id=key.sql.a\ncreate table a(id int);\n",
            "config/a.xml": "<!-- keystone: id=key.xml.a -->\n<root/>\n",
            "config/a.yml": "# keystone: id=key.yaml.a\na: true\n",
        }
        for path, text in sources.items():
            self.write(path, text)
        raw = b"golden binary\n"
        self.write("assets/a.bin", raw, binary=True)
        companion = {
            "schema_version": 1,
            "source": {"path": "assets/a.bin", "surface": "companion_metadata",
                       "baseline_digest": "sha256:" + hashlib.sha256(raw).hexdigest()},
            "nodes": [{"id": "key.asset.a", "kind": "output_artifact",
                       "artifact_kind": "generated_file", "locator": {"path": "assets/a.bin"},
                       "lifecycle": "active", "provenance": {"produced_from": [], "governed_by": []}}],
            "relations": [],
        }
        self.write("assets/a.bin.keystone.json", json.dumps(companion))
        paths = tuple(sources) + ("assets/a.bin",)

        first, diagnostics = reconstruct(self.root, tuple(reversed(paths)))
        self.assertEqual((), diagnostics)
        self.assertEqual(2, first.schema_version)
        golden = [
            ("key.asset.a", "generated_file", "assets/a.bin"),
            ("key.doc.a", "none", "docs/a.md"),
            ("key.java.a", "code", "src/A.java"),
            ("key.kt.a", "code", "src/A.kt"),
            ("key.sql.a", "schema", "schema/a.sql"),
            ("key.ts.a", "code", "src/a.ts"),
            ("key.xml.a", "config", "config/a.xml"),
            ("key.yaml.a", "config", "config/a.yml"),
        ]
        self.assertEqual(golden, [(node.id, node.artifact_kind.value, node.locator.path)
                                  for node in first.nodes])

        self.write(".keystone/graph-cache.json", "{stale derived cache")
        second, diagnostics = reconstruct(self.root, paths)
        self.assertEqual((), diagnostics)
        self.assertEqual(first, second)

    def test_legacy_and_canonical_markdown_have_golden_equivalence(self):
        canonical = "<!-- key: id=key.rule.a kind=document_item depends_on=key.rule.base -->\n- Rule A\n"
        legacy = "<!-- keystone: id=key.rule.a kind=document_item depends_on=key.rule.base -->\n- Rule A\n"
        canonical_graph = parse_source(canonical, "docs/a.md", MarkdownAdapter()).snapshot
        legacy_graph = parse_source(legacy, "docs/a.md", MarkdownAdapter()).snapshot
        self.assertEqual(canonical_graph, legacy_graph)
        self.assertEqual(("key.rule.a", "depends_on", "key.rule.base"),
                         (canonical_graph.relations[0].source,
                          canonical_graph.relations[0].relation.value,
                          canonical_graph.relations[0].target))

    def test_inferred_and_unattested_observed_changes_cannot_apply(self):
        node = Node("key.cap.new", NodeKind.CAPABILITY, locator=Locator("docs/a.md"),
                    provenance=Provenance(surface="document_metadata", locator=Locator("docs/a.md")))
        delta = Delta(DeltaKind.DOCUMENT, "docs/a.md", baseline_digest="sha256:" + "1" * 64)
        patch = PatchSpec(PatchOwner.AUTHOR, PatchSurface.DOCUMENT_METADATA, "docs/a.md",
                          delta.baseline_digest, "<!-- key: id=key.cap.new -->")
        with self.assertRaisesRegex(ValueError, "inferred"):
            plan_graph_sync(GraphSnapshot(), (delta,), "S04", requested_nodes_after=(node,),
                            patch_specs=(patch,), evidence=Evidence.INFERRED)

        observed = plan_graph_sync(GraphSnapshot(), (delta,), "S04", requested_nodes_after=(node,),
                                   patch_specs=(patch,), evidence=Evidence.OBSERVED)
        awaiting = begin_attestation(observed)
        self.assertEqual(TransactionState.AWAITING_ATTESTATION, awaiting.state)
        with self.assertRaisesRegex(ValueError, "ready_to_apply"):
            begin_application(awaiting, {awaiting.surface_patches[0].patch_id: delta.baseline_digest})

    def test_move_keeps_id_and_replacement_retires_orphaning_relations(self):
        old = Node("key.cap.old", NodeKind.CAPABILITY, locator=Locator("docs/graph.md"))
        implementation = Node("key.code.impl", NodeKind.OUTPUT_ARTIFACT, ArtifactKind.CODE,
                              Locator("src/impl.py"))
        inbound = Relation(implementation.id, RelationType.IMPLEMENTS, old.id)
        baseline = GraphSnapshot((old, implementation), (inbound,))
        delta = Delta(DeltaKind.DOCUMENT, "docs/graph.md", baseline_digest="sha256:" + "1" * 64)
        patch = PatchSpec(PatchOwner.AUTHOR, PatchSurface.DOCUMENT_METADATA, "docs/graph.md",
                          delta.baseline_digest, "replacement metadata")

        moved = replace(implementation, locator=Locator("src/moved_impl.py"))
        move = plan_graph_sync(baseline, (delta,), "S04", requested_nodes_after=(moved,),
                               patch_specs=(patch,))
        self.assertEqual(implementation.id, move.canonical_mutations[0].after.id)
        self.assertEqual(MutationOperation.UPDATE, move.canonical_mutations[0].operation)

        retired = replace(old, lifecycle=Lifecycle.REMOVED)
        successor = Node("key.cap.new", NodeKind.CAPABILITY, locator=Locator("docs/graph.md"))
        history = Relation(successor.id, RelationType.SUPERSEDES, retired.id,
                           lifecycle=Lifecycle.DEPRECATED)
        replacement = plan_graph_sync(
            baseline, (delta,), "S04", requested_nodes_after=(retired, successor),
            requested_relations_after=(history,),
            requested_relation_removals=((inbound.source, inbound.relation, inbound.target),),
            patch_specs=(patch,),
        )
        self.assertEqual(4, len(replacement.canonical_mutations))
        final = GraphSnapshot((retired, successor, implementation), (history,))
        self.write("docs/graph.md", "graph")
        self.write("src/impl.py", "implementation")
        codes = {item.code for item in validate_snapshot(self.root, final)}
        self.assertNotIn("active_orphan", codes)
        self.assertNotIn("missing_target", codes)
        self.assertNotIn("active_relation_to_retired", codes)

    def test_active_canonical_supersedes_may_target_deprecated_or_removed_only(self):
        self.write("docs/replacement.md", "replacement nodes")
        self.write("src/provider.py", "provider")
        for retired_lifecycle in (Lifecycle.DEPRECATED, Lifecycle.REMOVED):
            with self.subTest(retired_lifecycle=retired_lifecycle.value):
                successor = Node("key.cap.new", NodeKind.CAPABILITY,
                                 locator=Locator("docs/replacement.md"))
                retired = Node("key.cap.old", NodeKind.CAPABILITY,
                               locator=Locator("docs/replacement.md"),
                               lifecycle=retired_lifecycle)
                replacement = Relation(successor.id, RelationType.SUPERSEDES, retired.id,
                                       Evidence.DECLARED, lifecycle=Lifecycle.ACTIVE)
                findings = validate_snapshot(
                    self.root, GraphSnapshot((successor, retired), (replacement,)))
                self.assertNotIn("active_relation_to_retired", {item.code for item in findings})

                provider = Node("key.code.provider", NodeKind.OUTPUT_ARTIFACT, ArtifactKind.CODE,
                                Locator("src/provider.py"))
                ordinary = Relation(provider.id, RelationType.PROVIDES, retired.id)
                ordinary_codes = {item.code for item in validate_snapshot(
                    self.root, GraphSnapshot((provider, retired), (ordinary,)))}
                self.assertIn("active_relation_to_retired", ordinary_codes)

                removed_successor = replace(successor, lifecycle=Lifecycle.REMOVED)
                removed_source_codes = {item.code for item in validate_snapshot(
                    self.root, GraphSnapshot((removed_successor, retired), (replacement,)))}
                self.assertIn("active_relation_to_retired", removed_source_codes)
                self.assertIn("active_relation_from_retired", removed_source_codes)

                unattested_observed = replace(replacement, evidence=Evidence.OBSERVED)
                observed_codes = {item.code for item in validate_snapshot(
                    self.root, GraphSnapshot((successor, retired), (unattested_observed,)))}
                self.assertIn("active_relation_to_retired", observed_codes)

                invalid_attestation = replace(
                    unattested_observed,
                    provenance=replace(unattested_observed.provenance, attested_by="reviewer"),
                )
                invalid_codes = {item.code for item in validate_snapshot(
                    self.root, GraphSnapshot((successor, retired), (invalid_attestation,)))}
                self.assertIn("active_relation_to_retired", invalid_codes)

                wrong_surface_owner = replace(
                    unattested_observed,
                    provenance=Provenance(surface="document_metadata",
                                          locator=Locator("docs/replacement.md"),
                                          attested_by=PatchOwner.MAIN.value),
                )
                wrong_owner_codes = {item.code for item in validate_snapshot(
                    self.root, GraphSnapshot((successor, retired), (wrong_surface_owner,)))}
                self.assertIn("active_relation_to_retired", wrong_owner_codes)

                inferred = replace(replacement, evidence=Evidence.INFERRED)
                inferred_codes = {item.code for item in validate_snapshot(
                    self.root, GraphSnapshot((successor, retired), (inferred,)))}
                self.assertIn("active_relation_to_retired", inferred_codes)

                missing_codes = {item.code for item in validate_snapshot(
                    self.root, GraphSnapshot((successor,), (replacement,)))}
                self.assertIn("missing_target", missing_codes)

        for lifecycle in (Lifecycle.SUPERSEDED, Lifecycle.ARCHIVED):
            with self.subTest(lifecycle=lifecycle.value):
                source = Node("key.cap.source", NodeKind.CAPABILITY,
                              locator=Locator("docs/replacement.md"), lifecycle=lifecycle)
                target = Node("key.cap.target", NodeKind.CAPABILITY,
                              locator=Locator("docs/replacement.md"), lifecycle=lifecycle)
                relation = Relation(source.id, RelationType.USES, target.id)
                codes = {item.code for item in validate_snapshot(
                    self.root, GraphSnapshot((source, target), (relation,)))}
                self.assertIn("active_relation_from_retired", codes)
                self.assertIn("active_relation_to_retired", codes)

    def test_observed_supersedes_owner_attestation_survives_reconstruction_validation(self):
        self.write("docs/observed-replacement.md", "replacement")
        successor = Node("key.cap.observed.new", NodeKind.CAPABILITY,
                         locator=Locator("docs/observed-replacement.md"))
        retired = Node("key.cap.observed.old", NodeKind.CAPABILITY,
                       locator=Locator("docs/observed-replacement.md"),
                       lifecycle=Lifecycle.REMOVED)
        observed = Relation(
            successor.id, RelationType.SUPERSEDES, retired.id, Evidence.OBSERVED,
            Provenance(surface="document_metadata",
                       locator=Locator("docs/observed-replacement.md")),
        )
        delta = Delta(DeltaKind.DOCUMENT, "docs/observed-replacement.md",
                      baseline_digest="sha256:" + "4" * 64)
        patch = PatchSpec(PatchOwner.AUTHOR, PatchSurface.DOCUMENT_METADATA,
                          "docs/observed-replacement.md", delta.baseline_digest,
                          "<!-- key: supersedes=key.cap.observed.old -->")
        planned = plan_graph_sync(
            GraphSnapshot((successor, retired)), (delta,), "S04",
            requested_relations_after=(observed,), patch_specs=(patch,))
        awaiting = begin_attestation(planned)
        confirmed = record_attestation(
            awaiting,
            SurfaceAttestation(awaiting.surface_patches[0].patch_id, PatchOwner.AUTHOR,
                               AttestationDecision.CONFIRM, "author confirmed replacement meaning"),
        )
        self.assertEqual(TransactionState.READY_TO_APPLY, confirmed.state)

        reconstructed = replace(
            observed,
            provenance=replace(observed.provenance, attested_by=PatchOwner.AUTHOR.value),
        )
        codes = {item.code for item in validate_snapshot(
            self.root, GraphSnapshot((successor, retired), (reconstructed,)))}
        self.assertNotIn("active_relation_to_retired", codes)

    def test_coverage_debt_does_not_promote_or_fail_current_transaction(self):
        proposed = replace(plan_graph_sync(GraphSnapshot(), (), "S04"),
                           coverage_debt=("legacy corpus is not fully annotated",))
        wire = transaction_wire(proposed)
        self.assertEqual("proposed", wire["state"])
        self.assertEqual(["legacy corpus is not fully annotated"], wire["coverage_debt"])
        self.assertEqual((), validate_transaction(wire))

    def test_required_candidate_budget_has_no_omissions(self):
        capability = Node("key.cap.root", NodeKind.CAPABILITY, locator=Locator("docs/root.md"))
        artifacts = tuple(Node("key.code.%04d" % index, NodeKind.OUTPUT_ARTIFACT, ArtifactKind.CODE,
                               Locator("src/%04d.py" % index)) for index in range(400))
        relations = tuple(Relation(node.id, RelationType.IMPLEMENTS, capability.id)
                          for node in artifacts)
        candidates = changed_seed_candidates(GraphSnapshot((capability,) + artifacts, relations),
                                             (capability.id,))
        self.assertEqual(400, len(candidates))
        self.assertTrue(all(candidate.grade == ImpactGrade.REQUIRED for candidate in candidates))
        self.assertEqual([node.id for node in artifacts], [item.node.id for item in candidates])

    def test_candidate_budget_never_truncates_required_and_reports_lower_omissions(self):
        def candidate(name, grade):
            node = Node("key.%s" % name, NodeKind.CAPABILITY,
                        locator=Locator("docs/%s.md" % name))
            return TraversalCandidate(node, grade, ("key.seed", node.id))

        candidates = tuple(
            [candidate("required.%02d" % index, ImpactGrade.REQUIRED) for index in range(5)]
            + [candidate("strong.%02d" % index, ImpactGrade.STRONG_CANDIDATE) for index in range(3)]
            + [candidate("weak.%02d" % index, ImpactGrade.WEAK_CANDIDATE) for index in range(2)]
            + [candidate("info.%02d" % index, ImpactGrade.INFORMATIONAL) for index in range(2)]
        )

        below_required = candidate_budget_projection(tuple(reversed(candidates)), 3)
        self.assertEqual(5, len(below_required["candidates"]))
        self.assertTrue(all(item["grade"] == "required" for item in below_required["candidates"]))
        self.assertEqual(0, below_required["candidate_budget"]["truncated"]["required"])
        self.assertEqual({"total": 12, "returned": 5},
                         {key: below_required["candidate_budget"]["counts"][key]
                          for key in ("total", "returned")})

        projected = candidate_budget_projection(candidates, 7)
        self.assertEqual(
            ["key.required.00", "key.required.01", "key.required.02", "key.required.03",
             "key.required.04", "key.strong.00", "key.strong.01"],
            [item["id"] for item in projected["candidates"]],
        )
        budget = projected["candidate_budget"]
        self.assertEqual({"required": 0, "strong_candidates": 1,
                          "weak_candidates": 2, "informational": 2}, budget["truncated"])
        self.assertEqual(3, len(budget["omitted_summary"]))
        self.assertEqual(
            ["strong_candidate", "weak_candidate", "informational"],
            [item["grade"] for item in budget["omitted_summary"]],
        )
        self.assertTrue(all(item["evidence_type"] == "typed_relation_traversal"
                            and item["reason"] == "candidate_budget" and item["path_range"]
                            and item["keyword_range"] for item in budget["omitted_summary"]))
        self.assertEqual(projected, candidate_budget_projection(tuple(reversed(candidates)), 7))

    def test_thousand_artifact_traversal_is_bounded_and_deterministic(self):
        count = 1200
        nodes = tuple(Node("key.cap.%04d" % index, NodeKind.CAPABILITY,
                           locator=Locator("docs/%04d.md" % index)) for index in range(count))
        relations = tuple(Relation(nodes[index].id, RelationType.DEPENDS_ON, nodes[index - 1].id)
                          for index in range(1, count))
        start = time.monotonic()
        forward = changed_seed_candidates(GraphSnapshot(nodes, relations), (nodes[0].id,))
        reversed_input = changed_seed_candidates(GraphSnapshot(tuple(reversed(nodes)),
                                                               tuple(reversed(relations))),
                                                   (nodes[0].id,))
        elapsed = time.monotonic() - start
        self.assertEqual(count - 1, len(forward))
        self.assertEqual(forward, reversed_input)
        self.assertLess(elapsed, 5.0, "bounded 1,200-node traversal exceeded 5 seconds")


if __name__ == "__main__":
    unittest.main()
