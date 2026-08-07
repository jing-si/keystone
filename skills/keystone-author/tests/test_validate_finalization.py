import json
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_finalization.py"
RUNNER = Path(__file__).parents[1] / "scripts" / "run_finalization_validation.py"
REPOSITORY_ROOT = Path(__file__).parents[3]
INSTALLER = REPOSITORY_ROOT / "reinstall-local-keystone-skills.sh"
REQUIRED_CATEGORIES = [
    "progress",
    "work_order_change_set",
    "work_index",
    "round_index",
    "root_index",
    "context_map",
    "standard_decision_plan",
    "recovery",
    "implementation_gate",
    "residual_risk",
    "namespace",
]


class FinalizationValidatorCliTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "docs").mkdir()
        (self.root / "docs" / "s02.md").write_text(
            "---\nwork_status: accepted\nstep_ref: R004/S02\n"
            "work_ref: R004/finalization-runtime-validator\n"
            "finalization:\n  state: in_progress\n"
            "  acceptance_ref: R004/S02/main-acceptance\n"
            "---\n# S02\n",
            encoding="utf-8",
        )
        (self.root / "docs" / "round.md").write_text(
            "# Round\n\nActive steps: []\n", encoding="utf-8"
        )
        (self.root / "docs" / "work-index.md").write_text(
            "# Work\n\nActive steps: []\n", encoding="utf-8"
        )
        (self.root / "docs" / "context-map.md").write_text(
            "# Context\n\nActive steps: []\n", encoding="utf-8"
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def valid_manifest(self):
        manifest = {
            "schema_version": 1,
            "acceptance_ref": "R004/S02/main-acceptance",
            "steps": [
                {
                    "ref": "R004/S02",
                    "work_ref": "R004/finalization-runtime-validator",
                    "status": "accepted",
                    "progress_path": "docs/s02.md",
                }
            ],
            "accepted_steps": ["R004/S02"],
            "status_transitions": [
                {"ref": "R004/S02", "from": "in_progress", "to": "accepted", "kind": "step"}
            ],
            "active_steps": [],
            "active_step_sources": [
                {"category": "work_index", "path": "docs/work-index.md"},
                {"category": "round_index", "path": "docs/round.md"},
                {"category": "context_map", "path": "docs/context-map.md"},
            ],
            "early_work": [],
            "finalization": {
                "required": True,
                "state": "in_progress",
                "progress_path": "docs/s02.md",
                "evidence": ["main_acceptance", "impact_dispositions", "source_updates", "semantic_review"],
            },
            "impact_candidates": [
                {
                    "category": category,
                    "artifact": category,
                    "path": "docs/round.md",
                    "disposition": "no_change_required",
                    "reason": f"{category} was evaluated for this fixture.",
                }
                for category in REQUIRED_CATEGORIES
            ],
            "namespace_entries": [],
        }

        for candidate in manifest["impact_candidates"]:
            if candidate["category"] == "implementation_gate":
                candidate.update(gate_state="resolved", gate_scope="R004/S02 implementation")
            elif candidate["category"] == "residual_risk":
                candidate.update(risk_state="none", risk_items=[])
            elif candidate["category"] == "namespace":
                candidate.update(namespace_state="checked")
        return manifest

    def run_validator(self, manifest, *extra_args):
        manifest_path = self.root / "manifest.json"
        if manifest is not None:
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        process = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--root",
                str(self.root),
                "--manifest",
                str(manifest_path),
                *extra_args,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(process.stdout) if process.stdout else None
        return process, payload

    def verified_graph_transaction(self):
        raw = b"---\nkey: {id: key.doc, kind: source_document}\n---\n"
        (self.root / "source.md").write_bytes(raw)
        node = {
            "id": "key.doc", "kind": "source_document", "artifact_kind": "none",
            "locator": {"path": "source.md"}, "lifecycle": "active",
            "provenance": {"produced_from": [], "governed_by": [],
                           "surface": "document_metadata", "locator": {"path": "source.md"}},
        }
        return {
            "schema_version": 1, "transaction_id": "tx-finalization", "scope_ref": "R005/S03",
            "state": "verified", "input_deltas": [], "coverage_debt": [],
            "canonical_mutations": [{"operation": "add", "entity": "node", "before": None,
                                      "after": node, "evidence": "declared"}],
            "surface_patches": [{"patch_id": "p", "owner": "author", "surface": "document_metadata",
                                  "target_path": "source.md", "baseline_digest": "absent",
                                  "exact_patch": "add", "required": True}],
            "attestations": [{"patch_id": "p", "owner": "author", "decision": "confirm",
                              "evidence": "reviewed"}],
            "apply_results": [{"patch_id": "p", "result": "applied",
                               "resulting_digest": "sha256:" + hashlib.sha256(raw).hexdigest(),
                               "evidence": "applied"}],
            "reconstruction": {
                "baseline": {"schema_version": 1, "nodes": [], "relations": []},
                "result": {"schema_version": 1, "nodes": [node], "relations": []},
            },
            "mechanical_validation": {"schema_version": 1, "status": "pass", "diagnostics": [],
                                      "summary": {"errors": 0, "warnings": 0}},
        }

    def graph_complete_manifest(self, transaction):
        graph_path = self.root / "graph-validation.json"
        graph_path.write_text(json.dumps({"schema_version": 1, "sources": ["source.md"],
                                          "transaction": transaction}), encoding="utf-8")
        manifest = self.valid_manifest()
        self.upgrade_to_v3(manifest)
        manifest["finalization"]["state"] = "complete"
        manifest["finalization"]["evidence"].append("post_edit_verification")
        source = self.root / "docs" / "s02.md"
        source.write_text(source.read_text(encoding="utf-8").replace(
            "state: in_progress", "state: complete"), encoding="utf-8")
        manifest["graph_sync"] = {
            "required": True, "disposition": "required", "reason": "Metadata changed.",
            "validation_manifest_path": "graph-validation.json",
            "transaction_id": transaction["transaction_id"],
        }
        return manifest

    def upgrade_to_v3(self, manifest):
        manifest["schema_version"] = 3
        manifest["steps"][0].update(status="complete", approval_state="accepted")
        manifest.pop("status_transitions", None)
        manifest["execution_transitions"] = [
            {"ref": "R004/S02", "from": "in_progress", "to": "complete"}
        ]
        manifest["approval_transitions"] = [
            {"ref": "R004/S02", "from": "pending", "to": "accepted",
             "evidence": "R004/S02/main-acceptance"}
        ]
        for candidate in manifest["impact_candidates"]:
            if candidate["disposition"] == "no_change_required":
                candidate["disposition"] = "no_change"
        source = self.root / "docs" / "s02.md"
        content = source.read_text(encoding="utf-8")
        content = content.replace("work_status: accepted", "work_status: complete")
        if "approval:" not in content:
            content = content.replace(
                "work_status: complete\n",
                "work_status: complete\napproval:\n  state: accepted\n",
            )
        source.write_text(content, encoding="utf-8")
        return manifest

    def upgrade_to_v4(self, manifest):
        self.upgrade_to_v3(manifest)
        manifest["schema_version"] = 4
        manifest["steps"][0].update(
            finalization_state="in_progress",
            finalization_acceptance_ref="R004/S02/main-acceptance",
        )
        source_specs = [
            ("work_index", "docs/work-index.md", "key.work.index"),
            ("round_index", "docs/round.md", "key.round.index"),
            ("root_index", "docs/root-index.md", "key.root.index"),
            ("context_map", "docs/context-map.md", "key.context-map"),
        ]
        for _, path, key_id in source_specs:
            (self.root / path).write_text(
                "---\n"
                f"key: {{id: {key_id}}}\n"
                "global_state:\n"
                "  active_round: R004\n"
                "  latest_accepted_round: R003\n"
                "  active_steps: []\n"
                "---\n# State\n",
                encoding="utf-8",
            )
        manifest["global_state"] = {
            "active_round": "R004",
            "latest_accepted_round": "R003",
            "active_steps": [],
            "sources": [
                {"category": category, "path": path, "key_id": key_id}
                for category, path, key_id in source_specs
            ],
        }
        return manifest

    def upgrade_to_v5(self, manifest):
        self.upgrade_to_v4(manifest)
        manifest["schema_version"] = 5
        source_specs = [
            (
                "work_index", "docs/r004-fixture/work/00_key-index.md", "work",
                "key.work.fixture.index", "event_round",
            ),
            (
                "round_index", "docs/r004-fixture/00_key-index.md", "work_round",
                "key.work.round.r004-fixture.index", "event_round",
            ),
            (
                "root_index", "docs/root-index.md", "work_round_index",
                "key.work.index", "global",
            ),
            (
                "context_map", "docs/context-map.md", "context_map",
                "key.context-map", "global",
            ),
        ]
        for category, path, doc_type, key_id, round_role in source_specs:
            source_path = self.root / path
            source_path.parent.mkdir(parents=True, exist_ok=True)
            status = (
                "work_status: complete\n" if category == "work_index"
                else "round_status: active\n" if category == "round_index"
                else ""
            )
            source_path.write_text(
                "---\n"
                f"doc_type: {doc_type}\n"
                f"{status}"
                f"key: {{id: {key_id}}}\n"
                "global_state:\n"
                "  active_round: R004\n"
                "  latest_accepted_round: R003\n"
                "  active_steps: []\n"
                "---\n# State\n",
                encoding="utf-8",
            )
        manifest["global_state"]["sources"] = [
            {
                "category": category,
                "path": path,
                "key_id": key_id,
            }
            for category, path, _doc_type, key_id, _round_role in source_specs
        ]
        accepted_round = self.root / "docs" / "r003-accepted" / "00_key-index.md"
        accepted_round.parent.mkdir(parents=True, exist_ok=True)
        accepted_round.write_text(
            "---\n"
            "doc_type: work_round\n"
            "round_status: accepted\n"
            "key: {id: key.work.round.r003-accepted.index}\n"
            "---\n# Accepted Round\n",
            encoding="utf-8",
        )
        return manifest

    def run_finalization_runner(self, manifest):
        manifest_path = self.root / "manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        process = subprocess.run(
            [sys.executable, str(RUNNER), "--root", str(self.root), "--manifest", str(manifest_path)],
            capture_output=True, text=True, check=False,
        )
        return process, json.loads(process.stdout) if process.stdout else None

    def assert_diagnostic(self, payload, code):
        self.assertIn(code, [item["code"] for item in payload["diagnostics"]])

    # keystone: id=key.test.author.finalization-validator-contract kind=output_artifact artifact_kind=test verifies=key.code.author.finalization-validator locator.test_name=test_valid_manifest_returns_machine_readable_pass
    def test_valid_manifest_returns_machine_readable_pass(self):
        process, payload = self.run_validator(self.valid_manifest())

        self.assertEqual(0, process.returncode)
        self.assertEqual("pass", payload["status"])
        self.assertEqual([], payload["diagnostics"])
        self.assertEqual({"errors": 0, "warnings": 0}, payload["summary"])

    def test_missing_manifest_is_an_invocation_error(self):
        process, payload = self.run_validator(None)

        self.assertEqual(2, process.returncode)
        self.assertEqual("error", payload["status"])
        self.assert_diagnostic(payload, "manifest_unavailable")

    def test_invalid_manifest_json_is_an_invocation_error(self):
        manifest_path = self.root / "manifest.json"
        manifest_path.write_text("{broken", encoding="utf-8")

        process = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root), "--manifest", str(manifest_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(process.stdout) if process.stdout else None

        self.assertEqual(2, process.returncode)
        self.assert_diagnostic(payload, "manifest_invalid_json")

    def test_duplicate_manifest_key_is_an_invocation_error(self):
        manifest_path = self.root / "manifest.json"
        raw = json.dumps(self.valid_manifest())
        raw = raw.replace(
            '{"schema_version": 1,',
            '{"schema_version": 999, "schema_version": 1,',
            1,
        )
        manifest_path.write_text(raw, encoding="utf-8")

        process = subprocess.run(
            [
                sys.executable, str(SCRIPT), "--root", str(self.root),
                "--manifest", str(manifest_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(process.stdout)

        self.assertEqual(2, process.returncode)
        self.assert_diagnostic(payload, "manifest_invalid_json")

    def test_active_step_must_resolve_to_a_declared_active_status_step(self):
        manifest = self.valid_manifest()
        manifest["active_steps"] = ["R004/S99"]

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "active_step_unresolved")

    def test_duplicate_active_step_is_rejected(self):
        manifest = self.valid_manifest()
        manifest["active_steps"] = ["R004/S99", "R004/S99"]

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "active_step_duplicate")

    def test_active_step_with_completed_status_is_rejected(self):
        manifest = self.valid_manifest()
        manifest["active_steps"] = ["R004/S02"]

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "active_step_status_invalid")

    def test_early_work_requires_no_status_effect_and_traceable_scope(self):
        manifest = self.valid_manifest()
        manifest["steps"].append(
            {
                "ref": "R004/S03",
                "work_ref": "R004/finalization-integration-verification",
                "status": "planned",
                "progress_path": "docs/s02.md",
        }
        )
        manifest["early_work"] = [
            {
                "target_step": "R004/S03",
                "cause": "S02 fixture needed an integration sample.",
                "completed_scope": ["sample manifest"],
                "remaining_scope": ["integration verification"],
                "status_effect": "in_progress",
            }
        ]

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "early_work_status_effect_invalid")

    def test_candidate_requires_disposition_reason_and_existing_scoped_path(self):
        manifest = self.valid_manifest()
        manifest["impact_candidates"][0].update(path="docs/missing.md", reason="")

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "candidate_reason_missing")
        self.assert_diagnostic(payload, "candidate_path_unavailable")

    def test_stale_singular_current_step_claim_is_rejected_on_live_candidate(self):
        stale = self.root / "docs" / "stale.md"
        stale.write_text("# Recovery\n\n현재 단계: S01\n", encoding="utf-8")
        manifest = self.valid_manifest()
        manifest["impact_candidates"].append(
            {
                "category": "recovery",
                "artifact": "recovery instructions",
                "path": "docs/stale.md",
                "disposition": "updated",
                "reason": "Recovery state must match active steps.",
            }
        )

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "singular_current_step_claim")

    def test_historical_candidate_allows_past_current_step_wording(self):
        historical = self.root / "docs" / "history.md"
        historical.write_text("# Old report\n\n현재 단계: S01\n", encoding="utf-8")
        manifest = self.valid_manifest()
        manifest["impact_candidates"].append(
            {
                "category": "recovery",
                "artifact": "historical report",
                "path": "docs/history.md",
                "disposition": "historical",
                "reason": "Immutable execution history is intentionally preserved.",
            }
        )

        process, payload = self.run_validator(manifest)

        self.assertEqual(0, process.returncode)
        self.assertEqual("pass", payload["status"])

    def test_namespace_collision_between_owners_is_rejected(self):
        manifest = self.valid_manifest()
        manifest["namespace_entries"] = [
            {"namespace": "flyway", "value": "V12", "owner": "R008"},
            {"namespace": "flyway", "value": "V12", "owner": "R010"},
        ]

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "namespace_collision")

    def test_paths_cannot_escape_the_declared_root(self):
        manifest = self.valid_manifest()
        manifest["impact_candidates"][0]["path"] = "../outside.md"

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "candidate_path_outside_root")

    def test_manifest_step_status_must_match_progress_frontmatter(self):
        manifest = self.valid_manifest()
        manifest["steps"][0]["status"] = "in_progress"

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "step_status_source_mismatch")

    def test_body_examples_cannot_override_progress_frontmatter_state(self):
        manifest = self.valid_manifest()
        source = self.root / "docs" / "s02.md"
        source.write_text(
            source.read_text(encoding="utf-8")
            + "\n```yaml\nwork_status: complete\napproval: {state: accepted}\n"
              "finalization: {state: complete, acceptance_ref: forged}\n```\n",
            encoding="utf-8",
        )

        process, payload = self.run_validator(manifest)

        self.assertEqual(0, process.returncode, payload)

    def test_schema_v4_global_state_matches_distinct_typed_sources(self):
        manifest = self.valid_manifest()
        self.upgrade_to_v4(manifest)
        manifest["graph_sync"] = {
            "required": False,
            "disposition": "not_applicable",
            "reason": "No graph mutation.",
        }

        process, payload = self.run_validator(manifest)

        self.assertEqual(0, process.returncode, payload)

    def test_schema_v5_accepts_strict_category_identity_and_round_roles(self):
        manifest = self.valid_manifest()
        self.upgrade_to_v5(manifest)
        manifest["graph_sync"] = {
            "required": False,
            "disposition": "not_applicable",
            "reason": "No graph mutation.",
        }

        process, payload = self.run_validator(manifest)

        self.assertEqual(0, process.returncode, payload)

    def test_schema_v5_live_state_requires_one_accepted_latest_round_index(self):
        manifest = self.valid_manifest()
        self.upgrade_to_v5(manifest)
        manifest["graph_sync"] = {
            "required": False,
            "disposition": "not_applicable",
            "reason": "No graph mutation.",
        }
        latest = self.root / "docs" / "r003-accepted" / "00_key-index.md"
        latest.write_text(
            latest.read_text(encoding="utf-8").replace(
                "round_status: accepted", "round_status: active"
            ),
            encoding="utf-8",
        )

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "latest_accepted_round_status_invalid")

        latest.unlink()
        manifest["global_state"]["latest_accepted_round"] = "R002"
        for source in manifest["global_state"]["sources"]:
            path = self.root / source["path"]
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "latest_accepted_round: R003",
                    "latest_accepted_round: R002",
                ),
                encoding="utf-8",
            )
        process, payload = self.run_validator(manifest)
        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "latest_accepted_round_index_unresolved")

    def test_schema_v5_rejects_ambiguous_latest_round_indexes(self):
        manifest = self.valid_manifest()
        self.upgrade_to_v5(manifest)
        manifest["graph_sync"] = {
            "required": False,
            "disposition": "not_applicable",
            "reason": "No graph mutation.",
        }
        duplicate = self.root / "docs" / "r003-duplicate" / "00_key-index.md"
        duplicate.parent.mkdir(parents=True)
        duplicate.write_text(
            "---\n"
            "doc_type: work_round\n"
            "round_status: accepted\n"
            "key: {id: key.work.round.r003-duplicate.index}\n"
            "---\n# Duplicate Round\n",
            encoding="utf-8",
        )

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "latest_accepted_round_index_ambiguous")

    def test_schema_v5_rejects_active_step_outside_active_round(self):
        manifest = self.valid_manifest()
        self.upgrade_to_v5(manifest)
        manifest["active_steps"] = ["R005/S01"]
        manifest["global_state"]["active_steps"] = ["R005/S01"]
        manifest["graph_sync"] = {
            "required": False,
            "disposition": "not_applicable",
            "reason": "No graph mutation.",
        }

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "active_step_round_mismatch")

    def test_schema_v5_terminal_state_uses_accepted_step_event_round(self):
        manifest = self.valid_manifest()
        self.upgrade_to_v5(manifest)
        manifest["global_state"].update(
            active_round="none",
            latest_accepted_round="R004",
        )
        for source in manifest["global_state"]["sources"]:
            path = self.root / source["path"]
            path.write_text(
                path.read_text(encoding="utf-8")
                .replace("active_round: R004", "active_round: none")
                .replace("latest_accepted_round: R003", "latest_accepted_round: R004")
                .replace("round_status: active", "round_status: accepted"),
                encoding="utf-8",
            )
        manifest["graph_sync"] = {
            "required": False,
            "disposition": "not_applicable",
            "reason": "No graph mutation.",
        }

        process, payload = self.run_validator(manifest)

        self.assertEqual(0, process.returncode, payload)

    def test_schema_v5_terminal_state_rejects_other_active_work_index(self):
        manifest = self.valid_manifest()
        self.upgrade_to_v5(manifest)
        manifest["global_state"].update(
            active_round="none",
            latest_accepted_round="R004",
        )
        for source in manifest["global_state"]["sources"]:
            path = self.root / source["path"]
            path.write_text(
                path.read_text(encoding="utf-8")
                .replace("active_round: R004", "active_round: none")
                .replace("latest_accepted_round: R003", "latest_accepted_round: R004")
                .replace("round_status: active", "round_status: accepted"),
                encoding="utf-8",
            )
        other_work = (
            self.root / "docs" / "r005-other" / "active-work" / "00_key-index.md"
        )
        other_work.parent.mkdir(parents=True)
        other_work.write_text(
            "---\n"
            "doc_type: work\n"
            "work_status: in_progress\n"
            "key: {id: key.work.other-active.index}\n"
            "---\n# Other Active Work\n",
            encoding="utf-8",
        )
        distractor = (
            self.root / "docs" / "r005-other" / "progress" / "00_key-index.md"
        )
        distractor.parent.mkdir(parents=True)
        distractor.write_text(
            "---\n"
            "doc_type: progress\n"
            "work_status: in_progress\n"
            "key: {id: key.work.progress-lookalike.index}\n"
            "---\n# Not a Work Index\n",
            encoding="utf-8",
        )
        manifest["graph_sync"] = {
            "required": False,
            "disposition": "not_applicable",
            "reason": "No graph mutation.",
        }

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "terminal_active_work_remaining")

    def test_schema_v5_rejects_mixed_accepted_event_rounds(self):
        manifest = self.valid_manifest()
        self.upgrade_to_v5(manifest)
        manifest["accepted_steps"].append("R005/S03")
        manifest["steps"].append({"ref": "R005/S03"})
        manifest["graph_sync"] = {
            "required": False,
            "disposition": "not_applicable",
            "reason": "No graph mutation.",
        }

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "accepted_step_event_round_invalid")

    def test_schema_v5_rejects_round_status_semantic_drift(self):
        manifest = self.valid_manifest()
        self.upgrade_to_v5(manifest)
        manifest["graph_sync"] = {
            "required": False,
            "disposition": "not_applicable",
            "reason": "No graph mutation.",
        }
        round_path = self.root / manifest["global_state"]["sources"][1]["path"]
        round_path.write_text(
            round_path.read_text(encoding="utf-8").replace(
                "round_status: active", "round_status: accepted"
            ),
            encoding="utf-8",
        )

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "round_status_semantics_invalid")

    def test_schema_v5_rejects_category_doc_type_key_and_round_role_lies(self):
        manifest = self.valid_manifest()
        self.upgrade_to_v5(manifest)
        manifest["graph_sync"] = {
            "required": False,
            "disposition": "not_applicable",
            "reason": "No graph mutation.",
        }
        work_source = manifest["global_state"]["sources"][0]
        path = self.root / work_source["path"]
        misleading = self.root / "docs" / "work-v5.md"
        misleading.write_text(
            path.read_text(encoding="utf-8")
            .replace("doc_type: work", "doc_type: context_map")
            .replace("key.work.fixture.index", "key.context-map"),
            encoding="utf-8",
        )
        work_source["path"] = "docs/work-v5.md"
        work_source["key_id"] = "key.context-map"

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "global_state_source_doc_type_mismatch")
        self.assert_diagnostic(payload, "global_state_source_key_semantics_invalid")
        self.assert_diagnostic(payload, "global_state_source_round_role_invalid")

    def test_schema_v5_rejects_duplicate_frontmatter_semantics(self):
        manifest = self.valid_manifest()
        self.upgrade_to_v5(manifest)
        manifest["graph_sync"] = {
            "required": False,
            "disposition": "not_applicable",
            "reason": "No graph mutation.",
        }
        round_path = self.root / manifest["global_state"]["sources"][1]["path"]
        round_path.write_text(
            round_path.read_text(encoding="utf-8")
            .replace(
                "doc_type: work_round\n",
                "doc_type: work_round\ndoc_type: context_map\n",
            )
            .replace(
                "round_status: active\n",
                "round_status: active\nround_status: accepted\n",
            ),
            encoding="utf-8",
        )

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "global_state_source_doc_type_mismatch")
        self.assert_diagnostic(payload, "round_status_semantics_invalid")

    def test_schema_v5_rejects_mixed_mapping_frontmatter_semantics(self):
        manifest = self.valid_manifest()
        self.upgrade_to_v5(manifest)
        manifest["graph_sync"] = {
            "required": False,
            "disposition": "not_applicable",
            "reason": "No graph mutation.",
        }
        round_path = self.root / manifest["global_state"]["sources"][1]["path"]
        round_path.write_text(
            round_path.read_text(encoding="utf-8").replace(
                "key: {id: key.work.round.r004-fixture.index}\n",
                "key:\n"
                "  id: key.work.round.r004-fixture.index\n"
                "key: {id: key.context-map}\n",
            ),
            encoding="utf-8",
        )

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "global_state_source_key_semantics_invalid")

    def test_schema_v5_round_roles_use_canonical_resolved_paths(self):
        manifest = self.valid_manifest()
        self.upgrade_to_v5(manifest)
        manifest["graph_sync"] = {
            "required": False,
            "disposition": "not_applicable",
            "reason": "No graph mutation.",
        }
        work_source = manifest["global_state"]["sources"][0]
        original = self.root / work_source["path"]
        outside = self.root / "docs" / "forged-work.md"
        outside.write_bytes(original.read_bytes())
        work_source["path"] = "docs/r004-fixture/../forged-work.md"

        alias_process, alias_payload = self.run_validator(manifest)

        self.assertEqual(1, alias_process.returncode)
        self.assert_diagnostic(alias_payload, "global_state_source_unavailable")

        link = self.root / "docs" / "r004-fixture" / "linked-work.md"
        link.symlink_to(outside)
        work_source["path"] = "docs/r004-fixture/linked-work.md"

        link_process, link_payload = self.run_validator(manifest)

        self.assertEqual(1, link_process.returncode)
        self.assert_diagnostic(link_payload, "global_state_source_round_role_invalid")

    def test_schema_v4_represents_no_active_round_only_with_no_active_steps(self):
        manifest = self.valid_manifest()
        self.upgrade_to_v4(manifest)
        manifest["graph_sync"] = {
            "required": False,
            "disposition": "not_applicable",
            "reason": "No graph mutation.",
        }
        manifest["global_state"]["active_round"] = "none"
        for source in manifest["global_state"]["sources"]:
            path = self.root / source["path"]
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "active_round: R004", "active_round: none"
                ),
                encoding="utf-8",
            )

        process, payload = self.run_validator(manifest)
        self.assertEqual(0, process.returncode, payload)

        manifest["active_steps"] = ["R004/S02"]
        manifest["global_state"]["active_steps"] = ["R004/S02"]
        process, payload = self.run_validator(manifest)
        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "global_state_active_round_mismatch")

    def test_schema_v4_rejects_global_state_mismatch_and_body_override(self):
        manifest = self.valid_manifest()
        self.upgrade_to_v4(manifest)
        manifest["graph_sync"] = {
            "required": False,
            "disposition": "not_applicable",
            "reason": "No graph mutation.",
        }
        source = self.root / "docs" / "context-map.md"
        source.write_text(
            source.read_text(encoding="utf-8").replace(
                "latest_accepted_round: R003", "latest_accepted_round: R002"
            )
            + "\n```yaml\nglobal_state: {latest_accepted_round: R003}\n```\n",
            encoding="utf-8",
        )

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "global_state_source_mismatch")

    def test_schema_v4_rejects_duplicate_source_path_and_wrong_key_identity(self):
        manifest = self.valid_manifest()
        self.upgrade_to_v4(manifest)
        manifest["graph_sync"] = {
            "required": False,
            "disposition": "not_applicable",
            "reason": "No graph mutation.",
        }
        manifest["global_state"]["sources"][1]["path"] = "docs/work-index.md"
        manifest["global_state"]["sources"][2]["key_id"] = "key.wrong"

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "global_state_source_path_duplicate")
        self.assert_diagnostic(payload, "global_state_source_key_mismatch")

    def test_complete_multi_step_finalization_checks_every_accepted_progress(self):
        manifest = self.valid_manifest()
        self.upgrade_to_v4(manifest)
        manifest["acceptance_ref"] = "R004/main-acceptance"
        manifest["steps"][0]["finalization_state"] = "complete"
        manifest["steps"][0]["finalization_acceptance_ref"] = "R004/main-acceptance"
        second_path = self.root / "docs" / "s03.md"
        second_path.write_text(
            "---\nwork_status: complete\napproval: {state: accepted}\n"
            "step_ref: R004/S03\nwork_ref: R004/second\n"
            "finalization: {state: in_progress, acceptance_ref: R004/main-acceptance}\n"
            "---\n# S03\n",
            encoding="utf-8",
        )
        manifest["steps"].append({
            "ref": "R004/S03",
            "work_ref": "R004/second",
            "status": "complete",
            "approval_state": "accepted",
            "progress_path": "docs/s03.md",
            "finalization_state": "complete",
            "finalization_acceptance_ref": "R004/main-acceptance",
        })
        manifest["accepted_steps"].append("R004/S03")
        manifest["execution_transitions"].append({
            "ref": "R004/S03", "from": "in_progress", "to": "complete",
        })
        manifest["approval_transitions"].append({
            "ref": "R004/S03", "from": "pending", "to": "accepted",
            "evidence": "R004/S03/main-acceptance",
        })
        manifest["finalization"]["state"] = "complete"
        manifest["finalization"]["evidence"].append("post_edit_verification")
        source = self.root / "docs" / "s02.md"
        source.write_text(
            source.read_text(encoding="utf-8")
            .replace("state: in_progress", "state: complete")
            .replace("R004/S02/main-acceptance", "R004/main-acceptance"),
            encoding="utf-8",
        )
        manifest["graph_sync"] = {
            "required": False,
            "disposition": "not_applicable",
            "reason": "No graph mutation.",
        }

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "accepted_step_finalization_source_mismatch")

        second_path.write_text(
            second_path.read_text(encoding="utf-8").replace(
                "state: in_progress", "state: complete"
            ),
            encoding="utf-8",
        )
        process, payload = self.run_validator(manifest)

        self.assertEqual(0, process.returncode, payload)

    def test_manifest_active_steps_must_match_each_declared_source(self):
        manifest = self.valid_manifest()
        manifest["active_steps"] = ["R004/S99"]

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "active_steps_source_mismatch")

    def test_declared_active_status_step_cannot_be_omitted_from_active_steps(self):
        manifest = self.valid_manifest()
        manifest["steps"][0]["status"] = "in_progress"
        (self.root / "docs" / "s02.md").write_text(
            (self.root / "docs" / "s02.md").read_text(encoding="utf-8").replace(
                "work_status: accepted", "work_status: in_progress"
            ),
            encoding="utf-8",
        )

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "active_step_omitted")

    def test_active_step_sources_require_work_round_and_context_categories(self):
        manifest = self.valid_manifest()
        manifest["active_step_sources"] = manifest["active_step_sources"][:1]

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "active_step_source_category_missing")

    def test_step_work_ownership_must_match_progress_source(self):
        manifest = self.valid_manifest()
        manifest["steps"][0]["work_ref"] = "R004/invented-work"

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "step_work_ref_source_mismatch")

    def test_every_core_impact_category_is_required(self):
        manifest = self.valid_manifest()
        manifest["impact_candidates"] = [
            item for item in manifest["impact_candidates"] if item["category"] != "namespace"
        ]

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "impact_category_missing")

    def test_finalization_state_and_acceptance_ref_must_match_progress(self):
        manifest = self.valid_manifest()
        manifest["finalization"]["state"] = "complete"

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "finalization_state_source_mismatch")

    def test_finalization_requires_core_evidence(self):
        manifest = self.valid_manifest()
        manifest["finalization"]["evidence"] = ["main_acceptance"]

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "finalization_evidence_missing")

    def test_finalization_state_must_be_allowed(self):
        manifest = self.valid_manifest()
        manifest["finalization"]["state"] = "done-ish"
        (self.root / "docs" / "s02.md").write_text(
            (self.root / "docs" / "s02.md").read_text(encoding="utf-8").replace(
                "state: in_progress", "state: done-ish"
            ),
            encoding="utf-8",
        )

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "finalization_state_invalid")

    def test_only_main_accepted_steps_may_have_direct_step_transition(self):
        manifest = self.valid_manifest()
        manifest["status_transitions"].append(
            {"ref": "R004/S03", "from": "planned", "to": "in_progress", "kind": "step"}
        )

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "direct_step_transition_not_accepted")

    def test_every_accepted_step_requires_exact_in_progress_to_accepted_transition(self):
        manifest = self.valid_manifest()
        manifest["status_transitions"][0]["to"] = "complete"

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "direct_step_transition_invalid")

    def test_gate_risk_and_namespace_candidates_require_typed_assessments(self):
        manifest = self.valid_manifest()
        for candidate in manifest["impact_candidates"]:
            if candidate["category"] in {"implementation_gate", "residual_risk", "namespace"}:
                for field in ("gate_state", "gate_scope", "risk_state", "risk_items", "namespace_state"):
                    candidate.pop(field, None)

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "implementation_gate_assessment_invalid")
        self.assert_diagnostic(payload, "residual_risk_assessment_invalid")
        self.assert_diagnostic(payload, "namespace_assessment_invalid")

    def test_invalid_schema_version_fails_closed(self):
        manifest = self.valid_manifest()
        manifest["schema_version"] = 99

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "schema_version_unsupported")

        manifest["schema_version"] = True
        process, payload = self.run_validator(manifest)
        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "schema_version_unsupported")

    def test_schema_v5_rejects_unknown_top_level_field(self):
        manifest = self.valid_manifest()
        self.upgrade_to_v5(manifest)
        manifest["unexpected"] = "must fail closed"

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "manifest_field_unknown")

    def test_schema_v2_requires_graph_sync_assessment(self):
        manifest = self.valid_manifest()
        manifest["schema_version"] = 2

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "graph_sync_missing")

    def test_schema_v1_complete_is_limited_to_r004_compatibility(self):
        manifest = self.valid_manifest()
        manifest["acceptance_ref"] = "R005/S03/main-acceptance"
        manifest["steps"][0]["ref"] = "R005/S03"
        manifest["accepted_steps"] = ["R005/S03"]
        manifest["status_transitions"][0]["ref"] = "R005/S03"
        manifest["finalization"]["state"] = "complete"
        manifest["finalization"]["evidence"].append("post_edit_verification")
        source = (self.root / "docs" / "s02.md")
        source.write_text(
            source.read_text(encoding="utf-8")
            .replace("step_ref: R004/S02", "step_ref: R005/S03")
            .replace("state: in_progress", "state: complete")
            .replace("R004/S02/main-acceptance", "R005/S03/main-acceptance"),
            encoding="utf-8",
        )

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "legacy_schema_complete_forbidden")

    def test_schema_v1_graph_relevant_complete_is_forbidden_even_for_r004(self):
        manifest = self.valid_manifest()
        manifest["finalization"]["state"] = "complete"
        manifest["finalization"]["evidence"].append("post_edit_verification")
        manifest["graph_sync"] = {
            "required": True,
            "disposition": "required",
            "reason": "Graph-relevant metadata changed.",
        }
        source = self.root / "docs" / "s02.md"
        source.write_text(source.read_text(encoding="utf-8").replace(
            "state: in_progress", "state: complete"), encoding="utf-8")

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "legacy_schema_graph_sync_forbidden")

    def test_fresh_schema_v1_r004_prefixed_complete_is_forbidden(self):
        manifest = self.valid_manifest()
        manifest["finalization"]["state"] = "complete"
        manifest["finalization"]["evidence"].append("post_edit_verification")
        source = self.root / "docs" / "s02.md"
        source.write_text(source.read_text(encoding="utf-8").replace(
            "state: in_progress", "state: complete"), encoding="utf-8")

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "legacy_schema_complete_forbidden")

    def test_schema_v1_r004_in_progress_fixture_remains_compatible(self):
        process, payload = self.run_validator(self.valid_manifest())

        self.assertEqual(0, process.returncode, payload)

    def test_graph_sync_not_applicable_is_valid_for_complete_finalization(self):
        manifest = self.valid_manifest()
        self.upgrade_to_v3(manifest)
        manifest["finalization"]["state"] = "complete"
        manifest["finalization"]["evidence"].append("post_edit_verification")
        (self.root / "docs" / "s02.md").write_text(
            (self.root / "docs" / "s02.md").read_text(encoding="utf-8").replace(
                "state: in_progress", "state: complete"
            ), encoding="utf-8")
        manifest["graph_sync"] = {
            "required": False,
            "disposition": "not_applicable",
            "reason": "No graph-relevant source changed.",
        }

        process, payload = self.run_validator(manifest)

        self.assertEqual(0, process.returncode, payload)

    def test_schema_v3_accepts_inline_approval_and_finalization_source_mappings(self):
        manifest = self.valid_manifest()
        self.upgrade_to_v3(manifest)
        manifest["graph_sync"] = {
            "required": False, "disposition": "not_applicable",
            "reason": "No graph-relevant source changed.",
        }
        source = self.root / "docs" / "s02.md"
        content = source.read_text(encoding="utf-8")
        content = content.replace("approval:\n  state: accepted\n", "approval: {state: accepted}\n")
        content = content.replace(
            "finalization:\n  state: in_progress\n  acceptance_ref: R004/S02/main-acceptance\n",
            "finalization: {state: in_progress, acceptance_ref: R004/S02/main-acceptance}\n",
        )
        source.write_text(content, encoding="utf-8")

        process, payload = self.run_validator(manifest)

        self.assertEqual(0, process.returncode, payload)

    def test_complete_required_graph_sync_requires_bound_transaction(self):
        manifest = self.valid_manifest()
        self.upgrade_to_v3(manifest)
        manifest["finalization"]["state"] = "complete"
        manifest["finalization"]["evidence"].append("post_edit_verification")
        (self.root / "docs" / "s02.md").write_text(
            (self.root / "docs" / "s02.md").read_text(encoding="utf-8").replace(
                "state: in_progress", "state: complete"
            ), encoding="utf-8")
        manifest["graph_sync"] = {
            "required": True,
            "disposition": "required",
            "reason": "Document metadata changed.",
        }

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "graph_sync_evidence_missing")

    def test_complete_required_graph_sync_rejects_every_non_verified_state(self):
        for state in ("proposed", "partially_applied", "failed"):
            with self.subTest(state=state):
                transaction = self.verified_graph_transaction()
                transaction["state"] = state
                process, payload = self.run_finalization_runner(self.graph_complete_manifest(transaction))
                self.assertEqual(1, process.returncode)
                self.assert_diagnostic(payload, "graph_sync_transaction_not_verified")

    def test_default_sibling_linker_runner_accepts_only_verified_closure(self):
        transaction = self.verified_graph_transaction()
        process, payload = self.run_finalization_runner(self.graph_complete_manifest(transaction))

        self.assertEqual(0, process.returncode, payload)
        self.assertEqual("pass", payload["status"])

    def test_graph_validation_manifest_rejects_duplicate_json_keys(self):
        transaction = self.verified_graph_transaction()
        manifest = self.graph_complete_manifest(transaction)
        graph_path = self.root / "graph-validation.json"
        raw = graph_path.read_text(encoding="utf-8").replace(
            '"state": "verified"',
            '"state": "failed", "state": "verified"',
            1,
        )
        graph_path.write_text(raw, encoding="utf-8")

        process, payload = self.run_validator(manifest)

        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "graph_sync_evidence_malformed")

    def test_deferred_graph_sync_blocks_complete_but_not_in_progress(self):
        manifest = self.valid_manifest()
        manifest["schema_version"] = 2
        manifest["graph_sync"] = {
            "required": True,
            "disposition": "deferred",
            "reason": "Surface attestation remains pending.",
        }
        process, payload = self.run_validator(manifest)
        self.assertEqual(0, process.returncode, payload)

        manifest["finalization"]["state"] = "complete"
        manifest["finalization"]["evidence"].append("post_edit_verification")
        (self.root / "docs" / "s02.md").write_text(
            (self.root / "docs" / "s02.md").read_text(encoding="utf-8").replace(
                "state: in_progress", "state: complete"
            ), encoding="utf-8")
        process, payload = self.run_validator(manifest)
        self.assertEqual(1, process.returncode)
        self.assert_diagnostic(payload, "graph_sync_deferred")


class FinalizationRunnerCliTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.manifest = self.root / "manifest.json"
        self.manifest.write_text("{}", encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_runner(self, validator):
        process = subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--root",
                str(self.root),
                "--manifest",
                str(self.manifest),
                "--validator",
                str(validator),
                "--timeout-seconds",
                "0.1",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        return process, json.loads(process.stdout) if process.stdout else None

    def run_graph_runner(self, graph_runner, extension=None):
        manifest = {
            "schema_version": 2,
            "graph_sync": {
                "required": True, "disposition": "required", "reason": "metadata changed",
                "validation_manifest_path": "graph.json", "transaction_id": "tx-1",
            },
        }
        self.manifest.write_text(json.dumps(manifest), encoding="utf-8")
        (self.root / "graph.json").write_text(json.dumps({
            "schema_version": 1, "sources": [],
            "transaction": {"transaction_id": "tx-1"},
        }), encoding="utf-8")
        core = self.root / "core.py"
        core.write_text(
            "import json\nprint(json.dumps({'schema_version':1,'status':'pass','diagnostics':[],"
            "'summary':{'errors':0,'warnings':0}}))\n", encoding="utf-8")
        command = [sys.executable, str(RUNNER), "--root", str(self.root), "--manifest",
                   str(self.manifest), "--validator", str(core), "--graph-runner", str(graph_runner),
                   "--timeout-seconds", "0.1"]
        if extension:
            command.extend(("--extension", str(extension)))
        process = subprocess.run(command, capture_output=True, text=True, check=False)
        return process, json.loads(process.stdout) if process.stdout else None

    def test_missing_validator_maps_to_validator_unavailable(self):
        process, payload = self.run_runner(self.root / "missing.py")

        self.assertEqual(2, process.returncode)
        self.assertEqual("validator_unavailable", payload["diagnostics"][0]["code"])

    def test_timeout_maps_to_validator_execution_failed(self):
        slow = self.root / "slow.py"
        slow.write_text("import time\ntime.sleep(1)\n", encoding="utf-8")

        process, payload = self.run_runner(slow)

        self.assertEqual(2, process.returncode)
        self.assertEqual("validator_execution_failed", payload["diagnostics"][0]["code"])

    def test_valid_json_with_invalid_envelope_fails_closed_for_any_exit(self):
        for exit_code in (0, 1, 2):
            with self.subTest(exit_code=exit_code):
                fake = self.root / f"fake-{exit_code}.py"
                fake.write_text(
                    f"import json, sys\nprint(json.dumps(None))\nsys.exit({exit_code})\n",
                    encoding="utf-8",
                )

                process, payload = self.run_runner(fake)

                self.assertEqual(2, process.returncode)
                self.assertEqual("validator_execution_failed", payload["diagnostics"][0]["code"])

    def test_duplicate_key_in_child_envelope_fails_closed(self):
        fake = self.root / "duplicate-envelope.py"
        fake.write_text(
            "print('{\"schema_version\":1,\"status\":\"pass\","
            "\"diagnostics\":[],\"summary\":{\"errors\":9,"
            "\"errors\":0,\"warnings\":0}}')\n",
            encoding="utf-8",
        )

        process, payload = self.run_runner(fake)

        self.assertEqual(2, process.returncode)
        self.assertEqual(
            "validator_execution_failed", payload["diagnostics"][0]["code"]
        )

    def test_duplicate_graph_and_extension_envelopes_fail_closed(self):
        duplicate = (
            "print('{\"schema_version\":1,\"status\":\"pass\","
            "\"diagnostics\":[],\"summary\":{\"errors\":9,"
            "\"errors\":0,\"warnings\":0}}')\n"
        )
        duplicate_graph = self.root / "duplicate-graph.py"
        duplicate_graph.write_text(duplicate, encoding="utf-8")

        process, payload = self.run_graph_runner(duplicate_graph)

        self.assertEqual(2, process.returncode)
        self.assertEqual(
            "graph_validation_output_malformed", payload["diagnostics"][0]["code"]
        )

        passing_graph = self.root / "passing-graph.py"
        passing_graph.write_text(
            "import json\nprint(json.dumps({'schema_version':1,'status':'pass',"
            "'diagnostics':[],'summary':{'errors':0,'warnings':0}}))\n",
            encoding="utf-8",
        )
        duplicate_extension = self.root / "duplicate-extension.py"
        duplicate_extension.write_text(duplicate, encoding="utf-8")

        process, payload = self.run_graph_runner(
            passing_graph, extension=duplicate_extension
        )

        self.assertEqual(2, process.returncode)
        self.assertEqual(
            "validator_execution_failed", payload["diagnostics"][0]["code"]
        )

    def test_malformed_diagnostics_and_summary_fail_closed(self):
        cases = [
            (0, {"status": "pass", "diagnostics": [{"code": "x", "message": "x"}], "summary": {"errors": 0, "warnings": 0}}),
            (1, {"status": "fail", "diagnostics": [], "summary": {"errors": 0, "warnings": 0}}),
            (2, {"status": "error", "diagnostics": [{"severity": "error", "code": "x", "message": "x"}], "summary": {}}),
            (1, {"status": "fail", "diagnostics": [{"severity": "error", "code": "x", "message": "x"}], "summary": {"errors": 0, "warnings": 0}}),
        ]
        for index, (exit_code, envelope) in enumerate(cases):
            with self.subTest(index=index):
                fake = self.root / f"malformed-{index}.py"
                fake.write_text(
                    "import json, sys\n"
                    f"print(json.dumps({envelope!r}))\n"
                    f"sys.exit({exit_code})\n",
                    encoding="utf-8",
                )

                process, payload = self.run_runner(fake)

                self.assertEqual(2, process.returncode)
                self.assertEqual("validator_execution_failed", payload["diagnostics"][0]["code"])

    def test_missing_timeout_and_malformed_graph_runner_are_distinct(self):
        process, payload = self.run_graph_runner(self.root / "missing.py")
        self.assertEqual(2, process.returncode)
        self.assertEqual("graph_validator_unavailable", payload["diagnostics"][0]["code"])

        slow = self.root / "slow-graph.py"
        slow.write_text("import time\ntime.sleep(1)\n", encoding="utf-8")
        process, payload = self.run_graph_runner(slow)
        self.assertEqual(2, process.returncode)
        self.assertEqual("graph_validation_timeout", payload["diagnostics"][0]["code"])

        malformed = self.root / "malformed-graph.py"
        malformed.write_text("print('broken')\n", encoding="utf-8")
        process, payload = self.run_graph_runner(malformed)
        self.assertEqual(2, process.returncode)
        self.assertEqual("graph_validation_output_malformed", payload["diagnostics"][0]["code"])

    def test_graph_failure_prevents_extension_and_preserves_diagnostics(self):
        graph = self.root / "graph.py"
        graph.write_text(
            "import json,sys\nprint(json.dumps({'schema_version':1,'status':'fail',"
            "'diagnostics':[{'severity':'error','code':'verified_apply_missing','message':'missing'}],"
            "'summary':{'errors':1,'warnings':0}}))\nsys.exit(1)\n", encoding="utf-8")
        marker = self.root / "extension-ran"
        extension = self.root / "extension.py"
        extension.write_text(
            f"from pathlib import Path\nPath({str(marker)!r}).write_text('ran')\n", encoding="utf-8")

        process, payload = self.run_graph_runner(graph, extension)

        self.assertEqual(1, process.returncode)
        self.assertIn("verified_apply_missing", [item["code"] for item in payload["diagnostics"]])
        self.assertFalse(marker.exists())


class KeystoneInstallerSmokeTest(unittest.TestCase):
    def test_installer_copies_the_author_validator_with_the_skill(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            process = subprocess.run(
                ["bash", str(INSTALLER)],
                env={"PATH": "/usr/bin:/bin", "CODEX_HOME": temp_dir},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(0, process.returncode, process.stderr)
            self.assertTrue(
                (Path(temp_dir) / "skills" / "keystone-author" / "scripts" / "validate_finalization.py").is_file()
            )
            installed_runner = (
                Path(temp_dir) / "skills" / "keystone-author" / "scripts" / "run_finalization_validation.py"
            )
            smoke = subprocess.run(
                [
                    sys.executable,
                    str(installed_runner),
                    "--root",
                    temp_dir,
                    "--manifest",
                    str(Path(temp_dir) / "missing.json"),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(2, smoke.returncode)
            self.assertEqual("validator_execution_failed",
                             json.loads(smoke.stdout)["diagnostics"][0]["code"])


if __name__ == "__main__":
    unittest.main()
