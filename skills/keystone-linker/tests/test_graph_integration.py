import json
import hashlib
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
            "---\nkey: {id: key.doc, kind: source_document}\n---\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.directory.cleanup()

    def run_runner(self, *arguments):
        process = subprocess.run(
            [sys.executable, str(RUNNER), "--root", str(self.root),
             "--source", "source.md", *arguments],
            capture_output=True, text=True, check=False,
        )
        return process, json.loads(process.stdout) if process.stdout else None

    def test_runner_maps_missing_timeout_and_malformed_validator_to_error(self):
        missing, payload = self.run_runner("--validator", str(self.root / "missing.py"))
        self.assertEqual(2, missing.returncode)
        self.assertEqual("validator_unavailable", payload["diagnostics"][0]["code"])

        slow = self.root / "slow.py"
        slow.write_text("import time; time.sleep(2)\n", encoding="utf-8")
        timeout, payload = self.run_runner(
            "--validator", str(slow), "--timeout-seconds", "0.01"
        )
        self.assertEqual(2, timeout.returncode)
        self.assertEqual("validator_timeout", payload["diagnostics"][0]["code"])

        malformed = self.root / "malformed.py"
        malformed.write_text("print('not-json')\n", encoding="utf-8")
        invalid, payload = self.run_runner("--validator", str(malformed))
        self.assertEqual(2, invalid.returncode)
        self.assertEqual("validator_output_malformed", payload["diagnostics"][0]["code"])

    def test_extension_is_additive(self):
        extension = self.root / "extension.py"
        extension.write_text(
            "import json\nprint(json.dumps({'schema_version':1,'status':'fail',"
            "'diagnostics':[{'code':'extension_finding','message':'found','severity':'error'}],"
            "'summary':{'errors':1,'warnings':0}}))\nraise SystemExit(1)\n",
            encoding="utf-8",
        )
        process, payload = self.run_runner("--extension", str(extension))
        self.assertEqual(1, process.returncode)
        self.assertIn("extension_finding", {item["code"] for item in payload["diagnostics"]})

    def test_schema2_without_external_material_is_historical_structure_only(self):
        manifest = self.root / "historical.json"
        manifest.write_bytes(json.dumps({
            "application_evidence": {
                "digest": "sha256:" + "0" * 64,
                "path": "retired-application-evidence.json",
            },
            "schema_version": 2,
            "sources": ["source.md"],
            "transaction": {},
        }, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        process, payload = self.run_runner("--manifest", str(manifest))
        self.assertNotEqual(2, process.returncode, payload)
        self.assertIn("historical_structure_only", {
            item["code"] for item in payload["diagnostics"]
        })

    def test_schema2_with_legacy_keys_but_retired_producer_stays_structural(self):
        manifest = self.root / "historical-with-key.json"
        manifest.write_bytes(json.dumps({
            "application_evidence": {
                "digest": "sha256:" + "0" * 64,
                "path": "retired-application-evidence.json",
            },
            "schema_version": 2,
            "sources": ["source.md"],
            "transaction": {},
        }, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        evidence = self.root / "historical-evidence"
        evidence.mkdir()
        key = self.root / "historical-author.key"
        key.write_bytes(b"historical-key-material-that-is-long-enough")
        digest = "sha256:" + hashlib.sha256(key.read_bytes()).hexdigest()
        process, payload = self.run_runner(
            "--manifest", str(manifest),
            "--evidence-root", str(evidence),
            "--owner-key", "author=" + str(key),
            "--owner-key-sha256", "author=" + digest,
        )
        self.assertNotEqual(2, process.returncode, payload)
        self.assertIn("historical_structure_only", {
            item["code"] for item in payload["diagnostics"]
        })

    def test_schema1_rejects_historical_authority_options(self):
        manifest = self.root / "current.json"
        manifest.write_text(json.dumps({
            "schema_version": 1, "sources": ["source.md"],
        }), encoding="utf-8")
        process, payload = self.run_runner(
            "--manifest", str(manifest), "--evidence-root", str(self.root / "evidence")
        )
        self.assertEqual(2, process.returncode)
        self.assertEqual("application_evidence_context_unexpected", payload["diagnostics"][0]["code"])

    def test_installer_copies_current_runtime_and_omits_retired_producers(self):
        with tempfile.TemporaryDirectory() as temporary:
            environment = dict(os.environ, CODEX_HOME=temporary)
            process = subprocess.run(
                ["bash", str(INSTALLER)], cwd=str(ROOT), env=environment,
                capture_output=True, text=True, check=False,
            )
            installed = Path(temporary) / "skills"
            self.assertEqual(0, process.returncode, process.stderr)
            self.assertTrue((installed / "keystone-linker/scripts/validate_graph.py").is_file())
            self.assertFalse((installed / "keystone-author/scripts/run_owned_surface_apply.py").exists())
            self.assertFalse((installed / "keystone-coordinator/scripts/capture_assignment_snapshot.py").exists())


if __name__ == "__main__":
    unittest.main()
