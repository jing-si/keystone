import json
import unittest

from graph_runtime.companion import parse_companion
from graph_runtime.metadata import parse_companion as metadata_parse_companion


class CompanionFacadeTest(unittest.TestCase):
    def test_metadata_module_reexports_companion_parser(self):
        self.assertIs(parse_companion, metadata_parse_companion)

    def test_direct_companion_parser_accepts_empty_absent_source(self):
        payload = {
            "schema_version": 1,
            "source": {
                "path": "asset.bin",
                "surface": "companion_metadata",
                "baseline_digest": "absent",
            },
            "nodes": [],
            "relations": [],
        }

        result = parse_companion(
            json.dumps(payload),
            "asset.bin.keystone.json",
            "asset.bin",
            source_exists=False,
        )

        self.assertEqual((), result.diagnostics)
        self.assertEqual("absent", result.baseline_digest)
        self.assertEqual((), result.snapshot.nodes)

    def test_companion_uses_shared_node_and_relation_lifecycle_domains(self):
        payload = {
            "schema_version": 1,
            "source": {
                "path": "asset.bin",
                "surface": "companion_metadata",
                "baseline_digest": "absent",
            },
            "nodes": [{
                "id": "key.claim.old",
                "kind": "claim",
                "artifact_kind": "none",
                "locator": {"path": "asset.bin"},
                "lifecycle": "deprecated",
                "provenance": {"produced_from": [], "governed_by": []},
            }],
            "relations": [{
                "source": "key.claim.old",
                "relation": "depends_on",
                "target": "key.claim.other",
                "evidence": "declared",
                "provenance": {
                    "surface": "companion_metadata",
                    "locator": {"path": "asset.bin"},
                    "attested_by": None,
                },
                "lifecycle": "draft",
            }],
        }

        result = parse_companion(
            json.dumps(payload),
            "asset.bin.keystone.json",
            "asset.bin",
            source_exists=False,
        )

        self.assertEqual(
            {"node_lifecycle_domain_invalid", "relation_lifecycle_domain_invalid"},
            {item.code for item in result.diagnostics},
        )

    def test_companion_rejects_recursive_duplicate_json_keys(self):
        result = parse_companion(
            '{"schema_version":1,"source":{"path":"asset.bin",'
            '"path":"forged.bin","surface":"companion_metadata",'
            '"baseline_digest":"absent"},"nodes":[],"relations":[]}',
            "asset.bin.keystone.json",
            "asset.bin",
            source_exists=False,
        )

        self.assertEqual((), result.snapshot.nodes)
        self.assertEqual("malformed_companion", result.diagnostics[0].code)
        self.assertIn("duplicate JSON key", result.diagnostics[0].message)


if __name__ == "__main__":
    unittest.main()
