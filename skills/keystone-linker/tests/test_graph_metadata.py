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
from graph_runtime.dependency import (
    DependencyStatus,
    DependencyTargetState,
    evaluate_work_gates,
)
from graph_runtime.metadata import parse_companion, parse_reference_declaration, parse_source
from graph_runtime.model import (
    ApprovalState,
    CanonicalMutation,
    Evidence,
    Lifecycle,
    MutationEntity,
    MutationOperation,
    Node,
    NodeKind,
    RelationType,
)
from graph_runtime.validator import validate_snapshot


class GraphMetadataTest(unittest.TestCase):
    def test_markdown_hierarchy_uses_actual_annotated_and_unannotated_headings(self):
        source = """---
key: {id: key.doc.hierarchy, kind: source_document}
---
<!-- key: id=key.section.security -->
## Security

## Billing

<!-- key: id=key.rule.billing -->
- Billing rule

<!-- key: id=key.section.billing.details -->
### Details

<!-- key: id=key.rule.billing.details -->
- Billing detail

<!-- key: id=key.section.operations -->
## Operations

<!-- key: id=key.section.operations.nested -->
### Nested
"""

        result = parse_source(source, "00_docs/hierarchy.md", MarkdownAdapter())
        parents = {node.id: node.parent_id for node in result.snapshot.nodes}
        security = next(
            node for node in result.snapshot.nodes
            if node.id == "key.section.security"
        )

        self.assertFalse(result.diagnostics)
        self.assertEqual(NodeKind.DOCUMENT_SECTION, security.kind)
        self.assertEqual("Security", security.locator.heading)
        self.assertEqual("key.doc.hierarchy", parents["key.rule.billing"])
        self.assertEqual("key.doc.hierarchy", parents["key.section.billing.details"])
        self.assertEqual(
            "key.section.billing.details",
            parents["key.rule.billing.details"],
        )
        self.assertEqual(
            "key.section.operations",
            parents["key.section.operations.nested"],
        )

    def test_setext_heading_is_an_actual_hierarchy_boundary(self):
        source = """---
key: {id: key.doc.hierarchy, kind: source_document}
---
<!-- key: id=key.section.security -->
Security
--------

Billing
-------

<!-- key: id=key.rule.billing -->
- Billing rule
"""

        result = parse_source(source, "00_docs/hierarchy.md", MarkdownAdapter())
        parents = {node.id: node.parent_id for node in result.snapshot.nodes}
        security = next(
            node for node in result.snapshot.nodes
            if node.id == "key.section.security"
        )

        self.assertFalse(result.diagnostics)
        self.assertEqual(NodeKind.DOCUMENT_SECTION, security.kind)
        self.assertEqual("Security", security.locator.heading)
        self.assertEqual("key.doc.hierarchy", parents["key.rule.billing"])

    def test_document_governance_union_and_declared_relations_validate_end_to_end(self):
        source = """---
key:
  id: key.doc.rules
  kind: source_document
  governed_by: [key.decision.governance]
---
<!-- key: id=key.decision.governance kind=decision -->
## Governance

<!-- key: id=key.section.rules governed_by=key.decision.additional -->
## Rules

<!-- key: id=key.decision.additional kind=decision -->
### Additional Governance

<!-- key: id=key.rule.one governed_by=key.decision.item -->
- Rule one

<!-- key: id=key.decision.item kind=decision -->
### Item Governance
"""

        result = parse_source(source, "00_docs/rules.md", MarkdownAdapter())
        nodes = {node.id: node for node in result.snapshot.nodes}
        relations = {
            (relation.source, relation.relation, relation.target)
            for relation in result.snapshot.relations
        }

        self.assertFalse(result.diagnostics)
        self.assertEqual(
            ("key.decision.governance", "key.decision.additional"),
            nodes["key.section.rules"].provenance.governed_by,
        )
        self.assertEqual(
            (
                "key.decision.governance",
                "key.decision.additional",
                "key.decision.item",
            ),
            nodes["key.rule.one"].provenance.governed_by,
        )
        self.assertIn(
            (
                "key.rule.one",
                RelationType.GOVERNED_BY,
                "key.decision.item",
            ),
            relations,
        )
        self.assertNotIn(
            (
                "key.rule.one",
                RelationType.GOVERNED_BY,
                "key.decision.governance",
            ),
            relations,
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "00_docs").mkdir()
            (root / "00_docs" / "rules.md").write_text(source, encoding="utf-8")
            validation = validate_snapshot(root, result.snapshot, result.diagnostics)
        self.assertFalse(validation)

    def test_reference_declaration_exposes_only_owner_and_navigation_refs(self):
        declaration = parse_reference_declaration(
            "id=key.claim.consumer refs=key.claim.target,key.topic.graph "
            "depends_on=key.work.target")

        self.assertEqual(
            ("key.claim.consumer", ("key.claim.target", "key.topic.graph")),
            declaration,
        )
        self.assertIsNone(parse_reference_declaration("refs=key.claim.target"))

    def test_markdown_examples_inside_fences_are_passive(self):
        source = """---
key: {id: key.doc.real, kind: source_document}
---
```markdown
<!-- key: id=key.example.only kind=claim -->
## Example
<!-- key: ... -->
```
<!-- key: id=key.claim.real kind=claim -->
## Real
"""
        result = parse_source(source, "docs/real.md", MarkdownAdapter())

        self.assertEqual({"key.doc.real", "key.claim.real"},
                         {node.id for node in result.snapshot.nodes})
        self.assertFalse(result.diagnostics)

    def test_adjacent_compact_comments_extend_one_owner(self):
        source = """<!-- keystone: id=key.code.skill kind=output_artifact artifact_kind=skill_source -->
<!-- keystone: produced_from=key.work.skill -->
<!-- keystone: governed_by=key.standard.project -->
# Skill
"""
        result = parse_source(source, "skills/example/SKILL.md", MarkdownAdapter())

        self.assertFalse(result.diagnostics)
        self.assertEqual(["key.code.skill"], [node.id for node in result.snapshot.nodes])
        self.assertEqual(("key.work.skill",), result.snapshot.nodes[0].provenance.produced_from)
        self.assertEqual(("key.standard.project",), result.snapshot.nodes[0].provenance.governed_by)

    # keystone: id=key.test.linker.metadata-parser-contract kind=output_artifact artifact_kind=test verifies=key.code.linker.metadata-parser locator.test_name=test_compact_space_separated_multi_values_are_not_dropped
    def test_compact_space_separated_multi_values_are_not_dropped(self):
        source = """<!-- keystone: id=key.skill.example kind=output_artifact artifact_kind=skill_source -->
<!-- keystone: refs=key.doc.one key.doc.two -->
<!-- keystone: governed_by=key.standard.project key.standard.child -->
# Skill
"""

        result = parse_source(source, "skills/example/SKILL.md", MarkdownAdapter())
        declaration = parse_reference_declaration(
            "id=key.skill.example refs=key.doc.one key.doc.two")

        self.assertFalse(result.diagnostics)
        self.assertEqual(
            ("key.skill.example", ("key.doc.one", "key.doc.two")),
            declaration,
        )
        self.assertEqual(
            ("key.standard.project", "key.standard.child"),
            result.snapshot.nodes[0].provenance.governed_by,
        )

    def test_compact_bare_token_after_scalar_is_not_silently_ignored(self):
        result = parse_source(
            "<!-- keystone: id=key.claim.example unexpected kind=claim -->\n# Example\n",
            "docs/example.md",
            MarkdownAdapter(),
        )

        self.assertEqual((), result.snapshot.nodes)
        self.assertIn("malformed_metadata", {item.code for item in result.diagnostics})

    def test_inline_code_metadata_example_is_passive(self):
        source = """---
key: {id: key.doc.real, kind: source_document}
---
Do not write `<!-- keystone: depends_on=key.old -->` syntax.
Use ``<!-- key: id=key.claim.fake kind=claim -->`` as an example.
"""
        result = parse_source(source, "docs/real.md", MarkdownAdapter())

        self.assertEqual(["key.doc.real"], [node.id for node in result.snapshot.nodes])
        self.assertFalse(result.diagnostics)

    def test_non_keystone_frontmatter_is_passive(self):
        source = """---
name: example-skill
description: No Keystone document owner is declared here.
---
<!-- keystone: id=key.skill.example kind=output_artifact artifact_kind=skill_source -->
# Skill
"""
        result = parse_source(source, "skills/example/SKILL.md", MarkdownAdapter())

        self.assertEqual(["key.skill.example"], [node.id for node in result.snapshot.nodes])
        self.assertFalse(result.diagnostics)

    def test_structured_dependency_and_work_gate_are_executable(self):
        source = """---
document_lifecycle: active
approval:
  state: pending
key:
  id: key.work.current
  kind: work_order
  relations:
    depends_on:
      - target: key.work.target
work_gates:
  - dependency: key.work.target
    applies_to:
      steps: [S02]
    condition:
      work_status: complete
      approval_state: accepted
---
"""
        result = parse_source(source, "00_docs/current.md", MarkdownAdapter())

        self.assertFalse(result.diagnostics)
        self.assertEqual(
            [("key.work.current", RelationType.DEPENDS_ON, "key.work.target")],
            [(item.source, item.relation, item.target) for item in result.snapshot.relations],
        )
        self.assertEqual(("S02",), result.work_gates[0].steps)
        waiting = evaluate_work_gates(result.work_gates, {
            "key.work.target": DependencyTargetState("complete", "pending"),
        })
        satisfied = evaluate_work_gates(result.work_gates, {
            "key.work.target": DependencyTargetState("complete", "accepted"),
        })
        self.assertEqual(DependencyStatus.WAITING, waiting[0].status)
        self.assertTrue(waiting[0].blocking)
        self.assertEqual(DependencyStatus.SATISFIED, satisfied[0].status)
        self.assertFalse(satisfied[0].blocking)

    def test_document_section_item_metadata_is_inherited_without_relations(self):
        source = """---
document_lifecycle: archived
approval:
  state: rejected
authority:
  source: project-standard
key:
  id: key.doc.old
  kind: source_document
  governed_by: [key.standard.project]
  documents: [key.claim.document]
---
<!-- key: id=key.section.old -->
## Old
<!-- key: id=key.claim.old -->
- Historical claim
"""
        result = parse_source(source, "00_docs/old.md", MarkdownAdapter())
        nodes = {node.id: node for node in result.snapshot.nodes}

        for node_id in ("key.section.old", "key.claim.old"):
            node = nodes[node_id]
            self.assertEqual(Lifecycle.ARCHIVED, node.lifecycle)
            self.assertEqual(ApprovalState.REJECTED, node.approval_state)
            self.assertEqual(("key.standard.project",), node.provenance.governed_by)
            self.assertEqual((("source", "project-standard"),), node.source_authority)
        self.assertEqual("key.doc.old", nodes["key.section.old"].parent_id)
        self.assertEqual("key.section.old", nodes["key.claim.old"].parent_id)
        relations = {(item.source, item.relation, item.target)
                     for item in result.snapshot.relations}
        self.assertIn(("key.doc.old", RelationType.DOCUMENTS, "key.claim.document"), relations)
        self.assertIn(("key.doc.old", RelationType.GOVERNED_BY, "key.standard.project"), relations)
        self.assertFalse(any(source != "key.doc.old" for source, _, _ in relations))

    def test_structured_and_legacy_dependency_conflict_is_diagnosed(self):
        source = """---
key:
  id: key.work.current
  kind: work_order
  depends_on: [key.work.legacy]
  relations:
    depends_on:
      - target: key.work.structured
---
"""
        result = parse_source(source, "00_docs/current.md", MarkdownAdapter())
        self.assertTrue(any(item.code == "structured_legacy_relation_conflict"
                            for item in result.diagnostics))

    def test_requires_verification_requirement_is_distinct_from_evidence(self):
        text = """<!-- keystone: id=key.acceptance kind=claim requires_verification_of=key.claim -->
# Acceptance
<!-- keystone: id=key.claim kind=claim -->
# Claim
<!-- keystone: id=key.test kind=output_artifact artifact_kind=test verifies=key.claim -->
# Test
"""
        result = parse_source(text, "standard.md", MarkdownAdapter())

        relations = {(item.source, item.relation, item.target) for item in result.snapshot.relations}
        self.assertIn(("key.acceptance", RelationType.REQUIRES_VERIFICATION_OF, "key.claim"), relations)
        self.assertIn(("key.test", RelationType.VERIFIES, "key.claim"), relations)

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
