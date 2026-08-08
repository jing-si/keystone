import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[3]
RUNNER = Path(__file__).parents[1] / "scripts" / "run_graph_validation.py"
AUTHOR_RUNNER = (
    ROOT / "skills" / "keystone-author" / "scripts"
    / "run_owned_surface_apply.py"
)
INSTALLER = ROOT / "reinstall-local-keystone-skills.sh"
LINKER_SCRIPTS = Path(__file__).parents[1] / "scripts"
if str(LINKER_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(LINKER_SCRIPTS))

from graph_runtime.application_evidence import application_plan_digest  # noqa: E402
from graph_runtime.validator import reconstruct  # noqa: E402
from graph_runtime.wire import graph_snapshot_wire  # noqa: E402


def canonical_bytes(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def digest_bytes(value):
    return "sha256:" + hashlib.sha256(value).hexdigest()


def digest_json(value):
    return digest_bytes(canonical_bytes(value))


class GraphValidationIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.evidence_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.evidence = Path(self.evidence_directory.name).resolve()
        (self.root / "source.md").write_text(
            "---\nkey: {id: key.doc, kind: source_document, documents: key.missing}\n---\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.evidence_directory.cleanup()
        self.directory.cleanup()

    def run_runner(self, *arguments):
        process = subprocess.run(
            [sys.executable, str(RUNNER), "--root", str(self.root), "--source", "source.md", *arguments],
            capture_output=True, text=True, check=False,
        )
        return process, json.loads(process.stdout) if process.stdout else None

    def authority_manifest(self):
        manifest = self.root / "authority-manifest.json"
        manifest.write_bytes(json.dumps(
            {
                "schema_version": 2,
                "sources": [],
                "transaction": {},
                "application_evidence": {
                    "path": "application.json",
                    "digest": "sha256:" + "0" * 64,
                },
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8"))
        return manifest

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

    def test_runner_rejects_duplicate_unknown_and_boolean_envelopes(self):
        outputs = {
            "duplicate": (
                '{"schema_version":1,"status":"fail","status":"pass",'
                '"diagnostics":[],"summary":{"errors":0,"warnings":0}}'
            ),
            "nested-duplicate": (
                '{"schema_version":1,"status":"pass","diagnostics":[],'
                '"summary":{"errors":1,"errors":0,"warnings":0}}'
            ),
            "unknown": (
                '{"schema_version":1,"status":"pass","diagnostics":[],'
                '"summary":{"errors":0,"warnings":0},"forged":true}'
            ),
            "boolean-schema": (
                '{"schema_version":true,"status":"pass","diagnostics":[],'
                '"summary":{"errors":0,"warnings":0}}'
            ),
        }
        for name, output in outputs.items():
            with self.subTest(name=name):
                validator = self.root / (name + ".py")
                validator.write_text(
                    "print(%r)\n" % output, encoding="utf-8"
                )
                process, payload = self.run_runner(
                    "--validator", str(validator)
                )
                self.assertEqual(2, process.returncode)
                self.assertEqual(
                    "validator_output_malformed",
                    payload["diagnostics"][0]["code"],
                )
                self.assertEqual(
                    {"schema_version", "status", "diagnostics", "summary"},
                    set(payload),
                )

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
        self.assertEqual(
            {"schema_version", "status", "diagnostics", "summary"},
            set(payload),
        )

    def test_runner_preserves_repository_coverage_evidence(self):
        manifest = self.root / "manifest.json"
        manifest.write_text(json.dumps({
            "schema_version": 1,
            "scope": "repository",
            "coverage": "subset",
            "sources": [],
        }), encoding="utf-8")

        process = subprocess.run(
            [sys.executable, str(RUNNER), "--root", str(self.root),
             "--manifest", str(manifest)],
            capture_output=True, text=True, check=False,
        )
        payload = json.loads(process.stdout)

        self.assertIn(process.returncode, {0, 1}, payload)
        self.assertEqual("subset", payload["coverage"]["mode"])
        self.assertFalse(payload["coverage"]["complete"])
        self.assertEqual(["source.md"], payload["coverage"]["omitted_sources"])

    def test_schema1_rejects_application_authority_options(self):
        manifest = self.root / "legacy.json"
        manifest.write_text(json.dumps({
            "schema_version": 1, "sources": ["source.md"],
        }), encoding="utf-8")

        process = subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--root", str(self.root),
                "--manifest", str(manifest),
                "--evidence-root", str(self.evidence),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(process.stdout)

        self.assertEqual(2, process.returncode)
        self.assertEqual(
            "application_evidence_context_unexpected",
            payload["diagnostics"][0]["code"],
        )

    def test_schema2_manifest_requires_canonical_raw_json(self):
        manifest = self.root / "noncanonical-authority.json"
        manifest.write_text(json.dumps({
            "schema_version": 2,
            "sources": [],
            "transaction": {},
            "application_evidence": {
                "path": "application.json",
                "digest": "sha256:" + "0" * 64,
            },
        }), encoding="utf-8")

        process = subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--root", str(self.root),
                "--manifest", str(manifest),
                "--evidence-root", str(self.evidence),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(process.stdout)

        self.assertEqual(2, process.returncode)
        self.assertEqual(
            "manifest_noncanonical", payload["diagnostics"][0]["code"]
        )

    def test_application_authority_forbids_validator_and_extension_substitution(self):
        manifest = self.authority_manifest()
        substituted = self.root / "substituted.py"
        substituted.write_text("print('{}')\n", encoding="utf-8")
        extension = self.root / "extension.py"
        extension.write_text("print('{}')\n", encoding="utf-8")

        for flag, candidate in (
            ("--validator", substituted),
            ("--extension", extension),
        ):
            with self.subTest(flag=flag):
                process = subprocess.run(
                    [
                        sys.executable,
                        str(RUNNER),
                        "--root", str(self.root),
                        "--manifest", str(manifest),
                        "--evidence-root", str(self.evidence),
                        flag, str(candidate),
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                payload = json.loads(process.stdout)
                self.assertEqual(2, process.returncode)
                self.assertEqual(
                    "authority_validator_override_forbidden",
                    payload["diagnostics"][0]["code"],
                )

    def test_authority_core_ignores_hostile_python_import_environment(self):
        manifest = self.authority_manifest()
        hostile = self.root / "hostile-imports"
        hostile.mkdir()
        marker = self.root / "sitecustomize-loaded"
        (hostile / "sitecustomize.py").write_text(
            "from pathlib import Path\n"
            "Path(%r).write_text('loaded', encoding='utf-8')\n"
            % str(marker),
            encoding="utf-8",
        )
        environment = dict(os.environ, PYTHONPATH=str(hostile))

        process = subprocess.run(
            [
                sys.executable,
                "-S",
                str(RUNNER),
                "--root", str(self.root),
                "--manifest", str(manifest),
                "--evidence-root", str(self.evidence),
            ],
            capture_output=True,
            text=True,
            check=False,
            env=environment,
        )

        self.assertIn(process.returncode, {1, 2}, process.stdout)
        self.assertFalse(marker.exists())

    def test_authority_receipt_rejects_forged_relation_before_snapshot(self):
        source_path = self.root / "graph.md"
        source_bytes = b"# Graph\n"
        source_path.write_bytes(source_bytes)
        source_digest = digest_bytes(source_bytes)

        def companion(relation_lifecycle):
            locator = {"path": "graph.md"}
            node_provenance = {
                "produced_from": [],
                "governed_by": [],
            }
            relation_provenance = {
                "surface": "companion_metadata",
                "locator": locator,
                "attested_by": None,
            }
            return {
                "schema_version": 1,
                "source": {
                    "path": "graph.md",
                    "surface": "companion_metadata",
                    "baseline_digest": source_digest,
                },
                "nodes": [
                    {
                        "id": "key.code.example",
                        "kind": "output_artifact",
                        "artifact_kind": "code",
                        "locator": locator,
                        "lifecycle": "active",
                        "provenance": node_provenance,
                    },
                    {
                        "id": "key.capability.example",
                        "kind": "capability",
                        "artifact_kind": "none",
                        "locator": locator,
                        "lifecycle": "active",
                        "provenance": node_provenance,
                    },
                ],
                "relations": [{
                    "source": "key.code.example",
                    "relation": "uses",
                    "target": "key.capability.example",
                    "evidence": "declared",
                    "provenance": relation_provenance,
                    "lifecycle": relation_lifecycle,
                }],
            }

        baseline_bytes = canonical_bytes(companion("active"))
        after_bytes = canonical_bytes(companion("archived"))
        companion_path = self.root / "graph.md.keystone.json"
        companion_path.write_bytes(baseline_bytes)
        baseline_snapshot, baseline_findings = reconstruct(
            self.root, ["graph.md"]
        )
        result_snapshot, result_findings = reconstruct(
            self.root,
            ["graph.md"],
            {
                "graph.md": source_bytes,
                "graph.md.keystone.json": after_bytes,
            },
        )
        self.assertEqual((), baseline_findings)
        self.assertEqual((), result_findings)
        forged_baseline = graph_snapshot_wire(
            baseline_snapshot, schema_version=2
        )
        forged_baseline = copy.deepcopy(forged_baseline)
        forged_baseline["relations"][0]["lifecycle"] = "removed"
        result_wire = graph_snapshot_wire(result_snapshot, schema_version=2)
        patch = {
            "patch_id": "patch-forged-relation",
            "owner": "author",
            "surface": "companion_metadata",
            "target_path": "graph.md.keystone.json",
            "baseline_digest": digest_bytes(baseline_bytes),
            "baseline_content": baseline_bytes.decode("utf-8"),
            "exact_patch": after_bytes.decode("utf-8"),
            "patch_format": "full_replacement",
            "patch_body": after_bytes.decode("utf-8"),
            "expected_after_digest": digest_bytes(after_bytes),
            "required": True,
        }
        transaction = {
            "schema_version": 2,
            "transaction_id": "tx-forged-relation-before",
            "scope_ref": "R010/S03",
            "input_deltas": [{
                "kind": "document_delta",
                "source_surface": "graph.md.keystone.json",
                "changed_locators": [{"path": "graph.md"}],
                "semantic_summary": "Archive the declared graph relation.",
                "baseline_digest": patch["baseline_digest"],
                "graph_relevant": True,
            }],
            "canonical_mutations": [{
                "operation": "update",
                "entity": "relation",
                "before": forged_baseline["relations"][0],
                "after": result_wire["relations"][0],
                "evidence": "declared",
                "direct_relation_reason": None,
            }],
            "surface_patches": [patch],
            "attestations": [{
                "patch_id": patch["patch_id"],
                "owner": "author",
                "decision": "confirm",
                "evidence": "Author confirmed the exact companion patch.",
            }],
            "apply_results": [{
                "patch_id": patch["patch_id"],
                "result": "applied",
                "resulting_digest": patch["expected_after_digest"],
                "evidence": "Authenticated owner apply receipt.",
            }],
            "state": "verified",
            "conflict_reason": None,
            "failure_reason": None,
            "reconstruction": {
                "baseline": forged_baseline,
                "result": result_wire,
            },
            "mechanical_validation": {
                "schema_version": 1,
                "status": "pass",
                "diagnostics": [],
                "summary": {"errors": 0, "warnings": 0},
            },
            "coverage_debt": [],
        }
        key = Path(self.directory.name).resolve().parent / (
            Path(self.directory.name).name + "-author.key"
        )
        key.write_bytes(b"author-forged-relation-test-key-material")
        key.chmod(0o600)
        self.addCleanup(key.unlink, missing_ok=True)
        key_digest = digest_bytes(key.read_bytes())
        scope = {"allowed": ["graph.md.keystone.json"], "excluded": []}
        request = {
            "schema_version": 1,
            "transaction_id": transaction["transaction_id"],
            "transaction_digest": application_plan_digest(transaction),
            "assignment_id": "assignment-forged-relation",
            "assignment_digest": digest_bytes(b"assignment-forged-relation"),
            "phase_id": "pre_acceptance_closure",
            "phase_baseline_snapshot_digest": digest_bytes(b"phase-baseline"),
            "phase_parent_evidence_digest": digest_bytes(b"phase-parent"),
            "repository_root_digest": digest_json({
                "repository_root": str(self.root.resolve(strict=True)),
            }),
            "owner": "author",
            "scope": scope,
            "scope_digest": digest_json(scope),
            "prior_receipt_digest": "absent",
            "patch": patch,
        }
        request_path = self.evidence / "request.json"
        request_path.write_bytes(canonical_bytes(request))
        receipt_path = self.evidence / "receipts" / "author.json"
        receipt_path.parent.mkdir()
        apply_process = subprocess.run(
            [
                sys.executable,
                str(AUTHOR_RUNNER),
                "--root", str(self.root),
                "--request", str(request_path),
                "--evidence-root", str(self.evidence),
                "--output", str(receipt_path),
                "--authority-key", str(key),
                "--pinned-key-sha256", key_digest,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            0, apply_process.returncode,
            apply_process.stdout + apply_process.stderr,
        )
        aggregate = {
            "schema_version": 1,
            "transaction_id": transaction["transaction_id"],
            "transaction_digest": application_plan_digest(transaction),
            "repository_root_digest": request["repository_root_digest"],
            "assignment_id": request["assignment_id"],
            "assignment_digest": request["assignment_digest"],
            "receipts": [{
                "path": "receipts/author.json",
                "digest": digest_bytes(receipt_path.read_bytes()),
            }],
        }
        aggregate_path = self.evidence / "application.json"
        aggregate_path.write_bytes(canonical_bytes(aggregate))
        manifest = {
            "schema_version": 2,
            "sources": ["graph.md"],
            "transaction": transaction,
            "application_evidence": {
                "path": aggregate_path.name,
                "digest": digest_bytes(aggregate_path.read_bytes()),
            },
        }
        manifest_path = self.evidence / "manifest.json"
        manifest_path.write_bytes(canonical_bytes(manifest))

        process = subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--root", str(self.root),
                "--manifest", str(manifest_path),
                "--evidence-root", str(self.evidence),
                "--owner-key", "author=%s" % key,
                "--owner-key-sha256", "author=%s" % key_digest,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(process.stdout)

        self.assertEqual(1, process.returncode, payload)
        codes = {item["code"] for item in payload["diagnostics"]}
        self.assertIn("verified_baseline_snapshot_mismatch", codes)
        self.assertIn("mutation_baseline_context_mismatch", codes)

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
