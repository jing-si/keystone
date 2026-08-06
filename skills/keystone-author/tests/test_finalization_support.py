import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import validate_finalization as validator  # noqa: E402


class FinalizationSupportCharacterizationTest(unittest.TestCase):
    def test_scoped_path_rejects_missing_and_outside_values(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            self.assertEqual((None, "missing"), validator.resolve_scoped_path(root, None))
            self.assertEqual((None, "outside"), validator.resolve_scoped_path(root, "../outside.md"))

    def test_nested_and_inline_mapping_scalars_are_equivalent(self):
        nested = "approval:\n  state: accepted\n"
        inline = "approval: {state: accepted}\n"
        self.assertEqual("accepted", validator.approval_scalar(nested, "state"))
        self.assertEqual("accepted", validator.approval_scalar(inline, "state"))

    def test_active_steps_preserves_declared_order(self):
        content = "Active steps: [R007/S02, R007/S01]\n"
        self.assertEqual(["R007/S02", "R007/S01"], validator.active_steps_from_text(content))


if __name__ == "__main__":
    unittest.main()
