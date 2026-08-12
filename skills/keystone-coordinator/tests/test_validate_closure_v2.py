import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_closure import validate_manifest  # noqa: E402


class HistoricalClosureV2Test(unittest.TestCase):
    def test_historical_v2_is_structural_only_without_external_material(self):
        manifest = {
            "schema_version": 2,
            "closure_phase": "pre_acceptance",
            "closure_target": "step",
            "worker_report": {},
            "keystone_closure": {},
            "coordinator_review": {},
        }
        result = validate_manifest(manifest)
        self.assertEqual("pass", result["status"])
        self.assertEqual(1, result["summary"]["warnings"])
        self.assertEqual("historical_structure_only", result["diagnostics"][0]["code"])

    def test_historical_v2_reports_missing_structure(self):
        result = validate_manifest({"schema_version": 2})
        self.assertEqual("fail", result["status"])
        self.assertIn("historical_field_missing", {item["code"] for item in result["diagnostics"]})


if __name__ == "__main__":
    unittest.main()
