import unittest

from graph_runtime.model import RelationType
from graph_runtime.relation_policy import RELATION_POLICY, relation_direction_allowed


class RelationPolicyTests(unittest.TestCase):
    def test_model_vocabulary_and_executable_policy_are_identical(self):
        self.assertEqual(set(RELATION_POLICY), {item.value for item in RelationType})
        for policy in RELATION_POLICY.values():
            self.assertIn(policy["forward_grade"], {
                "required", "strong_candidate", "weak_candidate", "informational"})
            self.assertIn(policy["reverse_grade"], {
                "required", "strong_candidate", "weak_candidate", "informational"})
            self.assertIn(policy["direct_item_artifact"], {"allowed", "bounded", "forbidden"})

    def test_derived_skill_source_may_point_to_its_decision_source(self):
        self.assertTrue(relation_direction_allowed(
            "output_artifact", "skill_source", "derived_from", "document_section", "none"))


if __name__ == "__main__":
    unittest.main()
