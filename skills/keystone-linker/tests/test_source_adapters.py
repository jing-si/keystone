import unittest

from graph_runtime.adapters import adapter_for_path
from graph_runtime.metadata import parse_source
from graph_runtime.source_unit import resolve_source_unit


class SourceAdapterLexicalTest(unittest.TestCase):
    def test_bom_markdown_frontmatter_conflicts_with_companion(self):
        unit = resolve_source_unit(
            "docs/example.md",
            (
                "\ufeff---\n"
                "key:\n"
                "  id: key.doc.bom\n"
                "---\n"
                "# Example\n"
            ).encode("utf-8"),
            b"{}",
        )

        self.assertIsNone(unit.surface)
        self.assertEqual("metadata_surface_conflict", unit.diagnostics[0].code)

    def test_unterminated_lexical_region_is_an_ambiguous_candidate(self):
        adapter = adapter_for_path("src/example.ts")
        result = parse_source(
            "const sample = `\n"
            "// keystone: id=key.ambiguous kind=output_artifact\n",
            "src/example.ts",
            adapter,
        )

        self.assertFalse(result.snapshot.nodes)
        self.assertEqual(
            {"ambiguous_metadata_anchor"},
            {item.code for item in result.diagnostics},
        )

    def test_unterminated_language_quotes_remain_ambiguous(self):
        fixtures = {
            "src/example.rs": (
                "let value = 'a;\n"
                "// keystone: id=key.ambiguous kind=output_artifact\n"
            ),
            "config/example.yaml": (
                "value: 'unterminated\n"
                "# keystone: id=key.ambiguous kind=output_artifact\n"
            ),
            "scripts/example.sh": (
                "value='unterminated\n"
                "# keystone: id=key.ambiguous kind=output_artifact\n"
            ),
        }
        for path, text in fixtures.items():
            with self.subTest(path=path):
                result = parse_source(text, path, adapter_for_path(path))
                self.assertFalse(result.snapshot.nodes)
                self.assertEqual(
                    {"ambiguous_metadata_anchor"},
                    {item.code for item in result.diagnostics},
                )

    def test_closed_heredoc_ambiguity_does_not_leak_to_next_body(self):
        adapter = adapter_for_path("scripts/example.sh")
        result = parse_source(
            "cat <<A <<B\n"
            "# keystone: id=key.fake kind=output_artifact\n"
            "A\n"
            "plain unterminated B body\n",
            "scripts/example.sh",
            adapter,
        )

        self.assertFalse(result.snapshot.nodes)
        self.assertFalse(result.diagnostics)

    def assert_only_real_anchor(self, path, text):
        adapter = adapter_for_path(path)
        self.assertIsNotNone(adapter)
        blocks = [item[0] for item in adapter.metadata_blocks(text)]
        self.assertEqual(1, len(blocks), (path, blocks))
        self.assertIn("id=key.real", blocks[0])

    def test_javascript_and_typescript_template_literals_are_masked(self):
        for path in ("src/example.js", "src/example.ts"):
            with self.subTest(path=path):
                self.assert_only_real_anchor(
                    path,
                    "const sample = `\n  // keystone: id=key.fake\n`;\n"
                    "// keystone: id=key.real kind=output_artifact artifact_kind=code\n",
                )

    def test_javascript_template_interpolation_anchor_requires_companion(self):
        for path in (
            "src/example.js",
            "src/example.ts",
            "src/example.jsx",
            "src/example.tsx",
        ):
            with self.subTest(path=path):
                result = parse_source(
                    "const value = `literal\n"
                    "// keystone: id=key.fake kind=output_artifact\n"
                    "${\n"
                    "// keystone: id=key.real kind=output_artifact artifact_kind=code\n"
                    "1\n"
                    "}`;\n",
                    path,
                    adapter_for_path(path),
                )

                self.assertFalse(result.snapshot.nodes)
                self.assertEqual(
                    {"ambiguous_metadata_anchor"},
                    {item.code for item in result.diagnostics},
                )

    def test_unterminated_javascript_template_interpolation_is_ambiguous(self):
        fixtures = (
            (
                "const value = `${\n"
                "// keystone: id=key.ambiguous kind=output_artifact\n"
            ),
            (
                "const value = `${\n"
                "// keystone: id=key.ambiguous kind=output_artifact\n"
                "1\n"
                "};\n"
            ),
        )
        for text in fixtures:
            with self.subTest(text=text):
                result = parse_source(
                    text,
                    "src/example.js",
                    adapter_for_path("src/example.js"),
                )

                self.assertFalse(result.snapshot.nodes)
                self.assertEqual(
                    {"ambiguous_metadata_anchor"},
                    {item.code for item in result.diagnostics},
                )

    def test_template_interpolation_complex_expressions_fail_closed(self):
        expressions = (
            r"/\}/.test(x) && (",
            r"/[}]/.test(x) && (",
            r"total / /[}]/.exec('x') && (",
            r"(() => { if (x) /}/.test(y); return (",
            r"total++ / count && (",
        )
        for expression in expressions:
            with self.subTest(expression=expression):
                result = parse_source(
                    "const value = `${ %s\n" % expression
                    + "// keystone: id=key.real kind=output_artifact "
                    "artifact_kind=code locator.symbol=actual\n"
                    "1\n"
                    + (") }); })()`;\n" if expression.startswith("(()") else ") }`;\n"),
                    "src/example.tsx",
                    adapter_for_path("src/example.tsx"),
                )

                self.assertFalse(result.snapshot.nodes)
                self.assertEqual(
                    {"ambiguous_metadata_anchor"},
                    {item.code for item in result.diagnostics},
                )

    def test_unterminated_template_interpolation_regex_is_ambiguous(self):
        result = parse_source(
            "const value = `${ /unterminated\n"
            "// keystone: id=key.ambiguous kind=output_artifact\n",
            "src/example.js",
            adapter_for_path("src/example.js"),
        )

        self.assertFalse(result.snapshot.nodes)
        self.assertEqual(
            {"ambiguous_metadata_anchor"},
            {item.code for item in result.diagnostics},
        )

    def test_unsupported_template_interpolation_lexical_goals_fail_closed(self):
        marker = (
            "// keystone: id=key.ambiguous kind=output_artifact "
            "artifact_kind=code locator.symbol=actual\n"
        )
        fixtures = (
            "const value = `${ 1+/}/.test(x)\n" + marker + "}`;\n",
            "const value = `${ [.../}/.exec(x)]\n" + marker + "}`;\n",
            (
                "const value = `${ (() => { if (x) foo(); else /}/.test(y); })()\n"
                + marker + "}`;\n"
            ),
            (
                "const value = `${ (() => { do /}/.test(y); while (x); })()\n"
                + marker + "}`;\n"
            ),
            (
                "const value = `${ (async () => { for await "
                "(const x of xs) /}/.test(x); })()\n"
                + marker + "}`;\n"
            ),
            (
                "const value = `${ (() => { if (x) foo(); else "
                "/[}}`]/.test(y);\n"
                + marker + "return 1; })() }`;\n"
            ),
        )
        for text in fixtures:
            with self.subTest(text=text):
                result = parse_source(
                    text,
                    "src/example.tsx",
                    adapter_for_path("src/example.tsx"),
                )

                self.assertFalse(result.snapshot.nodes)
                self.assertEqual(
                    {"ambiguous_metadata_anchor"},
                    {item.code for item in result.diagnostics},
                )

    def test_java_kotlin_and_swift_multiline_strings_are_masked(self):
        for path in ("src/Example.java", "src/Example.kt", "src/Example.swift"):
            with self.subTest(path=path):
                self.assert_only_real_anchor(
                    path,
                    'const sample = """\n// keystone: id=key.fake\n"""\n'
                    "// keystone: id=key.real kind=output_artifact artifact_kind=code\n",
                )

    def test_nested_block_comments_are_masked(self):
        fixture = (
            "/* outer\n"
            "  /* inner */\n"
            "// keystone: id=key.fake kind=output_artifact artifact_kind=code\n"
            "*/\n"
            "// keystone: id=key.real kind=output_artifact artifact_kind=code\n"
        )
        for path in ("src/Example.kt", "src/example.rs", "src/Example.swift"):
            with self.subTest(path=path):
                self.assert_only_real_anchor(path, fixture)

    def test_non_nested_block_comment_languages_resume_after_first_closer(self):
        fixture = (
            "/* outer /* inner */\n"
            "// keystone: id=key.real kind=output_artifact artifact_kind=code\n"
        )
        for path in (
            "src/example.c",
            "src/example.cpp",
            "src/Example.java",
            "src/example.js",
            "src/example.go",
            "src/example.cs",
        ):
            with self.subTest(path=path):
                self.assert_only_real_anchor(path, fixture)

    def test_java_escaped_text_block_delimiter_is_masked(self):
        self.assert_only_real_anchor(
            "src/Example.java",
            'String sample = """\ntext \\"""\n'
            "// keystone: id=key.fake kind=output_artifact artifact_kind=code\n"
            '""";\n'
            "// keystone: id=key.real kind=output_artifact artifact_kind=code\n",
        )

    def test_kotlin_raw_triple_quote_does_not_treat_backslash_as_escape(self):
        self.assert_only_real_anchor(
            "src/Example.kt",
            'val sample = """\ntext \\"""\n'
            "// keystone: id=key.real kind=output_artifact artifact_kind=code\n",
        )

    def test_swift_extended_string_delimiters_are_masked(self):
        self.assert_only_real_anchor(
            "src/Example.swift",
            'let sample = #"""\n// keystone: id=key.fake\n"""#\n'
            "// keystone: id=key.real kind=output_artifact artifact_kind=code\n",
        )

    def test_rust_go_cpp_and_csharp_raw_strings_are_masked(self):
        fixtures = {
            "src/example.rs": (
                'let sample = r##"\n// keystone: id=key.fake\n"##;\n'
            ),
            "src/example.go": (
                "sample := `\n// keystone: id=key.fake\n`\n"
            ),
            "src/example.cpp": (
                'auto sample = R"tag(\n// keystone: id=key.fake\n)tag";\n'
            ),
            "src/example.cs": (
                'var sample = @"\n// keystone: id=key.fake\n";\n'
            ),
        }
        for path, prefix in fixtures.items():
            with self.subTest(path=path):
                self.assert_only_real_anchor(
                    path,
                    prefix
                    + "// keystone: id=key.real kind=output_artifact artifact_kind=code\n",
                )

    def test_cpp_raw_string_uses_full_delimiter_grammar(self):
        self.assert_only_real_anchor(
            "src/example.cpp",
            'auto sample = R"x-y(a " quote\n'
            "// keystone: id=key.fake kind=output_artifact artifact_kind=code\n"
            ')x-y";\n'
            "// keystone: id=key.real kind=output_artifact artifact_kind=code\n",
        )

    def test_csharp_raw_string_preserves_its_quote_count(self):
        self.assert_only_real_anchor(
            "src/example.cs",
            'var sample = """"\ncontent """\n'
            "// keystone: id=key.fake kind=output_artifact\n"
            '"""";\n'
            "// keystone: id=key.real kind=output_artifact\n",
        )

    def test_jsx_text_is_not_a_line_comment(self):
        for path in ("src/example.jsx", "src/example.tsx"):
            with self.subTest(path=path):
                self.assert_only_real_anchor(
                    path,
                    "const element = <pre>\n"
                    "// keystone: id=key.fake kind=output_artifact\n"
                    "</pre>;\n"
                    "// keystone: id=key.real kind=output_artifact\n",
                )

    def test_c_strings_block_comments_and_trailing_comments_are_not_anchors(self):
        self.assert_only_real_anchor(
            "src/example.c",
            'const char *sample = "\n// keystone: id=key.fake\n";\n'
            "/*\n// keystone: id=key.block_fake\n*/\n"
            "int value = 1; // keystone: id=key.trailing_fake\n"
            "// keystone: id=key.real kind=output_artifact artifact_kind=code\n",
        )

    def test_c_family_escaped_newline_preserves_logical_line_token(self):
        for path in ("src/example.c", "src/example.cpp"):
            with self.subTest(path=path):
                self.assert_only_real_anchor(
                    path,
                    "int value = 0; \\\n"
                    "// keystone: id=key.fake kind=output_artifact\n"
                    "// keystone: id=key.real kind=output_artifact\n",
                )

    def test_shell_multiline_strings_are_masked(self):
        self.assert_only_real_anchor(
            "scripts/example.sh",
            "sample='\n# keystone: id=key.fake\n'\n"
            "value=1 # keystone: id=key.trailing_fake\n"
            "# keystone: id=key.real kind=output_artifact artifact_kind=code\n",
        )

    def test_shell_multiline_quote_cannot_start_a_false_heredoc(self):
        self.assert_only_real_anchor(
            "scripts/example.sh",
            "sample='\n"
            "<<NOT_A_HEREDOC\n"
            "'\n"
            "# keystone: id=key.real kind=output_artifact artifact_kind=code\n",
        )

    def test_shell_heredoc_bodies_are_masked(self):
        self.assert_only_real_anchor(
            "scripts/example.sh",
            "cat <<'EOF'\n"
            "# keystone: id=key.fake\n"
            "EOF\n"
            "cat <<-TABBED\n"
            "# keystone: id=key.tabbed_fake\n"
            "\tTABBED\n"
            "# keystone: id=key.real kind=output_artifact artifact_kind=code\n",
        )

    def test_shell_heredoc_queue_and_delimiter_forms_are_masked(self):
        self.assert_only_real_anchor(
            "scripts/example.sh",
            "cat <<A <<'END-FOO' <<\\EOF\n"
            "# keystone: id=key.fake_a\n"
            "A\n"
            "# keystone: id=key.fake_b\n"
            "END-FOO\n"
            "# keystone: id=key.fake_c\n"
            "EOF\n"
            "# keystone: id=key.real kind=output_artifact\n",
        )

    def test_shell_shifts_here_strings_and_single_quotes_do_not_hide_comments(self):
        fixtures = (
            "value=$((1 << FLAG))\n",
            "(( value = 1 << FLAG ))\n",
            "cat <<<EOF\n",
            "value='abc\\'\n",
        )
        for prefix in fixtures:
            with self.subTest(prefix=prefix):
                self.assert_only_real_anchor(
                    "scripts/example.sh",
                    prefix
                    + "# keystone: id=key.real kind=output_artifact\n",
                )

    def test_shell_comment_text_cannot_start_a_heredoc(self):
        for prefix in (
            "echo ok # example <<EOF\n",
            "# example <<EOF\n",
        ):
            with self.subTest(prefix=prefix):
                self.assert_only_real_anchor(
                    "scripts/example.sh",
                    prefix
                    + "# keystone: id=key.real kind=output_artifact\n",
                )

    def test_shell_escaped_newline_preserves_logical_line_token(self):
        self.assert_only_real_anchor(
            "scripts/example.sh",
            "echo foo \\\n"
            "# keystone: id=key.fake kind=output_artifact\n"
            "# keystone: id=key.real kind=output_artifact\n",
        )

    def test_shell_and_yaml_do_not_treat_slash_star_as_a_comment(self):
        self.assert_only_real_anchor(
            "scripts/example.sh",
            "files=/*\n"
            "# keystone: id=key.real kind=output_artifact\n",
        )
        self.assert_only_real_anchor(
            "config/example.yaml",
            "pattern: /*\n"
            "# keystone: id=key.real kind=output_artifact\n",
        )

    def test_bom_before_first_anchor_is_ignored(self):
        self.assert_only_real_anchor(
            "src/Example.java",
            "\ufeff// keystone: id=key.real kind=output_artifact artifact_kind=code\n",
        )

    def test_sql_dollar_strings_and_yaml_block_scalars_are_masked(self):
        self.assert_only_real_anchor(
            "schema/example.sql",
            "DO $$\n"
            "-- keystone: id=key.fake kind=output_artifact\n"
            "$$;\n"
            "-- keystone: id=key.real kind=output_artifact\n",
        )
        self.assert_only_real_anchor(
            "config/example.yaml",
            "sample: |\n"
            "  # keystone: id=key.fake kind=output_artifact\n"
            "# keystone: id=key.real kind=output_artifact\n",
        )
        self.assert_only_real_anchor(
            "config/sequence.yaml",
            "items:\n"
            "  - |\n"
            "    # keystone: id=key.fake kind=output_artifact\n"
            "# keystone: id=key.real kind=output_artifact\n",
        )
        self.assert_only_real_anchor(
            "config/tagged.yaml",
            "sample: !!str |\n"
            "  # keystone: id=key.fake kind=output_artifact\n"
            "# keystone: id=key.real kind=output_artifact\n",
        )
        self.assert_only_real_anchor(
            "config/anchored.yaml",
            "sample: &payload |\n"
            "  # keystone: id=key.fake kind=output_artifact\n"
            "# keystone: id=key.real kind=output_artifact\n",
        )

    def test_language_apostrophes_do_not_create_false_quote_ambiguity(self):
        fixtures = {
            "src/example.rs": "struct Marker<'a>;\n",
            "src/example.cpp": "auto count = 1'000;\n",
            "config/example.yaml": "team: user's-team\n",
        }
        for path, prefix in fixtures.items():
            with self.subTest(path=path):
                marker = "#" if path.endswith(".yaml") else "//"
                self.assert_only_real_anchor(
                    path,
                    prefix
                    + f"{marker} keystone: id=key.real kind=output_artifact\n",
                )

    def test_jsx_detection_ignores_literals_comparisons_and_exposes_expressions(self):
        fixtures = (
            'const sample = "<pre>";\n',
            "const sample = `<pre>`;\n",
            "if (a < b && c > d) {}\n",
            "const element = <pre>\n"
            "{\n"
            "// keystone: id=key.real kind=output_artifact\n"
            "}\n"
            "</pre>;\n",
        )
        for prefix in fixtures:
            with self.subTest(prefix=prefix):
                text = prefix
                if "id=key.real" not in text:
                    text += "// keystone: id=key.real kind=output_artifact\n"
                self.assert_only_real_anchor("src/example.tsx", text)

    def test_tsx_generic_arrow_is_not_jsx_text(self):
        self.assert_only_real_anchor(
            "src/example.tsx",
            "const identity = <T,>(value: T) => value;\n"
            "// keystone: id=key.real kind=output_artifact\n",
        )


if __name__ == "__main__":
    unittest.main()
