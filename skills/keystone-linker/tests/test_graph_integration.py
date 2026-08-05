import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[3]
RUNNER = Path(__file__).parents[1] / "scripts" / "run_graph_validation.py"
INSTALLER = ROOT / "reinstall-local-keystone-skills.sh"


class GraphValidationIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        (self.root / "source.md").write_text(
            "---\nkey: {id: key.doc, kind: source_document, documents: key.missing}\n---\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.directory.cleanup()

    def run_runner(self, *arguments):
        process = subprocess.run(
            [sys.executable, str(RUNNER), "--root", str(self.root), "--source", "source.md", *arguments],
            capture_output=True, text=True, check=False,
        )
        return process, json.loads(process.stdout) if process.stdout else None

    def test_runner_maps_missing_timeout_and_malformed_validator_fail_closed(self):
        missing, missing_payload = self.run_runner("--validator", str(self.root / "missing.py"))
        self.assertEqual(2, missing.returncode)
        self.assertEqual("validator_unavailable", missing_payload["diagnostics"][0]["code"])

        slow = self.root / "slow.py"
        slow.write_text("import time; time.sleep(2)\n", encoding="utf-8")
        timeout, timeout_payload = self.run_runner("--validator", str(slow), "--timeout-seconds", "0.01")
        self.assertEqual(2, timeout.returncode)
        self.assertEqual("validator_timeout", timeout_payload["diagnostics"][0]["code"])

        malformed = self.root / "malformed.py"
        malformed.write_text("print('not-json')\n", encoding="utf-8")
        bad, bad_payload = self.run_runner("--validator", str(malformed))
        self.assertEqual(2, bad.returncode)
        self.assertEqual("validator_output_malformed", bad_payload["diagnostics"][0]["code"])

    def test_extension_is_additive_and_cannot_suppress_core_diagnostics(self):
        extension = self.root / "extension.py"
        extension.write_text(
            "import json\nprint(json.dumps({'schema_version': 1, 'status': 'pass', "
            "'diagnostics': [], 'summary': {'errors': 0, 'warnings': 0}}))\n",
            encoding="utf-8",
        )
        process, payload = self.run_runner("--extension", str(extension))

        self.assertEqual(1, process.returncode)
        self.assertIn("missing_target", [item["code"] for item in payload["diagnostics"]])

    def test_installer_copies_graph_runtime_and_runs_help_smoke(self):
        codex_home = self.root / "codex-home"
        environment = dict(os.environ, CODEX_HOME=str(codex_home))
        process = subprocess.run(
            ["bash", str(INSTALLER)], cwd=str(ROOT), env=environment,
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        installed = codex_home / "skills" / "keystone-linker"
        for relative in ("scripts/validate_graph.py", "scripts/run_graph_validation.py",
                         "scripts/check_graph_hook.sh", "scripts/graph_runtime/validator.py",
                         "references/graph-runtime.md", "tests/test_validate_graph.py"):
            self.assertTrue((installed / relative).is_file(), relative)


if __name__ == "__main__":
    unittest.main()
