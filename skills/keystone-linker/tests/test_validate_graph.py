import json
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from graph_runtime.model import Evidence, RelationType
from graph_runtime.validator import reconstruct


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_graph.py"
RUNNER = Path(__file__).parents[1] / "scripts" / "run_graph_validation.py"


class GraphValidatorCliTest(unittest.TestCase):
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
<!-- key: id=key.old kind=capability lifecycle=removed -->
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
