import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[2]
LINKER_SCRIPTS = ROOT / "skills" / "keystone-linker" / "scripts"
GRAPH_VALIDATOR = LINKER_SCRIPTS / "validate_graph.py"
FINALIZATION_RUNNER = (
    ROOT / "skills" / "keystone-author" / "scripts"
    / "run_finalization_validation.py"
)


class R008SelfHostE2ETest(unittest.TestCase):
    def readiness(self, cache_path, *, artifact_context=False):
        request = {
            "repository_root": str(ROOT),
            "cache_path": str(cache_path),
            "initiator": "linker" if artifact_context else "reader",
            "artifact_context": artifact_context,
            "include_typed_graph": artifact_context,
        }
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "graph_runtime.readiness_cli",
                "--request-json",
                json.dumps(request),
                "--response-json",
                "-",
            ],
            cwd=str(ROOT),
            env=dict(os.environ, PYTHONPATH=str(LINKER_SCRIPTS)),
            capture_output=True,
            text=True,
            check=False,
        )
        return process, json.loads(process.stdout)

    def test_actual_corpus_recovers_current_state_and_runtime_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory) / "reference-index.sqlite3"
            docs_process, docs = self.readiness(cache)
            repository_process, repository = self.readiness(
                cache, artifact_context=True
            )

        self.assertEqual(0, docs_process.returncode, docs_process.stderr)
        self.assertEqual(0, repository_process.returncode, repository_process.stderr)
        self.assertTrue(docs["complete"])
        self.assertTrue(repository["complete"])
        self.assertEqual(0, docs["coverage"]["skipped"])
        self.assertEqual(0, repository["coverage"]["skipped"])
        self.assertEqual(
            ["reader", "linker"],
            [item["lane"] for item in docs["trace"]],
        )

        owner_ids = {item["id"] for item in repository["owners"]}
        expected_runtime = {
            "key.code.linker.metadata-parser",
            "key.code.linker.context-readiness",
            "key.code.linker.source-views",
            "key.code.linker.graph-transaction-validator",
            "key.code.author.finalization-validator",
        }
        expected_tests = {
            "key.test.linker.metadata-parser-contract",
            "key.test.linker.source-views",
            "key.test.reader.linker-readiness-contract",
            "key.test.r011.reader-session-focus",
            "key.test.r012.reader-round-session-focus",
            "key.test.r012.uptendo-no-event-work-state",
            "key.test.r011.progress-ownership",
            "key.test.r011.reader-revision-readiness",
            "key.test.r011.resumable-finalization",
            "key.test.r011.derived-work-state-projection",
            "key.test.r013.clarify-group-application",
            "key.test.linker.graph-transaction-wire-contract",
            "key.test.author.finalization-validator-contract",
        }
        self.assertTrue(expected_runtime | expected_tests <= owner_ids)
        verifies = {
            (item["source_id"], item["target_id"])
            for item in repository["typed_edges"]
            if item["relation"] == "verifies"
        }
        self.assertEqual(
            {
                ("key.test.linker.metadata-parser-contract",
                 "key.code.linker.metadata-parser"),
                ("key.test.reader.linker-readiness-contract",
                 "key.code.linker.context-readiness"),
                ("key.test.linker.source-views",
                 "key.code.linker.source-views"),
                ("key.test.linker.source-views",
                 "key.standard.project.source-derived-semantic-views"),
                ("key.test.r011.reader-session-focus",
                 "key.standard.skill.reader.session-focus"),
                ("key.test.r012.reader-round-session-focus",
                 "key.standard.skill.reader.round-session-focus"),
                ("key.test.r012.uptendo-no-event-work-state",
                 "key.claim.current-work-state.uptendo-no-event-recovery"),
                ("key.test.r011.progress-ownership",
                 "key.standard.skill.author.progress-ownership"),
                ("key.test.r011.progress-ownership",
                 "key.standard.skill.author.terminal-status-reconciliation"),
                ("key.test.r011.reader-revision-readiness",
                 "key.standard.skill.reader.revision-readiness"),
                ("key.test.r011.resumable-finalization",
                 "key.standard.skill.author.resumable-finalization"),
                ("key.test.r011.derived-work-state-projection",
                 "key.standard.project.derived-work-state-projection"),
                ("key.test.r013.clarify-group-application",
                 "key.standard.project.std-keystone-060"),
                ("key.test.r013.clarify-group-application",
                 "key.standard.skill.clarify.topic-boundary"),
                ("key.test.r013.clarify-group-application",
                 "key.standard.skill.author.clarification-log-application"),
                ("key.test.linker.graph-transaction-wire-contract",
                 "key.code.linker.graph-transaction-validator"),
                ("key.test.author.finalization-validator-contract",
                 "key.code.author.finalization-validator"),
            },
            verifies,
        )

        context = (ROOT / "00_docs" / "key-context-map.md").read_text(
            encoding="utf-8"
        )
        work_state_process = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "work_state_runtime.py"),
             "--root", str(ROOT)],
            cwd=str(ROOT), capture_output=True, text=True, check=False,
        )
        self.assertEqual(
            0, work_state_process.returncode,
            work_state_process.stdout + work_state_process.stderr,
        )
        work_state = json.loads(work_state_process.stdout)
        self.assertEqual("pass", work_state["status"])
        self.assertEqual([], work_state["state"]["pointer_claims"])
        self.assertIsInstance(work_state["state"]["active_rounds"], list)
        self.assertIsInstance(work_state["state"]["active_steps"], list)
        self.assertNotIn("latest_accepted_round", work_state["state"])
        self.assertIn("R011", work_state["state"]["accepted_rounds"])
        self.assertTrue(all(
            item["state_source"]["mode"] == "aggregate_progress"
            for item in work_state["state"]["active_works"]
        ))
        self.assertIn("scripts/work_state_runtime.py --root .", context)

        graph = subprocess.run(
            [sys.executable, str(GRAPH_VALIDATOR), "--root", str(ROOT),
             "--scope", "repository"],
            cwd=str(ROOT), capture_output=True, text=True, check=False,
        )
        graph_payload = json.loads(graph.stdout)
        self.assertEqual(0, graph.returncode, graph.stderr)
        self.assertEqual("pass", graph_payload["status"])
        self.assertTrue(graph_payload["coverage"]["complete"])

        for manifest in (
            "00_docs/works/r008-skill-graph-traceability/"
            "key-finalization-manifest.json",
            "00_docs/works/r009-coordinator-keystone-closure/"
            "key-finalization-manifest.json",
        ):
            process = subprocess.run(
                [sys.executable, str(FINALIZATION_RUNNER), "--root", str(ROOT),
                 "--manifest", str(ROOT / manifest)],
                cwd=str(ROOT), capture_output=True, text=True, check=False,
            )
            payload = json.loads(process.stdout)
            if process.returncode == 0:
                self.assertEqual("pass", payload["status"])
            else:
                self.assertEqual(1, process.returncode, payload)
                self.assertEqual("fail", payload["status"])
                self.assertTrue(payload["diagnostics"])
                self.assertTrue(all(
                    item["code"] in {
                        "active_steps_source_missing",
                        "active_steps_source_mismatch",
                        "global_state_source_mismatch",
                    }
                    for item in payload["diagnostics"]
                ), payload)


if __name__ == "__main__":
    unittest.main()
