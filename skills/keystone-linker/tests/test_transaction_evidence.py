import hashlib
import tempfile
import unittest
from pathlib import Path

from graph_runtime.patch_replay import replay_patch
from graph_runtime.transaction_evidence import validate_transaction_evidence


class TransactionEvidenceTest(unittest.TestCase):
    def _v2_patch(self, patch_id, target_path, before, after, *, required):
        baseline = before.encode("utf-8")
        result = after.encode("utf-8")
        return {
            "patch_id": patch_id,
            "owner": "author",
            "surface": "document_metadata",
            "target_path": target_path,
            "baseline_digest": "sha256:" + hashlib.sha256(baseline).hexdigest(),
            "exact_patch": after,
            "patch_format": "full_replacement",
            "patch_body": after,
            "expected_after_digest": "sha256:" + hashlib.sha256(result).hexdigest(),
            "baseline_content": before,
            "required": required,
        }

    def _v2_delta(self, patch):
        return {
            "kind": (
                "document_delta"
                if patch["target_path"].endswith((".md", ".markdown"))
                else "artifact_delta"
            ),
            "source_surface": patch["target_path"],
            "changed_locators": [{"path": patch["target_path"]}],
            "semantic_summary": "bind executable patch",
            "baseline_digest": patch["baseline_digest"],
            "graph_relevant": True,
        }

    def test_duplicate_physical_patch_target_is_rejected(self):
        patch = {
            "patch_id": "p1",
            "owner": "main",
            "surface": "code_anchor",
            "target_path": "src/example.py",
            "exact_patch": "first",
            "required": True,
            "baseline_digest": "absent",
        }
        duplicate = dict(patch, patch_id="p2", exact_patch="second")

        result = validate_transaction_evidence(
            {
                "schema_version": 1,
                "surface_patches": [patch, duplicate],
                "attestations": [],
                "apply_results": [],
            },
            root=None,
            mutations=(),
        )

        self.assertIn(
            "patch_target_duplicate",
            {item.code for item in result.diagnostics},
        )

    def test_path_aliases_and_symlinks_cannot_duplicate_physical_target(self):
        patch = {
            "patch_id": "p1",
            "owner": "main",
            "surface": "code_anchor",
            "target_path": "src/example.py",
            "exact_patch": "first",
            "required": True,
            "baseline_digest": "absent",
        }
        noncanonical = dict(
            patch,
            patch_id="p2",
            target_path="src/../src/example.py",
            exact_patch="second",
        )
        invalid = validate_transaction_evidence(
            {
                "schema_version": 1,
                "surface_patches": [patch, noncanonical],
                "attestations": [],
                "apply_results": [],
            },
            root=None,
            mutations=(),
        )
        self.assertIn(
            "patch_target_invalid",
            {item.code for item in invalid.diagnostics},
        )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "src"
            source.mkdir()
            (source / "example.py").write_text("before\n", encoding="utf-8")
            (root / "alias").symlink_to(source, target_is_directory=True)
            symlink_alias = dict(
                patch,
                patch_id="p2",
                target_path="alias/example.py",
                exact_patch="second",
            )
            duplicate = validate_transaction_evidence(
                {
                    "schema_version": 1,
                    "surface_patches": [patch, symlink_alias],
                    "attestations": [],
                    "apply_results": [],
                },
                root=root,
                mutations=(),
            )
        self.assertIn(
            "patch_target_duplicate",
            {item.code for item in duplicate.diagnostics},
        )

    def test_schema_v2_applied_digest_must_equal_planned_after_digest(self):
        body = "after\n"
        expected = "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()
        patch = {
            "patch_id": "p1",
            "owner": "author",
            "surface": "document_metadata",
            "target_path": "source.md",
            "baseline_digest": "absent",
            "exact_patch": body,
            "patch_format": "full_replacement",
            "patch_body": body,
            "expected_after_digest": expected,
            "baseline_content": None,
            "required": True,
        }
        result = validate_transaction_evidence(
            {
                "schema_version": 2,
                "surface_patches": [patch],
                "attestations": [],
                "apply_results": [{
                    "patch_id": "p1",
                    "result": "applied",
                    "resulting_digest": "sha256:" + "f" * 64,
                    "evidence": "written",
                }],
            },
            root=None,
            mutations=(),
        )

        self.assertIn(
            "resulting_digest_expected_mismatch",
            {item.code for item in result.diagnostics},
        )

    def test_unified_diff_replay_checks_context_and_applies_hunks(self):
        patch = (
            "--- a/source.md\n+++ b/source.md\n"
            "@@ -1,2 +1,2 @@\n before\n-old\n+new\n"
        )

        self.assertEqual(
            b"before\nnew\n",
            replay_patch(b"before\nold\n", "unified_diff", patch),
        )
        with self.assertRaisesRegex(ValueError, "context"):
            replay_patch(b"before\nchanged\n", "unified_diff", patch)
        with self.assertRaisesRegex(ValueError, "counts"):
            replay_patch(
                b"before\nold\n",
                "unified_diff",
                patch.replace("@@ -1,2 +1,2 @@", "@@ -1,3 +1,2 @@"),
            )

        self.assertEqual(
            b"new\n",
            replay_patch(b"", "unified_diff", "@@ -0,0 +1 @@\n+new\n"),
        )

    def test_schema_v2_full_replacement_replays_to_expected_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "source.md"
            target.write_text("before\n", encoding="utf-8")
            after = b"after\n"
            patch = {
                "patch_id": "p1",
                "owner": "author",
                "surface": "document_metadata",
                "target_path": "source.md",
                "baseline_digest": "sha256:" + hashlib.sha256(b"before\n").hexdigest(),
                "exact_patch": "after\n",
                "patch_format": "full_replacement",
                "patch_body": "after\n",
                "expected_after_digest": "sha256:" + hashlib.sha256(after).hexdigest(),
                "baseline_content": "before\n",
                "required": True,
            }

            result = validate_transaction_evidence(
                {"schema_version": 2, "surface_patches": [patch],
                 "input_deltas": [self._v2_delta(patch)],
                 "attestations": [], "apply_results": []},
                root=root,
                mutations=(),
            )

        self.assertEqual((), result.diagnostics)

    def test_schema_v2_rejects_descriptive_or_mismatched_patch_body(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "source.md").write_text("before\n", encoding="utf-8")
            patch = {
                "patch_id": "p1",
                "owner": "author",
                "surface": "document_metadata",
                "target_path": "source.md",
                "baseline_digest": "sha256:" + hashlib.sha256(b"before\n").hexdigest(),
                "exact_patch": "description only",
                "patch_format": "full_replacement",
                "patch_body": "different body",
                "expected_after_digest": "sha256:" + "0" * 64,
                "baseline_content": "before\n",
                "required": True,
            }

            result = validate_transaction_evidence(
                {"schema_version": 2, "surface_patches": [patch],
                 "attestations": [], "apply_results": []},
                root=root,
                mutations=(),
            )

        codes = [item.code for item in result.diagnostics]
        self.assertIn("patch_body_alias_mismatch", codes)
        self.assertIn("patch_replay_mismatch", codes)
    def test_non_array_collection_stops_evidence_collection(self):
        result = validate_transaction_evidence(
            {
                "surface_patches": {},
                "attestations": [],
                "apply_results": [],
            },
            root=None,
            mutations=(),
        )

        self.assertIsNone(result.evidence)
        self.assertEqual(
            ["transaction_collection_invalid"],
            [item.code for item in result.diagnostics],
        )

    def test_valid_evidence_is_collected_in_immutable_sets(self):
        patch = {
            "patch_id": "p1",
            "owner": "main",
            "surface": "code_anchor",
            "target_path": "src/example.py",
            "exact_patch": "replace symbol",
            "required": True,
            "baseline_digest": "absent",
        }
        result = validate_transaction_evidence(
            {
                "surface_patches": [patch],
                "attestations": [{
                    "patch_id": "p1",
                    "owner": "main",
                    "decision": "confirm",
                    "evidence": "reviewed",
                }],
                "apply_results": [{
                    "patch_id": "p1",
                    "result": "applied",
                    "resulting_digest": "sha256:" + "0" * 64,
                    "evidence": "written",
                }],
            },
            root=None,
            mutations=(),
        )

        self.assertEqual((), result.diagnostics)
        self.assertEqual(frozenset({"p1"}), result.evidence.required_patch_ids)
        self.assertEqual(frozenset({"p1"}), result.evidence.confirmed_patch_ids)
        self.assertEqual(frozenset({"p1"}), result.evidence.applied_patch_ids)

    def test_patch_attestation_and_result_diagnostics_keep_source_order(self):
        result = validate_transaction_evidence(
            {
                "surface_patches": ["bad patch"],
                "attestations": ["bad attestation"],
                "apply_results": ["bad result"],
            },
            root=None,
            mutations=(),
        )

        self.assertEqual(
            ["surface_patch_invalid", "attestation_invalid", "apply_result_invalid"],
            [item.code for item in result.diagnostics],
        )

    def test_applied_optional_patch_requires_owner_confirmation(self):
        patch = self._v2_patch(
            "p-optional", "optional.md", "before\n", "after\n", required=False
        )
        result = validate_transaction_evidence(
            {
                "schema_version": 2,
                "surface_patches": [patch],
                "attestations": [],
                "apply_results": [{
                    "patch_id": patch["patch_id"],
                    "result": "applied",
                    "resulting_digest": patch["expected_after_digest"],
                    "evidence": "written",
                }],
            },
            root=None,
            mutations=(),
        )

        self.assertIn(
            "applied_patch_confirmation_missing",
            {item.code for item in result.diagnostics},
        )

    def test_confirmed_optional_patch_closes_against_current_source_bytes(self):
        patch = self._v2_patch(
            "p-optional", "optional.md", "before\n", "after\n", required=False
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "optional.md").write_text("after\n", encoding="utf-8")
            result = validate_transaction_evidence(
                {
                    "schema_version": 2,
                    "surface_patches": [patch],
                    "input_deltas": [self._v2_delta(patch)],
                    "attestations": [{
                        "patch_id": patch["patch_id"],
                        "owner": patch["owner"],
                        "decision": "confirm",
                        "evidence": "owner confirmed",
                    }],
                    "apply_results": [{
                        "patch_id": patch["patch_id"],
                        "result": "applied",
                        "resulting_digest": patch["expected_after_digest"],
                        "evidence": "written",
                    }],
                },
                root=root,
                mutations=(),
            )

        self.assertEqual((), result.diagnostics)

    def test_schema_v1_optional_application_keeps_historical_read_compatibility(self):
        patch = {
            "patch_id": "p-legacy-optional",
            "owner": "main",
            "surface": "code_anchor",
            "target_path": "src/example.py",
            "baseline_digest": "absent",
            "exact_patch": "legacy patch description",
            "required": False,
        }
        result = validate_transaction_evidence(
            {
                "schema_version": 1,
                "surface_patches": [patch],
                "attestations": [],
                "apply_results": [{
                    "patch_id": patch["patch_id"],
                    "result": "applied",
                    "resulting_digest": "sha256:" + "0" * 64,
                    "evidence": "historical application receipt",
                }],
            },
            root=None,
            mutations=(),
        )

        self.assertNotIn(
            "applied_patch_confirmation_missing",
            {item.code for item in result.diagnostics},
        )

    def test_unconfirmed_unapplied_optional_patch_drift_is_nonblocking(self):
        patch = self._v2_patch(
            "p-optional", "optional.md", "before\n", "after\n", required=False
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "optional.md").write_text("changed elsewhere\n", encoding="utf-8")
            result = validate_transaction_evidence(
                {
                    "schema_version": 2,
                    "state": "verified",
                    "surface_patches": [patch],
                    "input_deltas": [self._v2_delta(patch)],
                    "attestations": [],
                    "apply_results": [],
                },
                root=root,
                mutations=(),
            )

        self.assertNotIn(
            "unapplied_patch_baseline_mismatch",
            {item.code for item in result.diagnostics},
        )

    def test_schema_v2_mutation_requires_required_owner_patch_and_rejects_optional_owner(self):
        mutation = {
            "operation": "add",
            "entity": "node",
            "before": None,
            "after": {
                "id": "key.capability.example",
                "kind": "capability",
                "artifact_kind": "none",
                "locator": {"path": "source.md"},
                "lifecycle": "active",
                "lifecycle_domain": "document",
                "provenance": {"produced_from": [], "governed_by": []},
            },
            "evidence": "declared",
            "direct_relation_reason": None,
        }
        optional = self._v2_patch(
            "p-optional", "source.md", "before\n", "after\n", required=False
        )
        required = self._v2_patch(
            "p-required", "other.md", "old\n", "new\n", required=True
        )
        result = validate_transaction_evidence(
            {
                "schema_version": 2,
                "surface_patches": [optional, required],
                "attestations": [],
                "apply_results": [],
            },
            root=None,
            mutations=(mutation,),
        )

        self.assertTrue({
            "mutation_required_patch_missing",
            "mutation_optional_patch_forbidden",
        } <= {item.code for item in result.diagnostics})


if __name__ == "__main__":
    unittest.main()
