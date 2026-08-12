import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_closure import validate_manifest  # noqa: E402


class HistoricalClosureV3Test(unittest.TestCase):
    def test_historical_v3_is_structural_only_without_keys_or_producers(self):
        manifest = {
            "schema_version": 3,
            "closure_stage": "post_acceptance",
            "closure_target": "step",
            "worker_report": {},
            "keystone_closure": {},
            "coordinator_review": {},
        }
        result = validate_manifest(manifest)
        self.assertEqual("pass", result["status"])
        self.assertEqual("historical_structure_only", result["diagnostics"][0]["code"])

    def test_historical_v3_cannot_become_current_authority(self):
        manifest = {
            "schema_version": 3,
            "closure_stage": "post_acceptance",
            "closure_target": "step",
            "worker_report": {},
            "keystone_closure": {},
            "coordinator_review": {"decision": "closure_complete"},
        }
        result = validate_manifest(manifest)
        self.assertEqual("pass", result["status"])
        self.assertEqual(1, result["summary"]["warnings"])


if __name__ == "__main__":
    unittest.main()
