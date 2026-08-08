import unittest

from graph_runtime.model import ArtifactKind, Locator, NodeKind
from graph_runtime.source_hierarchy import build_source_node


class SourceHierarchyTest(unittest.TestCase):
    def setUp(self):
        self.path = "00_docs/standard.md"
        self.parent = build_source_node(
            {
                "_document_lifecycle": "archived",
                "_approval_state": "pending",
                "governed_by": ["key.standard.project"],
                "_source_authority": {"source": "project-standard"},
            },
            "key.doc.standard",
            NodeKind.SOURCE_DOCUMENT,
            ArtifactKind.NONE,
            Locator(self.path),
            "document_metadata",
            None,
            self.path,
        ).node

    def test_child_inherits_parent_effective_metadata(self):
        result = build_source_node(
            {},
            "key.section.standard",
            NodeKind.DOCUMENT_SECTION,
            ArtifactKind.NONE,
            Locator(self.path, heading="Section"),
            "document_metadata",
            self.parent,
            self.path,
        )

        self.assertEqual((), result.diagnostics)
        self.assertEqual(self.parent.lifecycle, result.node.lifecycle)
        self.assertEqual(self.parent.approval_state, result.node.approval_state)
        self.assertEqual(
            self.parent.provenance.governed_by,
            result.node.provenance.governed_by,
        )
        self.assertEqual(self.parent.source_authority, result.node.source_authority)
        self.assertEqual(self.parent.id, result.node.parent_id)

    def test_child_governance_is_additive_while_authority_expansion_is_clamped(self):
        result = build_source_node(
            {
                "_approval_state": "accepted",
                "governed_by": ["key.standard.other"],
                "_source_authority": {"source": "other"},
            },
            "key.claim.standard",
            NodeKind.DOCUMENT_ITEM,
            ArtifactKind.NONE,
            Locator(self.path, symbol="Claim"),
            "document_metadata",
            self.parent,
            self.path,
        )

        self.assertEqual(
            [
                "approval_authority_expansion",
                "source_authority_expansion",
            ],
            [item.code for item in result.diagnostics],
        )
        self.assertEqual(self.parent.approval_state, result.node.approval_state)
        self.assertEqual(
            ("key.standard.project", "key.standard.other"),
            result.node.provenance.governed_by,
        )
        self.assertEqual(self.parent.source_authority, result.node.source_authority)

    def test_output_artifact_does_not_inherit_document_domain_metadata(self):
        result = build_source_node(
            {},
            "key.code.feature",
            NodeKind.OUTPUT_ARTIFACT,
            ArtifactKind.CODE,
            Locator("src/feature.py", symbol="run"),
            "code_anchor",
            self.parent,
            "00_docs/standard.md",
        )

        self.assertEqual((), result.diagnostics)
        self.assertEqual("active", result.node.lifecycle.value)
        self.assertIsNone(result.node.approval_state)
        self.assertEqual((), result.node.provenance.governed_by)
        self.assertEqual((), result.node.source_authority)
        self.assertEqual(self.parent.id, result.node.parent_id)

    def test_output_artifact_uses_only_direct_artifact_metadata(self):
        result = build_source_node(
            {
                "lifecycle": "deprecated",
                "governed_by": ["key.standard.artifact"],
                "_source_authority": {"owner": "repository"},
            },
            "key.code.feature",
            NodeKind.OUTPUT_ARTIFACT,
            ArtifactKind.CODE,
            Locator("src/feature.py", symbol="run"),
            "code_anchor",
            self.parent,
            "00_docs/standard.md",
        )

        self.assertEqual((), result.diagnostics)
        self.assertEqual("deprecated", result.node.lifecycle.value)
        self.assertEqual(("key.standard.artifact",), result.node.provenance.governed_by)
        self.assertEqual((("owner", "repository"),), result.node.source_authority)


if __name__ == "__main__":
    unittest.main()
