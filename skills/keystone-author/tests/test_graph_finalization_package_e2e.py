import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from dataclasses import replace
from pathlib import Path


ROOT = Path(__file__).parents[3]
LINKER_SCRIPTS = ROOT / "skills" / "keystone-linker" / "scripts"
sys.path.insert(0, str(LINKER_SCRIPTS))

from graph_runtime.model import (  # noqa: E402
    ApplicationResult, ApplicationStatus, ArtifactKind, AttestationDecision,
    CanonicalMutation, Delta, DeltaKind, Evidence, GraphSnapshot, GraphTransaction, Lifecycle, Locator,
    MutationEntity, MutationOperation, Node, NodeKind, PatchOwner, PatchSurface,
    Provenance, SurfaceAttestation, SurfacePatch, TransactionState, transaction_wire,
)
from graph_runtime.reconciler import (  # noqa: E402
    AttemptHistory, begin_application, begin_attestation, new_attempt, record_application,
    record_attestation, resume_application, finalize_transaction,
)
from graph_runtime.planner import PatchSpec, changed_seed_candidates, plan_graph_sync  # noqa: E402
from graph_runtime.validator import reconstruct, validate_snapshot  # noqa: E402


CATEGORIES = (
    "progress", "work_order_change_set", "work_index", "round_index", "root_index",
    "context_map", "standard_decision_plan", "recovery", "implementation_gate",
    "residual_risk", "namespace",
)


