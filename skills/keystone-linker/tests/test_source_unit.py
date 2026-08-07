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


if __name__ == "__main__":
    unittest.main()
