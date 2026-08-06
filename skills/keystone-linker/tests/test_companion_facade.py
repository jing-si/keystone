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


if __name__ == "__main__":
    unittest.main()