class InstalledGraphFinalizationE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        started = time.monotonic()
        cls.install_dir = tempfile.TemporaryDirectory()
        cls.codex_home = Path(cls.install_dir.name)
        installed_skills = cls.codex_home / "skills"
        (installed_skills / "keystone-reader").mkdir(parents=True)
        (installed_skills / "keystone-reader" / "OLD").write_text("old", encoding="utf-8")
        (installed_skills / "unrelated-skill").mkdir()
        (installed_skills / "unrelated-skill" / "SKILL.md").write_text(
            "unrelated", encoding="utf-8")
        process = subprocess.run(
            ["bash", str(ROOT / "reinstall-local-keystone-skills.sh")],
            cwd=str(ROOT), env=dict(os.environ, CODEX_HOME=str(cls.codex_home)),
            capture_output=True, text=True, check=False,
        )
        if process.returncode:
            raise AssertionError(process.stderr)
        cls.author_runner = (cls.codex_home / "skills" / "keystone-author" / "scripts"
                             / "run_finalization_validation.py")
        cls.linker_runner = (cls.codex_home / "skills" / "keystone-linker" / "scripts"
                             / "run_graph_validation.py")
        cls.reference_runtime = (cls.codex_home / "skills" / "keystone-linker" / "scripts"
                                 / "graph_runtime" / "readiness.py")
        cls.reference_contract = (cls.codex_home / "skills" / "keystone-linker" / "references"
                                  / "reference-index-runtime.md")
        cls.coordinator_skill = cls.codex_home / "skills" / "keystone-coordinator" / "SKILL.md"
        cls.coordinator_validator = (cls.codex_home / "skills" / "keystone-coordinator" / "scripts"
                                     / "validate_closure.py")
        cls.coordinator_reference = (cls.codex_home / "skills" / "keystone-coordinator" / "references"
                                     / "closure-validator.md")
        cls.coordinator_test = (cls.codex_home / "skills" / "keystone-coordinator" / "tests"
                                / "test_validate_closure.py")
        cls.install_seconds = time.monotonic() - started

    @classmethod
    def tearDownClass(cls):
        cls.install_dir.cleanup()

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        (self.root / "docs").mkdir()
        self.progress = self.root / "docs" / "progress.md"
        self.progress.write_text(
            "---\nwork_status: complete\napproval:\n  state: accepted\n"
            "step_ref: R005/S03\nwork_ref: R005/graph-runtime\n"
            "finalization:\n  state: complete\n"
            "  acceptance_ref: R005/S03/main-acceptance\n"
            "---\n# Progress\n", encoding="utf-8")
        for name in ("work-index.md", "round-index.md", "context-map.md", "candidate.md"):
            (self.root / "docs" / name).write_text("# State\n\nActive steps: []\n", encoding="utf-8")

    def tearDown(self):
        self.directory.cleanup()

    def verified_transaction(self):
        raw = b"---\nkey: {id: key.doc, kind: source_document}\n---\n"
        (self.root / "source.md").write_bytes(raw)
        node = Node(
            "key.doc", NodeKind.SOURCE_DOCUMENT, ArtifactKind.NONE, Locator("source.md"),
            Lifecycle.ACTIVE,
            Provenance(surface="document_metadata", locator=Locator("source.md")),
        )
        patch = SurfacePatch("patch-doc", PatchOwner.AUTHOR, PatchSurface.DOCUMENT_METADATA,
                             "source.md", "absent", "add metadata", True)
        transaction = GraphTransaction(
            "tx-installed", "R005/S03",
            canonical_mutations=(CanonicalMutation(
                MutationOperation.ADD, MutationEntity.NODE, None, node, Evidence.DECLARED),),
            surface_patches=(patch,),
            attestations=(SurfaceAttestation(
                patch.patch_id, PatchOwner.AUTHOR, AttestationDecision.CONFIRM, "reviewed"),),
            apply_results=(ApplicationResult(
                patch.patch_id, ApplicationStatus.APPLIED,
                "sha256:" + hashlib.sha256(raw).hexdigest(), "written"),),
            state=TransactionState.VERIFIED,
            reconstruction=GraphSnapshot(nodes=(node,)),
        )
        return transaction_wire(transaction, baseline_snapshot=GraphSnapshot())

    def finalization_manifest(self, transaction):
        graph_path = self.root / "graph-validation.json"
        graph_path.write_text(json.dumps({
            "schema_version": 1, "sources": ["source.md"], "transaction": transaction,
        }), encoding="utf-8")
        candidates = []
        for category in CATEGORIES:
            item = {"category": category, "artifact": category, "path": "docs/candidate.md",
                    "disposition": "no_change", "reason": "evaluated by E2E fixture"}
            if category == "implementation_gate":
                item.update(gate_state="resolved", gate_scope="R005/S03")
            elif category == "residual_risk":
                item.update(risk_state="none", risk_items=[])
            elif category == "namespace":
                item.update(namespace_state="checked")
            candidates.append(item)
        return {
            "schema_version": 3, "acceptance_ref": "R005/S03/main-acceptance",
            "steps": [{"ref": "R005/S03", "work_ref": "R005/graph-runtime",
                       "status": "complete", "approval_state": "accepted",
                       "progress_path": "docs/progress.md"}],
            "accepted_steps": ["R005/S03"],
            "execution_transitions": [
                {"ref": "R005/S03", "from": "in_progress", "to": "complete"}],
            "approval_transitions": [
                {"ref": "R005/S03", "from": "pending", "to": "accepted",
                 "evidence": "R005/S03/main-acceptance"}],
            "active_steps": [],
            "active_step_sources": [
                {"category": "work_index", "path": "docs/work-index.md"},
                {"category": "round_index", "path": "docs/round-index.md"},
                {"category": "context_map", "path": "docs/context-map.md"},
            ],
            "early_work": [],
            "finalization": {"required": True, "state": "complete",
                             "progress_path": "docs/progress.md",
                             "evidence": ["main_acceptance", "impact_dispositions", "source_updates",
                                          "semantic_review", "post_edit_verification"]},
            "graph_sync": {"required": True, "disposition": "required",
                           "reason": "Document graph metadata changed.",
                           "validation_manifest_path": "graph-validation.json",
                           "transaction_id": transaction["transaction_id"]},
            "impact_candidates": candidates, "namespace_entries": [],
        }

    def run_installed(self, manifest):
        manifest_path = self.root / "finalization.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(self.author_runner), "--root", str(self.root),
             "--manifest", str(manifest_path)], capture_output=True, text=True, check=False,
        )

    @staticmethod
    def digest(path):
        return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "absent"

    def execute_production_pipeline(self, initial, final, scope="R005/S04"):
        paths = sorted(set(initial) | set(final))
        for relative, content in initial.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        for relative in set(final) - set(initial):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("", encoding="utf-8")
        baseline, baseline_findings = reconstruct(self.root, paths)
        self.assertEqual((), validate_snapshot(self.root, baseline, baseline_findings))

        golden_dir = tempfile.TemporaryDirectory()
        self.addCleanup(golden_dir.cleanup)
        golden_root = Path(golden_dir.name)
        for relative in paths:
            path = golden_root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(final.get(relative, ""), encoding="utf-8")
        golden, golden_findings = reconstruct(golden_root, paths)
        self.assertEqual((), validate_snapshot(golden_root, golden, golden_findings))

        before_nodes = {node.id: node for node in baseline.nodes}
        after_nodes = {node.id: node for node in golden.nodes}
        before_relations = {(r.source, r.relation, r.target): r for r in baseline.relations}
        after_relations = {(r.source, r.relation, r.target): r for r in golden.relations}
        changed_paths = [relative for relative in paths if initial.get(relative, "") != final.get(relative, "")]
        deltas, specs = [], []
        for relative in changed_paths:
            source_path = self.root / relative
            baseline_digest = self.digest(source_path)
            owner = PatchOwner.AUTHOR if relative.endswith(".md") else PatchOwner.MAIN
            surface = PatchSurface.DOCUMENT_METADATA if owner == PatchOwner.AUTHOR else PatchSurface.CODE_ANCHOR
            deltas.append(Delta(
                DeltaKind.DOCUMENT if owner == PatchOwner.AUTHOR else DeltaKind.ARTIFACT,
                relative, (Locator(relative),), "bounded current source change", baseline_digest, True))
            specs.append(PatchSpec(owner, surface, relative, baseline_digest,
                                   final.get(relative, ""), True))
        transaction = plan_graph_sync(
            baseline, deltas, scope,
            requested_nodes_after=tuple(node for key, node in after_nodes.items()
                                        if before_nodes.get(key) != node),
            requested_node_removals=tuple(key for key in before_nodes if key not in after_nodes),
            requested_relations_after=tuple(rel for key, rel in after_relations.items()
                                            if before_relations.get(key) != rel),
            requested_relation_removals=tuple(key for key in before_relations if key not in after_relations),
            patch_specs=specs,
        )
        current = begin_attestation(transaction)
        for patch in transaction.surface_patches:
            current = record_attestation(current, SurfaceAttestation(
                patch.patch_id, patch.owner, AttestationDecision.CONFIRM, "owner confirmed exact patch"))
        current_digests = {patch.patch_id: self.digest(self.root / patch.target_path)
                           for patch in current.surface_patches}
        current = begin_application(current, current_digests)
        for patch in current.surface_patches:
            target = self.root / patch.target_path
            self.assertEqual(patch.baseline_digest, self.digest(target))
            target.write_text(patch.exact_patch, encoding="utf-8")
            current = record_application(current, ApplicationResult(
                patch.patch_id, ApplicationStatus.APPLIED, self.digest(target), "owner lane applied"))
            if current.state == TransactionState.PARTIALLY_APPLIED:
                current = resume_application(current, {
                    item.patch_id: self.digest(self.root / item.target_path)
                    for item in current.surface_patches})
        reconstructed, parse_findings = reconstruct(self.root, paths)
        mechanical = validate_snapshot(self.root, reconstructed, parse_findings)
        current = finalize_transaction(
            current, reconstructed, mechanical,
            {patch.patch_id: self.digest(self.root / patch.target_path)
             for patch in current.surface_patches}, baseline_snapshot=baseline)
        self.assertEqual(TransactionState.VERIFIED, current.state)
        self.assertEqual(golden, reconstructed)
        wire = transaction_wire(current, baseline_snapshot=baseline)
        graph_manifest = self.root / "pipeline-graph.json"
        graph_manifest.write_text(json.dumps({"schema_version": 1, "sources": paths,
                                              "transaction": wire}), encoding="utf-8")
        cli = subprocess.run(
            [sys.executable, str(self.linker_runner), "--root", str(self.root),
             "--manifest", str(graph_manifest)], capture_output=True, text=True, check=False)
        self.assertEqual(0, cli.returncode, cli.stdout + cli.stderr)
        self.assertEqual("pass", json.loads(cli.stdout)["status"])
        return current, reconstructed

    def test_installed_author_discovers_sibling_linker_and_accepts_serializer_wire(self):
        self.assertTrue(self.author_runner.is_file())
        self.assertTrue(self.linker_runner.is_file())
        process = self.run_installed(self.finalization_manifest(self.verified_transaction()))
        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        self.assertEqual("pass", json.loads(process.stdout)["status"])

    def test_temporary_install_contains_internal_reference_index_package(self):
        self.assertTrue(self.reference_runtime.is_file())
        self.assertTrue(self.reference_contract.is_file())
        self.assertFalse((self.codex_home / "bin" / "keystone-index").exists())
        process = subprocess.run(
            [sys.executable, "-c", (
                "import sys; sys.path.insert(0, sys.argv[1]); "
                "from graph_runtime.readiness import context_readiness; "
                "assert callable(context_readiness)"),
             str(self.reference_runtime.parents[1])],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(0, process.returncode, process.stdout + process.stderr)

        manifest = self.codex_home / "skills" / ".keystone-install.json"
        self.assertTrue(manifest.is_file())
        installed = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertEqual(1, installed["schema_version"])
        self.assertEqual(
            ["keystone-init", "keystone-reader", "keystone-author", "keystone-clarify",
             "keystone-linker", "keystone-coordinator"],
            installed["skills"],
        )
        self.assertEqual(
            (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
            installed["package_version"],
        )
        self.assertTrue(installed["source_commit"])
        self.assertIsInstance(installed["source_dirty"], bool)
        self.assertTrue((self.codex_home / "skills" / "unrelated-skill" / "SKILL.md").is_file())
        backups = tuple((self.codex_home / "skills" / ".keystone-backups").glob("*/keystone-reader/OLD"))
        self.assertEqual(1, len(backups))

    def test_temporary_install_contains_callable_coordinator_closure_package(self):
        for path in (
            self.coordinator_skill,
            self.coordinator_validator,
            self.coordinator_reference,
            self.coordinator_test,
        ):
            self.assertTrue(path.is_file(), path)
        process = subprocess.run(
            [sys.executable, str(self.coordinator_validator), "--help"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(0, process.returncode, process.stdout + process.stderr)

    def test_post_swap_coordinator_validator_failure_restores_every_package_and_manifest(self):
        with tempfile.TemporaryDirectory() as temporary:
            codex_home = Path(temporary)
            skills = codex_home / "skills"
            expected = {}
            for name in ("keystone-init", "keystone-reader", "keystone-author", "keystone-clarify",
                         "keystone-linker", "keystone-coordinator"):
                marker = skills / name / "OLD"
                marker.parent.mkdir(parents=True)
                marker.write_text(name, encoding="utf-8")
                expected[name] = marker
            old_manifest = '{"schema_version":1,"package_version":"old"}\n'
            (skills / ".keystone-install.json").write_text(old_manifest, encoding="utf-8")

            process = subprocess.run(
                ["bash", str(ROOT / "reinstall-local-keystone-skills.sh")],
                cwd=str(ROOT),
                env=dict(os.environ, CODEX_HOME=str(codex_home),
                         _KEYSTONE_TEST_BREAK_COORDINATOR_VALIDATOR_AFTER_SWAP="true"),
                capture_output=True, text=True, check=False,
            )

            self.assertNotEqual(0, process.returncode)
            self.assertIn("Final installed-package verification failed", process.stderr)
            for name, marker in expected.items():
                self.assertEqual(name, marker.read_text(encoding="utf-8"))
            self.assertEqual(old_manifest, (skills / ".keystone-install.json").read_text(encoding="utf-8"))

    def test_post_swap_verification_failure_restores_every_package_and_manifest(self):
        with tempfile.TemporaryDirectory() as temporary:
            codex_home = Path(temporary)
            skills = codex_home / "skills"
            expected = {}
            for name in ("keystone-init", "keystone-reader", "keystone-author", "keystone-clarify",
                         "keystone-linker", "keystone-coordinator"):
                marker = skills / name / "OLD"
                marker.parent.mkdir(parents=True)
                marker.write_text(name, encoding="utf-8")
                expected[name] = marker
            old_manifest = '{"schema_version":1,"package_version":"old"}\n'
            (skills / ".keystone-install.json").write_text(old_manifest, encoding="utf-8")

            process = subprocess.run(
                ["bash", str(ROOT / "reinstall-local-keystone-skills.sh")],
                cwd=str(ROOT),
                env=dict(os.environ, CODEX_HOME=str(codex_home),
                         _KEYSTONE_TEST_BREAK_AFTER_SWAP="keystone-reader"),
                capture_output=True, text=True, check=False,
            )

            self.assertNotEqual(0, process.returncode)
            self.assertIn("Install failed for keystone-reader", process.stderr)
            for name, marker in expected.items():
                self.assertEqual(name, marker.read_text(encoding="utf-8"))
                self.assertFalse((skills / name / "SKILL.md").exists())
            self.assertEqual(
                old_manifest,
                (skills / ".keystone-install.json").read_text(encoding="utf-8"),
            )

    def test_nonverified_states_fail_closed_without_cancelling_acceptance(self):
        accepted_source = self.progress.read_bytes()
        for state in ("proposed", "partially_applied", "failed"):
            with self.subTest(state=state):
                transaction = self.verified_transaction()
                transaction["state"] = state
                manifest = self.finalization_manifest(transaction)
                process = self.run_installed(manifest)
                self.assertEqual(1, process.returncode)
                self.assertIn("graph_sync_transaction_not_verified", process.stdout)
                self.assertEqual("complete", manifest["steps"][0]["status"])
                self.assertEqual("accepted", manifest["steps"][0]["approval_state"])
                self.assertEqual(accepted_source, self.progress.read_bytes())

    def test_document_and_repository_patches_preserve_partial_stale_and_retry_evidence(self):
        doc = SurfacePatch("doc", PatchOwner.AUTHOR, PatchSurface.DOCUMENT_METADATA,
                           "00_docs/work.md", "sha256:" + "1" * 64, "doc patch")
        code = SurfacePatch("code", PatchOwner.MAIN, PatchSurface.CODE_ANCHOR,
                            "src/work.py", "sha256:" + "2" * 64, "code patch")
        node = Node("key.cap", NodeKind.CAPABILITY, locator=Locator("00_docs/work.md"))
        proposed = GraphTransaction(
            "tx-a", "R005/S04",
            canonical_mutations=(CanonicalMutation(
                MutationOperation.ADD, MutationEntity.NODE, None, node, Evidence.DECLARED),),
            surface_patches=(doc, code),
        )
        awaiting = begin_attestation(proposed)
        awaiting = record_attestation(awaiting, SurfaceAttestation(
            "doc", PatchOwner.AUTHOR, AttestationDecision.CONFIRM, "author confirms"))
        ready = record_attestation(awaiting, SurfaceAttestation(
            "code", PatchOwner.MAIN, AttestationDecision.CONFIRM, "main confirms"))
        applying = begin_application(ready, {"doc": doc.baseline_digest, "code": code.baseline_digest})
        partial = record_application(applying, ApplicationResult(
            "doc", ApplicationStatus.APPLIED, "sha256:" + "a" * 64, "document written"))
        self.assertEqual(TransactionState.PARTIALLY_APPLIED, partial.state)
        resumed = resume_application(partial, {
            "doc": "sha256:" + "a" * 64, "code": code.baseline_digest,
        })
        self.assertEqual(TransactionState.APPLYING, resumed.state)
        self.assertEqual(partial.apply_results, resumed.apply_results)

        stale = resume_application(partial, {
            "doc": "sha256:" + "a" * 64, "code": "sha256:" + "9" * 64,
        })
        self.assertEqual(TransactionState.CONFLICTED, stale.state)
        self.assertEqual(ApplicationStatus.STALE_BASELINE, stale.apply_results[-1].result)
        revised_code = replace(code, baseline_digest="sha256:" + "9" * 64)
        revised = replace(stale, transaction_id="tx-b", state=TransactionState.PROPOSED,
                          surface_patches=(doc, revised_code))
        history = new_attempt(AttemptHistory(stale), revised)
        self.assertEqual("tx-b", history.current.transaction_id)
        self.assertEqual(TransactionState.PROPOSED, history.current.state)
        self.assertEqual((stale,), history.prior_attempts)
        self.assertEqual((), history.current.apply_results)

    def test_greenfield_document_to_code_runs_full_production_path(self):
        transaction, graph = self.execute_production_pipeline(
            {"00_docs/feature.md": "# Feature\n", "src/feature.ts": "export const feature = 1;\n"},
            {"00_docs/feature.md": "---\nkey: {id: key.doc.feature, kind: source_document}\n---\n# Feature\n",
             "src/feature.ts": "// keystone: id=key.code.feature kind=output_artifact artifact_kind=code\nexport const feature = 1;\n"},
        )
        self.assertEqual({"key.doc.feature", "key.code.feature"}, {node.id for node in graph.nodes})
        self.assertEqual(2, len(transaction.surface_patches))

    def test_existing_code_with_zero_anchors_is_bounded_to_current_change(self):
        _, graph = self.execute_production_pipeline(
            {"src/current.ts": "export const current = 1;\n", "src/unrelated.ts": "export const untouched = 2;\n"},
            {"src/current.ts": "// keystone: id=key.code.current kind=output_artifact artifact_kind=code\nexport const current = 1;\n",
             "src/unrelated.ts": "export const untouched = 2;\n"},
        )
        self.assertEqual(["key.code.current"], [node.id for node in graph.nodes])
        self.assertEqual("export const untouched = 2;\n", (self.root / "src/unrelated.ts").read_text())

    def test_standard_impact_propagation_uses_reconstructed_graph(self):
        _, graph = self.execute_production_pipeline(
            {"00_docs/std.md": "# Standard\n", "src/standard.ts": "export const standard = 1;\n"},
            {"00_docs/std.md": "---\nkey: {id: key.cap.standard, kind: capability}\n---\n# Standard\n",
             "src/standard.ts": "// keystone: id=key.code.standard kind=output_artifact artifact_kind=code provides=key.cap.standard\nexport const standard = 1;\n"},
        )
        candidates = changed_seed_candidates(graph, ("key.cap.standard",))
        self.assertEqual(["key.code.standard"], [item.node.id for item in candidates])
        self.assertEqual("required", candidates[0].grade.value)

    def test_rename_move_preserves_stable_id_and_updates_locator(self):
        _, graph = self.execute_production_pipeline(
            {"src/old.ts": "// keystone: id=key.code.move kind=output_artifact artifact_kind=code\nexport const moved = 1;\n",
             "src/new.ts": ""},
            {"src/old.ts": "// anchor moved to src/new.ts\n",
             "src/new.ts": "// keystone: id=key.code.move kind=output_artifact artifact_kind=code\nexport const moved = 1;\n"},
        )
        self.assertEqual(["key.code.move"], [node.id for node in graph.nodes])
        self.assertEqual("src/new.ts", graph.nodes[0].locator.path)

    def test_removal_replacement_emits_exact_remove_and_add_mutations(self):
        transaction, graph = self.execute_production_pipeline(
            {"00_docs/replace.md": "---\nkey: {id: key.cap.old, kind: capability}\n---\n# Old\n"},
            {"00_docs/replace.md": "---\nkey: {id: key.cap.new, kind: capability}\n---\n# Replacement\n"},
        )
        self.assertEqual(["key.cap.new"], [node.id for node in graph.nodes])
        self.assertEqual({("add", "key.cap.new"), ("remove", "key.cap.old")}, {
            (mutation.operation.value, (mutation.after or mutation.before).id)
            for mutation in transaction.canonical_mutations
        })


if __name__ == "__main__":
    unittest.main()
