import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[2]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LeanCoreIntegrationTest(unittest.TestCase):
    def test_retired_current_producers_are_absent(self):
        for relative in (
            "scripts/generate_owned_surface_apply_runtimes.py",
            "scripts/owned_surface_apply_runtime.py",
            "scripts/validate_agent_evals.py",
            "scripts/agent_eval_scenarios.json",
            "skills/keystone-author/scripts/run_owned_surface_apply.py",
            "skills/keystone-coordinator/scripts/run_owned_surface_apply.py",
            "skills/keystone-coordinator/scripts/capture_assignment_snapshot.py",
            "skills/keystone-coordinator/scripts/record_acceptance_event.py",
        ):
            self.assertFalse((ROOT / relative).exists(), relative)

    def test_release_plan_has_only_canonical_lean_stages(self):
        release = load_module("lean_release_gate", ROOT / "scripts/run_release_gate.py")
        identifiers = [step.identifier for step in release.build_plan(ROOT)]
        self.assertEqual("release_preflight", identifiers[0])
        self.assertEqual("release_postflight", identifiers[-1])
        self.assertIn("installer_staging_parity_rollback", identifiers)
        self.assertNotIn("agent_behavior_evidence", identifiers)
        self.assertNotIn("current_finalization", identifiers)
        self.assertNotIn("historical_finalization", identifiers)

    def test_package_contracts_name_current_source_authority(self):
        author = (ROOT / "skills/keystone-author/SKILL.md").read_text(encoding="utf-8")
        coordinator = (ROOT / "skills/keystone-coordinator/SKILL.md").read_text(encoding="utf-8")
        linker = (ROOT / "skills/keystone-linker/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("does not require a new finalization manifest", author)
        self.assertIn("Current closure does not require", coordinator)
        self.assertIn("current graph success requires no HMAC receipt", linker)

    def test_package_contracts_preserve_two_level_round_authority(self):
        reader = (ROOT / "skills/keystone-reader/SKILL.md").read_text(
            encoding="utf-8"
        )
        author = (ROOT / "skills/keystone-author/SKILL.md").read_text(
            encoding="utf-8"
        )
        coordinator = (ROOT / "skills/keystone-coordinator/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("round_hierarchy", reader)
        self.assertIn("active_child_rounds", reader)
        self.assertIn("R010-a-a", author)
        self.assertIn("work_order_restructure", author)
        self.assertIn("work_order_restructure", coordinator)
        self.assertIn("Parent/child recovery", coordinator)


if __name__ == "__main__":
    unittest.main()
