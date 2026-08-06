import unittest

from graph_runtime.yaml_subset import MetadataError, parse_yaml_subset


class YamlSubsetTest(unittest.TestCase):
    def test_nested_mapping_sequence_and_inline_values_are_normalized(self):
        value = parse_yaml_subset("""key:
  id: key.work.current
  relations:
    depends_on:
      - target: key.work.target
work_gates:
  - dependency: key.work.target
    applies_to:
      steps: [S01, S02]
    condition: {work_status: complete, approval_state: accepted}
enabled: true
count: 2
optional: null
""")

        self.assertEqual("key.work.current", value["key"]["id"])
        self.assertEqual(
            [{"target": "key.work.target"}],
            value["key"]["relations"]["depends_on"],
        )
        self.assertEqual(["S01", "S02"], value["work_gates"][0]["applies_to"]["steps"])
        self.assertEqual("accepted", value["work_gates"][0]["condition"]["approval_state"])
        self.assertIs(value["enabled"], True)
        self.assertEqual(2, value["count"])
        self.assertIsNone(value["optional"])

    def test_malformed_or_non_mapping_root_is_rejected(self):
        for source in ("__malformed_frontmatter__", "key: [unterminated", "- root-item"):
            with self.subTest(source=source):
                with self.assertRaises(MetadataError):
                    parse_yaml_subset(source)

    def test_comments_blank_lines_and_quotes_are_supported(self):
        value = parse_yaml_subset("""# ignored

name: "quoted"
literal: 'value'
empty:
""")

        self.assertEqual({"name": "quoted", "literal": "value", "empty": {}}, value)


if __name__ == "__main__":
    unittest.main()
