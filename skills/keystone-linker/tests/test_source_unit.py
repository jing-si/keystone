import unittest

from graph_runtime.adapters import MarkdownAdapter
from graph_runtime.source_unit import SourceSurface, resolve_source_unit


class SourceUnitTest(unittest.TestCase):
    def test_inline_only_and_companion_only_select_one_canonical_surface(self):
        inline = resolve_source_unit(
            "docs/example.md",
            b"<!-- key: id=key.doc.example -->\n# Example\n",
            None,
        )
        companion = resolve_source_unit(
            "docs/example.md",
            b"# Example\n",
            b"{}",
        )

        self.assertEqual(SourceSurface.INLINE, inline.surface)
        self.assertEqual(("docs/example.md",), inline.generation_paths)
        self.assertEqual(SourceSurface.COMPANION, companion.surface)
        self.assertEqual(
            ("docs/example.md", "docs/example.md.keystone.json"),
            companion.generation_paths,
        )

    def test_inline_and_companion_declarations_fail_without_merge(self):
        unit = resolve_source_unit(
            "docs/example.md",
            b"<!-- key: id=key.doc.inline -->\n# Example\n",
            b"{}",
        )

        self.assertIsNone(unit.surface)
        self.assertEqual("metadata_surface_conflict", unit.diagnostics[0].code)

    def test_supported_adapter_is_preserved_for_inline_resolution(self):
        unit = resolve_source_unit("docs/example.md", b"# Example\n", None)

        self.assertIsInstance(unit.adapter, MarkdownAdapter)

    def test_companion_only_supported_source_preserves_absent_logical_source(self):
        unit = resolve_source_unit(
            "src/generated.py",
            None,
            b'{"source":{"baseline_digest":"absent"}}',
        )

        self.assertEqual(SourceSurface.COMPANION, unit.surface)
        self.assertEqual(("src/generated.py.keystone.json",), unit.generation_paths)
        self.assertIsNone(unit.source_bytes)

    def test_non_utf8_supported_source_falls_back_to_companion(self):
        raw_source = "# generated\n".encode("utf-16")

        unit = resolve_source_unit(
            "src/generated.py",
            raw_source,
            b'{"schema_version":1}',
        )

        self.assertEqual(SourceSurface.COMPANION, unit.surface)
        self.assertEqual(raw_source, unit.source_bytes)
        self.assertFalse(unit.diagnostics)
        self.assertEqual(
            ("src/generated.py", "src/generated.py.keystone.json"),
            unit.generation_paths,
        )

    def test_non_utf8_supported_source_without_companion_is_diagnostic(self):
        unit = resolve_source_unit(
            "src/generated.py",
            "# generated\n".encode("utf-16"),
            None,
        )

        self.assertIsNone(unit.surface)
        self.assertEqual("unsupported_encoding", unit.diagnostics[0].code)

    def test_non_utf8_companion_is_rejected_by_the_shared_resolver(self):
        unit = resolve_source_unit(
            "src/generated.py",
            "# generated\n".encode("utf-16"),
            b"\xff\xfe",
        )

        self.assertIsNone(unit.surface)
        self.assertEqual("unsupported_encoding", unit.diagnostics[0].code)
        self.assertEqual(
            "src/generated.py.keystone.json",
            unit.diagnostics[0].path,
        )

    def test_ambiguous_unterminated_anchor_blocks_companion_precedence(self):
        unit = resolve_source_unit(
            "src/example.ts",
            b'const sample = `\n// keystone: id=key.ambiguous\n',
            b'{"schema_version":1}',
        )

        self.assertIsNone(unit.surface)
        self.assertEqual(
            "ambiguous_metadata_anchor",
            unit.diagnostics[0].code,
        )


if __name__ == "__main__":
    unittest.main()
