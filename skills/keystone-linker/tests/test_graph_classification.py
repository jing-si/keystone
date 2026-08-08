import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


RUNNER = (
    Path(__file__).parents[1] / "scripts" / "run_graph_classification.py"
)


def json_bytes(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def digest_bytes(value):
    return "sha256:" + hashlib.sha256(value).hexdigest()


def digest_json(value):
    return digest_bytes(json_bytes(value))


class GraphClassificationCliTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name).resolve()
        self.root = self.base / "repository"
        self.root.mkdir()
        self.source = self.root / "src" / "example.py"
        self.source.parent.mkdir()
        self.source.write_text("def run():\n    return 1\n", encoding="utf-8")
        self.delta = {
            "kind": "artifact_delta",
            "source_surface": "src/example.py",
            "change_kind": "added",
            "changed_locators": [
                {"path": "src/example.py", "symbol": "run"},
            ],
            "semantic_summary": "Change the function return value.",
            "baseline_digest": "absent",
            "resulting_digest": digest_bytes(self.source.read_bytes()),
            "graph_relevant": False,
        }

    def tearDown(self):
        self.temporary.cleanup()

    def manifest(self, deltas=None, sources=None, **source_context_changes):
        deltas = list([self.delta] if deltas is None else deltas)
        sources = sorted(
            {item["source_surface"] for item in deltas}
            if sources is None else sources
        )
        coverage = {
            "mode": "delta_set",
            "complete": True,
            "source_count": len(sources),
            "source_path_digest": digest_json(sources),
        }
        source_context = {
            "repository_root_digest": digest_json(str(self.root)),
            "coverage": coverage,
            "sources": sources,
        }
        source_context.update(source_context_changes)
        return {
            "schema_version": 1,
            "delta_set_digest": digest_json(deltas),
            "deltas": deltas,
            "source_context": source_context,
        }

    def run_manifest(self, manifest=None, raw=None):
        path = self.base / "classification-input.json"
        path.write_bytes(raw if raw is not None else json_bytes(manifest))
        process = subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--root",
                str(self.root),
                "--manifest",
                str(path),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        payload = json.loads(process.stdout)
        return process, payload

    def test_not_applicable_binds_exact_delta_and_current_source_generation(self):
        manifest = self.manifest([self.delta])

        first_process, first = self.run_manifest(manifest)
        second_process, second = self.run_manifest(manifest)

        self.assertEqual(0, first_process.returncode, first)
        self.assertEqual(0, second_process.returncode, second)
        self.assertEqual(first, second)
        self.assertEqual(
            {
                "schema_version",
                "status",
                "disposition",
                "delta_set_digest",
                "source_generation_digest",
                "inspected_sources",
                "exclusion_evidence",
                "reason_codes",
                "diagnostics",
                "summary",
            },
            set(first),
        )
        self.assertEqual("pass", first["status"])
        self.assertEqual("not_applicable", first["disposition"])
        self.assertEqual(manifest["delta_set_digest"], first["delta_set_digest"])
        self.assertEqual(["added_plain_unowned_source"], first["reason_codes"])
        self.assertEqual(
            [
                {
                    "path": "src/example.py",
                    "type": "regular_file",
                    "raw_byte_digest": self.delta["resulting_digest"],
                    "executable": False,
                },
                {"path": "src/example.py.keystone.json", "type": "absent"},
            ],
            first["inspected_sources"],
        )
        self.assertEqual(
            [{
                "delta_index": 0,
                "locator_index": 0,
                "locator": {"path": "src/example.py", "symbol": "run"},
                "reason_code": "added_plain_unowned_source",
                "inspected_source_indexes": [0, 1],
            }],
            first["exclusion_evidence"],
        )

    def test_not_applicable_maps_every_locator_to_inspected_sources(self):
        delta = dict(self.delta)
        delta["changed_locators"] = [
            {"path": "src/example.py", "symbol": "other"},
            {"path": "src/example.py", "symbol": "run"},
        ]
        manifest = self.manifest([delta])

        process, payload = self.run_manifest(manifest)

        self.assertEqual(0, process.returncode, payload)
        self.assertEqual("not_applicable", payload["disposition"])
        self.assertEqual([0, 1], [
            item["locator_index"] for item in payload["exclusion_evidence"]
        ])
        self.assertTrue(all(
            item["inspected_source_indexes"] == [0, 1]
            for item in payload["exclusion_evidence"]
        ))

    def test_empty_delta_set_has_explicit_not_applicable_reason(self):
        manifest = self.manifest([])

        process, payload = self.run_manifest(manifest)

        self.assertEqual(0, process.returncode, payload)
        self.assertEqual("not_applicable", payload["disposition"])
        self.assertEqual(["empty_delta_set"], payload["reason_codes"])
        self.assertEqual([], payload["exclusion_evidence"])

    def test_graph_relevant_delta_is_required(self):
        delta = dict(self.delta)
        delta["graph_relevant"] = True
        manifest = self.manifest([delta])

        process, payload = self.run_manifest(manifest)

        self.assertEqual(0, process.returncode, payload)
        self.assertEqual("required", payload["disposition"])
        self.assertEqual(["graph_relevant_delta"], payload["reason_codes"])

    def test_false_caller_flag_cannot_exclude_declared_graph_metadata(self):
        self.source.write_text(
            "# keystone: id=key.code.example kind=output_artifact "
            "artifact_kind=code locator.symbol=run\n"
            "def run():\n    return 1\n",
            encoding="utf-8",
        )
        delta = dict(self.delta)
        delta["resulting_digest"] = digest_bytes(self.source.read_bytes())
        delta["graph_relevant"] = False
        manifest = self.manifest([delta])

        process, payload = self.run_manifest(manifest)

        self.assertEqual(0, process.returncode, payload)
        self.assertEqual("required", payload["disposition"])
        self.assertIn("declared_graph_metadata_present", payload["reason_codes"])

    def test_bom_prefixed_markdown_metadata_cannot_be_classified_not_applicable(self):
        source = self.root / "00_docs" / "bom.md"
        source.parent.mkdir()
        source.write_bytes(
            b"\xef\xbb\xbf---\n"
            b"key: {id: key.doc.bom, kind: source_document}\n"
            b"---\n# BOM document\n"
        )
        delta = dict(self.delta)
        delta.update({
            "source_surface": "00_docs/bom.md",
            "changed_locators": [{"path": "00_docs/bom.md"}],
            "resulting_digest": digest_bytes(source.read_bytes()),
            "graph_relevant": False,
        })

        process, payload = self.run_manifest(self.manifest([delta]))

        self.assertEqual(0, process.returncode, payload)
        self.assertEqual("required", payload["disposition"])
        self.assertIn("declared_graph_metadata_present", payload["reason_codes"])

    def test_template_interpolation_comment_cannot_be_classified_not_applicable(self):
        source = self.root / "src" / "template.js"
        source.write_text(
            "const value = `${\n"
            "// keystone: id=key.code.actual kind=output_artifact "
            "artifact_kind=code locator.symbol=actual\n"
            "1\n"
            "}`;\n",
            encoding="utf-8",
        )
        delta = dict(self.delta)
        delta.update({
            "source_surface": "src/template.js",
            "changed_locators": [
                {"path": "src/template.js", "symbol": "actual"},
            ],
            "resulting_digest": digest_bytes(source.read_bytes()),
            "graph_relevant": False,
        })

        process, payload = self.run_manifest(self.manifest([delta]))

        self.assertEqual(0, process.returncode, payload)
        self.assertEqual("required", payload["disposition"])
        self.assertIn("graph_reconstruction_diagnostic", payload["reason_codes"])

    def test_template_regex_brace_cannot_hide_graph_metadata_from_classification(self):
        source = self.root / "src" / "template-regex.tsx"
        source.write_text(
            "const value = `${ /[}]/.test(x) && (\n"
            "// keystone: id=key.code.actual kind=output_artifact "
            "artifact_kind=code locator.symbol=actual\n"
            "1\n"
            ") }`;\n",
            encoding="utf-8",
        )
        delta = dict(self.delta)
        delta.update({
            "source_surface": "src/template-regex.tsx",
            "changed_locators": [
                {"path": "src/template-regex.tsx", "symbol": "actual"},
            ],
            "resulting_digest": digest_bytes(source.read_bytes()),
            "graph_relevant": False,
        })

        process, payload = self.run_manifest(self.manifest([delta]))

        self.assertEqual(0, process.returncode, payload)
        self.assertEqual("required", payload["disposition"])
        self.assertIn("graph_reconstruction_diagnostic", payload["reason_codes"])

    def test_document_delta_is_never_excluded_by_a_false_caller_flag(self):
        delta = dict(self.delta)
        delta["kind"] = "document_delta"
        delta["graph_relevant"] = False
        manifest = self.manifest([delta])

        process, payload = self.run_manifest(manifest)

        self.assertEqual(0, process.returncode, payload)
        self.assertEqual("required", payload["disposition"])
        self.assertIn(
            "document_delta_requires_graph_review", payload["reason_codes"]
        )

    def test_external_document_locator_ownership_overrides_false_caller_flag(self):
        document = self.root / "00_docs" / "ownership.md"
        document.parent.mkdir()
        document.write_text(
            "---\n"
            "key: {id: key.doc.ownership, kind: source_document}\n"
            "---\n"
            "# Ownership\n"
            "<!-- key: id=key.code.external kind=output_artifact "
            "artifact_kind=code locator.path=src/example.py locator.symbol=run -->\n"
            "- External code owner\n",
            encoding="utf-8",
        )
        delta = dict(self.delta)
        delta["graph_relevant"] = False
        manifest = self.manifest([delta])

        process, payload = self.run_manifest(manifest)

        self.assertEqual(0, process.returncode, payload)
        self.assertEqual("required", payload["disposition"])
        self.assertIn("declared_locator_ownership", payload["reason_codes"])

    def test_modified_plain_source_without_baseline_graph_state_is_required(self):
        delta = dict(self.delta)
        delta["change_kind"] = "modified"
        delta["baseline_digest"] = digest_bytes(
            b"# keystone: id=key.code.removed kind=output_artifact "
            b"artifact_kind=code locator.symbol=run\n"
            b"def run():\n    return 0\n"
        )
        manifest = self.manifest([delta])

        process, payload = self.run_manifest(manifest)

        self.assertEqual(0, process.returncode, payload)
        self.assertEqual("required", payload["disposition"])
        self.assertIn(
            "baseline_graph_state_unavailable", payload["reason_codes"]
        )

    def test_type_replaced_plain_source_without_baseline_graph_state_is_required(self):
        delta = dict(self.delta)
        delta["change_kind"] = "type_replaced"
        delta["baseline_digest"] = digest_bytes(b"prior source generation")
        manifest = self.manifest([delta])

        process, payload = self.run_manifest(manifest)

        self.assertEqual(0, process.returncode, payload)
        self.assertEqual("required", payload["disposition"])
        self.assertIn(
            "baseline_graph_state_unavailable", payload["reason_codes"]
        )

    def test_missing_delta_source_coverage_fails_closed(self):
        manifest = self.manifest([self.delta], sources=[])

        process, payload = self.run_manifest(manifest)

        self.assertEqual(1, process.returncode, payload)
        self.assertEqual("fail", payload["status"])
        self.assertEqual("deferred", payload["disposition"])
        self.assertIn(
            "source_coverage_delta_omitted",
            {item["code"] for item in payload["diagnostics"]},
        )

    def test_stale_resulting_digest_fails_closed(self):
        delta = dict(self.delta)
        delta["resulting_digest"] = digest_bytes(b"stale source generation")
        manifest = self.manifest([delta])

        process, payload = self.run_manifest(manifest)

        self.assertEqual(1, process.returncode, payload)
        self.assertEqual("fail", payload["status"])
        self.assertEqual("deferred", payload["disposition"])
        self.assertIn(
            "source_generation_stale",
            {item["code"] for item in payload["diagnostics"]},
        )

    def test_repeated_surface_deltas_bind_the_phase_chain_and_current_result(self):
        intermediate = b"def run():\n    return 0\n"
        first = dict(self.delta)
        first["resulting_digest"] = digest_bytes(intermediate)
        second = dict(self.delta)
        second["change_kind"] = "modified"
        second["baseline_digest"] = first["resulting_digest"]
        manifest = self.manifest([first, second])

        process, payload = self.run_manifest(manifest)

        self.assertEqual(0, process.returncode, payload)
        self.assertEqual("pass", payload["status"])
        self.assertEqual("required", payload["disposition"])

    def test_repeated_surface_delta_with_broken_phase_chain_fails_closed(self):
        first = dict(self.delta)
        first["resulting_digest"] = digest_bytes(b"intermediate generation")
        second = dict(self.delta)
        second["change_kind"] = "modified"
        second["baseline_digest"] = digest_bytes(b"different generation")
        manifest = self.manifest([first, second])

        process, payload = self.run_manifest(manifest)

        self.assertEqual(1, process.returncode, payload)
        self.assertEqual("fail", payload["status"])
        self.assertIn(
            "delta_generation_chain_invalid",
            {item["code"] for item in payload["diagnostics"]},
        )

    def test_source_change_changes_generation_digest(self):
        manifest = self.manifest([self.delta])
        first_process, first = self.run_manifest(manifest)
        self.source.write_text("def run():\n    return 2\n", encoding="utf-8")
        stale_delta = dict(self.delta)
        stale_delta["resulting_digest"] = digest_bytes(self.source.read_bytes())
        stale_manifest = self.manifest([stale_delta])

        second_process, second = self.run_manifest(stale_manifest)

        self.assertEqual(0, first_process.returncode, first)
        self.assertEqual(0, second_process.returncode, second)
        self.assertNotEqual(
            first["source_generation_digest"],
            second["source_generation_digest"],
        )

    def test_strict_json_rejects_duplicate_unknown_nonfinite_and_bool_integer(self):
        valid = self.manifest([self.delta])
        cases = {
            "duplicate": (
                b'{"schema_version":1,"schema_version":1,"delta_set_digest":"x",'
                b'"deltas":[],"source_context":{}}'
            ),
            "unknown": json_bytes({**valid, "trusted": True}),
            "nonfinite": json_bytes(valid).replace(
                b'"schema_version":1', b'"schema_version":NaN'
            ),
            "bool_integer": json_bytes({**valid, "schema_version": True}),
        }
        for name, raw in cases.items():
            with self.subTest(name=name):
                process, payload = self.run_manifest(raw=raw)
                self.assertEqual(2, process.returncode, payload)
                self.assertEqual("error", payload["status"])


if __name__ == "__main__":
    unittest.main()
