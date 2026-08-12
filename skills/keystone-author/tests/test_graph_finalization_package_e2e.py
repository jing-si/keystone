import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[3]
INSTALLER = ROOT / "reinstall-local-keystone-skills.sh"


class LeanPackageE2E(unittest.TestCase):
    def test_temporary_install_contains_current_packages_and_historical_readers(self):
        with tempfile.TemporaryDirectory() as temporary:
            process = subprocess.run(
                ["bash", str(INSTALLER)], cwd=str(ROOT),
                env=dict(os.environ, CODEX_HOME=temporary),
                capture_output=True, text=True, check=False,
            )
            skills = Path(temporary) / "skills"
            self.assertEqual(0, process.returncode, process.stderr)
            self.assertTrue((skills / "keystone-author/scripts/validate_finalization.py").is_file())
            self.assertTrue((skills / "keystone-linker/scripts/validate_graph.py").is_file())
            self.assertTrue((skills / "keystone-coordinator/scripts/validate_closure.py").is_file())
            self.assertTrue((skills / "keystone-coordinator/scripts/closure_v3.py").is_file())
            self.assertFalse((skills / "keystone-author/scripts/run_owned_surface_apply.py").exists())
            self.assertFalse((skills / "keystone-coordinator/scripts/record_acceptance_event.py").exists())

    def test_installed_current_closure_runs_without_external_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            process = subprocess.run(
                ["bash", str(INSTALLER)], cwd=str(ROOT),
                env=dict(os.environ, CODEX_HOME=temporary),
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(0, process.returncode, process.stderr)
            manifest = Path(temporary) / "closure.json"
            manifest.write_text(json.dumps({
                "schema_version": 1,
                "execution_mode": "direct_execution",
                "closure_phase": "pre_acceptance",
                "worker_report": {
                    "status": "DONE",
                    "changed_files": ["src/example.py"],
                    "scope_check": "within_scope",
                    "forbidden_change_check": "none",
                    "verification": {"status": "pass", "evidence": ["unit tests passed"]},
                },
                "keystone_closure": {},
                "coordinator_review": {"decision": "accept_candidate"},
            }), encoding="utf-8")
            runner = (
                Path(temporary) / "skills/keystone-coordinator/scripts/validate_closure.py"
            )
            result = subprocess.run(
                [sys.executable, str(runner), "--manifest", str(manifest)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr or result.stdout)
            self.assertEqual("pass", json.loads(result.stdout)["status"])


if __name__ == "__main__":
    unittest.main()
