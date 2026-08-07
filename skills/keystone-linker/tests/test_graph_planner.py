import hashlib
import unittest

from graph_runtime.model import (
    ArtifactKind,
    Delta,
    DeltaKind,
    Evidence,
    GraphSnapshot,
    Lifecycle,
    Locator,
    MutationEvidence,
    MutationEntity,
    MutationOperation,
    Node,
    NodeKind,
    PatchOwner,
    PatchSurface,
    Provenance,
    Relation,
    RelationType,
)
from graph_runtime.planner import (
    DirectRelationCase,
    ImpactGrade,
    PatchSpec,
    changed_seed_candidates,
    plan_graph_sync,
)


class GraphPlannerTests(unittest.TestCase):
    def setUp(self):
        self.document = Node("key.doc.feature", NodeKind.SOURCE_DOCUMENT,
                             locator=Locator("00_docs/feature.md"))
        self.item = Node("key.item.feature", NodeKind.DOCUMENT_ITEM,
                         locator=Locator("00_docs/feature.md", heading="Feature"))
        self.capability = Node("key.capability.feature", NodeKind.CAPABILITY,
                               locator=Locator("00_docs/feature.md", heading="Feature"))
        self.code = Node("key.artifact.feature", NodeKind.OUTPUT_ARTIFACT, ArtifactKind.CODE,
                         Locator("src/feature.py", symbol="Feature"))
        self.test = Node("key.test.feature", NodeKind.OUTPUT_ARTIFACT, ArtifactKind.TEST,
                         Locator("tests/test_feature.py", test_name="test_feature"))
        self.snapshot = GraphSnapshot(
            nodes=(self.document, self.item, self.capability, self.code, self.test),
            relations=(
                Relation(self.item.id, RelationType.DOCUMENTS, self.capability.id),
                Relation(self.code.id, RelationType.PROVIDES, self.capability.id),
                Relation(self.test.id, RelationType.VERIFIES, self.capability.id),
            ),
        )
        self.delta = Delta(DeltaKind.DOCUMENT, "00_docs/feature.md",
                           (Locator("00_docs/feature.md", heading="Feature"),),
                           "declare capability", "sha256:" + "1" * 64)
        self.patch = PatchSpec(PatchOwner.AUTHOR, PatchSurface.DOCUMENT_METADATA,
                               "00_docs/feature.md", "sha256:" + "1" * 64,
                               "<!-- key: id=key.capability.new -->")

    def test_plan_emits_exact_add_mutation_and_stable_patch_id(self):
        new_node = Node("key.capability.new", NodeKind.CAPABILITY,
                        locator=Locator("00_docs/feature.md", heading="New"))
        first = plan_graph_sync(self.snapshot, (self.delta,), "scope:s02",
                                requested_nodes_after=(new_node,), patch_specs=(self.patch,))
        second = plan_graph_sync(self.snapshot, (self.delta,), "scope:s02",
                                 requested_nodes_after=(new_node,), patch_specs=(self.patch,))

        self.assertEqual(first, second)
        self.assertEqual(first.canonical_mutations[0].operation, MutationOperation.ADD)
        self.assertEqual(first.canonical_mutations[0].entity, MutationEntity.NODE)
        self.assertEqual(first.canonical_mutations[0].after, new_node)
        self.assertEqual(first.surface_patches[0].baseline_digest, self.delta.baseline_digest)
        self.assertEqual(first.surface_patches[0].patch_id, second.surface_patches[0].patch_id)

    def test_update_uses_exact_existing_before_state(self):
        moved = Node(self.code.id, self.code.kind, self.code.artifact_kind,
                     Locator("src/new_feature.py", symbol="Feature"))
        transaction = plan_graph_sync(self.snapshot, (self.delta,), "scope:s02",
                                      requested_nodes_after=(moved,), patch_specs=(self.patch,))
        mutation = transaction.canonical_mutations[0]
        self.assertEqual(mutation.operation, MutationOperation.UPDATE)
        self.assertEqual(mutation.before, self.code)
        self.assertEqual(mutation.after, moved)

    def test_inferred_evidence_is_rejected(self):
        new_node = Node("key.capability.new", NodeKind.CAPABILITY,
                        locator=Locator("00_docs/feature.md"))
        with self.assertRaisesRegex(ValueError, "inferred"):
            plan_graph_sync(self.snapshot, (self.delta,), "scope:s02",
                            requested_nodes_after=(new_node,), patch_specs=(self.patch,),
                            evidence=Evidence.INFERRED)

        inferred_relation = Relation(self.code.id, RelationType.USES, self.test.id,
                                     Evidence.INFERRED)
        with self.assertRaisesRegex(ValueError, "inferred"):
            plan_graph_sync(self.snapshot, (self.delta,), "scope:s02",
                            requested_relations_after=(inferred_relation,),
                            patch_specs=(self.patch,))

        inferred_snapshot = GraphSnapshot(
            self.snapshot.nodes, self.snapshot.relations + (inferred_relation,))
        declared_replacement = Relation(self.code.id, RelationType.USES, self.test.id,
                                        Evidence.DECLARED)
        with self.assertRaisesRegex(ValueError, "inferred"):
            plan_graph_sync(inferred_snapshot, (self.delta,), "scope:s02",
                            requested_relations_after=(declared_replacement,),
                            patch_specs=(self.patch,))

    def test_observed_evidence_is_preserved_for_owner_attestation(self):
        new_node = Node("key.capability.new", NodeKind.CAPABILITY,
                        locator=Locator("00_docs/feature.md"))
        transaction = plan_graph_sync(self.snapshot, (self.delta,), "scope:s02",
                                      requested_nodes_after=(new_node,), patch_specs=(self.patch,),
                                      evidence=Evidence.OBSERVED)
        self.assertEqual(transaction.canonical_mutations[0].evidence, MutationEvidence.OBSERVED)

        observed_relation = Relation(self.code.id, RelationType.USES, self.test.id,
                                     Evidence.OBSERVED,
                                     Provenance(surface="document_metadata",
                                                locator=Locator("00_docs/feature.md")))
        relation_transaction = plan_graph_sync(
            self.snapshot, (self.delta,), "scope:s02",
            requested_relations_after=(observed_relation,), patch_specs=(self.patch,))
        self.assertEqual(relation_transaction.canonical_mutations[0].evidence,
                         MutationEvidence.OBSERVED)

        unrelated_patch = PatchSpec(PatchOwner.MAIN, PatchSurface.CODE_ANCHOR,
                                    "src/unrelated.py", "sha256:" + "4" * 64,
                                    "// unrelated")
        with self.assertRaisesRegex(ValueError, "owning surface"):
            plan_graph_sync(self.snapshot, (self.delta,), "scope:s02",
                            requested_nodes_after=(new_node,), patch_specs=(unrelated_patch,),
                            evidence=Evidence.OBSERVED)

    def test_direct_item_to_artifact_requires_named_bounded_case_and_reason(self):
        direct = Relation(self.item.id, RelationType.DOCUMENTS, self.code.id)
        with self.assertRaisesRegex(ValueError, "capability-first"):
            plan_graph_sync(self.snapshot, (self.delta,), "scope:s02",
                            requested_relations_after=(direct,), patch_specs=(self.patch,))
        with self.assertRaisesRegex(ValueError, "direct_relation_reason"):
            plan_graph_sync(
                self.snapshot, (self.delta,), "scope:s02",
                requested_relations_after=(direct,), patch_specs=(self.patch,),
                direct_relation_case=DirectRelationCase.SINGLE_POLICY_IMPLEMENTATION,
            )

        transaction = plan_graph_sync(
            self.snapshot, (self.delta,), "scope:s02",
            requested_relations_after=(direct,), patch_specs=(self.patch,),
            direct_relation_case=DirectRelationCase.SINGLE_POLICY_IMPLEMENTATION,
            direct_relation_reason="One policy implemented by this artifact only.",
        )
        self.assertEqual(transaction.canonical_mutations[0].direct_relation_reason,
                         "One policy implemented by this artifact only.")

    def test_changed_seed_traversal_returns_every_directly_connected_candidate(self):
        candidates = changed_seed_candidates(self.snapshot, (self.capability.id,))
        self.assertEqual(tuple(candidate.node.id for candidate in candidates),
                         (self.code.id, self.item.id, self.test.id))
        self.assertEqual({candidate.node.id: candidate.grade for candidate in candidates}, {
            self.code.id: ImpactGrade.REQUIRED,
            self.item.id: ImpactGrade.STRONG_CANDIDATE,
            self.test.id: ImpactGrade.REQUIRED,
        })

    def test_verification_requirement_traverses_and_plans_without_bounded_direct_exception(self):
        requirement = Relation(
            self.item.id, RelationType.REQUIRES_VERIFICATION_OF, self.code.id)
        snapshot = GraphSnapshot(self.snapshot.nodes, self.snapshot.relations + (requirement,))

        candidates = changed_seed_candidates(snapshot, (self.code.id,))
        by_id = {candidate.node.id: candidate.grade for candidate in candidates}
        self.assertEqual(ImpactGrade.REQUIRED, by_id[self.item.id])

        transaction = plan_graph_sync(
            self.snapshot, (self.delta,), "scope:s02",
            requested_relations_after=(requirement,), patch_specs=(self.patch,),
        )
        self.assertEqual(RelationType.REQUIRES_VERIFICATION_OF,
                         transaction.canonical_mutations[0].after.relation)

    def test_required_propagation_recurses_without_hiding_two_hop_candidates(self):
        code_test = Relation(self.test.id, RelationType.VERIFIES, self.code.id)
        without_direct_test = tuple(
            relation for relation in self.snapshot.relations
            if not (relation.source == self.test.id and relation.target == self.capability.id))
        snapshot = GraphSnapshot(self.snapshot.nodes, without_direct_test + (code_test,))
        candidates = changed_seed_candidates(snapshot, (self.capability.id,))
        by_id = {candidate.node.id: candidate for candidate in candidates}
        self.assertEqual(by_id[self.code.id].grade, ImpactGrade.REQUIRED)
        self.assertEqual(by_id[self.test.id].grade, ImpactGrade.REQUIRED)
        self.assertIn(self.code.id, by_id[self.test.id].via)

    def test_directional_propagation_does_not_upgrade_provider_target(self):
        candidates = changed_seed_candidates(self.snapshot, (self.code.id,))
        by_id = {candidate.node.id: candidate.grade for candidate in candidates}
        self.assertEqual(by_id[self.capability.id], ImpactGrade.STRONG_CANDIDATE)
        self.assertNotIn(self.test.id, by_id)

    def test_impact_grade_is_capped_by_evidence_and_lifecycle(self):
        cases = (
            (Evidence.DECLARED, Lifecycle.ACTIVE, Provenance(), ImpactGrade.REQUIRED),
            (Evidence.OBSERVED, Lifecycle.ACTIVE, Provenance(), ImpactGrade.WEAK_CANDIDATE),
            (Evidence.OBSERVED, Lifecycle.ACTIVE, Provenance(
                surface="test_anchor",
                locator=Locator("tests/test_feature.py"),
                attested_by="main",
            ), ImpactGrade.STRONG_CANDIDATE),
            (Evidence.INFERRED, Lifecycle.ACTIVE, Provenance(), ImpactGrade.WEAK_CANDIDATE),
            (Evidence.DECLARED, Lifecycle.DEPRECATED, Provenance(), ImpactGrade.INFORMATIONAL),
        )
        for evidence, lifecycle, provenance, expected in cases:
            with self.subTest(evidence=evidence, lifecycle=lifecycle):
                relation = Relation(
                    self.test.id, RelationType.VERIFIES, self.capability.id,
                    evidence, provenance, lifecycle,
                )
                snapshot = GraphSnapshot(self.snapshot.nodes, (relation,))
                candidates = changed_seed_candidates(snapshot, (self.capability.id,))
                self.assertEqual(expected, candidates[0].grade)

        archived = Relation(
            self.test.id, RelationType.VERIFIES, self.capability.id,
            Evidence.DECLARED, lifecycle=Lifecycle.ARCHIVED,
        )
        self.assertEqual((), changed_seed_candidates(
            GraphSnapshot(self.snapshot.nodes, (archived,)), (self.capability.id,)
        ))

    def test_each_patch_baseline_must_match_its_source_delta(self):
        wrong = PatchSpec(PatchOwner.AUTHOR, PatchSurface.DOCUMENT_METADATA,
                          self.patch.target_path, "sha256:" + "2" * 64, self.patch.exact_patch)
        with self.assertRaisesRegex(ValueError, "baseline"):
            plan_graph_sync(self.snapshot, (self.delta,), "scope:s02",
                            patch_specs=(wrong,))

    def test_executable_patch_selects_schema_v2_and_preserves_replay_fields(self):
        baseline = "before\n"
        body = "replacement\n"
        baseline_digest = "sha256:" + hashlib.sha256(baseline.encode()).hexdigest()
        delta = Delta(
            self.delta.kind,
            self.delta.source_surface,
            self.delta.changed_locators,
            self.delta.semantic_summary,
            baseline_digest,
        )
        enhanced = PatchSpec(
            PatchOwner.AUTHOR,
            PatchSurface.DOCUMENT_METADATA,
            self.patch.target_path,
            baseline_digest,
            body,
            patch_format="full_replacement",
            patch_body=body,
            expected_after_digest="sha256:" + hashlib.sha256(body.encode()).hexdigest(),
            baseline_content=baseline,
        )

        transaction = plan_graph_sync(
            self.snapshot, (delta,), "scope:s02", patch_specs=(enhanced,)
        )

        self.assertEqual(2, transaction.schema_version)
        self.assertEqual("full_replacement", transaction.surface_patches[0].patch_format)
        self.assertEqual(body, transaction.surface_patches[0].patch_body)
        self.assertEqual("sha256:" + hashlib.sha256(body.encode()).hexdigest(),
                         transaction.surface_patches[0].expected_after_digest)
        self.assertEqual(baseline, transaction.surface_patches[0].baseline_content)

        invalid = PatchSpec(
            PatchOwner.AUTHOR,
            PatchSurface.DOCUMENT_METADATA,
            self.patch.target_path,
            baseline_digest,
            "description",
            patch_format="full_replacement",
            patch_body=body,
            expected_after_digest="sha256:" + "a" * 64,
            baseline_content=baseline,
        )
        with self.assertRaisesRegex(ValueError, "exact_patch"):
            plan_graph_sync(
                self.snapshot, (delta,), "scope:s02", patch_specs=(invalid,)
            )

    def test_delta_and_patch_input_order_does_not_change_transaction(self):
        artifact_delta = Delta(DeltaKind.ARTIFACT, "src/feature.py",
                               (Locator("src/feature.py", symbol="Feature"),),
                               "anchor update", "sha256:" + "2" * 64)
        code_patch = PatchSpec(PatchOwner.MAIN, PatchSurface.CODE_ANCHOR,
                               "src/feature.py", artifact_delta.baseline_digest,
                               "// keystone: id=key.artifact.feature")
        first = plan_graph_sync(self.snapshot, (self.delta, artifact_delta), "scope:s02",
                                patch_specs=(self.patch, code_patch))
        second = plan_graph_sync(self.snapshot, (artifact_delta, self.delta), "scope:s02",
                                 patch_specs=(code_patch, self.patch))
        self.assertEqual(first, second)

    def test_invalid_delta_baseline_is_rejected(self):
        malformed = Delta(DeltaKind.DOCUMENT, "00_docs/feature.md",
                          baseline_digest="SHA256:not-canonical")
        with self.assertRaisesRegex(ValueError, "baseline"):
            plan_graph_sync(self.snapshot, (malformed,), "scope:s02")

    def test_contradictory_after_state_and_removal_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "both after-state and removal"):
            plan_graph_sync(self.snapshot, (self.delta,), "scope:s02",
                            requested_nodes_after=(self.code,),
                            requested_node_removals=(self.code.id,))
        relation = self.snapshot.relations[0]
        with self.assertRaisesRegex(ValueError, "both after-state and removal"):
            plan_graph_sync(self.snapshot, (self.delta,), "scope:s02",
                            requested_relations_after=(relation,),
                            requested_relation_removals=((relation.source, relation.relation,
                                                         relation.target),))

    def test_duplicate_patch_specs_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate patch"):
            plan_graph_sync(self.snapshot, (self.delta,), "scope:s02",
                            patch_specs=(self.patch, self.patch))

    def test_direct_relation_case_must_match_bounded_artifact_kind(self):
        direct_code = Relation(self.item.id, RelationType.DOCUMENTS, self.code.id)
        with self.assertRaisesRegex(ValueError, "schema"):
            plan_graph_sync(
                self.snapshot, (self.delta,), "scope:s02",
                requested_relations_after=(direct_code,), patch_specs=(self.patch,),
                direct_relation_case=DirectRelationCase.SINGLE_SCHEMA_CONSTRAINT,
                direct_relation_reason="One constraint only.")
        direct_test = Relation(self.item.id, RelationType.DOCUMENTS, self.test.id)
        with self.assertRaisesRegex(ValueError, "policy"):
            plan_graph_sync(
                self.snapshot, (self.delta,), "scope:s02",
                requested_relations_after=(direct_test,), patch_specs=(self.patch,),
                direct_relation_case=DirectRelationCase.SINGLE_POLICY_IMPLEMENTATION,
                direct_relation_reason="Not actually a policy implementation.")

    def test_patch_owner_surface_matrix_rejects_physical_owner_mismatch(self):
        forbidden = (
            PatchSpec(PatchOwner.MAIN, PatchSurface.DOCUMENT_METADATA,
                      self.patch.target_path, self.patch.baseline_digest, "x"),
            PatchSpec(PatchOwner.AUTHOR, PatchSurface.CODE_ANCHOR,
                      "src/feature.py", "sha256:" + "2" * 64, "x"),
            PatchSpec(PatchOwner.AUTHOR, PatchSurface.COMPANION_METADATA,
                      "src/feature.bin.keystone.json", "sha256:" + "3" * 64, "x"),
        )
        for patch in forbidden:
            with self.subTest(patch=patch), self.assertRaisesRegex(ValueError, "owner.*surface"):
                plan_graph_sync(self.snapshot, (self.delta,), "scope:s02", patch_specs=(patch,))

    def test_document_companion_is_author_owned_and_repository_companion_is_main_owned(self):
        document = PatchSpec(PatchOwner.AUTHOR, PatchSurface.COMPANION_METADATA,
                             "docs/feature.md.keystone.json", "sha256:" + "2" * 64, "x")
        repository = PatchSpec(PatchOwner.MAIN, PatchSurface.COMPANION_METADATA,
                               "assets/feature.bin.keystone.json", "sha256:" + "3" * 64, "x")
        transaction = plan_graph_sync(self.snapshot, (self.delta,), "scope:s02",
                                      patch_specs=(document, repository))
        self.assertEqual(2, len(transaction.surface_patches))

    def test_graph_change_requires_at_least_one_required_patch(self):
        new_node = Node("key.capability.new", NodeKind.CAPABILITY,
                        locator=Locator("00_docs/feature.md"))
        optional = PatchSpec(PatchOwner.AUTHOR, PatchSurface.DOCUMENT_METADATA,
                             self.patch.target_path, self.patch.baseline_digest, "x", required=False)
        with self.assertRaisesRegex(ValueError, "required patch"):
            plan_graph_sync(self.snapshot, (self.delta,), "scope:s02",
                            requested_nodes_after=(new_node,), patch_specs=(optional,))


if __name__ == "__main__":
    unittest.main()
