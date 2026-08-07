import hashlib
import tempfile
import unittest
from pathlib import Path

from graph_runtime.adapters import MarkdownAdapter
from graph_runtime.metadata import parse_source
from graph_runtime.model import (
    ApplicationResult,
    ApplicationStatus,
    AttestationDecision,
    Delta,
    DeltaKind,
    Locator,
    PatchOwner,
    PatchSurface,
    RelationType,
    SurfaceAttestation,
)
from graph_runtime.planner import (
    ImpactGrade,
    PatchSpec,
    changed_seed_candidates,
    plan_graph_sync,
)
from graph_runtime.reconciler import (
    begin_application,
    begin_attestation,
    finalize_transaction,
    record_application,
    record_attestation,
)
from graph_runtime.model import transaction_wire
from graph_runtime.validator import validate_snapshot, validate_transaction


class GraphContractChainTest(unittest.TestCase):
    def test_repository_skill_metadata_preserves_all_governance_and_production_edges(self):
        repository_root = Path(__file__).resolve().parents[3]
        expected_governance = {
            "author": ("key.standard.project", "key.standard.skill.author"),
            "clarify": ("key.standard.project", "key.standard.skill.clarify"),
            "coordinator": ("key.standard.project", "key.standard.skill.coordinator"),
            "init": (
                "key.standard.project",
                "key.standard.bootstrap",
                "key.standard.skill.init",
            ),
            "linker": ("key.standard.project", "key.standard.skill.linker"),
            "reader": ("key.standard.project", "key.standard.skill.reader"),
        }

        for skill_name, governed_by in expected_governance.items():
            with self.subTest(skill=skill_name):
                relative_path = Path("skills") / ("keystone-" + skill_name) / "SKILL.md"
                result = parse_source(
                    (repository_root / relative_path).read_text(encoding="utf-8"),
                    relative_path.as_posix(),
                    MarkdownAdapter(),
                )
                skill_id = "key.skill." + skill_name
                node = next(item for item in result.snapshot.nodes if item.id == skill_id)

                self.assertFalse(result.diagnostics)
                self.assertEqual(governed_by, node.provenance.governed_by)
                self.assertTrue({
                    (relation.source, relation.relation, relation.target)
                    for relation in result.snapshot.relations
                }.issuperset({
                    (skill_id, RelationType.GOVERNED_BY, standard_id)
                    for standard_id in governed_by
                }))
                self.assertIn(
                    (
                        "key.work.skill-runtime-implementation.order",
                        RelationType.PRODUCES,
                        skill_id,
                    ),
                    {
                        (relation.source, relation.relation, relation.target)
                        for relation in result.snapshot.relations
                    },
                )

    def test_official_verification_relation_closes_the_full_execution_chain(self):
        before = """---
key: {id: key.doc.contract, kind: source_document}
---
<!-- key: id=key.acceptance.contract kind=claim -->
## Acceptance
<!-- key: id=key.code.contract kind=output_artifact artifact_kind=code -->
## ContractCode
"""
        after = before.replace(
            "id=key.acceptance.contract kind=claim",
            "id=key.acceptance.contract kind=claim requires_verification_of=key.code.contract",
        )
        baseline = parse_source(before, "contract.md", MarkdownAdapter()).snapshot
        reconstructed_result = parse_source(after, "contract.md", MarkdownAdapter())
        reconstruction = reconstructed_result.snapshot
        relation = next(item for item in reconstruction.relations
                        if item.relation == RelationType.REQUIRES_VERIFICATION_OF)

        self.assertFalse(reconstructed_result.diagnostics)
        candidates = changed_seed_candidates(reconstruction, ("key.code.contract",))
        self.assertEqual(ImpactGrade.REQUIRED,
                         {item.node.id: item.grade for item in candidates}["key.acceptance.contract"])

        before_digest = "sha256:" + hashlib.sha256(before.encode("utf-8")).hexdigest()
        after_digest = "sha256:" + hashlib.sha256(after.encode("utf-8")).hexdigest()
        delta = Delta(DeltaKind.DOCUMENT, "contract.md", (Locator("contract.md", heading="Acceptance"),),
                      "add verification requirement", before_digest)
        patch = PatchSpec(PatchOwner.AUTHOR, PatchSurface.DOCUMENT_METADATA,
                          "contract.md", before_digest, "add requires_verification_of")
        transaction = plan_graph_sync(
            baseline, (delta,), "R007/S01",
            requested_relations_after=(relation,), patch_specs=(patch,),
            transaction_schema_version=1,
        )
        transaction = begin_attestation(transaction)
        transaction = record_attestation(transaction, SurfaceAttestation(
            transaction.surface_patches[0].patch_id, PatchOwner.AUTHOR,
            AttestationDecision.CONFIRM, "declared document relation reviewed"))
        transaction = begin_application(transaction, {
            transaction.surface_patches[0].patch_id: before_digest,
        })
        transaction = record_application(transaction, ApplicationResult(
            transaction.surface_patches[0].patch_id, ApplicationStatus.APPLIED,
            after_digest, "source bytes updated"))

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "contract.md").write_text(after, encoding="utf-8")
            mechanical = validate_snapshot(root, reconstruction, reconstructed_result.diagnostics)
            transaction = finalize_transaction(
                transaction, reconstruction, mechanical,
                {transaction.surface_patches[0].patch_id: after_digest},
                baseline_snapshot=baseline,
            )
            wire = transaction_wire(transaction, baseline_snapshot=baseline)
            self.assertEqual((), validate_transaction(wire, root, reconstruction))


if __name__ == "__main__":
    unittest.main()
