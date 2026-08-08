import json
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from graph_runtime.model import Evidence, RelationType
from graph_runtime.scanner import ReferenceScanner, ScanScope
from graph_runtime.validator import reconstruct
from validate_graph import (
    application_baseline_sources,
    capture_sources,
    coverage_severity,
    generation_findings,
)


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_graph.py"
RUNNER = Path(__file__).parents[1] / "scripts" / "run_graph_validation.py"


class GraphValidatorCliTest(unittest.TestCase):
    def test_authenticated_receipts_restore_physical_preapplication_sources(self):
        captured = {
            "graph.bin": b"opaque-source",
            "graph.bin.keystone.json": b"after-companion",
            "added.md": b"after-added-source",
        }
        evidence = SimpleNamespace(receipts=(
            SimpleNamespace(envelope={
                "receipt": {"patch_receipt": {"patch": {
                    "target_path": "graph.bin.keystone.json",
                    "baseline_digest": "sha256:" + hashlib.sha256(
                        b"before-companion"
                    ).hexdigest(),
                    "baseline_content": "before-companion",
                }}},
            }),
            SimpleNamespace(envelope={
                "receipt": {"patch_receipt": {"patch": {
                    "target_path": "added.md",
                    "baseline_digest": "absent",
                    "baseline_content": None,
                }}},
            }),
        ))

        baseline = application_baseline_sources(captured, evidence)

        self.assertEqual(b"opaque-source", baseline["graph.bin"])
        self.assertEqual(
            b"before-companion", baseline["graph.bin.keystone.json"]
        )
        self.assertNotIn("added.md", baseline)

    def test_requirement_and_verification_evidence_directions_are_distinct(self):
        companion = {"schema_version": 1,
            "source": {"path": "graph.bin", "surface": "companion_metadata", "baseline_digest": "absent"},
            "nodes": [
                {"id": "key.acceptance", "kind": "claim", "artifact_kind": "none", "locator": {"path": "graph.bin"}},
                {"id": "key.claim", "kind": "claim", "artifact_kind": "none", "locator": {"path": "graph.bin"}},
                {"id": "key.test", "kind": "output_artifact", "artifact_kind": "test", "locator": {"path": "graph.bin"}},
            ],
            "relations": [
                {"source": "key.acceptance", "relation": "requires_verification_of", "target": "key.claim"},
                {"source": "key.test", "relation": "verifies", "target": "key.claim"},
                {"source": "key.test", "relation": "requires_verification_of", "target": "key.claim"},
                {"source": "key.acceptance", "relation": "verifies", "target": "key.claim"},
            ]}
        for node in companion["nodes"]:
            node["lifecycle"] = "active"
            node["provenance"] = {"produced_from": [], "governed_by": []}
        for relation in companion["relations"]:
            relation["evidence"] = "declared"
            relation["lifecycle"] = "active"
            relation["provenance"] = {"surface": "companion_metadata",
                                      "locator": {"path": "graph.bin"}, "attested_by": None}
        self.write("graph.bin.keystone.json", json.dumps(companion))
        _, payload = self.run_validator("--source", "graph.bin")

        self.assertEqual(2, [item["code"] for item in payload["diagnostics"]].count("invalid_relation_direction"))

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)

    def tearDown(self):
        self.directory.cleanup()

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def write_bytes(self, relative, value):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value)
        return path

    def run_validator(self, *arguments):
        process = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root), *arguments],
            capture_output=True, text=True, check=False,
        )
        return process, json.loads(process.stdout) if process.stdout else None

    def assert_code(self, payload, code):
        self.assertIn(code, [item["code"] for item in payload["diagnostics"]])

    def test_source_only_reconstruction_passes_without_cache(self):
        self.write("docs/graph.md", """---
key: {id: key.doc.graph, kind: source_document}
---
<!-- key: id=key.cap.graph kind=capability -->
## Graph
<!-- key: id=key.code.graph kind=output_artifact artifact_kind=code provides=key.cap.graph -->
- Runtime
""")
        process, payload = self.run_validator("--source", "docs/graph.md")

        self.assertEqual(0, process.returncode)
        self.assertEqual("pass", payload["status"])
        self.assertEqual(1, payload["schema_version"])
        self.assertEqual({"errors": 0, "warnings": 0}, payload["summary"])
        self.assertFalse((self.root / ".keystone" / "graph-cache.json").exists())

    def test_manifest_sources_are_deterministic_and_cache_is_never_required(self):
        self.write("a.md", "---\nkey: {id: key.a, kind: source_document}\n---\n")
        self.write("b.md", "---\nkey: {id: key.b, kind: source_document}\n---\n")
        manifest = self.write("manifest.json", json.dumps({"schema_version": 1, "sources": ["b.md", "a.md"]}))
        first, first_payload = self.run_validator("--manifest", str(manifest))
        (self.root / ".keystone").mkdir()
        self.write(".keystone/graph-cache.json", "{malformed")
        second, second_payload = self.run_validator("--manifest", str(manifest))

        self.assertEqual((0, first_payload), (second.returncode, second_payload))

    def test_authoritative_json_rejects_duplicates_and_boolean_schema_versions(self):
        self.write("source.md", "---\nkey: {id: key.doc, kind: source_document}\n---\n")
        duplicate = self.write(
            "duplicate.json",
            '{"schema_version":1,"sources":["source.md"],'
            '"transaction":{"schema_version":1,"schema_version":2}}',
        )
        duplicate_process, duplicate_payload = self.run_validator(
            "--manifest", str(duplicate)
        )
        bool_manifest = self.write(
            "bool-manifest.json", '{"schema_version":true,"sources":["source.md"]}'
        )
        bool_manifest_process, bool_manifest_payload = self.run_validator(
            "--manifest", str(bool_manifest)
        )
        bool_transaction = self.write(
            "bool-transaction.json",
            '{"schema_version":true,"transaction_id":"tx-bool",'
            '"scope_ref":"R010/S01","state":"proposed","input_deltas":[],'
            '"canonical_mutations":[],"surface_patches":[],"attestations":[],'
            '"apply_results":[]}',
        )
        bool_transaction_process, bool_transaction_payload = self.run_validator(
            "--source", "source.md", "--transaction", str(bool_transaction)
        )

        self.assertEqual(2, duplicate_process.returncode)
        self.assert_code(duplicate_payload, "manifest_invalid")
        self.assertEqual(2, bool_manifest_process.returncode)
        self.assert_code(bool_manifest_payload, "manifest_invalid")
        self.assertEqual(1, bool_transaction_process.returncode)
        self.assert_code(bool_transaction_payload, "transaction_schema_invalid")

    def test_duplicate_companion_relation_key_is_only_malformed_companion(self):
        self.write(
            "asset.bin.keystone.json",
            '{"schema_version":1,"source":{"path":"asset.bin",'
            '"surface":"companion_metadata","baseline_digest":"absent"},'
            '"nodes":[],"relations":[{"source":"key.a",'
            '"relation":"uses","relation":"invented","target":"key.b",'
            '"evidence":"declared","provenance":{"surface":'
            '"companion_metadata","locator":{"path":"asset.bin"},'
            '"attested_by":null},"lifecycle":"active"}]}',
        )

        process, payload = self.run_validator("--source", "asset.bin")

        self.assertEqual(1, process.returncode)
        codes = [item["code"] for item in payload["diagnostics"]]
        self.assertIn("malformed_companion", codes)
        self.assertNotIn("invalid_relation_vocabulary", codes)

    def test_repository_scope_auto_discovers_sources_and_reports_manifest_coverage(self):
        self.write("a.md", "---\nkey: {id: key.a, kind: source_document}\n---\n")
        self.write("src/app.py", "# keystone: id=key.app kind=output_artifact locator.symbol=run\ndef run():\n    pass\n")

        auto_process, auto = self.run_validator("--scope", "repository")
        subset_manifest = self.write("subset.json", json.dumps({
            "schema_version": 1, "scope": "repository", "coverage": "subset",
            "sources": ["a.md"],
        }))
        subset_process, subset = self.run_validator("--manifest", str(subset_manifest))
        full_manifest = self.write("full.json", json.dumps({
            "schema_version": 1, "scope": "repository", "coverage": "full",
            "sources": ["a.md"],
        }))
        full_process, full = self.run_validator("--manifest", str(full_manifest))

        self.assertEqual(0, auto_process.returncode, auto)
        self.assertEqual(0, subset_process.returncode, subset)
        self.assert_code(subset, "repository_coverage_debt")
        self.assertEqual("warning", next(item["severity"] for item in subset["diagnostics"]
                                         if item["code"] == "repository_coverage_debt"))
        self.assertEqual(1, full_process.returncode)
        self.assert_code(full, "repository_source_omitted")

    def test_binary_companion_reconstructs_from_raw_source_bytes(self):
        raw = b"\x00\xff\x80binary\x00"
        self.write_bytes("asset.bin", raw)
        companion = {
            "schema_version": 1,
            "source": {
                "path": "asset.bin",
                "surface": "companion_metadata",
                "baseline_digest": "sha256:" + hashlib.sha256(raw).hexdigest(),
            },
            "nodes": [],
            "relations": [],
        }
        self.write("asset.bin.keystone.json", json.dumps(companion))

        process, payload = self.run_validator("--source", "asset.bin")

        self.assertEqual(0, process.returncode, payload)

    def test_binary_companion_is_complete_in_full_repository_discovery(self):
        raw = b"\xff\x00model\x80"
        self.write_bytes("assets/model.bin", raw)
        self.write("assets/model.bin.keystone.json", json.dumps({
            "schema_version": 1,
            "source": {
                "path": "assets/model.bin",
                "surface": "companion_metadata",
                "baseline_digest": "sha256:" + hashlib.sha256(raw).hexdigest(),
            },
            "nodes": [],
            "relations": [],
        }))
        manifest = self.write("full.json", json.dumps({
            "schema_version": 1,
            "scope": "repository",
            "coverage": "full",
            "sources": ["assets/model.bin"],
        }))

        process, payload = self.run_validator("--manifest", str(manifest))

        self.assertEqual(0, process.returncode, payload)
        self.assertTrue(payload["coverage"]["complete"])
        self.assertEqual(
            ["assets/model.bin"], payload["coverage"]["parsed_sources"]
        )

    def test_companion_patch_target_maps_to_logical_validation_source(self):
        companion = {
            "schema_version": 1,
            "source": {
                "path": "asset.bin",
                "surface": "companion_metadata",
                "baseline_digest": "absent",
            },
            "nodes": [],
            "relations": [],
        }
        companion_path = self.write("asset.bin.keystone.json", json.dumps(companion))
        transaction = {
            "schema_version": 1,
            "transaction_id": "tx-companion",
            "scope_ref": "R008/S04",
            "state": "proposed",
            "input_deltas": [],
            "canonical_mutations": [],
            "surface_patches": [{
                "patch_id": "patch-companion",
                "owner": "main",
                "surface": "companion_metadata",
                "target_path": "asset.bin.keystone.json",
                "baseline_digest": "sha256:" + hashlib.sha256(companion_path.read_bytes()).hexdigest(),
                "exact_patch": "update companion metadata",
                "required": False,
            }],
            "attestations": [],
            "apply_results": [],
            "coverage_debt": [],
        }

        process, payload = self.run_validator(
            "--source", "asset.bin", "--transaction", str(self.write("tx.json", json.dumps(transaction)))
        )

        self.assertEqual(0, process.returncode, payload)
        self.assertNotIn("transaction_source_omission", [
            item["code"] for item in payload["diagnostics"]
        ])

    def test_full_repository_coverage_fails_for_skipped_and_declared_only_sources(self):
        self.write_bytes("large.md", b"x" * (5 * 1024 * 1024 + 1))
        manifest = self.write("full.json", json.dumps({
            "schema_version": 1,
            "scope": "repository",
            "coverage": "full",
            "sources": ["large.md", "ghost.md"],
        }))

        process, payload = self.run_validator("--manifest", str(manifest))

        self.assertEqual(1, process.returncode, payload)
        self.assert_code(payload, "source_too_large")
        self.assert_code(payload, "repository_declared_source_missing")
        self.assertFalse(payload["coverage"]["complete"])
        self.assertEqual(["large.md"], payload["coverage"]["skipped_sources"])
        self.assertEqual(["ghost.md"], payload["coverage"]["declared_only_sources"])

    def test_subset_repository_coverage_reports_explicit_omitted_and_skipped_sources(self):
        self.write("a.md", "---\nkey: {id: key.a, kind: source_document}\n---\n")
        self.write_bytes("large.md", b"x" * (5 * 1024 * 1024 + 1))
        manifest = self.write("subset.json", json.dumps({
            "schema_version": 1,
            "scope": "repository",
            "coverage": "subset",
            "sources": [],
        }))

        process, payload = self.run_validator("--manifest", str(manifest))

        self.assertEqual(0, process.returncode, payload)
        self.assertEqual(["a.md"], payload["coverage"]["omitted_sources"])
        self.assertEqual(["large.md"], payload["coverage"]["skipped_sources"])
        self.assertFalse(payload["coverage"]["complete"])

    def test_all_incomplete_discovery_reasons_are_coverage_sensitive(self):
        for code in ("scan_truncated", "source_too_large", "source_unreadable"):
            with self.subTest(code=code):
                self.assertEqual(
                    "error", coverage_severity(code, "full", None).value
                )
                self.assertEqual(
                    "warning", coverage_severity(code, "subset", None).value
                )

    def test_captured_generation_is_reconstructed_and_later_change_fails_closed(self):
        source = self.write(
            "source.md",
            "---\nkey: {id: key.before, kind: source_document}\n---\n",
        )
        captured = source.read_bytes()
        source.write_text(
            "---\nkey: {id: key.after, kind: source_document}\n---\n",
            encoding="utf-8",
        )

        snapshot, diagnostics = reconstruct(
            self.root, ["source.md"], {"source.md": captured}
        )
        changed = generation_findings(
            self.root, {"source.md": captured}, set()
        )

        self.assertEqual((), diagnostics)
        self.assertEqual(["key.before"], [node.id for node in snapshot.nodes])
        self.assertEqual(["source_generation_changed"], [item.code for item in changed])

    def test_duplicate_manifest_sources_are_not_silently_deduplicated(self):
        self.write("a.md", "---\nkey: {id: key.a, kind: source_document}\n---\n")
        manifest = self.write("manifest.json", json.dumps({
            "schema_version": 1, "sources": ["a.md", "a.md"],
        }))

        process, payload = self.run_validator("--manifest", str(manifest))

        self.assertEqual(1, process.returncode)
        self.assert_code(payload, "duplicate_manifest_source")

    def test_duplicate_missing_target_and_missing_source_are_diagnosed(self):
        self.write("one.md", """---
key: {id: key.doc.one, kind: source_document, documents: key.missing}
---
<!-- key: id=key.same kind=capability -->
## Same
""")
        self.write("two.md", """---
key: {id: key.same, kind: capability}
---
""")
        companion = {
            "schema_version": 1,
            "source": {"path": "asset.bin", "surface": "companion_metadata", "baseline_digest": "absent"},
            "nodes": [],
            "relations": [{"source": "key.ghost", "relation": "uses", "target": "key.same",
                           "evidence": "declared", "lifecycle": "active",
                           "provenance": {"surface": "companion_metadata",
                                          "locator": {"path": "asset.bin"}, "attested_by": None}}],
        }
        self.write("asset.bin.keystone.json", json.dumps(companion))
        process, payload = self.run_validator(
            "--source", "one.md", "--source", "two.md", "--source", "asset.bin"
        )

        self.assertEqual(1, process.returncode)
        self.assert_code(payload, "duplicate_id")
        self.assert_code(payload, "missing_target")
        self.assert_code(payload, "active_orphan")

    def test_malformed_invalid_vocabulary_direction_locator_cycle_and_removed_target(self):
        self.write("bad.md", """---
key: [broken
---
""")
        companion = {
            "schema_version": 1,
            "source": {"path": "graph.bin", "surface": "companion_metadata", "baseline_digest": "absent"},
            "nodes": [
                {"id": "key.cap", "kind": "capability", "locator": {"path": "missing.file"}},
                {"id": "key.removed", "kind": "capability", "lifecycle": "removed", "locator": {"path": "graph.bin"}},
                {"id": "key.code", "kind": "output_artifact", "artifact_kind": "code", "locator": {"path": "graph.bin"}},
                {"id": "key.old", "kind": "capability", "locator": {"path": "graph.bin"}},
            ],
            "relations": [
                {"source": "key.cap", "relation": "provides", "target": "key.code"},
                {"source": "key.code", "relation": "implements", "target": "key.removed"},
                {"source": "key.cap", "relation": "supersedes", "target": "key.old"},
                {"source": "key.old", "relation": "supersedes", "target": "key.cap"},
            ],
        }
        for node in companion["nodes"]:
            node.setdefault("artifact_kind", "none")
            node.setdefault("lifecycle", "active")
            node.setdefault("provenance", {"produced_from": [], "governed_by": []})
        for relation in companion["relations"]:
            relation.setdefault("evidence", "declared")
            relation.setdefault("lifecycle", "active")
            relation.setdefault("provenance", {"surface": "companion_metadata",
                                                "locator": {"path": "graph.bin"},
                                                "attested_by": None})
        self.write("graph.bin.keystone.json", json.dumps(companion))
        process, payload = self.run_validator("--source", "bad.md", "--source", "graph.bin")

        self.assertEqual(1, process.returncode)
        for code in ("malformed_metadata", "invalid_relation_direction", "locator_path_missing",
                     "supersession_cycle", "active_relation_to_retired"):
            self.assert_code(payload, code)

        companion["relations"][0]["relation"] = "invented"
        self.write("graph.bin.keystone.json", json.dumps(companion))
        _, invalid = self.run_validator("--source", "graph.bin")
        self.assert_code(invalid, "invalid_relation_vocabulary")

    def test_retired_history_and_provenance_references_are_allowed(self):
        self.write("history.md", """---
key:
  id: key.doc.history
  kind: source_document
  produced_from: [key.removed.work]
---
<!-- key: id=key.old kind=capability lifecycle=archived -->
## Old
""")
        process, payload = self.run_validator("--source", "history.md")
        self.assertEqual(0, process.returncode, payload)

    def test_verified_transaction_requires_complete_closure_and_excludes_inferred(self):
        self.write("source.md", "---\nkey: {id: key.doc, kind: source_document}\n---\n")
        transaction = {
            "schema_version": 1, "transaction_id": "tx-1", "scope_ref": "R005/S02",
            "state": "verified", "input_deltas": [],
            "canonical_mutations": [{"operation": "add", "entity": "node", "evidence": "inferred"}],
            "surface_patches": [{"patch_id": "p1", "owner": "author", "surface": "document_metadata",
                                 "target_path": "source.md", "baseline_digest": "absent", "exact_patch": "x", "required": True}],
            "attestations": [], "apply_results": [], "mechanical_validation": [],
        }
        path = self.write("transaction.json", json.dumps(transaction))
        process, payload = self.run_validator("--source", "source.md", "--transaction", str(path))

        self.assertEqual(1, process.returncode)
        for code in ("inferred_mutation_forbidden", "verified_attestation_missing",
                     "verified_apply_missing", "verified_reconstruction_missing"):
            self.assert_code(payload, code)

    def test_verified_transaction_checks_owner_digest_and_reconstruction_closure(self):
        raw = b"---\nkey: {id: key.doc, kind: source_document}\n---\n"
        (self.root / "source.md").write_bytes(raw)
        transaction = {
            "schema_version": 1, "transaction_id": "tx-closed", "scope_ref": "R005/S02",
            "state": "verified", "input_deltas": [], "canonical_mutations": [{
                "operation": "add", "entity": "node", "before": None, "evidence": "declared",
                "after": {"id": "key.doc", "kind": "source_document", "artifact_kind": "none",
                          "locator": {"path": "source.md"}, "lifecycle": "active",
                          "provenance": {"produced_from": [], "governed_by": [],
                                         "surface": "document_metadata", "locator": {"path": "source.md"}}}
            }],
            "surface_patches": [{"patch_id": "p1", "owner": "author", "surface": "document_metadata",
                                 "target_path": "source.md", "baseline_digest": "absent",
                                 "exact_patch": "x", "required": True}],
            "attestations": [{"patch_id": "p1", "owner": "main", "decision": "confirm", "evidence": "review"}],
            "apply_results": [{"patch_id": "p1", "result": "applied",
                               "resulting_digest": "sha256:" + "0" * 64, "evidence": "apply"}],
            "reconstruction": {"baseline": {"schema_version": 1, "nodes": [], "relations": []},
                               "result": {"schema_version": 1, "nodes": [], "relations": []}},
            "mechanical_validation": {"schema_version": 1, "status": "pass", "diagnostics": [],
                                      "summary": {"errors": 0, "warnings": 0}},
        }
        path = self.write("transaction.json", json.dumps(transaction))
        process, payload = self.run_validator("--source", "source.md", "--transaction", str(path))

        self.assertEqual(1, process.returncode)
        for code in ("attestation_owner_mismatch", "resulting_digest_mismatch",
                     "verified_reconstruction_mismatch"):
            self.assert_code(payload, code)

        transaction["attestations"][0]["owner"] = "author"
        transaction["apply_results"][0]["resulting_digest"] = "sha256:" + hashlib.sha256(raw).hexdigest()
        transaction["reconstruction"] = {"baseline": {"schema_version": 1, "nodes": [], "relations": []}, "result": {
            "schema_version": 1,
            "nodes": [{"id": "key.doc", "kind": "source_document", "artifact_kind": "none",
                       "locator": {"path": "source.md"}, "lifecycle": "active",
                       "provenance": {"produced_from": [], "governed_by": [],
                                      "surface": "document_metadata", "locator": {"path": "source.md"}}}],
            "relations": [],
        }}
        path.write_text(json.dumps(transaction), encoding="utf-8")
        passed, passed_payload = self.run_validator("--source", "source.md", "--transaction", str(path))
        self.assertEqual(0, passed.returncode, passed_payload)

    def test_non_object_relation_has_stable_invalid_format_diagnostic(self):
        companion = {
            "schema_version": 1,
            "source": {"path": "asset.bin", "surface": "companion_metadata", "baseline_digest": "absent"},
            "nodes": [], "relations": ["not-an-object"],
        }
        self.write("asset.bin.keystone.json", json.dumps(companion))
        process, payload = self.run_validator("--source", "asset.bin")
        self.assertEqual(1, process.returncode)
        self.assert_code(payload, "invalid_relation_format")

    def test_all_eight_transaction_states_are_admitted(self):
        for state in ("proposed", "awaiting_attestation", "ready_to_apply", "applying",
                      "partially_applied", "verified", "conflicted", "failed"):
            with self.subTest(state=state):
                transaction = {"schema_version": 1, "transaction_id": "tx", "scope_ref": "scope",
                               "state": state, "input_deltas": [], "canonical_mutations": [],
                               "surface_patches": [], "attestations": [], "apply_results": [],
                               "reconstruction": {"schema_version": 1, "nodes": [], "relations": []},
                               "mechanical_validation": []}
                path = self.write("tx.json", json.dumps(transaction))
                process, payload = self.run_validator("--transaction", str(path))
                self.assertNotEqual(2, process.returncode, payload)
                self.assertNotIn("transaction_state_invalid", [d["code"] for d in payload["diagnostics"]])

    def test_transaction_state_contradictions_have_stable_diagnostics(self):
        cases = [
            ("proposed", [{"patch_id": "p", "owner": "author", "decision": "confirm"}], [],
             "proposed_evidence_forbidden"),
            ("awaiting_attestation", [], [{"patch_id": "p", "result": "applied"}],
             "preapply_result_forbidden"),
            ("ready_to_apply", [], [], "state_attestation_incomplete"),
            ("applying", [], [], "state_attestation_incomplete"),
            ("partially_applied", [{"patch_id": "p", "owner": "author", "decision": "confirm"}], [],
             "partial_application_missing"),
            ("conflicted", [], [], "conflict_evidence_missing"),
            ("failed", [], [], "failure_evidence_missing"),
        ]
        for state, attestations, results, code in cases:
            with self.subTest(state=state):
                transaction = {
                    "schema_version": 1, "transaction_id": "tx", "scope_ref": "scope", "state": state,
                    "input_deltas": [], "canonical_mutations": [],
                    "surface_patches": [{"patch_id": "p", "owner": "author", "surface": "document_metadata",
                                         "target_path": "new.md", "baseline_digest": "absent",
                                         "exact_patch": "x", "required": True}],
                    "attestations": attestations, "apply_results": results,
                    "mechanical_validation": [],
                }
                path = self.write("tx.json", json.dumps(transaction))
                process, payload = self.run_validator("--transaction", str(path))
                self.assertEqual(1, process.returncode)
                self.assert_code(payload, code)

    def test_conflicted_counts_only_valid_known_patch_evidence(self):
        patch = {"patch_id": "p", "owner": "author", "surface": "document_metadata",
                 "target_path": "new.md", "baseline_digest": "absent",
                 "exact_patch": "x", "required": True}
        cases = [
            ([{"patch_id": "p", "owner": "author", "decision": "reject",
               "evidence": "reviewed", "extra": True}], [], "attestation_invalid"),
            ([{"patch_id": "unknown", "owner": "author", "decision": "needs_revision",
               "evidence": "reviewed"}], [], "attestation_patch_unknown"),
            ([], [{"patch_id": "p", "result": "stale_baseline", "resulting_digest": None,
                   "evidence": ""}], "application_result_invalid"),
        ]
        for attestations, results, schema_code in cases:
            with self.subTest(schema_code=schema_code):
                transaction = {
                    "schema_version": 1, "transaction_id": "tx", "scope_ref": "scope",
                    "state": "conflicted", "input_deltas": [], "canonical_mutations": [],
                    "surface_patches": [patch], "attestations": attestations,
                    "apply_results": results,
                }
                path = self.write("tx.json", json.dumps(transaction))
                _, payload = self.run_validator("--transaction", str(path))

                self.assert_code(payload, schema_code)
                self.assert_code(payload, "conflict_evidence_missing")

        valid_cases = [
            ([{"patch_id": "p", "owner": "author", "decision": "reject",
               "evidence": "reviewed"}], []),
            ([{"patch_id": "p", "owner": "author", "decision": "needs_revision",
               "evidence": "reviewed"}], []),
            ([], [{"patch_id": "p", "result": "stale_baseline", "resulting_digest": None,
                   "evidence": "baseline changed"}]),
        ]
        for attestations, results in valid_cases:
            with self.subTest(attestations=attestations, results=results):
                transaction = {
                    "schema_version": 1, "transaction_id": "tx", "scope_ref": "scope",
                    "state": "conflicted", "input_deltas": [], "canonical_mutations": [],
                    "surface_patches": [patch], "attestations": attestations,
                    "apply_results": results,
                }
                path = self.write("tx.json", json.dumps(transaction))
                _, payload = self.run_validator("--transaction", str(path))

                self.assertNotIn("conflict_evidence_missing",
                                 [item["code"] for item in payload["diagnostics"]])

    def test_wrong_owner_confirm_does_not_satisfy_ready_or_verified_state(self):
        patch = {"patch_id": "p", "owner": "author", "surface": "document_metadata",
                 "target_path": "new.md", "baseline_digest": "absent",
                 "exact_patch": "x", "required": True}
        for state, state_code in (("ready_to_apply", "state_attestation_incomplete"),
                                  ("verified", "verified_attestation_missing")):
            with self.subTest(state=state):
                transaction = {
                    "schema_version": 1, "transaction_id": "tx", "scope_ref": "scope",
                    "state": state, "input_deltas": [], "canonical_mutations": [],
                    "surface_patches": [patch],
                    "attestations": [{"patch_id": "p", "owner": "main",
                                      "decision": "confirm", "evidence": "reviewed"}],
                    "apply_results": [],
                }
                path = self.write("tx.json", json.dumps(transaction))
                _, payload = self.run_validator("--transaction", str(path))

                self.assert_code(payload, "attestation_owner_mismatch")
                self.assert_code(payload, state_code)

    def test_wrong_owner_reject_or_revision_does_not_satisfy_conflicted_state(self):
        patch = {"patch_id": "p", "owner": "author", "surface": "document_metadata",
                 "target_path": "new.md", "baseline_digest": "absent",
                 "exact_patch": "x", "required": True}
        for decision in ("reject", "needs_revision"):
            with self.subTest(decision=decision):
                transaction = {
                    "schema_version": 1, "transaction_id": "tx", "scope_ref": "scope",
                    "state": "conflicted", "input_deltas": [], "canonical_mutations": [],
                    "surface_patches": [patch],
                    "attestations": [{"patch_id": "p", "owner": "main",
                                      "decision": decision, "evidence": "reviewed"}],
                    "apply_results": [],
                }
                path = self.write("tx.json", json.dumps(transaction))
                _, payload = self.run_validator("--transaction", str(path))

                self.assert_code(payload, "attestation_owner_mismatch")
                self.assert_code(payload, "conflict_evidence_missing")

    def test_failed_counts_only_valid_known_patch_application_evidence(self):
        patch = {"patch_id": "p", "owner": "author", "surface": "document_metadata",
                 "target_path": "new.md", "baseline_digest": "absent",
                 "exact_patch": "x", "required": True}
        cases = [
            ({"patch_id": "unknown", "result": "failed", "resulting_digest": None,
              "evidence": "write failed"}, "apply_result_patch_unknown"),
            ({"patch_id": "p", "result": "failed", "resulting_digest": None,
              "evidence": "write failed", "extra": True}, "application_result_invalid"),
            ({"patch_id": "p", "result": "failed", "resulting_digest": None,
              "evidence": ""}, "application_result_invalid"),
        ]
        for result, schema_code in cases:
            with self.subTest(result=result):
                transaction = {
                    "schema_version": 1, "transaction_id": "tx", "scope_ref": "scope",
                    "state": "failed", "input_deltas": [], "canonical_mutations": [],
                    "surface_patches": [patch], "attestations": [],
                    "apply_results": [result],
                }
                path = self.write("tx.json", json.dumps(transaction))
                _, payload = self.run_validator("--transaction", str(path))

                self.assert_code(payload, schema_code)
                self.assert_code(payload, "failure_evidence_missing")

        transaction["apply_results"] = [{"patch_id": "p", "result": "failed",
                                          "resulting_digest": None,
                                          "evidence": "write failed"}]
        path = self.write("tx.json", json.dumps(transaction))
        _, payload = self.run_validator("--transaction", str(path))
        self.assertNotIn("failure_evidence_missing",
                         [item["code"] for item in payload["diagnostics"]])

    def test_failed_accepts_well_formed_failing_mechanical_envelope(self):
        transaction = {
            "schema_version": 1, "transaction_id": "tx", "scope_ref": "scope",
            "state": "failed", "input_deltas": [], "canonical_mutations": [],
            "surface_patches": [], "attestations": [], "apply_results": [],
            "mechanical_validation": {
                "schema_version": 1, "status": "fail",
                "diagnostics": [{"code": "missing_target", "message": "missing",
                                 "severity": "error"}],
                "summary": {"errors": 1, "warnings": 0},
            },
        }
        path = self.write("tx.json", json.dumps(transaction))
        _, payload = self.run_validator("--transaction", str(path))
        codes = [item["code"] for item in payload["diagnostics"]]

        self.assertNotIn("mechanical_validation_invalid", codes)
        self.assertNotIn("failure_evidence_missing", codes)

    def test_malformed_failing_mechanical_envelope_is_not_failure_evidence(self):
        transaction = {
            "schema_version": 1, "transaction_id": "tx", "scope_ref": "scope",
            "state": "failed", "input_deltas": [], "canonical_mutations": [],
            "surface_patches": [], "attestations": [], "apply_results": [],
            "mechanical_validation": {
                "schema_version": 1, "status": "fail",
                "diagnostics": [{"code": "missing_target", "message": "missing",
                                 "severity": "error"}],
                "summary": {"errors": 0, "warnings": 0},
            },
        }
        path = self.write("tx.json", json.dumps(transaction))
        _, payload = self.run_validator("--transaction", str(path))

        self.assert_code(payload, "mechanical_validation_invalid")
        self.assert_code(payload, "failure_evidence_missing")

    def test_verified_rejects_structurally_valid_failing_mechanical_envelope(self):
        transaction = {
            "schema_version": 1, "transaction_id": "tx", "scope_ref": "scope",
            "state": "verified", "input_deltas": [], "canonical_mutations": [],
            "surface_patches": [], "attestations": [], "apply_results": [],
            "mechanical_validation": {
                "schema_version": 1, "status": "fail",
                "diagnostics": [{"code": "missing_target", "message": "missing",
                                 "severity": "error"}],
                "summary": {"errors": 1, "warnings": 0},
            },
        }
        path = self.write("tx.json", json.dumps(transaction))
        _, payload = self.run_validator("--transaction", str(path))
        codes = [item["code"] for item in payload["diagnostics"]]

        self.assertNotIn("mechanical_validation_invalid", codes)
        self.assertIn("verified_validation_failed", codes)

    def test_invocation_failures_use_exit_two_and_json_envelope(self):
        process, payload = self.run_validator("--source", "missing.md")
        self.assertEqual(2, process.returncode)
        self.assertEqual("error", payload["status"])
        self.assert_code(payload, "source_unavailable")

    def test_manifest_rejects_non_relative_and_non_string_sources_without_traceback(self):
        for source in (None, 3, "", "/absolute.md", "../escape.md"):
            with self.subTest(source=source):
                manifest = self.write("manifest.json", json.dumps({"schema_version": 1, "sources": [source]}))
                process, payload = self.run_validator("--manifest", str(manifest))
                self.assertEqual(2, process.returncode)
                self.assertEqual("", process.stderr)
                self.assert_code(payload, "manifest_source_invalid")

    def test_verified_rejects_vacuous_and_source_mismatched_canonical_mutations(self):
        self.write("source.md", "---\nkey: {id: key.doc, kind: source_document}\n---\n")
        transaction = {
            "schema_version": 1, "transaction_id": "tx", "scope_ref": "scope", "state": "verified",
            "input_deltas": [], "canonical_mutations": [], "surface_patches": [],
            "attestations": [], "apply_results": [],
            "reconstruction": {"baseline": {"schema_version": 1, "nodes": [], "relations": []}, "result": {"schema_version": 1, "nodes": [{"id": "key.doc", "kind": "source_document",
                "artifact_kind": "none", "locator": {"path": "source.md"}, "lifecycle": "active",
                "provenance": {"produced_from": [], "governed_by": [], "surface": "document_metadata",
                               "locator": {"path": "source.md"}}}], "relations": []}},
            "mechanical_validation": [], "coverage_debt": [],
        }
        path = self.write("tx.json", json.dumps(transaction))
        _, vacuous = self.run_validator("--source", "source.md", "--transaction", str(path))
        self.assert_code(vacuous, "verified_closure_vacuous")
        self.assert_code(vacuous, "verified_validation_empty")

        transaction["canonical_mutations"] = [{"operation": "add", "entity": "node", "before": None,
            "after": {"id": "key.other", "kind": "capability", "artifact_kind": "none",
                      "locator": {"path": "source.md"}, "lifecycle": "active",
                      "provenance": {"produced_from": [], "governed_by": []}}, "evidence": "declared"}]
        transaction["mechanical_validation"] = {"schema_version": 1, "status": "pass", "diagnostics": [],
                                                 "summary": {"errors": 0, "warnings": 0}}
        path.write_text(json.dumps(transaction), encoding="utf-8")
        _, mismatch = self.run_validator("--source", "source.md", "--transaction", str(path))
        self.assert_code(mismatch, "mutation_reconstruction_mismatch")

    def test_canonical_mutation_wire_rejects_bad_entity_and_duplicate_identity(self):
        bad_node = {"id": "key.a", "kind": "invented", "artifact_kind": "none",
                    "locator": {"path": "x.md"}, "lifecycle": "active",
                    "provenance": {"produced_from": [], "governed_by": []}}
        tx = {"schema_version": 1, "transaction_id": "tx", "scope_ref": "scope", "state": "proposed",
              "input_deltas": [], "surface_patches": [], "attestations": [], "apply_results": [],
              "coverage_debt": [], "canonical_mutations": [
                  {"operation": "add", "entity": "node", "before": None, "after": bad_node, "evidence": "declared"},
                  {"operation": "add", "entity": "node", "before": None, "after": bad_node, "evidence": "declared"},
              ]}
        path = self.write("tx.json", json.dumps(tx))
        _, payload = self.run_validator("--transaction", str(path))
        self.assert_code(payload, "mutation_node_invalid")
        self.assert_code(payload, "mutation_identity_duplicate")

    def test_verified_baseline_plus_mutations_must_exactly_equal_reconstruction(self):
        self.write("source.md", "---\nkey: {id: key.doc, kind: source_document}\n---\n")
        node = {"id": "key.doc", "kind": "source_document", "artifact_kind": "none",
                "locator": {"path": "source.md"}, "lifecycle": "active",
                "provenance": {"produced_from": [], "governed_by": [], "surface": "document_metadata",
                               "locator": {"path": "source.md"}}}
        patch = {"patch_id": "p", "owner": "author", "surface": "document_metadata",
                 "target_path": "source.md", "baseline_digest": "absent", "exact_patch": "add", "required": True}
        tx = {"schema_version": 1, "transaction_id": "tx", "scope_ref": "scope", "state": "verified",
              "input_deltas": [], "coverage_debt": [],
              "canonical_mutations": [{"operation": "add", "entity": "node", "before": None,
                                       "after": node, "evidence": "declared"}],
              "surface_patches": [patch],
              "attestations": [{"patch_id": "p", "owner": "author", "decision": "confirm", "evidence": "reviewed"}],
              "apply_results": [{"patch_id": "p", "result": "applied", "resulting_digest":
                                  "sha256:" + hashlib.sha256((self.root / "source.md").read_bytes()).hexdigest(),
                                  "evidence": "applied"}],
              "reconstruction": {"baseline": {"schema_version": 1, "nodes": [], "relations": []},
                                 "result": {"schema_version": 1, "nodes": [node], "relations": []}},
              "mechanical_validation": {"schema_version": 1, "status": "pass", "diagnostics": [],
                                        "summary": {"errors": 0, "warnings": 0}}}
        path = self.write("tx.json", json.dumps(tx))
        process, payload = self.run_validator("--source", "source.md", "--transaction", str(path))
        self.assertEqual(0, process.returncode, payload)

        tx["reconstruction"]["baseline"] = {"schema_version": 1, "nodes": [node], "relations": []}
        path.write_text(json.dumps(tx), encoding="utf-8")
        _, mismatch = self.run_validator("--source", "source.md", "--transaction", str(path))
        self.assert_code(mismatch, "mutation_baseline_closure_mismatch")

    def test_transaction_items_and_mechanical_envelope_are_fully_validated(self):
        tx = {"schema_version": 1, "transaction_id": "tx", "scope_ref": "scope", "state": "proposed",
              "input_deltas": [{"kind": "wrong", "source_surface": "", "changed_locators": "bad",
                                "semantic_summary": 3, "baseline_digest": "bad", "graph_relevant": "yes"}],
              "coverage_debt": [], "canonical_mutations": [],
              "surface_patches": [{"patch_id": "p", "owner": "author", "surface": "document_metadata",
                                   "target_path": "../escape", "baseline_digest": "absent",
                                   "exact_patch": "", "required": True}],
              "attestations": [{"patch_id": "p", "owner": "bogus", "decision": "confirm",
                                "evidence": "", "extra": True}],
              "apply_results": [{"patch_id": "p", "result": "failed", "resulting_digest": None,
                                 "evidence": "", "extra": True}],
              "mechanical_validation": {"schema_version": 1, "status": "pass", "diagnostics":
                                        [{"code": "bad", "severity": "error", "message": "bad"}],
                                        "summary": {"errors": 0, "warnings": 0}}}
        path = self.write("tx.json", json.dumps(tx))
        _, payload = self.run_validator("--transaction", str(path))
        for code in ("input_delta_invalid", "patch_target_invalid", "patch_exact_patch_invalid",
                     "attestation_invalid", "application_result_invalid",
                     "mechanical_validation_invalid"):
            self.assert_code(payload, code)

    def test_transaction_wire_rejects_duplicate_patch_attestation_result_and_bad_shapes(self):
        patch = {"patch_id": "p", "owner": "author", "surface": "document_metadata",
                 "target_path": "x.md", "baseline_digest": "absent", "exact_patch": "x", "required": True}
        tx = {"schema_version": 1, "transaction_id": "tx", "scope_ref": "scope", "state": "failed",
              "input_deltas": "bad", "coverage_debt": {}, "canonical_mutations": [],
              "surface_patches": [patch, patch],
              "attestations": [{"patch_id": "p", "owner": "author", "decision": "confirm"}] * 2,
              "apply_results": [{"patch_id": "p", "result": "failed"}] * 2,
              "mechanical_validation": []}
        path = self.write("tx.json", json.dumps(tx))
        _, payload = self.run_validator("--transaction", str(path))
        for code in ("input_deltas_invalid", "coverage_debt_invalid", "patch_id_duplicate",
                     "attestation_duplicate", "apply_result_duplicate"):
            self.assert_code(payload, code)

    def test_declared_text_locators_are_checked_mechanically(self):
        self.write("loc.md", """---
key:
  id: key.loc
  kind: output_artifact
  artifact_kind: test
locator:
  path: loc.md
  heading: Missing heading
  symbol: MissingSymbol
  test_name: missing_test
  config_key: missing.key
  schema_name: missing_table
---
# Present
""")
        _, payload = self.run_validator("--source", "loc.md")
        for code in ("locator_heading_stale", "locator_symbol_stale", "locator_test_name_stale",
                     "locator_config_key_stale", "locator_schema_name_stale"):
            self.assert_code(payload, code)

    def test_relation_direction_table_rejects_wrong_official_directions(self):
        companion = {"schema_version": 1,
            "source": {"path": "graph.bin", "surface": "companion_metadata", "baseline_digest": "absent"},
            "nodes": [
                {"id": "key.cap", "kind": "capability", "locator": {"path": "graph.bin"}},
                {"id": "key.doc", "kind": "source_document", "locator": {"path": "graph.bin"}},
                {"id": "key.out", "kind": "output_artifact", "artifact_kind": "code", "locator": {"path": "graph.bin"}},
            ],
            "relations": [
                {"source": "key.cap", "relation": "produces", "target": "key.out"},
                {"source": "key.cap", "relation": "implements", "target": "key.doc"},
                {"source": "key.cap", "relation": "governed_by", "target": "key.doc"},
                {"source": "key.out", "relation": "documents", "target": "key.cap"},
                {"source": "key.cap", "relation": "uses", "target": "key.out"},
                {"source": "key.cap", "relation": "derived_from", "target": "key.out"},
            ]}
        for node in companion["nodes"]:
            node.setdefault("artifact_kind", "none")
            node.setdefault("lifecycle", "active")
            node.setdefault("provenance", {"produced_from": [], "governed_by": []})
        for relation in companion["relations"]:
            relation.setdefault("evidence", "declared")
            relation.setdefault("lifecycle", "active")
            relation.setdefault("provenance", {"surface": "companion_metadata",
                                                "locator": {"path": "graph.bin"},
                                                "attested_by": None})
        self.write("graph.bin.keystone.json", json.dumps(companion))
        _, payload = self.run_validator("--source", "graph.bin")
        self.assertGreaterEqual([d["code"] for d in payload["diagnostics"]].count("invalid_relation_direction"), 6)

    def test_uses_and_verifies_enforce_artifact_kind_targets(self):
        companion = {"schema_version": 1,
            "source": {"path": "graph.bin", "surface": "companion_metadata", "baseline_digest": "absent"},
            "nodes": [
                {"id": "key.code", "kind": "output_artifact", "artifact_kind": "code", "locator": {"path": "graph.bin"}},
                {"id": "key.api", "kind": "output_artifact", "artifact_kind": "api", "locator": {"path": "graph.bin"}},
                {"id": "key.config", "kind": "output_artifact", "artifact_kind": "config", "locator": {"path": "graph.bin"}},
                {"id": "key.test", "kind": "output_artifact", "artifact_kind": "test", "locator": {"path": "graph.bin"}},
                {"id": "key.cap", "kind": "capability", "locator": {"path": "graph.bin"}},
                {"id": "key.doc", "kind": "source_document", "locator": {"path": "graph.bin"}},
            ], "relations": [
                {"source": "key.code", "relation": "uses", "target": "key.api"},
                {"source": "key.test", "relation": "verifies", "target": "key.cap"},
                {"source": "key.code", "relation": "uses", "target": "key.config"},
                {"source": "key.test", "relation": "verifies", "target": "key.doc"},
            ]}
        for node in companion["nodes"]:
            node.setdefault("artifact_kind", "none")
            node.setdefault("lifecycle", "active")
            node.setdefault("provenance", {"produced_from": [], "governed_by": []})
        for relation in companion["relations"]:
            relation.setdefault("evidence", "declared")
            relation.setdefault("lifecycle", "active")
            relation.setdefault("provenance", {"surface": "companion_metadata",
                                                "locator": {"path": "graph.bin"},
                                                "attested_by": None})
        self.write("graph.bin.keystone.json", json.dumps(companion))
        _, payload = self.run_validator("--source", "graph.bin")
        self.assertEqual(2, [d["code"] for d in payload["diagnostics"]].count("invalid_relation_direction"))

    def test_produced_from_reconstructs_and_missing_target_has_stable_diagnostic(self):
        self.write("build.md", """---
key: {id: key.work.build, kind: work_order}
---
<!-- key: id=key.output.runtime kind=output_artifact artifact_kind=code produced_from=key.work.build -->
- Runtime
""")
        process, payload = self.run_validator("--source", "build.md")
        self.assertEqual(0, process.returncode, payload)

        self.write("missing.md", """---
key: {id: key.output.runtime, kind: output_artifact, artifact_kind: code, produced_from: key.work.missing}
---
""")
        _, missing = self.run_validator("--source", "missing.md")
        self.assert_code(missing, "produced_from_target_missing")

    def test_multisource_explicit_produces_wins_over_derived_mirror(self):
        self.write("work.md", """---
key: {id: key.work.build, kind: work_order, produces: key.output.runtime}
---
""")
        self.write("output.ts", """// keystone: id=key.output.runtime kind=output_artifact artifact_kind=code produced_from=key.work.build
export function runtime() {}
""")

        snapshot, diagnostics = reconstruct(self.root, ("output.ts", "work.md"))
        matches = [relation for relation in snapshot.relations
                   if (relation.source, relation.relation, relation.target) ==
                   ("key.work.build", RelationType.PRODUCES, "key.output.runtime")]

        self.assertEqual(1, len(matches))
        self.assertEqual(Evidence.DECLARED, matches[0].evidence)
        self.assertFalse(diagnostics)

    def test_reconstruction_rejects_inline_and_companion_metadata_conflict(self):
        source = self.write(
            "source.py",
            "# keystone: id=key.source.inline kind=output_artifact\npass\n",
        )
        digest = "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest()
        companion = {
            "schema_version": 1,
            "source": {"path": "source.py", "surface": "companion_metadata",
                       "baseline_digest": digest},
            "nodes": [{
                "id": "key.source.companion", "kind": "output_artifact",
                "artifact_kind": "code", "locator": {"path": "source.py"},
                "lifecycle": "active",
                "provenance": {"produced_from": [], "governed_by": []},
            }],
            "relations": [],
        }
        self.write("source.py.keystone.json", json.dumps(companion))

        snapshot, diagnostics = reconstruct(self.root, ("source.py",))

        self.assertFalse(snapshot.nodes)
        self.assertIn(
            "metadata_surface_conflict", {item.code for item in diagnostics}
        )

    def test_supported_companion_bytes_are_part_of_captured_generation(self):
        self.write("source.py", "pass\n")
        self.write("source.py.keystone.json", "{}")

        captured, absent = capture_sources(self.root, ("source.py",))

        self.assertEqual(
            {"source.py", "source.py.keystone.json"}, set(captured)
        )
        self.assertFalse(absent)

    def test_non_utf8_supported_source_reconstructs_from_companion(self):
        source = self.write_bytes(
            "generated.py",
            "generated output\n".encode("utf-16"),
        )
        digest = "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest()
        self.write("generated.py.keystone.json", json.dumps({
            "schema_version": 1,
            "source": {
                "path": "generated.py",
                "surface": "companion_metadata",
                "baseline_digest": digest,
            },
            "nodes": [{
                "id": "key.output.generated",
                "kind": "output_artifact",
                "artifact_kind": "code",
                "locator": {"path": "generated.py"},
                "lifecycle": "active",
                "provenance": {"produced_from": [], "governed_by": []},
            }],
            "relations": [],
        }))

        snapshot, diagnostics = reconstruct(self.root, ("generated.py",))

        self.assertEqual({"key.output.generated"}, {node.id for node in snapshot.nodes})
        self.assertFalse(diagnostics)

    def test_invalid_companion_encoding_has_scanner_reconstruction_parity(self):
        self.write_bytes("generated.py", "generated output\n".encode("utf-16"))
        self.write_bytes("generated.py.keystone.json", b"\xff\xfe")

        scan = ReferenceScanner(self.root).scan(ScanScope.REPOSITORY)
        snapshot, diagnostics = reconstruct(self.root, ("generated.py",))

        self.assertFalse(snapshot.nodes)
        self.assertEqual(
            {"unsupported_encoding"},
            {item.code for item in diagnostics},
        )
        self.assertIn(
            "unsupported_encoding",
            {item.code for item in scan.diagnostics},
        )

    def test_ambiguous_anchor_blocks_companion_with_scanner_reconstruction_parity(self):
        source = self.write(
            "example.ts",
            "const sample = `\n"
            "// keystone: id=key.ambiguous kind=output_artifact\n",
        )
        digest = "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest()
        self.write("example.ts.keystone.json", json.dumps({
            "schema_version": 1,
            "source": {
                "path": "example.ts",
                "surface": "companion_metadata",
                "baseline_digest": digest,
            },
            "nodes": [],
            "relations": [],
        }))

        scan = ReferenceScanner(self.root).scan(ScanScope.REPOSITORY)
        snapshot, diagnostics = reconstruct(self.root, ("example.ts",))

        self.assertFalse(snapshot.nodes)
        self.assertEqual(
            {"ambiguous_metadata_anchor"},
            {item.code for item in diagnostics},
        )
        self.assertIn(
            "ambiguous_metadata_anchor",
            {item.code for item in scan.diagnostics},
        )

    def test_supported_companion_reconstructs_with_absent_logical_source(self):
        self.write("generated.py.keystone.json", json.dumps({
            "schema_version": 1,
            "source": {
                "path": "generated.py",
                "surface": "companion_metadata",
                "baseline_digest": "absent",
            },
            "nodes": [],
            "relations": [],
        }))

        process, payload = self.run_validator("--source", "generated.py")

        self.assertEqual(0, process.returncode, payload)
        self.assertEqual("pass", payload["status"])
        self.assertEqual({"errors": 0, "warnings": 0}, payload["summary"])

    def test_validator_enforces_owner_surface_matrix_and_required_patch_invariant(self):
        node = {"id": "key.new", "kind": "capability", "artifact_kind": "none",
                "locator": {"path": "new.md"}, "lifecycle": "active",
                "provenance": {"produced_from": [], "governed_by": []}}
        transaction = {
            "schema_version": 1, "transaction_id": "tx", "scope_ref": "scope",
            "state": "ready_to_apply", "input_deltas": [],
            "canonical_mutations": [{"operation": "add", "entity": "node", "before": None,
                                      "after": node, "evidence": "declared"}],
            "surface_patches": [{"patch_id": "p", "owner": "main", "surface": "document_metadata",
                                  "target_path": "new.md", "baseline_digest": "absent",
                                  "exact_patch": "x", "required": False}],
            "attestations": [], "apply_results": [], "coverage_debt": [],
        }
        path = self.write("tx.json", json.dumps(transaction))
        _, payload = self.run_validator("--transaction", str(path))
        self.assert_code(payload, "patch_owner_surface_invalid")
        self.assert_code(payload, "graph_change_required_patch_missing")


if __name__ == "__main__":
    unittest.main()
