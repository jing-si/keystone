import unittest

from graph_runtime.model import (
    ArtifactKind,
    Evidence,
    Lifecycle,
    Locator,
    Node,
    NodeKind,
    Provenance,
    RelationType,
)
from graph_runtime.source_relations import build_source_relations


class SourceRelationsTest(unittest.TestCase):
    def test_declared_dependency_builds_gate_after_conflict_diagnostic(self):
        locator = Locator("00_docs/work.md")
        node = Node(
            "key.work.current",
            NodeKind.WORK_ORDER,
            ArtifactKind.NONE,
            locator,
            Lifecycle.ACTIVE,
            Provenance(surface="document_metadata", locator=locator),
        )
        data = {
            "depends_on": ["key.work.dependency"],
            "_relation_conflicts": ("depends_on",),
            "_work_gates": [{
                "dependency": "key.work.dependency",
                "applies_to": {"steps": ["S02"]},
                "condition": {
                    "work_status": "complete",
                    "approval_state": "accepted",
                },
            }],
        }

        result = build_source_relations(
            data,
            node,
            "document",
            "document_metadata",
            locator.path,
            locator,
        )

        self.assertEqual(
            ["structured_legacy_relation_conflict"],
            [item.code for item in result.diagnostics],
        )
        self.assertEqual("key.work.dependency", result.work_gates[0].dependency)
        self.assertEqual(RelationType.DEPENDS_ON, result.relations[0].relation)

    def test_output_produced_from_builds_inferred_relation(self):
        locator = Locator("src/example.py", symbol="Example")
        node = Node(
            "key.code.example",
            NodeKind.OUTPUT_ARTIFACT,
            ArtifactKind.CODE,
            locator,
            Lifecycle.ACTIVE,
            Provenance(
                produced_from=("key.claim.example",),
                surface="code_anchor",
                locator=locator,
            ),
        )

        result = build_source_relations(
            {}, node, None, "code_anchor", locator.path, locator
        )

        self.assertEqual(1, len(result.relations))
        relation = result.relations[0]
        self.assertEqual("key.claim.example", relation.source)
        self.assertEqual(RelationType.PRODUCES, relation.relation)
        self.assertEqual(Evidence.INFERRED, relation.evidence)


if __name__ == "__main__":
    unittest.main()
