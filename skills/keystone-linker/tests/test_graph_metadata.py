import json
import tempfile
import unittest
from pathlib import Path

from graph_runtime.adapters import (
    GenericLineCommentAdapter,
    KotlinJavaAdapter,
    MarkdownAdapter,
    SqlAdapter,
    XmlAdapter,
    YamlAdapter,
    adapter_for_path,
)
from graph_runtime.metadata import parse_companion, parse_source
from graph_runtime.model import (
    CanonicalMutation,
    Evidence,
    Lifecycle,
    MutationEntity,
    MutationOperation,
    Node,
    NodeKind,
    RelationType,
)


class GraphMetadataTest(unittest.TestCase):
    def test_canonical_and_flat_frontmatter_normalize_equally(self):
        canonical = """---
key:
  id: key.doc.example
  refs: [key.topic.graph]
  kind: source_document
  implements: [key.capability.graph]
  lifecycle: active
---
# Example
"""
        flat = """---
key.id: key.doc.example
key.refs: [key.topic.graph]
key.kind: source_document
key.implements: [key.capability.graph]
key.lifecycle: active
---
# Example
"""
        self.assertEqual(
            parse_source(canonical, "docs/example.md", MarkdownAdapter()).snapshot,
            parse_source(flat, "docs/example.md", MarkdownAdapter()).snapshot,
        )

    def test_markdown_immediate_item_comments_attach_locators(self):
        source = """---
key: {id: key.doc.items, kind: source_document}
---
<!-- key: id=key.section.one lifecycle=deprecated -->
## One
<!--
key:
  id: key.rule.one
  verifies: [key.claim.one]
-->
- Rule one

| ID | Meaning |
| --- | --- |
| <!-- key: id=key.row.one documents=key.claim.one --> `ROW-1` | value |
"""
        result = parse_source(source, "docs/items.md", MarkdownAdapter())
        nodes = {node.id: node for node in result.snapshot.nodes}
        self.assertEqual("One", nodes["key.section.one"].locator.heading)
        self.assertEqual("Rule one", nodes["key.rule.one"].locator.symbol)
        self.assertEqual("ROW-1", nodes["key.row.one"].locator.symbol)
        self.assertEqual(Lifecycle.DEPRECATED, nodes["key.section.one"].lifecycle)
        self.assertIn(
            ("key.rule.one", RelationType.VERIFIES, "key.claim.one"),
            {(r.source, r.relation, r.target) for r in result.snapshot.relations},
        )

    def test_all_comment_surfaces_produce_same_declared_graph(self):
        cases = [
            (GenericLineCommentAdapter(), "// keystone: id=key.code.x implements=key.cap.x\nfunction x() {}", "code"),
            (KotlinJavaAdapter(), "// keystone: id=key.code.x implements=key.cap.x\nclass X {}", "code"),
            (SqlAdapter(), "-- keystone: id=key.code.x implements=key.cap.x\nselect 1;", "schema"),
            (XmlAdapter(), "<!-- keystone: id=key.code.x implements=key.cap.x -->\n<root/>", "config") ,
            (YamlAdapter(), "# keystone: id=key.code.x implements=key.cap.x\nvalue: 1", "config"),
        ]
        for adapter, source, artifact_kind in cases:
            with self.subTest(adapter=type(adapter).__name__):
                result = parse_source(source, "src/example", adapter)
                self.assertEqual(["key.code.x"], [n.id for n in result.snapshot.nodes])
                self.assertEqual(artifact_kind, result.snapshot.nodes[0].artifact_kind.value)
                self.assertEqual(adapter.surface, result.snapshot.nodes[0].provenance.surface)
                relation = result.snapshot.relations[0]
                self.assertEqual(("key.code.x", RelationType.IMPLEMENTS, "key.cap.x"),
                                 (relation.source, relation.relation, relation.target))
                self.assertEqual(Evidence.DECLARED, relation.evidence)

    def test_malformed_input_is_fail_soft(self):
        result = parse_source("---\nkey: [unterminated\n---\n", "bad.md", MarkdownAdapter())
        self.assertEqual((), result.snapshot.nodes)
        self.assertTrue(result.diagnostics)
        self.assertEqual("error", result.diagnostics[0].severity.value)

    def test_legacy_keystone_markdown_comment_normalizes_as_declared_metadata(self):
        source = "<!-- keystone: id=key.rule.legacy depends_on=key.rule.base -->\n- Legacy rule"
        result = parse_source(source, "legacy.md", MarkdownAdapter())
        self.assertEqual(["key.rule.legacy"], [node.id for node in result.snapshot.nodes])
        self.assertEqual(
            ("key.rule.legacy", RelationType.DEPENDS_ON, "key.rule.base"),
            (result.snapshot.relations[0].source, result.snapshot.relations[0].relation,
             result.snapshot.relations[0].target),
        )

    def test_companion_validates_shape_source_and_absent_baseline(self):
        payload = {
            "schema_version": 1,
            "source": {"path": "src/a.bin", "surface": "companion_metadata", "baseline_digest": "absent"},
            "nodes": [{"id": "key.output.a", "kind": "output_artifact", "artifact_kind": "generated_file",
                       "locator": {"path": "src/a.bin"}, "lifecycle": "active",
                       "provenance": {"produced_from": [], "governed_by": []}}],
            "relations": [],
        }
        good = parse_companion(json.dumps(payload), "src/a.bin.keystone.json", "src/a.bin",
                               source_exists=False)
        self.assertEqual("absent", good.baseline_digest)
        self.assertEqual("key.output.a", good.snapshot.nodes[0].id)
        bad = parse_companion(json.dumps(payload), "src/other.bin.keystone.json", "src/other.bin",
                              source_exists=False)
        self.assertEqual((), bad.snapshot.nodes)
        self.assertTrue(any(d.code == "companion_source_mismatch" for d in bad.diagnostics))
        wrong_name = parse_companion(json.dumps(payload), "src/not-a.bin.keystone.json", "src/a.bin",
                                     source_exists=False)
        self.assertTrue(any(d.code == "companion_path_mismatch" for d in wrong_name.diagnostics))
        missing_shape = dict(payload)
        del missing_shape["nodes"]
        malformed = parse_companion(json.dumps(missing_shape), "src/a.bin.keystone.json", "src/a.bin",
                                    source_exists=False)
        self.assertTrue(any(d.code == "malformed_companion" for d in malformed.diagnostics))

    def test_companion_digest_distinguishes_new_match_and_mismatch(self):
        import hashlib
        raw = b"existing source\n"
        digest = "sha256:" + hashlib.sha256(raw).hexdigest()
        base = {"schema_version": 1, "source": {"path": "src/a.bin", "surface": "companion_metadata",
                "baseline_digest": digest}, "nodes": [], "relations": []}
        matching = parse_companion(json.dumps(base), "src/a.bin.keystone.json", "src/a.bin",
                                   source_exists=True, source_bytes=raw)
        self.assertFalse(matching.diagnostics)
        absent_existing = dict(base)
        absent_existing["source"] = dict(base["source"], baseline_digest="absent")
        rejected = parse_companion(json.dumps(absent_existing), "src/a.bin.keystone.json", "src/a.bin",
                                   source_exists=True, source_bytes=raw)
        self.assertTrue(any(d.code == "companion_baseline_mismatch" for d in rejected.diagnostics))
        mismatch = parse_companion(json.dumps(base), "src/a.bin.keystone.json", "src/a.bin",
                                   source_exists=True, source_bytes=b"changed")
        self.assertTrue(any(d.code == "companion_baseline_mismatch" for d in mismatch.diagnostics))

    def test_duplicates_and_unknown_fields_are_diagnosed(self):
        source = """<!-- key: id=key.same -->
## First
<!-- key: id=key.same mystery_relation=key.other -->
## Second
"""
        result = parse_source(source, "duplicate.md", MarkdownAdapter())
        self.assertEqual(1, len(result.snapshot.nodes))
        self.assertTrue(any(d.code == "duplicate_id" for d in result.diagnostics))
        self.assertTrue(any(d.code == "unknown_metadata_field" for d in result.diagnostics))

    def test_declared_locator_is_normalized_and_conflicts_are_diagnosed(self):
        source = """---
key: {id: key.config.x, kind: output_artifact, artifact_kind: config}
locator: {path: config/app.yml, config_key: app.feature}
---
"""
        result = parse_source(source, "config/app.yml", MarkdownAdapter())
        self.assertEqual("app.feature", result.snapshot.nodes[0].locator.config_key)
        conflict = parse_source(source, "config/other.yml", MarkdownAdapter())
        self.assertTrue(any(d.code == "locator_conflict" for d in conflict.diagnostics))

    def test_compact_locator_keys_normalize_across_language_anchors(self):
        declarations = [
            (GenericLineCommentAdapter(), "// keystone: ", "src/a.ts"),
            (KotlinJavaAdapter(), "// keystone: ", "src/A.kt"),
            (SqlAdapter(), "-- keystone: ", "schema/a.sql"),
            (XmlAdapter(), "<!-- keystone: ", "config/a.xml"),
            (YamlAdapter(), "# keystone: ", "config/a.yml"),
        ]
        for adapter, prefix, path in declarations:
            suffix = " -->" if isinstance(adapter, XmlAdapter) else ""
            source = (prefix + "id=key.anchor.x locator.path=" + path +
                      " locator.symbol=Thing locator.test_name=test_thing" +
                      " locator.config_key=app.thing locator.schema_name=thing_table" + suffix)
            with self.subTest(adapter=type(adapter).__name__):
                result = parse_source(source, path, adapter)
                self.assertFalse(any(d.code == "unknown_metadata_field" for d in result.diagnostics))
                locator = result.snapshot.nodes[0].locator
                self.assertEqual((path, "Thing", "test_thing", "app.thing", "thing_table"),
                                 (locator.path, locator.symbol, locator.test_name,
                                  locator.config_key, locator.schema_name))

    def test_inferred_evidence_cannot_construct_canonical_mutation(self):
        node = Node("key.a", NodeKind.CAPABILITY)
        with self.assertRaises(ValueError):
            CanonicalMutation(MutationOperation.ADD, MutationEntity.NODE, None, node, Evidence.INFERRED)

    def test_adapter_selection_uses_companion_fallback_for_unknown_surface(self):
        with tempfile.TemporaryDirectory() as directory:
            source_path = Path(directory) / "asset.bin"
            source_path.write_bytes(b"data")
            companion = source_path.with_name(source_path.name + ".keystone.json")
            companion.write_text(json.dumps({
                "schema_version": 1,
                "source": {"path": "asset.bin", "surface": "companion_metadata", "baseline_digest": "absent"},
                "nodes": [], "relations": [],
            }), encoding="utf-8")
            self.assertIsNone(adapter_for_path(str(source_path)))
            result = parse_source("", "asset.bin", None, companion_text=companion.read_text(),
                                  companion_path="asset.bin.keystone.json", companion_source_exists=False)
            self.assertFalse(result.diagnostics)

    def test_snapshot_order_is_deterministic_and_direction_is_preserved(self):
        source = """---
key:
  id: key.z
  kind: source_document
  depends_on: [key.b, key.a]
---
<!-- key: id=key.a -->
## A
<!-- key: id=key.b -->
## B
"""
        snapshot = parse_source(source, "ordered.md", MarkdownAdapter()).snapshot
        self.assertEqual(["key.a", "key.b", "key.z"], [n.id for n in snapshot.nodes])
        self.assertEqual(
            [("key.z", "key.a"), ("key.z", "key.b")],
            [(r.source, r.target) for r in snapshot.relations],
        )

    def test_produced_from_derives_one_inferred_produces_edge(self):
        source = """---
key: {id: key.work.build, kind: work_order}
---
<!-- key: id=key.output.runtime kind=output_artifact artifact_kind=code produced_from=key.work.build -->
- Runtime
"""
        snapshot = parse_source(source, "build.md", MarkdownAdapter()).snapshot
        relation = snapshot.relations[0]
        self.assertEqual(
            ("key.work.build", RelationType.PRODUCES, "key.output.runtime", Evidence.INFERRED),
            (relation.source, relation.relation, relation.target, relation.evidence),
        )
        nodes = {node.id: node for node in snapshot.nodes}
        self.assertEqual(("key.work.build",), nodes["key.output.runtime"].provenance.produced_from)

    def test_explicit_produces_is_not_duplicated_by_produced_from(self):
        source = """---
key: {id: key.work.build, kind: work_order, produces: key.output.runtime}
---
<!-- key: id=key.output.runtime kind=output_artifact artifact_kind=code produced_from=key.work.build -->
- Runtime
"""
        snapshot = parse_source(source, "build.md", MarkdownAdapter()).snapshot
        self.assertEqual(1, len(snapshot.relations))
        self.assertEqual(Evidence.DECLARED, snapshot.relations[0].evidence)

    def test_companion_rejects_extra_missing_and_wrong_typed_nested_fields(self):
        base = {
            "schema_version": 1,
            "source": {"path": "src/a.bin", "surface": "companion_metadata", "baseline_digest": "absent"},
            "nodes": [{"id": "key.output.a", "kind": "output_artifact", "artifact_kind": "generated_file",
                       "locator": {"path": "src/a.bin"}, "lifecycle": "active",
                       "provenance": {"produced_from": [], "governed_by": []}}],
            "relations": [],
        }
        cases = []
        extra = dict(base, extra=True)
        cases.append(extra)
        missing = json.loads(json.dumps(base))
        del missing["nodes"][0]["lifecycle"]
        cases.append(missing)
        wrong = json.loads(json.dumps(base))
        wrong["nodes"][0]["locator"]["path"] = 3
        cases.append(wrong)
        for payload in cases:
            with self.subTest(payload=payload):
                result = parse_companion(json.dumps(payload), "src/a.bin.keystone.json", "src/a.bin",
                                         source_exists=False)
                self.assertEqual((), result.snapshot.nodes)
                self.assertEqual("malformed_companion", result.diagnostics[0].code)


if __name__ == "__main__":
    unittest.main()
