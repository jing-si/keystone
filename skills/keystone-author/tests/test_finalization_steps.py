import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from finalization_steps import (  # noqa: E402
    validate_early_work,
    validate_steps_and_transitions,
)


class FinalizationStepCharacterizationTest(unittest.TestCase):
    def test_invalid_step_collections_keep_diagnostic_order(self):
        manifest = {
            "steps": "invalid",
            "active_steps": [],
            "active_step_sources": [],
            "accepted_steps": [],
            "execution_transitions": [],
            "approval_transitions": [],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            findings, steps = validate_steps_and_transitions(
                Path(temp_dir).resolve(), manifest, 3
            )

        self.assertEqual({}, steps)
        self.assertEqual(
            ["steps_invalid", "active_step_sources_missing", "accepted_steps_missing"],
            [item["code"] for item in findings],
        )

    def test_early_work_reports_gate_and_trace_failures_in_field_order(self):
        findings = validate_early_work([{
            "target_step": "R007/S99",
            "status_effect": "complete",
            "cause": "",
            "completed_scope": [],
            "remaining_scope": [],
        }], {"R007/S01": {}})

        self.assertEqual(
            [
                "early_work_target_unresolved",
                "early_work_status_effect_invalid",
                "early_work_trace_missing",
                "early_work_trace_missing",
                "early_work_trace_missing",
            ],
            [item["code"] for item in findings],
        )


if __name__ == "__main__":
    unittest.main()
