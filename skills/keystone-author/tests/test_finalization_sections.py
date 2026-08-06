import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from finalization_sections import (  # noqa: E402
    validate_finalization_closure,
    validate_impact_candidates,
    validate_namespace_entries,
)


class FinalizationSectionCharacterizationTest(unittest.TestCase):
    def finalization_manifest(self, root, schema_version=3):
        (root / "progress.md").write_text(
            "finalization:\n"
            "  state: complete\n"
            "  acceptance_ref: R007/S02/main-acceptance\n",
            encoding="utf-8",
        )
        return {
            "schema_version": schema_version,
            "acceptance_ref": "R007/S02/main-acceptance",
            "finalization": {
                "required": True,
                "state": "complete",
                "evidence": [
                    "main_acceptance",
                    "impact_dispositions",
                    "source_updates",
                    "semantic_review",
                    "post_edit_verification",
                ],
                "progress_path": "progress.md",
            },
            "graph_sync": {
                "disposition": "not_applicable",
                "required": False,
                "reason": "No graph-relevant delta.",
            },
        }

    def test_schema_v3_complete_closure_accepts_not_applicable_graph_sync(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            manifest = self.finalization_manifest(root)

            self.assertEqual([], validate_finalization_closure(root, manifest, 3))

    def test_legacy_complete_diagnostic_is_preserved(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            manifest = self.finalization_manifest(root, schema_version=2)

            findings = validate_finalization_closure(root, manifest, 2)

        self.assertEqual(
            ["legacy_schema_complete_forbidden"],
            [item["code"] for item in findings],
        )

    def test_impact_diagnostics_keep_candidate_findings_before_coverage_findings(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            (root / "live.md").write_text(
                "Current step: R007/S02\n", encoding="utf-8"
            )
            findings = validate_impact_candidates(root, [{
                "category": "progress",
                "disposition": "no_change",
                "reason": "checked",
                "path": "live.md",
            }], 3)

        self.assertEqual("singular_current_step_claim", findings[0]["code"])
        self.assertTrue(all(
            item["code"] == "impact_category_missing" for item in findings[1:]
        ))

    def test_namespace_collision_sorts_owner_names(self):
        findings = validate_namespace_entries([
            {"namespace": "flyway", "value": "V12", "owner": "R010"},
            {"namespace": "flyway", "value": "V12", "owner": "R008"},
        ])

        self.assertEqual(["namespace_collision"], [item["code"] for item in findings])
        self.assertIn("R008, R010", findings[0]["message"])


if __name__ == "__main__":
    unittest.main()
